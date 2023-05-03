#!/usr/bin/env python3

"""

This file includes code from the BSD3-licensed software starDist
Copyright (c) 2018-2022, Uwe Schmidt, Martin Weigert
All rights reserved.
 


Title: 02_deconvolve.py
Author: S.J. Roostee

Description:
	This scripts deconvolves the RGB colour space to HED colour space using unmixing. The DAB layer is then used in thresholding
	to determine positive/negative values for all pixels. The H layer is used for general cell nucleus detection using starDist. 
	Combined info on the position of the cell nuclei and positive/negative pixels determines positive and negative cell counts
	and positions in output files.

Procedure:
	- Deconvolve RGB to HED colour scheme
	- Check core area based on hematoxylin colour scheme, triangle-thresholding (>0.75% hema-coloured)
	- Threshold DAB-channel based on triangle-thresholding
	- Filter (remove small object, erosion, dilation)
	- Count DAB-stained pixels
	- Calculate fraction of area stained
TODO: - add flags to optionally store intermediate files like segmented nuclei of all cells or segmented nuclei of all positive cells 

"""

#####################	ARGPARSE 	###########################

import sys
import os
import argparse

from pathlib import Path

import numpy as np

import yaml

import numpy as np
import pandas as pd

from skimage import io
from skimage import filters

from skimage.color import rgb2hed, hed2rgb
from skimage.util import img_as_ubyte

from patch import core_centre_crop
from file_handling import path_to_dir, check_outdir, list_files, create_coord_dict
from core_analysis import threshold, set_coordinates, threshold_double, clean_threshold, count_nuclei
#from core_visualisation import show_HEDseparation, show_thresholds, show_stain, save_stain

from stardist.models import StarDist2D 
from csbdeep.utils import normalize

usage = "This script splits the TMA images in three different stains."


parser = argparse.ArgumentParser(description=usage)

parser.add_argument(
	"-v", "--version",
	action = "version",
	version = "%(prog)s 1.0"
	)

parser.add_argument(
	"-i",
	dest = "input_directory",
	metavar = "INPUT_DIRECTORY",
	type = path_to_dir,
	required = True
	)

parser.add_argument(
	"-c",
	dest = "coordinates",
	metavar = "COORDINATES",
	type = argparse.FileType("r"),
	required = True
	)

parser.add_argument(
	"-out",
	dest = "out",
	metavar = "OUT",
#	type = argparse.FileType("a"),
	help = "cell counts output",
	required = True
	)

parser.add_argument(
	"-m",
	dest = "meta",
	metavar = "META",
	#type = argparse.FileType("a"),
	help = "metadata generated during thresholding",
	required = True
	)

args = parser.parse_args()

input_dir = args.input_directory

coordinates = args.coordinates

output = args.out

metafile = args.meta

do_both = True

if do_both == True:
	do_hema = True
	do_dab = True

else:
	do_dab = True 

with open("config/tmaConfig.yaml") as ymlfile:
	cfg = yaml.safe_load(ymlfile)

max_radius = int((cfg["image_size"]/2))

files = list_files(input_dir)

coordinate_dict = create_coord_dict(coordinates)

with open(output, "a") as out:
	out.write('file \t hema_cells \t dab_cells10 \t dab_frac10 \t dab_cells20 \t dab_frac20 \t dab_cells30 \t dab_frac30 \t dab_cells40 \t dab_frac40 \t dab_cells50 \t dab_frac50 \n')

# with open(output, "a") as out:
# 	out.write('file \t hema_cells \t dab_cells\n')

model = StarDist2D.from_pretrained('2D_versatile_he')

#size around centre point of cell nucleus
n = 8

for f in files:
	# print(f)
	if not f in coordinate_dict:
		continue 

	center_y, center_x, radius = set_coordinates(coordinate_dict, f)

	ihc_rgb = io.imread(input_dir+"/"+f)
# 	img = ihc_rgb[...,0]
	ihc_hed_h = rgb2hed(ihc_rgb)
	ihc_hed_d = rgb2hed(ihc_rgb) #quick fix for memory pointer issues, fix this later


	ihc_copy_hema = ihc_hed_h
	ihc_copy_hema[:,:,2] = 0
	ihc_copy_hema[:,:,1] = 0
	ihc_copy_hema[:,:,0<0] = 0
	hema_rgb = hed2rgb(ihc_copy_hema)

	# dab_layer = ihc_rgb[:,:,2]
	dab_layer = ihc_hed_d[:,:,2]

	dab_layer = core_centre_crop(im=dab_layer, crop_max=max_radius, x_centre=center_x, y_centre=center_y)

	##add flag option here
	# np.save("results/dab_layer/" + f + "_dab.npy", dab_layer)

	mask, dab_threshold = threshold(dab_layer, radius, "dab", metafile)

	##add flag option here
	# np.save("results/dab_mask/" + f + "_mask.npy", mask)

