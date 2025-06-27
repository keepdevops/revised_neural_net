"""
Specialized Windows Module

Contains specialized window classes for the stock prediction GUI.
This module provides popup windows, dialogs, and specialized interfaces.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import threading
import time
from datetime import datetime

class LiveTrainingWindow:
    """Window for displaying live training progress."""
    
    def __init__(self, parent, title="Live Training Progress"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Training state
        self.is_training = False
        self.training_thread = None
        self.epochs = []
        self.losses = []
        self.val_losses = []
        
        # Create GUI elements
        self._create_widgets()
        
        # Center window
        self.window.transient(parent)
        self.window.grab_set()
        self._center_window()
    
    def _create_widgets(self):
        """Create the window widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Live Training Progress", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill="x", pady=(0, 10))
        
        # Current epoch
        self.epoch_var = tk.StringVar(value="Epoch: 0")
        epoch_label = ttk.Label(progress_frame, textvariable=self.epoch_var)
        epoch_label.pack()
        
        # Current loss
        self.loss_var = tk.StringVar(value="Loss: N/A")
        loss_label = ttk.Label(progress_frame, textvariable=self.loss_var)
        loss_label.pack()
        
        # Validation loss
        self.val_loss_var = tk.StringVar(value="Validation Loss: N/A")
        val_loss_label = ttk.Label(progress_frame, textvariable=self.val_loss_var)
        val_loss_label.pack()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill="x", pady=(10, 0))
        
        # Plot frame
        plot_frame = ttk.LabelFrame(main_frame, text="Training Plot", padding="10")
        plot_frame.pack(fill="both", expand=True)
        
        # Create matplotlib figure
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            self.fig, self.ax = plt.subplots(figsize=(8, 4))
            self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Initialize plot
            self.ax.set_xlabel('Epoch')
            self.ax.set_ylabel('Loss')
            self.ax.set_title('Training Progress')
            self.ax.grid(True)
            self.canvas.draw()
            
        except ImportError:
            # Fallback if matplotlib is not available
            self.fig = None
            self.canvas = None
            fallback_label = ttk.Label(plot_frame, 
                                     text="Matplotlib not available for plotting")
            fallback_label.pack(expand=True)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=(10, 0))
        
        # Stop button
        self.stop_button = ttk.Button(control_frame, text="Stop Training", 
                                     command=self.stop_training)
        self.stop_button.pack(side="left")
        
        # Clear button
        clear_button = ttk.Button(control_frame, text="Clear Plot", 
                                 command=self.clear_plot)
        clear_button.pack(side="left", padx=(10, 0))
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side="right")
    
    def _center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def update_progress(self, epoch, loss, val_loss=None):
        """Update the training progress display."""
        self.epochs.append(epoch)
        self.losses.append(loss)
        if val_loss is not None:
            self.val_losses.append(val_loss)
        
        # Update labels
        self.epoch_var.set(f"Epoch: {epoch}")
        self.loss_var.set(f"Loss: {loss:.6f}")
        if val_loss is not None:
            self.val_loss_var.set(f"Validation Loss: {val_loss:.6f}")
        
        # Update progress bar (assuming max epochs is known)
        if hasattr(self, 'max_epochs'):
            progress = (epoch / self.max_epochs) * 100
            self.progress_var.set(progress)
        
        # Update plot
        if self.fig is not None:
            self._update_plot()
    
    def _update_plot(self):
        """Update the training plot."""
        try:
            self.ax.clear()
            self.ax.plot(self.epochs, self.losses, 'b-', label='Training Loss')
            if self.val_losses:
                self.ax.plot(self.epochs, self.val_losses, 'r-', label='Validation Loss')
            
            self.ax.set_xlabel('Epoch')
            self.ax.set_ylabel('Loss')
            self.ax.set_title('Training Progress')
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating plot: {e}")
    
    def clear_plot(self):
        """Clear the training plot."""
        self.epochs.clear()
        self.losses.clear()
        self.val_losses.clear()
        
        if self.fig is not None:
            self.ax.clear()
            self.ax.set_xlabel('Epoch')
            self.ax.set_ylabel('Loss')
            self.ax.set_title('Training Progress')
            self.ax.grid(True)
            self.canvas.draw()
    
    def stop_training(self):
        """Stop the training process."""
        self.is_training = False
        self.status_var.set("Training stopped")
        self.stop_button.config(state="disabled")
    
    def _on_close(self):
        """Handle window close event."""
        self.stop_training()
        self.window.destroy()

