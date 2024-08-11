import sys
import numpy as np
from OpenGL.GL import *
from PyQt5 import QtCore, QtGui, QtWidgets
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

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
        #glColor3fv((0.5, 0.5, 0.5))
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
            print(float(self.rotation[2]))
        self.lastPos = event.pos()
        self.update()
        print(float(self.rotation[0]), float(self.rotation[1]))
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.update()
        print(float(self.zoom))


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(572, 407)
        Dialog.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.openGLWidget = OpenGLWidget(Dialog)  # Use the OpenGLWidget subclass
        self.openGLWidget.setGeometry(QtCore.QRect(150, 120, 241, 230)) #170, 160, 211, 181
        self.openGLWidget.setAutoFillBackground(False)
        self.openGLWidget.setObjectName("openGLWidget")

        self.RubikLabel = QtWidgets.QLabel(Dialog)
        self.RubikLabel.setGeometry(QtCore.QRect(100, 10, 351, 51))

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(0, 350, 571, 61))
        font = QtGui.QFont()
        font.setFamily("Northstar Laser Italic")
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background-color: rgb(0, 0, 0);\n" "color: rgb(255, 255, 255);")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.raise_()

        font = QtGui.QFont()
        font.setFamily("Big John")
        font.setPointSize(22)
        self.RubikLabel.setFont(font)
        self.RubikLabel.setAutoFillBackground(False)
        self.RubikLabel.setObjectName("RubikLabel")
        self.SolverLabel = QtWidgets.QLabel(Dialog)
        self.SolverLabel.setGeometry(QtCore.QRect(170, 65, 201, 51))
        font = QtGui.QFont()
        font.setFamily("Big John")
        font.setPointSize(22)
        self.SolverLabel.setFont(font)
        self.SolverLabel.setAutoFillBackground(False)
        self.SolverLabel.setObjectName("SolverLabel")

        self.retranslateUi(Dialog)

        # Connect the push button's clicked signal to the method
        self.pushButton.clicked.connect(self.on_pushButton_clicked)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.RubikLabel.setText(_translate("Dialog",
                                           "<html><head/><body><p><span style=\" font-size:36pt; color:#ffffff;\">rubiks cube </span></p><p><br/></p></body></html>"))
        self.SolverLabel.setText(_translate("Dialog",
                                            "<html><head/><body><p><span style=\" font-size:36pt; color:#ffffff;\">SOLVER</span></p><p><br/></p></body></html>"))
        self.pushButton.setText(_translate("Dialog", "Tap here to continue"))

    def on_pushButton_clicked(self):
        print("Button was clicked!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
