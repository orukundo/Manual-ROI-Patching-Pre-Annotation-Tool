# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 08:50:16 2024

@author: oruku
"""

# Olivier Rukundo, Ph.D. - orukundo@gmail.com - 2024-11-27
##################### patchExportFunction.py #################################
# This automates the extraction of fixed-size patches from images based 
# on ManualRoiPatchingFunction.py's predefined ROI centers.
# and saves the patches to a designated output folder.
##############################################################################

import os
import cv2

# Define directories
txt_folder = " "
image_folder =  " "
output_folder =  " "

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Step 1: Get all .txt files
txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]

# Step 2: Get all (e.g., .tiff) files
image_files = [f for f in os.listdir(image_folder) if f.endswith('.tiff')]

# Step 3: Check if .txt file names and .tiff file names match
txt_names = {os.path.splitext(f)[0] for f in txt_files}
image_names = {os.path.splitext(f)[0] for f in image_files}

if txt_names != image_names:
    missing_in_txt = image_names - txt_names
    missing_in_image = txt_names - image_names
    raise ValueError(f"File name mismatch:\nMissing in .txt: {missing_in_txt}\nMissing in images: {missing_in_image}")

print("All .txt files and .tiff files match.")

# Step 4: Crop and save patches
crop_size = 640  # Crop size or fixed-size is 640x640
half_crop = crop_size // 2

for txt_file in txt_files:
    base_name = os.path.splitext(txt_file)[0]
    txt_path = os.path.join(txt_folder, txt_file)
    image_path = os.path.join(image_folder, base_name + ".tiff")

    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Could not load image: {image_path}")
        continue

    # Read coordinates from .txt file
    with open(txt_path, 'r') as f:
        lines = f.readlines()
    
    # Skip the header (assuming the first line is a header)
    coordinates = [line.strip().split(',') for line in lines[1:]]
    coordinates = [(int(x), int(y)) for x, y in coordinates]

    # Crop patches and save
    for idx, (x, y) in enumerate(coordinates):
        top_left_x = max(0, x - half_crop)
        top_left_y = max(0, y - half_crop)
        bottom_right_x = min(image.shape[1], x + half_crop)
        bottom_right_y = min(image.shape[0], y + half_crop)

        patch = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

        # Generate unique patch name
        patch_name = f"{base_name}_patch_{idx + 1}.tiff"
        patch_path = os.path.join(output_folder, patch_name)

        # Save the patch
        cv2.imwrite(patch_path, patch)

print(f"Patches saved in: {output_folder}")
