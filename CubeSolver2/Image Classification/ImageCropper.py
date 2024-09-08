import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os


# Function to load images from the file dialog
def load_images():
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    return list(file_paths)


# Function to crop the image based on user input
def crop_image(event):
    global click_count, x1, y1, x2, y2

    # Ensure the click is within the image bounds
    def clamp(val, min_val, max_val):
        return max(min(val, max_val), min_val)

    if click_count == 0:
        x1, y1 = clamp(event.x, 0, image.width), clamp(event.y, 0, image.height)
        click_count += 1
    elif click_count == 1:
        x2, y2 = clamp(event.x, 0, image.width), clamp(event.y, 0, image.height)
        cropped_img = image.crop((x1, y1, x2, y2))

        # Save the cropped image in the same directory with the same name
        save_path = image_paths[img_index]
        cropped_img.save(save_path)
        print(f"Saved cropped image to {save_path}")

        click_count = 0
        next_image()


# Function to load the next image
def next_image():
    global img_index, image, tk_image, click_count

    click_count = 0  # Reset click count for the next image

    if img_index < len(image_paths) - 1:
        img_index += 1
        image = Image.open(image_paths[img_index])
        tk_image = ImageTk.PhotoImage(image)
        canvas.config(width=image.width, height=image.height)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    else:
        print("No more images to process.")
        root.quit()


# Function to skip the current image
def skip_image():
    print(f"Skipped image: {image_paths[img_index]}")
    next_image()


# Main program
root = tk.Tk()
root.title("Image Cropper")

# Initialize variables
click_count = 0
x1, y1, x2, y2 = 0, 0, 0, 0
img_index = -1

# Load images
image_paths = load_images()
if not image_paths:
    print("No images selected. Exiting.")
    root.quit()

# Create canvas to display the image
canvas = tk.Canvas(root)
canvas.pack()

# Bind mouse click event to the crop function
canvas.bind("<Button-1>", crop_image)

# Create a "Skip" button to skip the current image
skip_button = tk.Button(root, text="Skip", command=skip_image)
skip_button.pack()

# Start processing images
next_image()

root.mainloop()
