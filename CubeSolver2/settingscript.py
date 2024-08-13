import sys
import cv2
import imutils
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QImage, QPixmap

class CameraSettingsGUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupScreen4(self)
        self.cap3 = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Initialize webcam
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Set the timer to update the frame every 30 ms

    def setupScreen4(self, screen):
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(screen)

        # Left side layout with grid of buttons and webcam label
        left_layout = QtWidgets.QVBoxLayout()

        # Webcam Label
        self.WebcamSettingsFrame = QtWidgets.QLabel(screen)
        self.WebcamSettingsFrame.setFixedSize(200, 200)  # Set the size of the webcam display
        #self.WebcamSettingsFrame.setGeometry(QtCore.QRect(0, 0, 50, 20))
        self.WebcamSettingsFrame.setStyleSheet("background-color: black;")  # Background color before webcam is loaded
        left_layout.addWidget(self.WebcamSettingsFrame)

        # Grid layout for buttons
        grid_layout = QtWidgets.QGridLayout()
        self.button_camera = QtWidgets.QPushButton("Camera", screen)
        self.button_another = QtWidgets.QPushButton("Another Option", screen)
        grid_layout.addWidget(self.button_camera, 0, 0)
        grid_layout.addWidget(self.button_another, 1, 0)
        left_layout.addLayout(grid_layout)

        # Back button at the bottom left
        self.back_button = QtWidgets.QPushButton("Back", screen)
        self.back_button.setStyleSheet("background-color: red; color: white;")
        left_layout.addWidget(self.back_button)

        # Right side with a QStackedWidget to switch between different views
        self.stack = QtWidgets.QStackedWidget(screen)

        # Page 1: Camera Settings/Resolution layout
        camera_settings_widget = QtWidgets.QWidget()
        camera_settings_layout = QtWidgets.QVBoxLayout(camera_settings_widget)
        scroll_area_1 = QtWidgets.QScrollArea()
        scroll_area_widget_1 = QtWidgets.QWidget()
        scroll_area_layout_1 = QtWidgets.QVBoxLayout(scroll_area_widget_1)

        self.change_settings_button = QtWidgets.QPushButton("Change Camera Settings", screen)
        self.change_resolution_button = QtWidgets.QPushButton("Change Camera Resolution", screen)
        scroll_area_layout_1.addWidget(self.change_settings_button)
        scroll_area_layout_1.addWidget(self.change_resolution_button)

        # Adding more items to make the scroll area usable
        for i in range(15):
            button = QtWidgets.QPushButton(f"Additional Setting {i+1}", screen)
            scroll_area_layout_1.addWidget(button)

        scroll_area_1.setWidget(scroll_area_widget_1)
        scroll_area_1.setWidgetResizable(True)
        camera_settings_layout.addWidget(scroll_area_1)

        # Page 2: Another Option layout with a scroll area
        another_widget = QtWidgets.QWidget()
        another_layout = QtWidgets.QVBoxLayout(another_widget)
        scroll_area_2 = QtWidgets.QScrollArea()
        scroll_area_widget_2 = QtWidgets.QWidget()
        scroll_area_layout_2 = QtWidgets.QVBoxLayout(scroll_area_widget_2)

        # Adding buttons to the scrollable layout for "Another Option"
        for i in range(20):
            button = QtWidgets.QPushButton(f"Option {i+1} for Another", screen)
            scroll_area_layout_2.addWidget(button)

        scroll_area_2.setWidget(scroll_area_widget_2)
        scroll_area_2.setWidgetResizable(True)
        another_layout.addWidget(scroll_area_2)

        # Add pages to the stack
        self.stack.addWidget(camera_settings_widget)  # Index 0
        self.stack.addWidget(another_widget)          # Index 1

        # Set the initial page to the camera settings
        self.stack.setCurrentIndex(0)

        # Connect buttons to functions to change the stack
        self.button_camera.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.button_another.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.change_settings_button.clicked.connect(self.openCameraSettings)

        # Add left and right layouts to the main layout
        main_layout.addLayout(left_layout, 1)  # Left layout takes 1/4th of space
        main_layout.addWidget(self.stack, 3)  # Stacked widget takes 3/4th of space

    def update_frame(self):
        ret, image = self.cap3.read()
        if ret:
            # Resize and convert the image to RGB format
            image = imutils.resize(image, height=200, width=200)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Get image dimensions and create QImage
            height, width, channel = image.shape
            step = channel * width
            qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)

            # Display the image on the label
            self.WebcamSettingsFrame.setPixmap(QPixmap.fromImage(qImg))

    def openCameraSettings(self):
        # Open the camera properties/settings window
        self.cap3.set(cv2.CAP_PROP_SETTINGS, 0)

    def closeEvent(self, event):
        # Release the webcam on closing the application
        self.cap3.release()
        event.accept()

# Main Application
app = QtWidgets.QApplication(sys.argv)
window = CameraSettingsGUI()
window.show()
sys.exit(app.exec_())
