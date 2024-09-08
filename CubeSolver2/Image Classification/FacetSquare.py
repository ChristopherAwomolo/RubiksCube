import cv2

# Initialize global variables
squares = {'front': [], 'left': [], 'down': [], 'up': [], 'right': [], 'bottom': []}
drawing = False  # True if the mouse is pressed
ix, iy = -1, -1
current_face = 'front'
square_counter = {'front': 1, 'left': 1, 'down': 1, 'up': 1, 'right': 1, 'bottom': 1}
first_phase_complete = False
frame = None  # Define the frame globally


# Function to get the next face in the sequence
def get_next_face(current_face):
    face_order = ['front', 'left', 'down', 'up', 'right', 'bottom']
    current_index = face_order.index(current_face)
    return face_order[(current_index + 1) % len(face_order)]


# Mouse callback function
def draw_square(event, x, y, flags, param):
    global ix, iy, drawing, squares, current_face, square_counter, frame

    # When the left mouse button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    # When the mouse is moved with the left button pressed down
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = frame.copy()  # Use the globally defined frame
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Webcam', img_copy)

    # When the left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(frame, (ix, iy), (x, y), (0, 255, 0), 2)
        width = abs(x - ix)
        height = abs(y - iy)

        square_id = f"{current_face[0].upper()}{square_counter[current_face]}"
        squares[current_face].append((square_id, ix, iy, width, height))

        #with open('Polygons.txt', "w") as file:
        #    file.write(f"'{square_id}': ({ix}, {iy}, {width}, {height}),")
        print(f"'{square_id}': ({ix}, {iy}, {width}, {height}),")

        square_counter[current_face] += 1
        cv2.imshow('Webcam', frame)

        # Switch to the next face if 9 squares are drawn
        if square_counter[current_face] > 9:
            current_face = get_next_face(current_face)
            print(f"Switched to {current_face} face")


# Function to capture squares for a set of faces
def capture_squares_for_faces(cap, face_keys):
    global current_face, first_phase_complete, frame

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        cv2.imshow('Webcam', frame)

        k = cv2.waitKey(1) & 0xFF

        # Switch between faces manually using keys
        for key in face_keys:
            if k == ord(key[0]):
                current_face = key
                print(f"Switched to {key} face")

        # Check if all squares are drawn for current set of faces
        if all(len(squares[face]) == 9 for face in face_keys):
            break

        # Press 'q' to exit early
        if k == ord('q'):
            first_phase_complete = True
            break


# First phase: Capture squares for front, left, down using VideoCapture(0) with CAP_DSHOW
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow('Webcam')
cv2.setMouseCallback('Webcam', draw_square)

capture_squares_for_faces(cap, ['front', 'left', 'down'])

# Release first camera
cap.release()
cv2.destroyAllWindows()

'''
# If first phase is complete, proceed to second phase
if first_phase_complete or all(len(squares[face]) == 9 for face in ['front', 'left', 'down']):
    # Second phase: Capture squares for up, right, bottom using VideoCapture(1) with CAP_DSHOW
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    cv2.namedWindow('Webcam')
    cv2.setMouseCallback('Webcam', draw_square)

    capture_squares_for_faces(cap, ['up', 'right', 'bottom'])

    # Release second camera and close all windows
    cap.release()
    cv2.destroyAllWindows()

# Final output of all squares
print("\nFinal Squares Data:")
for face, square_list in squares.items():
    for square in square_list:
        print(f"{square[0]}: Top-Left: ({square[1]}, {square[2]}), Width: {square[3]}, Height: {square[4]}")
'''