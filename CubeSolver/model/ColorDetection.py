import os
import colorsys
import datetime
import glob
import math
import numpy as np
import pathlib
import pickle
import random
import shutil
from zipfile import ZipFile
np.set_printoptions(formatter={'float_kind':lambda x: "%.4f" % x})
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
from tensorflow.keras.optimizers import Adam
import pandas as pd
import seaborn as sns
import cv2
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from PIL import Image
from sklearn import tree
from sklearn.tree import export_text
from joblib import dump, load
from mpl_toolkits.mplot3d import Axes3D
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


'''
Error images:
training:
R.11-3-R1.png
R.3-2-L9.png
R.3-3-R3.png
R.3-3-R8.png
R.3-3-R9.png

testing
R.1-2-L8.png
R.1-3-R7.png
R.2-2-L3.png
R.2-3-R2.png
R.7-3-D9.png
R.5-3-D7.png

R.4-2-L9.png
R.4-3-R8.png 
R.4-3-R9.png
R.5-1-F7.png
R.7-3-D9.png

'''

base_drive_dir = os.path.dirname(os.path.dirname(__file__))
training_data_dir = os.path.join(base_drive_dir, 'Training Data')
version = 'v4-7'
model_dir = os.path.join(base_drive_dir, 'model')
model_name = 'color_detection-' + version + '.h5'
dt_model_name = 'decision_tree-' + version + '.joblib'
img_height = 96
img_width = 96

pd.set_option('display.width', 300)
pd.set_option('display.float_format', '{:,.4f}'.format)
pd.set_option('display.max_colwidth', 200)

training_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'Training Data')
version = 'v4-7'
print(f"Checking if file exists at: {training_data_dir}")
print("File exists:", os.path.exists(training_data_dir))

training_file_list = glob.glob(os.path.join(training_data_dir, 'training', '*png'))
print(training_file_list)
testing_file_list = glob.glob(os.path.join(training_data_dir, 'testing','*png'))
print(testing_file_list)

def extract_labels(file_list):
  labels = []
  closest_color_labels = []
  for filename in file_list:
    img_fname = os.path.basename(filename)
    parts = img_fname.split('.')
    label = parts[0]
    if len(parts) == 7:
      closest_color_label = parts[1]
    else:
      closest_color_label = label
    labels.append(label)
    closest_color_labels.append(closest_color_label)

  print(f"labels {labels}")
  return (labels, closest_color_labels)

(training_labels, training_closest_color_labels) = extract_labels(training_file_list)
(testing_labels, testing_closest_color_labels) = extract_labels(testing_file_list)

colors = list(set(training_labels))
colors.sort()
print(colors)

label_to_color = {
    0: 'blue',
    1: 'green',
    2: 'orange',
    3: 'red',
    4: 'white',
    5: 'yellow'
}
def label_to_idx(labels, to_be_converted):
    return [colors.index(x) for x in to_be_converted]

def confusion_matrix(ture_labels, predicted_labels):
    # Confusion matrix for closest RGB color and true color
    confusion_mtx = tf.math.confusion_matrix(ture_labels, predicted_labels)
    plt.figure(figsize=(10, 8)),
    sns.heatmap(confusion_mtx, xticklabels=colors, yticklabels=colors, annot=True, fmt='g')
    plt.xlabel('Closest RGB')
    plt.ylabel('Label')
    plt.show()

def show_diff(true_labels, predicts):
    diff = np.where(true_labels != predicts)
    plt.figure()
    num = len(diff[0])
    cols = 3
    rows = math.ceil(num / 3)
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10), squeeze=False)
    fig_idx = 0
    for _, idx in np.ndenumerate(diff):
        r = fig_idx // cols
        c = fig_idx % cols
        fig_idx += 1
    ax = axes[r][c]
    ax.imshow(Image.open(testing_file_list[idx]))
    ax.set_title('{}:True:{},Predicted:{}'.format(os.path.basename(testing_file_list[idx])[0:9], colors[true_labels[idx]], colors[predicts[idx]]))
    ax.axis('off')
    plt.show()

def get_dominant_bgr(img):
    average = img.mean(axis=0).mean(axis=0)
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    # dominant BGR
    (b, g, r) = palette[np.argmax(counts)]
    return (b, g, r)

