"""
Main application controller for the Stock Prediction GUI.
Handles the main application flow and coordination between modules.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.core.data_manager import DataManager
from gui.core.model_manager import ModelManager
from gui.visualization.plot_manager import PlotManager
from gui.training.training_manager import TrainingManager
from gui.prediction.prediction_manager import PredictionManager
from gui.utils.path_utils import PathUtils

class AppController:
    """Main application controller."""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.root = parent_gui.root  # Get the actual tkinter root from parent
        
        # Initialize managers
        self.data_manager = DataManager(self)
        self.model_manager = ModelManager(self)
        self.plot_manager = PlotManager(self)
        self.training_manager = TrainingManager(self)
        self.prediction_manager = PredictionManager(self)
        self.path_utils = PathUtils()
        
        # Initialize variables
        self._init_variables()
        
        # Load initial data
        self.model_manager.refresh_models(load_plots=False)
    
    def _init_variables(self):
        """Initialize application variables."""
        # Status variables
        self.status_var = tk.StringVar(value="Ready")
        self.prediction_status_var = tk.StringVar(value="No prediction data")
        
        # Training parameter variables
        self.epochs_var = tk.StringVar(value="100")
        self.validation_split_var = tk.StringVar(value="0.2")
        self.early_stopping_patience_var = tk.StringVar(value="10")
        self.patience_var = tk.StringVar(value="10")
        self.history_save_interval_var = tk.StringVar(value="10")
        self.history_interval_var = tk.StringVar(value="10")
        self.random_seed_var = tk.StringVar(value="42")
        self.save_history_var = tk.BooleanVar(value=True)
        self.memory_optimization_var = tk.BooleanVar(value=False)
        self.memory_opt_var = tk.BooleanVar(value=False)
        self.progress_reporting_interval_var = tk.StringVar(value="10")
        
        # Data file size variables
        self.data_file_size_var = tk.StringVar(value="File size: N/A")
        self.data_memory_size_var = tk.StringVar(value="Loaded size: N/A")
        
        # MPEG generation variables
        self.mpeg_status_var = tk.StringVar(value="Ready to generate MPEG")
        
        # Training parameter variables
        self.learning_rate_var = tk.StringVar(value="0.001")
        self.batch_size_var = tk.StringVar(value="32")
        
        # Add missing variables that are referenced in control panel
        self.data_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.hidden_size_var = tk.StringVar(value="64")
        self.vis_type_var = tk.StringVar(value="Wireframe")
        
        # Feature selection variables
        self.feature_vars = {}
        
        # Feature locking variables
        self.lock_status_var = tk.StringVar(value="Features unlocked")
        self.feature_status_var = tk.StringVar(value="No features selected")
        self.features_locked = False
        self.locked_features = []
    
    def setup_main_window(self):
        """Setup the main window and create all UI components."""
        try:
            print("🏗️ Setting up main window...")
            
            # Configure the main window
            self.root.configure(bg='#2b2b2b')
            self.root.minsize(1200, 800)
            
            # Create main menu
            self._create_menu()
            
            # Create main frame using grid geometry manager
            main_frame = ttk.Frame(self.root)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            main_frame.grid_columnconfigure(1, weight=1)
            main_frame.grid_rowconfigure(0, weight=1)
            
            # Configure root grid weights
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            
            # Create control panel (left side)
            self._create_control_panel(main_frame)
            
            # Create display panel (right side)
            self._create_display_panel(main_frame)
            
            # Create status bar
            self._create_status_bar()
            
            print("✅ Main window setup completed")
            
        except Exception as e:
            print(f"❌ Error setting up main window: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_menu(self):
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
    
    def _create_control_panel(self, parent):
        """Create the control panel on the left side."""
        try:
            from gui.panels.control_panel import ControlPanel
            self.control_panel = ControlPanel(parent, self)
            self.control_panel.frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            print("✅ Control panel created")
        except Exception as e:
            print(f"❌ Error creating control panel: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_display_panel(self, parent):
        """Create the display panel on the right side."""
        try:
            from gui.panels.display_panel import DisplayPanel
            self.display_panel = DisplayPanel(parent, self)
            self.display_panel.frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
            print("✅ Display panel created")
        except Exception as e:
            print(f"❌ Error creating display panel: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        try:
            status_frame = ttk.Frame(self.root)
            status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
            
            status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
            status_label.pack(fill=tk.X)
            
            print("✅ Status bar created")
        except Exception as e:
            print(f"Error creating status bar: {e}")
    
    def show_about(self):
        """Show the about dialog."""
        try:
            about_text = """
Stock Price Prediction Neural Network GUI
Version 1.0

A comprehensive GUI for training and visualizing neural networks
for stock price prediction with advanced 3D visualizations.

Features:
- Data loading and preprocessing
- Neural network training with customizable parameters
- Real-time training progress monitoring
- Advanced visualization and 3D plotting
- Prediction generation and analysis
- Model management and comparison
- Export capabilities for results and animations

This application provides an intuitive interface for stock price
prediction using neural networks with technical analysis indicators.
"""
            messagebox.showinfo("About", about_text)
        except Exception as e:
            print(f"Error showing about dialog: {e}")
    
    def on_closing(self):
        """Handle application closing."""
        try:
            # Clean up resources
            self._cleanup_tkinter_variables()
            
            # Close the main window
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during application closing: {e}")
            self.root.destroy()
    
    def _cleanup_tkinter_variables(self):
        """Clean up tkinter variables to prevent memory leaks."""
        try:
            # This is a placeholder for cleanup operations
            # In a real implementation, you would clean up any resources
            pass
        except Exception as e:
            print(f"Error cleaning up tkinter variables: {e}")
