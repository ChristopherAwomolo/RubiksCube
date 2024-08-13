import cv2
import time
import joblib
import numpy as np
import colorsys

# Load the trained decision tree model
model = joblib.load('decision_tree-v4-7.joblib')

# Define the colors and sort them
colors = ['B', 'G', 'O', 'R', 'W', 'Y']
colors.sort()

# Define the polygon regions
polygons = {
    'U1': (177, 157, 32, 32),
    'U2': (247, 146, 32, 32),
    'U3': (297, 137, 32, 32),
    'U4': (226, 172, 32, 32),
    'U5': (295, 163, 32, 32),  # Center of top face
    'U6': (348, 148, 32, 32),
    'U7': (279, 191, 32, 32),
    'U8': (348, 176, 32, 32),
    'U9': (408, 164, 32, 32),
    'L1': (149, 186, 32, 32),
    'L2': (198, 212, 32, 32),
    'L3': (243, 231, 32, 32),
    'L4': (154, 263, 32, 32),
    'L5': (198, 289, 32, 32),  # Center of left face
    'L6': (249, 314, 32, 32),
    'L7': (159, 331, 32, 32),
    'L8': (201, 359, 32, 32),
    'L9': (246, 390, 32, 32),
    'R1': (312, 233, 32, 32),
    'R2': (375, 219, 32, 32),
    'R3': (432, 202, 32, 32),
    'R4': (311, 325, 32, 32),
    'R5': (375, 299, 32, 32),  # Center of right face
    'R6': (427, 273, 32, 32),
    'R7': (312, 402, 32, 32),
    'R8': (366, 366, 32, 32),
    'R9': (417, 341, 32, 32),
}


def get_dominant_hsv(img):
    average = img.mean(axis=0).mean(axis=0)
    pixels = np.float32(img.reshape(-1, 3))
    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    # Dominant BGR
    (b, g, r) = palette[np.argmax(counts)]
    # Convert BGR to HSV
    (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (h * 360, s * 100, v * 100)

def get_predicts_and_labels(model, img):
    labels = []
    inputs = []
    predicts = []
    for label in polygons:
        labels.append(label)
        (x, y, width, height) = polygons[label]
        rect = img[round(y):round(y) + round(height), round(x):round(x) + round(width)]
        (h, s, v) = get_dominant_hsv(rect)
        inputs.append([h, s, v])
    predicts = model.predict(inputs)
    return (labels, predicts)

def show_polygons(img, label_to_predict):
    for label in polygons:
        (x, y, width, height) = polygons[label]
        # Draw a rectangle around the polygon
        cv2.rectangle(img, (x, y), (x + width, y + height), (0, 0, 255), 2)
        # Convert the prediction to a string
        prediction_text = str(label_to_predict[label])
        # Put the prediction text near the rectangle
        cv2.putText(img, prediction_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    return img

# Start the webcam
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
capture_interval = 5  # seconds
last_capture_time1 = time.time()
last_capture_time2 = time.time()

# Placeholder for the last processed frames
last_processed_frame1 = None
last_processed_frame2 = None

while True:
    # Capture frames from both cameras
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    if not ret1 or not ret2:
        break

    # Get the current time
    current_time = time.time()

    # Check if 5 seconds have passed for the first camera
    if current_time - last_capture_time1 >= capture_interval:
        # Update the last capture time
        last_capture_time1 = current_time

        # Get the predictions for the current frame from camera 1
        labels1, predicts1 = get_predicts_and_labels(model, frame1)
        label_to_predict1 = dict(zip(labels1, predicts1))

        # Show polygons with predictions for camera 1
        last_processed_frame1 = show_polygons(frame1.copy(), label_to_predict1)

    # Check if 5 seconds have passed for the second camera
    if current_time - last_capture_time2 >= capture_interval:
        # Update the last capture time
        last_capture_time2 = current_time

        # Get the predictions for the current frame from camera 2
        labels2, predicts2 = get_predicts_and_labels(model, frame2)
        label_to_predict2 = dict(zip(labels2, predicts2))

        # Show polygons with predictions for camera 2
        last_processed_frame2 = show_polygons(frame2.copy(), label_to_predict2)

    # Display the last processed frames side by side if available
    if last_processed_frame1 is not None and last_processed_frame2 is not None:
        combined_frame = np.hstack((last_processed_frame1, last_processed_frame2))
        cv2.imshow('Dual Webcam - Color Predictions', combined_frame)
    else:
        # Display the current frames side by side if no processed frame is available yet
        combined_frame = np.hstack((frame1, frame2))
        cv2.imshow('Dual Webcam - Color Predictions', combined_frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the captures and close windows
cap1.release()
cap2.release()
cv2.destroyAllWindows()
