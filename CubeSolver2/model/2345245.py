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
import pandas as pd
pd.set_option('display.width', 300)
pd.set_option('display.float_format', '{:,.4f}'.format)
pd.set_option('display.max_colwidth', 200)
import seaborn as sns
import tensorflow as tf
from sklearn import tree
from sklearn.tree import export_text
from joblib import dump, load
import cv2
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from PIL import Image
import ast

base_drive_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
training_data_dir = os.path.join(base_drive_dir, 'training')
testing_data_dir = os.path.join(base_drive_dir, 'testing')
version = 'v4-7'
model_dir = os.path.join(base_drive_dir, 'model')
dt_model_name = os.path.join(model_dir, 'decision_tree-' + version + '.joblib')
history_path = os.path.join(model_dir,'color_detection-' + version + '.history.pickle')
img_height = 96
img_width = 96

training_file_list = glob.glob(os.path.join(training_data_dir, '*png'))
print(training_file_list)
testing_file_list = glob.glob(os.path.join(testing_data_dir, '*png'))
print(training_file_list[0])

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
    return (labels, closest_color_labels)

(training_labels, training_closest_color_labels) = extract_labels(training_file_list)
(testing_labels, testing_closest_color_labels) = extract_labels(testing_file_list)

colors = list(set(training_labels))
colors.sort()
print(colors)
def label_to_idx(labels, to_be_converted):
  return [colors.index(x) for x in to_be_converted]

def confusion_matrix(ture_labels, predicted_labels):
    confusion_mtx = tf.math.confusion_matrix(ture_labels, predicted_labels)
    plt.figure(figsize=(10, 8)),
    sns.heatmap(confusion_mtx,xticklabels=colors,yticklabels=colors,annot=True, fmt='g')
    plt.xlabel('Closest RGB')
    plt.ylabel('Label')
    plt.show()

def show_diff(true_labels, predicts):
    diff = np.where(true_labels != predicts)
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
    (b, g, r) = palette[np.argmax(counts)]
    (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return (h * 360, s * 100, v * 100)

def generate_input_vector(file_list):
    inputs = []
    outputs = []
    for f in file_list:
        print(f)
        img = cv2.imread(f)
        (h, s, v) = get_dominant_hsv(img)
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
dump(clf, os.path.join(model_dir, dt_model_name))
clf = load(os.path.join(model_dir, dt_model_name))
(test_inputs, test_outputs) = generate_input_vector(testing_file_list)
predicts = clf.predict(test_inputs)
print(export_text(clf))
confusion_mtx = tf.math.confusion_matrix(test_outputs, predicts)
plt.figure(figsize=(10, 8)),
sns.heatmap(confusion_mtx,xticklabels=colors,yticklabels=colors,annot=True, fmt='g')
plt.xlabel('Predicted Label')
plt.ylabel('Label')
plt.show()
show_diff(test_outputs, predicts)
test_dir = os.path.join(base_drive_dir,"full pictures", "v4-7-test")
polygons = {}

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Image Classification", "Polygons.txt")) as file:
    for line in file:
        line = line.strip().rstrip(',')
        key_value = ast.literal_eval(f"{{{line}}}")
        polygons.update(key_value)

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
        inputs.append([h, s, v])
    predicts = model.predict(inputs)
    return (labels, predicts)

def test_full_picture(model, img_path):
    plt.imshow(Image.open(img_path))
    plt.show()
    #(labels, predicts) = get_predicts_and_labels_with_cnn(model, img_path)
    (labels, predicts) = get_predicts_and_labels(clf, img_path)
    label_to_predict = {}
    for i in range(len(labels)):
        #print('{}:{}'.format(labels[i], colors[tf.argmax(predicts[i], axis = 1)[0]]), predicts[i])
        #print('"{}":[{}],'.format(labels[i], ','.join('%0.4f' % x for x in predicts[i][0])))
        print('{}:{}'.format(labels[i], colors[predicts[i]], predicts[i]))
        label_to_predict[labels[i]] = predicts[i]
    return label_to_predict

def show_rect(img_path, label):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    (x, y, width, height) = polygons[label]
    rect = img[round(y): round(y)+ round(height), round(x): round(x) + round(width)]
    plt.imshow(rect)
    plt.show()
def show_polygons(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for label in polygons:
        (x, y, width, height) = polygons[label]
        center_x = x + width / 2
        center_y = y + height / 2
        cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0))
        plt.text(center_x, center_y, f"{colors[label_to_predict[label]]} {label}", horizontalalignment='center', verticalalignment='center', fontsize=6, color='white')
    plt.imshow(img)
    plt.show()

def plot_hsv_clusters(inputs, outputs):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    H = inputs[:, 0]  # Hue
    S = inputs[:, 1]  # Saturation
    V = inputs[:, 2]  # Value
    scatter = ax.scatter(H, S, V, c=outputs, cmap='viridis', s=50)
    ax.set_xlabel('Hue')
    ax.set_ylabel('Saturation')
    ax.set_zlabel('Value')
    ax.set_title('HSV Clustering of Data')
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=plt.cm.viridis(i / 5), markersize=10, label=colors[i]) for i in range(6)]
    ax.legend(handles=legend_elements, title="Colors")
    #legend1 = ax.legend(*scatter.legend_elements(), title="Classes")
    #ax.add_artist(legend1)
    plt.show()


clf = load(dt_model_name)
label_to_predict = test_full_picture(clf, os.path.join(test_dir, 'test-1-1.png'))
show_rect(os.path.join(test_dir, 'test-1-1.png'), 'L5')
show_polygons(os.path.join(test_dir, 'test-1-1.png'))
plot_hsv_clusters(np.array(inputs), np.array(outputs))