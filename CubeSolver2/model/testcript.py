import cv2
import time
import joblib
import numpy as np
import colorsys
import matplotlib.pyplot as plt

# Load the trained decision tree model
model = joblib.load('decision_tree-v4-7.joblib')

# Define the colors and sort them
colors = ['B', 'G', 'O', 'R', 'W', 'Y']
colors.sort()

# Define the polygon regions
polygons = {
    'U1': (177, 157, 19, 19),
    'U2': (247, 146, 19, 19),
    'U3': (297, 137, 19, 19),
    'U4': (226, 172, 19, 19),
    'U5': (295, 163, 19, 19),  # Center of top face
    'U6': (348, 148, 19, 19),
    'U7': (279, 191, 19, 19),
    'U8': (348, 176, 19, 19),
    'U9': (408, 164, 19, 19),
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

def getNumberAndColour():
    for i in range(len(labels)):
        # print('{}:{}'.format(labels[i], colors[tf.argmax(predicts[i], axis = 1)[0]]), predicts[i])
        # print('"{}":[{}],'.format(labels[i], ','.join('%0.4f' % x for x in predicts[i][0])))
        print('{}:{}'.format(labels[i], colors[predicts[i]], predicts[i]))
        print(f"labels i is {labels[i]}")
        print(f"color predicts i is {colors[predicts[i]]}")
def show_polygons(img, label_to_predict):
    for label in polygons:
        (x, y, width, height) = polygons[label]
        cv2.rectangle(img, (x, y), (x + width, y + height), (0, 0, 255), 2)
        cv2.putText(img, colors[label_to_predict[label]], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    return img

# Start the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture_interval = 5  # seconds
last_capture_time = time.time()

# Placeholder for the last processed frame
last_processed_frame = None

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Get the current time
    current_time = time.time()

    # Check if 5 seconds have passed
    if current_time - last_capture_time >= capture_interval:
        # Update the last capture time
        last_capture_time = current_time

        # Get the predictions for the current frame
        labels, predicts = get_predicts_and_labels(model, frame)
        label_to_predict = dict(zip(labels, predicts))
        getNumberAndColour()

        # Show polygons with predictions
        last_processed_frame = show_polygons(frame.copy(), label_to_predict)

    # Display the last processed frame (with predictions) if available
    if last_processed_frame is not None:
        cv2.imshow('Webcam - Color Predictions', last_processed_frame)
    else:
        # Display the current frame if no processed frame is available yet
        cv2.imshow('Webcam - Color Predictions', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
