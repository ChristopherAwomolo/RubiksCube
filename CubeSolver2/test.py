import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2


class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.cap = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def start_camera(self):
        if not self.cap:
            self.cap = cv2.VideoCapture(0)
        self.show_frame()

    def show_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(image))
                self.label.setAlignment(Qt.AlignCenter)
            self.update()

    def stop_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            self.label.clear()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()

        # Screen 1 with "Show Camera" and "Show Next Screen" buttons
        screen1 = QWidget()
        screen1_layout = QVBoxLayout()

        self.show_camera_btn_1 = QPushButton("Show Camera")
        self.show_next_screen_btn = QPushButton("Show Next Screen")
        screen1_layout.addWidget(self.show_camera_btn_1)
        screen1_layout.addWidget(self.show_next_screen_btn)
        screen1.setLayout(screen1_layout)

        # Screen 2 with "Show Camera" and "Show Previous Screen" buttons
        screen2 = QWidget()
        screen2_layout = QVBoxLayout()

        self.show_camera_btn_2 = QPushButton("Show Camera")
        self.show_previous_screen_btn = QPushButton("Show Previous Screen")
        screen2_layout.addWidget(self.show_camera_btn_2)
        screen2_layout.addWidget(self.show_previous_screen_btn)
        screen2.setLayout(screen2_layout)

        # Add both screens to the stacked widget
        self.stacked_widget.addWidget(screen1)
        self.stacked_widget.addWidget(screen2)

        # Set the layout of the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Camera Widget
        self.camera_widget = CameraWidget()

        # Connect buttons to functions
        self.show_camera_btn_1.clicked.connect(lambda: self.toggle_camera(self.show_camera_btn_1))
        self.show_next_screen_btn.clicked.connect(self.show_next_screen)
        self.show_camera_btn_2.clicked.connect(lambda: self.toggle_camera(self.show_camera_btn_2))
        self.show_previous_screen_btn.clicked.connect(self.show_previous_screen)

    def toggle_camera(self, button):
        if button.text() == "Show Camera":
            self.show_camera(button)
        else:
            self.stop_camera(button)

    def show_camera(self, button):
        self.camera_widget.start_camera()
        self.camera_widget.show_frame()

        # Add the camera widget to the current screen layout
        current_screen = self.stacked_widget.currentWidget()
        layout = current_screen.layout()
        layout.addWidget(self.camera_widget)

        # Update button text to "Stop Camera"
        button.setText("Stop Camera")

    def stop_camera(self, button):
        self.camera_widget.stop_camera()
        button.setText("Show Camera")

    def show_next_screen(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_previous_screen(self):
        self.stacked_widget.setCurrentIndex(0)

    def closeEvent(self, event):
        # Stop the camera when closing the window
        self.camera_widget.stop_camera()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Camera App")
    window.show()
    sys.exit(app.exec_())
