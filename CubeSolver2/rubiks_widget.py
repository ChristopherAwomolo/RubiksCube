import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtWidgets import QOpenGLWidget
import OpenGL.GL as GL
import OpenGL.GLU as GLU
from rubik import Rubik
import re

class RubiksWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubik = Rubik(2)
        self.lastPos = QtCore.QPoint()
        self.rotate_slc = {
            "U": (1, 2, -1), "D": (1, 0, 1), "R": (2, 2, -1),
            "L": (2, 0, 1), "F": (0, 0, 1), "B": (0, 2, -1)
        }
        self.animate = False
        self.animate_ang = 0
        self.animate_speed = 5
        self.rotate = (0, 0, 0)

        self.rotation = [33, 46, 0]
        self.zoom = 0.6830134553650705

        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
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
        else:
            QtCore.QTimer.singleShot(10, self.checkAnimationState)

    def transform_moves(self, moves):
        return re.sub(r'(\w)2', r'\1 \1', moves)

    def solveCubeAnimation(self, solve_string):
        self.solve_string_modified = self.transform_moves(solve_string)
        self.solve_queue = list(self.solve_string_modified.split())
        self.processNextMove()  # Start processing the queue

    def processNextMove(self):
        if self.solve_queue:
            char = self.solve_queue.pop(0)  # Get the next move from the queue
            face = char[0]  # The face (R, L, U, D, F, B)

            if len(char) > 1:  # Check if there's a direction or a 2
                if char[1] == "'":
                    self.animate = True  # Start the animation
                    x, y, z = self.rotate_slc[face]
                    z *= -1
                    new_tuple = (x,y,z)
                    self.rotate = new_tuple
                    self.update()
                elif char[1] == '2':
                    self.animate = True
                    self.rotate = self.rotate_slc[face]
                    self.update()

                    self.animate = True
                    self.rotate = self.rotate_slc[face]
                    self.update()
            else:
                self.animate = True
                self.rotate = self.rotate_slc[face]
                self.update()

        if self.animate:
            QtCore.QTimer.singleShot(10, self.checkAnimationState)  # Adjust timing as needed

    def checkAnimationState(self):
        if not self.animate:  # If animation finished
            self.processNextMove()  # Process the next move in the queue
        else:
            QtCore.QTimer.singleShot(10, self.checkAnimationState)



