import kociemba

def solve_cube(cube_dict):
    color_to_face = {}
    for key, value in cube_dict.items():
        if key.endswith('5'):  # This identifies the center pieces
            color_to_face[value] = key[0]
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    cube_string = ''
    for face in face_order:
        for i in range(1, 10):  # 1 to 9
            key = f'{face}{i}'
            color = cube_dict[key]
            cube_string += color_to_face[color]
    print(f"Cube string: {cube_string}")
    try:
        solution = kociemba.solve(cube_string)
        print(f"Solution: {solution}")
    except ValueError as e:
        print(f"Error: {e}")
        print("The cube configuration might be invalid or unsolvable.")

# Your cube dictionary
cube_dict = {
    'U1': 'O', 'U2': 'R', 'U3': 'R', 'U4': 'O', 'U5': 'O', 'U6': 'R', 'U7': 'Y', 'U8': 'W', 'U9': 'Y',
    'R1': 'B', 'R2': 'Y', 'R3': 'W', 'R4': 'G', 'R5': 'B', 'R6': 'Y', 'R7': 'Y', 'R8': 'W', 'R9': 'O',
    'F1': 'R', 'F2': 'G', 'F3': 'O', 'F4': 'B', 'F5': 'W', 'F6': 'O', 'F7': 'B', 'F8': 'B', 'F9': 'G',
    'D1': 'R', 'D2': 'R', 'D3': 'O', 'D4': 'B', 'D5': 'R', 'D6': 'R', 'D7': 'Y', 'D8': 'G', 'D9': 'W',
    'L1': 'W', 'L2': 'Y', 'L3': 'B', 'L4': 'W', 'L5': 'G', 'L6': 'O', 'L7': 'R', 'L8': 'W', 'L9': 'W',
    'B1': 'G', 'B2': 'G', 'B3': 'G', 'B4': 'B', 'B5': 'Y', 'B6': 'O', 'B7': 'B', 'B8': 'Y', 'B9': 'G'
}

# Solve the cube
solve_cube(cube_dict)