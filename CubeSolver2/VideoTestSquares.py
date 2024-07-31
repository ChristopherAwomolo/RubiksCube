import cv2
import numpy as np
import os

def set_exposure_manual(cap, exposure_value):
    # Set manual exposure if supported
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Usually 0.25 means manual mode
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure_value)

def adjust_saturation(frame, saturation_scale):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert BGR to HSV
    hsv = np.array(hsv, dtype=np.float64)  # Convert to float to prevent clipping issues
    hsv[..., 1] = hsv[..., 1] * saturation_scale  # Scale the saturation
    hsv[..., 1][hsv[..., 1] > 255] = 255  # Cap the values at 255
    hsv = np.array(hsv, dtype=np.uint8)  # Convert back to uint8
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)  # Convert back to BGR
    return frame

def get_next_photo_number(directory, prefix='photo_', extension='.jpg'):
    # Get the list of files in the directory
    files = os.listdir(directory)
    # Filter files with the specified prefix and extension
    photo_files = [f for f in files if f.startswith(prefix) and f.endswith(extension)]
    # Extract the numbers from the file names and find the highest number
    if photo_files:
        numbers = [int(f[len(prefix):-len(extension)]) for f in photo_files]
        return max(numbers) + 1
    else:
        return 1

def draw_squares(frame, squares):
    for square in squares:
        top_left = (square['x'], square['y'])
        bottom_right = (square['x'] + square['width'], square['y'] + square['height'])
        color = square.get('color', (0, 255, 0))
        thickness = square.get('thickness', 2)
        cv2.rectangle(frame, top_left, bottom_right, color, thickness)

def set_square_properties(squares, index, x, y, width, height):
    squares[index]['x'] = x
    squares[index]['y'] = y
    squares[index]['width'] = width
    squares[index]['height'] = height

def capture_squares(frame, squares, directory, prefix='square_'):
    for i, square in enumerate(squares):
        top_left = (square['x'], square['y'])
        bottom_right = (square['x'] + square['width'], square['y'] + square['height'])
        cropped_image = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        photo_filename = os.path.join(directory, f'{prefix}{i+1}.png')
        cv2.imwrite(photo_filename, cropped_image)
        print(f"Square {i+1} captured and saved as '{photo_filename}'")

# Directory to save photos
photo_directory = '.'

# Get the next photo number based on existing files
photo_counter = get_next_photo_number(photo_directory)

# Initialize squares with their positions and sizes
squares = [{'x': 20 * i, 'y': 20 * i, 'width': 50, 'height': 50} for i in range(27)]
start_num_list = [150, 200, 260]

for index, start_num in enumerate(start_num_list):
    # Calculate the vertical positions for squares
    vertical_positions = [140, 220, 300] if index == 0 else [160, 250, 340] if index == 1 else [200, 290, 380]

    # Loop through each vertical position
    for i, y in enumerate(vertical_positions):
        # Calculate the x position based on start_num and i
        x = start_num
        # Calculate the square number
        square_number = index * 3 + i
        # Set square properties
        set_square_properties(squares, square_number, x, y, 20, 20)
'''
# Manually program each of the 27 squares (example values provided, adjust as needed)
set_square_properties(squares, 0, 140, 120, 20, 20)
set_square_properties(squares, 1, 140, 210, 20, 20)
set_square_properties(squares, 2, 140, 300, 20, 20)

set_square_properties(squares, 3, 200, 160, 20, 20)
set_square_properties(squares, 4, 200, 250, 20, 20)
set_square_properties(squares, 5, 200, 340, 20, 20)

set_square_properties(squares, 6, 260, 200, 20, 20)
set_square_properties(squares, 7, 260, 290, 20, 20)
set_square_properties(squares, 8, 260, 380, 20, 20)
'''

set_square_properties(squares, 9, 340, 200, 20, 20)
set_square_properties(squares, 10, 340, 290, 20, 20)
set_square_properties(squares, 11, 340, 380, 20, 20)

set_square_properties(squares, 12, 400, 160, 20, 20)
set_square_properties(squares, 13, 400, 250, 20, 20)
set_square_properties(squares, 14, 400, 340, 20, 20)

set_square_properties(squares, 15, 460, 120, 20, 20)
set_square_properties(squares, 16, 460, 210, 20, 20)
set_square_properties(squares, 17, 460, 300, 20, 20)

set_square_properties(squares, 18, 290, 70, 10, 10)
set_square_properties(squares, 19, 400, 20, 20, 20)
set_square_properties(squares, 20, 10, 500, 20, 20)

set_square_properties(squares, 21, 120, 500, 20, 20)
set_square_properties(squares, 22, 210, 500, 20, 20)
set_square_properties(squares, 23, 290, 500, 20, 20)

set_square_properties(squares, 24, 10, 610, 20, 20)
set_square_properties(squares, 25, 80, 610, 20, 20)
set_square_properties(squares, 26, 140, 610, 20, 20)
# Open a connection to the webcam using DirectShow (0 is usually the built-in webcam)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Set manual exposure
exposure_value = -6  # Example value, adjust as needed
set_exposure_manual(cap, exposure_value)

# Set saturation scale (1.0 means no change, <1.0 means decrease, >1.0 means increase)
saturation_scale = 1.5  # Example value, adjust as needed

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        break

    # Adjust the saturation
    frame = adjust_saturation(frame, saturation_scale)

    # Draw the squares on the frame
    draw_squares(frame, squares)

    # Display the resulting frame
    cv2.imshow('Webcam', frame)

    # Check for key presses
    key = cv2.waitKey(1)

    # Break the loop on 'q' key press
    if key == ord('q'):
        break
    # Save a photo on 's' key press
    elif key == ord('s'):
        # Save the current frame with a unique name
        photo_filename = os.path.join(photo_directory, f'photo_{photo_counter}.jpg')
        cv2.imwrite(photo_filename, frame)
        print(f"Photo taken and saved as '{photo_filename}'")
        photo_counter += 1  # Increment the counter for the next photo
    # Capture images of squares on 'c' key press
    elif key == ord('c'):
        capture_squares(frame, squares, photo_directory)

# When everything done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()
