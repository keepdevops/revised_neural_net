import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class GridMatplotlibToolbar(NavigationToolbar2Tk):
    """Custom matplotlib toolbar that uses grid layout instead of pack."""
    
    def __init__(self, canvas, window):
        self.toolbar_frame = tk.Frame(window)
        super().__init__(canvas, self.toolbar_frame)
        window.grid_columnconfigure(0, weight=1)
        self.toolbar_frame.grid_columnconfigure(0, weight=1) 