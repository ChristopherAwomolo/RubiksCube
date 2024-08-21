import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU
from rubik import Rubik

def main():
    rubik = Rubik(2)
    #rotate_cube = {pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_LEFT: (1, -1), pygame.K_RIGHT: (1, 1)}
    rotate_slc = {
        pygame.K_1: (0, 0, 1), pygame.K_2: (0, 1, 1), pygame.K_3: (0, 2, 1),
        pygame.K_4: (1, 0, 1), pygame.K_5: (1, 1, 1), pygame.K_6: (1, 2, 1),
        pygame.K_7: (2, 0, 1), pygame.K_8: (2, 1, 1), pygame.K_9: (2, 2, 1)
    }

    ang_x, ang_y = 0, 0
    mouse_down = False
    last_mouse_pos = None

    rotation_matrix = GL.GLfloat * 16
    rot_matrix = rotation_matrix(1, 0, 0, 0,
                                 0, 1, 0, 0,
                                 0, 0, 1, 0,
                                 0, 0, 0, 1)

    animate = False
    animate_ang = 0
    animate_speed = 5
    rotate = (0, 0, 0)
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not animate and event.key in rotate_slc:
                    animate = True
                    rotate = rotate_slc[event.key]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_down = False
                    last_mouse_pos = None

            if event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    mouse_pos = pygame.mouse.get_pos()
                    if last_mouse_pos:
                        dx = mouse_pos[0] - last_mouse_pos[0]
                        dy = mouse_pos[1] - last_mouse_pos[1]

                        # Rotate around x and y axes
                        ang_x += dy * 0.5
                        ang_y += dx * 0.5

                        # Create rotation matrices for x and y axis separately
                        GL.glPushMatrix()
                        GL.glLoadIdentity()
                        GL.glRotatef(dx * 0.5, 0, 1, 0)  # Rotate around y-axis
                        GL.glMultMatrixf(rot_matrix)
                        GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, rot_matrix)
                        GL.glPopMatrix()

                        GL.glPushMatrix()
                        GL.glLoadIdentity()
                        GL.glRotatef(dy * 0.5, 1, 0, 0)  # Rotate around x-axis
                        GL.glMultMatrixf(rot_matrix)
                        GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, rot_matrix)
                        GL.glPopMatrix()

                    last_mouse_pos = mouse_pos

        GL.glMatrixMode(GL.GL_MODELVIEW)

        GL.glLoadIdentity()
        GL.glTranslatef(0, 0, -40)
        GL.glRotatef(ang_y, 0, 1, 0)
        GL.glRotatef(ang_x, 1, 0, 0)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glClearColor(1, 1, 1, 1)

        if animate:
            if animate_ang >= 90:
                for cube in rubik.cubes:
                    cube.update(*rotate)
                animate = False
                animate_ang = 0

        for cube in rubik.cubes:
            cube.draw(cube.polygons, animate, animate_ang, *rotate)
        if animate:
            animate_ang += animate_speed

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    pygame.init()
    display = (1080, 720)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Directional arrows to rotate the cube, keys from 1 to 9 to rotate each faces")
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GLU.gluPerspective(45, (display[0] / display[1]), 1, 50.0)
    main()
    pygame.quit()