#	print(f' threshold: {dab_threshold}')
# 		ihc_copy_dab[:,:,0] = ihc_copy_dab[:,:,2] #'colour' dab as hema channel
# 		print(ihc_copy_dab)
# 		ihc_copy_dab[:,:,2] = 0 #extra filter here yes or no?
# 		dab_rgb = hed2rgb(ihc_copy_dab) #translate back to rgb for export/segmentation

	# ######## SEGMENTATION of HEMA with STARDIST ##############

	hema_img = core_centre_crop(im=hema_rgb, crop_max=max_radius, x_centre=center_x, y_centre=center_y)

	hema_labels, _hema = model.predict_instances(normalize(hema_img))

	##add flag option
	# np.save("results/he_labels/" + f + "_labels.npy", hema_labels)

	# ######## EXTRACT CELL INFO USING STARDIST LABELS ##############
	cell_counts = range(1, np.amax(hema_labels.astype(int))+1)

	all_xmin = []
	all_xmax = []
	all_xwidth = []
	all_ymin = []
	all_ymax = []
	all_ywidth = []
	all_xmid = []
	all_ymid = []
	all_px = []
	
	for cell in cell_counts: #slowest part, speed up?
	
		rows, cols = np.where(hema_labels == cell)

		ymin = np.min(rows)
		ymax = np.max(rows)
		xmin = np.min(cols)
		xmax = np.max(cols)
		ywidth = (ymax - ymin) + 1
		xwidth =(xmax - xmin) + 1
		yid = np.rint(np.mean(rows)).astype('int')
		xid = np.rint(np.mean(cols)).astype('int')
		pix = np.sum(len(rows))
		
		all_xmin.append(xmin)
		all_xmax.append(xmax)
		all_xwidth.append(xwidth)
		all_ymin.append(ymin)
		all_ymax.append(ymax)
		all_ywidth.append(ywidth)
		all_xmid.append(xid)
		all_ymid.append(yid)
		all_px.append(pix)
		
	cell_info = {'xmin' : all_xmin, 'xmax' : all_xmax, 'xwidth': all_xwidth, 'ymin': all_ymin, 'ymax': all_ymax, 
			 'ywdith': all_ywidth, 'xid': all_xmid, 'yid' : all_ymid, 'pix' : all_px}
	cell_infodf = pd.DataFrame(cell_info, index=cell_counts)
	
	
	cells = cell_infodf.index.tolist()
	xids = cell_infodf['xid'].tolist()
	yids = cell_infodf['yid'].tolist()
	marker_10 = []
	marker_20 = []
	marker_30 = []
	marker_40 = []
	marker_50 = []

	dab_positive = np.copy(hema_labels)

	for cell, xid, yid in zip(cells, xids, yids):

		dab_pos_10 = False
		dab_pos_20 = False
		dab_pos_30 = False
		dab_pos_40 = False
		dab_pos_50 = False
			
		cell_dab_grid = mask[(yid-n):(yid+n), (xid-n):(xid+n)]
		n_pix = cell_dab_grid.size
		dab_pos_pix = np.sum(cell_dab_grid)
		if dab_pos_pix > 0:
			pix_frac = dab_pos_pix/n_pix
			if pix_frac > .1:
				dab_pos_10 = True
			if pix_frac > .2:
				dab_pos_20 = True
			if pix_frac > .3:
				dab_pos_30 = True
			if pix_frac > .4:
				dab_pos_40 = True
			if pix_frac > .5:
				dab_pos_50 = True
				
			else:
				dab_positive[dab_positive == cell] = 0

		else:
			dab_positive[dab_positive == cell] = 0
				
		marker_10.append(dab_pos_10)
		marker_20.append(dab_pos_20)
		marker_30.append(dab_pos_30)
		marker_40.append(dab_pos_40)
		marker_50.append(dab_pos_50)
	
	dab_positive10 = np.sum(marker_10)
	dab_positive20 = np.sum(marker_20)
	dab_positive30 = np.sum(marker_30)
	dab_positive40 = np.sum(marker_40)
	dab_positive50 = np.sum(marker_50)

	# np.save("results/dab_positive/" + f + "_mask.npy", dab_positive)
	
	if len(cell_counts) > 0: 
		dab_frac10 = np.divide(dab_positive10, len(cell_counts))
		dab_frac20 = np.divide(dab_positive20, len(cell_counts))
		dab_frac30 = np.divide(dab_positive30, len(cell_counts))
		dab_frac40 = np.divide(dab_positive40, len(cell_counts))
		dab_frac50 = np.divide(dab_positive50, len(cell_counts))

	with open(output, "a") as out:
		out.write(f' {f} \t {len(cell_counts)} \t {dab_positive10} \t {dab_frac10} \t {dab_positive20} \t {dab_frac20} \t {dab_positive30} \t {dab_frac30} \t {dab_positive40} \t {dab_frac40}\t {dab_positive50} \t {dab_frac50}\n')




