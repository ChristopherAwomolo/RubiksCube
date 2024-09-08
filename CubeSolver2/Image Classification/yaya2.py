from PyQt5 import QtCore, QtWidgets, QtGui


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


class DraggableSquaresWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.squares = []
        self.init_squares()
        self.selected_square = None
        self.setMouseTracking(True)
        self.setFixedSize(600, 600)
        self.setWindowTitle("Draggable Squares")

    def init_squares(self):
        faces = ['U', 'D', 'F']
        positions = [(x * 60, y * 60) for y in range(3) for x in range(9)]
        face_labels = [f'{face}{i + 1}' for face in faces for i in range(9)]

        for i, pos in enumerate(positions[:27]):
            square = DraggableSquare(pos[0], pos[1], 50)
            square.label = face_labels[i]  # Attach a label to each square
            self.squares.append(square)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for square in self.squares:
            self.draw_square(painter, square)

    def draw_square(self, painter, square):
        # Draw hollow square with a green outline
        painter.setPen(QtGui.QPen(QtCore.Qt.green, 3))
        painter.drawRect(square.rect)

        # Draw label
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
        print(saved_squares)  # Print the dictionary of saved square positions


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = DraggableSquaresWidget()
    window.show()
    app.exec_()
