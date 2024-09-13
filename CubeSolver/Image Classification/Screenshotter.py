import cv2
filename = '../model/cubescreenshot.png'
# Open the webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Display the resulting frame
    cv2.imshow('Webcam', frame)

    # Wait for a key press
    key = cv2.waitKey(1) & 0xFF

    # If 's' key is pressed, save a screenshot
    if key == ord('s'):
        cv2.imwrite(filename, frame)
        print(f"Screenshot saved as {filename}")

    # If 'q' key is pressed, exit the loop
    elif key == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
