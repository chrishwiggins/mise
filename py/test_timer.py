#!/usr/bin/env python3
"""
Simple Tkinter Timer Display Test

This script creates a minimal tkinter window displaying a timer label (00:05:00)
to test if tkinter renders correctly with system fonts. Useful for debugging
GUI display issues and font rendering on your system.
"""

import tkinter as tk

# Simple test window
root = tk.Tk()
root.title("Test Timer")
root.configure(bg="white")
root.geometry("200x100")

# Simple label with system default font
label = tk.Label(root, text="TEST TIMER", font=("System", 12), bg="white", fg="black")
label.pack(pady=20)

timer_label = tk.Label(
    root, text="00:05:00", font=("System", 16, "bold"), bg="white", fg="red"
)
timer_label.pack()

root.mainloop()
