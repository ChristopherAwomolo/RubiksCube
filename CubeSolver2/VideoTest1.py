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

# Directory to save photos
photo_directory = '.'

# Get the next photo number based on existing files
photo_counter = get_next_photo_number(photo_directory)

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

# When everything done, release the capture and close windows
cap.release()
cv2.destroyAllWindows()
