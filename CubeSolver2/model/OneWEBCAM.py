import cv2
import time
import joblib
import numpy as np
import colorsys
import matplotlib.pyplot as plt
import os
import ast
model = joblib.load('decision_tree-v4-7.joblib')
colors = ['B', 'G', 'O', 'R', 'W', 'Y']
colors.sort()
polygons = {}

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Image Classification", "Polygons.txt")) as file:
    for line in file:
        line = line.strip().rstrip(',')
        key_value = ast.literal_eval(f"{{{line}}}")
        polygons.update(key_value)

color_map = {
    'B': 'blue',
    'G': 'green',
    'O': 'orange',
    'R': 'red',
    'W': 'white',
    'Y': 'yellow'
}


def setup_camera_focus(cap):
    autofocus_supported = cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    if autofocus_supported:
        print("Autofocus disabled successfully")
    else:
        print("Autofocus disabling is not supported")
    focus_supported = cap.set(cv2.CAP_PROP_FOCUS, 50)  # Set focus to a specific level (adjust 10 to fit your needs)
    if focus_supported:
        print("Focus set successfully")
    else:
        print("Manual focus setting is not supported on this camera")

def get_dominant_hsv(img):
    average = img.mean(axis=0).mean(axis=0)
    pixels = np.float32(img.reshape(-1, 3))
    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    (b, g, r) = palette[np.argmax(counts)]
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
        'F': [[colors[label_to_predict[f'F{i}']] for i in range(1, 4)],
              [colors[label_to_predict[f'F{i}']] for i in range(4, 7)],
              [colors[label_to_predict[f'F{i}']] for i in range(7, 10)]],
        'L': [[colors[label_to_predict[f'L{i}']] for i in range(1, 4)],
              [colors[label_to_predict[f'L{i}']] for i in range(4, 7)],
              [colors[label_to_predict[f'L{i}']] for i in range(7, 10)]],
        'D': [[colors[label_to_predict[f'D{i}']] for i in range(1, 4)],
              [colors[label_to_predict[f'D{i}']] for i in range(4, 7)],
              [colors[label_to_predict[f'D{i}']] for i in range(7, 10)]],
    }
    plt.figure(figsize=(6, 6))
    plt.axis('off')
    for i in range(3):
        for j in range(3):
            color = color_map[face_mapping['F'][i][j]]
            plt.text(j, 6 - i, face_mapping['F'][i][j], ha='center', va='center', fontsize=18, bbox=dict(facecolor=color, edgecolor='black'))
    for i in range(3):
        for j in range(3):
            color_left = color_map[face_mapping['L'][i][j]]
            color_right = color_map[face_mapping['D'][i][j]]
            plt.text(j - 3, 3 - i, face_mapping['L'][i][j], ha='center', va='center', fontsize=18, bbox=dict(facecolor=color_left, edgecolor='black'))
            plt.text(j + 3, 3 - i, face_mapping['D'][i][j], ha='center', va='center', fontsize=18, bbox=dict(facecolor=color_right, edgecolor='black'))
    plt.xlim(-4, 4)
    plt.ylim(-4, 8)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
setup_camera_focus(cap)
capture_interval = 5  # seconds
last_capture_time = time.time()
last_processed_frame = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    current_time = time.time()
    if current_time - last_capture_time >= capture_interval:
        last_capture_time = current_time
        labels, predicts = get_predicts_and_labels(model, frame)
        label_to_predict = dict(zip(labels, predicts))
        last_processed_frame = show_polygons(frame.copy(), label_to_predict)
        draw_cube_visualization(label_to_predict)
    if last_processed_frame is not None:
        cv2.imshow('Webcam - Color Predictions', last_processed_frame)
    else:
        cv2.imshow('Webcam - Color Predictions', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
