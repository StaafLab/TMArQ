
"""
TODO: better exception handling when no threshold is found.
"""

import numpy as np

from skimage import filters

def set_coordinates(coord_dict, f):
	"""return coordinates from the dictionary as integer values"""
	
	center_y, center_x, radius = coord_dict[f]
	center_y = int(center_y)
	center_x = int(center_x)
	radius = int(radius)

	return center_y, center_x, radius

def _threshold(stain_layer, stain, metafile):

	"""
	function that returns a mask object and the threshold value after applying the otsu threshold
	stain_layer: image channel that corresponds to one of the stain layers hematoxylin or DAB
	stain : {'hema', 'dab'}
	metafile: file to write the threshold values to
	"""
	if stain == "hema":

		try:
			threshold = filters.threshold_mean(stain_layer)
			with open(metafile, "a") as m:
				m.write(f'{threshold} \t')
		except:
			threshold = 0 
			with open(metafile, "a") as m:
				m.write('NA \t')
			

	elif stain == "dab":
		try:
			threshold = filters.threshold_triangle(stain_layer)
			with open(metafile, "a") as m:
					m.write(f'{threshold} \t')
		except:
			threshold = 0 
			with open(metafile, "a") as m:
				m.write('NA \t')
			
	mask = stain_layer > threshold

	return(mask, threshold)


def _calc_coresize(radius):

	core_size = radius**2
	core_size = core_size*np.pi

	return core_size


def _check_threshold(stain_layer, core_size, mask, threshold):

	if np.sum(mask==True) > int(core_size): #fix threshold swap
		mask = stain_layer < threshold
		print("swapping threshold")

	return mask

def _calc_stained_frac(mask, core_size, stain,  metafile):

	stained_pix_mask = np.sum(mask==True) #mask area outside detected ROI 

	fraction = (np.float(stained_pix_mask)/(core_size))

	if stain == "hema":
		with open(metafile, "a") as m:
			m.write(f'{fraction*100} \t')
	elif stain == "dab":
		with open(metafile, "a") as m:
			m.write(f'{fraction*100} \n')

	return fraction


def threshold(stain_layer, radius, stain, metafile):

	mask, thresh = _threshold(stain_layer, stain, metafile)

	core_size = _calc_coresize(radius)

	if stain == "hema":
		mask = _check_threshold(stain_layer, core_size, mask, thresh)
	elif stain == "dab":
		mask = _check_threshold(stain_layer, core_size, mask, thresh) #### check effect, was excluded

	return mask, thresh

def threshold_double(stain_layer, single_threshold, metafile):

	try:
		multi_thresholds = filters.threshold_multiotsu(stain_layer)
		regions = np.digitize(stain_layer, bins=multi_thresholds)
		
		cell_cores = regions > 1
		
		with open(metafile, "a") as m:
			m.write(f'{multi_thresholds[0]} \t {multi_thresholds[1]} \t')
	except: #if only one level of thresholding is possible	
		cell_cores = single_threshold 
		
		with open(metafile, "a") as m:
			m.write(f'{0} \t {0} \t'.format("NA"))

	return cell_cores

def clean_threshold(mask, **kwargs):

	from skimage import morphology

	mask = morphology.remove_small_objects(mask, min_size=64)
	mask = morphology.binary_erosion(mask)
	mask = morphology.binary_dilation(mask)

	return mask

def count_nuclei(hema_nuclei, dab_mask):

	nuclei = np.logical_xor(hema_nuclei, dab_mask)

	return nuclei
