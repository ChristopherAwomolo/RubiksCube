import cv2

# Initialize global variables
squares = []
drawing = False  # True if the mouse is pressed
ix, iy = -1, -1

# Mouse callback function
def draw_square(event, x, y, flags, param):
    global ix, iy, drawing, squares

    # When the left mouse button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    # When the mouse is moved with the left button pressed down
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = frame.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Webcam', img_copy)

    # When the left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(frame, (ix, iy), (x, y), (0, 255, 0), 2)
        width = abs(x - ix)
        height = abs(y - iy)
        squares.append((ix, iy, width, height))
        print(f"Square: Top-Left: ({ix}, {iy}), Width: {width}, Height: {height}")
        cv2.imshow('Webcam', frame)

# Initialize webcam
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cv2.namedWindow('Webcam')
cv2.setMouseCallback('Webcam', draw_square)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        break

    # Display the frame
    cv2.imshow('Webcam', frame)

    k = cv2.waitKey(1) & 0xFF

    # Break the loop after 27 squares have been drawn
    if len(squares) >= 27:
        break

    # Press 'q' to exit the loop early
    if k == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
