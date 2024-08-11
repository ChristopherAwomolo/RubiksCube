
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtOpenGL import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import sys



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = OpenGLWidget()
    widget.show()
    sys.exit(app.exec_())
