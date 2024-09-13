import cv2
import os
import time
from tkinter import Tk, filedialog

# Initialize global variables
squares = {'front': [], 'left': [], 'down': []}
drawing = False  # True if the mouse is pressed
ix, iy = -1, -1
current_face = 'front'
square_counter = {'front': 1, 'left': 1, 'down': 1}
first_phase_complete = False
frame = None  # Define the frame globally

#colors = str(input('Write the colors of the cube: '))
#colors_list = list(colors)

def get_next_set_number(directory):
    count = 1  # Start checking from 1
    while True:
        prefix = f'{count}-'
        substring = f'.{count}-'
        files_with_prefix_or_substring = any(fn.startswith(prefix) for fn in os.listdir(directory))
        files_two = any(substring in fn for fn in os.listdir(directory))
        if files_with_prefix_or_substring or files_two:
            pass
        else:
            print(f"count is {count}")
            return count  # Return the first available number
        count += 1

def get_next_face(current_face):
    face_order = ['front', 'left', 'down']
    current_index = face_order.index(current_face)
    return face_order[(current_index + 1) % len(face_order)]

def draw_square(event, x, y, flags, param):
    global ix, iy, drawing, squares, current_face, square_counter, frame

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = frame.copy()  # Use the globally defined frame
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Selected Image', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(frame, (ix, iy), (x, y), (0, 255, 0), 2)
        width = abs(x - ix)
        height = abs(y - iy)

        square_id = f"{current_face[0].upper()}{square_counter[current_face]}"
        squares[current_face].append((square_id, ix, iy, width, height))

        print(f'"{square_id}": ({ix}, {iy}, {width}, {height}),')

        square_counter[current_face] += 1
        cv2.imshow('Selected Image', frame)

        if square_counter[current_face] > 9:
            current_face = get_next_face(current_face)
            print(f"Switched to {current_face} face")

# Function to open file dialog and select an image
def select_image():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.tif")],
    )
    root.destroy()
    return file_path

# Load the image using file dialog
image_path = select_image()
if not image_path:
    print("No image selected. Exiting.")
    exit()

frame = cv2.imread(image_path)
if frame is None:
    print("Error: Could not load the image")
    exit()

cv2.namedWindow('Selected Image')
cv2.setMouseCallback('Selected Image', draw_square)

while True:
    cv2.imshow('Selected Image', frame)
    k = cv2.waitKey(1) & 0xFF

    if k == ord('q'):
        break

print(squares)

polygons = {}

for direction, items in squares.items():
    for item in items:
        key = item[0]  # The text part ('F1', 'L1', etc.)
        value = item[1:]  # The rest of the tuple
        polygons[key] = value

grid_labels = ['F', 'L', 'D']
current_file_path = os.path.abspath(__file__)
parent_directory = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), "testing")
starting_set_number = get_next_set_number(parent_directory)
'''
for grid_index, grid_label in enumerate(grid_labels):
    print(f"grid index is {grid_index}")
    for i in range(3):
        for j in range(3):
            number = grid_index * 9 + i * 3 + j
            region_key = f'{grid_label}{3 * i + j + 1}'
            if region_key in polygons:
                x, y, w, h = polygons[region_key]
                roi = frame[y:y+h, x:x+w]
                filename = f"{parent_directory}\{colors_list[number]}.{starting_set_number}-{grid_index + 1}-{region_key}.png"
                cv2.imwrite(filename, roi)
                print(f"Saved: {filename}")

for (x, y, w, h) in polygons.values():
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
cv2.imshow('Final Image with Regions', frame)
cv2.waitKey(0)
'''

cv2.destroyAllWindows()
