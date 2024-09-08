import cv2
import time
import os

folder_one_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "full pictures", "v4-7-test")
os.makedirs(folder_one_path, exist_ok=True)

# Initialize the webcam (0 is the default camera)
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check if the webcam is opened correctly
if not cam.isOpened():
    print("Could not open webcam")
    exit()

# Warm up the camera by capturing a few frames with a delay
time.sleep(2)  # Wait for 2 seconds to allow the camera to adjust

for i in range(30):
    ret, frame = cam.read()
    if not ret:
        print("Failed to capture image")
        exit()

# Capture the final frame
ret, frame = cam.read()

# Check if the frame was captured successfully
if not ret:
    print("Failed to capture image")
    exit()

# Display the captured frame in a window
cv2.imshow("Captured Photo", frame)

# Wait for a key press to close the window
cv2.waitKey(0)

# Save the captured image to a file
cv2.imwrite(os.path.join(folder_one_path, "test-1-1.png"), frame)

# Release the webcam and close all windows
cam.release()
cv2.destroyAllWindows()

print("Photo saved as test-1-1.png")