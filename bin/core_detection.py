

def detect_circle(img_multichannel, **kwargs):

	from skimage.feature import canny
	from skimage.util import img_as_ubyte
	from skimage.transform import hough_circle, hough_circle_peaks
	import numpy as np

	img = img_as_ubyte(img_multichannel[...,0])

	edges = canny(img, sigma=1, low_threshold=50, high_threshold=150)

	# Detect the radii
	hough_radii = np.arange(125, 160, 5) #values set for 10x downsized (around 334x334 pixels)
	hough_res = hough_circle(edges, hough_radii)

	# Select the most prominent circle
	accums, cx, cy, radius = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)

	return(accums, cx, cy, radius)