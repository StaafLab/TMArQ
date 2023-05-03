#!/usr/bin/env python3

"""
Title: 01_deconvolve.py
Author: S.J. Roostee
Description:
	This script downsizes all images in a directory by a (default value) factor 10, identifies the coordinates of the 
	circle through Hough circle detection and stores these in a txt file.  
Procedure:
	- downsize images by factor 10
	- hough circle detection
	- export circle coordinates (multiplied by scaling factor) in txt file
	- if no circle is found through Hough circle detection export default coordinates
	- export that no circle is found for this core to metafile
"""

import sys
import os
import argparse

from skimage.io import imread, imsave
from skimage.transform import rescale, hough_circle, hough_circle_peaks
from skimage.color import gray2rgb
from skimage.draw import disk, circle_perimeter

import numpy as np

from file_handling import set_headers
from core_detection import detect_circle

#####################	ARGPARSE 	###########################

usage = "This script finds the region of interest for a TMA core are returns the coordinates of "
usage += "the ROI in a tab separeted txt file with the images file names."

def path_to_dir(ptd):
	if os.path.isdir(ptd):
		return ptd
	else:
		raise NotADirectoryError(ptd)

parser = argparse.ArgumentParser(description=usage)

parser.add_argument(
	"-v", "--version",
	action = "version",
	version = "%(prog)s 1.0"
	)

parser.add_argument(
	"-i",
	dest = "directory",
	metavar = "DIRECTORY",
	type = path_to_dir,
	required = True,
	help = "path to directory containing the TMA core images"
	)

parser.add_argument(
	"-o",
	dest = "output",
	metavar = "OUTPUT",
	default = "coordinates.txt", 
	help = "core coordinates"
	)

parser.add_argument(
	"-e",
	dest = "empty",
	metavar = "EMPTY",
	default = "logfile.log", 
	help = "logfile keeping track of excluded tma cores"
	)



args = parser.parse_args()

input_dir = args.directory

coordinates = args.output

empty_cores = args.empty

#######################

#config variables

scaling_factor = 10 #downsize all files by a factor 10

#####################	DATA LOADING	#####################

#find all visible files in the input directory
files = [f for f in os.listdir(input_dir) if os.path.isfile(input_dir+"/"+f) and not f.startswith(".")]

####################	FILE HEADERS 	#####################

coord_headers = '{}\t{}\t{}\t{}\n'.format("#file", "center_y", "center_x", "radius")
meta_headers = '{}\t{}\n'.format("file", "core")

set_headers(file = coordinates, headers = coord_headers)
set_headers(file = empty_cores, headers = meta_headers)

for f in files:
	print(f)
	img_full = imread(input_dir+"/"+f)
	img_rescaled = rescale(img_full, (1/scaling_factor), multichannel=True, anti_aliasing = True)

	#####################	CIRCLE DETECTION	################

	accums, cx, cy, radius = detect_circle(img_rescaled)

	if len(accums) > 0:
		
		for center_y, center_x, r in zip(cy, cx, radius):
		
			with open(coordinates, "a") as coord:
				coord.write('{}\t{}\t{}\t{}\n'.format(f, center_y*(scaling_factor), center_x*(scaling_factor), r*(scaling_factor)))
			with open(empty_cores, "a") as meta:
				meta.write('{}\t{}\n'.format(f, "yes"))
		
	else:
		with open(coordinates, "a") as coord:
			coord.write('{}\t{}\t{}\t{}\n'.format(f, (img_rescaled.shape[0]*5), (img_rescaled.shape[1]*5), (img_rescaled.shape[1]*4))) #*5 because *10 for scale and /2 for the centre point *4, take 80% of image width/heigth? for image radius
		with open(empty_cores, "a") as meta:
			meta.write('{}\t{}\n'.format(f, "no"))











