import os
import sys

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from scipy.optimize import minimize_scalar

from src import videoCrop
from src.imageTools import radialUndistort, perspectiveUndistort, getFrameFromVideo

class AdvancedDistortionCorrectionTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Distortion Correction Tool")
        self.master.geometry("1200x800")

        self.image = None
        self.original_image = None
        self.displayed_image = None
        self.k = 0  # Initialize K value
        self.dots = []
        self.dragging = None

        # Create UI elements
        # self.load_button = tk.Button(self.master, text="Load Image", command=self.load_image)
        # self.load_button.pack(pady=10)

        self.canvas = tk.Canvas(self.master)
        self.canvas.pack()
        # self.canvas.width
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.k_label = tk.Label(self.master, text="K value: 0")
        self.k_label.pack(pady=5)

        self.k_slider = tk.Scale(self.master, from_=-1.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, length=300, command=self.update_k)
        self.k_slider.pack(pady=10)

        self.zoom_slider = tk.Scale(self.master, from_=0.5, to=5.0, resolution=0.01, orient=tk.HORIZONTAL, label="Zoom", length=300, command=self.update_zoom)
        self.zoom_slider.pack(pady=10)

        self.perspective_var = tk.BooleanVar()
        self.perspective_check = tk.Checkbutton(self.master, text="Apply Perspective Correction", variable=self.perspective_var, command=self.update_persp)
        self.perspective_check.pack(pady=10)

        self.save_button = tk.Button(self.master, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        self.display_image_scale = 0.5

        self.k_value = 0
        self.zoom_value = 1

    def update_zoom(self, zoom_value):
        self.zoom_value = zoom_value
        self.update_image(self.k_value, zoom_value)

    def update_k(self, k_value):
        self.k_value = k_value
        self.update_image(k_value, self.zoom_value)

    def update_persp(self):
        self.update_image(self.k_value, self.zoom_value)

    def load_image(self, image):
        print(image)
        self.original_image = image
        self.save_button.config(state=tk.NORMAL)
        height, width = self.original_image.shape[:2]
        self.dots = [
            [10, 10],
            [width-10, 10],
            [width-10, height-10],
            [10, height-10]
        ]
        self.update_image(self.k_value, self.zoom_value)

    def display_image(self):
        if self.image is not None:
            self.displayed_image = self.image.copy()
            if not self.perspective_var.get():
                for x, y in self.dots:
                    cv2.circle(self.displayed_image, (int(x), int(y)), 15, (0, 255, 0), -1)
            image = cv2.cvtColor(self.displayed_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image.thumbnail((image.width*self.display_image_scale, image.height*self.display_image_scale), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

    def update_image(self, k_value, zoom_value):
        if self.original_image is None:
            return

        self.image = radialUndistort(self.original_image, float(k_value), float(zoom_value))

        if self.perspective_var.get():
            self.image = perspectiveUndistort(self.image, self.dots)

        self.display_image()
        self.k_label.config(text=f"K value: {self.k:.2f}")

    def count_lines(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        return len(lines) if lines is not None else 0

    def on_click(self, event):
        x, y = event.x / self.display_image_scale, event.y / self.display_image_scale
        for i, (dot_x, dot_y) in enumerate(self.dots):
            if abs(x - dot_x) < 50 and abs(y - dot_y) < 50:
                self.dragging = i
                break


    def on_drag(self, event):
        if self.dragging is not None:
            self.dots[self.dragging] = [event.x / self.display_image_scale, event.y / self.display_image_scale]
            self.update_image(self.k_value, self.zoom_value)

    def on_release(self, event):
        self.dragging = None

    def save_image(self):
        print(",".join([
            str(self.k_value),
            str(self.zoom_value),

            str(self.dots[0][0]),
            str(self.dots[0][1]),
            str(self.dots[1][0]),
            str(self.dots[1][1]),
            str(self.dots[2][0]),
            str(self.dots[2][1]),
            str(self.dots[3][0]),
            str( self.dots[3][1])
        ]))

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: undistort.py <event code>")
    filename = sys.argv[1] + "/" + (os.listdir(sys.argv[1])[0])

    root = tk.Tk()
    app = AdvancedDistortionCorrectionTool(root)

    start, stop = videoCrop.videoCrop(filename)
    if start != stop:
        print("Found video start and end")

    app.load_image(getFrameFromVideo(filename, start))

    root.mainloop()
