import tkinter as tk
from tkinter import ttk
from gui.theme import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import pandas as pd

class ControlPanel:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.frame = ttk.Frame(master)
        self.setup_ui()

    def setup_ui(self):
        print("🎛️ Setting up ControlPanel UI...")
        
        # Add a title label to make it clear this is the control panel
        title_label = ttk.Label(self.frame, text="CONTROL PANEL", 
                               style="Bold.TLabel", font=("Arial", 14, "bold"))
        title_label.pack(side=tk.TOP, pady=(5, 10))
        
        # Create notebook for different control sections
        self.app.control_notebook = ttk.Notebook(self.frame)
        self.app.control_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        print("✅ Control notebook created")
        
        # Data Selection Tab
        print("📊 Creating Data Selection tab...")
        data_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(data_frame, text="📊 Data Selection")
        data_frame.grid_columnconfigure(0, weight=1)
        
        # Data file selection with history
        data_label = ttk.Label(data_frame, text="Data File:", style="Bold.TLabel")
        data_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        data_entry_frame = ttk.Frame(data_frame)
        data_entry_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        data_entry_frame.grid_columnconfigure(0, weight=1)
        data_entry_frame.grid_columnconfigure(1, weight=0)
        data_entry_frame.grid_columnconfigure(2, weight=0)
        
        # Use combobox instead of entry for data file
        self.app.data_file_combo = ttk.Combobox(data_entry_frame, textvariable=self.app.data_file_var, 
                                               values=self.app.data_file_history, state="normal")
        self.app.data_file_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.app.data_file_combo.bind('<<ComboboxSelected>>', self.app.on_data_file_combo_select)
        
        browse_btn = tk.Button(data_entry_frame, text="📁 Browse", command=self.app.browse_data_file, 
                              bg="#4A90E2", fg="white", relief="raised", bd=2)
        browse_btn.grid(row=0, column=1, padx=5, pady=2)
        
        refresh_btn = tk.Button(data_entry_frame, text="🔄 Refresh", command=self.app.refresh_data_files, 
                               bg="#28A745", fg="white", relief="raised", bd=2)
        refresh_btn.grid(row=0, column=2, padx=5, pady=2)
        print("✅ Data file combobox with history created and placed")
        
        # Data file size and memory usage labels
        self.app.data_file_size_var = tk.StringVar(value="File size: N/A")
        self.app.data_memory_size_var = tk.StringVar(value="Loaded size: N/A")
        self.app.data_file_size_label = ttk.Label(data_frame, textvariable=self.app.data_file_size_var, foreground="green")
        self.app.data_file_size_label.grid(row=1, column=2, sticky="w", padx=(10, 0))
        self.app.data_memory_size_label = ttk.Label(data_frame, textvariable=self.app.data_memory_size_var, foreground="green")
        self.app.data_memory_size_label.grid(row=1, column=3, sticky="w", padx=(10, 0))

        def update_data_size_labels(event=None):
            """Update data file size and memory size labels."""
            selected_file = self.app.data_file_var.get()
            if selected_file and os.path.exists(selected_file):
                try:
                    # Get file size
                    file_size = os.path.getsize(selected_file)
                    file_size_str = f"File size: {file_size:,} bytes"
                    self.app.data_file_size_var.set(file_size_str)
                    
                    # Get data size (approximate)
                    df = pd.read_csv(selected_file)
                    data_size = df.memory_usage(deep=True).sum()
                    data_size_str = f"Loaded size: {data_size:,} bytes"
                    self.app.data_memory_size_var.set(data_size_str)
                except Exception as e:
                    self.app.data_file_size_var.set("File size: Error")
                    self.app.data_memory_size_var.set("Loaded size: Error")
            else:
                self.app.data_file_size_var.set("File size: N/A")
                self.app.data_memory_size_var.set("Loaded size: N/A")

        # Combined function that handles both feature loading and size updates
        def on_data_file_selected(event=None):
            """Handle data file selection - load features and update size labels."""
            # First call the main GUI's data file selection handler
            self.app.on_data_file_combo_select(event)
            # Then update the size labels
            update_data_size_labels(event)

        self.app.data_file_combo.bind('<<ComboboxSelected>>', on_data_file_selected)
        browse_btn.config(command=lambda: [self.app.browse_data_file(), update_data_size_labels()])
        # Also update on startup if a file is pre-selected
        update_data_size_labels()
        
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
        
        # Lock status indicator
        lock_status_frame = ttk.Frame(data_frame)
        lock_status_frame.grid(row=5, column=0, sticky="ew", pady=(10, 5))
        lock_status_frame.grid_columnconfigure(0, weight=1)
        
        lock_status_label = ttk.Label(lock_status_frame, text="Lock Status:", style="Bold.TLabel")
        lock_status_label.grid(row=0, column=0, sticky="w")
        
        self.app.lock_status_display = ttk.Label(lock_status_frame, textvariable=self.app.lock_status_var, 
                                                foreground="green", font=("Arial", 10, "bold"))
        self.app.lock_status_display.grid(row=1, column=0, sticky="w", pady=(2, 0))
        
        # Target feature selection
        target_label = ttk.Label(data_frame, text="Target Feature:", style="Bold.TLabel")
        target_label.grid(row=6, column=0, sticky="w", pady=(10, 5))
        
        self.app.target_combo = ttk.Combobox(data_frame, state="readonly", width=20)
        self.app.target_combo.grid(row=7, column=0, sticky="ew", pady=(0, 10))
        
        # Output directory with history
        output_label = ttk.Label(data_frame, text="Output Directory:", style="Bold.TLabel")
        output_label.grid(row=8, column=0, sticky="w", pady=(10, 5))
        
        output_entry_frame = ttk.Frame(data_frame)
        output_entry_frame.grid(row=9, column=0, sticky="ew", pady=(0, 10))
        output_entry_frame.grid_columnconfigure(0, weight=1)
        output_entry_frame.grid_columnconfigure(1, weight=0)
        
        # Use combobox instead of entry for output directory
        self.app.output_dir_combo = ttk.Combobox(output_entry_frame, textvariable=self.app.output_dir_var,
                                                values=self.app.output_dir_history, state="normal")
        self.app.output_dir_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.app.output_dir_combo.bind('<<ComboboxSelected>>', self.app.on_output_dir_combo_select)
        
        output_browse_btn = tk.Button(output_entry_frame, text="📁 Browse", command=self.app.browse_output_dir, 
                                     bg="#4A90E2", fg="white", relief="raised", bd=2)
        output_browse_btn.grid(row=0, column=1, padx=5, pady=2)
        print("✅ Output directory combobox with history created and placed")
        print("✅ Data Selection tab created")
        
        # Training Parameters Tab
        print("⚙️ Creating Training Parameters tab...")
        training_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(training_frame, text="⚙️ Training Parameters")
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
        
        # Epochs
        epochs_label = ttk.Label(training_frame, text="Epochs:", style="Bold.TLabel")
        epochs_label.grid(row=6, column=0, sticky="w", pady=(0, 5))
        
        epochs_entry = ttk.Entry(training_frame, textvariable=self.app.epochs_var, width=10)
        epochs_entry.grid(row=7, column=0, sticky="w", pady=(0, 10))
        
        # Early Stopping Patience
        patience_label = ttk.Label(training_frame, text="Early Stopping Patience:", style="Bold.TLabel")
        patience_label.grid(row=8, column=0, sticky="w", pady=(0, 5))
        
        patience_entry = ttk.Entry(training_frame, textvariable=self.app.patience_var, width=10)
        patience_entry.grid(row=9, column=0, sticky="w", pady=(0, 10))
        
        # History Interval
        history_interval_label = ttk.Label(training_frame, text="History Save Interval:", style="Bold.TLabel")
        history_interval_label.grid(row=10, column=0, sticky="w", pady=(0, 5))
        
        history_interval_entry = ttk.Entry(training_frame, textvariable=self.app.history_interval_var, width=10)
        history_interval_entry.grid(row=11, column=0, sticky="w", pady=(0, 10))
        
        # Validation Split
        validation_split_label = ttk.Label(training_frame, text="Validation Split (%):", style="Bold.TLabel")
        validation_split_label.grid(row=12, column=0, sticky="w", pady=(0, 5))
        
        validation_split_entry = ttk.Entry(training_frame, textvariable=self.app.validation_split_var, width=10)
        validation_split_entry.grid(row=13, column=0, sticky="w", pady=(0, 10))
        
        # Random Seed
        random_seed_label = ttk.Label(training_frame, text="Random Seed:", style="Bold.TLabel")
        random_seed_label.grid(row=14, column=0, sticky="w", pady=(0, 5))
        
        random_seed_entry = ttk.Entry(training_frame, textvariable=self.app.random_seed_var, width=10)
        random_seed_entry.grid(row=15, column=0, sticky="w", pady=(0, 10))
        
        # Training Options Frame
        training_options_frame = ttk.LabelFrame(training_frame, text="Training Options")
        training_options_frame.grid(row=16, column=0, sticky="ew", pady=(10, 10))
        training_options_frame.grid_columnconfigure(0, weight=1)
        
        # Save History Checkbox
        save_history_check = ttk.Checkbutton(training_options_frame, text="Save Weight History", 
                                            variable=self.app.save_history_var)
        save_history_check.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Memory Optimization Checkbox
        memory_opt_check = ttk.Checkbutton(training_options_frame, text="Memory Optimization", 
                                          variable=self.app.memory_opt_var)
        memory_opt_check.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Training button
        self.app.train_button = ttk.Button(training_frame, text="Start Training", command=self.app.start_training)
        self.app.train_button.grid(row=17, column=0, sticky="ew", pady=(10, 0))
        
        # Live Training button for Error loss
        self.app.live_training_button = ttk.Button(training_frame, text="📊 Live Training (Error Loss)", command=self.app.start_live_training)
        self.app.live_training_button.grid(row=18, column=0, sticky="ew", pady=(10, 0))
        
        # Cache clear button
        self.app.cache_clear_btn = ttk.Button(training_frame, text="Clear Cache", command=self.app.clear_cache_only)
        self.app.cache_clear_btn.grid(row=19, column=0, sticky="ew", pady=(10, 0))
        print("✅ Training Parameters tab created")
        
        # Model Management Tab
        print("🏗️ Creating Model Management tab...")
        model_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(model_frame, text="🏗️ Model Management")
        model_frame.grid_columnconfigure(0, weight=1)
        
        # Model Selection Section
        model_section = ttk.LabelFrame(model_frame, text="Model Selection")
        model_section.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 15))
        model_section.grid_columnconfigure(0, weight=1)
        
        # Model selection
        model_label = ttk.Label(model_section, text="Select Model:", style="Bold.TLabel")
        model_label.grid(row=0, column=0, sticky="w", pady=(10, 5))
        
        self.app.model_combo = ttk.Combobox(model_section, state="readonly", height=8)
        self.app.model_combo.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.app.model_combo.bind('<<ComboboxSelected>>', self.app.on_model_select)
        
        # Model Action Buttons Section
        model_actions_section = ttk.LabelFrame(model_frame, text="Model Actions")
        model_actions_section.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        model_actions_section.grid_columnconfigure(0, weight=1)
        model_actions_section.grid_columnconfigure(1, weight=1)
        model_actions_section.grid_columnconfigure(2, weight=1)
        
        # First row of buttons
        refresh_btn = ttk.Button(model_actions_section, text="🔄 Refresh Models", command=self.app.refresh_models)
        refresh_btn.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        predict_btn = ttk.Button(model_actions_section, text="📊 Make Prediction", command=self.app.make_prediction)
        predict_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        delete_btn = ttk.Button(model_actions_section, text="🗑️ Delete Model", command=self.app.delete_selected_model)
        delete_btn.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        # MPEG Generation Section
        mpeg_section = ttk.LabelFrame(model_frame, text="MPEG Animation Generation")
        mpeg_section.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 15))
        mpeg_section.grid_columnconfigure(0, weight=1)
        
        # MPEG Generation button
        self.app.mpeg_generation_button = ttk.Button(mpeg_section, text="🎬 Create MPEG Movie", 
                                                    command=self.app.generate_mpeg_animation)
        self.app.mpeg_generation_button.grid(row=0, column=0, padx=10, pady=(15, 10), sticky="ew")
        
        # MPEG Generation Progress Section
        mpeg_progress_frame = ttk.Frame(mpeg_section)
        mpeg_progress_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        mpeg_progress_frame.grid_columnconfigure(0, weight=1)
        
        # MPEG progress label
        self.app.mpeg_progress_label = ttk.Label(mpeg_progress_frame, text="MPEG Generation Status:", style="Bold.TLabel")
        self.app.mpeg_progress_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # MPEG progress bar - make it larger
        self.app.mpeg_progress_bar = ttk.Progressbar(mpeg_progress_frame, mode='indeterminate', length=400)
        self.app.mpeg_progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        
        # MPEG status text
        self.app.mpeg_status_var = tk.StringVar(value="Ready to generate MPEG")
        self.app.mpeg_status_text = ttk.Label(mpeg_progress_frame, textvariable=self.app.mpeg_status_var, 
                                             foreground="gray", font=("Arial", 10))
        self.app.mpeg_status_text.grid(row=2, column=0, sticky="w")
        
        # Prediction Files Section
        pred_files_section = ttk.LabelFrame(model_frame, text="Prediction Files")
        pred_files_section.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 15))
        pred_files_section.grid_columnconfigure(0, weight=1)
        pred_files_section.grid_rowconfigure(1, weight=1)
        
        # Prediction files listbox
        self.app.prediction_files_listbox = tk.Listbox(pred_files_section, height=8, selectmode=tk.SINGLE)
        self.app.prediction_files_listbox.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 10))
        self.app.prediction_files_listbox.bind('<<ListboxSelect>>', self.app.on_prediction_file_select)
        
        # Scrollbar for prediction files
        pred_files_scrollbar = ttk.Scrollbar(pred_files_section, orient="vertical", command=self.app.prediction_files_listbox.yview)
        pred_files_scrollbar.grid(row=0, column=1, sticky="ns", pady=(15, 10))
        self.app.prediction_files_listbox.configure(yscrollcommand=pred_files_scrollbar.set)
        
        # Prediction files buttons
        pred_files_btn_frame = ttk.Frame(pred_files_section)
        pred_files_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))
        pred_files_btn_frame.grid_columnconfigure(0, weight=1)
        pred_files_btn_frame.grid_columnconfigure(1, weight=1)
        
        refresh_pred_btn = ttk.Button(pred_files_btn_frame, text="🔄 Refresh Prediction Files", 
                                     command=self.app.refresh_prediction_files)
        refresh_pred_btn.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        view_pred_btn = ttk.Button(pred_files_btn_frame, text="📊 View Prediction Results", 
                                  command=self.app.view_prediction_results)
        view_pred_btn.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        
        # Panel Control Section
        panel_control_section = ttk.LabelFrame(model_frame, text="Results Panel Control")
        panel_control_section.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 15))
        panel_control_section.grid_columnconfigure(0, weight=1)
        panel_control_section.grid_columnconfigure(1, weight=1)
        
        toggle_panel_btn = ttk.Button(panel_control_section, text="🔄 Toggle Results Panel", 
                                     command=self.app.toggle_right_panel)
        toggle_panel_btn.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        show_panel_btn = ttk.Button(panel_control_section, text="📋 Show Results Panel", 
                                   command=self.app.show_right_panel)
        show_panel_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        print("✅ Model Management tab created")
        
        # Plot Controls Tab
        print("📈 Creating Plot Controls tab...")
        plot_controls_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(plot_controls_frame, text="📈 Plot Controls")
        plot_controls_frame.grid_columnconfigure(0, weight=1)
        plot_controls_frame.grid_rowconfigure(3, weight=1)  # Row 3 for the plot

        # Floating 3D Controls Section - moved to top
        controls_section = ttk.LabelFrame(plot_controls_frame, text="3D Visualization Controls")
        controls_section.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 15))
        controls_section.grid_columnconfigure(0, weight=1)
        
        # Add floating 3D controls button
        self.app.floating_3d_controls_btn = ttk.Button(controls_section, text="🎮 Open Floating 3D Controls", 
                                                      command=self.app.show_3d_controls)
        self.app.floating_3d_controls_btn.pack(fill="x", padx=10, pady=15)

        # Visualization Type Dropdown
        vis_type_frame = ttk.Frame(controls_section)
        vis_type_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(vis_type_frame, text="3D Plot Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.app.vis_type_var = tk.StringVar(value="Wireframe")
        self.app.vis_type_combo = ttk.Combobox(
            vis_type_frame,
            textvariable=self.app.vis_type_var,
            values=["Wireframe", "Surface", "Contour", "Scatter", "Bar3D", "Trisurf", "Voxels"],  # Multiple 3D plot types
            state="readonly",
            width=15
        )
        self.app.vis_type_combo.pack(side=tk.LEFT, padx=(0, 5))
        # Add a button to update the plot
        ttk.Button(vis_type_frame, text="Update Plot", command=self.app.update_3d_plot_type).pack(side=tk.LEFT, padx=(5, 0))

        # Add 3D view control buttons
        view_btn_frame = ttk.Frame(controls_section)
        view_btn_frame.pack(fill="x", pady=(0, 10))
        view_btn_frame.grid_columnconfigure(0, weight=1)
        view_btn_frame.grid_columnconfigure(1, weight=1)
        view_btn_frame.grid_columnconfigure(2, weight=1)
        view_btn_frame.grid_columnconfigure(3, weight=1)

        ttk.Button(view_btn_frame, text="🔄 Reset", command=self.app.reset_3d_view).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(view_btn_frame, text="👁 Top", command=self.app.set_top_view).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ttk.Button(view_btn_frame, text="👁 Side", command=self.app.set_side_view).grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        ttk.Button(view_btn_frame, text="👁 Iso", command=self.app.set_isometric_view).grid(row=0, column=3, padx=2, pady=2, sticky="ew")

        # Add info label
        info_label = ttk.Label(controls_section, 
                              text="💡 Click to open 3D controls in a separate floating window for better control",
                              font=("Arial", 9), foreground="blue")
        info_label.pack(pady=(0, 10))

        # Animation Files Section - moved below floating controls
        mpeg_section = ttk.LabelFrame(plot_controls_frame, text="Animation Files (MPEG/GIF/MP4)")
        mpeg_section.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        mpeg_section.grid_columnconfigure(0, weight=1)

        # Add helpful instructions
        instructions_frame = ttk.Frame(mpeg_section)
        instructions_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        instructions_label = ttk.Label(instructions_frame, 
                                      text="💡 Tip: Click 'Browse' to navigate to model directories and find animation files in their 'plots' subdirectories",
                                      font=("Arial", 9), foreground="blue")
        instructions_label.pack()

        # MPEG files listbox and controls
        mpeg_controls_frame = ttk.Frame(mpeg_section)
        mpeg_controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        mpeg_controls_frame.grid_columnconfigure(0, weight=1)

        # MPEG files listbox
        mpeg_listbox_frame = ttk.Frame(mpeg_controls_frame)
        mpeg_listbox_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        mpeg_listbox_frame.grid_columnconfigure(0, weight=1)
        mpeg_listbox_frame.grid_rowconfigure(0, weight=1)

        self.app.mpeg_files_listbox = tk.Listbox(mpeg_listbox_frame, height=6, selectmode=tk.SINGLE)
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
        plot_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        plot_frame.grid_columnconfigure(0, weight=1)
        plot_frame.grid_rowconfigure(0, weight=1)
        self.app.plot_frame = plot_frame  # Store for docking

        # Create matplotlib figure for 3D gradient descent with better error handling
        try:
            print("📊 Creating 3D plot...")
            self.app.gd3d_fig = plt.Figure(figsize=(8, 6))
            self.app.gd3d_ax = self.app.gd3d_fig.add_subplot(111, projection="3d")

            # Create canvas and embed in the plot frame
            self.app.gd3d_canvas = FigureCanvasTkAgg(self.app.gd3d_fig, plot_frame)
            self.app.gd3d_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

            # Add toolbar with error handling
            try:
                from gui.components.grid_matplotlib_toolbar import GridMatplotlibToolbar
                toolbar = GridMatplotlibToolbar(self.app.gd3d_canvas, plot_frame)
                toolbar.grid(row=1, column=0, sticky="ew")
                self.app.gd3d_toolbar = toolbar
                print("✅ Matplotlib toolbar created successfully")
            except Exception as toolbar_error:
                print(f"⚠️ Warning: Could not create matplotlib toolbar: {toolbar_error}")
                # Create a simple frame instead of toolbar
                toolbar_placeholder = ttk.Frame(plot_frame)
                toolbar_placeholder.grid(row=1, column=0, sticky="ew")
                ttk.Label(toolbar_placeholder, text="Toolbar not available", 
                         foreground="orange").pack()
                self.app.gd3d_toolbar = None

            # Add enhanced Pop Out/Dock button with better styling
            popout_frame = ttk.Frame(plot_frame)
            popout_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
            popout_frame.grid_columnconfigure(0, weight=1)
            popout_frame.grid_columnconfigure(1, weight=1)
            
            # Store reference to the button for dynamic text updates
            self.app.popout_btn = ttk.Button(popout_frame, text="🎮 Pop Out 3D Viewer", 
                                            command=self.app.popout_3d_viewer)
            self.app.popout_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
            
            # Add a help button for 3D viewer
            help_btn = ttk.Button(popout_frame, text="❓ 3D Help", 
                                 command=self.show_3d_help)
            help_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))

            # Initialize with placeholder - use proper 3D text placement
            self.app.gd3d_ax.text2D(0.5, 0.5, "3D Gradient Descent Animation\nSelect a model and click Play to start", 
                                  ha="center", va="center", transform=self.app.gd3d_ax.transAxes,
                                  fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            self.app.gd3d_ax.axis("off")

            try:
                self.app.gd3d_canvas.draw_idle()
                print("✅ 3D plot canvas drawn successfully")
            except Exception as canvas_error:
                print(f"⚠️ Warning: Could not draw 3D canvas: {canvas_error}")

            # Ensure the 3D axes are accessible to main GUI
            print("✅ 3D axes made accessible to main GUI")
            
        except Exception as plot_error:
            print(f"❌ Error creating 3D plot: {plot_error}")
            # Create a simple placeholder instead of 3D plot
            placeholder_frame = ttk.Frame(plot_frame)
            placeholder_frame.grid(row=0, column=0, sticky="nsew")
            placeholder_frame.grid_columnconfigure(0, weight=1)
            placeholder_frame.grid_rowconfigure(0, weight=1)
            
            placeholder_label = ttk.Label(placeholder_frame, 
                                        text="3D Plot Not Available\nCheck matplotlib installation",
                                        font=("Arial", 12), foreground="red")
            placeholder_label.grid(row=0, column=0, sticky="nsew")
            
            # Set dummy attributes to prevent errors
            self.app.gd3d_fig = None
            self.app.gd3d_ax = None
            self.app.gd3d_canvas = None
            self.app.gd3d_toolbar = None

        print("✅ Plot Controls tab created successfully")
        
        # Help Tab
        print("❓ Creating Help tab...")
        help_frame = ttk.Frame(self.app.control_notebook)
        self.app.control_notebook.add(help_frame, text="❓ Help")
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
        print("✅ Help tab created")
        
        print("✅ ControlPanel UI setup completed successfully") 

    def show_3d_help(self):
        """Show help for 3D viewer functionality."""
        help_text = """
🎮 3D Viewer Help
================

POP OUT/DOCK FEATURES:
• Click "Pop Out 3D Viewer" to open in a separate window
• Use "Dock Viewer" to return to the main interface
• Fullscreen mode available in floating window
• Floating window can be resized and moved

3D NAVIGATION:
• Mouse drag: Rotate view
• Mouse wheel: Zoom in/out
• Right-click drag: Pan view
• Use toolbar buttons for preset views

PLOT TYPES:
• Wireframe: Wire mesh visualization
• Surface: Solid surface with colors
• Contour: 2D contour projection
• Scatter: 3D point cloud
• Bar3D: 3D bar chart
• Trisurf: Triangular surface
• Voxels: 3D volume rendering

ANIMATION:
• Load model with weights history
• Click Play to start gradient descent animation
• Adjust speed and playback options
• Save animations as MP4/GIF files

For more detailed help, see the Help tab.
"""
        
        # Create help window
        help_window = tk.Toplevel(self.app.root)
        help_window.title("3D Viewer Help")
        help_window.geometry("500x600")
        help_window.resizable(True, True)
        
        # Configure grid
        help_window.grid_columnconfigure(0, weight=1)
        help_window.grid_rowconfigure(0, weight=1)
        
        # Create text widget
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10,
                             font=("Arial", 10), bg="white", fg="black")
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Insert help content
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED) 