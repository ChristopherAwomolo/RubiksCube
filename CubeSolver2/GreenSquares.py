import cv2
import numpy as np
import json

# Initialize the list to store all quadrilaterals' points
all_quadrilaterals = []
current_points = []

# Define the callback function for mouse events
def mouse_callback(event, x, y, flags, param):
    global current_points, all_quadrilaterals
    if event == cv2.EVENT_LBUTTONDOWN:
        # Store the point where the mouse is clicked
        current_points.append((x, y))
        # If four points are clicked, store the quadrilateral and reset current_points
        if len(current_points) == 4:
            all_quadrilaterals.append(current_points)
            current_points = []

def draw_quadrilaterals(frame):
    # Draw all stored quadrilaterals on the frame for visualization
    for quadrilateral in all_quadrilaterals:
        cv2.polylines(frame, [np.array(quadrilateral)], isClosed=True, color=(0, 255, 0), thickness=2)


def save_quadrilaterals(frame):
    for i, quadrilateral in enumerate(all_quadrilaterals):
        # Create a mask for the quadrilateral
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [np.array(quadrilateral)], 255)

        # Extract the region of interest using the mask
        roi = cv2.bitwise_and(frame, frame, mask=mask)

        # Get the bounding box of the quadrilateral to crop the ROI
        x, y, w, h = cv2.boundingRect(np.array(quadrilateral))
        cropped_roi = roi[y:y + h, x:x + w]

        # Save the cropped ROI
        cv2.imwrite(f'quadrilateral_{i}.png', cropped_roi)

    # Save the quadrilateral points to a text file
    with open('quadrilaterals.txt', 'w') as f:
        json.dump(all_quadrilaterals, f)


def load_quadrilaterals():
    global all_quadrilaterals
    try:
        with open('quadrilaterals.txt', 'r') as f:
            all_quadrilaterals = json.load(f)
    except FileNotFoundError:
        all_quadrilaterals = []


# Capture video from webcam using DirectShow
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Change the argument to 'your_video_file.mp4' for a video file

# Create a window and set the mouse callback function
cv2.namedWindow("Video")
cv2.setMouseCallback("Video", mouse_callback)

# Load existing quadrilaterals from file
load_quadrilaterals()

while True:
    # Read a frame from the video
    ret, frame = cap.read()
    if not ret:
        break

    # Create a copy of the frame for visualization
    vis_frame = frame.copy()

    # Draw the quadrilaterals on the copy for visualization
    draw_quadrilaterals(vis_frame)

    # Display the visualization frame
    cv2.imshow("Video", vis_frame)

    # Check for key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' '):
        save_quadrilaterals(frame)

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
