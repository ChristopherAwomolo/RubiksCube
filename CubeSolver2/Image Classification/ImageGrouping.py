import os
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

class ImageLabeler:
    def __init__(self, root, file_list):
        self.root = root
        self.file_list = file_list
        self.index = 0

        self.color_map = {
            'G': 'Green',
            'B': 'Blue',
            'O': 'Orange',
            'W': 'White',
            'Y': 'Yellow',
            'R': 'Red'
        }

        # Setup the GUI
        self.image_label = tk.Label(root)
        self.image_label.pack()

        button_frame = tk.Frame(root)
        button_frame.pack()

        for key, color in self.color_map.items():
            button = tk.Button(button_frame, text=color, command=lambda k=key: self.label_image(k))
            button.pack(side=tk.LEFT)

        self.display_image()

    def display_image(self):
        if self.index < len(self.file_list):
            img_path = self.file_list[self.index]
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img
        else:
            self.root.quit()  # Exit if no more images

    def label_image(self, label_initial):
        if self.index < len(self.file_list):
            img_path = self.file_list[self.index]
            img_name = os.path.basename(img_path)
            new_name = f"{label_initial}.{img_name}"
            new_path = os.path.join(os.path.dirname(img_path), new_name)
            os.rename(img_path, new_path)
            self.index += 1
            self.display_image()

def main():
    root = tk.Tk()
    root.title("Image Labeler")

    file_list = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    file_list = list(file_list)  # Convert to list

    if not file_list:
        print("No files selected.")
        return

    app = ImageLabeler(root, file_list)
    root.mainloop()

if __name__ == "__main__":
    main()
