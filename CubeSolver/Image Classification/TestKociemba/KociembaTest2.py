import kociemba

colors = ['B', 'G', 'O', 'R', 'W', 'Y']

cube_dict = {
    'U1': 2, 'U2': 3, 'U3': 3, 'U4': 2, 'U5': 2, 'U6': 3, 'U7': 5, 'U8': 4, 'U9': 5,
    'R1': 0, 'R2': 5, 'R3': 4, 'R4': 1, 'R5': 0, 'R6': 5, 'R7': 5, 'R8': 4, 'R9': 2,
    'F1': 3, 'F2': 1, 'F3': 2, 'F4': 0, 'F5': 4, 'F6': 2, 'F7': 0, 'F8': 0, 'F9': 1,
    'D1': 3, 'D2': 3, 'D3': 2, 'D4': 0, 'D5': 3, 'D6': 3, 'D7': 5, 'D8': 1, 'D9': 4,
    'L1': 4, 'L2': 5, 'L3': 0, 'L4': 4, 'L5': 1, 'L6': 2, 'L7': 3, 'L8': 4, 'L9': 4,
    'B1': 1, 'B2': 1, 'B3': 1, 'B4': 0, 'B5': 5, 'B6': 2, 'B7': 0, 'B8': 5, 'B9': 1
}

def solve_cube(cube_dict):
    color_to_face = {}
    cube_dict_initials = {}
    for key, value in cube_dict.items():
        cube_dict_initials[key] = colors[value][0]
        if key.endswith('5'):  # This identifies the center pieces
            color_to_face[colors[value]] = key[0]
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    cube_string = ''
    for face in face_order:
        for i in range(1, 10):  # 1 to 9
            key = f'{face}{i}'
            color = cube_dict_initials[key]
            cube_string += color_to_face[color]
    print(f"Cube string: {cube_string}")
    try:
        solution = kociemba.solve(cube_string)
        print(f"Solution: {solution}")
    except ValueError as e:
        print(f"Error: {e}")
        print("The cube configuration might be invalid or unsolvable.")


# Solve the cube
solve_cube(cube_dict)