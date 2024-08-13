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

# Define the polygon regions for faces U, L, and R only
polygons = {
    'U1': (184, 160, 37, 12),
    'U2': (247, 146, 32, 32),
    'U3': (297, 137, 32, 32),
    'U4': (226, 172, 32, 32),
    'U5': (295, 163, 32, 32),  # Center of top face
    'U6': (348, 146, 24, 19),
    'U7': (279, 191, 32, 32),
    'U8': (348, 176, 32, 32),
    'U9': (408, 164, 32, 32),
    'L1': (151, 198, 26, 26),
    'L2': (198, 212, 32, 32),
    'L3': (243, 231, 32, 32),
    'L4': (154, 263, 32, 32),
    'L5': (198, 289, 32, 32),  # Center of left face
    'L6': (249, 314, 32, 32),
    'L7': (159, 331, 32, 32),
    'L8': (201, 359, 32, 32),
    'L9': (265, 394, 32, 35),
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

color_map = {
    'B': 'blue',
    'G': 'green',
    'O': 'orange',
    'R': 'red',
    'W': 'white',
    'Y': 'yellow'
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
        cv2.rectangle(img, (x, y), (x + width, y + height), (0, 0, 255), 2)
        prediction_text = str(label_to_predict[label])
        cv2.putText(img, prediction_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    return img

def draw_cube_visualization(label_to_predict):
    face_mapping = {
        'U': [[colors[label_to_predict[f'U{i}']] for i in range(1, 4)],
              [colors[label_to_predict[f'U{i}']] for i in range(4, 7)],
              [colors[label_to_predict[f'U{i}']] for i in range(7, 10)]],
        'L': [[colors[label_to_predict[f'L{i}']] for i in range(1, 4)],
              [colors[label_to_predict[f'L{i}']] for i in range(4, 7)],
              [colors[label_to_predict[f'L{i}']] for i in range(7, 10)]],
        'R': [[colors[label_to_predict[f'R{i}']] for i in range(1, 4)],
              [colors[label_to_predict[f'R{i}']] for i in range(4, 7)],
              [colors[label_to_predict[f'R{i}']] for i in range(7, 10)]],
    }

    plt.figure(figsize=(6, 6))
    plt.axis('off')

    # Draw the top face (U)
    for i in range(3):
        for j in range(3):
            color = color_map[face_mapping['U'][i][j]]
            plt.text(j, 6 - i, face_mapping['U'][i][j], ha='center', va='center', fontsize=18, bbox=dict(facecolor=color, edgecolor='black'))

    # Draw the left (L) and right (R) faces
    for i in range(3):
        for j in range(3):
            color_left = color_map[face_mapping['L'][i][j]]
            color_right = color_map[face_mapping['R'][i][j]]
            plt.text(j - 3, 3 - i, face_mapping['L'][i][j], ha='center', va='center', fontsize=18, bbox=dict(facecolor=color_left, edgecolor='black'))
            plt.text(j + 3, 3 - i, face_mapping['R'][i][j], ha='center', va='center', fontsize=18, bbox=dict(facecolor=color_right, edgecolor='black'))

    plt.xlim(-4, 4)
    plt.ylim(-4, 8)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

# Start the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture_interval = 5  # seconds
last_capture_time = time.time()

# Placeholder for the last processed frame
last_processed_frame = None

while True:
    # Capture frame from the camera
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

        # Show polygons with predictions
        last_processed_frame = show_polygons(frame.copy(), label_to_predict)

        # Draw 2D cube visualization based on predictions
        draw_cube_visualization(label_to_predict)

    # Display the last processed frame
    if last_processed_frame is not None:
        cv2.imshow('Webcam - Color Predictions', last_processed_frame)
    else:
        cv2.imshow('Webcam - Color Predictions', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
