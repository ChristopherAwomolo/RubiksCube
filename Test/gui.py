from PyQt5 import QtCore, QtGui, QtWidgets
from rubiks_widget import RubiksWidget

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(571, 407)
        Dialog.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.openGLWidget = RubiksWidget(Dialog)
        self.openGLWidget.setGeometry(QtCore.QRect(130, 60, 300, 281))
        self.openGLWidget.setObjectName("openGLWidget")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        #self.openGLWidget.solveCubeAnimation(f"R' B' R' F' F' F2 F' B2 F' R2 R' F2 B' U2 U' U' R R' U U U' U' B F' F' R R' R' F B' B' F F' F' F F R B R")
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Rubik's Cube"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())