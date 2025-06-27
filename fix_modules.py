#!/usr/bin/env python3
"""
Script to fix all missing modular components
"""

import os

def create_missing_modules():
    """Create all missing module files."""
    
    # Define the modules and their content
    modules = {
        'gui/core/__init__.py': '',
        'gui/visualization/__init__.py': '',
        'gui/training/__init__.py': '',
        'gui/prediction/__init__.py': '',
        'gui/utils/__init__.py': '',
        'gui/windows/__init__.py': '',
        
        'gui/utils/path_utils.py': '''
"""
Path Utils Module
"""
import os
import json
import logging

class PathUtils:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_ticker_from_filename(self, filename):
        """Extract ticker symbol from filename."""
        try:
            # Extract ticker from filename patterns like "AAPL_data.csv" or "AAPL_20240101.csv"
            basename = os.path.basename(filename)
            parts = basename.split('_')
            if len(parts) > 0:
                return parts[0].upper()
            return "UNKNOWN"
        except Exception as e:
            self.logger.error(f"Error extracting ticker: {e}")
            return "UNKNOWN"
    
    def validate_path(self, path):
        """Validate if a path exists and is accessible."""
        if not path:
            return False, "Path is empty"
        if not os.path.exists(path):
            return False, "Path does not exist"
        if not os.access(path, os.R_OK):
            return False, "Path is not readable"
        return True, ""
''',
        
        'gui/visualization/plot_manager.py': '''
"""
Plot Manager Module - Placeholder
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class PlotManager:
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
    
    def create_figure_with_toolbar(self, parent, figsize=(10, 6)):
        """Create a matplotlib figure with embedded toolbar."""
        fig = Figure(figsize=figsize)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        return fig, canvas, toolbar
    
    def plot_training_results(self, model_dir, parent_frame):
        """Plot training results from a model directory."""
        # Clear existing plot
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create placeholder
        label = ttk.Label(parent_frame, text="Training Results Plot - Placeholder")
        label.pack(expand=True)
    
    def plot_prediction_results(self, prediction_file, parent_frame):
        """Plot prediction results from a CSV file."""
        # Clear existing plot
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create placeholder
        label = ttk.Label(parent_frame, text="Prediction Results Plot - Placeholder")
        label.pack(expand=True)
    
    def create_3d_gradient_descent_plot(self, parent_frame, model_dir):
        """Create 3D gradient descent visualization."""
        # Clear existing plot
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create placeholder
        label = ttk.Label(parent_frame, text="3D Gradient Descent Plot - Placeholder")
        label.pack(expand=True)
    
    def clear_cache(self):
        """Clear the image cache."""
        pass
''',
        
        'gui/training/training_manager.py': '''
"""
Training Manager Module - Placeholder
"""
import tkinter as tk
from tkinter import messagebox

class TrainingManager:
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
    
    def start_training(self, params, callback=None):
        """Start training process."""
        messagebox.showinfo("Training", "Training started - Placeholder implementation")
        return True
    
    def stop_training(self):
        """Stop the current training process."""
        pass
    
    def get_training_status(self):
        """Get current training status."""
        return {"is_training": False}
    
    def cleanup(self):
        """Clean up training resources."""
        pass
''',
        
        'gui/prediction/prediction_manager.py': '''
"""
Prediction Manager Module - Placeholder
"""
import tkinter as tk
from tkinter import messagebox

class PredictionManager:
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
    
    def make_prediction(self, model_dir, data_file, callback=None):
        """Make predictions using the specified model."""
        messagebox.showinfo("Prediction", "Prediction started - Placeholder implementation")
        return True
    
    def get_prediction_files(self, model_dir):
        """Get list of prediction files for a model."""
        return []
    
    def load_prediction_results(self, prediction_file):
        """Load prediction results from a CSV file."""
        return None
    
    def get_prediction_summary(self, prediction_file):
        """Get summary statistics for prediction results."""
        return {}
''',
        
        'gui/windows/specialized_windows.py': '''
"""
Specialized Windows Module - Placeholder
"""
import tkinter as tk
from tkinter import ttk

class LiveTrainingWindow:
    def __init__(self, parent, title="Live Training Progress"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x300")
        ttk.Label(self.window, text="Live Training Window - Placeholder").pack(expand=True)
    
    def update_progress(self, epoch, loss, val_loss=None):
        pass
    
    def stop_training(self):
        pass
    
    def clear_plot(self):
        pass

class SettingsDialog:
    def __init__(self, parent, settings=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("300x200")
        ttk.Label(self.window, text="Settings Dialog - Placeholder").pack(expand=True)
    
    def show(self):
        return {}

class HelpWindow:
    def __init__(self, parent, title="Help"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x400")
        ttk.Label(self.window, text="Help Window - Placeholder").pack(expand=True)

class AboutDialog:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("About")
        self.window.geometry("300x200")
        ttk.Label(self.window, text="About Dialog - Placeholder").pack(expand=True)
'''
    }
    
    # Create directories and files
    for file_path, content in modules.items():
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create file if it doesn't exist or is empty
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 10:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Created/Updated: {file_path}")
        else:
            print(f"Exists: {file_path}")

if __name__ == "__main__":
    create_missing_modules()
    print("Module creation complete!") 