import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtWidgets import QOpenGLWidget
import OpenGL.GL as GL
import OpenGL.GLU as GLU
from rubik import Rubik


class RubiksWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubik = Rubik(2)
        self.lastPos = QtCore.QPoint()
        self.rotate_slc = {
            Qt.Key_1: (0, 0, 1), Qt.Key_2: (0, 1, 1), Qt.Key_3: (0, 2, 1),
            Qt.Key_4: (1, 0, 1), Qt.Key_5: (1, 1, 1), Qt.Key_6: (1, 2, 1),
            Qt.Key_7: (2, 0, 1), Qt.Key_8: (2, 1, 1), Qt.Key_9: (2, 2, 1)

        }
        self.animate = False
        self.animate_ang = 0
        self.animate_speed = 5
        self.rotate = (0, 0, 0)

        self.rotation = [0, 0, 0]
        self.zoom = 1.0

        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        #GL.glClearColor(1, 1, 1, 1)
        GL.glClearColor(0, 0, 0, 1)
    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, width / height, 1, 50.0)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslatef(0, 0, -40 * self.zoom)
        GL.glRotatef(self.rotation[0], 1, 0, 0)
        GL.glRotatef(self.rotation[1], 0, 1, 0)
        GL.glRotatef(self.rotation[2], 0, 0, 1)

        if self.animate:
            if self.animate_ang >= 90:
                for cube in self.rubik.cubes:
                    cube.update(*self.rotate)
                self.animate = False
                self.animate_ang = 0

        for cube in self.rubik.cubes:
            cube.draw(cube.polygons, self.animate, self.animate_ang, *self.rotate)

        if self.animate:
            self.animate_ang += self.animate_speed

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

    def keyPressEvent(self, event):
        if not self.animate and event.key() in self.rotate_slc:
            self.animate = True
            self.rotate = self.rotate_slc[event.key()]
            self.update()