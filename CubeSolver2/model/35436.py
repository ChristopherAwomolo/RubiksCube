import cv2
import time

# Initialize the webcam (0 is usually the default webcam)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Set the exposure (values may vary based on your camera hardware)
# cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # Lower value increases brightness (may vary by camera)

# You can also set brightness or other properties if supported by the camera
# cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)  # You can try values like 100-200

# Allow the camera some time to adjust
time.sleep(2)

# Capture multiple frames to let the camera adjust the exposure
for i in range(30):
    ret, frame = cap.read()

# Now capture the actual frame after the camera has adjusted
ret, frame = cap.read()

if ret:
    # Display the captured frame
    cv2.imshow('Captured Image', frame)

    # Save the image to disk
    cv2.imwrite('test-1-1.png', frame)
    print("Image saved as 'captured_image.jpg'")

    # Wait for any key to close the window
    cv2.waitKey(0)

# Release the webcam and close any open windows
cap.release()
cv2.destroyAllWindows()
