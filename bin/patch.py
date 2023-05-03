
#!/usr/bin/env python3

"""
Title: patch.py
Date: 24.11.2020
Author: S.J. Roostee

Description:
	Module for patching images into non-overlapping patches of a given patch size. Patching is carried out from the top left corner of
	the image to the bottom right, going from top to bottom.
	


Procedure:


TODO:
- Allow for extra postional arguments to only patch the core area using the circle coordinates.
- Add check if patches perfeclty match image size -> no area of the image skipped
- Patch border value check for 'split cells'

- patches are not exaclty square ..? e.g. 3000 × 3001

"""

import numpy as np 
import warnings



def one_patch(im, patch_size, x=0, y=0):
    #creates one patch with offset x,y for the top left corner of the patch
    patch_height, patch_width = patch_size 
    patch = np.array([im[y:(patch_height+y)][(patch_height-1)][x:(patch_width+x)]])
    
    for i in range((patch_height-1),0, -1):
        patched = np.array([im[y:(patch_height+y)][i][x:(patch_width+x)]])
        patch = np.vstack((patched, patch)) 
        
    return patch


def patching(im, patch_size, overlap=0, centre=0):
    #returns a list of patches starting from top left to bottom right going top to bottom.
    patch_height, patch_width = patch_size 
    
    image_height, image_width =im.shape[:2]

    height_gap = image_height%patch_height
    width_gap = image_width%patch_width

    if height_gap!=0: 
        warnings.warn("Patch size does not match image height. Gap size of " +str(height_gap))
    if width_gap!=0:
        warnings.warn("Patch size does not match image width. Gap size of " +str(width_gap))


    x_off = range(0, (image_width-patch_width), patch_width)
    y_off = range(0, (image_height-patch_height), patch_height)
    
    patches = [] #change to list of predefined size
    
    for y in y_off:
        for x in x_off:
            patch = one_patch(im, patch_size, x, y)
            patches.append(patch)  
        
    return patches


def crop_dim(im, coordinates):
    """
    Return max no pixels the masks can be cropped by.  
    Assumes:
    - all masks of the same staining and same block have the same dimensions
    - all masks are square
    - crop should return a square mask
    """
    crops = []

    for f in coordinates:
        y, x, radius = coordinates[f]
        y = int(y)
        x = int(x)
        f_crop_max = max(x, y, (im.shape[1]-x), (im.shape[0]-y)) 
        crops.append(f_crop_max)

    crop_max = max(crops)

    return crop_max

def _shift(im, crop_max, y_centre, x_centre):

    x_shift = 0
    y_shift = 0

    if crop_max>x_centre:
        x_shift=crop_max - x_centre #add check for other side of x

    if crop_max>(im.shape[1]-x_centre):
        x_shift= ((im.shape[1]-x_centre) - crop_max)

    if crop_max>y_centre:
        y_shift=crop_max-y_centre #add check for other side of y

    if crop_max>(im.shape[0]-y_centre):
        y_shift= ((im.shape[0]-y_centre) - crop_max)

    return x_shift, y_shift

def core_centre_crop(im, crop_max, x_centre, y_centre):
    """Crop image with the crop centre x_centre and y_centre. 
    If x_centre or y_centre are too far out of the centre range
    then do a true centre crop."""

    #check if centre is more than 10% out of true centre
    if x_centre < ((im.shape[1]/2) - (im.shape[1]*.1)) or x_centre > ((im.shape[1]/2) + (im.shape[1]*.1)):
        x_centre = int(im.shape[1]/2)

    if y_centre < ((im.shape[0]/2) - (im.shape[0]*.1)) or y_centre > ((im.shape[0]/2) + (im.shape[0]*.1)):
        y_centre = int(im.shape[0]/2)

    x_shift, y_shift = _shift(im, crop_max, y_centre, x_centre)

    # print(x_centre)
    # print(y_centre)
    crop = one_patch(im, ((crop_max*2), (crop_max*2)), x = ((x_centre-crop_max)+x_shift), y = ((y_centre-crop_max)+y_shift))
    return crop

def crop_postthresh(dab_mask, crop_max, center_x, center_y, excluded_file, file_name):
    ######### fix exception handling in the case of missing arguments
    try:
        dab_mask = core_centre_crop(im=dab_mask, crop_max=crop_max, x_centre=center_x, y_centre=center_y)
        #slow, try to optimise?
    except:
        with open(excluded_file, "a") as e:
            e.write(f'{file_name} \t cropping failure')
            print(f'{file_name} cropping failed.')
    # continue

    return dab_mask