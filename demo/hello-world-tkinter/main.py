"""
minimal tkinter demo app.
"""

import tkinter as tk

# Create the main application window
root = tk.Tk()

# Set the window title
root.title("Hello World App")

# Create a label widget with the text "Hello, World!"
hello_label = tk.Label(root, text="Hello, World!")

# Place the label in the window using pack() geometry manager
hello_label.pack()

# Start the Tkinter event loop
root.mainloop()
