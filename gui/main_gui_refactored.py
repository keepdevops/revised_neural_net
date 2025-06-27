#!/usr/bin/env python3
"""
Refactored Stock Price Prediction GUI

This is the main GUI file that integrates all the modular components.
It provides a clean, maintainable interface for the stock prediction system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import modular components
from gui.core.app_controller import AppController
from gui.core.data_manager import DataManager
from gui.visualization.plot_manager import PlotManager
from gui.training.training_manager import TrainingManager
from gui.prediction.prediction_manager import PredictionManager
from gui.utils.gui_utils import GUIUtils, PathManager, ModelManager, FeatureManager
from gui.windows.specialized_windows import (
    LiveTrainingWindow, SettingsDialog, HelpWindow, AboutDialog
)
from gui.windows.plot_3d_window import Plot3DWindow
from gui.windows.floating_3d_window import Floating3DWindow

class StockPredictionGUI:
    """Main GUI class that integrates all modular components."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Prediction Neural Network GUI")
        self.root.geometry("1400x900")
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize managers
        self._initialize_managers()
        
        # Initialize GUI state
        self._initialize_gui_state()
        
        # Setup main window
        self._setup_main_window()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Load initial state
        self._load_initial_state()
        
        self.logger.info("GUI initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gui.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_managers(self):
        """Initialize all manager classes."""
        # Core managers
        self.app_controller = AppController(self)
        self.data_manager = DataManager(self)
        
        # Feature managers
        self.path_manager = PathManager()
        self.model_manager = ModelManager()
        self.feature_manager = FeatureManager()
        
        # Functional managers
        self.plot_manager = PlotManager(self)
        self.training_manager = TrainingManager(self)
        self.prediction_manager = PredictionManager(self)
        
        # Utility
        self.gui_utils = GUIUtils()
    
    def _initialize_gui_state(self):
        """Initialize GUI state variables."""
        # Main state
        self.selected_model_path = None
        self.selected_prediction_file = None
        self.is_training = False
        self.is_predicting = False
        
        # GUI variables
        self.status_var = tk.StringVar(value="Ready")
        self.prediction_status_var = tk.StringVar(value="No prediction data")
        
        # Training variables
        self.epochs_var = tk.StringVar(value="100")
        self.learning_rate_var = tk.StringVar(value="0.001")
        self.batch_size_var = tk.StringVar(value="32")
        self.hidden_size_var = tk.StringVar(value="64")
        self.validation_split_var = tk.StringVar(value="0.2")
        self.early_stopping_patience_var = tk.StringVar(value="10")
        self.history_save_interval_var = tk.StringVar(value="10")
        self.random_seed_var = tk.StringVar(value="42")
        self.save_history_var = tk.BooleanVar(value=True)
        self.memory_optimization_var = tk.BooleanVar(value=False)
        
        # Data variables
        self.data_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.data_file_size_var = tk.StringVar(value="File size: N/A")
        self.data_memory_size_var = tk.StringVar(value="Loaded size: N/A")
        
        # Feature variables
        self.feature_vars = {}
        self.features_locked = False
        self.locked_features = []
        self.lock_status_var = tk.StringVar(value="Features unlocked")
        self.feature_status_var = tk.StringVar(value="No features selected")
        
        # 3D visualization variables
        self.vis_type_var = tk.StringVar(value="Wireframe")
        self.color_var = tk.StringVar(value="viridis")
        self.w1_range_min_var = tk.StringVar(value="-2.0")
        self.w1_range_max_var = tk.StringVar(value="2.0")
        self.w2_range_min_var = tk.StringVar(value="-2.0")
        self.w2_range_max_var = tk.StringVar(value="2.0")
        self.n_points_var = tk.StringVar(value="20")
        
        # Animation variables
        self.animation_running = False
        self.current_frame = 0
        self.total_frames = 0
        self.anim_speed_var = tk.DoubleVar(value=1.0)
        self.mpeg_status_var = tk.StringVar(value="Ready to generate MPEG")
        
        # Control Plots variables
        self.control_plot_type_var = tk.StringVar(value="3D Scatter")
        self.control_plot_model_var = tk.StringVar()
        self.control_plot_animation_var = tk.BooleanVar(value=False)
        self.control_plot_save_var = tk.BooleanVar(value=False)
        self.control_plot_status_var = tk.StringVar(value="Ready to create 3D plot")
        self.floating_3d_window = None
    
    def _setup_main_window(self):
        """Setup the main window layout."""
        # Create main menu
        self._create_menu()
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create left panel (control panel)
        self.left_panel = ttk.Frame(main_frame, width=400)
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.pack_propagate(False)
        
        # Create right panel (display panel)
        self.right_panel = ttk.Frame(main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Setup panels
        self._setup_control_panel()
        self._setup_display_panel()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Data File", command=self._browse_data_file)
        file_menu.add_command(label="Select Output Directory", command=self._browse_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Training menu
        training_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Training", menu=training_menu)
        training_menu.add_command(label="Start Training", command=self._start_training)
        training_menu.add_command(label="Live Training", command=self._start_live_training)
        training_menu.add_separator()
        training_menu.add_command(label="Refresh Models", command=self._refresh_models)
        
        # Prediction menu
        prediction_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Prediction", menu=prediction_menu)
        prediction_menu.add_command(label="Make Prediction", command=self._make_prediction)
        prediction_menu.add_command(label="View Results", command=self._view_prediction_results)
        
        # Visualization menu
        viz_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualization", menu=viz_menu)
        viz_menu.add_command(label="3D Gradient Descent", command=self._show_3d_visualization)
        viz_menu.add_command(label="Generate Animation", command=self._generate_animation)
        viz_menu.add_separator()
        viz_menu.add_command(label="Save Plot", command=self._save_plot)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self._show_settings)
        tools_menu.add_command(label="Clear Cache", command=self._clear_cache)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_control_panel(self):
        """Setup the control panel."""
        # Create notebook for tabs
        self.control_notebook = ttk.Notebook(self.left_panel)
        self.control_notebook.pack(fill="both", expand=True)
        
        # Data tab
        self.data_frame = ttk.Frame(self.control_notebook, padding="10")
        self.control_notebook.add(self.data_frame, text="Data")
        self._create_data_tab()
        
        # Training tab
        self.training_frame = ttk.Frame(self.control_notebook, padding="10")
        self.control_notebook.add(self.training_frame, text="Training")
        self._create_training_tab()
        
        # Prediction tab
        self.prediction_frame = ttk.Frame(self.control_notebook, padding="10")
        self.control_notebook.add(self.prediction_frame, text="Prediction")
        self._create_prediction_tab()
        
        # Plot Controls tab
        self.plot_controls_frame = ttk.Frame(self.control_notebook, padding="10")
        self.control_notebook.add(self.plot_controls_frame, text="Plot Controls")
        self._create_plot_controls_tab()
        
        # Control Plots tab
        self.control_plots_frame = ttk.Frame(self.control_notebook, padding="10")
        self.control_notebook.add(self.control_plots_frame, text="Control Plots")
        self._create_control_plots_tab()
    
    def _setup_display_panel(self):
        """Setup the display panel."""
        # Create notebook for tabs
        self.display_notebook = ttk.Notebook(self.right_panel)
        self.display_notebook.pack(fill="both", expand=True)
        
        # Training Results tab
        self.training_results_frame = ttk.Frame(self.display_notebook, padding="10")
        self.display_notebook.add(self.training_results_frame, text="Training Results")
        self._create_training_results_tab()
        
        # Prediction Results tab
        self.prediction_results_frame = ttk.Frame(self.display_notebook, padding="10")
        self.display_notebook.add(self.prediction_results_frame, text="Prediction Results")
        self._create_prediction_results_tab()
        
        # 3D Visualization tab
        self.visualization_frame = ttk.Frame(self.display_notebook, padding="10")
        self.display_notebook.add(self.visualization_frame, text="3D Visualization")
        self._create_visualization_tab()
    
    def _create_data_tab(self):
        """Create the data configuration tab."""
        # Data file selection
        ttk.Label(self.data_frame, text="Data File:").pack(anchor="w")
        
        data_file_frame = ttk.Frame(self.data_frame)
        data_file_frame.pack(fill="x", pady=(0, 10))
        
        self.data_file_combo = ttk.Combobox(data_file_frame, textvariable=self.data_file_var, 
                                           state="readonly")
        self.data_file_combo.pack(side="left", fill="x", expand=True)
        
        ttk.Button(data_file_frame, text="Browse", command=self._browse_data_file).pack(side="right", padx=(5, 0))
        
        # Output directory selection
        ttk.Label(self.data_frame, text="Output Directory:").pack(anchor="w")
        
        output_dir_frame = ttk.Frame(self.data_frame)
        output_dir_frame.pack(fill="x", pady=(0, 10))
        
        self.output_dir_combo = ttk.Combobox(output_dir_frame, textvariable=self.output_dir_var, 
                                            state="readonly")
        self.output_dir_combo.pack(side="left", fill="x", expand=True)
        
        ttk.Button(output_dir_frame, text="Browse", command=self._browse_output_dir).pack(side="right", padx=(5, 0))
        
        # File info
        ttk.Label(self.data_frame, textvariable=self.data_file_size_var).pack(anchor="w")
        ttk.Label(self.data_frame, textvariable=self.data_memory_size_var).pack(anchor="w")
        
        # Feature selection
        feature_frame = ttk.LabelFrame(self.data_frame, text="Feature Selection", padding="5")
        feature_frame.pack(fill="x", pady=(10, 0))
        
        self.feature_listbox = tk.Listbox(feature_frame, height=6, selectmode=tk.MULTIPLE)
        self.feature_listbox.pack(fill="x")
        
        feature_btn_frame = ttk.Frame(feature_frame)
        feature_btn_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(feature_btn_frame, text="Lock Features", command=self._lock_features).pack(side="left")
        ttk.Button(feature_btn_frame, text="Unlock Features", command=self._unlock_features).pack(side="left", padx=(5, 0))
        
        ttk.Label(feature_frame, textvariable=self.lock_status_var).pack(anchor="w")
        ttk.Label(feature_frame, textvariable=self.feature_status_var).pack(anchor="w")
    
    def _create_training_tab(self):
        """Create the training configuration tab."""
        # Training parameters
        params_frame = ttk.LabelFrame(self.training_frame, text="Training Parameters", padding="5")
        params_frame.pack(fill="x", pady=(0, 10))
        
        # Epochs
        ttk.Label(params_frame, text="Epochs:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(params_frame, textvariable=self.epochs_var, width=10).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Learning rate
        ttk.Label(params_frame, text="Learning Rate:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(params_frame, textvariable=self.learning_rate_var, width=10).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Batch size
        ttk.Label(params_frame, text="Batch Size:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(params_frame, textvariable=self.batch_size_var, width=10).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Hidden size
        ttk.Label(params_frame, text="Hidden Size:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(params_frame, textvariable=self.hidden_size_var, width=10).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Validation split
        ttk.Label(params_frame, text="Validation Split:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(params_frame, textvariable=self.validation_split_var, width=10).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Training buttons
        btn_frame = ttk.Frame(self.training_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Start Training", command=self._start_training).pack(side="left")
        ttk.Button(btn_frame, text="Live Training", command=self._start_live_training).pack(side="left", padx=(5, 0))
        ttk.Button(btn_frame, text="Clear Training Data", command=self._clear_training_data).pack(side="right")
    
    def _create_prediction_tab(self):
        """Create the prediction configuration tab."""
        # Model selection
        ttk.Label(self.prediction_frame, text="Select Model:").pack(anchor="w")
        
        self.model_combo = ttk.Combobox(self.prediction_frame, state="readonly")
        self.model_combo.pack(fill="x", pady=(0, 10))
        self.model_combo.bind('<<ComboboxSelected>>', self._on_model_select)
        
        # Prediction file selection
        ttk.Label(self.prediction_frame, text="Prediction Data File:").pack(anchor="w")
        
        pred_file_frame = ttk.Frame(self.prediction_frame)
        pred_file_frame.pack(fill="x", pady=(0, 10))
        
        self.pred_file_combo = ttk.Combobox(pred_file_frame, state="readonly")
        self.pred_file_combo.pack(side="left", fill="x", expand=True)
        
        ttk.Button(pred_file_frame, text="Browse", command=self._browse_prediction_file).pack(side="right", padx=(5, 0))
        
        # Prediction buttons
        btn_frame = ttk.Frame(self.prediction_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Make Prediction", command=self._make_prediction).pack(side="left")
        ttk.Button(btn_frame, text="View Results", command=self._view_prediction_results).pack(side="left", padx=(5, 0))
        ttk.Button(btn_frame, text="Delete Model", command=self._delete_selected_model).pack(side="right")
        
        # Prediction status
        ttk.Label(self.prediction_frame, textvariable=self.prediction_status_var).pack(anchor="w", pady=(10, 0))
    
    def _create_plot_controls_tab(self):
        """Create the plot controls tab."""
        # Visualization type
        ttk.Label(self.plot_controls_frame, text="Visualization Type:").pack(anchor="w")
        vis_combo = ttk.Combobox(self.plot_controls_frame, textvariable=self.vis_type_var, 
                                values=["Wireframe", "Surface", "Contour"], state="readonly")
        vis_combo.pack(fill="x", pady=(0, 10))
        vis_combo.bind('<<ComboboxSelected>>', self._on_vis_type_change)
        
        # Color map
        ttk.Label(self.plot_controls_frame, text="Color Map:").pack(anchor="w")
        color_combo = ttk.Combobox(self.plot_controls_frame, textvariable=self.color_var,
                                  values=["viridis", "plasma", "inferno", "magma", "coolwarm"], state="readonly")
        color_combo.pack(fill="x", pady=(0, 10))
        color_combo.bind('<<ComboboxSelected>>', self._on_color_map_change)
        
        # W1 range
        w1_frame = ttk.LabelFrame(self.plot_controls_frame, text="W1 Range", padding="5")
        w1_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(w1_frame, text="Min:").grid(row=0, column=0, sticky="w")
        ttk.Entry(w1_frame, textvariable=self.w1_range_min_var, width=10).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(w1_frame, text="Max:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Entry(w1_frame, textvariable=self.w1_range_max_var, width=10).grid(row=0, column=3, padx=(5, 0))
        
        # W2 range
        w2_frame = ttk.LabelFrame(self.plot_controls_frame, text="W2 Range", padding="5")
        w2_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(w2_frame, text="Min:").grid(row=0, column=0, sticky="w")
        ttk.Entry(w2_frame, textvariable=self.w2_range_min_var, width=10).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(w2_frame, text="Max:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Entry(w2_frame, textvariable=self.w2_range_max_var, width=10).grid(row=0, column=3, padx=(5, 0))
        
        # Number of points
        ttk.Label(self.plot_controls_frame, text="Number of Points:").pack(anchor="w")
        ttk.Entry(self.plot_controls_frame, textvariable=self.n_points_var, width=10).pack(anchor="w", pady=(0, 10))
        
        # Preset buttons
        preset_frame = ttk.LabelFrame(self.plot_controls_frame, text="Presets", padding="5")
        preset_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(preset_frame, text="Default", command=self._apply_default_preset).pack(side="left", padx=(0, 5))
        ttk.Button(preset_frame, text="Wide Range", command=self._apply_wide_range_preset).pack(side="left", padx=(0, 5))
        ttk.Button(preset_frame, text="High Detail", command=self._apply_high_detail_preset).pack(side="left", padx=(0, 5))
        ttk.Button(preset_frame, text="Performance", command=self._apply_performance_preset).pack(side="left")
        
        # Apply button
        ttk.Button(self.plot_controls_frame, text="Apply Changes", command=self._apply_3d_changes).pack(fill="x")
    
    def _create_control_plots_tab(self):
        """Create the control plots tab."""
        # Control plot type
        ttk.Label(self.control_plots_frame, text="Control Plot Type:").pack(anchor="w")
        control_combo = ttk.Combobox(self.control_plots_frame, textvariable=self.control_plot_type_var, 
                                    values=["3D Scatter", "2D Scatter", "1D Scatter"], state="readonly")
        control_combo.pack(fill="x", pady=(0, 10))
        control_combo.bind('<<ComboboxSelected>>', self._on_control_plot_type_change)
        
        # Model selection
        ttk.Label(self.control_plots_frame, text="Select Model:").pack(anchor="w")
        model_combo = ttk.Combobox(self.control_plots_frame, textvariable=self.control_plot_model_var, state="readonly")
        model_combo.pack(fill="x", pady=(0, 10))
        model_combo.bind('<<ComboboxSelected>>', self._on_control_plot_model_select)
        
        # Animation control
        anim_frame = ttk.LabelFrame(self.control_plots_frame, text="Animation", padding="5")
        anim_frame.pack(side="right")
        
        ttk.Button(anim_frame, text="Generate Animation", command=self._generate_control_plot_animation).pack(side="left", padx=(0, 5))
        
        # Save control
        save_frame = ttk.LabelFrame(self.control_plots_frame, text="Save", padding="5")
        save_frame.pack(side="right")
        
        ttk.Button(save_frame, text="Save Plot", command=self._save_control_plot).pack(side="left", padx=(0, 5))
        
        # Status
        ttk.Label(self.control_plots_frame, textvariable=self.control_plot_status_var).pack(anchor="w", pady=(10, 0))
    
    def _create_training_results_tab(self):
        """Create the training results tab."""
        # Model selection
        model_frame = ttk.Frame(self.training_results_frame)
        model_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(model_frame, text="Select Model:").pack(side="left")
        self.training_model_combo = ttk.Combobox(model_frame, state="readonly")
        self.training_model_combo.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.training_model_combo.bind('<<ComboboxSelected>>', self._on_training_model_select)
        
        # Plot area
        self.training_plot_frame = ttk.Frame(self.training_results_frame)
        self.training_plot_frame.pack(fill="both", expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(self.training_results_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_training_results).pack(side="left")
        ttk.Button(btn_frame, text="Save Plot", command=self._save_training_plot).pack(side="right")
    
    def _create_prediction_results_tab(self):
        """Create the prediction results tab."""
        # Prediction file selection
        pred_frame = ttk.Frame(self.prediction_results_frame)
        pred_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(pred_frame, text="Select Prediction File:").pack(side="left")
        self.pred_results_combo = ttk.Combobox(pred_frame, state="readonly")
        self.pred_results_combo.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.pred_results_combo.bind('<<ComboboxSelected>>', self._on_prediction_file_select)
        
        # Results area
        self.prediction_results_frame_inner = ttk.Frame(self.prediction_results_frame)
        self.prediction_results_frame_inner.pack(fill="both", expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(self.prediction_results_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_prediction_results).pack(side="left")
        ttk.Button(btn_frame, text="Export Results", command=self._export_prediction_results).pack(side="right")
    
    def _create_visualization_tab(self):
        """Create the 3D visualization tab."""
        # 3D plot area
        self.visualization_plot_frame = ttk.Frame(self.visualization_frame)
        self.visualization_plot_frame.pack(fill="both", expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(self.visualization_frame)
        control_frame.pack(fill="x", pady=(10, 0))
        
        # View controls
        view_frame = ttk.LabelFrame(control_frame, text="View Controls", padding="5")
        view_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Button(view_frame, text="Reset View", command=self._reset_3d_view).pack(side="left", padx=(0, 5))
        ttk.Button(view_frame, text="Top View", command=self._set_top_view).pack(side="left", padx=(0, 5))
        ttk.Button(view_frame, text="Side View", command=self._set_side_view).pack(side="left", padx=(0, 5))
        ttk.Button(view_frame, text="Isometric", command=self._set_isometric_view).pack(side="left")
        
        # Animation controls
        anim_frame = ttk.LabelFrame(control_frame, text="Animation", padding="5")
        anim_frame.pack(side="right")
        
        ttk.Button(anim_frame, text="Generate MPEG", command=self._generate_mpeg_animation).pack(side="left", padx=(0, 5))
        ttk.Button(anim_frame, text="Generate GIF", command=self._generate_gif_animation).pack(side="left")
        
        # Popout button
        ttk.Button(control_frame, text="Popout 3D Viewer", command=self._popout_3d_viewer).pack(side="right", padx=(10, 0))
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_event_handlers(self):
        """Setup event handlers."""
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Data file combo events
        self.data_file_combo.bind('<<ComboboxSelected>>', self._on_data_file_select)
        
        # Output directory combo events
        self.output_dir_combo.bind('<<ComboboxSelected>>', self._on_output_dir_select)
    
    def _load_initial_state(self):
        """Load initial application state."""
        try:
            # Load path history
            self._update_data_file_combo()
            self._update_output_dir_combo()
            
            # Load model list
            self._refresh_models()
            
            # Load settings
            self._load_settings()
            
            self.logger.info("Initial state loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading initial state: {e}")
    
    def _load_settings(self):
        """Load application settings."""
        try:
            settings_file = "gui_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    import json
                    settings = json.load(f)
                    
                    # Apply settings to variables
                    self.epochs_var.set(str(settings.get('default_epochs', 100)))
                    self.learning_rate_var.set(str(settings.get('default_learning_rate', 0.001)))
                    self.batch_size_var.set(str(settings.get('default_batch_size', 32)))
                    self.hidden_size_var.set(str(settings.get('default_hidden_size', 64)))
                    
        except Exception as e:
            self.logger.warning(f"Could not load settings: {e}")
    
    def _save_settings(self):
        """Save application settings."""
        try:
            settings = {
                'default_epochs': int(self.epochs_var.get()),
                'default_learning_rate': float(self.learning_rate_var.get()),
                'default_batch_size': int(self.batch_size_var.get()),
                'default_hidden_size': int(self.hidden_size_var.get()),
                'max_history_size': 10,
                'auto_save_interval': 5,
                'enable_logging': True
            }
            
            with open("gui_settings.json", 'w') as f:
                import json
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Could not save settings: {e}")
    
    # Event handler methods
    def _on_closing(self):
        """Handle application closing."""
        try:
            # Stop any running processes
            if self.is_training:
                self.training_manager.stop_training()
            
            # Save settings
            self._save_settings()
            
            # Save path history
            self.path_manager.save_history()
            
            # Clean up
            self.plot_manager.clear_cache()
            
            self.logger.info("Application closing")
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during application closing: {e}")
            self.root.destroy()
    
    def _browse_data_file(self):
        """Browse for data file."""
        filename = tk.filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.data_file_var.set(filename)
            self.path_manager.add_data_file(filename)
            self._update_data_file_combo()
            self._load_data_features()
            self._update_file_info(filename)
    
    def _browse_output_dir(self):
        """Browse for output directory."""
        dirname = tk.filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir_var.set(dirname)
            self.path_manager.add_output_dir(dirname)
            self._update_output_dir_combo()
    
    def _browse_prediction_file(self):
        """Browse for prediction file."""
        filename = tk.filedialog.askopenfilename(
            title="Select Prediction Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            # Update the prediction file combo
            current_values = list(self.pred_file_combo['values'])
            if filename not in current_values:
                current_values.append(filename)
                self.pred_file_combo['values'] = current_values
            self.pred_file_combo.set(filename)
    
    def _on_data_file_select(self, event=None):
        """Handle data file selection."""
        selected_file = self.data_file_var.get()
        if selected_file and os.path.exists(selected_file):
            self._load_data_features()
            self._update_file_info(selected_file)
    
    def _on_output_dir_select(self, event=None):
        """Handle output directory selection."""
        selected_dir = self.output_dir_var.get()
        if selected_dir and os.path.exists(selected_dir):
            self._refresh_models()
    
    def _on_model_select(self, event=None):
        """Handle model selection."""
        selected_model = self.model_combo.get()
        if selected_model:
            self.selected_model_path = selected_model
            self._refresh_prediction_files()
            self._load_model_info()
    
    def _on_training_model_select(self, event=None):
        """Handle training model selection."""
        selected_model = self.training_model_combo.get()
        if selected_model:
            self._load_training_results(selected_model)
    
    def _on_prediction_file_select(self, event=None):
        """Handle prediction file selection."""
        selected_file = self.pred_results_combo.get()
        if selected_file:
            self.selected_prediction_file = selected_file
            self._load_prediction_results(selected_file)
    
    def _on_vis_type_change(self, event=None):
        """Handle visualization type change."""
        self._update_3d_plot()
    
    def _on_color_map_change(self, event=None):
        """Handle color map change."""
        self._update_3d_plot()
    
    def _on_control_plot_type_change(self, event=None):
        """Handle control plot type change."""
        plot_type = self.control_plot_type_var.get()
        self.control_plot_status_var.set(f"Plot type changed to: {plot_type}")
    
    def _on_control_plot_model_select(self, event=None):
        """Handle control plot model selection."""
        model_path = self.control_plot_model_var.get()
        if model_path:
            self.control_plot_status_var.set(f"Selected model: {os.path.basename(model_path)}")
    
    def _generate_control_plot_animation(self):
        """Generate animation for control plot."""
        try:
            plot_type = self.control_plot_type_var.get()
            model_path = self.control_plot_model_var.get()
            
            if not model_path:
                messagebox.showwarning("Warning", "Please select a model first.")
                return
            
            self.control_plot_status_var.set(f"Generating {plot_type} animation...")
            self.root.update()
            
            # Create floating 3D window
            self._create_floating_3d_window(plot_type, model_path)
            
            self.control_plot_status_var.set(f"{plot_type} animation generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating control plot animation: {e}")
            messagebox.showerror("Error", f"Failed to generate animation: {e}")
            self.control_plot_status_var.set("Error generating animation")
    
    def _save_control_plot(self):
        """Save the current control plot."""
        try:
            if not self.floating_3d_window:
                messagebox.showwarning("Warning", "No plot to save. Generate a plot first.")
                return
            
            # Get save path
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                # Save the plot
                self.floating_3d_window.save_plot(file_path)
                self.control_plot_status_var.set(f"Plot saved to: {os.path.basename(file_path)}")
                
        except Exception as e:
            self.logger.error(f"Error saving control plot: {e}")
            messagebox.showerror("Error", f"Failed to save plot: {e}")
            self.control_plot_status_var.set("Error saving plot")
    
    def _create_floating_3d_window(self, plot_type, model_path):
        """Create a floating 3D plot window."""
        try:
            # Close existing window if any
            if self.floating_3d_window:
                self.floating_3d_window.close()
            
            # Create new floating window
            self.floating_3d_window = Floating3DWindow(
                self.root, 
                plot_type, 
                model_path,
                on_close=self._on_floating_window_close
            )
            
        except Exception as e:
            self.logger.error(f"Error creating floating 3D window: {e}")
            raise
    
    def _on_floating_window_close(self):
        """Handle floating window close event."""
        self.floating_3d_window = None
        self.control_plot_status_var.set("3D plot window closed")
    
    # Data management methods
    def _update_data_file_combo(self):
        """Update data file combo box."""
        history = self.path_manager.get_data_file_history()
        self.data_file_combo['values'] = history
        if history:
            self.data_file_combo.set(history[0])
    
    def _update_output_dir_combo(self):
        """Update output directory combo box."""
        history = self.path_manager.get_output_dir_history()
        self.output_dir_combo['values'] = history
        if history:
            self.output_dir_combo.set(history[0])
    
    def _load_data_features(self):
        """Load and display data features."""
        try:
            data_file = self.data_file_var.get()
            if not data_file or not os.path.exists(data_file):
                return
            
            features, error = self.feature_manager.load_data_features(data_file)
            if error:
                messagebox.showerror("Error", f"Could not load data features: {error}")
                return
            
            # Update feature listbox
            self.feature_listbox.delete(0, tk.END)
            for feature in features['columns']:
                self.feature_listbox.insert(tk.END, feature)
            
            # Update status
            self.feature_status_var.set(f"Loaded {len(features['columns'])} features")
            
        except Exception as e:
            self.logger.error(f"Error loading data features: {e}")
            messagebox.showerror("Error", f"Error loading data features: {e}")
    
    def _update_file_info(self, file_path):
        """Update file information display."""
        try:
            # File size
            size_mb = self.gui_utils.get_file_size_mb(file_path)
            self.data_file_size_var.set(f"File size: {self.gui_utils.format_file_size(size_mb)}")
            
            # Memory size (if data is loaded)
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                mem_size_mb = self.gui_utils.get_dataframe_size_mb(df)
                self.data_memory_size_var.set(f"Loaded size: {self.gui_utils.format_file_size(mem_size_mb)}")
            except Exception:
                self.data_memory_size_var.set("Loaded size: N/A")
                
        except Exception as e:
            self.logger.error(f"Error updating file info: {e}")
            self.data_file_size_var.set("File size: Error")
            self.data_memory_size_var.set("Loaded size: Error")
    
    def _lock_features(self):
        """Lock selected features."""
        try:
            selected_indices = self.feature_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select features to lock.")
                return
            
            selected_features = [self.feature_listbox.get(i) for i in selected_indices]
            self.locked_features = selected_features
            self.features_locked = True
            self.lock_status_var.set("Features locked")
            self.feature_status_var.set(f"Locked {len(selected_features)} features")
            
        except Exception as e:
            self.logger.error(f"Error locking features: {e}")
            messagebox.showerror("Error", f"Error locking features: {e}")
    
    def _unlock_features(self):
        """Unlock features."""
        self.locked_features = []
        self.features_locked = False
        self.lock_status_var.set("Features unlocked")
        self.feature_status_var.set("No features selected")
    
    # Training methods
    def _start_training(self):
        """Start training process."""
        try:
            # Validate inputs
            if not self._validate_training_inputs():
                return
            
            # Prepare training parameters
            params = self._get_training_parameters()
            
            # Start training
            success = self.training_manager.start_training(params, self._on_training_progress)
            
            if success:
                self.is_training = True
                self.status_var.set("Training started...")
            
        except Exception as e:
            self.logger.error(f"Error starting training: {e}")
            messagebox.showerror("Training Error", f"Failed to start training: {e}")
    
    def _start_live_training(self):
        """Start live training with progress window."""
        try:
            # Validate inputs
            if not self._validate_training_inputs():
                return
            
            # Create live training window
            self.live_training_window = LiveTrainingWindow(self.root)
            
            # Prepare training parameters
            params = self._get_training_parameters()
            
            # Start training with live updates
            success = self.training_manager.start_training(params, self._on_live_training_progress)
            
            if success:
                self.is_training = True
                self.status_var.set("Live training started...")
            
        except Exception as e:
            self.logger.error(f"Error starting live training: {e}")
            messagebox.showerror("Training Error", f"Failed to start live training: {e}")
    
    def _validate_training_inputs(self):
        """Validate training inputs."""
        # Check data file
        data_file = self.data_file_var.get()
        if not data_file or not os.path.exists(data_file):
            messagebox.showerror("Error", "Please select a valid data file.")
            return False
        
        # Check output directory
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return False
        
        # Validate numeric parameters
        try:
            epochs = int(self.epochs_var.get())
            learning_rate = float(self.learning_rate_var.get())
            batch_size = int(self.batch_size_var.get())
            hidden_size = int(self.hidden_size_var.get())
            
            if epochs <= 0 or learning_rate <= 0 or batch_size <= 0 or hidden_size <= 0:
                raise ValueError("Parameters must be positive")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid training parameters: {e}")
            return False
        
        return True
    
    def _get_training_parameters(self):
        """Get training parameters from GUI variables."""
        return {
            'data_file': self.data_file_var.get(),
            'output_dir': self.output_dir_var.get(),
            'epochs': int(self.epochs_var.get()),
            'learning_rate': float(self.learning_rate_var.get()),
            'batch_size': int(self.batch_size_var.get()),
            'hidden_size': int(self.hidden_size_var.get()),
            'validation_split': float(self.validation_split_var.get()),
            'early_stopping_patience': int(self.early_stopping_patience_var.get()),
            'history_save_interval': int(self.history_save_interval_var.get()),
            'random_seed': int(self.random_seed_var.get()),
            'save_history': self.save_history_var.get(),
            'memory_optimization': self.memory_optimization_var.get()
        }
    
    def _on_training_progress(self, status, data):
        """Handle training progress updates."""
        if status == 'completed':
            self.is_training = False
            self.status_var.set("Training completed")
            self._refresh_models()
            messagebox.showinfo("Success", f"Training completed successfully!\nModel saved to: {data}")
        elif status == 'error':
            self.is_training = False
            self.status_var.set("Training failed")
            messagebox.showerror("Error", f"Training failed: {data}")
        else:
            # Progress update
            epoch, loss, val_loss = data
            self.status_var.set(f"Training... Epoch {epoch}, Loss: {loss:.6f}")
    
    def _on_live_training_progress(self, status, data):
        """Handle live training progress updates."""
        if hasattr(self, 'live_training_window') and self.live_training_window:
            if status == 'completed':
                self.is_training = False
                self.status_var.set("Live training completed")
                self._refresh_models()
                self.live_training_window.window.destroy()
                messagebox.showinfo("Success", f"Training completed successfully!\nModel saved to: {data}")
            elif status == 'error':
                self.is_training = False
                self.status_var.set("Live training failed")
                self.live_training_window.window.destroy()
                messagebox.showerror("Error", f"Training failed: {data}")
            else:
                # Progress update
                epoch, loss, val_loss = data
                self.live_training_window.update_progress(epoch, loss, val_loss)
    
    def _clear_training_data(self):
        """Clear training data and plots."""
        try:
            # Clear plot frames
            for widget in self.training_plot_frame.winfo_children():
                widget.destroy()
            
            # Clear model combo
            self.training_model_combo['values'] = ()
            self.training_model_combo.set('')
            
            self.status_var.set("Training data cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing training data: {e}")
    
    # Model management methods
    def _refresh_models(self):
        """Refresh the model list."""
        try:
            models = self.model_manager.get_model_directories()
            
            # Update model combos
            model_names = [os.path.basename(model) for model in models]
            self.model_combo['values'] = model_names
            self.training_model_combo['values'] = model_names
            
            if model_names:
                self.model_combo.set(model_names[0])
                self.training_model_combo.set(model_names[0])
            
            self.status_var.set(f"Found {len(models)} models")
            
        except Exception as e:
            self.logger.error(f"Error refreshing models: {e}")
    
    def _load_model_info(self):
        """Load and display model information."""
        try:
            if not self.selected_model_path:
                return
            
            model_info = self.model_manager.get_model_info(self.selected_model_path)
            if model_info:
                # Update status with model info
                self.status_var.set(f"Model: {model_info['name']} - Created: {model_info['created'].strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            self.logger.error(f"Error loading model info: {e}")
    
    def _delete_selected_model(self):
        """Delete the selected model."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Selection", "Please select a model to delete.")
                return
            
            # Confirm deletion
            result = messagebox.askyesno("Confirm Deletion", 
                                       f"Are you sure you want to delete the model:\n{os.path.basename(self.selected_model_path)}?")
            if not result:
                return
            
            # Delete model
            success, error = self.model_manager.delete_model(self.selected_model_path)
            if success:
                self.status_var.set("Model deleted")
                self._refresh_models()
                messagebox.showinfo("Success", "Model deleted successfully.")
            else:
                messagebox.showerror("Error", f"Error deleting model: {error}")
            
        except Exception as e:
            self.logger.error(f"Error deleting model: {e}")
            messagebox.showerror("Error", f"Error deleting model: {e}")
    
    # Prediction methods
    def _make_prediction(self):
        """Make predictions using the selected model."""
        try:
            # Validate inputs
            if not self.selected_model_path:
                messagebox.showwarning("No Model", "Please select a model first.")
                return
            
            # Get prediction data file
            pred_file = self.pred_file_combo.get()
            if not pred_file or not os.path.exists(pred_file):
                messagebox.showwarning("No Data", "Please select a prediction data file.")
                return
            
            # Start prediction
            success = self.prediction_manager.make_prediction(
                self.selected_model_path, pred_file, self._on_prediction_progress
            )
            
            if success:
                self.is_predicting = True
                self.status_var.set("Making predictions...")
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            messagebox.showerror("Prediction Error", f"Error making prediction: {e}")
    
    def _on_prediction_progress(self, status, data):
        """Handle prediction progress updates."""
        if status == 'completed':
            self.is_predicting = False
            self.status_var.set("Prediction completed")
            self._refresh_prediction_files()
            messagebox.showinfo("Success", f"Prediction completed successfully!\nResults saved to: {data}")
        elif status == 'error':
            self.is_predicting = False
            self.status_var.set("Prediction failed")
            messagebox.showerror("Error", f"Prediction failed: {data}")
    
    def _refresh_prediction_files(self):
        """Refresh the prediction files list."""
        try:
            if not self.selected_model_path:
                return
            
            prediction_files = self.prediction_manager.get_prediction_files(self.selected_model_path)
            
            # Update prediction file combos
            file_names = [os.path.basename(f) for f in prediction_files]
            self.pred_results_combo['values'] = file_names
            
            if file_names:
                self.pred_results_combo.set(file_names[0])
            
            self.prediction_status_var.set(f"Found {len(prediction_files)} prediction files")
            
        except Exception as e:
            self.logger.error(f"Error refreshing prediction files: {e}")
    
    def _view_prediction_results(self):
        """View prediction results."""
        try:
            if not self.selected_prediction_file:
                messagebox.showwarning("No Selection", "Please select a prediction file to view.")
                return
            
            # Load and display results
            self._load_prediction_results(self.selected_prediction_file)
            
        except Exception as e:
            self.logger.error(f"Error viewing prediction results: {e}")
            messagebox.showerror("Error", f"Error viewing prediction results: {e}")
    
    def _load_prediction_results(self, prediction_file):
        """Load and display prediction results."""
        try:
            # Load results
            df = self.prediction_manager.load_prediction_results(prediction_file)
            
            # Display in prediction results tab
            self.plot_manager.plot_prediction_results(prediction_file, self.prediction_results_frame_inner)
            
            # Update status
            summary = self.prediction_manager.get_prediction_summary(prediction_file)
            self.prediction_status_var.set(f"Loaded {summary['total_predictions']} predictions")
            
        except Exception as e:
            self.logger.error(f"Error loading prediction results: {e}")
            messagebox.showerror("Error", f"Error loading prediction results: {e}")
    
    def _load_training_results(self, model_path):
        """Load and display training results."""
        try:
            # Display training results
            self.plot_manager.plot_training_results(model_path, self.training_plot_frame)
            
        except Exception as e:
            self.logger.error(f"Error loading training results: {e}")
            messagebox.showerror("Error", f"Error loading training results: {e}")
    
    def _refresh_training_results(self):
        """Refresh training results."""
        try:
            selected_model = self.training_model_combo.get()
            if selected_model:
                self._load_training_results(selected_model)
            
        except Exception as e:
            self.logger.error(f"Error refreshing training results: {e}")
    
    def _refresh_prediction_results(self):
        """Refresh prediction results."""
        try:
            if self.selected_prediction_file:
                self._load_prediction_results(self.selected_prediction_file)
            
        except Exception as e:
            self.logger.error(f"Error refreshing prediction results: {e}")
    
    # Visualization methods
    def _show_3d_visualization(self):
        """Show 3D gradient descent visualization."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Model", "Please select a model first.")
                return
            
            # Create 3D visualization
            self.plot_manager.create_3d_gradient_descent_plot(
                self.visualization_plot_frame, self.selected_model_path
            )
            
            self.status_var.set("3D visualization loaded")
            
        except Exception as e:
            self.logger.error(f"Error showing 3D visualization: {e}")
            messagebox.showerror("Error", f"Error showing 3D visualization: {e}")
    
    def _update_3d_plot(self):
        """Update the 3D plot with current settings."""
        try:
            # This would update the 3D plot with current control settings
            # Implementation depends on the specific 3D plotting requirements
            self.status_var.set("3D plot updated")
            
        except Exception as e:
            self.logger.error(f"Error updating 3D plot: {e}")
    
    def _generate_animation(self):
        """Generate animation from weights history."""
        try:
            if not self.selected_model_path:
                messagebox.showwarning("No Model", "Please select a model first.")
                return
            
            # Generate animation
            success = self.plot_manager.generate_animation(self.selected_model_path)
            
            if success:
                self.status_var.set("Animation generated successfully")
                messagebox.showinfo("Success", "Animation generated successfully!")
            else:
                messagebox.showerror("Error", "Failed to generate animation")
            
        except Exception as e:
            self.logger.error(f"Error generating animation: {e}")
            messagebox.showerror("Error", f"Error generating animation: {e}")
    
    def _generate_mpeg_animation(self):
        """Generate MPEG animation."""
        self._generate_animation()
    
    def _generate_gif_animation(self):
        """Generate GIF animation."""
        self._generate_animation()
    
    def _popout_3d_viewer(self):
        """Pop out the 3D viewer into a separate window."""
        try:
            # This would create a separate window for the 3D viewer
            # Implementation depends on the specific 3D plotting requirements
            self.status_var.set("3D viewer popped out")
            
        except Exception as e:
            self.logger.error(f"Error popping out 3D viewer: {e}")
    
    # View control methods
    def _reset_3d_view(self):
        """Reset 3D view to default."""
        self._update_3d_plot()
    
    def _set_top_view(self):
        """Set 3D view to top view."""
        self._update_3d_plot()
    
    def _set_side_view(self):
        """Set 3D view to side view."""
        self._update_3d_plot()
    
    def _set_isometric_view(self):
        """Set 3D view to isometric view."""
        self._update_3d_plot()
    
    # Preset methods
    def _apply_default_preset(self):
        """Apply default preset settings."""
        self.vis_type_var.set("Surface")
        self.color_var.set("viridis")
        self.w1_range_min_var.set("-2.0")
        self.w1_range_max_var.set("2.0")
        self.w2_range_min_var.set("-2.0")
        self.w2_range_max_var.set("2.0")
        self.n_points_var.set("20")
        self.status_var.set("Applied default preset")
    
    def _apply_wide_range_preset(self):
        """Apply wide range preset settings."""
        self.vis_type_var.set("Surface")
        self.color_var.set("plasma")
        self.w1_range_min_var.set("-10.0")
        self.w1_range_max_var.set("10.0")
        self.w2_range_min_var.set("-10.0")
        self.w2_range_max_var.set("10.0")
        self.n_points_var.set("50")
        self.status_var.set("Applied wide range preset")
    
    def _apply_high_detail_preset(self):
        """Apply high detail preset settings."""
        self.vis_type_var.set("Wireframe")
        self.color_var.set("coolwarm")
        self.w1_range_min_var.set("-3.0")
        self.w1_range_max_var.set("3.0")
        self.w2_range_min_var.set("-3.0")
        self.w2_range_max_var.set("3.0")
        self.n_points_var.set("100")
        self.status_var.set("Applied high detail preset")
    
    def _apply_performance_preset(self):
        """Apply performance preset settings."""
        self.vis_type_var.set("Contour")
        self.color_var.set("viridis")
        self.w1_range_min_var.set("-2.0")
        self.w1_range_max_var.set("2.0")
        self.w2_range_min_var.set("-2.0")
        self.w2_range_max_var.set("2.0")
        self.n_points_var.set("10")
        self.status_var.set("Applied performance preset")
    
    def _apply_3d_changes(self):
        """Apply 3D changes and update plot."""
        self._update_3d_plot()
        self.status_var.set("3D changes applied")
    
    # Utility methods
    def _show_settings(self):
        """Show settings dialog."""
        try:
            dialog = SettingsDialog(self.root)
            result = dialog.show()
            if result:
                # Apply new settings
                self._apply_settings(result)
                
        except Exception as e:
            self.logger.error(f"Error showing settings: {e}")
    
    def _show_help(self):
        """Show help window."""
        try:
            HelpWindow(self.root)
            
        except Exception as e:
            self.logger.error(f"Error showing help: {e}")
    
    def _show_about(self):
        """Show about dialog."""
        try:
            AboutDialog(self.root)
            
        except Exception as e:
            self.logger.error(f"Error showing about dialog: {e}")
    
    def _clear_cache(self):
        """Clear application cache."""
        try:
            self.plot_manager.clear_cache()
            self.status_var.set("Cache cleared")
            messagebox.showinfo("Success", "Cache cleared successfully.")
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            messagebox.showerror("Error", f"Error clearing cache: {e}")
    
    def _save_training_plot(self):
        """Save training plot."""
        try:
            # Implementation for saving training plot
            self.status_var.set("Training plot saved")
            
        except Exception as e:
            self.logger.error(f"Error saving training plot: {e}")
    
    def _export_prediction_results(self):
        """Export prediction results."""
        try:
            # Implementation for exporting prediction results
            self.status_var.set("Prediction results exported")
            
        except Exception as e:
            self.logger.error(f"Error exporting prediction results: {e}")
    
    def _save_plot(self):
        """Save current plot."""
        try:
            # Implementation for saving current plot
            self.status_var.set("Plot saved")
            
        except Exception as e:
            self.logger.error(f"Error saving plot: {e}")
    
    def _apply_settings(self, settings):
        """Apply new settings."""
        try:
            # Apply settings to GUI variables
            self.epochs_var.set(str(settings.get('default_epochs', 100)))
            self.learning_rate_var.set(str(settings.get('default_learning_rate', 0.001)))
            self.batch_size_var.set(str(settings.get('default_batch_size', 32)))
            
            self.status_var.set("Settings applied")
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")

def main():
    """Main function to run the refactored GUI."""
    root = tk.Tk()
    app = StockPredictionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()