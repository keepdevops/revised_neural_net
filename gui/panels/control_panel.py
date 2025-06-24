import tkinter as tk
from tkinter import ttk
from gui.theme import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ControlPanel:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.frame = ttk.Frame(master)
        self.setup_ui()

    def setup_ui(self):
        # Create notebook for different control sections
        self.app.control_notebook = ttk.Notebook(self.frame)
        self.app.control_notebook.grid(row=0, column=0, sticky="nsew")
        
        # Data Selection Tab
        data_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(data_frame, text="Data Selection")
        data_frame.grid_columnconfigure(0, weight=1)
        
        # Data file selection
        data_label = ttk.Label(data_frame, text="Data File:", style="Bold.TLabel")
        data_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        data_entry_frame = ttk.Frame(data_frame)
        data_entry_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        data_entry_frame.grid_columnconfigure(0, weight=1)
        data_entry_frame.grid_columnconfigure(1, weight=0)
        
        self.app.data_entry = ttk.Entry(data_entry_frame, textvariable=self.app.data_file_var, state="readonly")
        self.app.data_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        browse_btn = tk.Button(data_entry_frame, text="📁 Browse", command=self.app.browse_data_file, bg="#4A90E2", fg="white", relief="raised", bd=2)
        browse_btn.grid(row=0, column=1, padx=5, pady=2)
        print("✅ Data file browse button created and placed")
        
        # Feature selection
        feature_label = ttk.Label(data_frame, text="Features:", style="Bold.TLabel")
        feature_label.grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        # Feature listbox with scrollbar
        feature_frame = ttk.Frame(data_frame)
        feature_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        feature_frame.grid_columnconfigure(0, weight=1)
        feature_frame.grid_rowconfigure(0, weight=1)
        
        self.app.feature_listbox = tk.Listbox(feature_frame, selectmode=tk.MULTIPLE, height=8)
        self.app.feature_listbox.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        feature_scrollbar = ttk.Scrollbar(feature_frame, orient="vertical", command=self.app.feature_listbox.yview)
        feature_scrollbar.grid(row=0, column=1, sticky="ns")
        self.app.feature_listbox.configure(yscrollcommand=feature_scrollbar.set)
        
        # Feature buttons
        feature_btn_frame = ttk.Frame(data_frame)
        feature_btn_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        feature_btn_frame.grid_columnconfigure(0, weight=1)
        feature_btn_frame.grid_columnconfigure(1, weight=1)
        
        lock_btn = ttk.Button(feature_btn_frame, text="Lock Selected", command=self.app.lock_features)
        lock_btn.grid(row=0, column=0, padx=(0, 5))
        
        unlock_btn = ttk.Button(feature_btn_frame, text="Unlock All", command=self.app.unlock_features)
        unlock_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Target feature selection
        target_label = ttk.Label(data_frame, text="Target Feature:", style="Bold.TLabel")
        target_label.grid(row=5, column=0, sticky="w", pady=(10, 5))
        
        self.app.target_combo = ttk.Combobox(data_frame, state="readonly", width=20)
        self.app.target_combo.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        
        # Output directory
        output_label = ttk.Label(data_frame, text="Output Directory:", style="Bold.TLabel")
        output_label.grid(row=7, column=0, sticky="w", pady=(10, 5))
        
        output_entry_frame = ttk.Frame(data_frame)
        output_entry_frame.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        output_entry_frame.grid_columnconfigure(0, weight=1)
        output_entry_frame.grid_columnconfigure(1, weight=0)
        
        self.app.output_entry = ttk.Entry(output_entry_frame, textvariable=self.app.output_dir_var)
        self.app.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        output_browse_btn = tk.Button(output_entry_frame, text="📁 Browse", command=self.app.browse_output_dir, bg="#4A90E2", fg="white", relief="raised", bd=2)
        output_browse_btn.grid(row=0, column=1, padx=5, pady=2)
        print("✅ Output directory browse button created and placed")
        print("✅ Data file browse button created and placed")
        
        # Training Parameters Tab
        training_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(training_frame, text="Training Parameters")
        training_frame.grid_columnconfigure(0, weight=1)
        
        # Hidden layer size
        hidden_label = ttk.Label(training_frame, text="Hidden Layer Size:", style="Bold.TLabel")
        hidden_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        hidden_entry = ttk.Entry(training_frame, textvariable=self.app.hidden_size_var, width=10)
        hidden_entry.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Learning rate
        lr_label = ttk.Label(training_frame, text="Learning Rate:", style="Bold.TLabel")
        lr_label.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        lr_entry = ttk.Entry(training_frame, textvariable=self.app.learning_rate_var, width=10)
        lr_entry.grid(row=3, column=0, sticky="w", pady=(0, 10))
        
        # Batch size
        batch_label = ttk.Label(training_frame, text="Batch Size:", style="Bold.TLabel")
        batch_label.grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        batch_entry = ttk.Entry(training_frame, textvariable=self.app.batch_size_var, width=10)
        batch_entry.grid(row=5, column=0, sticky="w", pady=(0, 10))
        
        # Training button
        self.app.train_button = ttk.Button(training_frame, text="Start Training", command=self.app.start_training)
        self.app.train_button.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        
        # Live Training button for Error loss
        self.app.live_training_button = ttk.Button(training_frame, text="📊 Live Training (Error Loss)", command=self.app.start_live_training)
        self.app.live_training_button.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        
        # Cache clear button
        self.app.cache_clear_btn = ttk.Button(training_frame, text="Clear Cache", command=self.app.clear_cache_only)
        self.app.cache_clear_btn.grid(row=8, column=0, sticky="ew", pady=(10, 0))
        
        # Model Management Tab
        model_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(model_frame, text="Model Management")
        model_frame.grid_columnconfigure(0, weight=1)
        
        # Model selection
        model_label = ttk.Label(model_frame, text="Select Model:", style="Bold.TLabel")
        model_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.app.model_combo = ttk.Combobox(model_frame, state="readonly")
        self.app.model_combo.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.app.model_combo.bind('<<ComboboxSelected>>', self.app.on_model_select)
        
        # Model buttons
        model_btn_frame = ttk.Frame(model_frame)
        model_btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        model_btn_frame.grid_columnconfigure(0, weight=1)
        model_btn_frame.grid_columnconfigure(1, weight=1)
        model_btn_frame.grid_columnconfigure(2, weight=1)
        
        refresh_btn = ttk.Button(model_btn_frame, text="Refresh Models", command=self.app.refresh_models)
        refresh_btn.grid(row=0, column=0, padx=(0, 5))
        
        predict_btn = ttk.Button(model_btn_frame, text="Make Prediction", command=self.app.make_prediction)
        predict_btn.grid(row=0, column=1, padx=(5, 5))
        
        delete_btn = ttk.Button(model_btn_frame, text="🗑️ Delete Model", command=self.app.delete_selected_model)
        delete_btn.grid(row=0, column=2, padx=(5, 0))
        
        # MPEG Generation button
        mpeg_btn = ttk.Button(model_btn_frame, text="🎬 Create MPEG Movie", command=self.app.generate_mpeg_animation)
        mpeg_btn.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        # Prediction Files Section
        pred_files_label = ttk.Label(model_frame, text="Prediction Files:", style="Bold.TLabel")
        pred_files_label.grid(row=3, column=0, sticky="w", pady=(20, 5))
        
        # Create frame for prediction files listbox and scrollbar
        pred_files_frame = ttk.Frame(model_frame)
        pred_files_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        pred_files_frame.grid_columnconfigure(0, weight=1)
        pred_files_frame.grid_rowconfigure(0, weight=1)
        
        # Prediction files listbox
        self.app.prediction_files_listbox = tk.Listbox(pred_files_frame, height=6, selectmode=tk.SINGLE)
        self.app.prediction_files_listbox.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.app.prediction_files_listbox.bind('<<ListboxSelect>>', self.app.on_prediction_file_select)
        
        # Scrollbar for prediction files
        pred_files_scrollbar = ttk.Scrollbar(pred_files_frame, orient="vertical", command=self.app.prediction_files_listbox.yview)
        pred_files_scrollbar.grid(row=0, column=1, sticky="ns")
        self.app.prediction_files_listbox.configure(yscrollcommand=pred_files_scrollbar.set)
        
        # Prediction files buttons
        pred_files_btn_frame = ttk.Frame(model_frame)
        pred_files_btn_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        pred_files_btn_frame.grid_columnconfigure(0, weight=1)
        pred_files_btn_frame.grid_columnconfigure(1, weight=1)
        
        refresh_pred_btn = ttk.Button(pred_files_btn_frame, text="Refresh Prediction Files", command=self.app.refresh_prediction_files)
        refresh_pred_btn.grid(row=0, column=0, padx=(0, 5))
        
        view_pred_btn = ttk.Button(pred_files_btn_frame, text="View Prediction Results", command=self.app.view_prediction_results)
        view_pred_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Floating Panel Control
        panel_control_frame = ttk.Frame(model_frame)
        panel_control_frame.grid(row=6, column=0, sticky="ew", pady=(20, 0))
        panel_control_frame.grid_columnconfigure(0, weight=1)
        panel_control_frame.grid_columnconfigure(1, weight=1)
        
        toggle_panel_btn = ttk.Button(panel_control_frame, text="Toggle Results Panel", command=self.app.toggle_right_panel)
        toggle_panel_btn.grid(row=0, column=0, padx=(0, 5))
        
        show_panel_btn = ttk.Button(panel_control_frame, text="Show Results Panel", command=self.app.show_right_panel)
        show_panel_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Plot Controls Tab
        plot_controls_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(plot_controls_frame, text="Plot Controls")
        plot_controls_frame.grid_columnconfigure(0, weight=1)
        plot_controls_frame.grid_rowconfigure(1, weight=1)  # Row 1 for the plot

        # Animation Controls for 3D Gradient Descent
        anim_controls = ttk.LabelFrame(plot_controls_frame, text="3D Gradient Descent Animation")
        anim_controls.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Playback controls
        playback_frame = ttk.Frame(anim_controls)
        playback_frame.grid(row=0, column=0, sticky="ew", pady=5)
        playback_frame.grid_columnconfigure(0, weight=1)
        playback_frame.grid_columnconfigure(1, weight=1)
        playback_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(playback_frame, text="▶ Play", command=self.app.play_gd_animation).grid(row=0, column=0, padx=5)
        ttk.Button(playback_frame, text="⏸ Pause", command=self.app.pause_gd_animation).grid(row=0, column=1, padx=5)
        ttk.Button(playback_frame, text="⏹ Stop", command=self.app.stop_gd_animation).grid(row=0, column=2, padx=5)

        # Speed and frame controls
        control_frame = ttk.Frame(anim_controls)
        control_frame.grid(row=1, column=0, sticky="ew", pady=5)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(control_frame, text="Speed:").grid(row=0, column=0, padx=(0, 5))
        self.app.gd_anim_speed = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.app.gd_anim_speed, 
                                orient="horizontal", command=self.app.on_anim_speed_change)
        speed_scale.grid(row=0, column=1, sticky="ew", padx=5)
        self.app.speed_label = ttk.Label(control_frame, text="1.0x")
        self.app.speed_label.grid(row=0, column=2, padx=5)

        ttk.Label(control_frame, text="Frame:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        self.app.frame_slider = ttk.Scale(control_frame, from_=0, to=100, orient="horizontal", 
                                          command=self.app.on_frame_pos_change)
        self.app.frame_slider.grid(row=1, column=1, sticky="ew", padx=5, pady=(10, 0))
        self.app.frame_label = ttk.Label(control_frame, text="0/0")
        self.app.frame_label.grid(row=1, column=2, padx=5, pady=(10, 0))

        # 3D Interaction Controls
        interaction_frame = ttk.LabelFrame(plot_controls_frame, text="3D View Controls")
        interaction_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Rotation controls
        rotation_frame = ttk.Frame(interaction_frame)
        rotation_frame.grid(row=0, column=0, sticky="ew", pady=5)
        rotation_frame.grid_columnconfigure(1, weight=1)
        rotation_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(rotation_frame, text="Elevation:").grid(row=0, column=0, padx=(0, 5))
        self.app.elevation_var = tk.DoubleVar(value=30)
        elevation_scale = ttk.Scale(rotation_frame, from_=-90, to=90, variable=self.app.elevation_var,
                                   orient="horizontal", command=self.app.on_elevation_change)
        elevation_scale.grid(row=0, column=1, sticky="ew", padx=5)
        self.app.elevation_label = ttk.Label(rotation_frame, text="30°")
        self.app.elevation_label.grid(row=0, column=2, padx=5)

        ttk.Label(rotation_frame, text="Azimuth:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        self.app.azimuth_var = tk.DoubleVar(value=45)
        azimuth_scale = ttk.Scale(rotation_frame, from_=0, to=360, variable=self.app.azimuth_var,
                                 orient="horizontal", command=self.app.on_azimuth_change)
        azimuth_scale.grid(row=1, column=1, sticky="ew", padx=5, pady=(10, 0))
        self.app.azimuth_label = ttk.Label(rotation_frame, text="45°")
        self.app.azimuth_label.grid(row=1, column=2, padx=5, pady=(10, 0))

        # Zoom and reset controls
        zoom_frame = ttk.Frame(interaction_frame)
        zoom_frame.grid(row=1, column=0, sticky="ew", pady=5)
        zoom_frame.grid_columnconfigure(1, weight=1)
        zoom_frame.grid_columnconfigure(3, weight=1)

        ttk.Label(zoom_frame, text="Zoom:").grid(row=0, column=0, padx=(0, 5))
        self.app.zoom_var = tk.DoubleVar(value=1.0)
        zoom_scale = ttk.Scale(zoom_frame, from_=0.1, to=3.0, variable=self.app.zoom_var,
                              orient="horizontal", command=self.app.on_zoom_change)
        zoom_scale.grid(row=0, column=1, sticky="ew", padx=5)
        self.app.zoom_label = ttk.Label(zoom_frame, text="1.0x")
        self.app.zoom_label.grid(row=0, column=2, padx=5)

        # Reset and preset buttons
        preset_frame = ttk.Frame(interaction_frame)
        preset_frame.grid(row=2, column=0, sticky="ew", pady=5)
        preset_frame.grid_columnconfigure(0, weight=1)
        preset_frame.grid_columnconfigure(1, weight=1)
        preset_frame.grid_columnconfigure(2, weight=1)
        preset_frame.grid_columnconfigure(3, weight=1)

        ttk.Button(preset_frame, text="🔄 Reset View", command=self.app.reset_3d_view).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(preset_frame, text="👁 Top View", command=self.app.set_top_view).grid(row=0, column=1, padx=5)
        ttk.Button(preset_frame, text="👁 Side View", command=self.app.set_side_view).grid(row=0, column=2, padx=5)
        ttk.Button(preset_frame, text="👁 Isometric", command=self.app.set_isometric_view).grid(row=0, column=3, padx=(5, 0))

        # Mouse interaction info
        info_frame = ttk.Frame(interaction_frame)
        info_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        info_label = ttk.Label(info_frame, 
                              text="💡 Mouse: Left drag to rotate, Right drag to zoom, Middle drag to pan",
                              font=("Arial", 9), foreground="green")
        info_label.pack()

        # MPEG File Management Section
        mpeg_frame = ttk.LabelFrame(plot_controls_frame, text="Animation Files (MPEG/GIF/MP4)")
        mpeg_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Add helpful instructions
        instructions_frame = ttk.Frame(mpeg_frame)
        instructions_frame.grid(row=0, column=0, sticky="ew", pady=(5, 0))
        instructions_label = ttk.Label(instructions_frame, 
                                      text="💡 Tip: Click 'Browse' to navigate to model directories and find animation files in their 'plots' subdirectories",
                                      font=("Arial", 9), foreground="blue")
        instructions_label.pack()

        # MPEG files listbox and controls
        mpeg_controls_frame = ttk.Frame(mpeg_frame)
        mpeg_controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
        mpeg_controls_frame.grid_columnconfigure(0, weight=1)

        # MPEG files listbox
        mpeg_listbox_frame = ttk.Frame(mpeg_controls_frame)
        mpeg_listbox_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        mpeg_listbox_frame.grid_columnconfigure(0, weight=1)
        mpeg_listbox_frame.grid_rowconfigure(0, weight=1)

        self.app.mpeg_files_listbox = tk.Listbox(mpeg_listbox_frame, height=4, selectmode=tk.SINGLE)
        self.app.mpeg_files_listbox.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.app.mpeg_files_listbox.bind('<Double-Button-1>', self.app.on_mpeg_file_select)

        # Scrollbar for MPEG files
        mpeg_scrollbar = ttk.Scrollbar(mpeg_listbox_frame, orient="vertical", command=self.app.mpeg_files_listbox.yview)
        mpeg_scrollbar.grid(row=0, column=1, sticky="ns")
        self.app.mpeg_files_listbox.configure(yscrollcommand=mpeg_scrollbar.set)

        # MPEG file buttons
        mpeg_btn_frame = ttk.Frame(mpeg_controls_frame)
        mpeg_btn_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        mpeg_btn_frame.grid_columnconfigure(0, weight=1)
        mpeg_btn_frame.grid_columnconfigure(1, weight=1)
        mpeg_btn_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(mpeg_btn_frame, text="🎬 Browse Animation Files", command=self.app.browse_mpeg_files).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(mpeg_btn_frame, text="Open Selected", command=self.app.open_selected_mpeg).grid(row=0, column=1, padx=5)
        ttk.Button(mpeg_btn_frame, text="Refresh List", command=self.app.refresh_mpeg_files).grid(row=0, column=2, padx=(5, 0))

        # Create 3D plot embedded in the Plot Controls tab
        plot_frame = ttk.Frame(plot_controls_frame)
        plot_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5, 10))
        plot_frame.grid_columnconfigure(0, weight=1)
        plot_frame.grid_rowconfigure(0, weight=1)

        # Create matplotlib figure for 3D gradient descent
        self.app.gd3d_fig = plt.Figure(figsize=(8, 6))
        self.app.gd3d_ax = self.app.gd3d_fig.add_subplot(111, projection="3d")

        # Create canvas and embed in the plot frame
        self.app.gd3d_canvas = FigureCanvasTkAgg(self.app.gd3d_fig, plot_frame)
        self.app.gd3d_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Add toolbar
        from gui.components.grid_matplotlib_toolbar import GridMatplotlibToolbar
        toolbar = GridMatplotlibToolbar(self.app.gd3d_canvas, plot_frame)
        toolbar.grid(row=1, column=0, sticky="ew")

        # Initialize with placeholder - use proper 3D text placement
        self.app.gd3d_ax.text2D(0.5, 0.5, "3D Gradient Descent Animation\nSelect a model and click Play to start", 
                              ha="center", va="center", transform=self.app.gd3d_ax.transAxes,
                              fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        self.app.gd3d_ax.axis("off")

        try:
            self.app.gd3d_canvas.draw_idle()
        except Exception as canvas_error:
            print(f"Canvas update error in Plot Controls initialization: {canvas_error}")

        # Ensure the 3D axes are accessible to the main GUI
        print("✅ 3D axes made accessible to main GUI")
        
        print("✅ Plot Controls tab with 3D animation created successfully")
        
        # Help Tab
        help_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(help_frame, text="?")
        help_frame.grid_columnconfigure(0, weight=1)
        help_frame.grid_rowconfigure(0, weight=1)
        
        # Create help content
        help_content_frame = ttk.Frame(help_frame)
        help_content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        help_content_frame.grid_columnconfigure(0, weight=1)
        help_content_frame.grid_rowconfigure(1, weight=1)
        
        # Help title
        help_title = ttk.Label(help_content_frame, text="Stock Prediction GUI - User Manual", 
                              style="Bold.TLabel", font=("Arial", 14, "bold"))
        help_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Create scrollable text widget for help content
        help_text_frame = ttk.Frame(help_content_frame)
        help_text_frame.grid(row=1, column=0, sticky="nsew")
        help_text_frame.grid_columnconfigure(0, weight=1)
        help_text_frame.grid_rowconfigure(0, weight=1)
        
        # Create text widget with better configuration
        help_text = tk.Text(help_text_frame, wrap=tk.WORD, width=50, height=20, 
                           font=("Arial", 10), bg=FRAME_COLOR, fg=TEXT_COLOR, relief=tk.SUNKEN,
                           padx=10, pady=10, state=tk.NORMAL)
        help_scrollbar = ttk.Scrollbar(help_text_frame, orient="vertical", command=help_text.yview)
        help_text.configure(yscrollcommand=help_scrollbar.set)
        
        help_text.grid(row=0, column=0, sticky="nsew")
        help_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Insert help content immediately
        help_content = self.app.get_help_content()
        if help_content.strip():
            help_text.insert(tk.END, help_content)
            print(f"✅ Help tab: Inserted {len(help_content)} characters of help content")
        else:
            # Fallback content if help content is empty
            fallback_content = """
STOCK PREDICTION GUI - QUICK HELP
================================

OVERVIEW
--------
This GUI provides neural network-based stock price prediction with advanced visualization.

QUICK START
-----------
1. Select a data file in the Data Selection tab
2. Choose features and target variable
3. Configure training parameters
4. Click "Start Training"
5. Monitor progress in Training Results tab
6. Use Model Management for predictions

TABS GUIDE
----------
• Data Selection: Load and configure data
• Training Parameters: Set model parameters
• Model Management: Load models and make predictions
• Plot Controls: Configure 3D visualizations
• Help (?): This help section

For detailed information, use the buttons below.
"""
            help_text.insert(tk.END, fallback_content)
            print("✅ Help tab: Inserted fallback help content")
        
        # Make read-only after inserting content
        help_text.config(state=tk.DISABLED) 