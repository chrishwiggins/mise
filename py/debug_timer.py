#!/usr/bin/env python3
"""
Simple Tkinter Debug Test Window

This script creates a basic tkinter window with test labels to debug
GUI display issues. Useful for testing if tkinter is working properly
and if fonts/colors render correctly on your system.
"""

import os

os.environ["TK_SILENCE_DEPRECATION"] = "1"

import tkinter as tk

root = tk.Tk()
root.title("DEBUG")
root.geometry("200x150")

# Try different approaches
label1 = tk.Label(root, text="TEST 1")
label1.pack()

label2 = tk.Label(root, text="TEST 2", font=("Arial", 12))
label2.pack()

label3 = tk.Label(root, text="TEST 3", bg="white", fg="black")
label3.pack()

# Force update
root.update()
root.mainloop()
