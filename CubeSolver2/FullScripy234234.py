choices_list = ["training", "testing", "prediction", "full pictures"]
print("What would you like to choose:")
for i in range(1, len(choices_list) + 1):
    print(f"{i} for {choices_list[i - 1]}")

choice = int(input("Enter the number corresponding to your choice: "))
subchoice = str(input("Is this webcam based or photo based"))
subsubchoice = str(input("Would you like to create the square list?"))
camerachoice = int(input("What camera would you like to use?"))

import cv2
import os
import time

def createtesttrainimages(choice):
    squares = {'front': [], 'left': [], 'down': [], 'up': [], 'right': [], 'bottom': []}
    drawing = False  # True if the mouse is pressed
    ix, iy = -1, -1
    current_face = 'front'
    square_counter = {'front': 1, 'left': 1, 'down': 1, 'up': 1, 'right': 1, 'bottom': 1}
    first_phase_complete = False
    frame = None
    colors = str(input('Write the colors of the cube: '))
    colors_list = list(colors)
    def get_next_set_number(directory):
        count = 1
        while True:
            prefix = f'{count}-'
            substring = f'.{count}-'
            files_with_prefix_or_substring = any(fn.startswith(prefix) for fn in os.listdir(directory))
            files_two = any(substring in fn for fn in os.listdir(directory))
            if files_with_prefix_or_substring == True or files_two == True:
                pass
            else:
                print(f"count is {count}")
                return count
            count += 1
    def get_next_face(current_face):
        face_order = ['front', 'left', 'down']# 'up', 'right', 'bottom']
        current_index = face_order.index(current_face)
        return face_order[(current_index + 1) % len(face_order)]
    def draw_square(event, x, y, flags, param):
        global ix, iy, drawing, squares, current_face, square_counter, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_copy = frame.copy()  # Use the globally defined frame
                cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
                cv2.imshow('Webcam', img_copy)
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
            if square_counter[current_face] > 9:
                current_face = get_next_face(current_face)
                print(f"Switched to {current_face} face")

    def capture_squares_for_faces(cap, face_keys):
        global current_face, first_phase_complete, frame
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break
            cv2.imshow('Webcam', frame)
            k = cv2.waitKey(1) & 0xFF
            for key in face_keys:
                if k == ord(key[0]):
                    current_face = key
                    print(f"Switched to {key} face")
            if all(len(squares[face]) == 9 for face in face_keys):
                break
            if k == ord('q'):
                first_phase_complete = True
                break

    if camerachoice is int:
        cap = cv2.VideoCapture(camerachoice, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cv2.namedWindow('Webcam')
    cv2.setMouseCallback('Webcam', draw_square)
    capture_squares_for_faces(cap, ['front', 'left', 'down'])
    print(squares)
    polygons = {}
    for direction, items in squares.items():
        for item in items:
            key = item[0]  # The text part ('F1', 'L1', etc.)
            value = item[1:]  # The rest of the tuple
            polygons[key] = value
    grid_labels = ['F', 'L', 'D']  # Labels corresponding to the face of the cube
    starting_set_number = 1         # Starting number for the sets
    current_file_path = os.path.abspath(__file__)
    parent_directory = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), "testing")
    starting_set_number = get_next_set_number(parent_directory)
    time.sleep(2)
    for i in range(30):
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            exit()
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image")
    else:
        for grid_index, grid_label in enumerate(grid_labels):
            print(f"grid index is {grid_index}")
            for i in range(3):
                for j in range(3):
                    number = grid_index * 9 + i * 3 + j
                    # Calculate the region index based on grid index, i, and j
                    region_key = f'{grid_label}{3 * i + j + 1}'
                    if region_key in polygons:
                        x, y, w, h = polygons[region_key]
                        roi = frame[y:y+h, x:x+w]
                        filename = f"{parent_directory}\{colors_list[number]}.{starting_set_number}-{grid_index + 1}-{region_key}.png"
                        cv2.imwrite(filename, roi)
                        print(f"Saved: {filename}")
        for (x, y, w, h) in polygons.values():
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imshow('Webcam Frame with Regions', frame)
        cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()
