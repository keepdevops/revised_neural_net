#!/usr/bin/env python3
"""
Simple GUI Test to verify tkinter functionality
"""

import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Simple GUI Test")
    root.geometry("800x600")
    root.configure(bg="#2E2E2E")
    
    # Create a simple frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add a label
    label = ttk.Label(main_frame, text="GUI Test - If you can see this, tkinter is working!")
    label.pack(pady=20)
    
    # Add a button
    button = ttk.Button(main_frame, text="Test Button", command=lambda: print("Button clicked!"))
    button.pack(pady=10)
    
    # Add a notebook
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Add a tab
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Test Tab")
    
    # Add content to tab
    tab_label = ttk.Label(tab1, text="This is a test tab")
    tab_label.pack(pady=20)
    
    tab_button = ttk.Button(tab1, text="Tab Button", command=lambda: print("Tab button clicked!"))
    tab_button.pack(pady=10)
    
    # Add status bar
    status_var = tk.StringVar(value="Ready")
    status_label = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    print("Simple GUI test window should be visible now")
    root.mainloop()

if __name__ == "__main__":
    main() 