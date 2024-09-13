import kociemba

# Correct color to face mapping (this is an example for a typical Rubik's Cube color scheme)
color_to_face = {
    5: 'U',  # White -> Up
    1: 'L',  # Blue -> Left
    3: 'F',  # Orange -> Front
    4: 'R',  # Red -> Right
    2: 'B',  # Green -> Back
    6: 'D'   # Yellow -> Down
}

# A valid, scrambled Rubik's Cube (make sure the cube is solvable)
cube_dict = {
    'U1': 5, 'U2': 5, 'U3': 5, 'U4': 5, 'U5': 5, 'U6': 5, 'U7': 5, 'U8': 5, 'U9': 5,  # Up (White)
    'L1': 1, 'L2': 1, 'L3': 1, 'L4': 1, 'L5': 1, 'L6': 1, 'L7': 1, 'L8': 1, 'L9': 1,  # Left (Blue)
    'F1': 3, 'F2': 3, 'F3': 3, 'F4': 3, 'F5': 3, 'F6': 3, 'F7': 3, 'F8': 3, 'F9': 3,  # Front (Orange)
    'R1': 4, 'R2': 4, 'R3': 4, 'R4': 4, 'R5': 4, 'R6': 4, 'R7': 4, 'R8': 4, 'R9': 4,  # Right (Red)
    'B1': 2, 'B2': 2, 'B3': 2, 'B4': 2, 'B5': 2, 'B6': 2, 'B7': 2, 'B8': 2, 'B9': 2,  # Back (Green)
    'D1': 6, 'D2': 6, 'D3': 6, 'D4': 6, 'D5': 6, 'D6': 6, 'D7': 6, 'D8': 6, 'D9': 6   # Down (Yellow)
}

# Ensure the cube string is correctly constructed
face_order = 'U L F R B D'.split()
face_positions = {
    'U': ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9'],
    'L': ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9'],
    'F': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9'],
    'R': ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9'],
    'B': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'],
    'D': ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9'],
}

# Construct the cube string
cube_string = ''.join(color_to_face[cube_dict[pos]] for face in face_order for pos in face_positions[face])

# Solve the cube
solution = kociemba.solve(cube_string)

print(f"Cube String: {cube_string}")
print(f"Solution: {solution}")
