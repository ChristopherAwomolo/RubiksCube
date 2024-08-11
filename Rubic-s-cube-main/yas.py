from tkinter import *
from vpython import *
import numpy as np
import random
from solve_rubiccs_cube import *
from cube import Rubic_Cube
class RubicCubeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Rubik's Cube")

        self.rubic_cube = Rubic_Cube()

        # Create the canvas to display the Rubik's Cube
        self.canvas = Canvas(master, width=800, height=800)
        self.canvas.pack()

        # Create the buttons
        self.create_buttons()

        # Start the main loop
        self.rubic_cube.start()

    def create_buttons(self):
        # Create the buttons and bind them to the corresponding methods
        Button(self.master, text="F", command=self.rubic_cube.rotate_front_clock).pack(side=LEFT)
        Button(self.master, text="F'", command=self.rubic_cube.rotate_front_counter).pack(side=LEFT)
        Button(self.master, text="R", command=self.rubic_cube.rotate_right_clock).pack(side=LEFT)
        Button(self.master, text="R'", command=self.rubic_cube.rotate_right_counter).pack(side=LEFT)
        Button(self.master, text="B", command=self.rubic_cube.rotate_back_clock).pack(side=LEFT)
        Button(self.master, text="B'", command=self.rubic_cube.rotate_back_counter).pack(side=LEFT)
        Button(self.master, text="L", command=self.rubic_cube.rotate_left_clock).pack(side=LEFT)
        Button(self.master, text="L'", command=self.rubic_cube.rotate_left_counter).pack(side=LEFT)
        Button(self.master, text="U", command=self.rubic_cube.rotate_top_clock).pack(side=LEFT)
        Button(self.master, text="U'", command=self.rubic_cube.rotate_top_counter).pack(side=LEFT)
        Button(self.master, text="D", command=self.rubic_cube.rotate_bottom_clock).pack(side=LEFT)
        Button(self.master, text="D'", command=self.rubic_cube.rotate_bottom_counter).pack(side=LEFT)
        Button(self.master, text="Scramble", command=self.rubic_cube.scramble).pack(side=LEFT)
        Button(self.master, text="Solve", command=self.rubic_cube.solve).pack(side=LEFT)

root = Tk()
app = RubicCubeGUI(root)
root.mainloop()