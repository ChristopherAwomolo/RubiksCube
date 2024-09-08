import cv2
import os

testing_folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testing")
fullpic_folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "full pictures", "v4-7-test")
os.makedirs(testing_folder_path, exist_ok=True)

def get_next_set_number():
    count = 1  # Start checking from 1
    while True:
        # Define the prefix and the substring to check
        prefix = f'{count}-'
        substring = f'.{count}-'

        # Check if there are files with either the prefix or the substring
        files_with_prefix_or_substring = any(fn.startswith(prefix) for fn in os.listdir('.'))
        files_two = any(substring in fn for fn in os.listdir('.'))
        if files_with_prefix_or_substring == True or files_two == True:
            pass
        else:
            return count  # Return the first available number
        count += 1
        # Increment to check the next number

# Determine the starting set number based on existing files
starting_set_number = get_next_set_number()
# Dictionary of polygons with keys as identifiers
polygons = {
    'F1': (247, 240, 24, 21),
    'F2': (295, 224, 21, 18),
    'F3': (331, 210, 21, 17),
    'F4': (283, 260, 39, 19),
    'F5': (336, 238, 25, 22),
    'F6': (370, 222, 26, 20),
    'F7': (337, 277, 33, 26),
    'F8': (380, 256, 29, 24),
    'F9': (415, 236, 29, 23),
    'L1': (227, 269, 26, 30),
    'L2': (266, 291, 35, 33),
    'L3': (313, 314, 37, 34),
    'L4': (229, 319, 32, 35),
    'L5': (271, 345, 24, 24),
    'L6': (318, 370, 29, 26),
    'L7': (234, 373, 21, 21),
    'L8': (274, 400, 23, 22),
    'L9': (318, 426, 25, 24),
    'D1': (362, 316, 24, 27),
    'D2': (404, 293, 23, 23),
    'D3': (440, 272, 21, 22),
    'D4': (363, 372, 24, 25),
    'D5': (403, 348, 20, 21),
    'D6': (434, 325, 22, 23),
    'D7': (361, 426, 22, 24),
    'D8': (400, 395, 21, 22),
    'D9': (431, 374, 20, 21)
}

# Input image path
input_image_path = os.path.join(fullpic_folder_path, "test-1-1.png")

# Create output directory if it doesn't exist

# Labels and starting set number
grid_labels = ['F', 'L', 'D']  # Labels corresponding to the face of the cube

# Load the image from the directory
frame = cv2.imread(input_image_path)

if frame is None:
    print(f"Error: Failed to load image from {input_image_path}")
else:
    # Naming the files based on the grid_index and coordinates
    for grid_index, grid_label in enumerate(grid_labels):
        for i in range(3):
            for j in range(3):
                # Calculate the region index based on grid index, i, and j
                region_key = f'{grid_label}{3 * i + j + 1}'
                if region_key in polygons:
                    x, y, w, h = polygons[region_key]
                    roi = frame[y:y+h, x:x+w]

                    # Filename generation
                    filename = f"{testing_folder_path}\{starting_set_number}-{grid_index + 1}-{region_key}.png"
                    cv2.imwrite(filename, roi)
                    print(f"Saved: {filename}")
    # Display the resulting frame with rectangles around the regions
    for (x, y, w, h) in polygons.values():
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow('Original Image with Regions', frame)

    # Wait for a key press to close the windows
    cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()
