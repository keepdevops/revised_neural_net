"""
Stock Price Prediction GUI

This module provides a graphical user interface for the stock price prediction system.
It integrates training, prediction, and visualization capabilities into a single interface.

Features:
- Train new models
- Make predictions
- View training results and plots
- Compare different model versions
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import subprocess
import shutil

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from datetime import datetime
import glob
import json
import numpy as np
import tempfile
import threading
import time
import re
from collections import OrderedDict
import concurrent.futures
import importlib.util
from PIL import Image, ImageTk
import path_utils
import script_launcher
from script_launcher import launch_training, launch_prediction, launch_3d_visualization
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import logging
from concurrent.futures import ThreadPoolExecutor
import queue
import io
from path_utils import get_ticker_from_filename
from gui.panels.control_panel import ControlPanel
from gui.panels.display_panel import DisplayPanel
from gui.theme import *

# Import the data converter
try:
    from data_converter import convert_data_file, detect_data_format, validate_and_convert_for_gui
    DATA_CONVERTER_AVAILABLE = True
except ImportError:
    DATA_CONVERTER_AVAILABLE = False
    print("⚠️  Data converter not available - manual data conversion may be required")

try:
    import stock_net
    from stock_net import StockNet, add_technical_indicators
except ImportError:
    # If stock_net is not available, we'll implement the needed functions inline
    # We will be removing the inline implementation, so this might need adjustment
    StockNet = None

class StockPredictionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Prediction Neural Network GUI")
        self.root.geometry("1400x900")
        
        # Training parameter variables
        self.learning_rate_var = tk.StringVar(value="0.001")  # Default learning rate
        self.batch_size_var = tk.StringVar(value="32")        # Default batch size

        # Set the model directory to the project root (where model_* folders are)
        self.current_model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        self.setup_main_window()
        
        # Initialize variables
        self.data_file = None
        self.output_dir = None
        self.selected_model_path = None
        self.training_process = None
        self.visualization_process = None
        
        # Training variables
        self.epochs_var = tk.StringVar(value="100")
        self.validation_split_var = tk.StringVar(value="0.2")
        
        # Feature selection variables
        self.feature_vars = {}
        self.locked_features = set()
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")  # Status bar variable
        self.feature_status_var = tk.StringVar(value="")  # Feature status variable
        self.prediction_status_var = tk.StringVar(value="No prediction data")  # Prediction status variable
        
        # Live plot status (will be initialized as a Label widget when needed)
        self.live_plot_status = None
        
        # Live plot update variables
        self.last_plot_update = 0
        self.plot_update_interval = 0.1  # Update every 100ms
        
        # Live plot variables
        self.live_plot_fig = None
        self.live_plot_epochs = []
        self.live_plot_losses = []
        self.live_plot_window_open = False
        
        # Selected prediction file
        self.selected_prediction_file = None
        
        # 3D visualization variables
        self.gd3d_fig = None
        # self.gd3d_ax = None  # Created by control panel
        # self.gd3d_canvas = None  # Created by control panel
        
        # 3D animation variables
        self.animation_running = False
        self.current_frame = 0
        self.total_frames = 0
        self.anim_speed_var = tk.DoubleVar(value=1.0)
        
        # Model directory
        # self.current_model_dir = "."  # REMOVE THIS LINE
        
        # Image cache for saved plots
        self.image_cache = {}
        self.max_cache_size = 10
        
        # Thread pool for background tasks
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        # Test script availability
        self.test_script_availability()
        
        # Load initial data
        self.refresh_models(load_plots=False)
        
        # Cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing event."""
        try:
            # Stop any running animations more thoroughly
            if hasattr(self, 'gd_anim_running'):
                self.gd_anim_running = False
                print("Stopped gradient descent animation")
            
            # Stop 3D animations
            if hasattr(self, 'anim_running'):
                self.anim_running = False
                print("Stopped 3D animation")
            
            # Cancel any pending after events to prevent invalid command errors
            if hasattr(self, 'root') and self.root.winfo_exists():
                try:
                    # Cancel tracked after IDs
                    if hasattr(self, 'gd_after_ids'):
                        for after_id in self.gd_after_ids:
                            try:
                                self.root.after_cancel(after_id)
                            except:
                                pass
                        self.gd_after_ids.clear()
                except:
                    pass
            
            # Close live training plot if open
            if hasattr(self, 'live_plot_window') and self.live_plot_window:
                try:
                    self.live_plot_window.close()
                except:
                    pass
            
            # Clean up thread pool
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=False)
                print("Thread pool cleaned up")
            
            # Destroy the root window
            if hasattr(self, 'root'):
                self.root.destroy()
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force destroy even if cleanup fails
            if hasattr(self, 'root'):
                self.root.destroy()

    def setup_main_window(self):
        """Configure the main window and creates the primary layout panes."""
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.minsize(800, 600)
        
        # Create floating right panel as a separate window
        self.create_floating_right_panel()

        # Create left pane for controls (main window)
        self.left_pane = ttk.Frame(self.root, style="TFrame")
        self.left_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize image cache for plots (optimization) - Updated to OrderedDict for LRU
        self.plot_image_cache = OrderedDict()  # LRU cache for images
        
        # Track ongoing plot loading operations
        self.plot_futures = {}  # Track ongoing plot loading operations
        
        # Initialize variables
        self.data_file = None
        self.data_file_var = tk.StringVar()  # Variable for data file entry
        self.current_model_dir = "."
        self.selected_model_path = None  # Track the currently selected model path
        self.x_features = []
        self.y_feature = ""
        self.features_locked = False
        self.locked_features = []
        self.is_training = False
        self.training_thread = None
        
        # Initialize output directory
        self.output_dir = "."  # Default to current directory
        self.output_dir_var = tk.StringVar(value=self.output_dir)
        
        # Initialize model directory and create it if it doesn't exist
        os.makedirs(self.current_model_dir, exist_ok=True)
        
        # Initialize feature variables
        self.feature_list = []  # Available features from data file
        
        # Initialize training parameters
        self.hidden_size_var = tk.StringVar(value="4")  # Default hidden layer size
        # self.learning_rate_var = tk.StringVar(value="0.001")  # Duplicate - remove from here
        # self.batch_size_var = tk.StringVar(value="32")  # Duplicate - remove from here
        
        # Gradient descent visualization parameters
        self.color_var = tk.StringVar(value="viridis")
        self.point_size_var = tk.StringVar(value="8")
        self.line_width_var = tk.StringVar(value="3")
        self.surface_alpha_var = tk.StringVar(value="0.6")
        
        # Additional 3D visualization parameters
        self.w1_range_min_var = tk.StringVar(value="-2.0")
        self.w1_range_max_var = tk.StringVar(value="2.0")
        self.w2_range_min_var = tk.StringVar(value="-2.0")
        self.w2_range_max_var = tk.StringVar(value="2.0")
        self.n_points_var = tk.StringVar(value="30")
        self.view_elev_var = tk.StringVar(value="30.0")
        self.view_azim_var = tk.StringVar(value="45.0")
        self.fps_var = tk.StringVar(value="30")
        self.w1_index_var = tk.StringVar(value="0")
        self.w2_index_var = tk.StringVar(value="0")
        self.output_width_var = tk.StringVar(value="1200")
        self.output_height_var = tk.StringVar(value="800")
        # 3D Animation variables
        self.x_rotation_var = tk.DoubleVar(value=30.0)
        self.y_rotation_var = tk.DoubleVar(value=0.0)
        self.z_rotation_var = tk.DoubleVar(value=45.0)
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.frame_pos_var = tk.DoubleVar(value=0.0)
        self.frame_rate_var = tk.IntVar(value=30)
        self.loop_mode_var = tk.StringVar(value="Forward")
        self.autoplay_var = tk.BooleanVar(value=False)
        self.gd_anim_speed = tk.DoubleVar(value=1.0)
        self.anim_progress_var = tk.DoubleVar(value=0.0)
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")  # Status bar variable
        self.feature_status_var = tk.StringVar(value="")  # Feature status variable
        self.prediction_status_var = tk.StringVar(value="No prediction data")  # Prediction status variable
        
        # Live plot status (will be initialized as a Label widget when needed)
        self.live_plot_status = None
        
        # Live plot update variables
        self.last_plot_update = 0
        self.plot_update_interval = 0.1  # Update every 100ms
        
        # Live plot variables
        self.live_plot_fig = None
        self.live_plot_epochs = []
        self.live_plot_losses = []
        self.live_plot_window_open = False
        
        # Selected prediction file
        self.selected_prediction_file = None
        
        # Test script availability on startup
        self.test_script_availability()
        
        # Create control panel
        self.create_control_panel()
        
        # Add floating panel control button
        panel_control_frame = ttk.Frame(self.root)
        panel_control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        toggle_panel_btn = ttk.Button(panel_control_frame, text="📋 Toggle Results Panel", command=self.toggle_right_panel)
        toggle_panel_btn.pack(side=tk.RIGHT)
        
        # Add status bar to show floating panel status
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        self.status_label = ttk.Label(self.status_bar, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add floating panel status indicator
        self.panel_status_var = tk.StringVar(value="Results Panel: Hidden")
        self.panel_status_label = ttk.Label(self.status_bar, textvariable=self.panel_status_var, relief=tk.SUNKEN, anchor=tk.E)
        self.panel_status_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Initialize model list
        self.refresh_models(load_plots=False)

    def create_floating_right_panel(self):
        """Creates a floating right panel as a separate window."""
        # Create the floating window
        self.right_panel_window = tk.Toplevel(self.root)
        self.right_panel_window.title("Stock Prediction - Results Panel")
        self.right_panel_window.configure(bg=BACKGROUND_COLOR)
        self.right_panel_window.minsize(600, 400)
        
        # Position the window to the right of the main window
        self.root.update_idletasks()  # Ensure main window is positioned
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get main window position and size
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        # Calculate position for floating panel
        # Try to position it to the right of main window, but ensure it fits on screen
        panel_width = 600
        panel_height = 500
        
        # Position to the right of main window with some gap
        panel_x = main_x + main_width + 20
        
        # If it would go off screen, position it to the left of main window
        if panel_x + panel_width > screen_width:
            panel_x = main_x - panel_width - 20
        
        # Ensure panel doesn't go off screen horizontally
        if panel_x < 0:
            panel_x = 0
        elif panel_x + panel_width > screen_width:
            panel_x = screen_width - panel_width
        
        # Position vertically centered with main window
        panel_y = main_y + (main_height - panel_height) // 2
        
        # Ensure panel doesn't go off screen vertically
        if panel_y < 0:
            panel_y = 0
        elif panel_y + panel_height > screen_height:
            panel_y = screen_height - panel_height
        
        # Set the geometry
        self.right_panel_window.geometry(f"{panel_width}x{panel_height}+{panel_x}+{panel_y}")
        
        # Make the floating window stay on top initially, but allow it to be moved behind
        self.right_panel_window.attributes('-topmost', True)
        
        # Create the right pane frame
        self.right_pane = ttk.Frame(self.right_panel_window, style="TFrame")
        self.right_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Handle window close event
        self.right_panel_window.protocol("WM_DELETE_WINDOW", self.on_right_panel_close)
        
        # Create display panel
        self.create_display_panel()
        
        # Update status indicator
        if hasattr(self, 'panel_status_var'):
            self.panel_status_var.set("Results Panel: Visible")
        
        print(f"✅ Floating right panel created successfully at position ({panel_x}, {panel_y})")
        print(f"   Main window: ({main_x}, {main_y}) {main_width}x{main_height}")
        print(f"   Panel window: {panel_width}x{panel_height}")

    def on_right_panel_close(self):
        """Handle closing of the floating right panel."""
        # Hide the window instead of destroying it
        self.right_panel_window.withdraw()
        if hasattr(self, 'panel_status_var'):
            self.panel_status_var.set("Results Panel: Hidden")
        print("📋 Right panel hidden (use 'Show Results Panel' to restore)")

    def show_right_panel(self):
        """Show the floating right panel."""
        if hasattr(self, 'right_panel_window'):
            self.right_panel_window.deiconify()
            self.right_panel_window.lift()
            if hasattr(self, 'panel_status_var'):
                self.panel_status_var.set("Results Panel: Visible")
            print("📋 Right panel shown")
        else:
            self.create_floating_right_panel()

    def hide_right_panel(self):
        """Hide the floating right panel."""
        if hasattr(self, 'right_panel_window'):
            self.right_panel_window.withdraw()
            if hasattr(self, 'panel_status_var'):
                self.panel_status_var.set("Results Panel: Hidden")
            print("📋 Right panel hidden")

    def toggle_right_panel(self):
        """Toggle the visibility of the floating right panel."""
        if hasattr(self, 'right_panel_window'):
            if self.right_panel_window.state() == 'withdrawn':
                self.show_right_panel()
            else:
                self.hide_right_panel()
        else:
            self.create_floating_right_panel()
            if hasattr(self, 'panel_status_var'):
                self.panel_status_var.set("Results Panel: Visible")

    def test_script_availability(self):
        """Test if all required scripts are available and log the results."""
        try:
            availability = script_launcher.launcher.test_script_availability()
            
            # Log results
            print("Script availability check:")
            for script, available in availability.items():
                status = "✅ Available" if available else "❌ Not found"
                print(f"  {script}: {status}")
            
            # Check if all scripts are available
            all_available = all(availability.values())
            if all_available:
                print("✅ All required scripts are available")
                self.status_var.set("Ready - All scripts available")
            else:
                missing_scripts = [script for script, available in availability.items() if not available]
                print(f"⚠️  Missing scripts: {missing_scripts}")
                self.status_var.set(f"Warning - Missing scripts: {', '.join(missing_scripts)}")
                
        except Exception as e:
            print(f"Error testing script availability: {e}")
            self.status_var.set("Error testing script availability")

    
    def create_control_panel(self):
        """Creates and places the control panel in the left pane."""
        self.control_panel = ControlPanel(self.left_pane, self)
        self.control_panel.frame.pack(fill=tk.BOTH, expand=True)
    
    
    def create_display_panel(self):
        """Creates and places the display panel in the right pane."""
        self.display_panel = DisplayPanel(self.right_pane, self)
        self.display_panel.frame.pack(fill=tk.BOTH, expand=True)

    
    def browse_data_file(self):
        print("🔍 browse_data_file() called")
        """Browse for data file."""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.data_file = filename
            self.data_file_var.set(filename)
            self.load_data_features()
            self.status_var.set(f"Loaded data file: {os.path.basename(filename)}")

    def browse_output_dir(self):
        print("🔍 browse_output_dir() called")
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_dir_var.set(directory)
            self.status_var.set(f"Output directory: {directory}")

    def load_data_features(self):
        """Load features from the selected data file."""
        try:
            if not self.data_file or not os.path.exists(self.data_file):
                return
            
            # Load data to get column names
            df = pd.read_csv(self.data_file)
            self.feature_list = list(df.columns)
            
            # Update feature listbox
            self.feature_listbox.delete(0, tk.END)
            for feature in self.feature_list:
                self.feature_listbox.insert(tk.END, feature)
            
            # Update target combo
            self.target_combo['values'] = self.feature_list
            if 'close' in self.feature_list:
                self.target_combo.set('close')
            elif len(self.feature_list) > 0:
                self.target_combo.set(self.feature_list[0])
            
            self.status_var.set(f"Loaded {len(self.feature_list)} features from data file")
            
        except Exception as e:
            print(f"Error loading data features: {e}")
            self.status_var.set(f"Error loading features: {str(e)}")

    def lock_features(self):
        """Lock the currently selected features."""
        try:
            selected_indices = self.feature_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select features to lock.")
                return
            
            self.locked_features = [self.feature_list[i] for i in selected_indices]
            self.features_locked = True
            self.feature_status_var.set(f"Locked {len(self.locked_features)} features")
            self.status_var.set(f"Locked features: {', '.join(self.locked_features)}")
            
        except Exception as e:
            print(f"Error locking features: {e}")
            self.status_var.set(f"Error locking features: {str(e)}")

    def unlock_features(self):
        """Unlock all features."""
        self.locked_features = []
        self.features_locked = False
        self.feature_status_var.set("Features unlocked")
        self.status_var.set("All features unlocked")

    def start_training(self):
        """Start the training process in a separate thread."""
        if self.is_training:
            messagebox.showwarning("Training in Progress", "Training is already in progress.")
            return
        
        if not self.data_file:
            # Try to find a suitable data file automatically
            auto_file = self.find_suitable_data_file()
            if auto_file:
                # Validate and convert the auto-selected file
                validated_file = self.validate_and_convert_data_file(auto_file)
                if validated_file:
                    self.data_file = validated_file
                    self.data_file_var.set(os.path.basename(validated_file))
                    self.load_data_features()  # Load features for the auto-selected file
                    messagebox.showinfo("Data File Auto-Selected", 
                                      f"Automatically selected and validated data file: {os.path.basename(validated_file)}\n\n"
                                      f"Training will proceed with this file.")
                else:
                    messagebox.showerror("Data File Error", 
                                       "No suitable data file found. Please select a data file manually.")
                    return
            else:
                messagebox.showerror("No Data File", 
                                   "Please select a data file before starting training.\n\n"
                                   "The file should have OHLCV columns (open, high, low, close, vol) "
                                   "or generic feature columns (feature_1, feature_2, etc.).")
                return
        
        # Validate the selected data file
        validated_file = self.validate_and_convert_data_file(self.data_file)
        if not validated_file:
            messagebox.showerror("Data File Error", 
                               "The selected data file is not valid for training.\n\n"
                               "Please select a file with proper OHLCV format or "
                               "generic feature columns that can be converted.")
            return
        
        # Update the data file to the validated/converted version
        if validated_file != self.data_file:
            self.data_file = validated_file
            self.data_file_var.set(os.path.basename(validated_file))
            self.load_data_features()
        
        # Check if output directory is set
        if not self.output_dir:
            messagebox.showerror("No Output Directory", "Please select an output directory.")
            return
        
        # Clear all plots and reset plot state before starting new training
        self.clear_all_plots()
        
        # Start training in a separate thread
        self.is_training = True
        self.training_thread = threading.Thread(target=self._train_model)
        self.training_thread.daemon = True
        self.training_thread.start()
        
        # Update UI
        self.train_button.config(state='disabled')
        self.status_var.set("Training in progress...")

    def start_live_training(self):
        """Start live training with error loss plotting in the Live Training Plot tab."""
        if self.is_training:
            messagebox.showwarning("Training in Progress", "Training is already in progress.")
            return
        
        if not self.data_file:
            # Try to find a suitable data file automatically
            auto_file = self.find_suitable_data_file()
            if auto_file:
                # Validate and convert the auto-selected file
                validated_file = self.validate_and_convert_data_file(auto_file)
                if validated_file:
                    self.data_file = validated_file
                    self.data_file_var.set(os.path.basename(validated_file))
                    self.load_data_features()  # Load features for the auto-selected file
                    messagebox.showinfo("Data File Auto-Selected", 
                                      f"Automatically selected and validated data file: {os.path.basename(validated_file)}\n\n"
                                      f"Live training will proceed with this file.")
                else:
                    messagebox.showerror("Data File Error", 
                                       "No suitable data file found. Please select a data file manually.")
                    return
            else:
                messagebox.showerror("No Data File", 
                                   "Please select a data file before starting live training.\n\n"
                                   "The file should have OHLCV columns (open, high, low, close, vol) "
                                   "or generic feature columns (feature_1, feature_2, etc.).")
                return
        
        # Validate the selected data file
        validated_file = self.validate_and_convert_data_file(self.data_file)
        if not validated_file:
            messagebox.showerror("Data File Error", 
                               "The selected data file is not valid for training.\n\n"
                               "Please select a file with proper OHLCV format or "
                               "generic feature columns that can be converted.")
            return
        
        # Update the data file to the validated/converted version
        if validated_file != self.data_file:
            self.data_file = validated_file
            self.data_file_var.set(os.path.basename(validated_file))
            self.load_data_features()
        
        # Check if output directory is set
        if not self.output_dir:
            messagebox.showerror("No Output Directory", "Please select an output directory.")
            return
        
        # Clear all plots and reset plot state before starting new training
        self.clear_all_plots()
        
        # Initialize live training plot data
        self.live_plot_epochs = []
        self.live_plot_losses = []
        
        # Show the right panel and switch to Live Training Plot tab
        self.show_right_panel()
        self.switch_to_tab(5)  # Switch to Live Training Plot tab (index 5)
        
        # Update live training status
        if hasattr(self, 'live_training_status'):
            self.live_training_status.config(text="Live training starting...")
        
        # Start training in a separate thread
        self.is_training = True
        self.training_thread = threading.Thread(target=self._train_model)
        self.training_thread.daemon = True
        self.training_thread.start()
        
        # Update UI
        self.live_training_button.config(state='disabled')
        self.train_button.config(state='disabled')
        self.status_var.set("Live training in progress...")
        
        messagebox.showinfo("Live Training Started", 
                          "Live training has started!\n\n"
                          "The error loss will be plotted in real-time in the 'Live Training Plot' tab.\n"
                          "You can monitor the training progress there.")

    def find_suitable_data_file(self):
        """Find a suitable data file for training."""
        # Check for sample data files first
        sample_files = [
            'sample_stock_data.csv',
            'sample_stock_data_extended.csv',
            'tsla_combined.csv'
        ]
        
        for file in sample_files:
            if os.path.exists(file):
                return file
        
        # Check for any CSV files in current directory
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            return csv_files[0]
        
        return None

    def validate_and_convert_data_file(self, file_path):
        """
        Validate a data file and convert it to OHLCV format if needed.
        
        Args:
            file_path (str): Path to the data file
            
        Returns:
            str: Path to the validated/converted file, or None if failed
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            # Read the file to check its format
            df = pd.read_csv(file_path, nrows=5)  # Read first 5 rows for analysis
            
            if DATA_CONVERTER_AVAILABLE:
                # Use the data converter to detect format
                format_info = detect_data_format(df)
                
                if format_info['status'] == 'ready':
                    # File is already in OHLCV format
                    return file_path
                
                elif format_info['status'] == 'convertible':
                    # File can be converted
                    response = messagebox.askyesno(
                        "Data Conversion Required",
                        f"Data file '{os.path.basename(file_path)}' needs to be converted to OHLCV format.\n\n"
                        f"Detected format: {format_info['format']}\n"
                        f"Message: {format_info['message']}\n\n"
                        "Would you like to convert it automatically?"
                    )
                    
                    if response:
                        # Convert the file
                        converted_file = convert_data_file(file_path)
                        if converted_file:
                            messagebox.showinfo(
                                "Conversion Successful",
                                f"Data file converted successfully!\n\n"
                                f"Original: {os.path.basename(file_path)}\n"
                                f"Converted: {os.path.basename(converted_file)}\n\n"
                                f"The converted file will be used for training."
                            )
                            return converted_file
                        else:
                            messagebox.showerror(
                                "Conversion Failed",
                                "Failed to convert the data file. Please check the file format."
                            )
                            return None
                    else:
                        # User chose not to convert
                        return None
                
                else:
                    # File is incompatible
                    messagebox.showerror(
                        "Incompatible Data Format",
                        f"Data file '{os.path.basename(file_path)}' has an incompatible format.\n\n"
                        f"Error: {format_info['message']}\n\n"
                        "Please use a file with OHLCV columns (open, high, low, close, vol) or "
                        "generic feature columns (feature_1, feature_2, etc.)."
                    )
                    return None
            
            else:
                # Data converter not available - do basic validation
                columns = list(df.columns)
                ohlcv_columns = ['open', 'high', 'low', 'close', 'vol']
                
                if all(col in columns for col in ohlcv_columns):
                    return file_path
                else:
                    messagebox.showerror(
                        "Invalid Data Format",
                        f"Data file '{os.path.basename(file_path)}' does not have the required OHLCV columns.\n\n"
                        f"Required columns: {ohlcv_columns}\n"
                        f"Found columns: {columns}\n\n"
                        "Please use a file with proper OHLCV format or install the data converter."
                    )
                    return None
                    
        except Exception as e:
            messagebox.showerror(
                "File Read Error",
                f"Error reading data file '{os.path.basename(file_path)}':\n\n{str(e)}"
            )
            return None

    def append_training_log(self, line):
        """Safely append a line to the training log text widget."""
        try:
            self.training_log_text.config(state="normal")
            self.training_log_text.insert("end", line)
            self.training_log_text.see("end")
            self.training_log_text.config(state="disabled")
        except Exception as e:
            print(f"Error appending to training log: {e}")

    def clear_training_log(self):
        """Clear the training log text widget."""
        try:
            self.training_log_text.config(state="normal")
            self.training_log_text.delete(1.0, tk.END)
            self.training_log_text.config(state="disabled")
        except Exception as e:
            print(f"Error clearing training log: {e}")

    def clear_all_plots(self):
        """Clear all plots and reset plot state before starting new training."""
        try:
            print("🧹 Clearing all plots and resetting plot state...")
            
            # 1. Close any existing live plot
            if hasattr(self, 'live_plot_window_open') and self.live_plot_window_open:
                self.close_live_plot()
            
            # 2. Clear training results plot
            if hasattr(self, 'results_ax') and self.results_ax is not None:
                self.results_ax.clear()
                self.results_ax.set_title("Training Results")
                self.results_ax.set_xlabel("Epoch")
                self.results_ax.set_ylabel("Loss")
                self.results_ax.grid(True)
                try:
                    self.results_canvas.draw_idle()
                except Exception as e:
                    print(f"Error updating results canvas: {e}")
            
            # 3. Clear plots tab
            if hasattr(self, 'plots_ax') and self.plots_ax is not None:
                self.plots_ax.clear()
                self.plots_ax.set_title("Training Plots")
                self.plots_ax.set_xlabel("Epoch")
                self.plots_ax.set_ylabel("Loss")
                self.plots_ax.grid(True)
                try:
                    self.plots_canvas.draw_idle()
                except Exception as e:
                    print(f"Error updating plots canvas: {e}")
            
            # 4. Clear 3D gradient descent plot
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                self.gd3d_ax.clear()
                self.gd3d_ax.set_title("3D Gradient Descent")
                self.gd3d_ax.set_xlabel("Weight 1")
                self.gd3d_ax.set_ylabel("Weight 2")
                self.gd3d_ax.set_zlabel("Loss")
                try:
                    self.gd3d_canvas.draw_idle()
                except Exception as e:
                    print(f"Error updating 3D canvas: {e}")
            
            # 5. Clear prediction plots
            if hasattr(self, 'pred_ax') and self.pred_ax is not None:
                self.pred_ax.clear()
                self.pred_ax.set_title("Prediction Results")
               # self.pred_ax.set_xlabel(self.get_ticker_from_filename())
                self.pred_ax.set_ylabel("Value")
                self.pred_ax.grid(True)
                try:
                    self.pred_canvas.draw_idle()
                except Exception as e:
                    print(f"Error updating prediction canvas: {e}")
            
            # 6. Clear saved plots
            if hasattr(self, 'saved_plots_inner_frame'):
                for widget in self.saved_plots_inner_frame.winfo_children():
                    widget.destroy()
                if hasattr(self, 'saved_plots_images'):
                    self.saved_plots_images.clear()
            
            # 7. Clear training log
            self.clear_training_log()
            
            # 8. Reset selected model
            self.selected_model_path = None
            
            # 9. Update status
            self.status_var.set("All plots cleared and reset")
            print("✅ All plots cleared and reset successfully")
            
        except Exception as e:
            print(f"Error clearing plots: {e}")
            self.status_var.set(f"Error clearing plots: {str(e)}")

    def clear_cache_only(self):
        """Clear all caches without reinitializing plots."""
        try:
            print("🧹 Clearing all caches...")
            
            # 1. Clear image caches
            if hasattr(self, 'image_cache'):
                self.image_cache.clear()
                print("✅ Image cache cleared")
            
            if hasattr(self, 'plot_image_cache'):
                self.plot_image_cache.clear()
                print("✅ Plot image cache cleared")
            
            # 2. Clear saved plots images
            if hasattr(self, 'saved_plots_images'):
                self.saved_plots_images.clear()
                print("✅ Saved plots images cleared")
            
            # 3. Clear any pending plot futures
            if hasattr(self, 'plot_futures'):
                for future in self.plot_futures.values():
                    if not future.done():
                        future.cancel()
                self.plot_futures.clear()
                print("✅ Plot futures cleared")
            
            # 4. Update status
            self.status_var.set("Cache cleared successfully")
            print("✅ Cache cleared successfully")
            
        except Exception as e:
            print(f"Error clearing cache: {e}")
            self.status_var.set(f"Error clearing cache: {str(e)}")

    def clear_cache_and_reinitialize(self):
        """Clear all caches and reinitialize all plots."""
        try:
            print("🧹 Clearing all caches and reinitializing plots...")
            
            # 1. Clear image caches
            if hasattr(self, 'image_cache'):
                self.image_cache.clear()
                print("✅ Image cache cleared")
            
            if hasattr(self, 'plot_image_cache'):
                self.plot_image_cache.clear()
                print("✅ Plot image cache cleared")
            
            # 2. Clear saved plots images
            if hasattr(self, 'saved_plots_images'):
                self.saved_plots_images.clear()
                print("✅ Saved plots images cleared")
            
            # 3. Clear any pending plot futures
            if hasattr(self, 'plot_futures'):
                for future in self.plot_futures.values():
                    if not future.done():
                        future.cancel()
                self.plot_futures.clear()
                print("✅ Plot futures cleared")
            
            # 4. Clear all plots
            self.clear_all_plots()
            
            # 5. Reinitialize all plot canvases
            self._reinitialize_plot_canvases()
            
            # 6. Refresh models to reload data
            self.refresh_models()
            
            # 7. Update status
            self.status_var.set("Cache cleared and plots reinitialized")
            print("✅ Cache cleared and plots reinitialized successfully")
            
        except Exception as e:
            print(f"Error clearing cache and reinitializing: {e}")
            self.status_var.set(f"Error clearing cache: {str(e)}")

    def _reinitialize_plot_canvases(self):
        """Reinitialize all plot canvases with fresh matplotlib figures."""
        try:
            print("🔄 Reinitializing plot canvases...")
            
            self._reinitialize_single_canvas('train_results_frame', 'results_ax', 'results_canvas', "Training Results", "Epoch", "Loss")
            self._reinitialize_single_canvas('plots_frame', 'plots_ax', 'plots_canvas', "Training Plots", "Epoch", "Loss")
            self._reinitialize_single_canvas('gd3d_frame', 'gd3d_ax', 'gd3d_canvas', "3D Gradient Descent", "Weight 1", "Weight 2", z_label="Loss", is_3d=True)
            self._reinitialize_single_canvas('pred_results_frame', 'pred_ax', 'pred_canvas', "Prediction Results", self.get_ticker_from_filename(), "Value", placeholder_text='Select a model and data file to view predictions')

            print("✅ All plot canvases reinitialized successfully")
            
        except Exception as e:
            print(f"Error reinitializing plot canvases: {e}")
            self.status_var.set(f"Error reinitializing plots: {str(e)}")

    def _reinitialize_single_canvas(self, frame_attr, ax_attr, canvas_attr, title, x_label, y_label, z_label=None, is_3d=False, placeholder_text='Training in progress...'):
        """Helper to reinitialize a single plot canvas."""
        if hasattr(self, frame_attr):
            frame = getattr(self, frame_attr)
            # Clear existing canvas
            for widget in frame.winfo_children():
                if isinstance(widget, FigureCanvasTkAgg):
                    widget.get_tk_widget().destroy()
            
            # Create new figure and canvas
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d' if is_3d else None)
            setattr(self, ax_attr, ax)
            
            canvas = FigureCanvasTkAgg(fig, frame)
            setattr(self, canvas_attr, canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Add toolbar
            toolbar = packMatplotlibToolbar(canvas, frame)
            toolbar.pack(fill="x")
            
            # Set initial plot
            ax.set_title(title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            if is_3d and z_label:
                ax.set_zlabel(z_label)
            ax.grid(True)
            if is_3d:
                ax.text2D(0.5, 0.5, placeholder_text, ha='center', va='center', transform=ax.transAxes, fontsize=12)
            else:
                ax.text(0.5, 0.5, placeholder_text, ha='center', va='center', transform=ax.transAxes, fontsize=12)

    def _train_model(self):
        """Train the model (runs in separate thread)."""
        try:
            # Get training parameters
            hidden_size = int(self.hidden_size_var.get())
            learning_rate = float(self.learning_rate_var.get())
            batch_size = int(self.batch_size_var.get())
            
            # Get features
            if self.features_locked:
                x_features = self.locked_features
            else:
                selected_indices = self.feature_listbox.curselection()
                if not selected_indices:
                    x_features = self.feature_list[:5]  # Default to first 5 features
                else:
                    x_features = [self.feature_list[i] for i in selected_indices]
            
            y_feature = self.target_combo.get()
            
            # Validate data file exists and has required columns
            if not os.path.exists(self.data_file):
                raise Exception(f"Data file not found: {self.data_file}")
            
            process = launch_training(self.data_file, x_features, y_feature, hidden_size, learning_rate, batch_size)
            
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    # Update GUI with the line
                    self.root.after(0, lambda l=line: self.append_training_log(l))
                    
                    # Parse line for loss information and update live plot
                    self.root.after(0, lambda l=line: self.parse_training_output_for_loss(l))
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code != 0:
                error_msg = f"Training failed with return code {return_code}"
                self.root.after(0, lambda: self.append_training_log(f"\n{error_msg}\n"))
                
                # Provide more specific error information
                if return_code == 1:
                    error_msg += "\n\nCommon causes:\n"
                    error_msg += "1. Data file missing required columns (open, high, low, close, vol)\n"
                    error_msg += "2. Data file is empty or corrupted\n"
                    error_msg += "3. Invalid feature names specified\n"
                    error_msg += "4. Insufficient data for training\n\n"
                    error_msg += "Please check your data file and try again."
                
                raise Exception(error_msg)
            
            # Training completed successfully
            self.root.after(0, lambda: self.append_training_log("\nTraining completed successfully!\n"))
            self.root.after(0, self._training_completed_success)
            
        except Exception as e:
            print(f"Error in training: {e}")
            # Fix lambda scoping issue by capturing the exception variable
            error_msg = str(e)
            self.root.after(0, lambda: self.append_training_log(f"\nError: {error_msg}\n"))
            self.root.after(0, lambda: self._training_completed_error(error_msg))

    def _training_completed_success(self):
        """Handle successful training completion."""
        self.is_training = False
        self.train_button.config(state=tk.NORMAL)
        self.status_var.set("Training completed successfully!")
        self.refresh_models()
        # Display model info and training plots after training
        self._load_model_info()
        self.display_training_plots()
        # Close live plot if it's open
        if self.live_plot_window_open:
            self.close_live_plot()
        messagebox.showinfo("Success", "Model training completed successfully!")

    def _training_completed_error(self, error_msg):
        """Handle training completion with error."""
        self.is_training = False
        self.train_button.config(state=tk.NORMAL)
        self.status_var.set(f"Training failed: {error_msg}")
        # Close live plot if it's open
        if self.live_plot_window_open:
            self.close_live_plot()
        messagebox.showerror("Training Error", f"Training failed: {error_msg}")

    def make_prediction(self):
        """Make a prediction using the selected model."""
        if not self.selected_model_path:
            messagebox.showerror("No Model", "Please select a model first.")
            return
        
        if not self.data_file:
            messagebox.showerror("No Data", "Please select a data file for prediction.")
            return
        
        try:
            self.status_var.set("Making prediction...")
            
            # Load feature info from the model
            feature_info_path = os.path.join(self.selected_model_path, 'feature_info.json')
            if not os.path.exists(feature_info_path):
                messagebox.showerror("Model Error", "No feature_info.json found in model directory.")
                return
            
            with open(feature_info_path, 'r') as f:
                feature_info = json.load(f)
            
            result = launch_prediction(self.data_file, self.selected_model_path, feature_info['x_features'], feature_info['y_feature'])
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                raise Exception(f"Prediction failed: {error_msg}")
            
            self.status_var.set("Prediction completed successfully!")
            messagebox.showinfo("Success", "Prediction completed successfully!")
            
            # Automatically update the Prediction Results tab
            self.update_prediction_results()
            
            # Refresh prediction files list
            self.refresh_prediction_files()
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            self.status_var.set(f"Prediction failed: {str(e)}")
            messagebox.showerror("Prediction Error", f"Prediction failed: {str(e)}")

    def create_3d_visualization(self):
        """Create 3D gradient descent visualization."""
        print(f"🎬 create_3d_visualization() called")
        print(f"📁 Current selected_model_path: {self.selected_model_path}")
        
        if not self.selected_model_path:
            print("❌ No model selected")
            messagebox.showerror("No Model", "Please select a model first.")
            return
        
        print(f"✅ Model selected: {self.selected_model_path}")
        
        # Check if plots directory exists
        plots_dir = os.path.join(self.selected_model_path, 'plots')
        print(f"📂 Plots directory: {plots_dir}")
        if os.path.exists(plots_dir):
            print(f"✅ Plots directory exists")
            # List existing files
            existing_files = os.listdir(plots_dir)
            print(f"📋 Existing files in plots directory: {existing_files}")
        else:
            print(f"⚠️  Plots directory does not exist yet")
        
        try:
            self.status_var.set("Creating 3D visualization...")
            print(f"🔄 Starting 3D visualization process...")
            
            # Start 3D visualization in a separate thread
            self.visualization_thread = threading.Thread(target=self._create_3d_visualization_thread)
            self.visualization_thread.daemon = True
            self.visualization_thread.start()
            print(f"✅ 3D visualization thread started")
            
        except Exception as e:
            print(f"❌ Error starting 3D visualization: {e}")
            self.status_var.set(f"Error starting 3D visualization: {str(e)}")
            messagebox.showerror("3D Visualization Error", f"Error starting 3D visualization: {str(e)}")

    def _create_3d_visualization_thread(self):
        """Create 3D gradient descent visualization (runs in separate thread)."""
        try:
            print(f"🎬 _create_3d_visualization_thread() started")
            print(f"📁 Model path: {self.selected_model_path}")
            
            # Get visualization parameters
            params = {
                'color': self.color_var.get(),
                'point_size': int(self.point_size_var.get()),
                'line_width': int(self.line_width_var.get()),
                'surface_alpha': float(self.surface_alpha_var.get()),
                'w1_range_min': float(self.w1_range_min_var.get()),
                'w1_range_max': float(self.w1_range_max_var.get()),
                'w2_range_min': float(self.w2_range_min_var.get()),
                'w2_range_max': float(self.w2_range_max_var.get()),
                'n_points': int(self.n_points_var.get()),
                'view_elev': float(self.view_elev_var.get()),
                'view_azim': float(self.view_azim_var.get()),
                'fps': int(self.fps_var.get()),
                'w1_index': int(self.w1_index_var.get()),
                'w2_index': int(self.w2_index_var.get()),
                'output_width': int(self.output_width_var.get()),
                'output_height': int(self.output_height_var.get())
            }
            
            print(f"📋 3D visualization parameters: {params}")
            
            # Check if gradient_descent_3d.py exists
            script_path = "gradient_descent_3d.py"
            if os.path.exists(script_path):
                print(f"✅ Found gradient_descent_3d.py: {script_path}")
            else:
                print(f"❌ gradient_descent_3d.py not found at: {script_path}")
                raise Exception(f"gradient_descent_3d.py not found at {script_path}")
            
            result = launch_3d_visualization(self.selected_model_path, params)
            
            print(f"🎬 3D visualization script completed")
            print(f"📊 Return code: {result.returncode}")
            if result.stdout:
                print(f"📤 stdout: {result.stdout}")
            if result.stderr:
                print(f"📥 stderr: {result.stderr}")
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                print(f"❌ 3D visualization failed with return code {result.returncode}")
                raise Exception(f"3D visualization failed: {error_msg}")
            
            # Check if new files were created
            plots_dir = os.path.join(self.selected_model_path, 'plots')
            if os.path.exists(plots_dir):
                new_files = os.listdir(plots_dir)
                print(f"📋 Files in plots directory after visualization: {new_files}")
                
                # Look for animation files
                animation_files = []
                for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
                    animation_files.extend(glob.glob(os.path.join(plots_dir, ext)))
                print(f"🎬 Animation files found after visualization: {[os.path.basename(f) for f in animation_files]}")
            
            print(f"✅ 3D visualization completed successfully")
            self.root.after(0, self._3d_visualization_completed_success)
            
        except Exception as e:
            print(f"❌ Error creating 3D visualization: {e}")
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            self.root.after(0, lambda: self._3d_visualization_completed_error(error_msg))

    def _3d_visualization_completed_success(self):
        """Handle successful 3D visualization completion."""
        self.status_var.set("3D visualization created successfully!")
        self.refresh_models()  # Refresh to show new plots
        self.refresh_mpeg_files()  # Refresh animation files list
        messagebox.showinfo("Success", "3D visualization created successfully!")

    def _3d_visualization_completed_error(self, error_msg):
        """Handle 3D visualization completion with error."""
        self.status_var.set(f"3D visualization failed: {error_msg}")
        messagebox.showerror("3D Visualization Error", f"3D visualization failed: {error_msg}")

    def _load_model_info(self):
        """Load information about the selected model."""
        try:
            if not self.selected_model_path:
                return
            
            # Load model configuration if available
            config_file = os.path.join(self.selected_model_path, 'model_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                print(f"Model config: {config}")
            
            # Load training losses if available
            loss_file = os.path.join(self.selected_model_path, 'training_losses.csv')
            if os.path.exists(loss_file):
                losses = np.loadtxt(loss_file, delimiter=',')
                print(f"Training losses loaded: {len(losses)} epochs")
            
            # Load normalization parameters
            self.X_min = np.loadtxt(os.path.join(self.selected_model_path, 'scaler_mean.csv'), delimiter=',')
            self.X_max = np.loadtxt(os.path.join(self.selected_model_path, 'scaler_std.csv'), delimiter=',') + self.X_min
            
        except Exception as e:
            print(f"Error loading model info: {e}")

    def display_training_plots(self):
        """Display training plots for the selected model."""
        try:
            if not self.selected_model_path:
                return
            
            # Load training losses
            loss_file = os.path.join(self.selected_model_path, 'training_losses.csv')
            if os.path.exists(loss_file):
                losses = np.loadtxt(loss_file, delimiter=',')
                if losses.ndim > 1:
                    train_losses = losses[:, 0]
                    val_losses = losses[:, 1] if losses.shape[1] > 1 else None
                else:
                    train_losses = losses
                    val_losses = None
                
                # Update plots
                self.update_training_results(train_losses)
                self.update_plots_tab(train_losses, val_losses)
                
            self.load_saved_plots()
            
        except Exception as e:
            print(f"Error displaying training plots: {e}")

    def load_saved_plots(self):
        """Load and display PNG plots from the selected model's plots directory."""
        try:
            # Clear existing images
            for widget in self.saved_plots_inner_frame.winfo_children():
                widget.destroy()
            
            if not self.selected_model_path:
                self.saved_plots_placeholder = ttk.Label(self.saved_plots_inner_frame, 
                                                        text="Select a model to view saved plots", 
                                                        foreground=TEXT_COLOR, background=FRAME_COLOR)
                self.saved_plots_placeholder.pack(pady=20)
                return
            
            plots_dir = os.path.join(self.selected_model_path, 'plots')
            if not os.path.exists(plots_dir):
                self.saved_plots_placeholder = ttk.Label(self.saved_plots_inner_frame, 
                                                        text="No plots directory found", 
                                                        foreground=TEXT_COLOR, background=FRAME_COLOR)
                self.saved_plots_placeholder.pack(pady=20)
                self.status_var.set("No plots directory found")
                return
            
            plot_files = sorted(glob.glob(os.path.join(plots_dir, '*.png')))
            if not plot_files:
                self.saved_plots_placeholder = ttk.Label(self.saved_plots_inner_frame, 
                                                        text="No PNG plots found in model directory", 
                                                        foreground=TEXT_COLOR, background=FRAME_COLOR)
                self.saved_plots_placeholder.pack(pady=20)
                self.status_var.set("No PNG plots found")
                return
            
            # Limit to 10 plots for better performance
            plot_files = plot_files[:10]  # Limit to 10 plots
            total_plots = len(glob.glob(os.path.join(plots_dir, '*.png')))
            show_limit_message = len(plot_files) < total_plots
            
            # Load and display each PNG
            self.saved_plots_images = []  # Keep references to avoid garbage collection
            max_width = 400  # Smaller images for faster loading
            for i, plot_file in enumerate(plot_files):
                # Load image
                img = Image.open(plot_file)
                # Resize image to fit
                img_width, img_height = img.size
                scale = min(max_width / img_width, 1.0)  # Scale down if too wide
                new_size = (int(img_width * scale), int(img_height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.saved_plots_images.append(photo)
                
                # Create label with image and filename using pack
                frame = ttk.Frame(self.saved_plots_inner_frame)
                frame.pack(pady=5, padx=10, fill="x")
                
                ttk.Label(frame, text=os.path.basename(plot_file), 
                          foreground=TEXT_COLOR, background=FRAME_COLOR).pack(anchor="w")
                ttk.Label(frame, image=photo).pack(anchor="w")
            
            # Show limit message if there are more plots available
            if show_limit_message:
                limit_label = ttk.Label(self.saved_plots_inner_frame, 
                                       text=f"Showing first 10 plots (more available - {total_plots} total)", 
                                       foreground=TEXT_COLOR, background=FRAME_COLOR)
                limit_label.pack(pady=10)
            
            self.status_var.set(f"Loaded {len(plot_files)} plot(s) from {plots_dir}")
            print(f"Loaded {len(plot_files)} plot(s): {plot_files}")
            
            # Update scroll region
            self.saved_plots_canvas.configure(scrollregion=self.saved_plots_canvas.bbox("all"))
            
        except Exception as e:
            self.saved_plots_placeholder = ttk.Label(self.saved_plots_inner_frame, 
                                                    text=f"Error loading plots: {str(e)}", 
                                                    foreground="red", background=FRAME_COLOR)
            self.saved_plots_placeholder.pack(pady=20)
            self.status_var.set(f"Error loading plots: {str(e)}")
            print(f"Error loading plots: {e}")

    def create_3d_gradient_descent_visualization(self, model_dir_or_losses):
        """Create 3D visualization of gradient descent training path."""
        try:
            # Check if model_dir_or_losses is a directory path or training losses
            if isinstance(model_dir_or_losses, str) and os.path.isdir(model_dir_or_losses):
                model_dir = model_dir_or_losses
                # Load training losses from file
                loss_file = os.path.join(model_dir, 'training_losses.csv')
                if os.path.exists(loss_file):
                    train_losses = np.loadtxt(loss_file, delimiter=',')
                else:
                    print(f"Training losses file not found: {loss_file}")
                    return
            else:
                # Assume it's training losses array
                train_losses = model_dir_or_losses
                model_dir = self.selected_model_path
            
            if not model_dir:
                print("No model directory available for 3D visualization")
                return
            
            # Load weight history files
            weights_files = sorted(glob.glob(os.path.join(model_dir, 'weights_history_*.csv')))
            if weights_files:
                weights = [np.loadtxt(f, delimiter=',') for f in weights_files]
                w1 = [w[0] for w in weights]  # Example: first weight
                w2 = [w[1] for w in weights]  # Example: second weight
                z = train_losses[:len(w1)]    # Align with losses
                
                # Clear the 3D plot
                self.gd3d_ax.clear()
                
                # Plot the training path
                self.gd3d_ax.plot(w1, w2, z, 'r-', linewidth=3, label='Training Path')
                
                # Add scatter points for key positions
                self.gd3d_ax.scatter(w1[0], w2[0], z[0], c='green', s=100, label='Start', marker='o')
                self.gd3d_ax.scatter(w1[-1], w2[-1], z[-1], c='red', s=100, label='End', marker='s')
                
                # Set labels and title
                self.gd3d_ax.set_xlabel('Weight 1')
                self.gd3d_ax.set_ylabel('Weight 2')
                self.gd3d_ax.set_zlabel('Training Loss')
                self.gd3d_ax.set_title('3D Gradient Descent Training Path')
                
                # Add legend
                self.gd3d_ax.legend()
                
                # Safe canvas update
                try:
                    self.gd3d_canvas.draw_idle()
                except Exception as canvas_error:
                    print(f"Canvas update error in 3D gradient descent creation: {canvas_error}")
                
                print(f"Created 3D gradient descent visualization with {len(weights)} weight points")
            else:
                print(f"No weight history files found in {model_dir}")
                
        except Exception as e:
            print(f"Error creating 3D gradient descent visualization: {e}")
            import traceback
            traceback.print_exc()

   
    def on_prediction_file_select(self, event):
        """Handle prediction file selection."""
        try:
            selection = self.prediction_files_listbox.curselection()
            if selection:
                selected_file = self.prediction_files_listbox.get(selection[0])
                self.selected_prediction_file = selected_file
                print(f"Selected prediction file: {selected_file}")
                self.status_var.set(f"Selected prediction file: {os.path.basename(selected_file)}")
        except Exception as e:
            print(f"Error in prediction file selection: {e}")
            self.status_var.set(f"Error selecting prediction file: {str(e)}")

    def refresh_prediction_files(self):
        """Refresh the list of prediction files for the selected model."""
        try:
            self.prediction_files_listbox.delete(0, tk.END)
            
            if not self.selected_model_path:
                self.status_var.set("No model selected")
                return
            
            # Look for prediction files in the model directory
            prediction_files = []
            model_dir = self.selected_model_path
            
            # Check for common prediction file patterns
            for file in os.listdir(model_dir):
                if file.endswith('.csv') and any(pattern in file.lower() for pattern in ['prediction', 'pred', 'result', 'output']):
                    prediction_files.append(file)
            
            # Also check for prediction files in subdirectories
            for subdir in ['predictions', 'results', 'output']:
                subdir_path = os.path.join(model_dir, subdir)
                if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
                    for file in os.listdir(subdir_path):
                        if file.endswith('.csv'):
                            prediction_files.append(os.path.join(subdir, file))
            
            # Sort files by modification time (newest first)
            prediction_files.sort(key=lambda x: os.path.getmtime(os.path.join(model_dir, x)), reverse=True)
            
            # Add files to listbox
            for file in prediction_files:
                self.prediction_files_listbox.insert(tk.END, file)
            
            if prediction_files:
                self.status_var.set(f"Found {len(prediction_files)} prediction file(s)")
            else:
                # Add helpful message to listbox when no files found
                self.prediction_files_listbox.insert(tk.END, "No prediction files found")
                self.prediction_files_listbox.insert(tk.END, "Use 'Make Prediction' button to create predictions")
                self.prediction_files_listbox.insert(tk.END, "or run predict.py manually")
                self.status_var.set("No prediction files found - use 'Make Prediction' to create them")
                
        except Exception as e:
            print(f"Error refreshing prediction files: {e}")
            self.status_var.set(f"Error refreshing prediction files: {str(e)}")

    def view_prediction_results(self):
        """View the selected prediction file results."""
        try:
            selection = self.prediction_files_listbox.curselection()
            if not selection:
                self.status_var.set("No prediction file selected")
                return
            
            selected_file = self.prediction_files_listbox.get(selection[0])
            
            if not self.selected_model_path:
                self.status_var.set("No model selected")
                return
            
            # Construct full path to prediction file
            if os.path.dirname(selected_file):
                # File is in a subdirectory
                pred_file_path = os.path.join(self.selected_model_path, selected_file)
            else:
                # File is directly in model directory
                pred_file_path = os.path.join(self.selected_model_path, selected_file)
            
            if not os.path.exists(pred_file_path):
                self.status_var.set(f"Prediction file not found: {selected_file}")
                return
            
            # Load and display prediction results
            self.load_prediction_file(pred_file_path)
            
            # Switch to Prediction Results tab
            self.switch_to_tab(1)  # Prediction Results tab
            
            self.status_var.set(f"Loaded prediction results: {os.path.basename(selected_file)}")
            
        except Exception as e:
            print(f"Error viewing prediction results: {e}")
            self.status_var.set(f"Error viewing prediction results: {str(e)}")

    def load_prediction_file(self, file_path):
        """Load prediction file and update the Prediction Results tab."""
        try:
            import pandas as pd
            
            # Load the prediction file
            df = pd.read_csv(file_path)
            
            # Update prediction results display
            self.update_prediction_results_with_data(df, file_path)
            
        except Exception as e:
            print(f"Error loading prediction file: {e}")
            self.status_var.set(f"Error loading prediction file: {str(e)}")

    def update_prediction_results_with_data(self, df, file_path):
        """Update the Prediction Results tab with loaded prediction data."""
        try:
            # Clear the existing plot instead of destroying the canvas
            if hasattr(self, 'pred_ax') and self.pred_ax:
                self.pred_ax.clear()
            else:
                # If no existing axes, create a new figure
                fig, ax = plt.subplots(figsize=(10, 6))
                self.pred_ax = ax
                # Create canvas if it doesn't exist
                if not hasattr(self, 'pred_canvas') or not self.pred_canvas:
                    # Find the prediction results frame
                    for widget in self.root.winfo_children():
                        if hasattr(widget, 'winfo_children'):
                            for child in widget.winfo_children():
                                if hasattr(child, 'winfo_children'):
                                    for grandchild in child.winfo_children():
                                        if isinstance(grandchild, ttk.Notebook):
                                            # This is the display notebook
                                            for tab_id in range(grandchild.index('end')):
                                                tab = grandchild.select()
                                                if 'prediction' in grandchild.tab(tab_id, 'text').lower():
                                                    # Found prediction results tab
                                                    for tab_child in grandchild.winfo_children():
                                                        if hasattr(tab_child, 'winfo_children'):
                                                            for frame in tab_child.winfo_children():
                                                                if isinstance(frame, ttk.Frame):
                                                                    self.pred_canvas = FigureCanvasTkAgg(fig, frame)
                                                                    self.pred_canvas.draw()
                                                                    self.pred_canvas.get_tk_widget().pack(fill="both", expand=True)
                                                                    break
                                                    break
                                            break
                                    break
                        break
                return
            
            # Get ticker name for x-axis label
            ticker = self.get_ticker_from_filename()
            
            # Plot prediction results based on data structure
            if 'actual' in df.columns and 'predicted' in df.columns:
                # Create single combined plot with both actual and predicted
                x_axis = range(len(df))
                
                # Plot both lines on the same axis
                self.pred_ax.plot(x_axis, df['actual'], label='Actual', color='blue', alpha=0.7, linewidth=2)
                self.pred_ax.plot(x_axis, df['predicted'], label='Predicted', color='red', alpha=0.7, linewidth=2)
                
                # Calculate and display correlation
                correlation = np.corrcoef(df['actual'], df['predicted'])[0, 1]
                self.pred_ax.text(0.02, 0.98, f'Correlation: {correlation:.4f}', 
                                transform=self.pred_ax.transAxes, va='top', fontsize=10,
                                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
                
                # Calculate error metrics
                mae = np.mean(np.abs(df['actual'] - df['predicted']))
                mse = np.mean((df['actual'] - df['predicted']) ** 2)
                rmse = np.sqrt(mse)
                
                title = f"Prediction Results - MAE: {mae:.4f}, RMSE: {rmse:.4f}"
                
            elif 'prediction' in df.columns:
                # Plot predictions only
                x_axis = range(len(df))
                self.pred_ax.plot(x_axis, df['prediction'], label='Prediction', color='green', linewidth=2)
                title = 'Predictions'
                
            else:
                # Plot first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    x_axis = range(len(df))
                    self.pred_ax.plot(x_axis, df[numeric_cols[0]], label=numeric_cols[0], color='purple', linewidth=2)
                    title = f'Prediction Results: {numeric_cols[0]}'
                else:
                    # No numeric columns, show data info
                    self.pred_ax.text(0.5, 0.5, f'No numeric data to plot\nFile: {os.path.basename(file_path)}\nShape: {df.shape}', 
                                   transform=self.pred_ax.transAxes, ha='center', va='center', fontsize=12)
                    self.pred_ax.set_title('Prediction File Info')
                    self.pred_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        if hasattr(self, 'pred_canvas') and self.pred_canvas:
                            self.pred_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error: {canvas_error}")
                    return
            
            # Set plot properties with ticker name instead of "Sample"
            self.pred_ax.set_title(title)
            self.pred_ax.set_xlabel(ticker)
            self.pred_ax.set_ylabel("Value")
            self.pred_ax.legend()
            self.pred_ax.grid(True, alpha=0.3)
            
            # Safe canvas update with error handling
            try:
                # Use draw_idle() instead of draw() to avoid recursion
                if hasattr(self, 'pred_canvas') and self.pred_canvas:
                    self.pred_canvas.draw_idle()
                    # Force a small delay to allow the canvas to update
                    self.root.after(100, lambda: None)
            except Exception as canvas_error:
                print(f"Canvas update error: {canvas_error}")
                # Try alternative update method
                try:
                    if hasattr(self, 'pred_canvas') and self.pred_canvas:
                        self.pred_canvas.flush_events()
                except:
                    pass
            
            # Update status
            self.prediction_status_var.set(f"Loaded: {os.path.basename(file_path)} | Shape: {df.shape}")
            
            # Also update the status label
            if hasattr(self, 'pred_status_label'):
                self.pred_status_label.config(text=f"Loaded: {os.path.basename(file_path)} | Shape: {df.shape}")
            
        except Exception as e:
            print(f"Error updating prediction results with data: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message in the plot
            try:
                if hasattr(self, 'pred_ax') and self.pred_ax:
                    self.pred_ax.clear()
                    self.pred_ax.text(0.5, 0.5, f'Error loading prediction data:\n{str(e)}', 
                                    ha='center', va='center', transform=self.pred_ax.transAxes,
                                    fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                    self.pred_ax.set_title("Prediction Results - Error")
                    self.pred_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        if hasattr(self, 'pred_canvas') and self.pred_canvas:
                            self.pred_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error: {canvas_error}")
            except Exception as plot_error:
                print(f"Error creating error plot: {plot_error}")
            
            self.prediction_status_var.set(f"Error displaying prediction data: {str(e)}")
            
            # Also update the status label
            if hasattr(self, 'pred_status_label'):
                self.pred_status_label.config(text=f"Error displaying prediction data: {str(e)}")

    def update_prediction_results(self):
        """Update the Prediction Results tab with prediction data and statistics."""
        try:
            if not self.selected_model_path or not self.data_file:
                # Show placeholder if no model or data selected
                if hasattr(self, 'pred_ax') and self.pred_ax:
                    self.pred_ax.clear()
                    self.pred_ax.text(0.5, 0.5, 'Select a model and data file to view predictions', 
                                    ha='center', va='center', transform=self.pred_ax.transAxes,
                                    fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                    self.pred_ax.set_title("Prediction Results")
                    self.pred_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        if hasattr(self, 'pred_canvas') and self.pred_canvas:
                            self.pred_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error: {canvas_error}")
                
                # Update status label
                if not self.selected_model_path:
                    self.prediction_status_var.set("No model selected")
                elif not self.data_file:
                    self.prediction_status_var.set("No data file selected")
                return
            
            # Look for prediction files in the model directory
            pred_files = glob.glob(os.path.join(self.selected_model_path, 'predictions_*.csv'))
            
            # Also look for other possible prediction file patterns
            all_csv_files = glob.glob(os.path.join(self.selected_model_path, '*.csv'))
            
            # Check if model directory exists and list its contents
            if os.path.exists(self.selected_model_path):
                model_contents = os.listdir(self.selected_model_path)
            
            if not pred_files:
                # Show placeholder if no prediction files found
                if hasattr(self, 'pred_ax') and self.pred_ax:
                    self.pred_ax.clear()
                    self.pred_ax.text(0.5, 0.5, 'No prediction files found.\nRun prediction to generate results.', 
                                    ha='center', va='center', transform=self.pred_ax.transAxes,
                                    fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                    self.pred_ax.set_title("Prediction Results")
                    self.pred_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        if hasattr(self, 'pred_canvas') and self.pred_canvas:
                            self.pred_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error: {canvas_error}")
                
                # Update status label
                self.prediction_status_var.set("No prediction files found - run prediction first")
                return
            
            # Use the latest prediction file
            latest_pred_file = max(pred_files, key=os.path.getctime)
            
            # Load prediction data
            import pandas as pd
            df = pd.read_csv(latest_pred_file)
            
            # Clear the plot
            if hasattr(self, 'pred_ax') and self.pred_ax:
                self.pred_ax.clear()
            else:
                print("Warning: pred_ax not found, cannot update prediction results")
                return
            
            # Determine what columns are available for plotting
            has_close = 'close' in df.columns
            has_predicted_close = 'predicted_close' in df.columns
            has_actual = 'actual' in df.columns
            has_predicted = 'predicted' in df.columns
            
            if has_close and has_predicted_close:
                # Plot actual vs predicted close prices
                x_axis = range(len(df))
                self.pred_ax.plot(x_axis, df['close'], 'b-', label='Actual Close', alpha=0.7, linewidth=2)
                self.pred_ax.plot(x_axis, df['predicted_close'], 'r-', label='Predicted Close', alpha=0.7, linewidth=2)
                
                # Calculate and display correlation
                correlation = np.corrcoef(df['close'], df['predicted_close'])[0, 1]
                self.pred_ax.text(0.02, 0.98, f'Correlation: {correlation:.4f}', 
                                transform=self.pred_ax.transAxes, va='top', fontsize=10,
                                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
                
                # Calculate error metrics
                mae = np.mean(np.abs(df['close'] - df['predicted_close']))
                mse = np.mean((df['close'] - df['predicted_close']) ** 2)
                rmse = np.sqrt(mse)
                
                # Add metrics to title
                title = f"Prediction Results - MAE: ${mae:.2f}, RMSE: ${rmse:.2f}"
                
                # Update status label
                self.prediction_status_var.set(f"Showing {len(df)} predictions - MAE: ${mae:.2f}, Correlation: {correlation:.4f}")
                
            elif has_actual and has_predicted:
                # Plot actual vs predicted values
                x_axis = range(len(df))
                self.pred_ax.plot(x_axis, df['actual'], 'b-', label='Actual', alpha=0.7, linewidth=2)
                self.pred_ax.plot(x_axis, df['predicted'], 'r-', label='Predicted', alpha=0.7, linewidth=2)
                
                # Calculate and display correlation
                correlation = np.corrcoef(df['actual'], df['predicted'])[0, 1]
                self.pred_ax.text(0.02, 0.98, f'Correlation: {correlation:.4f}', 
                                transform=self.pred_ax.transAxes, va='top', fontsize=10,
                                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
                
                # Calculate error metrics
                mae = np.mean(np.abs(df['actual'] - df['predicted']))
                mse = np.mean((df['actual'] - df['predicted']) ** 2)
                rmse = np.sqrt(mse)
                
                # Add metrics to title
                title = f"Prediction Results - MAE: {mae:.4f}, RMSE: {rmse:.4f}"
                
                # Update status label
                self.prediction_status_var.set(f"Showing {len(df)} predictions - MAE: {mae:.4f}, Correlation: {correlation:.4f}")
                
            else:
                # Show available columns for debugging
                self.pred_ax.text(0.5, 0.5, f'Available columns: {list(df.columns)}\nNo standard prediction columns found', 
                                ha='center', va='center', transform=self.pred_ax.transAxes,
                                fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                title = "Prediction Results - Column Format Issue"
                
                # Update status label
                self.prediction_status_var.set(f"Column format issue - found: {list(df.columns)}")
            
            # Set plot properties
            self.pred_ax.set_title(title)
            self.pred_ax.set_xlabel(self.get_ticker_from_filename())
            self.pred_ax.set_ylabel("Value")
            self.pred_ax.legend()
            self.pred_ax.grid(True, alpha=0.3)
            
            # Safe canvas update with error handling
            try:
                # Use draw_idle() instead of draw() to avoid recursion
                if hasattr(self, 'pred_canvas') and self.pred_canvas:
                    self.pred_canvas.draw_idle()
                    # Force a small delay to allow the canvas to update
                    self.root.after(100, lambda: None)
            except Exception as canvas_error:
                print(f"Canvas update error: {canvas_error}")
                # Try alternative update method
                try:
                    self.pred_canvas.flush_events()
                except:
                    pass
                    
        except Exception as e:
            print(f"Error updating prediction results: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message in the plot
            try:
                if hasattr(self, 'pred_ax') and self.pred_ax:
                    self.pred_ax.clear()
                    self.pred_ax.text(0.5, 0.5, f'Error updating prediction results:\n{str(e)}', 
                                    ha='center', va='center', transform=self.pred_ax.transAxes,
                                    fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                    self.pred_ax.set_title("Prediction Results - Error")
                    self.pred_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        if hasattr(self, 'pred_canvas') and self.pred_canvas:
                            self.pred_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error: {canvas_error}")
            except Exception as plot_error:
                print(f"Error creating error plot: {plot_error}")
            
            self.prediction_status_var.set(f"Error updating prediction results: {str(e)}")

    def refresh_models(self, load_plots=True):
        """Refresh the list of available models and update plots."""
        try:
            # Clear existing models from combobox
            self.model_combo['values'] = ()
            self.selected_model_path = None
            
            if not os.path.exists(self.current_model_dir):
                os.makedirs(self.current_model_dir, exist_ok=True)
                self.status_var.set(f"Created models directory: {self.current_model_dir}")
                if load_plots:
                    self.load_saved_plots()
                return
            
            model_dirs = sorted([
                d for d in os.listdir(self.current_model_dir)
                if os.path.isdir(os.path.join(self.current_model_dir, d)) and d.startswith('model_')
            ], reverse=True)
            
            # Update combobox with model directories
            self.model_combo['values'] = model_dirs
            
            if model_dirs:
                self.model_combo.set(model_dirs[0])
                if load_plots:
                    self.on_model_select(None)  # Trigger plot loading
            else:
                self.status_var.set("No models available")
                if load_plots:
                    self.load_saved_plots()
            
            # --- ADD THIS LINE ---
            self.refresh_prediction_files()
            
            # Also refresh MPEG files list
            self.refresh_mpeg_files()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh model list: {str(e)}")
            self.status_var.set(f"Error refreshing models: {str(e)}")
    
    def _training_completed(self, model_dir, train_losses, val_losses):
        """Handle training completion and save plots."""
        try:
            self.status_var.set("Training completed successfully!")
            self.train_button.config(state=tk.NORMAL)
            
            # Save loss plot
            plots_dir = os.path.join(model_dir, 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            fig = plt.Figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            epochs = list(range(1, len(train_losses) + 1))
            ax.plot(epochs, train_losses, 'b-', label='Training Loss')
            if len(val_losses) == len(train_losses):
                ax.plot(epochs, val_losses, 'r-', label='Validation Loss')
            ax.set_title(f"Training Progress ({self.get_ticker_from_filename()})")
            ax.set_xlabel("Epoch")
            ax.set_ylabel("MSE Loss")
            ax.legend()
            ax.grid(True)
            fig.savefig(os.path.join(plots_dir, 'loss_curve.png'), dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            # Refresh models and plots
            self.refresh_models()
            self.update_training_results(train_losses)
            self.update_plots_tab(train_losses, val_losses)
            self.create_3d_gradient_descent_visualization(train_losses)
            # Removed switch to 3D Gradient Descent tab since it no longer exists in Results Panel
            
            # Set the newly trained model as selected
            self.selected_model_path = model_dir
            
            # Automatically generate MPEG animation
            print("Training completed - generating MPEG animation...")
            self.status_var.set("Training completed - generating MPEG animation...")
            
            # Use after() to schedule the MPEG generation to run after GUI updates
            self.root.after(2000, self.generate_mpeg_animation)
            
            # Automatically make a prediction with the newly trained model
            if self.data_file:
                print("Training completed - making automatic prediction...")
                self.status_var.set("Training completed - making automatic prediction...")
                
                # Use after() to schedule the automatic prediction to run after GUI updates
                self.root.after(1000, self.auto_make_prediction)
            else:
                print("Training completed - no data file selected for automatic prediction")
                self.status_var.set("Training completed - select data file for prediction")
            
            messagebox.showinfo("Success", f"Model training completed successfully!\nModel saved in: {model_dir}")
            
        except Exception as e:
            print(f"Error in training completion: {e}")
            messagebox.showerror("Error", f"Error updating results: {str(e)}")
    
    def get_ticker_from_filename(self):
        """Extract ticker symbol from data filename."""
        if self.data_file:
            filename = os.path.basename(self.data_file)
            # Extract ticker from filename (e.g., 'tsla_combined.csv' -> 'TSLA')
            ticker = filename.split('_')[0].upper()
            return ticker
        return "STOCK"
    
    def update_training_results(self, train_losses):
        """Update the training results tab with loss plot."""
        try:
            self.results_ax.clear()
            epochs = list(range(1, len(train_losses) + 1))
            self.results_ax.plot(epochs, train_losses, 'b-', linewidth=2, label='Training Loss')
            self.results_ax.set_title("Training Loss Over Time")
            self.results_ax.set_xlabel("Epoch")
            self.results_ax.set_ylabel("Loss")
            self.results_ax.legend()
            self.results_ax.grid(True)
            
            # Safe canvas update
            try:
                self.results_canvas.draw_idle()
            except Exception as canvas_error:
                print(f"Canvas update error in training results: {canvas_error}")
                
        except Exception as e:
            print(f"Error updating training results: {e}")
    
    def update_plots_tab(self, train_losses, val_losses):
        """Update the plots tab with training results and saved PNG plots."""
        try:
            self.plots_ax.clear()
            ticker = self.get_ticker_from_filename()
            epochs = list(range(1, len(train_losses) + 1))
            
            # Plot training and validation losses
            self.plots_ax.plot(epochs, train_losses, 'b-', linewidth=2, label='Training Loss', alpha=0.8)
            if val_losses is not None and len(val_losses) == len(train_losses):
                self.plots_ax.plot(epochs, val_losses, 'r-', linewidth=2, label='Validation Loss', alpha=0.8)
            
            self.plots_ax.set_title(f"Training Progress Overview ({ticker})")
            self.plots_ax.set_xlabel("Epoch")
            self.plots_ax.set_ylabel("MSE Loss")
            self.plots_ax.legend()
            self.plots_ax.grid(True, alpha=0.3)
            
            # Safe canvas update
            try:
                self.plots_canvas.draw_idle()
            except Exception as canvas_error:
                print(f"Canvas update error in plots tab: {canvas_error}")
            
            # Check for PNG plots and display them in the Saved Plots tab
            plot_files = []
            if self.selected_model_path:
                plots_dir = os.path.join(self.selected_model_path, 'plots')
                if os.path.exists(plots_dir):
                    plot_files = sorted(glob.glob(os.path.join(plots_dir, '*.png')))
            
            # Update the Saved Plots tab with the new plots
            if plot_files:
                # Trigger refresh of saved plots tab
                self.load_saved_plots()
                print(f"Plots tab updated with {len(train_losses)} epochs and {len(plot_files)} PNG plots available")
            else:
                print(f"Plots tab updated with {len(train_losses)} epochs (no PNG plots found)")
                
        except Exception as e:
            print(f"Error updating plots tab: {e}")
    
    def switch_to_tab(self, tab_index):
        """Switch to a specific tab in the display notebook."""
        try:
            if 0 <= tab_index < self.display_notebook.index('end'):
                self.display_notebook.select(tab_index)
        except Exception as e:
            print(f"Error switching to tab {tab_index}: {e}")
    
    def has_3d_visualization(self):
        """Check if the selected model has 3D visualization files."""
        if not self.selected_model_path:
            return False
        plots_dir = os.path.join(self.selected_model_path, 'plots')
        if not os.path.exists(plots_dir):
            return False
        # Check for 3D gradient descent frame files
        gd3d_files = glob.glob(os.path.join(plots_dir, 'gradient_descent_3d_frame_*.png'))
        return len(gd3d_files) > 0
    
    def update_3d_gradient_descent_tab(self):
        """Update the 3D gradient descent tab with visualization."""
        try:
            if not self.has_3d_visualization():
                print("No 3D visualization files found")
                # Show a placeholder message
                if hasattr(self, 'gd3d_display_ax') and self.gd3d_display_ax is not None:
                    self.gd3d_display_ax.clear()
                    self.gd3d_display_ax.text(0.5, 0.5, 'No 3D gradient descent visualization found.\nRun 3D visualization to generate one.', 
                                        ha='center', va='center', transform=self.gd3d_display_ax.transAxes,
                                        fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                    self.gd3d_display_ax.set_title("3D Gradient Descent Visualization")
                    self.gd3d_display_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        self.gd3d_display_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error in 3D tab: {canvas_error}")
                return
            
            plots_dir = os.path.join(self.selected_model_path, 'plots')
            gd3d_files = sorted(glob.glob(os.path.join(plots_dir, 'gradient_descent_3d_frame_*.png')))
            
            print(f"Found {len(gd3d_files)} 3D visualization files: {[os.path.basename(f) for f in gd3d_files]}")
            
            if gd3d_files and hasattr(self, 'gd3d_display_ax') and self.gd3d_display_ax is not None:
                # Load the last frame (most complete visualization)
                latest_frame = gd3d_files[-1]
                print(f"Loading latest 3D visualization: {os.path.basename(latest_frame)}")
                self.load_3d_visualization_image_display(latest_frame)
                
                # Update status
                self.status_var.set(f"3D visualization loaded: {len(gd3d_files)} frames available")
            else:
                print("No 3D visualization files found in plots directory")
                # Show a placeholder message
                if hasattr(self, 'gd3d_display_ax') and self.gd3d_display_ax is not None:
                    self.gd3d_display_ax.clear()
                    self.gd3d_display_ax.text(0.5, 0.5, 'No 3D gradient descent visualization found.\nRun 3D visualization to generate one.', 
                                        ha='center', va='center', transform=self.gd3d_display_ax.transAxes,
                                        fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                    self.gd3d_display_ax.set_title("3D Gradient Descent Visualization")
                    self.gd3d_display_ax.axis('off')
                    
                    # Safe canvas update
                    try:
                        self.gd3d_display_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error in 3D tab: {canvas_error}")
                
        except Exception as e:
            print(f"Error updating 3D gradient descent tab: {e}")
            import traceback
            traceback.print_exc()

    def load_3d_visualization_image(self, image_path):
        """Load and display 3D visualization image in the 3D tab."""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Resize image to fit the canvas (75% of original size)
            img_width, img_height = img.size
            scale = 0.75
            new_size = (int(img_width * scale), int(img_height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array for matplotlib
            img_array = np.array(img)
            
            # Clear the 3D axis and display the image
            self.gd3d_ax.clear()
            
            # Use imshow to display the image properly
            # The image array should be in the format (height, width, channels)
            if len(img_array.shape) == 3:  # RGB image
                self.gd3d_ax.imshow(img_array)
            else:  # Grayscale image
                self.gd3d_ax.imshow(img_array, cmap='gray')
            
            self.gd3d_ax.set_title(f"3D Gradient Descent Visualization\n{os.path.basename(image_path)}")
            self.gd3d_ax.axis('off')
            
            # Safe canvas update
            try:
                self.gd3d_canvas.draw_idle()
            except Exception as canvas_error:
                print(f"Canvas update error in 3D visualization: {canvas_error}")
            
            print(f"Loaded 3D visualization image: {os.path.basename(image_path)} (resized to {new_size[0]}x{new_size[1]} - {scale*100}% of original)")
            
        except Exception as e:
            print(f"Error loading 3D visualization image: {e}")
            import traceback
            traceback.print_exc()

            messagebox.showerror("Error", f"Failed to create interactive plot: {str(e)}")

    def open_live_training_plot(self):
        """Open a live training plot window using Matplotlib."""
        try:
            # Close any existing plot first
            if hasattr(self, 'live_plot_fig') and self.live_plot_fig is not None:
                try:
                    plt.close(self.live_plot_fig)
                except:
                    pass
            
            # Create a new matplotlib window with error handling
            try:
                self.live_plot_fig, self.live_plot_ax = plt.subplots(figsize=(10, 6))
            except Exception as fig_error:
                print(f"Error creating figure: {fig_error}")
                raise
            
            self.live_plot_window_open = True
            self.live_plot_epochs = []
            self.live_plot_losses = []
            
            # Set up the plot with error handling
            try:
                ticker = self.get_ticker_from_filename()
                self.live_plot_ax.set_title(f'Live Training Loss ({ticker})')
                self.live_plot_ax.set_xlabel('Epoch')
                self.live_plot_ax.set_ylabel('Loss')
                self.live_plot_ax.grid(True, alpha=0.3)
                
                # Set initial limits
                self.live_plot_ax.set_xlim(0, 10)
                self.live_plot_ax.set_ylim(0, 1)
                
            except Exception as setup_error:
                print(f"Error setting up plot: {setup_error}")
                # Continue anyway, the plot will still work
            
            # Show the plot in non-blocking mode with error handling
            try:
                plt.show(block=False)
                # Give the plot a moment to initialize
                plt.pause(0.1)
            except Exception as show_error:
                print(f"Error showing plot: {show_error}")
                # Try alternative method
                try:
                    self.live_plot_fig.show()
                except:
                    pass
            
            # Create live plot status label if it doesn't exist
            if self.live_plot_status is None:
                self.live_plot_status = ttk.Label(self.root, text="Live training plot status")
                self.live_plot_status.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
            
            self.live_plot_status.config(text="Live training plot opened. Training progress will be shown here.")
            print("Live training plot opened successfully")
            
        except Exception as e:
            print(f"Error opening live training plot: {e}")
            import traceback
            traceback.print_exc()
            self.live_plot_window_open = False
            self.live_plot_fig = None
            self.live_plot_ax = None
            messagebox.showerror("Error", f"Failed to open live training plot: {str(e)}")

    def update_live_plot(self, epoch, loss):
        """Update the live matplotlib plot with new data."""
        if not self.live_plot_window_open:
            return
        
        try:
            # Add new data point
            self.live_plot_epochs.append(epoch)
            self.live_plot_losses.append(loss)
            
            # Clear and redraw the plot with error handling
            try:
                self.live_plot_ax.clear()
                self.live_plot_ax.plot(self.live_plot_epochs, self.live_plot_losses, 'b-', linewidth=2, marker='o', markersize=4)
                
                # Update labels and title
                ticker = self.get_ticker_from_filename()
                self.live_plot_ax.set_title(f'Live Training Loss ({ticker})')
                self.live_plot_ax.set_xlabel('Epoch')
                self.live_plot_ax.set_ylabel('Loss')
                self.live_plot_ax.grid(True, alpha=0.3)
                
                # Auto-scale the axes with bounds checking
                if len(self.live_plot_epochs) > 1:
                    self.live_plot_ax.set_xlim(0, max(self.live_plot_epochs) + 1)
                    if len(self.live_plot_losses) > 1:
                        min_loss = min(self.live_plot_losses)
                        max_loss = max(self.live_plot_losses)
                        if max_loss > min_loss:  # Avoid division by zero
                            margin = (max_loss - min_loss) * 0.1
                            self.live_plot_ax.set_ylim(min_loss - margin, max_loss + margin)
                        else:
                            # If all losses are the same, set a small range
                            self.live_plot_ax.set_ylim(min_loss - 0.1, min_loss + 0.1)
                
            except Exception as plot_error:
                print(f"Error updating plot data: {plot_error}")
                return
            
            # Safe canvas update with multiple fallback methods
            update_success = False
            
            # Method 1: Try draw_idle()
            try:
                self.live_plot_fig.canvas.draw_idle()
                update_success = True
            except Exception as e1:
                print(f"Method 1 failed: {e1}")
                
                # Method 2: Try draw()
                try:
                    self.live_plot_fig.canvas.draw()
                    update_success = True
                except Exception as e2:
                    print(f"Method 2 failed: {e2}")
                    
                    # Method 3: Try flush_events()
                    try:
                        self.live_plot_fig.canvas.flush_events()
                        update_success = True
                    except Exception as e3:
                        print(f"Method 3 failed: {e3}")
                        
                        # Method 4: Try plt.pause()
                        try:
                            plt.pause(0.001)
                            update_success = True
                        except Exception as e4:
                            print(f"Method 4 failed: {e4}")
            
            if not update_success:
                print("Warning: All canvas update methods failed")
            
            # Also update the Live Training Plot tab if it exists
            try:
                if hasattr(self, 'live_training_ax') and self.live_training_ax is not None:
                    # Update the live training plot tab
                    self.live_training_ax.clear()
                    self.live_training_ax.plot(self.live_plot_epochs, self.live_plot_losses, 'b-', linewidth=2, marker='o', markersize=4)
                    
                    # Update labels and title
                    ticker = self.get_ticker_from_filename()
                    self.live_training_ax.set_title(f'Live Training Loss ({ticker})')
                    self.live_training_ax.set_xlabel('Epoch')
                    self.live_training_ax.set_ylabel('Loss')
                    self.live_training_ax.grid(True, alpha=0.3)
                    
                    # Auto-scale the axes
                    if len(self.live_plot_epochs) > 1:
                        self.live_training_ax.set_xlim(0, max(self.live_plot_epochs) + 1)
                        if len(self.live_plot_losses) > 1:
                            min_loss = min(self.live_plot_losses)
                            max_loss = max(self.live_plot_losses)
                            if max_loss > min_loss:
                                margin = (max_loss - min_loss) * 0.1
                                self.live_training_ax.set_ylim(min_loss - margin, max_loss + margin)
                            else:
                                self.live_training_ax.set_ylim(min_loss - 0.1, min_loss + 0.1)
                    
                    # Update status
                    if hasattr(self, 'live_training_status'):
                        self.live_training_status.config(text=f"Live training: Epoch {epoch}, Loss {loss:.6f}")
                    
                    # Safe canvas update for live training tab
                    try:
                        self.live_training_canvas.draw_idle()
                    except Exception as canvas_error:
                        print(f"Canvas update error in live training tab: {canvas_error}")
                        
            except Exception as tab_error:
                print(f"Error updating live training tab: {tab_error}")
            
            print(f"Live plot updated: Epoch {epoch}, Loss {loss:.6f}")
            
        except Exception as e:
            print(f"Error updating live plot: {e}")
            import traceback
            traceback.print_exc()
            # If we get a serious error, close the plot to prevent further issues
            try:
                self.close_live_plot()
            except:
                pass

    def close_live_plot(self):
        """Close the live training plot."""
        try:
            self.live_plot_window_open = False
            
            if hasattr(self, 'live_plot_fig') and self.live_plot_fig is not None:
                try:
                    # Check if the figure still exists
                    if plt.fignum_exists(self.live_plot_fig.number):
                        plt.close(self.live_plot_fig)
                except Exception as close_error:
                    print(f"Error closing plot: {close_error}")
                    # Try alternative closing method
                    try:
                        self.live_plot_fig.canvas.get_tk_widget().destroy()
                    except:
                        pass
            
            # Clean up variables
            self.live_plot_fig = None
            self.live_plot_ax = None
            self.live_plot_epochs = []
            self.live_plot_losses = []
            
            # Update status
            try:
                self.live_plot_status.config(text="Live training plot closed.")
            except:
                pass
                
            print("Live training plot closed")
            
        except Exception as e:
            print(f"Error closing live plot: {e}")
            # Force cleanup even if there's an error
            self.live_plot_window_open = False
            self.live_plot_fig = None
            self.live_plot_ax = None
            self.live_plot_epochs = []
            self.live_plot_losses = []

    def parse_training_output_for_loss(self, line):
        """Parse training output line to extract epoch and loss information."""
        try:
            # Look for new LOSS format: "LOSS:epoch,loss_value"
            loss_pattern = r"LOSS:(\d+),([\d.]+)"
            match = re.search(loss_pattern, line)
            if match:
                epoch = int(match.group(1))
                loss = float(match.group(2))
                if self.live_plot_window_open:
                    self.root.after(0, lambda e=epoch, l=loss: self.update_live_plot(e, l))
                return epoch, loss

            # Look for new WEIGHTS format: "WEIGHTS:epoch,w1_avg,w2_avg"
            weights_pattern = r"WEIGHTS:(\d+),([\d.-]+),([\d.-]+)"
            match = re.search(weights_pattern, line)
            if match:
                epoch = int(match.group(1))
                w1_avg = float(match.group(2))
                w2_avg = float(match.group(3))
                if not hasattr(self, "live_gd_weights"):
                    self.live_gd_weights = []
                self.live_gd_weights.append([w1_avg, w2_avg])
                return epoch, None

            # Legacy patterns
            epoch_pattern = r'Epoch\s+(\d+)/(\d+),\s+Loss:\s+([\d.]+)'
            match = re.search(epoch_pattern, line)
            if match:
                epoch = int(match.group(1))
                total_epochs = int(match.group(2))
                loss = float(match.group(3))
                if self.live_plot_window_open:
                    self.root.after(0, lambda e=epoch, l=loss: self.update_live_plot(e, l))
                return epoch, loss

            alt_pattern = r'epoch\s+(\d+)\s+loss:\s+([\d.]+)'
            match = re.search(alt_pattern, line)
            if match:
                epoch = int(match.group(1))
                loss = float(match.group(2))
                if self.live_plot_window_open:
                    self.root.after(0, lambda e=epoch, l=loss: self.update_live_plot(e, l))
                return epoch, loss

            return None, None
        except Exception as e:
            print(f"Error parsing training output: {e}")
            return None, None

    def auto_make_prediction(self):
        """Automatically make a prediction after training completes."""
        try:
            if self.selected_model_path and self.data_file:
                print("🔄 Auto-making prediction after training...")
                self.make_prediction()
            else:
                print("⚠️  Cannot auto-make prediction: missing model or data file")
        except Exception as e:
            print(f"❌ Error in auto-make prediction: {e}")

    def select_data_file(self):
        """Automatically select a suitable data file if available."""
        try:
            # Look for common data files in the current directory
            data_files = []
            for file in os.listdir('.'):
                if file.endswith('.csv') and any(pattern in file.lower() for pattern in ['stock', 'price', 'data', 'tsla', 'aapl', 'msft']):
                    data_files.append(file)
            
            if data_files:
                # Use the first found data file
                selected_file = data_files[0]
                self.data_file = selected_file
                self.data_file_var.set(selected_file)
                self.load_data_features()
                self.status_var.set(f"Auto-selected data file: {selected_file}")
                return True
            else:
                self.status_var.set("No suitable data file found - please browse manually")
                return False
                
        except Exception as e:
            print(f"Error auto-selecting data file: {e}")
            self.status_var.set(f"Error selecting data file: {str(e)}")
            return False

    # 3D Animation and Control Methods
    def play_3d_animation(self):
        """Start playing the 3D animation."""
        try:
            if not hasattr(self, 'gd3d_ax') or not self.gd3d_ax:
                self.status_var.set("No 3D visualization available")
                return
            
            if not hasattr(self, 'animation_running'):
                self.animation_running = False
            
            if not self.animation_running:
                self.animation_running = True
                self.current_frame = 0
                self.animate_3d_frames()
                self.status_var.set("3D animation started")
            else:
                self.status_var.set("Animation already running")
                
        except Exception as e:
            print(f"Error starting 3D animation: {e}")
            self.status_var.set(f"Error starting animation: {str(e)}")

    def pause_3d_animation(self):
        """Pause the 3D animation."""
        try:
            if hasattr(self, 'animation_running'):
                self.animation_running = False
                self.status_var.set("3D animation paused")
            else:
                self.status_var.set("No animation running")
                
        except Exception as e:
            print(f"Error pausing 3D animation: {e}")
            self.status_var.set(f"Error pausing animation: {str(e)}")

    def stop_3d_animation(self):
        """Stop the 3D animation and reset to first frame."""
        try:
            if hasattr(self, 'animation_running'):
                self.animation_running = False
                self.current_frame = 0
                self.load_3d_frame(0)
                self.status_var.set("3D animation stopped")
            else:
                self.status_var.set("No animation running")
                
        except Exception as e:
            print(f"Error stopping 3D animation: {e}")
            self.status_var.set(f"Error stopping animation: {str(e)}")

    def animate_3d_frames(self):
        """Animate through 3D frames."""
        try:
            if not hasattr(self, 'animation_running') or not self.animation_running:
                return
            
            if not hasattr(self, 'current_frame'):
                self.current_frame = 0
            
            if not hasattr(self, 'total_frames'):
                self.total_frames = self.get_total_3d_frames()
            
            if self.current_frame >= self.total_frames:
                self.current_frame = 0
            
            # Load current frame
            self.load_3d_frame(self.current_frame)
            
            # Update frame label
            if hasattr(self, 'frame_label'):
                self.frame_label.config(text=f"Frame: {self.current_frame + 1}/{self.total_frames}")
            
            # Schedule next frame
            delay = int(1000 / (self.anim_speed_var.get() * 10))  # Convert speed to milliseconds
            self.root.after(delay, self.animate_3d_frames)
            
            self.current_frame += 1
            
        except Exception as e:
            print(f"Error in 3D animation: {e}")
            self.animation_running = False

    def get_total_3d_frames(self):
        """Get the total number of 3D frames available."""
        try:
            if not self.selected_model_path:
                return 0
            
            plots_dir = os.path.join(self.selected_model_path, 'plots')
            if not os.path.exists(plots_dir):
                return 0
            
            gd3d_files = glob.glob(os.path.join(plots_dir, 'gradient_descent_3d_frame_*.png'))
            return len(gd3d_files)
            
        except Exception as e:
            print(f"Error getting total 3D frames: {e}")
            return 0

    def load_3d_frame(self, frame_index):
        """Load a specific 3D frame."""
        try:
            if not self.selected_model_path:
                return
            
            plots_dir = os.path.join(self.selected_model_path, 'plots')
            if not os.path.exists(plots_dir):
                return
            
            gd3d_files = sorted(glob.glob(os.path.join(plots_dir, 'gradient_descent_3d_frame_*.png')))
            
            if 0 <= frame_index < len(gd3d_files):
                frame_path = gd3d_files[frame_index]
                self.load_3d_visualization_image(frame_path)
                
        except Exception as e:
            print(f"Error loading 3D frame {frame_index}: {e}")

    def prev_3d_frame(self):
        """Go to previous 3D frame."""
        try:
            if not hasattr(self, 'current_frame'):
                self.current_frame = 0
            
            total_frames = self.get_total_3d_frames()
            if total_frames > 0:
                self.current_frame = (self.current_frame - 1) % total_frames
                self.load_3d_frame(self.current_frame)
                
                if hasattr(self, 'frame_label'):
                    self.frame_label.config(text=f"Frame: {self.current_frame + 1}/{total_frames}")
                
                self.status_var.set(f"Frame {self.current_frame + 1}/{total_frames}")
                
        except Exception as e:
            print(f"Error going to previous frame: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def next_3d_frame(self):
        """Go to next 3D frame."""
        try:
            if not hasattr(self, 'current_frame'):
                self.current_frame = 0
            
            total_frames = self.get_total_3d_frames()
            if total_frames > 0:
                self.current_frame = (self.current_frame + 1) % total_frames
                self.load_3d_frame(self.current_frame)
                
                if hasattr(self, 'frame_label'):
                    self.frame_label.config(text=f"Frame: {self.current_frame + 1}/{total_frames}")
                
                self.status_var.set(f"Frame {self.current_frame + 1}/{total_frames}")
                
        except Exception as e:
            print(f"Error going to next frame: {e}")
            self.status_var.set(f"Error: {str(e)}")

    def reset_3d_view(self):
        """Reset the 3D view to default."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax and hasattr(self.gd3d_ax, 'view_init'):
                self.gd3d_ax.view_init(elev=30, azim=45)
                
                # Update rotation sliders
                if hasattr(self, 'elevation_var'):
                    self.elevation_var.set(30.0)
                if hasattr(self, 'azimuth_var'):
                    self.azimuth_var.set(45.0)
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    self.gd3d_canvas.draw()
                
                self.status_var.set("3D view reset")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error resetting 3D view: {e}")
            self.status_var.set(f"Error resetting view: {str(e)}")

    def set_top_view(self):
        """Set 3D view to top view."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax and hasattr(self.gd3d_ax, 'view_init'):
                self.gd3d_ax.view_init(elev=90, azim=0)
                
                # Update rotation sliders
                if hasattr(self, 'elevation_var'):
                    self.elevation_var.set(90.0)
                if hasattr(self, 'azimuth_var'):
                    self.azimuth_var.set(0.0)
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    self.gd3d_canvas.draw()
                
                self.status_var.set("3D view: Top")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error setting top view: {e}")
            self.status_var.set(f"Error setting view: {str(e)}")

    def set_side_view(self):
        """Set 3D view to side view."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax and hasattr(self.gd3d_ax, 'view_init'):
                self.gd3d_ax.view_init(elev=0, azim=0)
                
                # Update rotation sliders
                if hasattr(self, 'elevation_var'):
                    self.elevation_var.set(0.0)
                if hasattr(self, 'azimuth_var'):
                    self.azimuth_var.set(0.0)
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    self.gd3d_canvas.draw()
                
                self.status_var.set("3D view: Side")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error setting side view: {e}")
            self.status_var.set(f"Error setting view: {str(e)}")

    def set_isometric_view(self):
        """Set 3D view to isometric."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax and hasattr(self.gd3d_ax, 'view_init'):
                self.gd3d_ax.view_init(elev=35.264, azim=45)
                
                # Update rotation sliders
                if hasattr(self, 'elevation_var'):
                    self.elevation_var.set(35.264)
                if hasattr(self, 'azimuth_var'):
                    self.azimuth_var.set(45.0)
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    self.gd3d_canvas.draw()
                
                self.status_var.set("3D view: Isometric")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error setting isometric view: {e}")
            self.status_var.set(f"Error setting view: {str(e)}")

    def rotate_x(self):
        """Rotate 3D view around X axis."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax and hasattr(self.current_3d_ax, 'view_init'):
                current_elev, current_azim = self.current_3d_ax.elev, self.current_3d_ax.azim
                self.current_3d_ax.view_init(elev=current_elev + 15, azim=current_azim)
                
                # Update rotation sliders
                self.x_rotation_var.set(current_elev + 15)
                self.y_rotation_var.set(current_azim)
                self.z_rotation_var.set(current_azim)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("Rotated around X axis")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error rotating X: {e}")
            self.status_var.set(f"Error rotating: {str(e)}")

    def rotate_y(self):
        """Rotate 3D view around Y axis."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax and hasattr(self.current_3d_ax, 'view_init'):
                current_elev, current_azim = self.current_3d_ax.elev, self.current_3d_ax.azim
                self.current_3d_ax.view_init(elev=current_elev, azim=current_azim + 15)
                
                # Update rotation sliders
                self.x_rotation_var.set(current_elev)
                self.y_rotation_var.set(current_azim + 15)
                self.z_rotation_var.set(current_azim + 15)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("Rotated around Y axis")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error rotating Y: {e}")
            self.status_var.set(f"Error rotating: {str(e)}")

    def rotate_z(self):
        """Rotate 3D view around Z axis."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax and hasattr(self.current_3d_ax, 'view_init'):
                current_elev, current_azim = self.current_3d_ax.elev, self.current_3d_ax.azim
                self.current_3d_ax.view_init(elev=current_elev, azim=current_azim - 15)
                
                # Update rotation sliders
                self.x_rotation_var.set(current_elev)
                self.y_rotation_var.set(current_azim - 15)
                self.z_rotation_var.set(current_azim - 15)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("Rotated around Z axis")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error rotating Z: {e}")
            self.status_var.set(f"Error rotating: {str(e)}")

    def zoom_in(self):
        """Zoom in on 3D plot."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                # Get current limits
                xlim = self.current_3d_ax.get_xlim()
                ylim = self.current_3d_ax.get_ylim()
                zlim = self.current_3d_ax.get_zlim()
                
                # Zoom in by reducing range
                x_range = xlim[1] - xlim[0]
                y_range = ylim[1] - ylim[0]
                z_range = zlim[1] - zlim[0]
                
                self.current_3d_ax.set_xlim(xlim[0] + x_range * 0.1, xlim[1] - x_range * 0.1)
                self.current_3d_ax.set_ylim(ylim[0] + y_range * 0.1, ylim[1] - y_range * 0.1)
                self.current_3d_ax.set_zlim(zlim[0] + z_range * 0.1, zlim[1] - z_range * 0.1)
                
                # Update zoom slider
                current_zoom = self.zoom_var.get()
                self.zoom_var.set(min(5.0, current_zoom * 1.2))
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("Zoomed in")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error zooming in: {e}")
            self.status_var.set(f"Error zooming: {str(e)}")

    def zoom_out(self):
        """Zoom out the 3D visualization."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                # Get current view limits
                xlim = self.current_3d_ax.get_xlim()
                ylim = self.current_3d_ax.get_ylim()
                zlim = self.current_3d_ax.get_zlim()
                
                # Calculate new limits (zoom out by 20%)
                x_range = xlim[1] - xlim[0]
                y_range = ylim[1] - ylim[0]
                z_range = zlim[1] - zlim[0]
                
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                z_center = (zlim[0] + zlim[1]) / 2
                
                new_x_range = x_range * 1.2
                new_y_range = y_range * 1.2
                new_z_range = z_range * 1.2
                
                self.current_3d_ax.set_xlim(x_center - new_x_range/2, x_center + new_x_range/2)
                self.current_3d_ax.set_ylim(y_center - new_y_range/2, y_center + new_y_range/2)
                self.current_3d_ax.set_zlim(z_center - new_z_range/2, z_center + new_z_range/2)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("3D visualization zoomed out")
                
        except Exception as e:
            print(f"Error zooming out 3D visualization: {e}")
            self.status_var.set(f"Error zooming out: {str(e)}")

    def on_x_rotation_change(self, value):
        """Handle X rotation slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                # Convert slider value to radians
                angle = float(value) * np.pi / 180
                
                # Apply rotation to the 3D plot
                self.current_3d_ax.view_init(elev=self.current_3d_ax.elev, azim=angle)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set(f"X rotation: {value}°")
                
        except Exception as e:
            print(f"Error applying X rotation: {e}")

    def on_y_rotation_change(self, value):
        """Handle Y rotation slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                # Convert slider value to radians
                angle = float(value) * np.pi / 180
                
                # Apply rotation to the 3D plot
                self.current_3d_ax.view_init(elev=angle, azim=self.current_3d_ax.azim)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set(f"Y rotation: {value}°")
                
        except Exception as e:
            print(f"Error applying Y rotation: {e}")

    def on_z_rotation_change(self, value):
        """Handle Z rotation slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax and hasattr(self.current_3d_ax, 'view_init'):
                current_elev = self.current_3d_ax.elev
                self.current_3d_ax.view_init(elev=current_elev, azim=float(value))
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set(f"Z rotation: {value}°")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error changing Z rotation: {e}")
            self.status_var.set(f"Error changing rotation: {str(e)}")

    def on_elevation_change(self, value):
        """Handle elevation slider change for 3D plot."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax and hasattr(self.gd3d_ax, 'view_init'):
                current_azim = self.gd3d_ax.azim
                self.gd3d_ax.view_init(elev=float(value), azim=current_azim)
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    self.gd3d_canvas.draw()
                
                # Update the label
                if hasattr(self, 'elevation_label'):
                    self.elevation_label.config(text=f"{float(value):.0f}°")
                
                self.status_var.set(f"Elevation: {float(value):.0f}°")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error changing elevation: {e}")
            self.status_var.set(f"Error changing elevation: {str(e)}")

    def on_azimuth_change(self, value):
        """Handle azimuth slider change for 3D plot."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax and hasattr(self.gd3d_ax, 'view_init'):
                current_elev = self.gd3d_ax.elev
                self.gd3d_ax.view_init(elev=current_elev, azim=float(value))
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    self.gd3d_canvas.draw()
                
                # Update the label
                if hasattr(self, 'azimuth_label'):
                    self.azimuth_label.config(text=f"{float(value):.0f}°")
                
                self.status_var.set(f"Azimuth: {float(value):.0f}°")
            else:
                self.status_var.set("No 3D visualization available")
                
        except Exception as e:
            print(f"Error changing azimuth: {e}")
            self.status_var.set(f"Error changing azimuth: {str(e)}")

    def on_zoom_change(self, value):
        """Handle zoom slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                zoom_level = float(value)
                
                # Get current view limits
                xlim = self.current_3d_ax.get_xlim()
                ylim = self.current_3d_ax.get_ylim()
                zlim = self.current_3d_ax.get_zlim()
                
                # Calculate centers
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                z_center = (zlim[0] + zlim[1]) / 2
                
                # Calculate base ranges (assuming original zoom level of 1.0)
                base_x_range = (xlim[1] - xlim[0]) / zoom_level
                base_y_range = (ylim[1] - ylim[0]) / zoom_level
                base_z_range = (zlim[1] - zlim[0]) / zoom_level
                
                # Apply new zoom level
                new_x_range = base_x_range * zoom_level
                new_y_range = base_y_range * zoom_level
                new_z_range = base_z_range * zoom_level
                
                self.current_3d_ax.set_xlim(x_center - new_x_range/2, x_center + new_x_range/2)
                self.current_3d_ax.set_ylim(y_center - new_y_range/2, y_center + new_y_range/2)
                self.current_3d_ax.set_zlim(z_center - new_z_range/2, z_center + new_z_range/2)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set(f"Zoom level: {zoom_level:.2f}")
                
        except Exception as e:
            print(f"Error applying zoom: {e}")

    def on_camera_x_change(self, value):
        """Handle camera X position slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                camera_x = float(value)
                
                # Get current camera position
                current_pos = self.current_3d_ax.get_proj()
                
                # Update camera position (this is a simplified approach)
                # In a real implementation, you might need to use different methods
                # depending on the matplotlib version and backend
                
                self.status_var.set(f"Camera X: {camera_x}")
                
        except Exception as e:
            print(f"Error applying camera X position: {e}")

    def on_camera_y_change(self, value):
        """Handle camera Y position slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                camera_y = float(value)
                
                # Get current camera position
                current_pos = self.current_3d_ax.get_proj()
                
                # Update camera position (this is a simplified approach)
                # In a real implementation, you might need to use different methods
                # depending on the matplotlib version and backend
                
                self.status_var.set(f"Camera Y: {camera_y}")
                
        except Exception as e:
            print(f"Error applying camera Y position: {e}")

    def on_camera_z_change(self, value):
        """Handle camera Z position slider change."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                camera_z = float(value)
                
                # Get current camera position
                current_pos = self.current_3d_ax.get_proj()
                
                # Update camera position (this is a simplified approach)
                # In a real implementation, you might need to use different methods
                # depending on the matplotlib version and backend
                
                self.status_var.set(f"Camera Z: {camera_z}")
                
        except Exception as e:
            print(f"Error applying camera Z position: {e}")

    def on_frame_pos_change(self, value):
        """Handle frame position slider change."""
        try:
            frame_pos = float(value)
            
            # Calculate frame index based on percentage
            total_frames = self.get_total_3d_frames()
            if total_frames > 0:
                frame_index = int((frame_pos / 100.0) * (total_frames - 1))
                frame_index = max(0, min(frame_index, total_frames - 1))
                
                # Load the frame
                self.load_3d_frame(frame_index)
                
                # Update frame label if it exists
                if hasattr(self, 'frame_label'):
                    self.frame_label.config(text=f"Frame: {frame_index}/{total_frames-1}")
                
                self.status_var.set(f"Frame position: {frame_pos:.1f}% (Frame {frame_index})")
            else:
                self.status_var.set("No frames available")
                
        except Exception as e:
            print(f"Error changing frame position: {e}")

    def on_view_preset_change(self, event):
        """Handle view preset listbox selection change."""
        try:
            # Get the selected item
            selection = event.widget.curselection()
            if selection:
                preset_name = event.widget.get(selection[0])
                
                # Apply the selected view preset
                if preset_name == "Default":
                    self.reset_3d_view()
                elif preset_name == "Top View":
                    self.set_top_view()
                elif preset_name == "Side View":
                    self.set_side_view()
                elif preset_name == "Isometric":
                    self.set_isometric_view()
                elif preset_name == "Front View":
                    self.set_front_view()
                elif preset_name == "Back View":
                    self.set_back_view()
                
                self.status_var.set(f"View preset: {preset_name}")
                
        except Exception as e:
            print(f"Error applying view preset: {e}")

    def set_front_view(self):
        """Set front view of the 3D visualization."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                # Set front view (elev=0, azim=0)
                self.current_3d_ax.view_init(elev=0, azim=0)
                
                # Update rotation sliders
                self.x_rotation_var.set(0.0)
                self.y_rotation_var.set(0.0)
                self.z_rotation_var.set(0.0)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("3D visualization set to front view")
                
        except Exception as e:
            print(f"Error setting front view: {e}")
            self.status_var.set(f"Error setting front view: {str(e)}")

    def set_back_view(self):
        """Set back view of the 3D visualization."""
        try:
            if hasattr(self, 'current_3d_ax') and self.current_3d_ax:
                # Set back view (elev=0, azim=180)
                self.current_3d_ax.view_init(elev=0, azim=180)
                
                # Update rotation sliders
                self.x_rotation_var.set(0.0)
                self.y_rotation_var.set(0.0)
                self.z_rotation_var.set(180.0)
                
                # Update the canvas
                if hasattr(self, 'current_3d_canvas') and self.current_3d_canvas:
                    self.current_3d_canvas.draw()
                
                self.status_var.set("3D visualization set to back view")
                
        except Exception as e:
            print(f"Error setting back view: {e}")
            self.status_var.set(f"Error setting back view: {str(e)}")

    def on_anim_speed_change(self, value):
        """Handle animation speed slider change."""
        try:
            speed = float(value)
            self.gd_anim_speed.set(speed)
            if hasattr(self, 'speed_label'):
                self.speed_label.config(text=f"{speed:.1f}x")
            self.status_var.set(f"Animation speed: {speed}x")
            # If animation is running, restart the loop to apply new speed immediately
            if hasattr(self, 'gd_anim_running') and self.gd_anim_running:
                self.gd_anim_running = False
                self.root.after(10, self._restart_gd_animation)
        except ValueError:
            print(f"Invalid animation speed format: {value}")

    def _restart_gd_animation(self):
        """Helper to restart the GD animation loop with new speed."""
        self.gd_anim_running = True
        self.animate_gd_frames()

    def on_frame_rate_change(self, value):
        """Handle frame rate slider change."""
        try:
            self.frame_rate_var.set(int(value))
            self.status_var.set(f"Frame rate: {value} FPS")
        except ValueError:
            print(f"Invalid frame rate format: {value}")

    def on_loop_mode_change(self, event):
        """Handle loop mode listbox selection change."""
        try:
            # Get the selected item
            selection = event.widget.curselection()
            if selection:
                self.loop_mode_var.set(event.widget.get(selection[0]))
                self.status_var.set(f"Loop mode: {event.widget.get(selection[0])}")
        except Exception as e:
            print(f"Error handling loop mode change: {e}")

    def on_playback_dir_change(self, event):
        """Handle playback direction listbox selection change."""
        try:
            # Get the selected item
            selection = event.widget.curselection()
            if selection:
                self.playback_dir_var.set(event.widget.get(selection[0]))
                self.status_var.set(f"Playback direction: {event.widget.get(selection[0])}")
        except Exception as e:
            print(f"Error handling playback direction change: {e}")

    def on_autoplay_change(self):
        """Handle autoplay checkbox change."""
        try:
            self.autoplay_var.set(not self.autoplay_var.get())
            self.status_var.set(f"Auto-play: {'Enabled' if self.autoplay_var.get() else 'Disabled'}")
        except Exception as e:
            print(f"Error handling autoplay change: {e}")

    def on_anim_progress_change(self, value):
        """Handle animation progress slider change."""
        try:
            progress = float(value)
            self.anim_progress_var.set(progress)
            # Calculate frame index based on percentage
            total_frames = self.get_total_3d_frames()
            if total_frames > 0:
                frame_index = int((progress / 100.0) * (total_frames - 1))
                frame_index = max(0, min(frame_index, total_frames - 1))
                # Load the frame
                self.load_3d_frame(frame_index)
        except Exception as e:
            print(f"Error updating animation progress: {e}")

    def reset_3d_animation(self):
        """Reset 3D animation to beginning."""
        try:
            # Reset animation progress
            self.anim_progress_var.set(0.0)
            
            # Stop any ongoing animation
            if hasattr(self, 'animation_running') and self.animation_running:
                self.stop_3d_animation()
            
            # Load first frame
            self.load_3d_frame(0)
            
            # Reset animation speed to default
            self.anim_speed_var.set(1.0)
            
            # Reset frame position slider
            if hasattr(self, 'frame_pos_var'):
                self.frame_pos_var.set(0.0)
            
            self.status_var.set("3D animation reset to beginning")
            
        except Exception as e:
            print(f"Error resetting 3D animation: {e}")
            self.status_var.set(f"Error resetting animation: {str(e)}")

    # New 3D Gradient Descent Animation Methods
    def play_gd_animation(self):
        """Start the 3D gradient descent animation."""
        try:
            # Ensure we have the 3D axes available
            if not self.ensure_3d_axes_available():
                self.status_var.set("Error: 3D plot not initialized")
                return
            
            # Load the gradient descent history if not already loaded
            if not hasattr(self, "gd_history"):
                self.load_gd3d_history()
            
            if not hasattr(self, "gd_history") or not self.gd_history:
                self.status_var.set("Error: No gradient descent history available")
                return
            
            # Start the animation
            self.gd_anim_running = True
            self.gd_current_frame = 0
            
            # Update the frame slider
            if hasattr(self, "frame_slider"):
                self.frame_slider.config(to=len(self.gd_history["losses"]) - 1)
                self.frame_slider.set(0)
                self.frame_label.config(text=f"0/{len(self.gd_history['losses'])}")
            
            # Start the animation loop
            self.animate_gd_frames()
            
            self.status_var.set("3D animation started")
            
        except Exception as e:
            print(f"Error starting 3D animation: {e}")
            import traceback
            traceback.print_exc()
            self.status_var.set(f"Error starting animation: {str(e)}")

    def pause_gd_animation(self):
        """Pause the 3D gradient descent animation."""
        try:
            if hasattr(self, 'gd_anim_running'):
                self.gd_anim_running = False
                self.status_var.set("3D gradient descent animation paused")
            else:
                self.status_var.set("No gradient descent animation running")
                
        except Exception as e:
            print(f"Error pausing gradient descent animation: {e}")
            self.status_var.set(f"Error pausing animation: {str(e)}")

    def stop_gd_animation(self):
        """Stop the 3D gradient descent animation and reset to first frame."""
        try:
            if hasattr(self, 'gd_anim_running'):
                self.gd_anim_running = False
                self.gd_current_frame = 0
                
                # Update the frame slider and label
                if hasattr(self, "frame_slider") and hasattr(self, "gd_history"):
                    self.frame_slider.set(0)
                    self.frame_label.config(text=f"0/{len(self.gd_history['losses'])}")
                
                # Update the plot to show the first frame
                if hasattr(self, "gd_history"):
                    self.update_gd3d_frame(0)
                
                self.status_var.set("3D gradient descent animation stopped")
            else:
                self.status_var.set("No gradient descent animation running")
                
        except Exception as e:
            print(f"Error stopping gradient descent animation: {e}")
            self.status_var.set(f"Error stopping animation: {str(e)}")

    def animate_gd_frames(self):
        """Animate the gradient descent frames."""
        try:
            # Check if the GUI is still valid and exists
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                print("GUI window no longer exists, stopping animation")
                self.gd_anim_running = False
                return
            
            # Check if the animation should still be running
            if not hasattr(self, "gd_anim_running") or not self.gd_anim_running:
                return
            
            # Check if we have the required data
            if not hasattr(self, "gd_history") or not self.gd_history:
                print("No gradient descent history available, stopping animation")
                self.gd_anim_running = False
                return
            
            # Update the current frame
            if hasattr(self, "gd_current_frame"):
                self.update_gd3d_frame(self.gd_current_frame)
                
                # Update the frame slider and label if they exist
                try:
                    # Check if the root window still exists before accessing widgets
                    if (hasattr(self, 'root') and 
                        self.root.winfo_exists() and
                        hasattr(self, "frame_slider") and 
                        self.frame_slider.winfo_exists()):
                        self.frame_slider.set(self.gd_current_frame)
                    if (hasattr(self, 'root') and 
                        self.root.winfo_exists() and
                        hasattr(self, "frame_label") and 
                        self.frame_label.winfo_exists()):
                        self.frame_label.config(text=f"{self.gd_current_frame}/{len(self.gd_history['losses'])}")
                except Exception as e:
                    print(f"Error updating frame controls: {e}")
                
                # Move to next frame
                self.gd_current_frame += 1
                
                # Check if we've reached the end
                if self.gd_current_frame >= len(self.gd_history["losses"]):
                    self.gd_current_frame = 0  # Loop back to start
                
                # Schedule next frame only if animation is still running and GUI exists
                if (self.gd_anim_running and 
                    hasattr(self, 'root') and 
                    self.root.winfo_exists() and 
                    hasattr(self, 'animate_gd_frames')):
                    
                    try:
                        speed = self.gd_anim_speed.get() if hasattr(self, "gd_anim_speed") else 1.0
                        interval = int(1000 // speed)  # Convert to milliseconds
                        # Track the after ID for proper cleanup
                        after_id = self.root.after(interval, lambda: self._safe_animate_gd_frames())
                        # Store the after ID for cleanup
                        if not hasattr(self, 'gd_after_ids'):
                            self.gd_after_ids = []
                        self.gd_after_ids.append(after_id)
                    except Exception as e:
                        print(f"Error scheduling next animation frame: {e}")
                        self.gd_anim_running = False
            
        except Exception as e:
            print(f"Error in animation loop: {e}")
            import traceback
            traceback.print_exc()
            # Stop animation on error
            self.gd_anim_running = False

    def _safe_animate_gd_frames(self):
        """Safe wrapper for animate_gd_frames to prevent invalid command errors."""
        try:
            # Double-check that the GUI still exists before calling the animation
            if (hasattr(self, 'root') and 
                self.root.winfo_exists() and 
                hasattr(self, 'animate_gd_frames')):
                self.animate_gd_frames()
            else:
                print("GUI no longer valid, stopping animation")
                self.gd_anim_running = False
        except Exception as e:
            print(f"Error in safe animation wrapper: {e}")
            self.gd_anim_running = False

    def load_gd3d_history(self):
        """Load weights and losses for animation."""
        try:
            if hasattr(self, "gd_history"):
                return
                
            model_dir = self.selected_model_path
            weights_files = sorted(glob.glob(os.path.join(model_dir, "weights_history", "weights_history_*.npz")))
            
            if not weights_files:
                raise Exception("No weight history files found")
                
            losses_file = os.path.join(model_dir, "training_losses.csv")
            if not os.path.exists(losses_file):
                raise Exception("No training losses file found")
                
            losses = np.loadtxt(losses_file, delimiter=",")
            if losses.ndim > 1:
                losses = losses[:, 0]  # Use training losses
                
            weights = []
            for wf in weights_files:
                with np.load(wf) as data:
                    weights.append({
                        "W1": data["W1"],
                        "W2": data["W2"]
                    })
                    
            self.gd_history = {"weights": weights, "losses": losses}
            print(f"Loaded {len(weights)} weight snapshots and {len(losses)} loss values")
            
        except Exception as e:
            print(f"Error loading 3D history: {e}")
            raise

    def update_gd3d_frame(self, frame):
        """Update the 3D plot for the given frame."""
        try:
            if not hasattr(self, "gd_history") or frame >= len(self.gd_history["losses"]):
                return
                
            # Ensure 3D axes are available
            if not self.ensure_3d_axes_available():
                print("Error: Could not get or create 3D axes")
                return
                
            # Get the 3D axes - they should be available now
            ax = self.gd3d_ax
            canvas = self.gd3d_canvas
            
            if ax is None:
                print("Error: 3D axes are still None after ensure_3d_axes_available")
                return
                
            # Clear the plot but preserve the surface
            ax.clear()
            
            # First, plot the loss surface if we have a visualizer
            if hasattr(self, 'current_3d_visualizer') and self.current_3d_visualizer:
                visualizer = self.current_3d_visualizer
                # Plot the loss surface
                surface = ax.plot_surface(visualizer.W1, visualizer.W2, visualizer.Z,
                                        cmap=visualizer.color, alpha=visualizer.surface_alpha,
                                        linewidth=0.5, antialiased=True)
                
                # Add colorbar only if it doesn't exist
                if (not hasattr(self, 'gd3d_fig') or self.gd3d_fig is None) and hasattr(self, 'control_panel') and hasattr(self.control_panel, 'app') and hasattr(self.control_panel.app, 'gd3d_fig'):
                    self.gd3d_fig = self.control_panel.app.gd3d_fig
                if hasattr(self, 'gd3d_fig') and self.gd3d_fig:
                    # Check if colorbar already exists
                    colorbar_exists = False
                    for child in self.gd3d_fig.get_children():
                        if hasattr(child, 'get_label') and 'colorbar' in str(child).lower():
                            colorbar_exists = True
                            break
                    
                    if not colorbar_exists:
                        self.gd3d_fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
            
            # Extract weights for visualization (use first few weights for simplicity)
            w1_values = []
            w2_values = []
            z_values = []
            
            for i in range(min(frame + 1, len(self.gd_history["weights"]))):
                w = self.gd_history["weights"][i]
                # Use first weight from each layer for 3D visualization
                w1_values.append(w["W1"].flatten()[0])
                w2_values.append(w["W2"].flatten()[0])
                z_values.append(self.gd_history["losses"][i])
            
            # Plot the gradient descent path
            if len(w1_values) > 1:
                ax.plot(w1_values, w2_values, z_values, "r-", linewidth=3, label="Training Path", alpha=0.8)
            
            # Plot current position
            if w1_values:
                ax.scatter(w1_values[-1], w2_values[-1], z_values[-1], 
                          c="blue", s=100, label="Current Position", alpha=0.8)
            
            # Plot start and end points
            if len(w1_values) > 1:
                ax.scatter(w1_values[0], w2_values[0], z_values[0], 
                          c="green", s=100, label="Start", alpha=0.8)
                ax.scatter(w1_values[-1], w2_values[-1], z_values[-1], 
                          c="red", s=100, label="End", alpha=0.8)
            
            # Set labels and title
            ax.set_xlabel("Weight 1")
            ax.set_ylabel("Weight 2")
            ax.set_zlabel("Loss")
            ax.set_title(f"3D Gradient Descent - Epoch {frame + 1}")
            
            # Add legend
            if len(w1_values) > 1:
                ax.legend()
            
            # Update canvas with proper method for M3 Macs
            if canvas is not None:
                try:
                    # Use flush_events() for better compatibility with M3 Macs
                    canvas.flush_events()
                    # Also try draw() for immediate update
                    canvas.draw()
                except Exception as canvas_error:
                    print(f"Canvas update error: {canvas_error}")
                    # Fallback to draw_idle()
                    try:
                        canvas.draw_idle()
                    except Exception as fallback_error:
                        print(f"Fallback canvas update error: {fallback_error}")
            
        except Exception as e:
            print(f"Error updating 3D frame {frame}: {e}")
            import traceback
            traceback.print_exc()

    def _reinitialize_3d_plot(self):
        """Reinitialize the 3D plot if it's not properly set up."""
        try:
            # The 3D plot is created in the control panel, so we need to access it through self
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                print("✅ 3D axes already available")
                return True
                
            # If we can't find it, try to access it through the control panel
            if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'app'):
                if hasattr(self.control_panel.app, 'gd3d_ax') and self.control_panel.app.gd3d_ax is not None:
                    self.gd3d_ax = self.control_panel.app.gd3d_ax
                    self.gd3d_canvas = self.control_panel.app.gd3d_canvas
                    self.gd3d_fig = self.control_panel.app.gd3d_fig  # Also sync the figure
                    print("✅ 3D plot reinitialized from control panel")
                    return True
                    
            # If we still can't find it, try to access it through the control panel
            if hasattr(self, 'control_panel'):
                if hasattr(self.control_panel, 'app') and hasattr(self.control_panel.app, 'gd3d_ax'):
                    self.gd3d_ax = self.control_panel.app.gd3d_ax
                    self.gd3d_canvas = self.control_panel.app.gd3d_canvas
                    print("✅ 3D plot reinitialized from control panel (direct access)")
                    return True
                    
            # If we can't find it in the control panel, try to create a new one
            print("Creating new 3D plot...")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create a new figure and axes
            self.gd3d_fig = plt.Figure(figsize=(8, 6))
            self.gd3d_ax = self.gd3d_fig.add_subplot(111, projection="3d")
            
            # Create canvas (we'll need a parent widget)
            if hasattr(self, 'right_pane'):
                self.gd3d_canvas = FigureCanvasTkAgg(self.gd3d_fig, self.right_pane)
                print("✅ New 3D plot created")
                return True
            else:
                print("Error: No parent widget available for 3D canvas")
                return False
                
        except Exception as e:
            print(f"Error reinitializing 3D plot: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_help_content(self):
        """Get the help content for the GUI."""
        help_text = """
STOCK PREDICTION GUI - USER MANUAL
=================================

OVERVIEW
--------
The Stock Prediction GUI is a comprehensive neural network application for stock price prediction with advanced visualization capabilities.

Key Features:
• Neural network training with real-time visualization
• 3D gradient descent visualization
• Live training plots with Plotly integration
• Comprehensive model management
• Advanced plot controls and animation
• Prediction capabilities with multiple data sources

INTERFACE OVERVIEW
------------------
The GUI consists of two main panels:

1. CONTROL PANEL (Left Side)
   • Data Selection Tab
   • Training Parameters Tab
   • Model Management Tab
   • Plot Controls Tab
   • Help Tab (?)

2. DISPLAY PANEL (Right Side)
   • Training Results Tab
   • Prediction Results Tab
   • Gradient Descent Tab
   • 3D Gradient Descent Tab
   • Saved Plots Tab
   • Live Training Plot Tab

USAGE TIPS
----------
1. Start by selecting a data file in the Data Selection tab
2. Configure training parameters in the Training Parameters tab
3. Click "Start Training" to begin model training
4. Monitor training progress in the Training Results tab
5. Use Model Management to make predictions
6. Explore 3D visualizations in the Plot Controls tab

TROUBLESHOOTING
---------------
• If training fails, check data format and feature selection
• Clear cache if experiencing display issues
• Ensure sufficient disk space for model saving
• Check console output for detailed error messages

For more detailed information, use the "Print Full Manual" button.
"""
        return help_text

    def print_full_manual(self):
        """Print the full user manual to console."""
        try:
            from STOCK_GUI_USER_MANUAL import StockGUIUserManual
            manual = StockGUIUserManual()
            manual.print_full_manual()
        except ImportError:
            print("Manual file not found. Printing basic help...")
            print(self.get_help_content())

    def open_manual_file(self):
        """Open the manual file in a dedicated window within the GUI."""
        import os
        
        manual_file = os.path.join(os.path.dirname(__file__), "STOCK_GUI_USER_MANUAL.py")
        
        if os.path.exists(manual_file):
            self.show_manual_window(manual_file)
        else:
            print(f"Manual file not found at: {manual_file}")
            # Show basic help in a window instead
            self.show_manual_window(None)

    def show_manual_window(self, manual_file_path=None):
        """Show the manual in a dedicated window."""
        # Create a new top-level window
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Stock Prediction GUI - Complete User Manual")
        manual_window.geometry("800x600")
        manual_window.configure(bg='white')
        
        # Make the window modal (user must close it before using main window)
        manual_window.transient(self.root)
        manual_window.grab_set()
        
        # Configure pack weights
        manual_window.pack_columnconfigure(0, weight=1)
        manual_window.pack_rowconfigure(1, weight=1)
        
        # Title frame
        title_frame = ttk.Frame(manual_window)
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        title_frame.pack_columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="Stock Prediction GUI - Complete User Manual", 
                               font=("Arial", 16, "bold"))
        title_label.pack(anchor="w")
        
        # Close button
        close_btn = ttk.Button(title_frame, text="Close", command=manual_window.destroy)
        close_btn.pack(padx=(10, 0))
        
        # Text widget frame
        text_frame = ttk.Frame(manual_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        text_frame.pack_columnconfigure(0, weight=1)
        text_frame.pack_rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar - improved configuration
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 11), 
                             bg="white", relief=tk.SUNKEN, padx=10, pady=10,
                             state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(fill="both", expand=True)
        scrollbar.pack(fill="y")
        
        # Get content
        if manual_file_path:
            try:
                # Try to load the actual manual file
                with open(manual_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the docstring content from the manual file
                import re
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    manual_content = docstring_match.group(1).strip()
                else:
                    manual_content = content
                    
            except Exception as e:
                print(f"Error reading manual file: {e}")
                manual_content = self.get_full_manual_content()
        else:
            manual_content = self.get_full_manual_content()
        
        # Insert content - make sure it's not empty
        if manual_content.strip():
            text_widget.insert(tk.END, manual_content)
            print(f"✅ Manual window: Inserted {len(manual_content)} characters of manual content")
        else:
            # Fallback content
            fallback_content = """
STOCK PREDICTION GUI - USER MANUAL
=================================

OVERVIEW
--------
The Stock Prediction GUI is a comprehensive neural network application for stock price prediction with advanced visualization capabilities.

Key Features:
• Neural network training with real-time visualization
• 3D gradient descent visualization
• Live training plots with Plotly integration
• Comprehensive model management
• Advanced plot controls and animation
• Prediction capabilities with multiple data sources

INTERFACE OVERVIEW
------------------
The GUI consists of two main panels:

1. CONTROL PANEL (Left Side)
   • Data Selection Tab
   • Training Parameters Tab
   • Model Management Tab
   • Plot Controls Tab
   • Help Tab (?)

2. DISPLAY PANEL (Right Side)
   • Training Results Tab
   • Prediction Results Tab
   • Gradient Descent Tab
   • 3D Gradient Descent Tab
   • Saved Plots Tab
   • Live Training Plot Tab

USAGE TIPS
----------
1. Start by selecting a data file in the Data Selection tab
2. Configure training parameters in the Training Parameters tab
3. Click "Start Training" to begin model training
4. Monitor training progress in the Training Results tab
5. Use Model Management to make predictions
6. Explore 3D visualizations in the Plot Controls tab

TROUBLESHOOTING
---------------
• If training fails, check data format and feature selection
• Clear cache if experiencing display issues
• Ensure sufficient disk space for model saving
• Check console output for detailed error messages

For more detailed information, use the "Print Full Manual" button.
"""
            text_widget.insert(tk.END, fallback_content)
            print("✅ Manual window: Inserted fallback manual content")
        
        # Make read-only after inserting content
        text_widget.config(state=tk.DISABLED)
        
        # Force update to ensure content is displayed
        text_widget.update()
        
        # Focus on the window
        manual_window.focus_set()
        
        # Center the window on screen
        manual_window.update_idletasks()
        x = (manual_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (manual_window.winfo_screenheight() // 2) - (600 // 2)
        manual_window.geometry(f"800x600+{x}+{y}")
        
        # Force update to ensure content is displayed
        manual_window.update()

    def get_full_manual_content(self):
        """Get the full manual content as a formatted string."""
        return """
STOCK PREDICTION GUI - COMPREHENSIVE USER MANUAL
===============================================

OVERVIEW
--------
The Stock Prediction GUI is a comprehensive neural network application for stock price prediction with advanced visualization capabilities.

Key Features:
• Neural network training with real-time visualization
• 3D gradient descent visualization
• Live training plots with Plotly integration
• Comprehensive model management
• Advanced plot controls and animation
• Prediction capabilities with multiple data sources

INSTALLATION
------------
1. Ensure Python 3.8+ is installed
2. Install required dependencies:
   pip install tkinter matplotlib numpy pandas scikit-learn plotly
3. Navigate to the simple directory:
   cd /path/to/neural_net/simple
4. Run the GUI:
   python stock_gui.py

INTERFACE OVERVIEW
------------------
The GUI consists of two main panels:

1. CONTROL PANEL (Left Side)
   • Data Selection Tab
   • Training Parameters Tab
   • Model Management Tab
   • Plot Controls Tab
   • Help Tab (?)

2. DISPLAY PANEL (Right Side)
   • Training Results Tab
   • Prediction Results Tab
   • Gradient Descent Tab
   • 3D Gradient Descent Tab
   • Saved Plots Tab
   • Live Training Plot Tab

DETAILED TAB GUIDE
==================

DATA SELECTION TAB
-----------------
Location: Control Panel → Data Selection

Features:
• Data File Selection: Browse and select CSV files with stock data
• Feature Selection: Multi-select listbox for choosing input features
• Target Feature: Dropdown to select the target variable (default: close)
• Output Directory: Choose where to save results

Data File Requirements:
• CSV format with columns like: open, high, low, close, volume
• Or generic feature columns: feature_1, feature_2, etc.
• Minimum 100 rows recommended for training

Feature Selection:
• Lock Selected: Permanently select specific features
• Unlock All: Clear feature selection
• Target Feature: The variable to predict (usually 'close' price)

TRAINING PARAMETERS TAB
----------------------
Location: Control Panel → Training Parameters

Model Configuration:
• Hidden Layer Size: 4-128 neurons (default: 32)
• Learning Rate: 0.001-0.1 (default: 0.01)
• Batch Size: 1-512 (default: 32)

Training Process:
• Start Training: Begin model training process
• Live Training Plot: Open real-time training visualization
• Clear Cache: Clear cached data and plots

Training Tips:
• Start with default parameters for first training
• Adjust hidden layer size based on data complexity
• Lower learning rate for more stable training
• Larger batch sizes for faster training

MODEL MANAGEMENT TAB
-------------------
Location: Control Panel → Model Management

Model Operations:
• Select Model: Choose from trained models in dropdown
• Refresh Models: Update the model list
• Make Prediction: Generate predictions with selected model

Prediction Files:
• View saved prediction results
• Refresh prediction files list
• View detailed prediction results

3D Visualization:
• Create 3D Visualization: Generate 3D gradient descent plots
• Requires a trained model with saved weights

PLOT CONTROLS TAB
-----------------
Location: Control Panel → Plot Controls

3D Visualization Parameters:
• View Preset: Default, Top View, Side View, Isometric, Front View, Back View
• Rotation X: -180° to 180° (default: 0°)
• Rotation Y: -180° to 180° (default: 0°)
• Rotation Z: -180° to 180° (default: 0°)
• Zoom Level: 0.1x to 5.0x (default: 1.0x)
• Camera Position: Adjust 3D camera view (X, Y, Z coordinates)

Animation Controls:
• Animation Speed: 0.1x to 5.0x (default: 1.0x)
• Frame Rate: 1 to 60 FPS (default: 30 FPS)
• Loop Mode: Loop, Once, Ping-Pong (default: Loop)
• Playback Direction: Forward, Reverse (default: Forward)
• Auto-play: Enable/disable automatic animation (default: Disabled)
• Animation Progress: 0% to 100% (default: 0%)

Animation Buttons:
• Play: Start/resume animation
• Pause: Pause animation
• Stop: Stop and reset animation
• Reset: Reset to beginning

Visualization Parameters:
• Color Map: Choose from various matplotlib colormaps
• Point Size: Adjust size of 3D points
• Line Width: Adjust width of 3D lines
• Surface Alpha: Transparency of 3D surfaces
• pack Points: Number of points for 3D pack
• Output Resolution: Width and height for saved images

DISPLAY PANEL TABS
==================

TRAINING RESULTS TAB
-------------------
• Real-time training progress display
• Loss curve visualization
• Training metrics and statistics
• Matplotlib toolbar for plot interaction

PREDICTION RESULTS TAB
---------------------
• Display prediction results
• Actual vs Predicted plots
• Prediction accuracy metrics
• Export functionality

GRADIENT DESCENT TAB
-------------------
• 2D gradient descent visualization
• Training path visualization
• Loss surface plots
• Interactive plot controls

3D GRADIENT DESCENT TAB
----------------------
• 3D visualization of gradient descent
• Interactive 3D controls
• Animation playback
• Multiple view presets

SAVED PLOTS TAB
--------------
• Browse and view saved plots
• Plot management
• Export functionality

LIVE TRAINING PLOT TAB
---------------------
• Real-time training visualization
• Live loss curve updates
• Training progress monitoring

USAGE WORKFLOW
==============

Step 1: Data Preparation
• Select a data file in the Data Selection tab
• Choose appropriate features for training
• Set the target feature (usually 'close' price)
• Select an output directory

Step 2: Model Configuration
• Configure training parameters in Training Parameters tab
• Start with default values for first training
• Adjust parameters based on results

Step 3: Training
• Click "Start Training" to begin
• Monitor progress in Training Results tab
• Use Live Training Plot for real-time monitoring

Step 4: Model Management
• Select trained model in Model Management tab
• Make predictions on new data
• View prediction results and accuracy

Step 5: Visualization
• Create 3D visualizations in Plot Controls tab
• Explore different view angles and animations
• Save plots for later use

TROUBLESHOOTING
===============

Common Issues:

1. Training Fails
   • Check data format and feature selection
   • Ensure sufficient data (minimum 100 rows)
   • Verify target feature is numeric
   • Check console output for error messages

2. Display Issues
   • Clear cache using "Clear Cache" button
   • Restart the application if needed
   • Check available system memory

3. 3D Visualization Problems
   • Ensure model has been trained successfully
   • Check that 3D visualization files exist
   • Try different view presets

4. Performance Issues
   • Reduce batch size for large datasets
   • Use smaller hidden layer sizes
   • Clear cache regularly

5. File Not Found Errors
   • Verify file paths are correct
   • Check file permissions
   • Ensure files are in the expected format

KEYBOARD SHORTCUTS
==================
• Ctrl+O: Open data file
• Ctrl+S: Save model
• Ctrl+P: Make prediction
• Ctrl+Q: Quit application

ADVANCED FEATURES
=================

Custom Optimizers:
• Support for custom optimization algorithms
• Integration with custom_optimizers module
• Dynamic optimizer loading

Technical Indicators:
• Automatic calculation of technical indicators
• RSI, Moving Averages, Bollinger Bands
• Custom indicator support

Data Conversion:
• Automatic data format detection
• OHLCV format conversion
• Support for various data sources

Model Persistence:
• Automatic model saving
• Training history preservation
• Scalable model storage

LIMITATIONS
===========
• Requires Python 3.8 or higher
• Limited to tabular data (CSV format)
• Single target variable prediction
• No real-time data streaming
• Memory usage scales with dataset size

FUTURE ENHANCEMENTS
===================
• Support for multiple target variables
• Real-time data integration
• Advanced model architectures
• Cloud deployment options
• Enhanced visualization options

CONTACT AND SUPPORT
==================
For issues and questions:
• Check the console output for error messages
• Review this manual for troubleshooting
• Ensure all dependencies are properly installed
• Verify data format and file paths

Version: 1.0
Last Updated: 2025-01-27
"""

    def format_manual_text(self, text_widget):
        """Apply formatting tags to the manual text."""
        content = text_widget.get("1.0", tk.END)
        
        # Find and tag titles (lines with =)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().endswith('=') and len(line.strip()) > 3:
                start = f"{i+1}.0"
                end = f"{i+1}.end"
                text_widget.tag_add("title", start, end)
        
        # Find and tag section headers (lines with -)
        for i, line in enumerate(lines):
            if line.strip().endswith('-') and len(line.strip()) > 3:
                start = f"{i+1}.0"
                end = f"{i+1}.end"
                text_widget.tag_add("section", start, end)
        
        # Find and tag subsections (lines with •)
        for i, line in enumerate(lines):
            if line.strip().startswith('•'):
                start = f"{i+1}.0"
                end = f"{i+1}.end"
                text_widget.tag_add("subsection", start, end)

    def refresh_color_combobox(self):
        """Refresh the color combobox to ensure it displays the current value."""
        try:
            if hasattr(self, 'color_combo') and self.color_combo:
                current_color = self.color_var.get()
                valid_colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Reds', 'Blues', 'Greens', 'Oranges', 'Purples', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'jet', 'hot', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter']
                
                if current_color and current_color in valid_colormaps:
                    self.color_combo.set(current_color)
                    print(f"🔄 Refreshed color combobox to: '{current_color}'")
                else:
                    self.color_combo.set('viridis')
                    self.color_var.set('viridis')
                    print(f"🔄 Reset color combobox to default: 'viridis'")
                
                # Force update
                self.color_combo.update()
                return True
        except Exception as e:
            print(f"❌ Error refreshing color combobox: {e}")
            return False

    def browse_data_file(self):
        print("🔍 browse_data_file() called")
        """Browse for data file."""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.data_file = filename
            self.data_file_var.set(filename)
            self.load_data_features()
            self.status_var.set(f"Loaded data file: {os.path.basename(filename)}")

    def on_model_select(self, event):
        """Handle model selection from the combo box."""
        selected_model = self.model_combo.get()
        if selected_model:
            self.selected_model_path = os.path.join(self.current_model_dir, selected_model)
            self.status_var.set(f"Selected model: {selected_model}")
            # Always refresh MPEG files after model selection
            self.refresh_mpeg_files()
            
            # Load 3D visualization automatically when model is selected
            try:
                self.load_3d_visualization_in_gui()
            except Exception as e:
                print(f"⚠️  Could not load 3D visualization automatically: {e}")
        else:
            self.selected_model_path = None

    def ensure_3d_axes_available(self):
        """Ensure 3D axes are available for gradient descent animation."""
        try:
            # First, try to access the 3D axes from the control panel
            if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'app'):
                if hasattr(self.control_panel.app, 'gd3d_ax') and self.control_panel.app.gd3d_ax is not None:
                    self.gd3d_ax = self.control_panel.app.gd3d_ax
                    self.gd3d_canvas = self.control_panel.app.gd3d_canvas
                    # Also get the figure from the control panel
                    if hasattr(self.control_panel.app, 'gd3d_fig'):
                        self.gd3d_fig = self.control_panel.app.gd3d_fig
                    print("✅ 3D axes accessed from control panel")
                    return True
                    
            # If we can't find it in the control panel, try direct access
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                print("✅ 3D axes already available")
                return True
                    
            # If we can't find it anywhere, try to create a new one
            print("Creating new 3D plot...")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Create a new figure and axes
            self.gd3d_fig = plt.Figure(figsize=(8, 6))
            self.gd3d_ax = self.gd3d_fig.add_subplot(111, projection="3d")
            
            # Create canvas (we'll need a parent widget)
            if hasattr(self, 'right_pane'):
                self.gd3d_canvas = FigureCanvasTkAgg(self.gd3d_fig, self.right_pane)
                print("✅ New 3D plot created")
                return True
            else:
                print("Error: No parent widget available for 3D canvas")
                return False
                
        except Exception as e:
            print(f"Error ensuring 3D axes availability: {e}")
            import traceback
            traceback.print_exc()
            return False

    def refresh_live_training_plot(self):
        """Refresh the live training plot with current training data."""
        try:
            if not hasattr(self, 'live_training_ax') or self.live_training_ax is None:
                return
            
            # Check if we have training data
            if hasattr(self, 'live_plot_epochs') and hasattr(self, 'live_plot_losses') and self.live_plot_epochs:
                # Update the live training plot
                self.live_training_ax.clear()
                self.live_training_ax.plot(self.live_plot_epochs, self.live_plot_losses, 'b-', linewidth=2, marker='o', markersize=4)
                
                # Update labels and title
                ticker = self.get_ticker_from_filename()
                self.live_training_ax.set_title(f'Live Training Loss ({ticker})')
                self.live_training_ax.set_xlabel('Epoch')
                self.live_training_ax.set_ylabel('Loss')
                self.live_training_ax.grid(True, alpha=0.3)
                
                # Auto-scale the axes
                if len(self.live_plot_epochs) > 1:
                    self.live_training_ax.set_xlim(0, max(self.live_plot_epochs) + 1)
                    if len(self.live_plot_losses) > 1:
                        min_loss = min(self.live_plot_losses)
                        max_loss = max(self.live_plot_losses)
                        if max_loss > min_loss:
                            margin = (max_loss - min_loss) * 0.1
                            self.live_training_ax.set_ylim(min_loss - margin, max_loss + margin)
                        else:
                            self.live_training_ax.set_ylim(min_loss - 0.1, min_loss + 0.1)
                
                # Update status
                if hasattr(self, 'live_training_status'):
                    self.live_training_status.config(text=f"Live training plot updated: {len(self.live_plot_epochs)} epochs")
                
                # Safe canvas update
                try:
                    self.live_training_canvas.draw_idle()
                except Exception as canvas_error:
                    print(f"Canvas update error in live training plot refresh: {canvas_error}")
                
                print(f"Live training plot refreshed with {len(self.live_plot_epochs)} epochs")
            else:
                # Show placeholder if no training data
                self.live_training_ax.clear()
                self.live_training_ax.text(0.5, 0.5, 'No live training data available\nStart training to see real-time updates', 
                                      ha='center', va='center', transform=self.live_training_ax.transAxes,
                                      fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                self.live_training_ax.set_title("Live Training Progress")
                self.live_training_ax.set_xlabel("Epoch")
                self.live_training_ax.set_ylabel("Loss")
                self.live_training_ax.grid(True, alpha=0.3)
                
                if hasattr(self, 'live_training_status'):
                    self.live_training_status.config(text="No live training data available")
                
                try:
                    self.live_training_canvas.draw_idle()
                except Exception as canvas_error:
                    print(f"Canvas update error in live training plot refresh: {canvas_error}")
                
        except Exception as e:
            print(f"Error refreshing live training plot: {e}")
            import traceback
            traceback.print_exc()

    def load_3d_visualization_image_display(self, image_path):
        """Load and display 3D visualization image in the 3D display tab."""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Resize image to fit the canvas (75% of original size)
            img_width, img_height = img.size
            scale = 0.75
            new_size = (int(img_width * scale), int(img_height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array for matplotlib
            img_array = np.array(img)
            
            # Clear the 3D display axis and display the image
            self.gd3d_display_ax.clear()
            
            # Use imshow to display the image properly
            # The image array should be in the format (height, width, channels)
            if len(img_array.shape) == 3:  # RGB image
                self.gd3d_display_ax.imshow(img_array)
            else:  # Grayscale image
                self.gd3d_display_ax.imshow(img_array, cmap='gray')
            
            self.gd3d_display_ax.set_title(f"3D Gradient Descent Visualization\n{os.path.basename(image_path)}")
            self.gd3d_display_ax.axis('off')
            
            # Safe canvas update
            try:
                self.gd3d_display_canvas.draw_idle()
            except Exception as canvas_error:
                print(f"Canvas update error in 3D display visualization: {canvas_error}")
            
            print(f"Loaded 3D visualization image: {os.path.basename(image_path)} (resized to {new_size[0]}x{new_size[1]} - {scale*100}% of original)")
            
        except Exception as e:
            print(f"Error loading 3D visualization image: {e}")
            import traceback
            traceback.print_exc()

    def open_mpeg_file(self, file_path=None):
        """Open MPEG/GIF/MP4 file with system default player."""
        try:
            if file_path is None:
                # Open file dialog to select animation file
                file_path = filedialog.askopenfilename(
                    title="Select Animation File",
                    filetypes=[
                        ("Animation files", "*.mpeg *.mpg *.mp4 *.gif"),
                        ("MPEG files", "*.mpeg *.mpg *.mp4"),
                        ("GIF files", "*.gif"),
                        ("All files", "*.*")
                    ]
                )
            
            if not file_path:
                return
            
            if not os.path.exists(file_path):
                messagebox.showerror("File Not Found", f"File not found: {file_path}")
                return
            
            # Open with system default player
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", file_path])
            elif sys.platform == "win32":  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
            
            self.status_var.set(f"Opened animation file: {os.path.basename(file_path)}")
            print(f"Opened animation file: {file_path}")
            
        except Exception as e:
            error_msg = f"Error opening animation file: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)
            messagebox.showerror("Error", error_msg)

    def browse_mpeg_files(self):
        """Browse for animation files in model directories."""
        try:
            print(f"🔍 browse_mpeg_files() called")
            
            # Open directory browser to let user navigate to model directories
            initial_dir = self.current_model_dir if hasattr(self, 'current_model_dir') else "."
            
            # Ask user to select a directory (could be a model directory or plots subdirectory)
            selected_dir = filedialog.askdirectory(
                title="Browse for Animation Files - Select Model Directory or Plots Subdirectory",
                initialdir=initial_dir
            )
            
            if not selected_dir:
                print("❌ No directory selected")
                return
            
            print(f"📁 User selected directory: {selected_dir}")
            
            # Check if the selected directory is a plots subdirectory
            if os.path.basename(selected_dir) == 'plots':
                plots_path = selected_dir
                print(f"✅ User selected plots directory directly: {plots_path}")
            else:
                # Check if it's a model directory with a plots subdirectory
                plots_path = os.path.join(selected_dir, 'plots')
                if os.path.exists(plots_path):
                    print(f"✅ Found plots subdirectory in model: {plots_path}")
                else:
                    # Check if the selected directory itself contains animation files
                    plots_path = selected_dir
                    print(f"🔍 Checking selected directory for animation files: {plots_path}")
            
            # Look for animation files in the selected directory
            print(f"📂 Looking for animation files in: {plots_path}")
            
            if not os.path.exists(plots_path):
                print(f"❌ Directory does not exist: {plots_path}")
                messagebox.showinfo("Directory Not Found", f"Directory not found: {plots_path}")
                return
            
            print(f"✅ Directory exists: {plots_path}")
            
            animation_files = []
            for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
                files = glob.glob(os.path.join(plots_path, ext))
                if files:
                    print(f"🎬 Found {len(files)} files with extension {ext}:")
                    for f in files:
                        print(f"   📄 {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")
                animation_files.extend(files)
            
            print(f"🎬 Total animation files found: {len(animation_files)}")
            
            if not animation_files:
                print("❌ No animation files found")
                # List all files in directory for debugging
                all_files = os.listdir(plots_path)
                print(f"📋 All files in directory: {all_files}")
                
                # Show a more helpful message with suggestions
                message = f"No animation files found in:\n{plots_path}\n\n"
                message += "Suggestion: Navigate to a model directory (e.g., model_20250623_112543) "
                message += "and select its 'plots' subdirectory, or select the 'plots' directory directly."
                messagebox.showinfo("No Animation Files", message)
                return
            
            # If multiple files, let user choose
            if len(animation_files) == 1:
                print(f"🎯 Single animation file found, opening: {animation_files[0]}")
                self.open_mpeg_file(animation_files[0])
            else:
                print(f"🎯 Multiple animation files found, showing selector")
                # Create a simple file selection dialog
                self.show_mpeg_file_selector(animation_files)
                
        except Exception as e:
            error_msg = f"Error browsing animation files: {str(e)}"
            print(f"❌ {error_msg}")
            self.status_var.set(error_msg)
            messagebox.showerror("Error", error_msg)

    def show_mpeg_file_selector(self, animation_files):
        """Show a dialog to select from multiple animation files."""
        try:
            # Create a simple selection window
            selector_window = tk.Toplevel(self.root)
            selector_window.title("Select Animation File")
            selector_window.geometry("500x300")
            selector_window.transient(self.root)
            selector_window.grab_set()
            
            # Center the window
            selector_window.update_idletasks()
            x = (selector_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (selector_window.winfo_screenheight() // 2) - (300 // 2)
            selector_window.geometry(f"500x300+{x}+{y}")
            
            # Create frame
            main_frame = ttk.Frame(selector_window, padding="10")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Select Animation File:", 
                                   font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Create listbox with scrollbar
            listbox_frame = ttk.Frame(main_frame)
            listbox_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            listbox = tk.Listbox(listbox_frame, height=10)
            scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)
            
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Populate listbox
            for file_path in animation_files:
                listbox.insert(tk.END, os.path.basename(file_path))
            
            # Double-click to open
            def on_double_click(event):
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    file_path = animation_files[index]
                    selector_window.destroy()
                    self.open_mpeg_file(file_path)
            
            listbox.bind('<Double-Button-1>', on_double_click)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            def open_selected():
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    file_path = animation_files[index]
                    selector_window.destroy()
                    self.open_mpeg_file(file_path)
                else:
                    messagebox.showwarning("No Selection", "Please select a file to open.")
            
            def cancel():
                selector_window.destroy()
            
            ttk.Button(button_frame, text="Open Selected", command=open_selected).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Cancel", command=cancel).pack(side="left")
            
            # Select first item by default
            if animation_files:
                listbox.selection_set(0)
                listbox.see(0)
            
        except Exception as e:
            error_msg = f"Error creating file selector: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)

    def refresh_mpeg_files(self):
        """Refresh the list of available animation files."""
        try:
            print(f"🔄 refresh_mpeg_files() called")
            print(f"📁 Current selected_model_path: {self.selected_model_path}")
            
            if not self.selected_model_path:
                print("❌ No model selected")
                return
            
            # Look for animation files in the plots subdirectory
            plots_path = os.path.join(self.selected_model_path, 'plots')
            print(f"📂 Looking for animation files in: {plots_path}")
            
            if not os.path.exists(plots_path):
                print(f"❌ Plots directory does not exist: {plots_path}")
                return
            
            print(f"✅ Plots directory exists: {plots_path}")
            
            animation_files = []
            for ext in ['*.mpeg', '*.mpg', '*.mp4', '*.gif', '*.avi', '*.mov']:
                files = glob.glob(os.path.join(plots_path, ext))
                if files:
                    print(f"🎬 Found {len(files)} files with extension {ext}:")
                    for f in files:
                        print(f"   📄 {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")
                animation_files.extend(files)
            
            print(f"🎬 Total animation files found: {len(animation_files)}")
            
            # Update the MPEG files listbox if it exists
            if hasattr(self, 'mpeg_files_listbox'):
                print(f"📋 Updating mpeg_files_listbox with {len(animation_files)} files")
                self.mpeg_files_listbox.delete(0, tk.END)
                for file_path in animation_files:
                    filename = os.path.basename(file_path)
                    self.mpeg_files_listbox.insert(tk.END, filename)
                    print(f"   📝 Added to listbox: {filename}")
            else:
                print(f"⚠️  mpeg_files_listbox not found")
            
            self.status_var.set(f"Found {len(animation_files)} animation file(s)")
            print(f"Found {len(animation_files)} animation file(s): {[os.path.basename(f) for f in animation_files]}")
            
        except Exception as e:
            print(f"❌ Error refreshing animation files: {e}")
            import traceback
            traceback.print_exc()

    def on_mpeg_file_select(self, event):
        """Handle animation file selection from the listbox."""
        try:
            selection = self.mpeg_files_listbox.curselection()
            if selection:
                index = selection[0]
                filename = self.mpeg_files_listbox.get(index)
                file_path = os.path.join(self.selected_model_path, 'plots', filename)
                self.status_var.set(f"Selected animation file: {filename}")
                print(f"Selected animation file: {file_path}")
        except Exception as e:
            print(f"Error selecting animation file: {e}")

    def open_selected_mpeg(self):
        """Open the currently selected animation file."""
        try:
            selection = self.mpeg_files_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an animation file to open.")
                return
            
            index = selection[0]
            filename = self.mpeg_files_listbox.get(index)
            file_path = os.path.join(self.selected_model_path, 'plots', filename)
            
            if os.path.exists(file_path):
                self.open_mpeg_file(file_path)
            else:
                messagebox.showerror("File Not Found", f"File not found: {file_path}")
                
        except Exception as e:
            error_msg = f"Error opening selected animation file: {str(e)}"
            print(error_msg)
            self.status_var.set(error_msg)
            messagebox.showerror("Error", error_msg)

    def delete_selected_model(self):
        """Delete the selected model directory and all its contents."""
        import shutil
        if not self.selected_model_path:
            messagebox.showerror("No Model Selected", "Please select a model to delete.")
            return
        model_name = os.path.basename(self.selected_model_path)
        confirm = messagebox.askyesno(
            "Delete Model",
            f"Are you sure you want to delete the model '{model_name}' and all its files? This action cannot be undone.")
        if not confirm:
            return
        try:
            shutil.rmtree(self.selected_model_path)
            self.status_var.set(f"Deleted model: {model_name}")
            self.refresh_models()
            messagebox.showinfo("Model Deleted", f"Model '{model_name}' was deleted successfully.")
        except Exception as e:
            messagebox.showerror("Delete Failed", f"Failed to delete model '{model_name}': {e}")
            self.status_var.set(f"Failed to delete model: {model_name}")

    def load_3d_visualization_in_gui(self):
        """Load 3D gradient descent visualization directly into the GUI's 3D plot."""
        try:
            if not self.selected_model_path:
                print("❌ No model selected for 3D visualization")
                return
            
            print(f"🎬 Loading 3D visualization for model: {self.selected_model_path}")
            
            # Import the gradient descent visualizer
            from gradient_descent_3d import GradientDescentVisualizer
            
            # Create visualizer with current parameters
            visualizer = GradientDescentVisualizer(
                model_dir=self.selected_model_path,
                w1_range=(float(self.w1_range_min_var.get()), float(self.w1_range_max_var.get())),
                w2_range=(float(self.w2_range_min_var.get()), float(self.w2_range_max_var.get())),
                n_points=int(self.n_points_var.get()),
                view_elev=float(self.view_elev_var.get()),
                view_azim=float(self.view_azim_var.get()),
                color=self.color_var.get(),
                point_size=int(self.point_size_var.get()),
                line_width=int(self.line_width_var.get()),
                surface_alpha=float(self.surface_alpha_var.get()),
                w1_index=int(self.w1_index_var.get()),
                w2_index=int(self.w2_index_var.get())
            )
            
            # Ensure 3D axes are available before proceeding
            if not self.ensure_3d_axes_available():
                print("❌ Could not ensure 3D axes availability")
                return
            
            # Clear the current 3D plot
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax:
                self.gd3d_ax.clear()
                
                # Copy the surface and other elements from the visualizer
                # Plot the loss surface
                surface = self.gd3d_ax.plot_surface(visualizer.W1, visualizer.W2, visualizer.Z,
                                                  cmap=visualizer.color, alpha=0.8,
                                                  linewidth=0.5, antialiased=True)
                
                # Add colorbar only if gd3d_fig is available
                if hasattr(self, 'gd3d_fig') and self.gd3d_fig is not None:
                    try:
                        self.gd3d_fig.colorbar(surface, ax=self.gd3d_ax, shrink=0.5, aspect=5)
                    except Exception as colorbar_error:
                        print(f"Warning: Could not add colorbar: {colorbar_error}")
                else:
                    print("Warning: gd3d_fig not available, skipping colorbar")
                
                # Set labels and title
                self.gd3d_ax.set_xlabel(f'Weight 1 (Index {visualizer.w1_index})')
                self.gd3d_ax.set_ylabel(f'Weight 2 (Index {visualizer.w2_index})')
                self.gd3d_ax.set_zlabel('Loss')
                
                # Set view
                self.gd3d_ax.view_init(elev=visualizer.view_elev, azim=visualizer.view_azim)
                
                # Update the canvas
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas:
                    try:
                        self.gd3d_canvas.draw()
                    except Exception as canvas_error:
                        print(f"Warning: Could not update canvas: {canvas_error}")
                
                print(f"✅ 3D visualization loaded into GUI plot")
                print(f"   Surface shape: {visualizer.Z.shape}")
                print(f"   Z range: {np.min(visualizer.Z):.6f} to {np.max(visualizer.Z):.6f}")
                print(f"   Z std: {np.std(visualizer.Z):.6f}")
                
                # Store the visualizer for animation
                self.current_3d_visualizer = visualizer
                
            else:
                print("❌ 3D axes not available")
                
        except Exception as e:
            print(f"❌ Error loading 3D visualization: {e}")
            import traceback
            traceback.print_exc()

    def generate_mpeg_animation(self):
        """Generate MPEG animation for the selected model using gradient_descent_3d.py."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Model Selected", "Please select a model first.")
                return
            
            print(f"🎬 Generating MPEG animation for model: {self.selected_model_path}")
            self.status_var.set("Generating MPEG animation...")
            
            # Check if gradient_descent_3d.py exists
            script_path = "gradient_descent_3d.py"
            if os.path.exists(script_path):
                print(f"✅ Found gradient_descent_3d.py: {script_path}")
            else:
                print(f"❌ gradient_descent_3d.py not found at: {script_path}")
                messagebox.showerror("Error", f"gradient_descent_3d.py not found at {script_path}")
                return
            
            # Run the gradient descent 3D script with MPEG generation
            cmd = [sys.executable, script_path, "--model_dir", self.selected_model_path, "--save_mpeg"]
            
            print(f"Running command: {' '.join(cmd)}")
            
            # Run in a separate thread to avoid blocking the GUI
            def run_mpeg_generation():
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print("✅ MPEG animation generated successfully")
                        # Update the GUI on the main thread
                        self.root.after(0, lambda: self._mpeg_generation_completed_success())
                    else:
                        error_msg = f"MPEG generation failed: {result.stderr}"
                        print(f"❌ {error_msg}")
                        self.root.after(0, lambda: self._mpeg_generation_completed_error(error_msg))
                        
                except subprocess.TimeoutExpired:
                    error_msg = "MPEG generation timed out after 5 minutes"
                    print(f"❌ {error_msg}")
                    self.root.after(0, lambda: self._mpeg_generation_completed_error(error_msg))
                except Exception as e:
                    error_msg = f"MPEG generation error: {str(e)}"
                    print(f"❌ {error_msg}")
                    self.root.after(0, lambda: self._mpeg_generation_completed_error(error_msg))
            
            # Start the thread
            import threading
            thread = threading.Thread(target=run_mpeg_generation, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error starting MPEG generation: {e}")
            messagebox.showerror("Error", f"Error starting MPEG generation: {str(e)}")
    
    def _mpeg_generation_completed_success(self):
        """Handle successful MPEG generation."""
        try:
            self.status_var.set("MPEG animation generated successfully!")
            messagebox.showinfo("Success", "MPEG animation generated successfully!\nCheck the model's plots directory for the animation file.")
            
            # Refresh the MPEG files list
            self.refresh_mpeg_files()
            
        except Exception as e:
            print(f"Error in MPEG generation success handler: {e}")
    
    def _mpeg_generation_completed_error(self, error_msg):
        """Handle MPEG generation error."""
        try:
            self.status_var.set(f"MPEG generation failed: {error_msg}")
            messagebox.showerror("MPEG Generation Error", f"Failed to generate MPEG animation:\n{error_msg}")
            
        except Exception as e:
            print(f"Error in MPEG generation error handler: {e}")

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = StockPredictionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
        