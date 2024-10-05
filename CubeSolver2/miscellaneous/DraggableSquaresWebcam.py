import cv2
import numpy as np

# Initialize variables for squares and their positions
squares = []
dragging = False
drag_idx = -1
drag_offset = (0, 0)
saved_squares = {}  # Dictionary to store square positions when "s" is pressed

# Parameters
square_size = 32
outline_thickness = 2  # Outline thickness for hollow squares
faces = ['U', 'D', 'F']
positions = [(x * (square_size + 10), y * (square_size + 10)) for y in range(3) for x in range(9)]
face_labels = [f'{face}{i + 1}' for face in faces for i in range(9)]  # Labels U1-U9, D1-D9, F1-F9

# Initialize positions for each square
for i in range(27):
    squares.append({
        'label': face_labels[i],
        'pos': positions[i % 9]
    })


# Function to draw squares on the frame
def draw_squares(frame):
    for square in squares:
        x, y = square['pos']
        label = square['label']
        # Draw hollow green square with a green outline
        cv2.rectangle(frame, (x, y), (x + square_size, y + square_size), (0, 255, 0), outline_thickness)
        # Draw the label inside the square
        cv2.putText(frame, label, (x + 5, y + square_size // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


# Mouse event callback function for dragging squares
def mouse_events(event, x, y, flags, param):
    global dragging, drag_idx, drag_offset

    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if we clicked on any square
        for i, square in enumerate(squares):
            sx, sy = square['pos']
            if sx < x < sx + square_size and sy < y < sy + square_size:
                dragging = True
                drag_idx = i
                drag_offset = (x - sx, y - sy)
                break

    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging and drag_idx != -1:
            squares[drag_idx]['pos'] = (x - drag_offset[0], y - drag_offset[1])

    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
        drag_idx = -1


# Function to save squares to a dictionary
def save_squares_to_dict():
    global saved_squares
    saved_squares = {square['label']: (square['pos'][0], square['pos'][1], square_size, square_size) for square in
                     squares}
    print(saved_squares)  # Print the dictionary after saving


# Capture video from webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Set up mouse callback for dragging
cv2.namedWindow('Webcam')
cv2.setMouseCallback('Webcam', mouse_events)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw hollow squares on the frame
    draw_squares(frame)

    # Display the frame
    cv2.imshow('Webcam', frame)

    # Check for key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Save the squares to the dictionary and print it when "s" is pressed
        save_squares_to_dict()

# Release resources
cap.release()
cv2.destroyAllWindows()