def get_dominant_hsv(img):
    average = img.mean(axis=0).mean(axis=0)
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    # dominant BGR
    (b, g, r) = palette[np.argmax(counts)]

    # convert BGR to HSV
    (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return (h * 360, s * 100, v * 100)

def generate_input_vector(file_list):
    inputs = []
    outputs = []
    for f in file_list:
        img = cv2.imread(f)
        (h, s, v) = get_dominant_hsv(img)
        print(f"{f} - {(h, s, v)}")
        label = os.path.basename(f).split('.')[0]
        inputs.append([h, s, v])
        if label in colors:
            outputs.append(colors.index(label))
        else:
            outputs.append('')

    return (inputs, outputs)

(inputs, outputs) = generate_input_vector(training_file_list)

clf = tree.DecisionTreeClassifier()
clf = clf.fit(inputs, outputs)
dump(clf, 'decision_tree-v4-7.joblib')

clf = load('decision_tree-v4-7.joblib')
# test on test set
(test_inputs, test_outputs) = generate_input_vector(testing_file_list)
predicts = clf.predict(test_inputs)

print(export_text(clf))

print(f"length of outputs is {len(test_outputs)}")

confusion_mtx = tf.math.confusion_matrix(test_outputs, predicts)
plt.figure(figsize=(10, 8)),
sns.heatmap(confusion_mtx,xticklabels=colors,yticklabels=colors, annot=True, fmt='g')
plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.show()

#show_diff(test_outputs, predicts)

test_dir = os.path.join(base_drive_dir, 'full pictures', version + '-test')

polygons = {"F1": (195, 157, 28, 26),
"F2": (244, 136, 33, 25),
"F3": (296, 118, 27, 23),
"F4": (238, 178, 37, 28),
"F5": (294, 157, 33, 24),
"F6": (341, 135, 33, 25),
"F7": (296, 204, 39, 32),
"F8": (349, 175, 41, 32),
"F9": (394, 153, 31, 27),

"L1": (184, 312, 27, 26),
"L2": (179, 253, 26, 34),
"L3": (169, 195, 33, 36),
"L4": (228, 340, 26, 28),
"L5": (219, 282, 38, 37),
"L6": (213, 213, 34, 39),
"L7": (269, 375, 31, 28),
"L8": (271, 315, 36, 38),
"L9": (266, 244, 40, 45),

"D1": (320, 255, 36, 34),
"D2": (376, 220, 31, 35),
"D3": (420, 192, 27, 29),
"D4": (316, 316, 37, 33),
"D5": (369, 283, 31, 28),
"D6": (418, 253, 24, 26),
"D7": (326, 374, 27, 24),
"D8": (370, 340, 28, 24),
"D9": (407, 310, 26, 21)}

def get_predicts_and_labels_with_cnn(model, img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    labels = []
    predicts = []
    for label in polygons:
        (x, y, width, height) = polygons[label]
        rect = img[round(y):round(y)+round(height), round(x):round(x)+round(width)]
        rect = cv2.resize(rect, (img_width, img_height))
        resized = tf.reshape(rect, [-1, 96, 96, 3])
        labels.append(label)
        predict = model.predict(resized)
        predicts.append(np.argmax(predict))
    return (labels, predicts)

def get_predicts_and_labels(model, img_path):
    img = cv2.imread(img_path)
    labels = []
    inputs = []
    predicts = []
    for label in polygons:
        labels.append(label)
        (x, y, width, height) = polygons[label]
        rect = img[round(y):round(y)+round(height), round(x):round(x)+round(width)]
        (h, s, v) = get_dominant_hsv(rect)
        #print(label, (h, s, v))
        inputs.append([h, s, v])
    predicts = model.predict(inputs)
    return (labels, predicts)

def test_full_picture(model, img_path):
    #plt.imshow(Image.open(img_path))
    #(labels, predicts) = get_predicts_and_labels_with_cnn(model, img_path)
    (labels, predicts) = get_predicts_and_labels(clf, img_path)
    label_to_predict = {}
    for i in range(len(labels)):
        #print('{}:{}'.format(labels[i], colors[tf.argmax(predicts[i], axis = 1)[0]]), predicts[i])
        #print('"{}":[{}],'.format(labels[i], ','.join('%0.4f' % x for x in predicts[i][0])))
        #print('{}:{}'.format(labels[i], colors[predicts[i]], predicts[i]))
        label_to_predict[labels[i]] = predicts[i]
    return label_to_predict

#model = load_model(f'{model_name}', compile=False)
label_to_predict = test_full_picture(clf, 'cubescreenshot.png') #os.path.join(test_dir, '0-2.png')

def show_polygons(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for label in polygons:
        (x, y, width, height) = polygons[label]
        center_x = x + width / 2
        center_y = y + height / 2
        cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0))
        plt.text(center_x,center_y, f"{colors[label_to_predict[label]]} {label}", horizontalalignment='center', verticalalignment='center', fontsize=6, color='white')
    plt.imshow(img)

show_polygons('cubescreenshot.png')
#show_polygons(os.path.join(test_dir, 'test-1-1.png'))

def plot_hsv_clusters(inputs, outputs):
    # Create a 3D scatter plot
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Extract H, S, and V from inputs
    H = inputs[:, 0]  # Hue
    S = inputs[:, 1]  # Saturation
    V = inputs[:, 2]  # Value

    colors_t = [label_to_color[label] for label in outputs]
    scatter = ax.scatter(H, S, V, c=colors_t, s=50)
    #scatter = ax.scatter(H, S, V, c=outputs, cmap=colors_t, s=50)

    # Add axis labels
    ax.set_xlabel('Hue')
    ax.set_ylabel('Saturation')
    ax.set_zlabel('Value')
    ax.set_title('HSV Clustering of Data')

    # Add color bar to show which class each color corresponds to
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=label_to_color[i], markersize=10, label=colors[i]) for i in range(6)]
    ax.legend(handles=legend_elements, title="Colors")
    #legend1 = ax.legend(*scatter.legend_elements(), title="Classes")
    #ax.add_artist(legend1)
    plt.show()

# Example usage assuming 'inputs' is an array of HSV values and 'outputs' are the corresponding labels
plot_hsv_clusters(np.array(inputs), np.array(outputs))

