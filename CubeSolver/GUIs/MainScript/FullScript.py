import sys
import numpy as np
from PyQt5 import QtCore, QtGui
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
import kociemba
from rubiks_widget import RubiksWidget

'''
To do list (easiest to hardest)
-Add more training data
-Make the GUI scalable and include a fullscreen in the dialog
-Make the waiting screens work for generating steps and solving the cube (not click based)
-Finish all of the settings work
 -Make calibration squares for Camera 1
 -Make calibration squares for Camera 2
Make 3d printed holder for rubiks cube - Just cylinder shape no square bit at the end
'''
class DraggableSquare:
    def __init__(self, x, y, size=50):
        self.rect = QtCore.QRect(x, y, size, size)
        self.dragging = False
        self.offset = QtCore.QPoint(0, 0)
    def contains(self, point):
        return self.rect.contains(point)
    def start_dragging(self, point):
        self.dragging = True
        self.offset = point - self.rect.topLeft()
    def move(self, point):
        if self.dragging:
            new_pos = point - self.offset
            self.rect.moveTo(new_pos)
    def stop_dragging(self):
        self.dragging = False
    def resize(self, new_size):
        center = self.rect.center()
        self.rect.setSize(QtCore.QSize(new_size, new_size))
        self.rect.moveCenter(center)
    def get_dimensions(self):
        return self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()

class OpenGLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, parent=None, cube_dictionary=None):
        super(OpenGLWidget, self).__init__(parent)
        self.lastPos = None
        self.rotation = [570.0, -46.0, 0]
        self.zoom = 1.3
        self.cube_dictionary = self.default_cube_dict() #cube_dict if cube_dict else self.default_cube_dict()
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
    def color_from_char(self, char):
        colors = {
            'W': (1, 1, 1),  # White
            'B': (0, 0.318, 0.729),  # Blue
            'Y': (1, 0.835, 0),  # Yellow
            'G': (0, 0.62, 0.376),  # Green
            'O': (1, 0.345, 0),  # Orange
            'R': (0.8, 0.118, 0.118)  # Red
        }
        return colors.get(char, (0, 0, 0))  # Default to black if char not found
    def default_cube_dict(self):
        return {
            'U1': 'W', 'U2': 'W', 'U3': 'W', 'U4': 'W', 'U5': 'W', 'U6': 'W', 'U7': 'W', 'U8': 'W', 'U9': 'W',
            'D1': 'Y', 'D2': 'Y', 'D3': 'Y', 'D4': 'Y', 'D5': 'Y', 'D6': 'Y', 'D7': 'Y', 'D8': 'Y', 'D9': 'Y',
            'F1': 'R', 'F2': 'R', 'F3': 'R', 'F4': 'R', 'F5': 'R', 'F6': 'R', 'F7': 'R', 'F8': 'R', 'F9': 'R',
            'B1': 'O', 'B2': 'O', 'B3': 'O', 'B4': 'O', 'B5': 'O', 'B6': 'O', 'B7': 'O', 'B8': 'O', 'B9': 'O',
            'L1': 'B', 'L2': 'B', 'L3': 'B', 'L4': 'B', 'L5': 'B', 'L6': 'B', 'L7': 'B', 'L8': 'B', 'L9': 'B',
            'R1': 'G', 'R2': 'G', 'R3': 'G', 'R4': 'G', 'R5': 'G', 'R6': 'G', 'R7': 'G', 'R8': 'G', 'R9': 'G'
        }
    def cube(self):
        cube_verts = (
            (3, -3, -3), (3, 3, -3), (-3, 3, -3), (-3, -3, -3),
            (3, -3, 3), (3, 3, 3), (-3, -3, 3), (-3, 3, 3)
        )
        cube_edges = (
            (0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
            (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)
        )
        surface_indices = [
            (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
            (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
        ]
        face_order = ['U', 'L', 'F', 'R', 'B', 'D']
        glBegin(GL_QUADS)
        for i, face in enumerate(face_order):
            for pos in range(1, 10):
                key = f'{face}{pos}'
                color = self.color_from_char(self.cube_dictionary.get(key, 'B'))
                surface = surface_indices[(pos - 1) % 6]
                glColor3fv(color)
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


class DraggableSquaresWidget(QtWidgets.QWidget):
    def __init__(self, current_cap=0, parent=None):
        print(current_cap)
        super().__init__(parent)
        self.squares = []
        self.current_cap = current_cap
        self.init_squares()
        self.selected_square = None
        self.setMouseTracking(True)

        # Webcam initialization
        self.cap = cv2.VideoCapture(current_cap, cv2.CAP_DSHOW)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms

        # Widget to display webcam feed
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, 640, 480)

    def init_squares(self):
        self.squares.clear()

        faces = [['U', 'D', 'F'], ['B', 'R', 'L']]
        positions = [(x * 60, y * 60) for y in range(3) for x in range(9)]
        face_labels = [f'{face}{i + 1}' for face in faces[self.current_cap] for i in range(9)]

        for i, pos in enumerate(positions[:27]):
            square = DraggableSquare(pos[0], pos[1], 50)
            square.label = face_labels[i]  # Attach a label to each square
            self.squares.append(square)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to QImage to display in PyQt
            image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_RGB888)
            self.label.setPixmap(QtGui.QPixmap.fromImage(image))
            self.update()  # Trigger the paint event to draw squares

    def paintEvent(self, event):
        painter = QtGui.QPainter(self.label.pixmap())
        for square in self.squares:
            self.draw_square(painter, square)

    def draw_square(self, painter, square):
        # Draw hollow square with a green outline
        painter.setPen(QtGui.QPen(QtCore.Qt.green, 3))
        painter.drawRect(square.rect)

        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.setFont(QtGui.QFont('Arial', 10))
        painter.drawText(square.rect, QtCore.Qt.AlignCenter, square.label)

    def mousePressEvent(self, event):
        point = event.pos()
        for square in self.squares:
            if square.contains(point):
                square.start_dragging(point)
                self.selected_square = square
                break

    def mouseMoveEvent(self, event):
        if self.selected_square:
            self.selected_square.move(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.selected_square:
            self.selected_square.stop_dragging()
            self.selected_square = None

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_S:
            self.save_squares_to_dict()

    def save_squares_to_dict(self):
        saved_squares = {square.label: square.get_dimensions() for square in self.squares}
        print(saved_squares)

    def closeEvent(self, event):
        self.cap.release()

    def update_camera_feed(self, new_cap):
        if self.cap.isOpened():
            self.cap.release()
        self.current_cap = new_cap
        self.cap = cv2.VideoCapture(self.current_cap, cv2.CAP_DSHOW)
        self.init_squares()

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        self.previous_number = 0
        self.current_pos = 0
        self.settingCameraOption = "Camera2"
        self.counter = 0
        self.current_cap = 0
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
        self.screen1 = QtWidgets.QWidget()
        self.setupScreen1(self.screen1)
        self.stackedWidget.addWidget(self.screen1)
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
        self.screen6 = QtWidgets.QWidget()
        self.setupScreen6(self.screen6)
        self.stackedWidget.addWidget(self.screen6)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.model = joblib.load('../../model/decision_tree-v4-7.joblib')
        self.colors = ['B', 'G', 'O', 'R', 'W', 'Y']
        self.cam1faces= ['F', 'L', 'D']
        self.cam2faces = ['U', 'R', 'B']
        self.colors.sort()
        self.total_squares_per_color = 9  # Each color should appear exactly 9 times
        with open("../../Polygons.txt", "r") as file:
            dict_str = file.read()
        self.polygons = eval(dict_str)
        self.cnt = 0
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
            'B': "background-color: rgb(0, 0, 255);",     # Blue
            'G': "background-color: rgb(0, 255, 0);",     # Green
            'O': "background-color: rgb(255, 165, 0);",   # Orange
            'R': "background-color: rgb(255, 0, 0);",     # Red
            'W': "background-color: rgb(255, 255, 255);", # White
            'Y': "background-color: rgb(255, 255, 0);"    # Yellow
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
        self.s1openGLWidget = RubiksWidget(screen)  # Use the OpenGLWidget subclass
        self.s1openGLWidget.setGeometry(QtCore.QRect(150, 120, 241, 230)) #170, 160, 211, 181
        self.s1openGLWidget.setAutoFillBackground(False)

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
        self.settingsButton.setStyleSheet("background-color: rgb(10, 132, 18);\n""background-color: rgb(163, 163, 163);")
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setText("Settings")
        self.settingsButton.clicked.connect(self.showScreen5)

        self.s2openGLWidget = RubiksWidget(screen)
        self.s2openGLWidget.setGeometry(QtCore.QRect(330, 20, 211, 191))
        self.s2openGLWidget.setAutoFillBackground(False)
        self.s2openGLWidget.setObjectName("openGLWidget")
        self.s2openGLWidget.solveCubeAnimation = self.s1openGLWidget.solveCubeAnimation
        self.s2openGLWidget.initializeGL = self.s1openGLWidget.initializeGL
        self.s2openGLWidget.paintGL = self.s1openGLWidget.paintGL
        self.s2openGLWidget.mousePressEvent = self.s1openGLWidget.mousePressEvent
        self.s2openGLWidget.mouseMoveEvent = self.s1openGLWidget.mouseMoveEvent
        self.s2openGLWidget.wheelEvent = self.s1openGLWidget.wheelEvent
        self.s2openGLWidget.keyPressEvent = self.s1openGLWidget.keyPressEvent

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
        self.CubeReady.setHidden(True)

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
        self.s3openGLWidget = RubiksWidget(screen)  # Use the OpenGLWidget subclass
        self.s3openGLWidget.setGeometry(QtCore.QRect(20, 20, 529, 330)) #170, 160, 211, 181
        self.s3openGLWidget.setAutoFillBackground(False)
        self.s3openGLWidget.setObjectName("openGLWidget")
        #self.s3openGLWidget.resizeGL(700, 200)
        self.s3openGLWidget.solveCubeAnimation = self.s1openGLWidget.solveCubeAnimation
        self.s3openGLWidget.initializeGL = self.s1openGLWidget.initializeGL
        self.s3openGLWidget.paintGL = self.s1openGLWidget.paintGL
        self.s3openGLWidget.mousePressEvent = self.s1openGLWidget.mousePressEvent
        self.s3openGLWidget.mouseMoveEvent = self.s1openGLWidget.mouseMoveEvent
        self.s3openGLWidget.wheelEvent =  self.s1openGLWidget.wheelEvent
        self.s3openGLWidget.keyPressEvent = self.s1openGLWidget.keyPressEvent
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
        self.stepsButton.clicked.connect(self.showSteps)
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
        max_height = 100
        n = 15  # Replace with the actual number of buttons
        button_height = max_height // n
        min_button_height = 30
        if button_height < min_button_height:
            button_height = min_button_height
        self.container_widget = QtWidgets.QWidget(screen)
        self.container_widget.setGeometry(460, 20, 110, 301)  # X: 460px, Y: 220px, Width: 150px, Height: 350px
        self.container_widget.setHidden(True)
        self.main_layout = QtWidgets.QVBoxLayout(self.container_widget)
        self.scroll_area = QtWidgets.QScrollArea(self.container_widget)
        #self.scroll_area.setFixedSize(91, 301)
        self.scroll_area_widget_contents = QtWidgets.QWidget(self.scroll_area)
        self.scroll_area_layout = QtWidgets.QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_widget_contents.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

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
        self.button_camera.clicked.connect(self.change_to_camera_1) #self.controlTimer
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
        self.change_settings_button.clicked.connect(lambda: self.openCameraSettings(1))
        self.calibrate_squares_button = QtWidgets.QPushButton("Calibrate Squares", screen)
        self.calibrate_squares_button.setStyleSheet("background-color: white; color: black;")
        self.calibrate_squares_button.clicked.connect(self.showScreen6)
        self.scroll_area_layout_1.addWidget(self.change_settings_button)
        self.scroll_area_layout_1.addWidget(self.calibrate_squares_button)
        self.scroll_area_1.setWidget(self.scroll_area_widget_1)
        self.scroll_area_1.setWidgetResizable(True)
        self.camera_settings_layout.addWidget(self.scroll_area_1)
        self.another_widget = QtWidgets.QWidget(screen)
        self.another_layout = QtWidgets.QVBoxLayout(self.another_widget)
        self.scroll_area_2 = QtWidgets.QScrollArea(screen)
        self.scroll_area_widget_2 = QtWidgets.QWidget(screen)
        self.scroll_area_layout_2 = QtWidgets.QVBoxLayout(self.scroll_area_widget_2)
        self.cam2_change_settings_button = QtWidgets.QPushButton("Change Camera Settings", screen)
        self.cam2_change_settings_button.setStyleSheet("background-color: white; color: black;")
        self.cam2_change_settings_button.clicked.connect(lambda: self.openCameraSettings(2))
        self.scroll_area_layout_2.addWidget(self.cam2_change_settings_button)
        self.cam2_calibrate_squares_button = QtWidgets.QPushButton("Calibrate Squares", screen)
        self.cam2_calibrate_squares_button.setStyleSheet("background-color: white; color: black;")
        self.cam2_calibrate_squares_button.clicked.connect(self.showScreen6)
        self.scroll_area_layout_1.addWidget(self.change_settings_button)
        self.scroll_area_layout_1.addWidget(self.calibrate_squares_button)
        self.scroll_area_layout_2.addWidget(self.cam2_change_settings_button)
        self.scroll_area_layout_2.addWidget(self.cam2_calibrate_squares_button)
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

    def setupScreen6(self, screen):
        self.open_webcam_button = QtWidgets.QPushButton('Open Webcam', screen)
        self.open_webcam_button.setStyleSheet("background-color: white; color: black;")
        self.open_webcam_button.clicked.connect(self.open_webcam)
        self.save_button = QtWidgets.QPushButton('Save', screen)
        self.save_button.setStyleSheet("background-color: white; color: black;")
        self.save_button.clicked.connect(self.save_dimensions) #save_dimensions
        self.size_input = QtWidgets.QLineEdit(screen)
        self.size_input.setPlaceholderText("Enter square size")
        self.size_input.setStyleSheet("background-color: white; color: black;")
        self.apply_button = QtWidgets.QPushButton('Apply', screen)
        self.apply_button.setStyleSheet("background-color: white; color: black;")
        self.apply_button.clicked.connect(self.apply_square_size)
        self.label = QtWidgets.QLabel(screen)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")  # Just to ensure it's visible
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.size_input)
        h_layout.addWidget(self.apply_button)
        v_layout = QtWidgets.QVBoxLayout(screen)
        v_layout.addWidget(self.open_webcam_button)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.label)
        v_layout.addWidget(self.save_button)
        screen.setLayout(v_layout)
        self.cap = None
        self.cap2 = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.draggable_squares_widget = DraggableSquaresWidget(self.current_cap, self.label)
        self.dragging_square = None
        self.label.setMouseTracking(True)
        self.label.mousePressEvent = self.mouse_press
        self.label.mouseMoveEvent = self.mouse_move
        self.label.mouseReleaseEvent = self.mouse_release

    def open_webcam(self):
        self.controlTimer()
        self.timer.start(5)

    def update_frame(self):
        if self.current_cap == 0:
            ret, frame = self.cap.read()
            if ret:
                self.frame_height, self.frame_width = frame.shape[:2]

                for square in self.squares:
                    label = square['label']
                    x, y, w, h = square.get_dimensions()
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x + 5, y + 32 // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                pixmap = QPixmap.fromImage(qt_image)
                self.label.setPixmap(pixmap)
                self.displayed_image_size = pixmap.size()
        elif self.current_cap == 1:
            ret2, frame2 = self.cap2.read()
            if ret2:
                self.frame_height, self.frame_width = frame2.shape[:2]

                for square in self.squares:
                    x, y, w, h = square.get_dimensions()
                    cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)

                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                h, w, ch = frame2.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame2.data, w, h, bytes_per_line, QImage.Format_RGB888)

                pixmap2 = QPixmap.fromImage(qt_image)
                self.label.setPixmap(pixmap2)
                self.displayed_image_size = pixmap2.size()
        else:
            pass

    def adjust_mouse_coordinates(self, event):
        label_width = self.label.width()
        label_height = self.label.height()

        x_offset = (label_width - self.displayed_image_size.width()) / 2
        y_offset = (label_height - self.displayed_image_size.height()) / 2

        adjusted_x = event.x() - x_offset
        adjusted_y = event.y() - y_offset

        adjusted_x = max(0, min(adjusted_x, self.displayed_image_size.width()))
        adjusted_y = max(0, min(adjusted_y, self.displayed_image_size.height()))

        scale_x = self.frame_width / self.displayed_image_size.width()
        scale_y = self.frame_height / self.displayed_image_size.height()

        scaled_pos_x = int(adjusted_x * scale_x)
        scaled_pos_y = int(adjusted_y * scale_y)

        return QtCore.QPoint(scaled_pos_x, scaled_pos_y)

    def mouse_press(self, event):
        adjusted_pos = self.adjust_mouse_coordinates(event)
        for square in self.squares:
            if square.contains(adjusted_pos):
                self.dragging_square = square
                square.start_dragging(adjusted_pos)
                break

    def mouse_move(self, event):
        if self.dragging_square:
            adjusted_pos = self.adjust_mouse_coordinates(event)
            self.dragging_square.move(adjusted_pos)

    def mouse_release(self, event):
        if self.dragging_square:
            self.dragging_square.stop_dragging()
            self.dragging_square = None

    def save_dimensions(self):
        self.draggable_squares_widget.save_squares_to_dict()
        if self.cap is not None:
            self.closeEvent()
        elif self.cap2 is not None:
            self.closeEvent()
        else:
            pass
        self.showScreen5()

    def apply_square_size(self):
        try:
            new_size = int(self.size_input.text())
            for square in self.squares:
                square.resize(new_size)
            self.update_frame()
        except ValueError:
            print("Please enter a valid integer for square size.")
    def closeEvent(self):
        self.controlTimer()
        self.timer.stop()

    def openCameraSettings(self, cap_value):
        if cap_value == 1:
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_SETTINGS, 1)
            else:
                self.controlTimer()
                self.cap.set(cv2.CAP_PROP_SETTINGS, 1)
        elif cap_value == 2:
            if hasattr(self, 'cap2') and self.cap2.isOpened():
                self.cap2.set(cv2.CAP_PROP_SETTINGS, 1)
            else:
                self.controlTimer()
                self.cap2.set(cv2.CAP_PROP_SETTINGS, 1)
        else:
            pass
    def showSteps(self):
        self.s3openGLWidget.solveCubeAnimation(self.reverse_list)
        self.container_widget.setHidden(False)
    def settingsBack(self):
        self.controlTimer()
        self.stackedWidget.setCurrentWidget(self.screen2)
    def solveCube(self, cube_dict):
        color_to_face = {}
        cube_dict_initials = {}
        for key, value in cube_dict.items():
            cube_dict_initials[key] = self.colors[value][0]
            if key.endswith('5'):  # This identifies the center pieces
                color_to_face[self.colors[value]] = key[0]
        face_order = ['U', 'R', 'F', 'D', 'L', 'B'] #self.cam1faces + self.cam2faces # ['U', 'R', 'F', 'D', 'L', 'B']
        cube_string = ''
        for face in face_order:
            for i in range(1, 10):  # 1 to 9
                key = f'{face}{i}'
                color = cube_dict_initials[key]
                cube_string += color_to_face[color]
        print(f"Cube string: {cube_string}")
        try:
            solution = kociemba.solve(cube_string)
            #self.solutionSteps = self.expand_moves(self.sol.split(" "))
            #self.step_numbers = len(solution)
            print(f"Solution: {solution}")
            self.CubeReady.setHidden(False)
        except ValueError as e:
            print(f"Error: {e}")
            print("The cube configuration might be invalid or unsolvable.")
        return solution

    def backtoHome(self):
        self.counter = -1
        self.exitButton.setHidden(True)
        self.stepsButton.setHidden(True)
        self.changeText()
        self.showScreen2()

    def exitScript(self):
        self.counter = -1
        self.exitButton.setHidden(True)
        self.stepsButton.setHidden(True)
        self.changeText()
        self.showScreen1()

    def showScreen1(self):
        self.stackedWidget.setCurrentWidget(self.screen1)
    def showScreen2(self):
        self.stackedWidget.setCurrentWidget(self.screen2)
    def showScreen3(self):
        self.stackedWidget.setCurrentWidget(self.screen3)
    def showScreen4(self):
        self.stackedWidget.setCurrentWidget(self.screen4)
    def showScreen5(self):
        self.stackedWidget.setCurrentWidget(self.screen5)

    def showScreen6(self):
        self.stackedWidget.setCurrentWidget(self.screen6)
        self.draggable_squares_widget.update_camera_feed(self.current_cap)
    def changeNumDetected(self):
        self.NumDetected_Video1.setText(str(len(self.label_to_predict)))
        self.NumDetected_Video2.setText(str(len(self.label_to_predict2)))

    def changeText(self):
        self.counter += 1
        if self.counter == 0:
            self.generatingButton.setText("Generating steps...")
        elif self.counter == 1:
            self.generatingButton.setText("Ready")
        elif self.counter == 2:
            self.showScreen4()
            self.generatingButton.setText("Solving...")
            solution = self.solveCube(self.label_to_predict_copy)
            self.s3openGLWidget.solveCubeAnimation(solution)
            print("solving")
        elif self.counter == 3:
            self.generatingButton.setText("Solved!")
            self.create_buttons(self.sol, self.scroll_area_widget_contents, self.scroll_area_layout)
            self.exitButton.setHidden(False)
            self.stepsButton.setHidden(False)

    def get_opposite_moves(self, sequence):
        moves = sequence.split()
        opposite_sequence = []
        for move in reversed(moves):
            face = move[0]
            if len(move) == 1:
                opposite_sequence.append(face + "'")
            elif move[1] == "'":
                opposite_sequence.append(face)
            elif move[1] == "2":
                opposite_sequence.append(face + "' " + face + "'")
        return ' '.join(opposite_sequence)

    def get_opposite_step(self, step):
        if len(step) == 2 and step.endswith("'"):
            return step[0]
        elif step.endswith("2"):
            return step[0] + "' " + step[0] + "'"
        elif len(step) == 1:
            return step + "'"
        else:
            return step[0]

    def compute_reverse_steps(self, steps):
        reversed_steps = []
        steps.reverse()
        for step in steps:
            reversed_steps.append(self.get_opposite_step(step))
        return reversed_steps

    def expand_moves(self, moves):
        expanded_moves = []
        for move in moves:
            if move.endswith("2"):
                expanded_moves.append(move[0])
                expanded_moves.append(move[0])
            else:
                expanded_moves.append(move)
        return expanded_moves

    def animateStepName(self, number):
        self.solSteps = self.expand_moves(self.sol.split(" "))
        if number == self.previous_number:
            print(f"Already at step {number}.")
        elif number == self.previous_number + 1:  # Equivalent to 'next'
            if self.current_pos < len(self.solSteps) - 1:
                self.current_pos += 1
                self.previous_number += 1
                joined_prev_number = self.solSteps[self.previous_number-1]
                self.s3openGLWidget.solveCubeAnimation(joined_prev_number)
                self.current_pos = self.previous_number - 1
            else:
                print("You are already at the last step.")
        elif number == self.previous_number - 1:  # Equivalent to 'prev'
            if self.current_pos > -1:
                self.current_pos -= 1
                self.previous_number -= 1
                reverse_steps = self.compute_reverse_steps([self.solSteps[self.previous_number]])
                joined_reverse_steps = ' '.join(reverse_steps)
                self.s3openGLWidget.solveCubeAnimation(joined_reverse_steps)
                self.current_pos = self.previous_number - 1
            else:
                print("You are already at the first step.")
        elif 0 <= number <= len(self.solSteps):  # Jump to specific step
            if number > self.previous_number:
                difference = self.solSteps[self.previous_number:number]
                joined_difference_steps = ' '.join(difference)
                self.s3openGLWidget.solveCubeAnimation(joined_difference_steps)
                self.previous_number = number
            elif number < self.previous_number:
                reverse_steps = self.compute_reverse_steps(self.solSteps[number:self.previous_number])
                joined_reverse_steps = ' '.join(reverse_steps)
                self.s3openGLWidget.solveCubeAnimation(joined_reverse_steps)
                self.previous_number = number
        else:
            print(f"Please enter a valid step number between 1 and {len(self.solSteps)}.")

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
                #labels, predicts = self.get_predicts_and_labels(self.model, image, 1)
                #self.label_to_predict = dict(zip(labels, predicts))
                #labels2, predicts2 = self.get_predicts_and_labels(self.model, image2, 2)
                #self.label_to_predict2 = dict(zip(labels2, predicts2))
                #self.label_to_predict_copy = self.label_to_predict.copy()
                '''
                self.label_to_predict_copy = {
                    'U1': 2, 'U2': 3, 'U3': 3, 'U4': 2, 'U5': 2, 'U6': 3, 'U7': 5, 'U8': 4, 'U9': 5,
                    'R1': 0, 'R2': 5, 'R3': 4, 'R4': 1, 'R5': 0, 'R6': 5, 'R7': 5, 'R8': 4, 'R9': 2,
                    'F1': 3, 'F2': 1, 'F3': 2, 'F4': 0, 'F5': 4, 'F6': 2, 'F7': 0, 'F8': 0, 'F9': 1,
                    'D1': 3, 'D2': 3, 'D3': 2, 'D4': 0, 'D5': 3, 'D6': 3, 'D7': 5, 'D8': 1, 'D9': 4,
                    'L1': 4, 'L2': 5, 'L3': 0, 'L4': 4, 'L5': 1, 'L6': 2, 'L7': 3, 'L8': 4, 'L9': 4,
                    'B1': 1, 'B2': 1, 'B3': 1, 'B4': 0, 'B5': 5, 'B6': 2, 'B7': 0, 'B8': 5, 'B9': 1
                }
                '''
                self.label_to_predict_copy = {
                    'U1': 3, 'U2': 3, 'U3': 2, 'U4': 2, 'U5': 2, 'U6': 0, 'U7': 1, 'U8': 0, 'U9': 0,
                    'R1': 4, 'R2': 5, 'R3': 0, 'R4': 3, 'R5': 0, 'R6': 1, 'R7': 4, 'R8': 2, 'R9': 4,
                    'F1': 5, 'F2': 4, 'F3': 2, 'F4': 0, 'F5': 4, 'F6': 0, 'F7': 5, 'F8': 3, 'F9': 3,
                    'D1': 1, 'D2': 5, 'D3': 0, 'D4': 4, 'D5': 3, 'D6': 4, 'D7': 3, 'D8': 2, 'D9': 2,
                    'L1': 0, 'L2': 1, 'L3': 2, 'L4': 1, 'L5': 1, 'L6': 2, 'L7': 4, 'L8': 1, 'L9': 3,
                    'B1': 5, 'B2': 4, 'B3': 5, 'B4': 3, 'B5': 5, 'B6': 5, 'B7': 1, 'B8': 5, 'B9': 1
                }

                #['B', 'G', 'O', 'R', 'W', 'Y']
                #self.label_to_predict2.update(missing_dict)
                #self.label_to_predict_copy.update(self.label_to_predict2)
                #self.changeNumDetected()

                self.update_cube_colors(self.label_to_predict_copy)
                if self.cnt == 0:
                    self.sol = self.solveCube(self.label_to_predict_copy)
                    self.reverse_list = self.get_opposite_moves(self.sol)
                    self.s2openGLWidget.solveCubeAnimation(self.reverse_list)

                self.cnt += 1
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
                pass
        else:
            pass

    def create_buttons(self, sol, scroll_area_widget_contents, scroll_area_layout):
        s3solSteps = self.expand_moves(sol.split(" "))
        step_numbers = len(s3solSteps) + 1
        button_height = 30
        for i in range(step_numbers):
            button = QtWidgets.QPushButton(f"{i}", scroll_area_widget_contents)
            button.setStyleSheet("background-color: white; color: black;")
            button.setFixedHeight(button_height)
            button.setFixedWidth(50)
            button.clicked.connect(lambda checked, i=i: self.animateStepName(i))
            scroll_area_layout.addWidget(button)

    def change_to_camera_1(self):
        self.controlTimer()  # Stop the camera if it's running
        self.settingCameraOption = "Camera1"
        self.current_cap = 0

    def change_to_camera_2(self):
        self.controlTimer()
        self.settingCameraOption = "Camera2"
        self.current_cap = 1


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
            if self.stackedWidget.currentWidget() == self.screen2:
                self.CameraButton.setText("Stop Camera")
        else:
            self.ctimer.stop()
            self.cap.release()
            self.cap2.release()
            if self.stackedWidget.currentWidget() == self.screen2:
                self.CameraButton.setText("Start Camera")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())