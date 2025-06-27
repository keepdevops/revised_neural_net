"""
3D Plot Window Module

This module provides a dedicated window for 3D plotting visualization.
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class Plot3DWindow:
    """Dedicated window for 3D plotting visualization."""
    
    def __init__(self, parent, fig, toolbar=None, on_close=None):
        """
        Initialize the 3D plot window.
        
        Args:
            parent: Parent window
            fig: Matplotlib figure to display
            toolbar: Matplotlib toolbar (optional)
            on_close: Callback function when window is closed
        """
        self.parent = parent
        self.fig = fig
        self.toolbar = toolbar
        self.on_close = on_close
        
        # Create the window
        self.window = tk.Toplevel(parent)
        self.window.title("3D Plot Viewer")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configure window
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(fig, main_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Add toolbar if provided
        if toolbar:
            self.toolbar = NavigationToolbar2Tk(self.canvas, main_frame)
            self.toolbar.grid(row=1, column=0, sticky="ew")
        
        # Add control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Dock button
        dock_btn = ttk.Button(button_frame, text="Dock Viewer", command=self._dock_viewer)
        dock_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Close button
        close_btn = ttk.Button(button_frame, text="Close Window", command=self._on_closing)
        close_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="3D Plot Viewer Ready")
        self.status_label.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    
    def _on_closing(self):
        """Handle window closing."""
        if self.on_close:
            self.on_close()
        self.window.destroy()
    
    def _dock_viewer(self):
        """Dock the viewer back to the main window."""
        if self.on_close:
            self.on_close()
        self.window.destroy()
    
    def update_plot(self, fig):
        """Update the plot with a new figure."""
        self.fig = fig
        self.canvas.figure = fig
        self.canvas.draw()
        self.status_label.config(text="Plot updated")
    
    def set_status(self, message):
        """Set the status message."""
        self.status_label.config(text=message)# gui/windows/plot_3d_window.py


