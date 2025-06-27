"""
Control Plots Panel Widget

This module provides a panel for controlling 3D Matplotlib plots with floating windows.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow

class ControlPlotsPanel:
    """Panel for controlling 3D Matplotlib plots."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create the main frame
        self.frame = ttk.Frame(parent, padding="10")
        
        # Initialize state
        self.floating_window = None
        self.current_model = None
        
        # Create the interface
        self.create_interface()
        
        # Load initial state
        self.load_initial_state()
    
    def create_interface(self):
        """Create the control plots interface."""
        # Title
        title_label = ttk.Label(self.frame, text="3D Plot Controls", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Plot Type Selection
        plot_type_frame = ttk.LabelFrame(self.frame, text="Plot Type", padding="10")
        plot_type_frame.pack(fill="x", pady=(0, 10))
        
        self.plot_type_var = tk.StringVar(value="3D Scatter")
        plot_types = ["3D Scatter", "3D Surface", "3D Wireframe", "3D Gradient Descent", "2D Scatter", "1D Line"]
        
        for plot_type in plot_types:
            ttk.Radiobutton(plot_type_frame, text=plot_type, 
                           variable=self.plot_type_var, value=plot_type,
                           command=self.on_plot_type_change).pack(anchor="w")
        
        # Model Selection
        model_frame = ttk.LabelFrame(self.frame, text="Model Selection", padding="10")
        model_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(model_frame, text="Select Model:").pack(anchor="w")
        
        self.model_combo = ttk.Combobox(model_frame, state="readonly", width=40)
        self.model_combo.pack(fill="x", pady=(5, 0))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_select)
        
        # Plot Controls
        controls_frame = ttk.LabelFrame(self.frame, text="Plot Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Color scheme
        color_frame = ttk.Frame(controls_frame)
        color_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(color_frame, text="Color Scheme:").pack(side="left")
        self.color_var = tk.StringVar(value="viridis")
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_var,
                                  values=["viridis", "plasma", "inferno", "magma", "coolwarm", "rainbow"],
                                  state="readonly", width=15)
        color_combo.pack(side="right")
        
        # Point size
        size_frame = ttk.Frame(controls_frame)
        size_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(size_frame, text="Point Size:").pack(side="left")
        self.point_size_var = tk.StringVar(value="20")
        size_scale = ttk.Scale(size_frame, from_=1, to=100, variable=self.point_size_var,
                              orient="horizontal")
        size_scale.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Animation controls
        anim_frame = ttk.LabelFrame(self.frame, text="Animation", padding="5")
        anim_frame.pack(fill="x", pady=(5, 0))
        
        self.animation_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(anim_frame, text="Enable Animation", 
                       variable=self.animation_var).pack(side="left")
        
        ttk.Label(anim_frame, text="Speed:").pack(side="left", padx=(20, 5))
        self.anim_speed_var = tk.StringVar(value="1.0")
        speed_combo = ttk.Combobox(anim_frame, textvariable=self.anim_speed_var,
                                  values=["0.5", "1.0", "1.5", "2.0"], 
                                  state="readonly", width=8)
        speed_combo.pack(side="left")
        
        # Gradient Descent specific controls
        gd_frame = ttk.LabelFrame(self.frame, text="Gradient Descent Controls", padding="5")
        gd_frame.pack(fill="x", pady=(10, 0))
        
        # W1 and W2 ranges
        ranges_frame = ttk.Frame(gd_frame)
        ranges_frame.pack(fill="x", pady=(0, 5))
        
        # W1 range
        w1_frame = ttk.Frame(ranges_frame)
        w1_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Label(w1_frame, text="W1 Range:").pack(anchor="w")
        w1_range_frame = ttk.Frame(w1_frame)
        w1_range_frame.pack(fill="x")
        
        self.w1_min_var = tk.StringVar(value="-2.0")
        self.w1_max_var = tk.StringVar(value="2.0")
        ttk.Entry(w1_range_frame, textvariable=self.w1_min_var, width=8).pack(side="left")
        ttk.Label(w1_range_frame, text=" to ").pack(side="left")
        ttk.Entry(w1_range_frame, textvariable=self.w1_max_var, width=8).pack(side="left")
        
        # W2 range
        w2_frame = ttk.Frame(ranges_frame)
        w2_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        ttk.Label(w2_frame, text="W2 Range:").pack(anchor="w")
        w2_range_frame = ttk.Frame(w2_frame)
        w2_range_frame.pack(fill="x")
        
        self.w2_min_var = tk.StringVar(value="-2.0")
        self.w2_max_var = tk.StringVar(value="2.0")
        ttk.Entry(w2_range_frame, textvariable=self.w2_min_var, width=8).pack(side="left")
        ttk.Label(w2_range_frame, text=" to ").pack(side="left")
        ttk.Entry(w2_range_frame, textvariable=self.w2_max_var, width=8).pack(side="left")
        
        # Weight indices
        indices_frame = ttk.Frame(gd_frame)
        indices_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(indices_frame, text="W1 Index:").pack(side="left")
        self.w1_index_var = tk.StringVar(value="0")
        ttk.Entry(indices_frame, textvariable=self.w1_index_var, width=5).pack(side="left", padx=(5, 10))
        
        ttk.Label(indices_frame, text="W2 Index:").pack(side="left")
        self.w2_index_var = tk.StringVar(value="0")
        ttk.Entry(indices_frame, textvariable=self.w2_index_var, width=5).pack(side="left", padx=(5, 0))
        
        # Save control
        save_frame = ttk.LabelFrame(self.frame, text="Save", padding="5")
        save_frame.pack(side="right")
        
        # Action Buttons
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Create plot button
        create_btn = ttk.Button(buttons_frame, text="Create 3D Plot", 
                               command=self.create_3d_plot, style="Accent.TButton")
        create_btn.pack(side="left", padx=(0, 10))
        
        # Save plot button
        save_btn = ttk.Button(buttons_frame, text="Save Plot", 
                             command=self.save_plot)
        save_btn.pack(side="left", padx=(0, 10))
        
        # Close window button
        close_btn = ttk.Button(buttons_frame, text="Close Window", 
                              command=self.close_floating_window)
        close_btn.pack(side="left")
        
        # Status
        self.status_var = tk.StringVar(value="Ready to create 3D plots")
        status_label = ttk.Label(self.frame, textvariable=self.status_var, 
                                foreground="blue")
        status_label.pack(pady=(10, 0))
    
    def load_initial_state(self):
        """Load initial state."""
        try:
            # Load available models
            self.refresh_model_list()
            
        except Exception as e:
            self.logger.error(f"Error loading initial state: {e}")
    
    def refresh_model_list(self):
        """Refresh the list of available models."""
        try:
            # Get models from the app
            models = self.app.model_manager.get_available_models()
            
            # Update combo box
            model_names = [os.path.basename(model) for model in models]
            self.model_combo['values'] = model_names
            
            if model_names:
                self.model_combo.set(model_names[0])
                self.current_model = models[0]
            
        except Exception as e:
            self.logger.error(f"Error refreshing model list: {e}")
    
    def on_plot_type_change(self):
        """Handle plot type change."""
        plot_type = self.plot_type_var.get()
        self.status_var.set(f"Plot type changed to: {plot_type}")
    
    def on_model_select(self, event=None):
        """Handle model selection."""
        try:
            selected_index = self.model_combo.current()
            if selected_index >= 0:
                models = self.app.model_manager.get_available_models()
                if selected_index < len(models):
                    self.current_model = models[selected_index]
                    model_name = os.path.basename(self.current_model)
                    self.status_var.set(f"Selected model: {model_name}")
        except Exception as e:
            self.logger.error(f"Error selecting model: {e}")
    
    def create_3d_plot(self):
        """Create a 3D plot in a floating window."""
        try:
            if not self.current_model:
                messagebox.showwarning("No Model", "Please select a model first.")
                return
            
            # Close existing window if any
            if self.floating_window:
                self.floating_window.close()
            
            # Get plot parameters
            plot_params = {
                'plot_type': self.plot_type_var.get(),
                'color_scheme': self.color_var.get(),
                'point_size': int(self.point_size_var.get()),
                'animation_enabled': self.animation_var.get(),
                'animation_speed': float(self.anim_speed_var.get())
            }
            
            # Add gradient descent specific parameters if needed
            if plot_params['plot_type'] == "3D Gradient Descent":
                plot_params.update({
                    'w1_range': [float(self.w1_min_var.get()), float(self.w1_max_var.get())],
                    'w2_range': [float(self.w2_min_var.get()), float(self.w2_max_var.get())],
                    'w1_index': int(self.w1_index_var.get()),
                    'w2_index': int(self.w2_index_var.get()),
                    'n_points': 30,  # Default for gradient descent
                    'line_width': 3,
                    'surface_alpha': 0.6
                })
            
            self.status_var.set("Creating 3D plot...")
            self.parent.update()
            
            # Create floating window
            self.floating_window = Floating3DWindow(
                self.parent,
                self.current_model,
                plot_params,
                on_close=self.on_floating_window_close
            )
            
            self.status_var.set("3D plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating 3D plot: {e}")
            messagebox.showerror("Error", f"Failed to create 3D plot: {e}")
            self.status_var.set("Error creating 3D plot")
    
    def save_plot(self):
        """Save the current plot."""
        try:
            if not self.floating_window:
                messagebox.showwarning("No Plot", "No plot to save. Create a plot first.")
                return
            
            # Get save path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ],
                title="Save 3D Plot"
            )
            
            if file_path:
                self.floating_window.save_plot(file_path)
                self.status_var.set(f"Plot saved to: {os.path.basename(file_path)}")
                
        except Exception as e:
            self.logger.error(f"Error saving plot: {e}")
            messagebox.showerror("Error", f"Failed to save plot: {e}")
            self.status_var.set("Error saving plot")
    
    def close_floating_window(self):
        """Close the floating window."""
        try:
            if self.floating_window:
                self.floating_window.close()
                self.floating_window = None
                self.status_var.set("Floating window closed")
        except Exception as e:
            self.logger.error(f"Error closing floating window: {e}")
    
    def on_floating_window_close(self):
        """Handle floating window close event."""
        self.floating_window = None
        self.status_var.set("3D plot window closed") 