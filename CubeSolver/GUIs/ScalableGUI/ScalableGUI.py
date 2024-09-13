import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt

class ScalableGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Scalable PyQt5 GUI")

        # Create widgets
        label = QLabel("Enter your name:")
        input_field = QLineEdit()
        text_area = QTextEdit()
        submit_button = QPushButton("Submit")
        # Set size policy for widgets (Expanding makes them grow with the window)
        input_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        text_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        submit_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Layout management
        vbox = QVBoxLayout()  # Vertical layout
        vbox.addWidget(label)
        vbox.addWidget(input_field)
        vbox.addWidget(text_area)
        vbox.addWidget(submit_button)

        # Set the main layout to the window
        self.setLayout(vbox)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScalableGUI()
    window.resize(400, 300)  # Initial window size
    window.show()
    sys.exit(app.exec_())
