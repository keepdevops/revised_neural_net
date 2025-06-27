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
        # Path history for dropdown lists (must be initialized first)
        self.data_file_history = []  # List of previously used data file paths
        self.output_dir_history = []  # List of previously used output directories
        self.max_history_size = 10  # Maximum number of items to remember
        
        # Load path history from file
        self._load_path_history()
        
        # Feature locking variables (must be before setup_main_window)
        self.lock_status_var = tk.StringVar(value="Features unlocked")
        self.feature_status_var = tk.StringVar(value="No features selected")
        self.features_locked = False
        self.locked_features = []
        
        # Training parameter variables (must be before setup_main_window)
        self.epochs_var = tk.StringVar(value="100")
        self.validation_split_var = tk.StringVar(value="0.2")
        self.early_stopping_patience_var = tk.StringVar(value="10")
        self.patience_var = tk.StringVar(value="10")  # Alias for control panel
        self.history_save_interval_var = tk.StringVar(value="10")
        self.history_interval_var = tk.StringVar(value="10")  # Alias for control panel
        self.random_seed_var = tk.StringVar(value="42")
        self.save_history_var = tk.BooleanVar(value=True)
        self.memory_optimization_var = tk.BooleanVar(value=False)
        self.memory_opt_var = tk.BooleanVar(value=False)  # Alias for control panel
        self.progress_reporting_interval_var = tk.StringVar(value="10")
        
        # Data file size variables
        self.data_file_size_var = tk.StringVar(value="File size: N/A")
        self.data_memory_size_var = tk.StringVar(value="Loaded size: N/A")
        
        # MPEG generation variables
        self.mpeg_status_var = tk.StringVar(value="Ready to generate MPEG")
        
        self.root = root
        self.root.title("Stock Prediction Neural Network GUI")
        self.root.geometry("1400x900")
        
        # Training parameter variables
        self.learning_rate_var = tk.StringVar(value="0.001")  # Default learning rate
        self.batch_size_var = tk.StringVar(value="32")        # Default batch size

        # Set the model directory to the project root (where model_* folders are)
        self.current_model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Add missing variables that are referenced in control panel
        self.data_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.hidden_size_var = tk.StringVar(value="64")
        self.vis_type_var = tk.StringVar(value="Wireframe")
        
        # Feature selection variables
        self.feature_vars = {}
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")  # Status bar variable
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

        self.setup_main_window()
        
        # Initialize variables
        self.data_file = None
        self.output_dir = None
        self.selected_model_path = None
        self.training_process = None
        self.visualization_process = None

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
            
            # Clean up Tkinter variables to prevent garbage collection errors
            self._cleanup_tkinter_variables()
            
            # Destroy the root window
            if hasattr(self, 'root'):
                self.root.destroy()
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force destroy even if cleanup fails
            if hasattr(self, 'root'):
                self.root.destroy()

    def _cleanup_tkinter_variables(self):
        """Clean up tkinter variables to prevent memory leaks."""
        try:
            # Clean up all tkinter variables
            for var_name in dir(self):
                var = getattr(self, var_name)
                if isinstance(var, (tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar)):
                    try:
                        var.set("")
                    except:
                        pass
        except Exception as e:
            print(f"Error cleaning up tkinter variables: {e}")

    def setup_main_window(self):
        """Setup the main window and create all UI components."""
        try:
            print("🏗️ Setting up main window...")
            
            # Configure the main window
            self.root.title("Stock Prediction Neural Network GUI")
            self.root.configure(bg=BACKGROUND_COLOR)
            self.root.minsize(1200, 800)
            
            # Set window icon if available
            try:
                # You can add an icon file here if you have one
                pass
            except:
                pass
            
            # Create main menu
            self.create_menu()
            
            # Create main frame using grid geometry manager
            main_frame = ttk.Frame(self.root)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            main_frame.grid_columnconfigure(1, weight=1)  # Right side (display panel) gets more space
            main_frame.grid_rowconfigure(0, weight=1)
            
            # Configure root grid weights
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            
            # Create control panel (left side)
            self.create_control_panel(main_frame)
            
            # Create display panel (right side)
            self.create_display_panel(main_frame)
            
            # Create status bar
            self.create_status_bar()
            
            # Initialize 3D visualization variables
            self.initialize_3d_variables()
            
            # Load path history
            self._load_path_history()
            
            # Test script availability
            self.test_script_availability()
            
            print("✅ Main window setup completed")
            
        except Exception as e:
            print(f"❌ Error setting up main window: {e}")
            import traceback
            traceback.print_exc()

    def create_menu(self):
        """Create the main menu bar."""
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)
            
            # File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Exit", command=self.on_closing)
            
            # Help menu
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="About", command=self.show_about)
            
        except Exception as e:
            print(f"Error creating menu: {e}")

    def create_control_panel(self, parent):
        """Create the control panel on the left side."""
        try:
            self.control_panel = ControlPanel(parent, self)
            self.control_panel.frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            print("✅ Control panel created")
        except Exception as e:
            print(f"❌ Error creating control panel: {e}")
            import traceback
            traceback.print_exc()

    def create_display_panel(self, parent):
        """Create the display panel on the right side."""
        try:
            self.display_panel = DisplayPanel(parent, self)
            self.display_panel.frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
            print("✅ Display panel created")
        except Exception as e:
            print(f"❌ Error creating display panel: {e}")
            import traceback
            traceback.print_exc()

    def create_status_bar(self):
        """Create the status bar at the bottom."""
        try:
            status_frame = ttk.Frame(self.root)
            status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
            
            self.status_var = tk.StringVar(value="Ready")
            status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
            status_label.pack(fill=tk.X)
            
            print("✅ Status bar created")
        except Exception as e:
            print(f"Error creating status bar: {e}")

    def initialize_3d_variables(self):
        """Initialize 3D visualization variables."""
        try:
            # 3D view control variables
            self.x_rotation_var = tk.DoubleVar(value=0.0)
            self.y_rotation_var = tk.DoubleVar(value=0.0)
            self.z_rotation_var = tk.DoubleVar(value=0.0)
            self.zoom_var = tk.DoubleVar(value=1.0)
            self.view_elev_var = tk.DoubleVar(value=30.0)
            self.view_azim_var = tk.DoubleVar(value=45.0)
            
            # 3D animation variables
            self.frame_pos_var = tk.IntVar(value=0)
            self.anim_speed_var = tk.DoubleVar(value=1.0)
            self.frame_rate_var = tk.IntVar(value=30)
            self.loop_mode_var = tk.StringVar(value="loop")
            self.playback_dir_var = tk.StringVar(value="forward")
            self.autoplay_var = tk.BooleanVar(value=False)
            self.anim_progress_var = tk.DoubleVar(value=0.0)
            
            # 3D plot control variables
            self.w1_range_min_var = tk.StringVar(value="-2.0")
            self.w1_range_max_var = tk.StringVar(value="2.0")
            self.w2_range_min_var = tk.StringVar(value="-2.0")
            self.w2_range_max_var = tk.StringVar(value="2.0")
            self.n_points_var = tk.StringVar(value="20")
            self.color_var = tk.StringVar(value="viridis")
            
            print("✅ 3D variables initialized")
        except Exception as e:
            print(f"Error initializing 3D variables: {e}")

    def show_about(self):
        """Show the about dialog."""
        try:
            about_text = """
Stock Prediction Neural Network GUI
Version 1.0

A comprehensive GUI for training and visualizing neural networks
for stock price prediction with advanced 3D visualizations.

Features:
- Data loading and preprocessing
- Neural network training
- Real-time training visualization
- 3D gradient descent visualization
- Multiple plot types (Wireframe, Surface, Contour, etc.)
- Animation generation (MPEG/GIF)
- Model management
            """
            messagebox.showinfo("About", about_text)
        except Exception as e:
            print(f"Error showing about dialog: {e}")

    def test_script_availability(self):
        """Test if required scripts are available."""
        try:
            scripts_to_test = [
                "visualization/gradient_descent_3d.py",
                "script_launcher.py"
            ]
            
            for script in scripts_to_test:
                if os.path.exists(script):
                    print(f"✅ Found script: {script}")
                else:
                    print(f"⚠️ Missing script: {script}")
                    
        except Exception as e:
            print(f"Error testing script availability: {e}")

    def update_3d_plot_type(self):
        """Update the 3D plot based on the selected visualization type."""
        try:
            plot_type = self.vis_type_var.get()
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                ax = self.gd3d_ax
                ax.clear()
                
                # Get the current color map
                selected_color = self.color_var.get()
                print(f"🎨 Using color map: {selected_color}")
                
                # Get dynamic W1 and W2 ranges from controls
                w1_min = float(self.w1_range_min_var.get())
                w1_max = float(self.w1_range_max_var.get())
                w2_min = float(self.w2_range_min_var.get())
                w2_max = float(self.w2_range_max_var.get())
                n_points = int(self.n_points_var.get())
                
                print(f"📊 Using W1 range: {w1_min} to {w1_max}")
                print(f"📊 Using W2 range: {w2_min} to {w2_max}")
                print(f"📊 Using {n_points} points")
                
                # Create meshgrid with dynamic ranges
                import numpy as np
                X = np.linspace(w1_min, w1_max, n_points)
                Y = np.linspace(w2_min, w2_max, n_points)
                X, Y = np.meshgrid(X, Y)
                
                # Create Z values based on the weight space (example function)
                # This could be replaced with actual loss surface calculation
                Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-(X**2 + Y**2) / 10)
                
                if plot_type == "Wireframe":
                    try:
                        import importlib
                        wireframe_mod = importlib.import_module("visualizations.wireframe_plot")
                        # Use the selected color map for the wireframe
                        wireframe_mod.plot_wireframe(ax, X, Y, Z, color=selected_color, alpha=0.7)
                        ax.set_title(f"3D Wireframe Plot - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        print(f"✅ Wireframe plotted with color: {selected_color}")
                    except ImportError as e:
                        print(f"⚠️ Wireframe module not found: {e}")
                        # Fallback to matplotlib wireframe if module not found
                        ax.plot_wireframe(X, Y, Z, color=selected_color, alpha=0.7)
                        ax.set_title(f"3D Wireframe Plot (Fallback) - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        print(f"✅ Fallback wireframe plotted with color: {selected_color}")
                    except Exception as e:
                        print(f"❌ Error plotting wireframe: {e}")
                        # Final fallback
                        ax.plot_wireframe(X, Y, Z, color='red', alpha=0.5)
                        ax.set_title("3D Wireframe Plot (Error Fallback)")
                        ax.set_xlabel("W1")
                        ax.set_ylabel("W2")
                        ax.set_zlabel("Loss")
                
                elif plot_type == "Surface":
                    try:
                        surface = ax.plot_surface(X, Y, Z, cmap=selected_color, alpha=0.8, linewidth=0.5, antialiased=True)
                        ax.set_title(f"3D Surface Plot - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        # Add colorbar
                        if hasattr(self, 'gd3d_fig') and self.gd3d_fig is not None:
                            self.gd3d_fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
                        print(f"✅ Surface plotted with color: {selected_color}")
                    except Exception as e:
                        print(f"❌ Error plotting surface: {e}")
                        ax.plot_surface(X, Y, Z, color='red', alpha=0.5)
                        ax.set_title("3D Surface Plot (Error Fallback)")
                        ax.set_xlabel("W1")
                        ax.set_ylabel("W2")
                        ax.set_zlabel("Loss")
                
                elif plot_type == "Contour":
                    try:
                        contour = ax.contour(X, Y, Z, levels=20, cmap=selected_color, alpha=0.8)
                        ax.set_title(f"3D Contour Plot - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        # Add contour labels
                        ax.clabel(contour, inline=True, fontsize=8)
                        print(f"✅ Contour plotted with color: {selected_color}")
                    except Exception as e:
                        print(f"❌ Error plotting contour: {e}")
                        ax.contour(X, Y, Z, levels=10, colors='red', alpha=0.5)
                        ax.set_title("3D Contour Plot (Error Fallback)")
                        ax.set_xlabel("W1")
                        ax.set_ylabel("W2")
                        ax.set_zlabel("Loss")
                
                elif plot_type == "Scatter":
                    try:
                        # Create scatter plot with sample points
                        n_scatter = min(1000, n_points * n_points)
                        indices = np.random.choice(n_points * n_points, n_scatter, replace=False)
                        x_scatter = X.flatten()[indices]
                        y_scatter = Y.flatten()[indices]
                        z_scatter = Z.flatten()[indices]
                        
                        scatter = ax.scatter(x_scatter, y_scatter, z_scatter, c=z_scatter, cmap=selected_color, 
                                           s=20, alpha=0.7, edgecolors='black', linewidth=0.5)
                        ax.set_title(f"3D Scatter Plot - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        # Add colorbar
                        if hasattr(self, 'gd3d_fig') and self.gd3d_fig is not None:
                            self.gd3d_fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=5)
                        print(f"✅ Scatter plotted with color: {selected_color}")
                    except Exception as e:
                        print(f"❌ Error plotting scatter: {e}")
                        ax.scatter(X.flatten()[:100], Y.flatten()[:100], Z.flatten()[:100], 
                                 color='red', alpha=0.5, s=20)
                        ax.set_title("3D Scatter Plot (Error Fallback)")
                        ax.set_xlabel("W1")
                        ax.set_ylabel("W2")
                        ax.set_zlabel("Loss")
                
                elif plot_type == "Bar3D":
                    try:
                        # Create bar3d plot with sample data
                        x_bars = X[::2, ::2].flatten()
                        y_bars = Y[::2, ::2].flatten()
                        z_bars = Z[::2, ::2].flatten()
                        
                        # Create bar dimensions
                        dx = (w1_max - w1_min) / (n_points * 2)
                        dy = (w2_max - w2_min) / (n_points * 2)
                        dz = np.abs(z_bars)
                        
                        # Normalize colors
                        norm = plt.Normalize(z_bars.min(), z_bars.max())
                        colors = plt.cm.get_cmap(selected_color)(norm(z_bars))
                        
                        ax.bar3d(x_bars, y_bars, np.zeros_like(z_bars), dx, dy, dz, 
                               color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
                        ax.set_title(f"3D Bar Plot - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        print(f"✅ Bar3D plotted with color: {selected_color}")
                    except Exception as e:
                        print(f"❌ Error plotting bar3d: {e}")
                        ax.bar3d(X.flatten()[:50], Y.flatten()[:50], np.zeros(50), 
                               0.1, 0.1, np.abs(Z.flatten()[:50]), color='red', alpha=0.5)
                        ax.set_title("3D Bar Plot (Error Fallback)")
                        ax.set_xlabel("W1")
                        ax.set_ylabel("W2")
                        ax.set_zlabel("Loss")
                
                elif plot_type == "Trisurf":
                    try:
                        # Create triangulated surface
                        from matplotlib.tri import Triangulation
                        tri = Triangulation(X.flatten(), Y.flatten())
                        ax.plot_trisurf(X.flatten(), Y.flatten(), Z.flatten(), 
                                      triangles=tri.triangles, cmap=selected_color, alpha=0.8)
                        ax.set_title(f"3D Triangulated Surface - {selected_color}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                        ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                        ax.set_zlabel("Loss")
                        print(f"✅ Trisurf plotted with color: {selected_color}")
                    except Exception as e:
                        print(f"❌ Error plotting trisurf: {e}")
                        ax.plot_trisurf(X.flatten(), Y.flatten(), Z.flatten(), color='red', alpha=0.5)
                        ax.set_title("3D Triangulated Surface (Error Fallback)")
                        ax.set_xlabel("W1")
                        ax.set_ylabel("W2")
                        ax.set_zlabel("Loss")
                
                elif plot_type == "Voxels":
                    try:
                        # For voxels, we need 3D data, so let's create a simple example
                        voxel_data = np.zeros((10, 10, 10))
                        for i in range(10):
                            for j in range(10):
                                for k in range(10):
                                    if np.sqrt(i**2 + j**2 + k**2) < 7:
                                        voxel_data[i, j, k] = 1
                        
                        # Use a proper color for voxels instead of colormap name
                        ax.voxels(voxel_data, facecolors='lightblue', alpha=0.3, edgecolor='black')
                        ax.set_title(f"3D Voxel Plot - Sample Voxel Data")
                        ax.set_xlabel("X")
                        ax.set_ylabel("Y")
                        ax.set_zlabel("Z")
                        print(f"✅ Voxels plotted with color: lightblue")
                    except Exception as e:
                        print(f"❌ Error plotting voxels: {e}")
                        # Fallback to simple cube
                        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                        
                        # Create a simple cube
                        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                                           [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
                        faces = [[vertices[0], vertices[1], vertices[2], vertices[3]],
                               [vertices[4], vertices[5], vertices[6], vertices[7]],
                               [vertices[0], vertices[1], vertices[5], vertices[4]],
                               [vertices[2], vertices[3], vertices[7], vertices[6]],
                               [vertices[1], vertices[2], vertices[6], vertices[5]],
                               [vertices[4], vertices[7], vertices[3], vertices[0]]]
                        
                        poly3d = Poly3DCollection(faces, alpha=0.3, facecolor='red', edgecolor='black')
                        ax.add_collection3d(poly3d)
                        ax.set_xlim([0, 1])
                        ax.set_ylim([0, 1])
                        ax.set_zlim([0, 1])
                        ax.set_title("3D Voxel Plot (Error Fallback)")
                        ax.set_xlabel("X")
                        ax.set_ylabel("Y")
                        ax.set_zlabel("Z")
                
                else:
                    # Default fallback
                    ax.plot_wireframe(X, Y, Z, color='blue', alpha=0.7)
                    ax.set_title(f"3D Plot - {plot_type}\nW1: [{w1_min:.2f}, {w1_max:.2f}] W2: [{w2_min:.2f}, {w2_max:.2f}]")
                    ax.set_xlabel(f"W1 [{w1_min:.2f}, {w1_max:.2f}]")
                    ax.set_ylabel(f"W2 [{w2_min:.2f}, {w2_max:.2f}]")
                    ax.set_zlabel("Loss")
                    print(f"⚠️ Unknown plot type '{plot_type}', using fallback")
                
                if hasattr(self, 'gd3d_canvas') and self.gd3d_canvas is not None:
                    self.gd3d_canvas.draw_idle()
                    
                self.status_var.set(f"Updated 3D plot to {plot_type} with {selected_color} (W1: [{w1_min:.2f}, {w1_max:.2f}], W2: [{w2_min:.2f}, {w2_max:.2f}])")
                print(f"✅ Updated 3D plot to {plot_type} with color {selected_color}")
                
        except Exception as e:
            print(f"Error updating 3D plot type: {e}")
            self.status_var.set(f"Error updating plot: {str(e)}")

    def generate_mpeg_animation(self):
        """Generate MPEG animation for the selected model using gradient_descent_3d.py."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Model Selected", "Please select a model first.")
                return
            
            print(f"🎬 Generating MPEG animation for model: {self.selected_model_path}")
            self.status_var.set("Generating MPEG animation...")
            
            # Start the progress bar
            if hasattr(self, 'mpeg_progress_bar') and self.mpeg_progress_bar is not None:
                try:
                    self.mpeg_progress_bar.start(10)  # Start with 10ms interval
                    if hasattr(self, 'mpeg_status_var'):
                        self.mpeg_status_var.set("Generating MPEG animation...")
                    print("✅ MPEG progress bar started")
                except Exception as e:
                    print(f"⚠️ Could not start progress bar: {e}")
            
            # Check if gradient_descent_3d.py exists
            script_path = "visualization/gradient_descent_3d.py"
            if os.path.exists(script_path):
                print(f"✅ Found gradient_descent_3d.py: {script_path}")
            else:
                print(f"❌ gradient_descent_3d.py not found at: {script_path}")
                messagebox.showerror("Error", f"gradient_descent_3d.py not found at {script_path}")
                # Stop progress bar on error
                if hasattr(self, 'mpeg_progress_bar') and self.mpeg_progress_bar is not None:
                    try:
                        self.mpeg_progress_bar.stop()
                        if hasattr(self, 'mpeg_status_var'):
                            self.mpeg_status_var.set("MPEG generation failed")
                    except:
                        pass
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
            # Stop progress bar on error
            if hasattr(self, 'mpeg_progress_bar') and self.mpeg_progress_bar is not None:
                try:
                    self.mpeg_progress_bar.stop()
                    if hasattr(self, 'mpeg_status_var'):
                        self.mpeg_status_var.set("MPEG generation failed")
                except:
                    pass
    
    def _mpeg_generation_completed_success(self):
        """Handle successful MPEG generation."""
        try:
            # Stop the progress bar
            if hasattr(self, 'mpeg_progress_bar') and self.mpeg_progress_bar is not None:
                try:
                    self.mpeg_progress_bar.stop()
                    if hasattr(self, 'mpeg_status_var'):
                        self.mpeg_status_var.set("MPEG generation completed successfully!")
                    print("✅ MPEG progress bar stopped")
                except Exception as e:
                    print(f"⚠️ Could not stop progress bar: {e}")
            
            self.status_var.set("MPEG animation generated successfully!")
            messagebox.showinfo("Success", "MPEG animation generated successfully!\nCheck the model's plots directory for the animation file.")
            
            # Refresh the MPEG files list
            self.refresh_mpeg_files()
            
        except Exception as e:
            print(f"Error in MPEG generation success handler: {e}")
    
    def _mpeg_generation_completed_error(self, error_msg):
        """Handle MPEG generation error."""
        try:
            # Stop the progress bar
            if hasattr(self, 'mpeg_progress_bar') and self.mpeg_progress_bar is not None:
                try:
                    self.mpeg_progress_bar.stop()
                    if hasattr(self, 'mpeg_status_var'):
                        self.mpeg_status_var.set("MPEG generation failed")
                    print("✅ MPEG progress bar stopped")
                except Exception as e:
                    print(f"⚠️ Could not stop progress bar: {e}")
            
            self.status_var.set(f"MPEG generation failed: {error_msg}")
            messagebox.showerror("MPEG Generation Error", f"Failed to generate MPEG animation:\n{error_msg}")
            
        except Exception as e:
            print(f"Error in MPEG generation error handler: {e}")

    def update_live_training_tab(self, epoch, loss):
        """Update the Live Training Plot tab with new training data."""
        try:
            # Add new data point
            self.live_plot_epochs.append(epoch)
            self.live_plot_losses.append(loss)
            
            # Check if the Live Training Plot tab exists
            if not hasattr(self, 'live_training_ax') or self.live_training_ax is None:
                return
            
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
            
            # Update status with proper widget existence check
            if hasattr(self, 'live_training_status') and self.live_training_status is not None:
                try:
                    # Check if the widget is still valid (not destroyed)
                    if self.live_training_status.winfo_exists():
                        self.live_training_status.config(text=f"Live training: Epoch {epoch}, Loss {loss:.6f}")
                    else:
                        print("Live training status widget has been destroyed")
                except tk.TclError:
                    print("Live training status widget has been destroyed")
                except Exception as status_error:
                    print(f"Error updating live training status: {status_error}")
            
            # Safe canvas update
            try:
                if hasattr(self, 'live_training_canvas') and self.live_training_canvas is not None:
                    # Check if the canvas is still valid
                    try:
                        if self.live_training_canvas.winfo_exists():
                            self.live_training_canvas.draw_idle()
                        else:
                            print("Live training canvas has been destroyed")
                    except tk.TclError:
                        print("Live training canvas has been destroyed")
                    except Exception as canvas_error:
                        print(f"Canvas update error in live training tab: {canvas_error}")
            except Exception as canvas_error:
                print(f"Canvas update error in live training tab: {canvas_error}")
                
            print(f"Live Training Plot tab updated: Epoch {epoch}, Loss {loss:.6f}")
            
        except Exception as e:
            print(f"Error updating live training tab: {e}")
            import traceback
            traceback.print_exc()

    def on_data_file_combo_select(self, event=None):
        """Handle selection of a data file from the combobox."""
        print(f"🔄 on_data_file_combo_select() called with event: {event}")
        selected_file = self.data_file_var.get()
        print(f"📁 Selected file: {selected_file}")
        
        if selected_file:
            self.data_file = selected_file
            print(f"✅ Data file set to: {self.data_file}")
            
            # Load features from the selected file
            print("🔄 Triggering feature loading...")
            try:
                self.load_data_features()
                print("✅ load_data_features() completed successfully")
            except Exception as e:
                print(f"❌ Error in load_data_features(): {e}")
                import traceback
                traceback.print_exc()
            
            # Update status
            self.status_var.set(f"Selected data file: {os.path.basename(selected_file)}")
            print(f"✅ Data file selection completed for: {selected_file}")
        else:
            print("❌ No file selected")
            self.status_var.set("No file selected")

    def on_output_dir_combo_select(self, event=None):
        """Handle selection of an output directory from the combobox."""
        selected_dir = self.output_dir_var.get()
        if selected_dir:
            self.output_dir = selected_dir
            self.status_var.set(f"Selected output directory: {selected_dir}")

    def refresh_data_files(self):
        """Refresh the data file dropdown list by scanning for CSV files."""
        try:
            print("🔄 Refreshing data file list...")
            
            # Scan for CSV files in current directory
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            
            # Add any new files to history
            for file in csv_files:
                if file not in self.data_file_history:
                    self._add_to_history(self.data_file_history, file)
            
            # Update the combobox
            self._update_data_file_combo()
            
            # Update status
            self.status_var.set(f"Found {len(csv_files)} CSV files")
            print(f"✅ Found {len(csv_files)} CSV files: {csv_files}")
            
        except Exception as e:
            print(f"Error refreshing data files: {e}")
            self.status_var.set(f"Error refreshing data files: {str(e)}")

    def _update_data_file_combo(self):
        """Update the data file combobox with current history."""
        if hasattr(self, 'data_file_combo'):
            self.data_file_combo['values'] = self.data_file_history

    def _add_to_history(self, history_list, value):
        """Add a value to the history list if it's not already there."""
        if value and value not in history_list:
            history_list.insert(0, value)
            if len(history_list) > self.max_history_size:
                del history_list[self.max_history_size:]
            self._save_path_history()

    def _save_path_history(self):
        """Save the path history to a JSON file."""
        h = {
            "data_files": self.data_file_history[:self.max_history_size],
            "output_dirs": self.output_dir_history[:self.max_history_size]
        }
        try:
            with open(self._history_file(), "w") as f:
                json.dump(h, f, indent=2)
        except Exception as e:
            print("Could not save path history:", e)

    def _history_file(self):
        """Get the path to the history file."""
        return os.path.join(os.path.dirname(__file__), "path_history.json")

    def _load_path_history(self):
        """Load the path history from a JSON file."""
        try:
            with open(self._history_file(), "r") as f:
                h = json.load(f)
                self.data_file_history = h.get("data_files", [])
                self.output_dir_history = h.get("output_dirs", [])
        except Exception:
            self.data_file_history = []
            self.output_dir_history = []

    def on_color_map_change(self, event):
        """Handle color map change event."""
        try:
            selected_color = self.color_var.get()
            print(f"🎨 Color map changed to: {selected_color}")
            
            # Update the 3D plot if it exists
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                self.update_3d_plot_type()
            
            self.status_var.set(f"Color map changed to: {selected_color}")
            print(f"✅ Color map updated to: {selected_color}")
            
        except Exception as e:
            print(f"Error handling color map change: {e}")
            self.status_var.set("Error handling color map change")

    def on_w1_range_change(self, event):
        """Handle W1 range change event."""
        try:
            new_w1_min = float(self.w1_range_min_var.get())
            new_w1_max = float(self.w1_range_max_var.get())
            self.w1_range_min_var.set(f"{new_w1_min:.2f}")
            self.w1_range_max_var.set(f"{new_w1_max:.2f}")
            # Add a small delay to prevent too many rapid updates
            self.root.after(500, self.update_3d_plot_type)
        except ValueError:
            print(f"Invalid W1 range format: {self.w1_range_min_var.get()} to {self.w1_range_max_var.get()}")

    def on_w2_range_change(self, event):
        """Handle W2 range change event."""
        try:
            new_w2_min = float(self.w2_range_min_var.get())
            new_w2_max = float(self.w2_range_max_var.get())
            self.w2_range_min_var.set(f"{new_w2_min:.2f}")
            self.w2_range_max_var.set(f"{new_w2_max:.2f}")
            # Add a small delay to prevent too many rapid updates
            self.root.after(500, self.update_3d_plot_type)
        except ValueError:
            print(f"Invalid W2 range format: {self.w2_range_min_var.get()} to {self.w2_range_max_var.get()}")

    def on_n_points_change(self, event):
        """Handle N points change event."""
        try:
            new_n_points = int(self.n_points_var.get())
            self.n_points_var.set(f"{new_n_points}")
            # Add a small delay to prevent too many rapid updates
            self.root.after(500, self.update_3d_plot_type)
        except ValueError:
            print(f"Invalid N points format: {self.n_points_var.get()}")

    def refresh_models(self, load_plots=False):
        """Refresh the model list by scanning for model directories."""
        try:
            print("🔄 Refreshing model list...")
            
            # Scan for model directories (model_*)
            model_dirs = []
            for item in os.listdir(self.current_model_dir):
                if item.startswith('model_') and os.path.isdir(os.path.join(self.current_model_dir, item)):
                    model_dirs.append(item)
            
            # Sort by creation time (newest first)
            model_dirs.sort(key=lambda x: os.path.getctime(os.path.join(self.current_model_dir, x)), reverse=True)
            
            # Update the model combobox
            if hasattr(self, 'model_combo'):
                self.model_combo['values'] = model_dirs
                if model_dirs and not self.model_combo.get():
                    self.model_combo.set(model_dirs[0])
            
            self.status_var.set(f"Found {len(model_dirs)} models")
            print(f"✅ Found {len(model_dirs)} models: {model_dirs}")
            
        except Exception as e:
            print(f"Error refreshing models: {e}")
            self.status_var.set(f"Error refreshing models: {str(e)}")

    def browse_data_file(self):
        """Browse for a data file."""
        try:
            filename = filedialog.askopenfilename(
                title="Select Data File",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                self.data_file = filename
                self.data_file_var.set(filename)
                self._add_to_history(self.data_file_history, filename)
                self.load_data_features()
                self.status_var.set(f"Selected data file: {filename}")
        except Exception as e:
            print(f"Error browsing data file: {e}")
            messagebox.showerror("Error", f"Error browsing data file: {str(e)}")

    def browse_output_dir(self):
        """Browse for an output directory."""
        try:
            dirname = filedialog.askdirectory(title="Select Output Directory")
            if dirname:
                self.output_dir = dirname
                self.output_dir_var.set(dirname)
                self._add_to_history(self.output_dir_history, dirname)
                self.status_var.set(f"Selected output directory: {dirname}")
        except Exception as e:
            print(f"Error browsing output directory: {e}")
            messagebox.showerror("Error", f"Error browsing output directory: {str(e)}")

    def load_data_features(self):
        """Load features from the selected data file."""
        try:
            print(f"🔍 load_data_features() called with data_file: {self.data_file}")
            
            if not self.data_file or not os.path.exists(self.data_file):
                print(f"❌ Data file not found or not set: {self.data_file}")
                return
            
            print(f"📊 Loading features from: {self.data_file}")
            
            # Load the data to get column names
            try:
                df = pd.read_csv(self.data_file, nrows=1)  # Just read header
                features = list(df.columns)
                print(f"✅ Found {len(features)} features: {features}")
            except Exception as e:
                print(f"❌ Error reading CSV file: {e}")
                self.status_var.set(f"Error reading CSV file: {str(e)}")
                return
            
            # Update feature listbox
            print(f"🔍 Checking if feature_listbox exists: {hasattr(self, 'feature_listbox')}")
            if hasattr(self, 'feature_listbox'):
                print(f"🔄 Updating feature listbox with {len(features)} features")
                try:
                    self.feature_listbox.delete(0, tk.END)
                    for feature in features:
                        self.feature_listbox.insert(tk.END, feature)
                    print(f"✅ Feature listbox updated with {len(features)} features")
                except Exception as e:
                    print(f"❌ Error updating feature listbox: {e}")
            else:
                print("❌ feature_listbox not found")
            
            # Update target combo
            print(f"🔍 Checking if target_combo exists: {hasattr(self, 'target_combo')}")
            if hasattr(self, 'target_combo'):
                try:
                    self.target_combo['values'] = features
                    if features:
                        # Try to set a sensible default target
                        if 'close' in features:
                            self.target_combo.set('close')
                            print("🎯 Set target to 'close'")
                        elif 'price' in features:
                            self.target_combo.set('price')
                            print("🎯 Set target to 'price'")
                        else:
                            self.target_combo.set(features[-1])  # Default to last column
                            print(f"🎯 Set target to last column: {features[-1]}")
                    print("✅ Target combo updated")
                except Exception as e:
                    print(f"❌ Error updating target combo: {e}")
            else:
                print("❌ target_combo not found")
            
            self.status_var.set(f"Loaded {len(features)} features from {os.path.basename(self.data_file)}")
            print(f"✅ load_data_features() completed successfully")
            
        except Exception as e:
            print(f"❌ Error loading data features: {e}")
            import traceback
            traceback.print_exc()
            self.status_var.set(f"Error loading features: {str(e)}")

    def refresh_data_features(self):
        """Manually refresh the data features display."""
        try:
            print("🔄 Manually refreshing data features...")
            if self.data_file and os.path.exists(self.data_file):
                self.load_data_features()
            else:
                print("❌ No valid data file selected")
                self.status_var.set("No valid data file selected")
        except Exception as e:
            print(f"❌ Error refreshing data features: {e}")
            self.status_var.set(f"Error refreshing features: {str(e)}")

    def lock_features(self):
        """Lock the selected features."""
        try:
            if not hasattr(self, 'feature_listbox'):
                print("❌ Feature listbox not found")
                messagebox.showwarning("Error", "Feature listbox not found. Please select a data file first.")
                return
            
            selected_indices = self.feature_listbox.curselection()
            if not selected_indices:
                print("❌ No features selected")
                messagebox.showwarning("No Features Selected", "Please select features to lock.")
                return
            
            features = [self.feature_listbox.get(i) for i in selected_indices]
            print(f"🔒 Locking {len(features)} features: {features}")
            
            self.locked_features = features
            self.features_locked = True
            
            # Update status displays
            if hasattr(self, 'lock_status_var'):
                self.lock_status_var.set(f"Features locked: {', '.join(features)}")
            if hasattr(self, 'feature_status_var'):
                self.feature_status_var.set(f"Locked: {len(features)} features")
            
            self.status_var.set(f"Locked {len(features)} features")
            print(f"✅ Successfully locked {len(features)} features")
            
        except Exception as e:
            print(f"❌ Error locking features: {e}")
            messagebox.showerror("Error", f"Error locking features: {str(e)}")

    def unlock_features(self):
        """Unlock all features."""
        try:
            print("🔓 Unlocking all features...")
            
            self.locked_features = []
            self.features_locked = False
            
            # Update status displays
            if hasattr(self, 'lock_status_var'):
                self.lock_status_var.set("Features unlocked")
            if hasattr(self, 'feature_status_var'):
                self.feature_status_var.set("No features selected")
            
            self.status_var.set("All features unlocked")
            print("✅ Successfully unlocked all features")
            
        except Exception as e:
            print(f"❌ Error unlocking features: {e}")
            messagebox.showerror("Error", f"Error unlocking features: {str(e)}")

    def start_training(self):
        """Start the training process."""
        try:
            if not self.data_file:
                messagebox.showwarning("No Data File", "Please select a data file first.")
                return
            
            if not self.output_dir:
                messagebox.showwarning("No Output Directory", "Please select an output directory first.")
                return
            
            # Get training parameters
            hidden_size = int(self.hidden_size_var.get())
            learning_rate = float(self.learning_rate_var.get())
            batch_size = int(self.batch_size_var.get())
            epochs = int(self.epochs_var.get())
            
            print(f"🚀 Starting training with parameters:")
            print(f"   Data file: {self.data_file}")
            print(f"   Output dir: {self.output_dir}")
            print(f"   Hidden size: {hidden_size}")
            print(f"   Learning rate: {learning_rate}")
            print(f"   Batch size: {batch_size}")
            print(f"   Epochs: {epochs}")
            
            # Launch training using script_launcher
            launch_training(
                data_file=self.data_file,
                output_dir=self.output_dir,
                hidden_size=hidden_size,
                learning_rate=learning_rate,
                batch_size=batch_size,
                epochs=epochs
            )
            
            self.status_var.set("Training started")
            
        except Exception as e:
            print(f"Error starting training: {e}")
            messagebox.showerror("Error", f"Error starting training: {str(e)}")

    def start_live_training(self):
        """Start live training with real-time plot updates."""
        try:
            if not self.data_file:
                messagebox.showwarning("No Data File", "Please select a data file first.")
                return
            
            if not self.output_dir:
                messagebox.showwarning("No Output Directory", "Please select an output directory first.")
                return
            
            print("🚀 Starting live training...")
            self.status_var.set("Starting live training...")
            
            # Create live training window
            self.create_live_training_window()
            
            # Start training in background thread
            import threading
            thread = threading.Thread(target=self._run_live_training, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error starting live training: {e}")
            messagebox.showerror("Error", f"Error starting live training: {str(e)}")

    def create_live_training_window(self):
        """Create the live training plot window."""
        try:
            # Create new window for live training
            self.live_plot_window = tk.Toplevel(self.root)
            self.live_plot_window.title("Live Training Progress")
            self.live_plot_window.geometry("800x600")
            
            # Create matplotlib figure
            self.live_plot_fig = Figure(figsize=(10, 6))
            self.live_training_ax = self.live_plot_fig.add_subplot(111)
            
            # Create canvas
            self.live_training_canvas = FigureCanvasTkAgg(self.live_plot_fig, self.live_plot_window)
            self.live_training_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Create toolbar
            toolbar = NavigationToolbar2Tk(self.live_training_canvas, self.live_plot_window)
            toolbar.update()
            
            # Create status label
            self.live_plot_status = tk.Label(self.live_plot_window, text="Initializing...", font=("Arial", 12))
            self.live_plot_status.pack(pady=10)
            
            # Initialize plot data
            self.live_plot_epochs = []
            self.live_plot_losses = []
            
            self.live_plot_window_open = True
            
        except Exception as e:
            print(f"Error creating live training window: {e}")

    def _run_live_training(self):
        """Run the live training process."""
        try:
            # This would typically launch the training script and monitor its output
            # For now, we'll simulate training progress
            print("🔄 Running live training simulation...")
            
            for epoch in range(100):
                if not self.live_plot_window_open:
                    break
                
                # Simulate loss
                loss = 1.0 / (1 + epoch * 0.1) + 0.1 * np.random.random()
                
                # Update plot on main thread
                self.root.after(0, lambda e=epoch, l=loss: self.update_live_training_tab(e, l))
                
                time.sleep(0.1)  # Simulate training time
            
            print("✅ Live training completed")
            
        except Exception as e:
            print(f"Error in live training: {e}")

    def clear_cache_only(self):
        """Clear the image cache."""
        try:
            if hasattr(self, 'image_cache'):
                self.image_cache.clear()
                print("✅ Image cache cleared")
                self.status_var.set("Image cache cleared")
            else:
                print("⚠️ No image cache to clear")
                self.status_var.set("No cache to clear")
        except Exception as e:
            print(f"Error clearing cache: {e}")
            self.status_var.set(f"Error clearing cache: {str(e)}")

    def on_model_select(self, event=None):
        """Handle model selection."""
        try:
            selected_model = self.model_combo.get()
            if selected_model:
                self.selected_model_path = os.path.join(self.current_model_dir, selected_model)
                self.status_var.set(f"Selected model: {selected_model}")
                self.refresh_prediction_files()
                self.refresh_mpeg_files()
        except Exception as e:
            print(f"Error selecting model: {e}")

    def make_prediction(self):
        """Make a prediction using the selected model."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Model Selected", "Please select a model first.")
                return
            
            if not self.data_file:
                messagebox.showwarning("No Data File", "Please select a data file first.")
                return
            
            print(f"📊 Making prediction with model: {self.selected_model_path}")
            self.status_var.set("Making prediction...")
            
            # Launch prediction using script_launcher
            launch_prediction(
                model_dir=self.selected_model_path,
                data_file=self.data_file
            )
            
            self.status_var.set("Prediction completed")
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            messagebox.showerror("Error", f"Error making prediction: {str(e)}")

    def delete_selected_model(self):
        """Delete the selected model."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Model Selected", "Please select a model first.")
                return
            
            # Confirm deletion
            result = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete the model:\n{self.selected_model_path}?"
            )
            
            if result:
                shutil.rmtree(self.selected_model_path)
                self.status_var.set("Model deleted")
                self.refresh_models()
                
        except Exception as e:
            print(f"Error deleting model: {e}")
            messagebox.showerror("Error", f"Error deleting model: {str(e)}")

    def refresh_prediction_files(self):
        """Refresh the prediction files list."""
        try:
            if not self.selected_model_path:
                return
            
            prediction_files = []
            plots_dir = os.path.join(self.selected_model_path, "plots")
            if os.path.exists(plots_dir):
                for file in os.listdir(plots_dir):
                    if file.endswith('.csv') and 'prediction' in file.lower():
                        prediction_files.append(file)
            
            # Update listbox
            if hasattr(self, 'prediction_files_listbox'):
                self.prediction_files_listbox.delete(0, tk.END)
                for file in prediction_files:
                    self.prediction_files_listbox.insert(tk.END, file)
            
            self.status_var.set(f"Found {len(prediction_files)} prediction files")
            
        except Exception as e:
            print(f"Error refreshing prediction files: {e}")

    def on_prediction_file_select(self, event=None):
        """Handle prediction file selection."""
        try:
            if not hasattr(self, 'prediction_files_listbox'):
                return
            
            selection = self.prediction_files_listbox.curselection()
            if selection:
                filename = self.prediction_files_listbox.get(selection[0])
                self.selected_prediction_file = os.path.join(self.selected_model_path, "plots", filename)
                self.status_var.set(f"Selected prediction file: {filename}")
        except Exception as e:
            print(f"Error selecting prediction file: {e}")

    def view_prediction_results(self):
        """View the selected prediction results."""
        try:
            if not self.selected_prediction_file:
                messagebox.showwarning("No Prediction File", "Please select a prediction file first.")
                return
            
            # Load and display prediction results
            df = pd.read_csv(self.selected_prediction_file)
            
            # Create a simple display window
            display_window = tk.Toplevel(self.root)
            display_window.title("Prediction Results")
            display_window.geometry("600x400")
            
            # Create text widget
            text_widget = scrolledtext.ScrolledText(display_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Display results
            text_widget.insert(tk.END, f"Prediction Results from: {os.path.basename(self.selected_prediction_file)}\n")
            text_widget.insert(tk.END, "=" * 50 + "\n\n")
            text_widget.insert(tk.END, df.to_string())
            
            self.status_var.set("Prediction results displayed")
            
        except Exception as e:
            print(f"Error viewing prediction results: {e}")
            messagebox.showerror("Error", f"Error viewing prediction results: {str(e)}")

    def toggle_right_panel(self):
        """Toggle the right panel visibility."""
        try:
            if hasattr(self, 'display_panel'):
                if self.display_panel.frame.winfo_viewable():
                    self.display_panel.frame.pack_forget()
                    self.status_var.set("Right panel hidden")
                else:
                    self.display_panel.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                    self.status_var.set("Right panel shown")
        except Exception as e:
            print(f"Error toggling right panel: {e}")

    def show_right_panel(self):
        """Show the right panel."""
        try:
            if hasattr(self, 'display_panel'):
                self.display_panel.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                self.status_var.set("Right panel shown")
        except Exception as e:
            print(f"Error showing right panel: {e}")

    def show_3d_controls(self):
        """Show the floating 3D controls window."""
        try:
            # Create floating 3D controls window
            controls_window = tk.Toplevel(self.root)
            controls_window.title("3D Visualization Controls")
            controls_window.geometry("400x600")
            
            # Add 3D control widgets here
            # This is a placeholder - you can expand this as needed
            
            self.status_var.set("3D controls window opened")
            
        except Exception as e:
            print(f"Error showing 3D controls: {e}")

    def reset_3d_view(self):
        """Reset the 3D view to default."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                self.gd3d_ax.view_init(elev=30, azim=45)
                if hasattr(self, 'gd3d_canvas'):
                    self.gd3d_canvas.draw_idle()
                self.status_var.set("3D view reset")
        except Exception as e:
            print(f"Error resetting 3D view: {e}")

    def set_top_view(self):
        """Set the 3D view to top view."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                self.gd3d_ax.view_init(elev=90, azim=0)
                if hasattr(self, 'gd3d_canvas'):
                    self.gd3d_canvas.draw_idle()
                self.status_var.set("3D view set to top")
        except Exception as e:
            print(f"Error setting top view: {e}")

    def set_side_view(self):
        """Set the 3D view to side view."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                self.gd3d_ax.view_init(elev=0, azim=0)
                if hasattr(self, 'gd3d_canvas'):
                    self.gd3d_canvas.draw_idle()
                self.status_var.set("3D view set to side")
        except Exception as e:
            print(f"Error setting side view: {e}")

    def set_isometric_view(self):
        """Set the 3D view to isometric view."""
        try:
            if hasattr(self, 'gd3d_ax') and self.gd3d_ax is not None:
                self.gd3d_ax.view_init(elev=30, azim=45)
                if hasattr(self, 'gd3d_canvas'):
                    self.gd3d_canvas.draw_idle()
                self.status_var.set("3D view set to isometric")
        except Exception as e:
            print(f"Error setting isometric view: {e}")

    def browse_mpeg_files(self):
        """Browse for MPEG files in model directories."""
        try:
            # Open file dialog to select a model directory
            model_dir = filedialog.askdirectory(
                title="Select Model Directory",
                initialdir=self.current_model_dir
            )
            
            if model_dir:
                # Look for animation files in the plots subdirectory
                plots_dir = os.path.join(model_dir, "plots")
                if os.path.exists(plots_dir):
                    self.refresh_mpeg_files_from_dir(plots_dir)
                else:
                    messagebox.showinfo("No Plots Directory", "No 'plots' directory found in the selected model directory.")
            
        except Exception as e:
            print(f"Error browsing MPEG files: {e}")
            messagebox.showerror("Error", f"Error browsing MPEG files: {str(e)}")

    def refresh_mpeg_files(self):
        """Refresh the MPEG files list."""
        try:
            if self.selected_model_path:
                plots_dir = os.path.join(self.selected_model_path, "plots")
                if os.path.exists(plots_dir):
                    self.refresh_mpeg_files_from_dir(plots_dir)
            else:
                # Clear the listbox
                if hasattr(self, 'mpeg_files_listbox'):
                    self.mpeg_files_listbox.delete(0, tk.END)
                    self.mpeg_files_listbox.insert(tk.END, "No model selected")
        except Exception as e:
            print(f"Error refreshing MPEG files: {e}")

    def refresh_mpeg_files_from_dir(self, plots_dir):
        """Refresh MPEG files from a specific directory."""
        try:
            animation_files = []
            for file in os.listdir(plots_dir):
                if file.lower().endswith(('.mp4', '.mpeg', '.mpg', '.gif', '.avi')):
                    animation_files.append(file)
            
            # Update listbox
            if hasattr(self, 'mpeg_files_listbox'):
                self.mpeg_files_listbox.delete(0, tk.END)
                if animation_files:
                    for file in animation_files:
                        self.mpeg_files_listbox.insert(tk.END, file)
                else:
                    self.mpeg_files_listbox.insert(tk.END, "No animation files found")
            
            self.status_var.set(f"Found {len(animation_files)} animation files")
            
        except Exception as e:
            print(f"Error refreshing MPEG files from directory: {e}")

    def on_mpeg_file_select(self, event=None):
        """Handle MPEG file selection."""
        try:
            if not hasattr(self, 'mpeg_files_listbox'):
                return
            
            selection = self.mpeg_files_listbox.curselection()
            if selection:
                filename = self.mpeg_files_listbox.get(selection[0])
                if filename != "No animation files found" and filename != "No model selected":
                    # Determine the full path
                    if self.selected_model_path:
                        file_path = os.path.join(self.selected_model_path, "plots", filename)
                    else:
                        # Try to find the file in any model directory
                        file_path = self.find_animation_file(filename)
                    
                    if file_path and os.path.exists(file_path):
                        self.selected_mpeg_file = file_path
                        self.status_var.set(f"Selected animation: {filename}")
                    else:
                        self.status_var.set(f"Animation file not found: {filename}")
        except Exception as e:
            print(f"Error selecting MPEG file: {e}")

    def find_animation_file(self, filename):
        """Find an animation file in any model directory."""
        try:
            for item in os.listdir(self.current_model_dir):
                if item.startswith('model_') and os.path.isdir(os.path.join(self.current_model_dir, item)):
                    plots_dir = os.path.join(self.current_model_dir, item, "plots")
                    if os.path.exists(plots_dir):
                        file_path = os.path.join(plots_dir, filename)
                        if os.path.exists(file_path):
                            return file_path
            return None
        except Exception as e:
            print(f"Error finding animation file: {e}")
            return None

    def open_selected_mpeg(self):
        """Open the selected MPEG file."""
        try:
            if not hasattr(self, 'selected_mpeg_file') or not self.selected_mpeg_file:
                messagebox.showwarning("No Animation Selected", "Please select an animation file first.")
                return
            
            if not os.path.exists(self.selected_mpeg_file):
                messagebox.showerror("File Not Found", f"Animation file not found:\n{self.selected_mpeg_file}")
                return
            
            # Open the file with the default system application
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", self.selected_mpeg_file])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["start", self.selected_mpeg_file], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", self.selected_mpeg_file])
            
            self.status_var.set(f"Opened animation: {os.path.basename(self.selected_mpeg_file)}")
            
        except Exception as e:
            print(f"Error opening MPEG file: {e}")
            messagebox.showerror("Error", f"Error opening animation file: {str(e)}")

    def get_ticker_from_filename(self):
        """Extract ticker symbol from filename."""
        try:
            if self.data_file:
                return path_utils.get_ticker_from_filename(self.data_file)
            return "Unknown"
        except Exception as e:
            print(f"Error getting ticker from filename: {e}")
            return "Unknown"

    def update_prediction_results(self):
        """Update the prediction results display."""
        try:
            if not self.selected_model_path:
                self.pred_status_label.config(text="No model selected")
                return
            
            # Look for prediction files in the model's plots directory
            plots_dir = os.path.join(self.selected_model_path, "plots")
            if not os.path.exists(plots_dir):
                self.pred_status_label.config(text="No plots directory found")
                return
            
            prediction_files = []
            for file in os.listdir(plots_dir):
                if file.endswith('.csv') and 'prediction' in file.lower():
                    prediction_files.append(file)
            
            if not prediction_files:
                self.pred_status_label.config(text="No prediction files found")
                return
            
            # Load the most recent prediction file
            latest_pred_file = sorted(prediction_files)[-1]
            pred_file_path = os.path.join(plots_dir, latest_pred_file)
            
            # Load and display prediction results
            df = pd.read_csv(pred_file_path)
            
            # Clear the plot
            self.pred_ax.clear()
            
            # Create a simple visualization
            if 'actual' in df.columns and 'predicted' in df.columns:
                # Plot actual vs predicted
                self.pred_ax.scatter(df['actual'], df['predicted'], alpha=0.6)
                self.pred_ax.plot([df['actual'].min(), df['actual'].max()], 
                                [df['actual'].min(), df['actual'].max()], 'r--', alpha=0.8)
                self.pred_ax.set_xlabel('Actual')
                self.pred_ax.set_ylabel('Predicted')
                self.pred_ax.set_title(f'Actual vs Predicted ({os.path.basename(latest_pred_file)})')
            else:
                # Plot the first two numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    self.pred_ax.scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6)
                    self.pred_ax.set_xlabel(numeric_cols[0])
                    self.pred_ax.set_ylabel(numeric_cols[1])
                    self.pred_ax.set_title(f'Prediction Results ({os.path.basename(latest_pred_file)})')
                else:
                    # Fallback to simple text display
                    self.pred_ax.text(0.5, 0.5, f'Prediction data loaded\n{len(df)} rows\n{len(df.columns)} columns', 
                                    ha='center', va='center', transform=self.pred_ax.transAxes)
                    self.pred_ax.set_title(f'Prediction Results ({os.path.basename(latest_pred_file)})')
            
            self.pred_ax.grid(True, alpha=0.3)
            self.pred_canvas.draw_idle()
            
            self.pred_status_label.config(text=f"Displaying prediction results from {latest_pred_file}")
            
        except Exception as e:
            print(f"Error updating prediction results: {e}")
            self.pred_status_label.config(text=f"Error loading prediction results: {str(e)}")

    def refresh_live_training_plot(self):
        """Refresh the live training plot."""
        try:
            if not hasattr(self, 'live_plot_epochs') or not self.live_plot_epochs:
                self.live_training_status.config(text="No live training data available")
                return
            
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
            
            self.live_training_canvas.draw_idle()
            self.live_training_status.config(text=f"Live training plot updated - {len(self.live_plot_epochs)} epochs")
            
        except Exception as e:
            print(f"Error refreshing live training plot: {e}")
            self.live_training_status.config(text=f"Error updating plot: {str(e)}")

    def get_help_content(self):
        """Get help content for the help tab."""
        try:
            help_content = """
# Stock Prediction Neural Network GUI - Help Guide

## 🚀 Getting Started

### 1. Data Selection
- **Data File**: Select your CSV data file containing stock data
- **Features**: Choose which columns to use as input features
- **Target**: Select the column you want to predict
- **Output Directory**: Choose where to save your trained models

### 2. Training Parameters
- **Hidden Layer Size**: Number of neurons in the hidden layer (default: 64)
- **Learning Rate**: How fast the model learns (default: 0.001)
- **Batch Size**: Number of samples per training batch (default: 32)
- **Epochs**: Number of complete training cycles (default: 100)
- **Patience**: Early stopping patience (default: 10)
- **History Interval**: How often to save training progress (default: 10)

### 3. Model Management
- **Refresh Models**: Scan for existing trained models
- **Make Prediction**: Use selected model to make predictions
- **Delete Model**: Remove unwanted models

### 4. Visualization Features
- **3D Plot Controls**: Interactive 3D visualizations of the loss surface
- **Plot Types**: Wireframe, Surface, Contour, Scatter, Bar3D, Trisurf, Voxels
- **Animation Generation**: Create MPEG/GIF animations of training progress
- **Live Training**: Real-time training progress visualization

## 📊 Understanding the Interface

### Control Panel (Left Side)
- **Data Selection Tab**: Choose your data and features
- **Training Parameters Tab**: Configure model training settings
- **Model Management Tab**: Manage existing models
- **Plot Controls Tab**: 3D visualization and animation controls
- **Help Tab**: This help guide

### Display Panel (Right Side)
- **Training Results**: View training progress and results
- **Prediction Results**: Display model predictions
- **Plots**: View model-generated plots
- **Saved Plots**: Browse saved plot images
- **Live Training Plot**: Real-time training visualization

## 🎯 Tips for Best Results

1. **Data Preparation**: Ensure your CSV file has clean, numeric data
2. **Feature Selection**: Choose relevant features for prediction
3. **Parameter Tuning**: Start with default values and adjust based on results
4. **Model Comparison**: Train multiple models with different parameters
5. **Visualization**: Use 3D plots to understand model behavior

## 🔧 Troubleshooting

### Common Issues:
- **No Data File**: Make sure to select a valid CSV file
- **Training Fails**: Check that your data is numeric and properly formatted
- **No Models Found**: Use "Refresh Models" to scan for existing models
- **Plot Errors**: Ensure matplotlib and numpy are properly installed

### Getting Help:
- Check the status bar for current operation status
- Look for error messages in the console output
- Use the Help tab for detailed information

## 📈 Advanced Features

### 3D Visualization
- **Multiple Plot Types**: Switch between different 3D visualization styles
- **Interactive Controls**: Rotate, zoom, and pan the 3D plots
- **Animation**: Generate animated visualizations of training progress

### Live Training
- **Real-time Updates**: Watch training progress in real-time
- **Loss Visualization**: See how the loss function changes during training
- **Performance Monitoring**: Monitor training metrics as they update

### Model Management
- **Version Control**: Each training run creates a timestamped model
- **Comparison**: Compare different models and their performance
- **Cleanup**: Remove old or unsuccessful models

## 🎨 Customization

### Themes and Styling
- The GUI uses a modern dark theme for better visibility
- Customizable color schemes for plots and visualizations
- Responsive layout that adapts to window size

### Keyboard Shortcuts
- **Ctrl+Q**: Quit application
- **F1**: Show help
- **Ctrl+R**: Refresh models
- **Ctrl+T**: Start training

## 📞 Support

For additional support or feature requests, please refer to the project documentation or contact the development team.

---
*Stock Prediction Neural Network GUI v1.0*
            """
            return help_content
        except Exception as e:
            print(f"Error getting help content: {e}")
            return "Error loading help content"

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = StockPredictionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
        