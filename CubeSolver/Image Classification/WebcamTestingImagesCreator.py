import cv2
import os
import time
# Initialize global variables
squares = {'front': [], 'left': [], 'down': [], 'up': [], 'right': [], 'bottom': []}
drawing = False  # True if the mouse is pressed
ix, iy = -1, -1
current_face = 'front'
square_counter = {'front': 1, 'left': 1, 'down': 1, 'up': 1, 'right': 1, 'bottom': 1}
first_phase_complete = False
frame = None  # Define the frame globally

colors = str(input('Write the colors of the cube: '))
colors_list = list(colors)
def get_next_set_number(directory):
    count = 1  # Start checking from 1
    while True:
        # Define the prefix and the substring to check
        prefix = f'{count}-'
        substring = f'.{count}-'
        # Check if there are files with either the prefix or the substring
        files_with_prefix_or_substring = any(fn.startswith(prefix) for fn in os.listdir(directory))
        files_two = any(substring in fn for fn in os.listdir(directory))
        if files_with_prefix_or_substring == True or files_two == True:
            pass
        else:
            print(f"count is {count}")
            return count  # Return the first available number
        count += 1

# Determine the starting set number based on existing files

# Function to get the next face in the sequence
def get_next_face(current_face):
    face_order = ['front', 'left', 'down']# 'up', 'right', 'bottom']
    current_index = face_order.index(current_face)
    return face_order[(current_index + 1) % len(face_order)]


# Mouse callback function
def draw_square(event, x, y, flags, param):
    global ix, iy, drawing, squares, current_face, square_counter, frame

    # When the left mouse button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    # When the mouse is moved with the left button pressed down
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = frame.copy()  # Use the globally defined frame
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Webcam', img_copy)

    # When the left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(frame, (ix, iy), (x, y), (0, 255, 0), 2)
        width = abs(x - ix)
        height = abs(y - iy)

        square_id = f"{current_face[0].upper()}{square_counter[current_face]}"
        squares[current_face].append((square_id, ix, iy, width, height))

        #with open('Polygons.txt', "w") as file:
        #    file.write(f"'{square_id}': ({ix}, {iy}, {width}, {height}),")
        print(f"'{square_id}': ({ix}, {iy}, {width}, {height}),")

        square_counter[current_face] += 1
        cv2.imshow('Webcam', frame)

        # Switch to the next face if 9 squares are drawn
        if square_counter[current_face] > 9:
            current_face = get_next_face(current_face)
            print(f"Switched to {current_face} face")


# Function to capture squares for a set of faces
def capture_squares_for_faces(cap, face_keys):
    global current_face, first_phase_complete, frame

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        cv2.imshow('Webcam', frame)

        k = cv2.waitKey(1) & 0xFF

        # Switch between faces manually using keys
        for key in face_keys:
            if k == ord(key[0]):
                current_face = key
                print(f"Switched to {key} face")

        # Check if all squares are drawn for current set of faces
        if all(len(squares[face]) == 9 for face in face_keys):
            break

        # Press 'q' to exit early
        if k == ord('q'):
            first_phase_complete = True
            break


# First phase: Capture squares for front, left, down using VideoCapture(0) with CAP_DSHOW
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow('Webcam')
cv2.setMouseCallback('Webcam', draw_square)

capture_squares_for_faces(cap, ['front', 'left', 'down'])
print(squares)
# Release first camera
polygons = {}

# Loop through each key in the original dictionary
for direction, items in squares.items():
    for item in items:
        key = item[0]  # The text part ('F1', 'L1', etc.)
        value = item[1:]  # The rest of the tuple
        polygons[key] = value

# Labels and starting set number
grid_labels = ['F', 'L', 'D']  # Labels corresponding to the face of the cube
starting_set_number = 1         # Starting number for the sets

# Create output directory if it doesn't exist
current_file_path = os.path.abspath(__file__)
parent_directory = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), "testing")
starting_set_number = get_next_set_number(parent_directory)

time.sleep(2)

# Wait for 2 seconds to let the camera adjust to the brightness
for i in range(30):
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        exit()

# Capture a single frame
ret, frame = cap.read()

if not ret:
    print("Error: Failed to capture image")
else:
    # Naming the files based on the grid_index and coordinates
    for grid_index, grid_label in enumerate(grid_labels):
        print(f"grid index is {grid_index}")
        for i in range(3):
            for j in range(3):
                number = grid_index * 9 + i * 3 + j
                # Calculate the region index based on grid index, i, and j
                region_key = f'{grid_label}{3 * i + j + 1}'
                if region_key in polygons:
                    x, y, w, h = polygons[region_key]
                    roi = frame[y:y+h, x:x+w]
                    filename = f"{parent_directory}\{colors_list[number]}.{starting_set_number}-{grid_index + 1}-{region_key}.png"
                    cv2.imwrite(filename, roi)
                    print(f"Saved: {filename}")

    # Display the resulting frame with rectangles around the regions
    for (x, y, w, h) in polygons.values():
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow('Webcam Frame with Regions', frame)

    # Wait for a key press to close the windows
    cv2.waitKey(0)

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()