class SettingsDialog:
    """Dialog for application settings."""
    
    def __init__(self, parent, settings=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("500x400")
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self.settings = settings or {}
        self.result = None
        
        # Create GUI elements
        self._create_widgets()
        
        # Center window
        self.window.transient(parent)
        self.window.grab_set()
        self._center_window()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Application Settings", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Settings notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # General settings tab
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="General")
        self._create_general_settings(general_frame)
        
        # Training settings tab
        training_frame = ttk.Frame(notebook, padding="10")
        notebook.add(training_frame, text="Training")
        self._create_training_settings(training_frame)
        
        # Visualization settings tab
        viz_frame = ttk.Frame(notebook, padding="10")
        notebook.add(viz_frame, text="Visualization")
        self._create_visualization_settings(viz_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right")
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side="left")
    
    def _create_general_settings(self, parent):
        """Create general settings widgets."""
        # Max history size
        ttk.Label(parent, text="Max History Size:").grid(row=0, column=0, sticky="w", pady=5)
        self.max_history_var = tk.StringVar(value=str(self.settings.get('max_history_size', 10)))
        ttk.Entry(parent, textvariable=self.max_history_var, width=10).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Auto-save interval
        ttk.Label(parent, text="Auto-save Interval (minutes):").grid(row=1, column=0, sticky="w", pady=5)
        self.auto_save_var = tk.StringVar(value=str(self.settings.get('auto_save_interval', 5)))
        ttk.Entry(parent, textvariable=self.auto_save_var, width=10).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Enable logging
        self.enable_logging_var = tk.BooleanVar(value=self.settings.get('enable_logging', True))
        ttk.Checkbutton(parent, text="Enable Logging", variable=self.enable_logging_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
    
    def _create_training_settings(self, parent):
        """Create training settings widgets."""
        # Default epochs
        ttk.Label(parent, text="Default Epochs:").grid(row=0, column=0, sticky="w", pady=5)
        self.default_epochs_var = tk.StringVar(value=str(self.settings.get('default_epochs', 100)))
        ttk.Entry(parent, textvariable=self.default_epochs_var, width=10).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Default learning rate
        ttk.Label(parent, text="Default Learning Rate:").grid(row=1, column=0, sticky="w", pady=5)
        self.default_lr_var = tk.StringVar(value=str(self.settings.get('default_learning_rate', 0.001)))
        ttk.Entry(parent, textvariable=self.default_lr_var, width=10).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Default batch size
        ttk.Label(parent, text="Default Batch Size:").grid(row=2, column=0, sticky="w", pady=5)
        self.default_batch_var = tk.StringVar(value=str(self.settings.get('default_batch_size', 32)))
        ttk.Entry(parent, textvariable=self.default_batch_var, width=10).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Memory optimization
        self.memory_opt_var = tk.BooleanVar(value=self.settings.get('memory_optimization', False))
        ttk.Checkbutton(parent, text="Memory Optimization", variable=self.memory_opt_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
    
    def _create_visualization_settings(self, parent):
        """Create visualization settings widgets."""
        # Default plot style
        ttk.Label(parent, text="Default Plot Style:").grid(row=0, column=0, sticky="w", pady=5)
        self.plot_style_var = tk.StringVar(value=self.settings.get('default_plot_style', 'default'))
        style_combo = ttk.Combobox(parent, textvariable=self.plot_style_var, 
                                  values=['default', 'seaborn', 'ggplot', 'bmh'])
        style_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Auto-refresh plots
        self.auto_refresh_var = tk.BooleanVar(value=self.settings.get('auto_refresh_plots', True))
        ttk.Checkbutton(parent, text="Auto-refresh Plots", variable=self.auto_refresh_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # High DPI plots
        self.high_dpi_var = tk.BooleanVar(value=self.settings.get('high_dpi_plots', False))
        ttk.Checkbutton(parent, text="High DPI Plots", variable=self.high_dpi_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        self.max_history_var.set("10")
        self.auto_save_var.set("5")
        self.enable_logging_var.set(True)
        self.default_epochs_var.set("100")
        self.default_lr_var.set("0.001")
        self.default_batch_var.set("32")
        self.memory_opt_var.set(False)
        self.plot_style_var.set("default")
        self.auto_refresh_var.set(True)
        self.high_dpi_var.set(False)
    
    def _on_ok(self):
        """Handle OK button click."""
        try:
            self.result = {
                'max_history_size': int(self.max_history_var.get()),
                'auto_save_interval': int(self.auto_save_var.get()),
                'enable_logging': self.enable_logging_var.get(),
                'default_epochs': int(self.default_epochs_var.get()),
                'default_learning_rate': float(self.default_lr_var.get()),
                'default_batch_size': int(self.default_batch_var.get()),
                'memory_optimization': self.memory_opt_var.get(),
                'default_plot_style': self.plot_style_var.get(),
                'auto_refresh_plots': self.auto_refresh_var.get(),
                'high_dpi_plots': self.high_dpi_var.get()
            }
            self.window.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input values: {e}")
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.window.destroy()
    
    def _center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def show(self):
        """Show the dialog and return the result."""
        self.window.wait_window()
        return self.result

class HelpWindow:
    """Window for displaying help information."""
    
    def __init__(self, parent, title="Help"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("700x500")
        
        # Create GUI elements
        self._create_widgets()
        
        # Center window
        self.window.transient(parent)
        self._center_window()
    
    def _create_widgets(self):
        """Create the help window widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Stock Prediction GUI Help", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Help notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # Getting Started tab
        getting_started_frame = ttk.Frame(notebook, padding="10")
        notebook.add(getting_started_frame, text="Getting Started")
        self._create_getting_started_content(getting_started_frame)
        
        # Training tab
        training_frame = ttk.Frame(notebook, padding="10")
        notebook.add(training_frame, text="Training")
        self._create_training_help_content(training_frame)
        
        # Prediction tab
        prediction_frame = ttk.Frame(notebook, padding="10")
        notebook.add(prediction_frame, text="Prediction")
        self._create_prediction_help_content(prediction_frame)
        
        # Visualization tab
        viz_frame = ttk.Frame(notebook, padding="10")
        notebook.add(viz_frame, text="Visualization")
        self._create_visualization_help_content(viz_frame)
        
        # Troubleshooting tab
        troubleshooting_frame = ttk.Frame(notebook, padding="10")
        notebook.add(troubleshooting_frame, text="Troubleshooting")
        self._create_troubleshooting_content(troubleshooting_frame)
    
    def _create_getting_started_content(self, parent):
        """Create getting started help content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
Getting Started with Stock Prediction GUI

1. Data Preparation:
   - Ensure your data file is in CSV format
   - Required columns: open, high, low, close, vol (volume)
   - Additional technical indicators will be added automatically
   - Remove any rows with missing values

2. First Steps:
   - Select your data file using the "Browse" button
   - Choose an output directory for saving models
   - Configure training parameters (epochs, learning rate, etc.)
   - Click "Start Training" to begin

3. Understanding the Interface:
   - Control Panel: Configure training and prediction settings
   - Display Panel: View training results and predictions
   - Status Bar: Monitor current operations and progress

4. Model Management:
   - Trained models are saved in timestamped directories
   - Each model contains weights, plots, and configuration
   - Use the model selector to switch between different models

For more detailed information, see the other help tabs.
"""
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
    
    def _create_training_help_content(self, parent):
        """Create training help content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
Training Guide

1. Training Parameters:
   - Epochs: Number of training iterations (recommended: 100-1000)
   - Learning Rate: Step size for gradient descent (recommended: 0.001-0.01)
   - Batch Size: Number of samples per training step (recommended: 32-128)
   - Hidden Size: Number of neurons in hidden layer (recommended: 32-128)
   - Validation Split: Fraction of data for validation (recommended: 0.2)

2. Training Process:
   - Data is automatically normalized using min-max scaling
   - Technical indicators are added to improve prediction accuracy
   - Early stopping prevents overfitting
   - Training progress is displayed in real-time

3. Monitoring Training:
   - Watch the loss curves for convergence
   - Validation loss should decrease and stabilize
   - If loss increases, try reducing learning rate
   - Use early stopping to prevent overfitting

4. Model Selection:
   - Best model is automatically saved based on validation loss
   - Final model is saved after all epochs complete
   - Weights history is saved for visualization
"""
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
    
    def _create_prediction_help_content(self, parent):
        """Create prediction help content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
Prediction Guide

1. Making Predictions:
   - Select a trained model from the model list
   - Choose a data file for prediction
   - Click "Make Prediction" to generate results
   - Results are saved as CSV files

2. Data Requirements:
   - Prediction data must have the same features as training data
   - Missing features will be automatically added
   - Data is normalized using the same parameters as training

3. Understanding Results:
   - Predicted values are denormalized to original scale
   - Error metrics are calculated if actual values are available
   - Results include both predicted and actual values

4. Model Compatibility:
   - Only use models trained with compatible feature sets
   - Check feature_info.json for model requirements
   - Re-train model if data format changes significantly
"""
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
    
    def _create_visualization_help_content(self, parent):
        """Create visualization help content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
Visualization Guide

1. Training Plots:
   - Loss curves show training and validation progress
   - Actual vs Predicted plots show model accuracy
   - Error distribution plots help identify bias

2. 3D Visualizations:
   - Gradient descent visualization shows weight evolution
   - Surface plots show loss landscape
   - Wireframe plots show detailed structure
   - Contour plots show loss contours

3. Animation Features:
   - Generate MPEG animations of training process
   - Create GIF animations for presentations
   - Export plots in various formats (PNG, PDF, SVG)

4. Plot Controls:
   - Adjust viewing angles and perspectives
   - Change color schemes and plot types
   - Zoom and pan for detailed examination
   - Save plots for external use
"""
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
    
    def _create_troubleshooting_content(self, parent):
        """Create troubleshooting help content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
Troubleshooting Guide

Common Issues and Solutions:

1. Training Issues:
   - Loss not decreasing: Reduce learning rate
   - Overfitting: Increase validation split, add early stopping
   - Memory errors: Reduce batch size, enable memory optimization
   - Slow training: Reduce hidden size, use fewer epochs

2. Prediction Issues:
   - Feature mismatch: Check data format matches training data
   - All predictions same: Check normalization, retrain model
   - File not found: Verify file paths and permissions
   - Import errors: Install required packages (numpy, pandas, matplotlib)

3. Visualization Issues:
   - Plots not updating: Check auto-refresh settings
   - 3D plots slow: Reduce number of points, use performance preset
   - Animation errors: Check ffmpeg installation for MPEG generation
   - Display issues: Update matplotlib, check display drivers

4. Data Issues:
   - Missing columns: Ensure required features are present
   - NaN values: Clean data before training
   - Wrong format: Convert to CSV format
   - Large files: Use memory optimization, split data

For additional help, check the console output for error messages.
"""
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
    
    def _center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

class AboutDialog:
    """Dialog for displaying application information."""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("About Stock Prediction GUI")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Create GUI elements
        self._create_widgets()
        
        # Center window
        self.window.transient(parent)
        self.window.grab_set()
        self._center_window()
    
    def _create_widgets(self):
        """Create the about dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Stock Prediction Neural Network", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(main_frame, text="Version 2.0", 
                                 font=("Arial", 12))
        version_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """
A comprehensive GUI application for training neural networks
to predict stock prices using technical analysis indicators.

Features:
• Neural network training with customizable parameters
• Real-time training progress monitoring
• Advanced visualization and 3D plotting
• Prediction generation and analysis
• Model management and comparison
• Export capabilities for results and animations
"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        # Dependencies
        deps_text = "Dependencies: numpy, pandas, matplotlib, tkinter"
        deps_label = ttk.Label(main_frame, text=deps_text, font=("Arial", 9))
        deps_label.pack(pady=(0, 20))
        
        # Copyright
        copyright_text = "© 2024 Stock Prediction Project"
        copyright_label = ttk.Label(main_frame, text=copyright_text, font=("Arial", 9))
        copyright_label.pack(pady=(0, 20))
        
        # OK button
        ttk.Button(main_frame, text="OK", command=self.window.destroy).pack()
    
    def _center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}") 