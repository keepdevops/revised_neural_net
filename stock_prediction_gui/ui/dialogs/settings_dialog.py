"""
Settings dialog for the Stock Prediction GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SettingsDialog:
    """Settings dialog."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.result = None
        
        # Create the dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create widgets
        self.create_widgets()
        
        # Center dialog
        self.center_dialog()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Application Settings", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Settings notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # General settings tab
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="General")
        self.create_general_settings(general_frame)
        
        # Training settings tab
        training_frame = ttk.Frame(notebook, padding="10")
        notebook.add(training_frame, text="Training")
        self.create_training_settings(training_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side="right")
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side="left")
    
    def create_general_settings(self, parent):
        """Create general settings widgets."""
        # Max history size
        ttk.Label(parent, text="Max History Size:").grid(row=0, column=0, sticky="w", pady=5)
        self.max_history_var = tk.StringVar(value="10")
        ttk.Entry(parent, textvariable=self.max_history_var, width=10).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Auto-save interval
        ttk.Label(parent, text="Auto-save Interval (minutes):").grid(row=1, column=0, sticky="w", pady=5)
        self.auto_save_var = tk.StringVar(value="5")
        ttk.Entry(parent, textvariable=self.auto_save_var, width=10).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Enable logging
        self.enable_logging_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Enable Logging", variable=self.enable_logging_var).grid(row=2, column=0, columnspan=2, pady=5)
    
    def create_training_settings(self, parent):
        """Create training settings widgets."""
        # Training settings frame
        training_frame = ttk.LabelFrame(parent, text="Training Settings", padding="10")
        training_frame.pack(fill="x", pady=(0, 10))
        
        # Training settings widgets
        ttk.Label(training_frame, text="Training Parameters:").pack(anchor="w")
        
        self.training_params_var = tk.StringVar(value="")
        self.training_params_entry = ttk.Entry(training_frame, textvariable=self.training_params_var, width=50)
        self.training_params_entry.pack(fill="x", pady=(5, 0))
        
        ttk.Button(training_frame, text="Browse", command=self.browse_training_params).pack(side="right", padx=(5, 0))
        
        # Use current data checkbox
        self.use_current_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(training_frame, text="Use currently loaded data", variable=self.use_current_data_var, 
                       command=self.on_use_current_data_change).pack(anchor="w", pady=(10, 0))
    
    def on_ok(self):
        """Handle OK button click."""
        self.result = {
            'max_history_size': self.max_history_var.get(),
            'auto_save_interval': self.auto_save_var.get(),
            'enable_logging': self.enable_logging_var.get(),
            'training_params': self.training_params_var.get(),
            'use_current_data': self.use_current_data_var.get()
        }
        self.dialog.destroy()
    
    def on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def reset_defaults(self):
        """Handle Reset to Defaults button click."""
        self.max_history_var.set("10")
        self.auto_save_var.set("5")
        self.enable_logging_var.set(True)
        self.training_params_var.set("")
        self.use_current_data_var.set(True)
    
    def center_dialog(self):
        """Center the dialog on the screen."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}") 