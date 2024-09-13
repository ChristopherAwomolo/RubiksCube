import cv2
import os

"""
This script uses a predefined dictionary and a 


"""




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
    "F1": (192, 107, 35, 23),
    "F2": (267, 88, 32, 25),
    "F3": (329, 73, 34, 19),
    "F4": (234, 134, 54, 26),
    "F5": (316, 112, 45, 25),
    "F6": (386, 90, 33, 25),
    "F7": (298, 164, 57, 34),
    "F8": (384, 134, 42, 33),
    "F9": (449, 111, 44, 33),
    "L1": (174, 294, 34, 31),
    "L2": (171, 224, 30, 40),
    "L3": (164, 146, 28, 47),
    "L4": (221, 335, 32, 39),
    "L5": (216, 261, 34, 48),
    "L6": (208, 174, 37, 57),
    "L7": (270, 382, 35, 35),
    "L8": (269, 301, 37, 50),
    "L9": (261, 209, 51, 69),
    "D1": (329, 218, 53, 55),
    "D2": (412, 189, 42, 44),
    "D3": (478, 156, 38, 50),
    "D4": (327, 309, 48, 44),
    "D5": (403, 278, 35, 35),
    "D6": (471, 240, 32, 39),
    "D7": (331, 388, 37, 35),
    "D8": (396, 349, 43, 36),
    "D9": (455, 318, 33, 33),
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
