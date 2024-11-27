# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 23:22:19 2024

@author: oruku
"""

# Olivier Rukundo, Ph.D. - orukundo@gmail.com - 2024-11-27
################### ManualRoiPatchingFunction.py #############################
# This provides options for manually defining the fixed ROI size, 
# marking (left-clicking) and correcting (right-clicking) ROIs on an image. 
# The output includes annotated image with the fixed-size ROI squares and 
# corresponding text files with the ROI centers.
##############################################################################


import cv2
from matplotlib import pyplot as plt
from tkinter import filedialog, Tk
from matplotlib.widgets import Button

# Function to select input image and output folder
def select_file_and_folder():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title="Select the Image File",
                                           filetypes=[("Image Files", "*.tiff *.jpg *.png")])
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    root.destroy()
    return file_path, output_folder

# Select input image and output folder
image_path, output_folder = select_file_and_folder()

if not image_path or not output_folder:
    raise Exception("Image file and output folder must be selected.")

# Load the image
image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Could not load the image from the path: {image_path}")

# Make a copy for modifications
image_with_squares = image.copy()

# Input: Square properties
square_size = int(input("Enter the size of the square (in pixels): "))

# Default square color (blue)
square_color = (255, 0, 0)  

# Temporary memory to store square centers
square_centers = []

# Get base name of the input image for saving the .txt file
output_file_name = f"{output_folder}/{image_path.split('/')[-1].split('.')[0]}.txt"

# Save button axis, initialized later
save_button_bounds = None

def onclick(event):
    global square_centers, image_with_squares, save_button_bounds

    # Check if the click is inside the save button area, ignore if true
    if save_button_bounds and save_button_bounds[0] <= event.x <= save_button_bounds[2] and \
       save_button_bounds[1] <= event.y <= save_button_bounds[3]:
        return

    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        
        # Left-click: Draw square
        if event.button == 1:  
            top_left = (x - square_size // 2, y - square_size // 2)
            bottom_right = (x + square_size // 2, y + square_size // 2)
            centroid = (x, y)
            cv2.rectangle(image_with_squares, top_left, bottom_right, square_color, thickness=2)
            square_centers.append(centroid)  
            redraw_image()
        
        # Right-click: Delete the last square
        elif event.button == 3:  
            if square_centers:
                square_centers.pop() 
                redraw_image()
            else:
                print("No squares to remove.")

def redraw_image():
    global image_with_squares
    # Reset the image
    image_with_squares = image.copy()
    # Redraw all squares and centers from the memory
    for centroid in square_centers:
        x, y = centroid
        top_left = (x - square_size // 2, y - square_size // 2)
        bottom_right = (x + square_size // 2, y + square_size // 2)
        cv2.rectangle(image_with_squares, top_left, bottom_right, square_color, thickness=2)
    # Update only the image without affecting the button
    image_display.set_data(cv2.cvtColor(image_with_squares, cv2.COLOR_BGR2RGB))
    plt.draw()

def save_data(event=None):
    # Save centers to a .txt file
    with open(output_file_name, 'w') as file:
        file.write("centers (x, y):\n")
        for centroid in square_centers:
            file.write(f"{centroid[0]}, {centroid[1]}\n")
    print(f"Centroid data saved to {output_file_name}.")

    # Save the image without the "Save" button
    cropped_image_path = f"{output_folder}/{image_path.split('/')[-1].split('.')[0]}.png"
    cv2.imwrite(cropped_image_path, image_with_squares)
    print(f"Cropped image saved to {cropped_image_path}.")

# Initialize Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 8))
image_display = plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.axis('off')

# Add "Save" button at the top-left corner
save_ax = plt.axes([0.02, 0.92, 0.1, 0.05])
save_button = Button(save_ax, 'Save')

# Get button bounds for click filtering
renderer = fig.canvas.get_renderer()
save_button_bounds = save_ax.get_window_extent(renderer).bounds  
save_button_bounds = (save_button_bounds[0], save_button_bounds[1], 
                      save_button_bounds[0] + save_button_bounds[2], 
                      save_button_bounds[1] + save_button_bounds[3]) 

# Connect button to save function
save_button.on_clicked(save_data)

# Connect mouse clicks to the onclick function
cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Show the interactive plot
plt.show()

