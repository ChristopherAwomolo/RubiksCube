import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import cv2
import imutils
import time
import joblib
import colorsys
import random
import kociemba

'''
To do list (easiest to hardest)

-Add more training data
-Make the GUI scalable and include a fullscreen in the dialog
-Make the waiting screens work for generating steps and solving the cube (not click based)
-Scrap current cube + make another cube which visualises the faces from the webcam
-Make the rubiks cube solve using kociemba
-Finish all of the settings work
 -Make Camera Settings for Camera 2
 -Make Camera Resolution for Camera 1
 -Make Camera Resolution for Camera 2
 -Make calibration squares for Camera 1
 -Make calibration squares for Camera 2

'''


class OpenGLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.lastPos = None
        self.rotation = [570.0, -46.0, 0]
        self.zoom = 1.3

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (w / h), 0.5, 40)
        glTranslatef(0.0, 0.0, -17.5)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glScalef(self.zoom, self.zoom, self.zoom)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        self.cube()

    def cube(self):
        cube_verts = (
            (3, -3, -3), (3, 3, -3), (-3, 3, -3), (-3, -3, -3),
            (3, -3, 3), (3, 3, 3), (-3, -3, 3), (-3, 3, 3)
        )
        cube_edges = (
            (0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
            (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)
        )
        cube_surfaces = (
            (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
            (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
        )

        colors = [
            (1, 1, 1),  # White
            (0, 0.318, 0.729),  # Blue
            (1, 0.835, 0),  # Yellow
            (0, 0.62, 0.376),  # Green
            (1, 0.345, 0),  # Orange
            (0.8, 0.118, 0.118)  # Red
        ]

        glBegin(GL_QUADS)
        for i, surface in enumerate(cube_surfaces):
            glColor3fv(colors[i])
            for vertex in surface:
                glVertex3fv(cube_verts[vertex])
        glEnd()

        glBegin(GL_LINES)
        glColor3fv((0, 0, 0))
        for edge in cube_edges:
            for vertex in edge:
                glVertex3fv(cube_verts[vertex])
        glEnd()

        glLineWidth(5)
        glColor3fv((0, 0, 0))  # Grid lines color: black

        for i in range(3):
            for j in range(3):
                # X-Y plane (Front and Back faces)
                glBegin(GL_LINE_LOOP)
                glVertex3f(3 - i * 2, 3 - j * 2, 3)
                glVertex3f(3 - (i + 1) * 2, 3 - j * 2, 3)
                glVertex3f(3 - (i + 1) * 2, 3 - (j + 1) * 2, 3)
                glVertex3f(3 - i * 2, 3 - (j + 1) * 2, 3)
                glEnd()

                glBegin(GL_LINE_LOOP)
                glVertex3f(3 - i * 2, 3 - j * 2, -3)
                glVertex3f(3 - (i + 1) * 2, 3 - j * 2, -3)
                glVertex3f(3 - (i + 1) * 2, 3 - (j + 1) * 2, -3)
                glVertex3f(3 - i * 2, 3 - (j + 1) * 2, -3)
                glEnd()

                # X-Z plane (Top and Bottom faces)
                glBegin(GL_LINE_LOOP)
                glVertex3f(3 - i * 2, 3, 3 - j * 2)
                glVertex3f(3 - (i + 1) * 2, 3, 3 - j * 2)
                glVertex3f(3 - (i + 1) * 2, 3, 3 - (j + 1) * 2)
                glVertex3f(3 - i * 2, 3, 3 - (j + 1) * 2)
                glEnd()

                glBegin(GL_LINE_LOOP)
                glVertex3f(3 - i * 2, -3, 3 - j * 2)
                glVertex3f(3 - (i + 1) * 2, -3, 3 - j * 2)
                glVertex3f(3 - (i + 1) * 2, -3, 3 - (j + 1) * 2)
                glVertex3f(3 - i * 2, -3, 3 - (j + 1) * 2)
                glEnd()

                # Y-Z plane (Left and Right faces)
                glBegin(GL_LINE_LOOP)
                glVertex3f(3, 3 - i * 2, 3 - j * 2)
                glVertex3f(3, 3 - (i + 1) * 2, 3 - j * 2)
                glVertex3f(3, 3 - (i + 1) * 2, 3 - (j + 1) * 2)
                glVertex3f(3, 3 - i * 2, 3 - (j + 1) * 2)
                glEnd()

                glBegin(GL_LINE_LOOP)
                glVertex3f(-3, 3 - i * 2, 3 - j * 2)
                glVertex3f(-3, 3 - (i + 1) * 2, 3 - j * 2)
                glVertex3f(-3, 3 - (i + 1) * 2, 3 - (j + 1) * 2)
                glVertex3f(-3, 3 - i * 2, 3 - (j + 1) * 2)
                glEnd()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotation[1] += dx
            self.rotation[0] += dy
        elif event.buttons() & Qt.RightButton:
            self.rotation[2] += dx
        self.lastPos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.update()


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.settingCameraOption = "Camera1"
        self.counter = 0
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(571, 407)
        Dialog.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.capture_interval = 5
        self.stackedWidget = QtWidgets.QStackedWidget(Dialog)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 571, 407))
        self.stackedWidget.setObjectName("stackedWidget")
        self.last_capture_time = time.time()
        self.ctimer = QTimer()
        self.ctimer.timeout.connect(self.screen2viewCam)

        # First Screen
        self.screen1 = QtWidgets.QWidget()
        self.setupScreen1(self.screen1)
        self.stackedWidget.addWidget(self.screen1)

        # Second Screen
        self.screen2 = QtWidgets.QWidget()
        self.setupScreen2(self.screen2)
        self.stackedWidget.addWidget(self.screen2)

        self.screen3 = QtWidgets.QWidget()
        self.setupScreen3(self.screen3)
        self.stackedWidget.addWidget(self.screen3)

        self.screen4 = QtWidgets.QWidget()
        self.setupScreen4(self.screen4)
        self.stackedWidget.addWidget(self.screen4)

        self.screen5 = QtWidgets.QWidget()
        self.setupScreen5(self.screen5)
        self.stackedWidget.addWidget(self.screen5)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.model = joblib.load('model/decision_tree-v4-7.joblib')

        self.colors = ['B', 'G', 'O', 'R', 'W', 'Y']
        self.cam1faces = ['F', 'L', 'D']
        self.cam2faces = ['U', 'R']
        self.colors.sort()
        self.total_squares_per_color = 9  # Each color should appear exactly 9 times

        self.polygons = {

            'F1': (162, 56, 28, 22),
            'F2': (250, 44, 23, 18),
            'F3': (317, 30, 28, 20),
            'F4': (211, 83, 35, 29),
            'F5': (304, 65, 33, 27),
            'F6': (369, 50, 33, 27),
            'F7': (263, 114, 47, 40),
            'F8': (364, 90, 45, 37),
            'F9': (449, 72, 33, 29),

            'L1': (129, 106, 23, 32),
            'L2': (169, 139, 30, 37),
            'L3': (223, 176, 41, 51),
            'L4': (137, 191, 23, 36),
            'L5': (177, 228, 37, 41),
            'L6': (232, 272, 44, 54),
            'L7': (145, 264, 27, 38),
            'L8': (181, 308, 32, 35),
            'L9': (237, 360, 34, 39),

            'D1': (294, 181, 47, 46),
            'D2': (393, 154, 43, 41),
            'D3': (464, 129, 41, 42),
            'D4': (293, 276, 44, 47),
            'D5': (379, 245, 39, 39),
            'D6': (452, 210, 34, 44),
            'D7': (300, 359, 46, 46),
            'D8': (374, 317, 39, 42),
            'D9': (433, 292, 39, 38),

            'U1': (286, 83, 65, 67),
            'U2': (391, 42, 57, 56),
            'U3': (482, 17, 43, 51),
            'U4': (284, 203, 67, 68),
            'U5': (392, 170, 48, 45),
            'U6': (469, 128, 41, 42),
            'U7': (301, 306, 54, 54),
            'U8': (389, 257, 46, 45),
            'U9': (457, 217, 41, 41),

            'R1': (63, 14, 34, 42),
            'R2': (122, 51, 40, 44),
            'R3': (190, 80, 60, 63),
            'R4': (85, 122, 33, 50),
            'R5': (142, 163, 42, 49),
            'R6': (212, 209, 56, 63),
            'R7': (100, 212, 42, 57),
            'R8': (160, 252, 42, 55),
            'R9': (220, 307, 36, 43),

        }

        self.color_map = {
            'B': 'blue',
            'G': 'green',
            'O': 'orange',
            'R': 'red',
            'W': 'white',
            'Y': 'yellow'
        }

        self.color_to_face = {
            1: 'D',  # Blue ->  Down
            2: 'U',  # Green -> Up
            3: 'F',  # Orange -> Front
            4: 'B',  # Red -> Back
            5: 'L',  # White -> Left
            6: 'R'  # Yellow ->  Right
        }

        self.face_order = 'ULFRBD'.split()
        self.face_positions = {
            'U': ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9'],
            'L': ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9'],
            'F': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9'],
            'R': ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9'],
            'B': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'],
            'D': ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9'],
        }

    def solveCube(self, cube_dict):
        cube_string = ''
        for face in self.face_order:
            for i in range(1, 10):
                key = f'{face}{i}'
                color_index = cube_dict[key]
                cube_string += self.colors[color_index]

        if self.missing_dict == "pass":
            pass
        else:
            solution = kociemba.solve(cube_string)
            print(solution)

    def get_dominant_hsv(self, img):
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

    def get_predicts_and_labels(self, model, img, camnum):
        labels = []
        inputs = []
        predicts = []
        for label in self.polygons:
            if camnum == 1:
                if label.startswith(tuple(self.cam1faces)):
                    labels.append(label)
                    (x, y, width, height) = self.polygons[label]
                    rect = img[round(y):round(y) + round(height), round(x):round(x) + round(width)]
                    (h, s, v) = self.get_dominant_hsv(rect)
                    inputs.append([h, s, v])
            elif camnum == 2:
                if label.startswith(tuple(self.cam2faces)):
                    labels.append(label)
                    (x, y, width, height) = self.polygons[label]
                    rect = img[round(y):round(y) + round(height), round(x):round(x) + round(width)]
                    (h, s, v) = self.get_dominant_hsv(rect)
                    inputs.append([h, s, v])
            else:
                pass

        predicts = model.predict(inputs)
        return (labels, predicts)

    def update_cube_colors(self, label_to_predict):
        color_mapping = {
            'B': "background-color: rgb(0, 0, 255);",  # Blue
            'G': "background-color: rgb(0, 255, 0);",  # Green
            'O': "background-color: rgb(255, 165, 0);",  # Orange
            'R': "background-color: rgb(255, 0, 0);",  # Red
            'W': "background-color: rgb(255, 255, 255);",  # White
            'Y': "background-color: rgb(255, 255, 0);"  # Yellow
        }

        self.L1.setStyleSheet(color_mapping[self.colors[label_to_predict['L1']]])
        self.L2.setStyleSheet(color_mapping[self.colors[label_to_predict['L2']]])
        self.L3.setStyleSheet(color_mapping[self.colors[label_to_predict['L3']]])
        self.L4.setStyleSheet(color_mapping[self.colors[label_to_predict['L4']]])
        self.L5.setStyleSheet(color_mapping[self.colors[label_to_predict['L5']]])
        self.L6.setStyleSheet(color_mapping[self.colors[label_to_predict['L6']]])
        self.L7.setStyleSheet(color_mapping[self.colors[label_to_predict['L7']]])
        self.L8.setStyleSheet(color_mapping[self.colors[label_to_predict['L8']]])
        self.L9.setStyleSheet(color_mapping[self.colors[label_to_predict['L9']]])

        self.F1.setStyleSheet(color_mapping[self.colors[label_to_predict['F1']]])
        self.F2.setStyleSheet(color_mapping[self.colors[label_to_predict['F2']]])
        self.F3.setStyleSheet(color_mapping[self.colors[label_to_predict['F3']]])
        self.F4.setStyleSheet(color_mapping[self.colors[label_to_predict['F4']]])
        self.F5.setStyleSheet(color_mapping[self.colors[label_to_predict['F5']]])
        self.F6.setStyleSheet(color_mapping[self.colors[label_to_predict['F6']]])
        self.F7.setStyleSheet(color_mapping[self.colors[label_to_predict['F7']]])
        self.F8.setStyleSheet(color_mapping[self.colors[label_to_predict['F8']]])
        self.F9.setStyleSheet(color_mapping[self.colors[label_to_predict['F9']]])

        self.D1.setStyleSheet(color_mapping[self.colors[label_to_predict['D1']]])
        self.D2.setStyleSheet(color_mapping[self.colors[label_to_predict['D2']]])
        self.D3.setStyleSheet(color_mapping[self.colors[label_to_predict['D3']]])
        self.D4.setStyleSheet(color_mapping[self.colors[label_to_predict['D4']]])
        self.D5.setStyleSheet(color_mapping[self.colors[label_to_predict['D5']]])
        self.D6.setStyleSheet(color_mapping[self.colors[label_to_predict['D6']]])
        self.D7.setStyleSheet(color_mapping[self.colors[label_to_predict['D7']]])
        self.D8.setStyleSheet(color_mapping[self.colors[label_to_predict['D8']]])
        self.D9.setStyleSheet(color_mapping[self.colors[label_to_predict['D9']]])

        self.U1.setStyleSheet(color_mapping[self.colors[label_to_predict['U1']]])
        self.U2.setStyleSheet(color_mapping[self.colors[label_to_predict['U2']]])
        self.U3.setStyleSheet(color_mapping[self.colors[label_to_predict['U3']]])
        self.U4.setStyleSheet(color_mapping[self.colors[label_to_predict['U4']]])
        self.U5.setStyleSheet(color_mapping[self.colors[label_to_predict['U5']]])
        self.U6.setStyleSheet(color_mapping[self.colors[label_to_predict['U6']]])
        self.U7.setStyleSheet(color_mapping[self.colors[label_to_predict['U7']]])
        self.U8.setStyleSheet(color_mapping[self.colors[label_to_predict['U8']]])
        self.U9.setStyleSheet(color_mapping[self.colors[label_to_predict['U9']]])

        self.R1.setStyleSheet(color_mapping[self.colors[label_to_predict['R1']]])
        self.R2.setStyleSheet(color_mapping[self.colors[label_to_predict['R2']]])
        self.R3.setStyleSheet(color_mapping[self.colors[label_to_predict['R3']]])
        self.R4.setStyleSheet(color_mapping[self.colors[label_to_predict['R4']]])
        self.R5.setStyleSheet(color_mapping[self.colors[label_to_predict['R5']]])
        self.R6.setStyleSheet(color_mapping[self.colors[label_to_predict['R6']]])
        self.R7.setStyleSheet(color_mapping[self.colors[label_to_predict['R7']]])
        self.R8.setStyleSheet(color_mapping[self.colors[label_to_predict['R8']]])
        self.R9.setStyleSheet(color_mapping[self.colors[label_to_predict['R9']]])

        self.B1.setStyleSheet(color_mapping[self.colors[label_to_predict['B1']]])
        self.B2.setStyleSheet(color_mapping[self.colors[label_to_predict['B2']]])
        self.B3.setStyleSheet(color_mapping[self.colors[label_to_predict['B3']]])
        self.B4.setStyleSheet(color_mapping[self.colors[label_to_predict['B4']]])
        self.B5.setStyleSheet(color_mapping[self.colors[label_to_predict['B5']]])
        self.B6.setStyleSheet(color_mapping[self.colors[label_to_predict['B6']]])
        self.B7.setStyleSheet(color_mapping[self.colors[label_to_predict['B7']]])
        self.B8.setStyleSheet(color_mapping[self.colors[label_to_predict['B8']]])
        self.B9.setStyleSheet(color_mapping[self.colors[label_to_predict['B9']]])

    def setupScreen1(self, screen):
        self.openGLWidget = OpenGLWidget(screen)  # Use the OpenGLWidget subclass
        self.openGLWidget.setGeometry(QtCore.QRect(150, 120, 241, 230))  # 170, 160, 211, 181
        self.openGLWidget.setAutoFillBackground(False)
        self.openGLWidget.setObjectName("openGLWidget")

        font = QtGui.QFont()
        font.setFamily("Big John")
        font.setPointSize(35)
        self.RubikLabel = QtWidgets.QLabel(screen)
        self.RubikLabel.setGeometry(QtCore.QRect(100, 10, 351, 51))
        self.RubikLabel.setFont(font)
        self.RubikLabel.setStyleSheet("color: white;")
        self.RubikLabel.setAutoFillBackground(False)
        self.RubikLabel.setObjectName("RubikLabel")
        self.RubikLabel.setText("Rubiks Cube")

        self.pushButton = QtWidgets.QPushButton(screen)
        self.pushButton.setGeometry(QtCore.QRect(0, 350, 571, 61))
        font = QtGui.QFont()
        font.setFamily("Northstar Laser Italic")
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("tap here to continue")
        self.pushButton.raise_()
        self.pushButton.clicked.connect(self.showScreen2)

        self.SolverLabel = QtWidgets.QLabel(screen)
        self.SolverLabel.setGeometry(QtCore.QRect(170, 65, 201, 51))
        font = QtGui.QFont()
        font.setFamily("Big John")
        font.setPointSize(35)
        self.SolverLabel.setFont(font)
        self.SolverLabel.setAutoFillBackground(False)
        self.SolverLabel.setObjectName("SolverLabel")
        self.SolverLabel.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")
        self.SolverLabel.setText("Solver")
        self.retranslateUi(screen)

    def setupScreen2(self, screen):
        self.backButton = QtWidgets.QPushButton(screen)
        self.backButton.setGeometry(QtCore.QRect(265, 363, 60, 28))
        font = QtGui.QFont()
        font.setFamily("Bowlby One SC")
        font.setPointSize(10)
        self.backButton.setFont(font)
        self.backButton.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.backButton.setFlat(False)
        self.backButton.setObjectName("backButton")
        self.backButton.setText("Back")
        self.backButton.clicked.connect(self.showScreen1)

        self.SolveButton = QtWidgets.QPushButton(screen)
        self.SolveButton.setGeometry(QtCore.QRect(330, 330, 221, 61))
        font = QtGui.QFont()
        font.setFamily("Bowlby One SC")
        font.setPointSize(22)
        self.SolveButton.setFont(font)
        self.SolveButton.setStyleSheet("background-color: rgb(10, 132, 18);\n""color: rgb(0, 0, 0);")
        self.SolveButton.setFlat(False)
        self.SolveButton.setObjectName("SolveButton")
        self.SolveButton.setText("Solve!")
        self.SolveButton.clicked.connect(self.showScreen3)

        self.settingsButton = QtWidgets.QPushButton(screen)
        self.settingsButton.setGeometry(QtCore.QRect(330, 290, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(16)
        self.settingsButton.setFont(font)
        self.settingsButton.setStyleSheet(
            "background-color: rgb(10, 132, 18);\n""background-color: rgb(163, 163, 163);")
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setText("Settings")
        self.settingsButton.clicked.connect(self.showScreen5)

        self.openGLWidget = OpenGLWidget(screen)
        self.openGLWidget.setGeometry(QtCore.QRect(330, 20, 211, 191))
        self.openGLWidget.setAutoFillBackground(False)
        self.openGLWidget.setObjectName("openGLWidget")

        self.Video_1Label = QtWidgets.QLabel(screen)
        self.Video_1Label.setGeometry(QtCore.QRect(180, 10, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Unispace")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.Video_1Label.setFont(font)
        self.Video_1Label.setObjectName("Video_1Label")
        self.Video_1Label.setText("Video 1")
        self.Video_1Label.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.Detected_Video1 = QtWidgets.QLabel(screen)
        self.Detected_Video1.setGeometry(QtCore.QRect(200, 50, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.Detected_Video1.setFont(font)
        self.Detected_Video1.setObjectName("Detected_Video1")
        self.Detected_Video1.setText("Detected")
        self.Detected_Video1.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.Num27Video1 = QtWidgets.QLabel(screen)
        self.Num27Video1.setGeometry(QtCore.QRect(240, 80, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.Num27Video1.setFont(font)
        self.Num27Video1.setObjectName("Num27Video1")
        self.Num27Video1.setText("/27")
        self.Num27Video1.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.NumDetected_Video1 = QtWidgets.QLabel(screen)
        self.NumDetected_Video1.setGeometry(QtCore.QRect(221, 80, 18, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.NumDetected_Video1.setFont(font)
        self.NumDetected_Video1.setObjectName("NumDetected_Video1")
        self.NumDetected_Video1.setText("0")
        self.NumDetected_Video1.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.Video_2Label = QtWidgets.QLabel(screen)
        self.Video_2Label.setGeometry(QtCore.QRect(20, 120, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Unispace")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.Video_2Label.setFont(font)
        self.Video_2Label.setObjectName("Video_2Label")
        self.Video_2Label.setText("Video 2")
        self.Video_2Label.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.Detected_Video2 = QtWidgets.QLabel(screen)
        self.Detected_Video2.setGeometry(QtCore.QRect(40, 160, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.Detected_Video2.setFont(font)
        self.Detected_Video2.setObjectName("Detected_Video2")
        self.Detected_Video2.setText("Detected")
        self.Detected_Video2.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.Num27Video2 = QtWidgets.QLabel(screen)
        self.Num27Video2.setGeometry(QtCore.QRect(80, 190, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.Num27Video2.setFont(font)
        self.Num27Video2.setObjectName("Num27Video2")
        self.Num27Video2.setText("/27")
        self.Num27Video2.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.NumDetected_Video2 = QtWidgets.QLabel(screen)
        self.NumDetected_Video2.setGeometry(QtCore.QRect(59, 190, 18, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.NumDetected_Video2.setFont(font)
        self.NumDetected_Video2.setObjectName("NumDetected_Video2")
        self.NumDetected_Video2.setText("0")
        self.NumDetected_Video2.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        cam1_x, cam1_y, cam1_width, cam1_height = 5, 5, 150, 105
        self.WebcamFrame = QtWidgets.QLabel(screen)
        self.WebcamFrame.setGeometry(QtCore.QRect(cam1_x, cam1_y, cam1_width, cam1_height))
        self.WebcamFrame.setObjectName("WebcamFrame")

        self.WebcamFrame_2 = QtWidgets.QLabel(screen)
        self.WebcamFrame_2.setGeometry(QtCore.QRect(cam1_x + cam1_width, cam1_y + cam1_height, cam1_width, cam1_height))
        self.WebcamFrame_2.setObjectName("WebcamFrame_2")

        self.CubeReady = QtWidgets.QLabel(screen)
        self.CubeReady.setGeometry(QtCore.QRect(330, 221, 221, 20))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(12)
        self.CubeReady.setFont(font)
        self.CubeReady.setStyleSheet("background-color: rgb(255, 255, 0);\n")
        self.CubeReady.setObjectName("CubeReady")
        self.CubeReady.setText("Cube Ready For Solving!")

        self.CameraButton = QtWidgets.QPushButton(screen)
        self.CameraButton.setGeometry(QtCore.QRect(330, 250, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(16)
        self.CameraButton.setFont(font)
        self.CameraButton.setStyleSheet("background-color: rgb(163, 163, 163);")
        self.CameraButton.setObjectName("CameraButton")
        self.CameraButton.setText("Show Camera")
        self.CameraButton.clicked.connect(self.controlTimer)

        self.gridLayoutWidget = QtWidgets.QWidget(screen)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 220, 251, 173))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.B7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B7.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B7.setText("")
        self.B7.setObjectName("B7")
        self.gridLayout_6.addWidget(self.B7, 2, 0, 1, 1)
        self.B8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B8.setText("")
        self.B8.setObjectName("B8")
        self.gridLayout_6.addWidget(self.B8, 2, 1, 1, 1)
        self.B5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B5.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B5.setText("")
        self.B5.setObjectName("B5")
        self.gridLayout_6.addWidget(self.B5, 1, 1, 1, 1)
        self.B4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B4.setText("")
        self.B4.setObjectName("B4")
        self.gridLayout_6.addWidget(self.B4, 1, 0, 1, 1)
        self.B2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B2.setText("")
        self.B2.setObjectName("B2")
        self.gridLayout_6.addWidget(self.B2, 0, 1, 1, 1)
        self.B3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B3.setText("")
        self.B3.setObjectName("B3")
        self.gridLayout_6.addWidget(self.B3, 0, 2, 1, 1)
        self.B6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B6.setText("")
        self.B6.setObjectName("B6")
        self.gridLayout_6.addWidget(self.B6, 1, 2, 1, 1)
        self.B9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B9.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B9.setText("")
        self.B9.setObjectName("B9")
        self.gridLayout_6.addWidget(self.B9, 2, 2, 1, 1)
        self.B1 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.B1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.B1.setText("")
        self.B1.setObjectName("B1")
        self.gridLayout_6.addWidget(self.B1, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_6, 2, 4, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.U5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U5.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U5.setText("")
        self.U5.setObjectName("U5")
        self.gridLayout_2.addWidget(self.U5, 1, 1, 1, 1)
        self.U4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U4.setText("")
        self.U4.setObjectName("U4")
        self.gridLayout_2.addWidget(self.U4, 1, 0, 1, 1)
        self.U2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U2.setText("")
        self.U2.setObjectName("U2")
        self.gridLayout_2.addWidget(self.U2, 0, 1, 1, 1)
        self.U3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U3.setText("")
        self.U3.setObjectName("U3")
        self.gridLayout_2.addWidget(self.U3, 0, 2, 1, 1)
        self.U6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U6.setText("")
        self.U6.setObjectName("U6")
        self.gridLayout_2.addWidget(self.U6, 1, 2, 1, 1)
        self.U9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U9.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U9.setText("")
        self.U9.setObjectName("U9")
        self.gridLayout_2.addWidget(self.U9, 2, 2, 1, 1)
        self.U1 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U1.setText("")
        self.U1.setObjectName("U1")
        self.gridLayout_2.addWidget(self.U1, 0, 0, 1, 1)
        self.U8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U8.setText("")
        self.U8.setObjectName("U8")
        self.gridLayout_2.addWidget(self.U8, 2, 1, 1, 1)
        self.U7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.U7.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.U7.setText("")
        self.U7.setObjectName("U7")
        self.gridLayout_2.addWidget(self.U7, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 1, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.F7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F7.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F7.setText("")
        self.F7.setObjectName("F7")
        self.gridLayout_4.addWidget(self.F7, 2, 0, 1, 1)
        self.F8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F8.setText("")
        self.F8.setObjectName("F8")
        self.gridLayout_4.addWidget(self.F8, 2, 1, 1, 1)
        self.F5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F5.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F5.setText("")
        self.F5.setObjectName("F5")
        self.gridLayout_4.addWidget(self.F5, 1, 1, 1, 1)
        self.F4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F4.setText("")
        self.F4.setObjectName("F4")
        self.gridLayout_4.addWidget(self.F4, 1, 0, 1, 1)
        self.F3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F3.setText("")
        self.F3.setObjectName("F3")
        self.gridLayout_4.addWidget(self.F3, 0, 2, 1, 1)
        self.F6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F6.setText("")
        self.F6.setObjectName("F6")
        self.gridLayout_4.addWidget(self.F6, 1, 2, 1, 1)
        self.F9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F9.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F9.setText("")
        self.F9.setObjectName("F9")
        self.gridLayout_4.addWidget(self.F9, 2, 2, 1, 1)
        self.F1 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F1.setText("")
        self.F1.setObjectName("F1")
        self.gridLayout_4.addWidget(self.F1, 0, 0, 1, 1)
        self.F2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.F2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.F2.setText("")
        self.F2.setObjectName("F2")
        self.gridLayout_4.addWidget(self.F2, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_4, 2, 1, 1, 1)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.L7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L7.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L7.setText("")
        self.L7.setObjectName("L7")
        self.gridLayout_7.addWidget(self.L7, 2, 0, 1, 1)
        self.L8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L8.setText("")
        self.L8.setObjectName("L8")
        self.gridLayout_7.addWidget(self.L8, 2, 1, 1, 1)
        self.L5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L5.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L5.setText("")
        self.L5.setObjectName("L5")
        self.gridLayout_7.addWidget(self.L5, 1, 1, 1, 1)
        self.L4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L4.setText("")
        self.L4.setObjectName("L4")
        self.gridLayout_7.addWidget(self.L4, 1, 0, 1, 1)
        self.L2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L2.setText("")
        self.L2.setObjectName("L2")
        self.gridLayout_7.addWidget(self.L2, 0, 1, 1, 1)
        self.L6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L6.setText("")
        self.L6.setObjectName("L6")
        self.gridLayout_7.addWidget(self.L6, 1, 2, 1, 1)
        self.L9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L9.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L9.setText("")
        self.L9.setObjectName("L9")
        self.gridLayout_7.addWidget(self.L9, 2, 2, 1, 1)
        self.L1 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L1.setText("")
        self.L1.setObjectName("L1")
        self.gridLayout_7.addWidget(self.L1, 0, 0, 1, 1)
        self.L3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.L3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.L3.setText("")
        self.L3.setObjectName("L3")
        self.gridLayout_7.addWidget(self.L3, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_7, 2, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.D7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D7.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D7.setText("")
        self.D7.setObjectName("D7")
        self.gridLayout_3.addWidget(self.D7, 2, 0, 1, 1)
        self.D8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D8.setText("")
        self.D8.setObjectName("D8")
        self.gridLayout_3.addWidget(self.D8, 2, 1, 1, 1)
        self.D5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D5.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D5.setText("")
        self.D5.setObjectName("D5")
        self.gridLayout_3.addWidget(self.D5, 1, 1, 1, 1)
        self.D4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D4.setText("")
        self.D4.setObjectName("D4")
        self.gridLayout_3.addWidget(self.D4, 1, 0, 1, 1)
        self.D2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D2.setText("")
        self.D2.setObjectName("D2")
        self.gridLayout_3.addWidget(self.D2, 0, 1, 1, 1)
        self.D3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D3.setText("")
        self.D3.setObjectName("D3")
        self.gridLayout_3.addWidget(self.D3, 0, 2, 1, 1)
        self.D6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D6.setText("")
        self.D6.setObjectName("D6")
        self.gridLayout_3.addWidget(self.D6, 1, 2, 1, 1)
        self.D9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D9.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D9.setText("")
        self.D9.setObjectName("D9")
        self.gridLayout_3.addWidget(self.D9, 2, 2, 1, 1)
        self.D1 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.D1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.D1.setText("")
        self.D1.setObjectName("D1")
        self.gridLayout_3.addWidget(self.D1, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 3, 1, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.R7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R7.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R7.setText("")
        self.R7.setObjectName("R7")
        self.gridLayout_5.addWidget(self.R7, 2, 0, 1, 1)
        self.R8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R8.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R8.setText("")
        self.R8.setObjectName("R8")
        self.gridLayout_5.addWidget(self.R8, 2, 1, 1, 1)
        self.R5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R5.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R5.setText("")
        self.R5.setObjectName("R5")
        self.gridLayout_5.addWidget(self.R5, 1, 1, 1, 1)
        self.R4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R4.setText("")
        self.R4.setObjectName("R4")
        self.gridLayout_5.addWidget(self.R4, 1, 0, 1, 1)
        self.R2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R2.setText("")
        self.R2.setObjectName("R2")
        self.gridLayout_5.addWidget(self.R2, 0, 1, 1, 1)
        self.R3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R3.setText("")
        self.R3.setObjectName("R3")
        self.gridLayout_5.addWidget(self.R3, 0, 2, 1, 1)
        self.R6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R6.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R6.setText("")
        self.R6.setObjectName("R6")
        self.gridLayout_5.addWidget(self.R6, 1, 2, 1, 1)
        self.R9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R9.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R9.setText("")
        self.R9.setObjectName("R9")
        self.gridLayout_5.addWidget(self.R9, 2, 2, 1, 1)
        self.R1 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.R1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.R1.setText("")
        self.R1.setObjectName("R1")
        self.gridLayout_5.addWidget(self.R1, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_5, 2, 3, 1, 1)

    def setupScreen3(self, screen):

        self.openGLWidget = OpenGLWidget(screen)  # Use the OpenGLWidget subclass
        self.openGLWidget.setGeometry(QtCore.QRect(80, 20, 400, 300))  # 170, 160, 211, 181
        self.openGLWidget.setAutoFillBackground(False)
        self.openGLWidget.setObjectName("openGLWidget")

        self.exitButton = QtWidgets.QPushButton(screen)
        self.exitButton.setGeometry(QtCore.QRect(10, 360, 111, 31))
        font = QtGui.QFont()
        font.setFamily("Bowlby One SC")
        font.setPointSize(16)
        self.exitButton.setFont(font)
        self.exitButton.setStyleSheet("background-color: rgb(255, 0, 0);\n")
        self.exitButton.setObjectName("exitButton")
        self.exitButton.setText("Exit")
        self.exitButton.raise_()
        self.exitButton.setHidden(True)
        self.exitButton.clicked.connect(self.exitScript)
        self.retranslateUi(screen)

        self.stepsButton = QtWidgets.QPushButton(screen)
        self.stepsButton.setGeometry(QtCore.QRect(440, 360, 111, 31))
        font = QtGui.QFont()
        font.setFamily("Bowlby One SC")
        font.setPointSize(16)
        self.stepsButton.setFont(font)
        self.stepsButton.setStyleSheet("background-color: rgb(75, 75, 75);\n")
        self.stepsButton.setObjectName("stepsButton")
        self.stepsButton.setText("Steps")
        self.stepsButton.raise_()
        self.stepsButton.setHidden(True)
        self.retranslateUi(screen)

        self.generatingButton = QtWidgets.QPushButton(screen)
        self.generatingButton.setGeometry(QtCore.QRect(170, 360, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(16)
        self.generatingButton.setFont(font)
        self.generatingButton.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")
        self.generatingButton.setObjectName("generatingButton")
        self.generatingButton.setText("Generating steps...")
        self.generatingButton.raise_()
        self.generatingButton.clicked.connect(self.changeText)
        self.retranslateUi(screen)

    def setupScreen4(self, screen):
        self.cubeSolveButton = QtWidgets.QPushButton(screen)
        self.cubeSolveButton.setGeometry(QtCore.QRect(70, 30, 431, 181))
        font = QtGui.QFont()
        font.setFamily("Bowlby One SC")
        font.setPointSize(36)
        self.cubeSolveButton.setFont(font)
        self.cubeSolveButton.setStyleSheet("background-color: rgb(11, 177, 86);")
        self.cubeSolveButton.setObjectName("cubeSolveButton")
        self.cubeSolveButton.setText("Solve Cube!")
        self.cubeSolveButton.clicked.connect(self.showScreen3)

        self.pushButton_2 = QtWidgets.QPushButton(screen)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 330, 171, 51))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("background-color: rgb(152, 154, 149);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Back to Home")
        self.pushButton_2.clicked.connect(self.backtoHome)

        self.ETALabel = QtWidgets.QLabel(screen)
        self.ETALabel.setGeometry(QtCore.QRect(120, 240, 401, 51))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(40)
        font.setBold(False)
        font.setWeight(50)
        self.ETALabel.setFont(font)
        self.ETALabel.setObjectName("ETALabel")
        self.ETALabel.setText("ETA: 7.0313s")
        self.ETALabel.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")

        self.solveCubeQuit = QtWidgets.QPushButton(screen)
        self.solveCubeQuit.setGeometry(QtCore.QRect(430, 330, 121, 51))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.solveCubeQuit.setFont(font)
        self.solveCubeQuit.setStyleSheet("background-color: rgb(175, 4, 35);")
        self.solveCubeQuit.setObjectName("solveCubeQuit")
        self.solveCubeQuit.setText("Quit")
        self.solveCubeQuit.clicked.connect(self.exitScript)

    def setupScreen5(self, screen):
        self.main_layout = QtWidgets.QHBoxLayout(screen)
        self.left_layout = QtWidgets.QGridLayout(screen)
        self.WebcamSettingsFrame = QtWidgets.QLabel(screen)
        self.WebcamSettingsFrame.setFixedSize(200, 100)  # Set the size of the webcam display
        self.WebcamSettingsFrame.setStyleSheet("background-color: black;")  # Background color before webcam is loaded
        self.left_layout.addWidget(self.WebcamSettingsFrame, 0, 0)

        self.button_camera = QtWidgets.QPushButton("Camera", screen)
        self.button_camera.setStyleSheet("background-color: white; color: black;")
        self.left_layout.addWidget(self.button_camera, 1, 0)
        self.button_camera.clicked.connect(self.change_to_camera_1)

        self.button_another = QtWidgets.QPushButton("Camera 2", screen)
        self.button_another.setStyleSheet("background-color: white; color: black;")
        self.left_layout.addWidget(self.button_another, 2, 0)
        self.button_another.clicked.connect(self.change_to_camera_2)

        self.back_button = QtWidgets.QPushButton("Back", screen)
        self.back_button.setStyleSheet("background-color: red; color: white;")
        self.back_button.clicked.connect(self.settingsBack)
        self.left_layout.addWidget(self.back_button, 3, 0)

        self.stack = QtWidgets.QStackedWidget(screen)

        self.camera_settings_widget = QtWidgets.QWidget(screen)
        self.camera_settings_layout = QtWidgets.QVBoxLayout(self.camera_settings_widget)
        self.scroll_area_1 = QtWidgets.QScrollArea(screen)
        self.scroll_area_widget_1 = QtWidgets.QWidget(screen)
        self.scroll_area_layout_1 = QtWidgets.QVBoxLayout(self.scroll_area_widget_1)

        self.change_settings_button = QtWidgets.QPushButton("Change Camera Settings", screen)
        self.change_settings_button.setStyleSheet("background-color: white; color: black;")
        self.change_settings_button.clicked.connect(self.openCameraSettings)
        self.change_resolution_button = QtWidgets.QPushButton("Change Camera Resolution", screen)
        self.change_resolution_button.setStyleSheet("background-color: white; color: black;")
        self.scroll_area_layout_1.addWidget(self.change_settings_button)
        self.scroll_area_layout_1.addWidget(self.change_resolution_button)

        for i in range(15):
            self.button = QtWidgets.QPushButton(f"Additional Setting {i + 1}", screen)
            self.button.setStyleSheet("background-color: white; color: black;")
            self.scroll_area_layout_1.addWidget(self.button)

        self.scroll_area_1.setWidget(self.scroll_area_widget_1)
        self.scroll_area_1.setWidgetResizable(True)
        self.camera_settings_layout.addWidget(self.scroll_area_1)

        self.another_widget = QtWidgets.QWidget(screen)
        self.another_layout = QtWidgets.QVBoxLayout(self.another_widget)
        self.scroll_area_2 = QtWidgets.QScrollArea(screen)
        self.scroll_area_widget_2 = QtWidgets.QWidget(screen)
        self.scroll_area_layout_2 = QtWidgets.QVBoxLayout(self.scroll_area_widget_2)

        for i in range(20):
            self.button = QtWidgets.QPushButton(f"Option {i + 1} for Another", screen)
            self.button.setStyleSheet("background-color: white; color: black;")
            self.scroll_area_layout_2.addWidget(self.button)

        self.scroll_area_2.setWidget(self.scroll_area_widget_2)
        self.scroll_area_2.setWidgetResizable(True)
        self.another_layout.addWidget(self.scroll_area_2)

        self.stack.addWidget(self.camera_settings_widget)  # Index 0
        self.stack.addWidget(self.another_widget)  # Index 1

        self.stack.setCurrentIndex(0)

        self.button_camera.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.button_another.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        self.main_layout.addLayout(self.left_layout, 1)  # Left grid layout takes 1/4th of space
        self.main_layout.addWidget(self.stack, 3)  # Stacked widget takes 3/4th of space

    def openCameraSettings(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_SETTINGS, 1)
        else:
            self.controlTimer()

    def showScreen1(self):
        self.stackedWidget.setCurrentWidget(self.screen1)

    def settingsBack(self):
        self.controlTimer()
        self.stackedWidget.setCurrentWidget(self.screen2)

    def backtoHome(self):
        self.counter = -1
        self.exitButton.setHidden(True)
        self.stepsButton.setHidden(True)
        self.changeText()
        self.showScreen2()

    def showScreen2(self):
        self.stackedWidget.setCurrentWidget(self.screen2)

    def showScreen3(self):
        self.stackedWidget.setCurrentWidget(self.screen3)

    def exitScript(self):
        self.counter = -1
        self.exitButton.setHidden(True)
        self.stepsButton.setHidden(True)
        self.changeText()
        self.showScreen1()

    def showScreen4(self):
        self.stackedWidget.setCurrentWidget(self.screen4)

    def showScreen5(self):
        self.stackedWidget.setCurrentWidget(self.screen5)

    def changeNumDetected(self):
        self.NumDetected_Video1.setText(str(len(self.label_to_predict)))
        self.NumDetected_Video2.setText(str(len(self.label_to_predict2)))

    def getMissingSquares(self, cube_dict):
        diction_colors = dict(zip(range(len(self.colors)), self.colors))
        color_count = {color: 0 for color in range(6)}
        for color in cube_dict.values():
            if color in color_count:
                color_count[color] += 1
        missing_colors = {color: self.total_squares_per_color - count for color, count in color_count.items()}
        bottom_face_positions = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
        missing_colors_list = []
        for color, missing_count in missing_colors.items():
            missing_colors_list.extend([color] * missing_count)
        if len(missing_colors_list) != len(bottom_face_positions):
            print("Mismatch between number of missing colors and number of positions on the bottom face")
            # return "pass"
        center_pieces = ['U5', 'F5', 'L5', 'R5', 'D5']
        used_center_colors = set(cube_dict.get(pos, None) for pos in center_pieces if cube_dict.get(pos) is not None)
        all_colors = set(range(6))
        unused_colors = all_colors - used_center_colors
        if len(unused_colors) != 1:
            print("There should be exactly one unused color for the center piece")
        unused_center_color = unused_colors.pop()
        if missing_colors_list.count(unused_center_color) > 0:
            missing_colors_list.remove(unused_center_color)
        bottom_face_dict = {pos: None for pos in bottom_face_positions}
        bottom_face_dict['B5'] = unused_center_color
        random.shuffle(missing_colors_list)
        remaining_positions = [pos for pos in bottom_face_positions if pos != 'B5']
        for pos, color in zip(remaining_positions, missing_colors_list):
            bottom_face_dict[pos] = color
        return bottom_face_dict

    def changeText(self):
        self.counter += 1
        if self.counter == 0:
            self.generatingButton.setText("Generating steps...")
        elif self.counter == 1:
            self.generatingButton.setText("Ready")
        elif self.counter == 2:
            self.showScreen4()
            self.generatingButton.setText("Solving...")

        elif self.counter == 3:
            self.generatingButton.setText("Solved!")
            self.exitButton.setHidden(False)
            self.stepsButton.setHidden(False)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))

    def screen2viewCam(self):
        self.current_time = time.time()

        if self.stackedWidget.currentWidget() == self.screen2:
            ret, image = self.cap.read()
            ret2, image2 = self.cap2.read()
            if self.current_time - self.last_capture_time >= self.capture_interval:
                self.last_capture_time = self.current_time
                labels, predicts = self.get_predicts_and_labels(self.model, image, 1)
                self.label_to_predict = dict(zip(labels, predicts))
                labels2, predicts2 = self.get_predicts_and_labels(self.model, image2, 2)
                self.label_to_predict2 = dict(zip(labels2, predicts2))
                label_to_predict_copy = self.label_to_predict.copy()
                label_to_predict_copy.update(self.label_to_predict2)
                self.changeNumDetected()
                self.missing_dict = self.getMissingSquares(label_to_predict_copy)
                print(self.missing_dict)
                if self.missing_dict == "pass":
                    pass
                else:
                    label_to_predict_copy.update(self.missing_dict)
                self.update_cube_colors(label_to_predict_copy)
                self.solveCube(label_to_predict_copy)
                image = imutils.resize(image, height=400, width=200)
                image2 = imutils.resize(image2, height=400, width=200)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                height2, width2, channel2 = image2.shape
                step = channel * width
                step2 = channel2 * width2
                qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
                qImg2 = QImage(image2.data, width2, height2, step2, QImage.Format_RGB888)
                if qImg is not None and qImg2 is not None:
                    self.WebcamFrame.setPixmap(QPixmap.fromImage(qImg))
                    self.WebcamFrame_2.setPixmap(QPixmap.fromImage(qImg2))
                else:
                    self.WebcamFrame.setPixmap(QPixmap.fromImage(image))
                    self.WebcamFrame_2.setPixmap(QPixmap.fromImage(image2))
        elif self.stackedWidget.currentWidget() == self.screen5:
            if self.settingCameraOption == "Camera1":
                ret, image = self.cap.read()
                image = imutils.resize(image, height=400, width=200)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                step = channel * width
                qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
                self.WebcamSettingsFrame.setPixmap(QPixmap.fromImage(qImg))
            elif self.settingCameraOption == "Camera2":
                ret, image = self.cap2.read()
                image = imutils.resize(image, height=400, width=200)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                height, width, channel = image.shape
                step = channel * width
                qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
                self.WebcamSettingsFrame.setPixmap(QPixmap.fromImage(qImg))
            else:
                print("nonoa")
        else:
            print("Another screen is currently visible")

    def change_to_camera_1(self):
        self.settingCameraOption = "Camera1"
        if hasattr(self, 'cap') and self.cap.isOpened():
            pass
        else:
            self.controlTimer()

    def change_to_camera_2(self):
        self.settingCameraOption = "Camera2"
        if hasattr(self, 'cap2') and self.cap2.isOpened():
            pass
        else:
            self.controlTimer()

    def screen5viewCam(self):
        ret, image = self.cap.read()
        image = imutils.resize(image, height=400, width=200)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        step = channel * width
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        self.WebcamSettingsFrame.setPixmap(QPixmap.fromImage(qImg))

    def controlTimer(self):
        if not self.ctimer.isActive():
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            self.ctimer.start(5)
            self.CameraButton.setText("Stop Camera")
        else:
            self.ctimer.stop()
            self.cap.release()
            self.cap2.release()
            self.CameraButton.setText("Start Camera")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())