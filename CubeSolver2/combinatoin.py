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

        # Draw the cube faces with different colors
        glBegin(GL_QUADS)
        for i, surface in enumerate(cube_surfaces):
            glColor3fv(colors[i])
            for vertex in surface:
                glVertex3fv(cube_verts[vertex])
        glEnd()

        # Draw the cube edges in gray
        glBegin(GL_LINES)
        glColor3fv((0, 0, 0))
        # glColor3fv((0.5, 0.5, 0.5))
        for edge in cube_edges:
            for vertex in edge:
                glVertex3fv(cube_verts[vertex])
        glEnd()

        # Draw grid lines on each face
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
        self.counter = 0
        self.Dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(571, 407)
        Dialog.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.stackedWidget = QtWidgets.QStackedWidget(Dialog)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 571, 407))
        self.stackedWidget.setObjectName("stackedWidget")

        self.timer = QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)

        '''
        self.CubeStepTimer = QTimer()
        self.CubeStepTimer.timeout.connect(self.)
        '''
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

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def setupScreen1(self, screen):
        self.openGLWidget = OpenGLWidget(screen)  # Use the OpenGLWidget subclass
        self.openGLWidget.setGeometry(QtCore.QRect(150, 120, 241, 230)) #170, 160, 211, 181
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

        self.pushButton.clicked.connect(self.showScreen2)


    def setupScreen2(self, screen):
        '''
        self.backButton = QtWidgets.QPushButton(screen)
        self.backButton.setGeometry(QtCore.QRect(10, 378, 90, 28))
        font = QtGui.QFont()
        font.setFamily("Bowlby One SC")
        font.setPointSize(20)
        self.backButton.setFont(font)
        self.backButton.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.backButton.setFlat(False)
        self.backButton.setObjectName("backButton")
        self.backButton.setText("Back")
        self.backButton.clicked.connect(self.showScreen1)
        '''

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

        self.pushButton_2 = QtWidgets.QPushButton(screen)
        self.pushButton_2.setGeometry(QtCore.QRect(330, 290, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(16)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("background-color: rgb(10, 132, 18);\n""background-color: rgb(163, 163, 163);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("Settings")

        self.openGLWidget = OpenGLWidget(screen)
        #self.openGLWidget = QtWidgets.QOpenGLWidget(screen)
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
        self.NumDetected_Video1.setGeometry(QtCore.QRect(219, 80, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.NumDetected_Video1.setFont(font)
        self.NumDetected_Video1.setObjectName("NumDetected_Video1")
        self.NumDetected_Video1.setText("23")
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
        self.NumDetected_Video2.setGeometry(QtCore.QRect(59, 190, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Swis721 Hv BT")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.NumDetected_Video2.setFont(font)
        self.NumDetected_Video2.setObjectName("NumDetected_Video2")
        self.NumDetected_Video2.setText("23")
        self.NumDetected_Video2.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")


        self.WebcamFrame = QtWidgets.QLabel(screen)
        self.WebcamFrame.setGeometry(QtCore.QRect(10, 10, 141, 91))
        self.WebcamFrame.setObjectName("WebcamFrame")

        self.WebcamFrame_2 = QtWidgets.QLabel(screen)
        self.WebcamFrame_2.setGeometry(QtCore.QRect(170, 120, 141, 91))
        self.WebcamFrame_2.setObjectName("WebcamFrame_2")


        self.CameraButton = QtWidgets.QPushButton(screen)
        self.CameraButton.setGeometry(QtCore.QRect(330, 250, 221, 31))

        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(16)
        self.CameraButton.setFont(font)
        self.CameraButton.setStyleSheet("background-color: rgb(10, 132, 18);\n" "background-color: rgb(163, 163, 163);")
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
        self.openGLWidget.setGeometry(QtCore.QRect(80, 20, 400, 300)) #170, 160, 211, 181
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
        #self.pushButton.clicked.connect(self.showScreen4)
        #self.pushButton.setHidden(True)
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
        self.pushButton_2.clicked.connect(self.showScreen2)
        #self.pushButton_2.setHidden(True)

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

        self.pushButton_3 = QtWidgets.QPushButton(screen)
        self.pushButton_3.setGeometry(QtCore.QRect(430, 330, 121, 51))
        font = QtGui.QFont()
        font.setFamily("Swis721 BlkCn BT")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("background-color: rgb(175, 4, 35);")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText("Quit")
        #self.pushButton_3.setHidden(True)
    def showScreen1(self):
        self.stackedWidget.setCurrentWidget(self.screen1)

    def showScreen2(self):
        self.stackedWidget.setCurrentWidget(self.screen2)

    def showScreen3(self):
        self.stackedWidget.setCurrentWidget(self.screen3)

    def exitScript(self):
        self.showScreen1()
        self.exitButton.setHidden(True)
        self.stepsButton.setHidden(True)
        self.counter = 0
    def showScreen4(self):
        self.stackedWidget.setCurrentWidget(self.screen4)

    def changeText(self):
        self.counter += 1
        if self.counter == 1:
            self.generatingButton.setText("Ready")
        elif self.counter == 2:
            self.showScreen4()
            self.generatingButton.setText("Solving...")
        elif self.counter == 3:
            self.generatingButton.setText("Solving...")
        elif self.counter == 4:
            self.generatingButton.setText("Solved!")
            self.exitButton.setHidden(False)
            self.stepsButton.setHidden(False)
        print("cLICKED")

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))

    def viewCam(self):
        # self.cap = cv2.VideoCapture(0)
        # start timer
        # self.timer.start(20)
        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = imutils.resize(image, height=400, width=200)
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.WebcamFrame.setPixmap(QPixmap.fromImage(qImg))

        ret2, image2 = self.cap2.read()
        # convert image to RGB format
        image2 = imutils.resize(image2, height=400, width=200)
        # convert image to RGB format
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
        # get image infos
        height2, width2, channel2 = image2.shape
        step2 = channel2 * width2
        # create QImage from image
        qImg2 = QImage(image2.data, width2, height2, step2, QImage.Format_RGB888)
        # show image in img_label
        self.WebcamFrame_2.setPixmap(QPixmap.fromImage(qImg2))



    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.cap2 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            # start timer
            self.timer.start(5)
            # update control_bt text
            self.CameraButton.setText("Stop Camera")
            #print("Running")
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            self.cap2.release()
            # update control_bt text
            print("Running")
            self.CameraButton.setText("Start Camera")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
