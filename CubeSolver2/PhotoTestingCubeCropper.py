import cv2
import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# List to store the points
points = []
photo_counter = 0  # Counter to keep track of the number of photos saved


# Mouse callback function to capture points
def draw_circle(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 12:  # 3 grids, 4 points each
            points.append((x, y))
        else:
            points.clear()
            points.append((x, y))


# Function to get the next available set number
def get_next_set_number():
    count = 1  # Start checking from 1
    while True:
        # Define the prefix and the substring to check
        prefix = f'{count}-'
        substring = f'.{count}-'

        # Check if there are files with either the prefix or the substring
        files_with_prefix_or_substring = any(fn.startswith(prefix) for fn in os.listdir('..'))
        files_two = any(substring in fn for fn in os.listdir('..'))
        if files_with_prefix_or_substring == True or files_two == True:
            pass
        else:
            return count  # Return the first available number
        count += 1
        # Increment to check the next number

# Determine the starting set number based on existing files
starting_set_number = get_next_set_number()

# Use Tkinter file dialog to select the image
Tk().withdraw()  # We don't want a full GUI, so keep the root window from appearing
img_path = askopenfilename(title="Select an image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])

if not img_path:
    print("No image selected")
    exit()

# Load the selected image
img = cv2.imread(img_path)

if img is None:
    print("Error loading image")
    exit()

cv2.namedWindow('Image')
cv2.setMouseCallback('Image', draw_circle)

print("Click on the image to select points in the order of top-left, top-right, bottom-left, bottom-right for each grid (3 sets of 4 points).")

while True:
    img_copy = img.copy()

    # Draw existing points
    '''
    for point in points:
        cv2.circle(img_copy, point, 5, (0, 0, 255), -1)
    '''
    # Draw grids if we have 4 points for each grid (total 12 points)
    if len(points) == 12:
        # Labels for each grid
        grid_labels = ['U', 'L', 'R']

        for grid_index in range(3):  # 3 grids
            # Get the 4 points for the current grid
            grid_points = points[grid_index * 4:(grid_index + 1) * 4]
            grid_label = grid_labels[grid_index]
            '''
            # Draw the perspective square
            cv2.line(img_copy, grid_points[0], grid_points[1], (255, 0, 0), 2)
            cv2.line(img_copy, grid_points[1], grid_points[3], (255, 0, 0), 2)
            cv2.line(img_copy, grid_points[3], grid_points[2], (255, 0, 0), 2)
            cv2.line(img_copy, grid_points[2], grid_points[0], (255, 0, 0), 2)
            '''
            # Calculate the 1/3 and 2/3 points along the top and bottom lines
            top_third1 = (
                int(grid_points[0][0] + (grid_points[1][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + (grid_points[1][1] - grid_points[0][1]) / 3)
            )
            top_third2 = (
                int(grid_points[0][0] + 2 * (grid_points[1][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + 2 * (grid_points[1][1] - grid_points[0][1]) / 3)
            )

            bottom_third1 = (
                int(grid_points[2][0] + (grid_points[3][0] - grid_points[2][0]) / 3),
                int(grid_points[2][1] + (grid_points[3][1] - grid_points[2][1]) / 3)
            )
            bottom_third2 = (
                int(grid_points[2][0] + 2 * (grid_points[3][0] - grid_points[2][0]) / 3),
                int(grid_points[2][1] + 2 * (grid_points[3][1] - grid_points[2][1]) / 3)
            )
            '''
            # Draw vertical grid lines
            cv2.line(img_copy, top_third1, bottom_third1, (0, 255, 0), 2)
            cv2.line(img_copy, top_third2, bottom_third2, (0, 255, 0), 2)
            '''
            # Calculate the 1/3 and 2/3 points along the left and right lines
            left_third1 = (
                int(grid_points[0][0] + (grid_points[2][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + (grid_points[2][1] - grid_points[0][1]) / 3)
            )
            left_third2 = (
                int(grid_points[0][0] + 2 * (grid_points[2][0] - grid_points[0][0]) / 3),
                int(grid_points[0][1] + 2 * (grid_points[2][1] - grid_points[0][1]) / 3)
            )

            right_third1 = (
                int(grid_points[1][0] + (grid_points[3][0] - grid_points[1][0]) / 3),
                int(grid_points[1][1] + (grid_points[3][1] - grid_points[1][1]) / 3)
            )
            right_third2 = (
                int(grid_points[1][0] + 2 * (grid_points[3][0] - grid_points[1][0]) / 3),
                int(grid_points[1][1] + 2 * (grid_points[3][1] - grid_points[1][1]) / 3)
            )
            '''
            # Draw horizontal grid lines
            cv2.line(img_copy, left_third1, right_third1, (0, 255, 0), 2)
            cv2.line(img_copy, left_third2, right_third2, (0, 255, 0), 2)
            '''
            # Draw 32x32 pixel squares inside each cell of the 3x3 grid
            square_size = 32

            def interpolate(p1, p2, t):
                """Interpolate between points p1 and p2 by a factor of t."""
                return (int(p1[0] + t * (p2[0] - p1[0])), int(p1[1] + t * (p2[1] - p1[1])))


            # Loop over the 3x3 grid cells
            for i in range(3):
                for j in range(3):
                    # Interpolate to find the corners of the current grid cell
                    top_left = interpolate(interpolate(grid_points[0], grid_points[2], i / 3),
                                           interpolate(grid_points[1], grid_points[3], i / 3), j / 3)
                    top_right = interpolate(interpolate(grid_points[0], grid_points[2], i / 3),
                                            interpolate(grid_points[1], grid_points[3], i / 3), (j + 1) / 3)
                    bottom_left = interpolate(interpolate(grid_points[0], grid_points[2], (i + 1) / 3),
                                              interpolate(grid_points[1], grid_points[3], (i + 1) / 3), j / 3)
                    bottom_right = interpolate(interpolate(grid_points[0], grid_points[2], (i + 1) / 3),
                                               interpolate(grid_points[1], grid_points[3], (i + 1) / 3), (j + 1) / 3)

                    # Find the center of the current cell
                    center_x = (top_left[0] + top_right[0] + bottom_left[0] + bottom_right[0]) // 4
                    center_y = (top_left[1] + top_right[1] + bottom_left[1] + bottom_right[1]) // 4

                    # Top-left corner of the small square
                    top_left_x = center_x - square_size // 2
                    top_left_y = center_y - square_size // 2

                    # Bottom-right corner of the small square
                    bottom_right_x = top_left_x + square_size
                    bottom_right_y = top_left_y + square_size
                    '''
                    # Draw the small square centered at the center of the current cell
                    cv2.rectangle(img_copy, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 1)
                    '''
                    # Extract and save the region inside the small square
                    if top_left_x >= 0 and top_left_y >= 0 and bottom_right_x <= img_copy.shape[1] and bottom_right_y <= \
                            img_copy.shape[0]:
                        roi = img_copy[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
                        filename = f'{starting_set_number}-{grid_index + 1}-{grid_label}{3 * i + j + 1}.png'
                        cv2.imwrite(filename, roi)
                        photo_counter += 1  # Increment the photo counter

                    # Stop if we have saved 27 photos
                    if photo_counter >= 27:
                        print("Generated 27 photos. Exiting.")
                        cv2.destroyAllWindows()
                        exit()

        #starting_set_number += 1

    cv2.imshow('Image', img_copy)

    # Break the loop on 'ESC' key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
