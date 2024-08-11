import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Initialize Pygame and set up the display
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('Rubik\'s Cube with GUI')

# Set up OpenGL perspective
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -7)
glRotatef(25, 2, 1, 0)

# Define the vertices and edges of a cube
vertices = np.array([
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1]
])

edges = (
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
)

# Define colors for each face of the cube
colors = [
    (1, 0, 0),    # Red
    (0, 1, 0),    # Green
    (0, 0, 1),    # Blue
    (1, 1, 0),    # Yellow
    (1, 0.5, 0),  # Orange
    (1, 1, 1)     # White
]

# Define the structure of the Rubik's Cube
cube_structure = np.zeros((3, 3, 3), dtype=int)

# Function to draw a single cubelet with given color and position
def draw_cubelet(color, position):
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glBegin(GL_QUADS)
    glColor3fv(color)
    for face in range(6):
        glVertex3fv(vertices[edges[face][0]])
        glVertex3fv(vertices[edges[face][1]])
        glVertex3fv(vertices[edges[face][1]] * 0.9)
        glVertex3fv(vertices[edges[face][0]] * 0.9)
    glEnd()
    glPopMatrix()

# Function to draw the entire Rubik's Cube
def draw_rubiks_cube(cube_structure):
    for x in range(3):
        for y in range(3):
            for z in range(3):
                if cube_structure[x][y][z] != 0:
                    color_index = cube_structure[x][y][z] - 1
                    color = colors[color_index]
                    draw_cubelet(color, (x*2-2, y*2-2, z*2-2))

# Main rendering loop
running = True
rotate_cube = False
rotate_speed = 0.2
rotate_x, rotate_y = 0, 0
last_mouse_pos = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rotate_cube = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            rotate_cube = False
            last_mouse_pos = None

    if rotate_cube:
        current_mouse_pos = pygame.mouse.get_pos()
        if last_mouse_pos:
            dx, dy = current_mouse_pos[0] - last_mouse_pos[0], current_mouse_pos[1] - last_mouse_pos[1]
            rotate_x += dy * rotate_speed
            rotate_y += dx * rotate_speed
            glRotatef(dx * rotate_speed, 0, 1, 0)
            glRotatef(dy * rotate_speed, 1, 0, 0)
        last_mouse_pos = current_mouse_pos

    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Draw the Rubik's Cube
    draw_rubiks_cube(cube_structure)

    # Update the display
    pygame.display.flip()
    pygame.time.wait(10)  # Adjust for frame rate

# Quit Pygame
pygame.quit()
