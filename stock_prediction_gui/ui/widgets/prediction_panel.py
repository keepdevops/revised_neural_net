"""
Enhanced Prediction panel for the Stock Prediction GUI.
Features condensed left panel and right panel with live forward pass visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
import time

from .forward_pass_visualizer import ForwardPassVisualizer

class PredictionPanel:
    """Enhanced prediction panel with forward pass visualization."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create the main panel with split layout
        self.frame = ttk.Frame(parent, padding="5")
        self.create_widgets()
    
    def create_widgets(self):
        """Create the panel widgets with split layout."""
        # Create main container with horizontal split
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)
        
        # Configure grid weights for split layout
        main_container.grid_columnconfigure(0, weight=1)  # Left panel
        main_container.grid_columnconfigure(1, weight=2)  # Right panel (visualizer)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create left panel (condensed controls)
        self.create_left_panel(main_container)
        
        # Create right panel (forward pass visualizer)
        self.create_right_panel(main_container)
        
    def create_left_panel(self, parent):
        """Create the condensed left control panel."""
        left_frame = ttk.Frame(parent, padding="5")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Title
        title_label = ttk.Label(left_frame, text="Prediction Controls", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Compact model selection
        self.create_compact_model_section(left_frame)
        
        # Compact data selection
        self.create_compact_data_section(left_frame)
        
        # Compact controls
        self.create_compact_controls_section(left_frame)
        
        # Compact status
        self.create_compact_status_section(left_frame)
        
    def create_compact_model_section(self, parent):
        """Create compact model selection section."""
        # Model frame
        model_frame = ttk.LabelFrame(parent, text="Model", padding="8")
        model_frame.pack(fill="x", pady=(0, 10))
        
        # Model selection in one row
        model_row = ttk.Frame(model_frame)
        model_row.pack(fill="x")
        
        ttk.Label(model_row, text="Model:").pack(side="left")
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_row, textvariable=self.model_var, state="readonly", width=20)
        self.model_combo.pack(side="left", fill="x", expand=True, padx=(5, 5))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_select)
        
        # Enhanced refresh button row with better styling
        btn_row = ttk.Frame(model_frame)
        btn_row.pack(fill="x", pady=(5, 0))
        
        # Refresh button with better styling
        refresh_btn = ttk.Button(btn_row, text="🔄 Refresh Models", command=self.refresh_models, style="Accent.TButton")
        refresh_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Latest button
        latest_btn = ttk.Button(btn_row, text="📋 Latest", width=8, command=self.refresh_and_select_latest)
        latest_btn.pack(side="left", padx=(2, 0))
        
        # Compact model info with refresh status
        self.model_info_var = tk.StringVar(value="Click 'Refresh Models' to load available models")
        ttk.Label(model_frame, textvariable=self.model_info_var, font=("Arial", 8), foreground="gray").pack(anchor="w", pady=(5, 0))
        
    def create_compact_data_section(self, parent):
        """Create compact data selection section."""
        # Data frame
        data_frame = ttk.LabelFrame(parent, text="Data", padding="8")
        data_frame.pack(fill="x", pady=(0, 10))
        
        # Data file selection
        data_row = ttk.Frame(data_frame)
        data_row.pack(fill="x")
        
        ttk.Label(data_row, text="File:").pack(side="left")
        
        self.prediction_data_var = tk.StringVar()
        self.prediction_data_entry = ttk.Entry(data_row, textvariable=self.prediction_data_var, state="readonly")
        self.prediction_data_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        ttk.Button(data_row, text="📁", width=3, command=self.browse_prediction_data).pack(side="right")
        
        # Use current data checkbox
        self.use_current_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(data_frame, text="Use current data", variable=self.use_current_data_var, 
                       command=self.on_use_current_data_change).pack(anchor="w", pady=(5, 0))
        
    def create_compact_controls_section(self, parent):
        """Create compact controls section."""
        # Controls frame
        controls_frame = ttk.LabelFrame(parent, text="Actions", padding="8")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Button grid
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill="x")
        
        # Row 1
        row1 = ttk.Frame(btn_frame)
        row1.pack(fill="x", pady=(0, 5))
        
        self.predict_button = ttk.Button(row1, text="🚀 Predict", command=self.make_prediction)
        self.predict_button.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        ttk.Button(row1, text="📊 Results", command=self.view_results).pack(side="left", fill="x", expand=True, padx=(2, 0))
        
        # Row 2
        row2 = ttk.Frame(btn_frame)
        row2.pack(fill="x")
        
        ttk.Button(row2, text="🗑️ Clear", command=self.clear_results).pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        ttk.Button(row2, text="⚙️ Settings", command=self.show_prediction_settings).pack(side="left", fill="x", expand=True, padx=(2, 0))
        
    def create_compact_status_section(self, parent):
        """Create compact status section."""
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Status", padding="8")
        status_frame.pack(fill="x")
        
        # Status labels
        self.prediction_status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.prediction_status_var, font=("Arial", 9)).pack(anchor="w")
        
        self.prediction_progress_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.prediction_progress_var, font=("Arial", 8), foreground="gray").pack(anchor="w")
        
        # Progress bar
        self.prediction_progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.prediction_progress_bar.pack(fill="x", pady=(5, 0))
        
    def create_right_panel(self, parent):
        """Create the right panel with forward pass visualizer."""
        right_frame = ttk.Frame(parent, padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Create forward pass visualizer
        self.forward_pass_visualizer = ForwardPassVisualizer(right_frame, self.app)
        self.forward_pass_visualizer.frame.pack(fill="both", expand=True)
        
    def show_prediction_settings(self):
        """Show prediction settings dialog."""
        # Simple settings dialog for prediction parameters
        settings_window = tk.Toplevel(self.frame)
        settings_window.title("Prediction Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.frame)
        settings_window.grab_set()
        
        # Center the window
        settings_window.geometry("+%d+%d" % (
            self.frame.winfo_rootx() + 50,
            self.frame.winfo_rooty() + 50
        ))
        
        # Settings content
        content_frame = ttk.Frame(settings_window, padding="20")
        content_frame.pack(fill="both", expand=True)
        
        ttk.Label(content_frame, text="Prediction Settings", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Batch size setting
        batch_frame = ttk.Frame(content_frame)
        batch_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(batch_frame, text="Batch Size:").pack(side="left")
        batch_var = tk.StringVar(value="32")
        batch_entry = ttk.Entry(batch_frame, textvariable=batch_var, width=10)
        batch_entry.pack(side="right")
        
        # Confidence threshold
        conf_frame = ttk.Frame(content_frame)
        conf_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(conf_frame, text="Confidence Threshold:").pack(side="left")
        conf_var = tk.StringVar(value="0.8")
        conf_entry = ttk.Entry(conf_frame, textvariable=conf_var, width=10)
        conf_entry.pack(side="right")
        
        # Save settings button
        ttk.Button(content_frame, text="Save Settings", 
                  command=lambda: self.save_prediction_settings(batch_var.get(), conf_var.get(), settings_window)).pack(pady=(20, 0))
        
    def save_prediction_settings(self, batch_size, confidence, window):
        """Save prediction settings."""
        try:
            # Store settings in app
            self.app.prediction_batch_size = int(batch_size)
            self.app.prediction_confidence = float(confidence)
            window.destroy()
            messagebox.showinfo("Settings", "Prediction settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")
    
    def on_model_select(self, event):
        """Handle model selection with thread safety."""
        try:
            selected_model = self.model_var.get()
            if selected_model:
                # Find the full path of the selected model
                models = self.app.model_manager.get_available_models()
                for model_path in models:
                    if os.path.basename(model_path) == selected_model:
                        self.app.selected_model = model_path
                        # Use the safe update method
                        self.update_model_info(model_path)
                        self.logger.info(f"Model selected: {selected_model}")
                        break
                        
        except Exception as e:
            self.logger.error(f"Error in model selection: {e}")
    
    def on_use_current_data_change(self):
        """Handle use current data checkbox change."""
        if self.use_current_data_var.get():
            if self.app.current_data_file:
                self.prediction_data_var.set(self.app.current_data_file)
                self.prediction_data_entry.config(state="disabled")
            else:
                messagebox.showwarning("No Data", "No data file is currently loaded.")
                self.use_current_data_var.set(False)
        else:
            self.prediction_data_entry.config(state="normal")
    
    def refresh_models(self):
        """Refresh the model list with enhanced feedback."""
        try:
            # Update status
            self.prediction_status_var.set("Refreshing models...")
            self.model_info_var.set("Scanning for available models...")
            
            # Get models from app
            if hasattr(self.app, 'model_manager'):
                models = self.app.model_manager.get_available_models()
                
                if models:
                    # Update the combobox
                    model_names = [os.path.basename(model) for model in models]
                    self.model_combo['values'] = model_names
                    
                    # Update status
                    self.prediction_status_var.set(f"Found {len(models)} models")
                    self.model_info_var.set(f"Available models: {len(models)} (select one from dropdown)")
                    
                    self.logger.info(f"Model list updated with {len(models)} models")
                else:
                    self.prediction_status_var.set("No models found")
                    self.model_info_var.set("No trained models found in output directory")
                    self.model_combo['values'] = []
                    
            else:
                self.prediction_status_var.set("Model manager not available")
                self.model_info_var.set("Cannot refresh models - model manager unavailable")
                
        except Exception as e:
            self.logger.error(f"Error refreshing models: {e}")
            self.prediction_status_var.set("Error refreshing models")
            self.model_info_var.set(f"Refresh failed: {str(e)}")
    
    def refresh_and_select_latest(self):
        """Refresh models and select the latest one with enhanced safety."""
        try:
            # First refresh the model list
            self.refresh_models()
            
            # Wait a moment for the refresh to complete
            self.parent.after(100, self._select_latest_model)
            
        except Exception as e:
            self.logger.error(f"Error in refresh_and_select_latest: {e}")
            self.prediction_status_var.set("Error selecting latest model")
    
    def _select_latest_model(self):
        """Safely select the latest model from the dropdown."""
        try:
            # Get the current values in the combobox
            values = self.model_combo['values']
            
            if values:
                # Select the first (latest) model
                latest_model = values[0]
                self.model_var.set(latest_model)
                
                # Trigger the model selection event
                self.on_model_select(None)
                
                self.prediction_status_var.set(f"Selected latest model: {latest_model}")
                self.logger.info(f"Latest model selected: {latest_model}")
            else:
                self.prediction_status_var.set("No models available to select")
                
        except Exception as e:
            self.logger.error(f"Error selecting latest model: {e}")
            self.prediction_status_var.set("Error selecting latest model")
    
    def browse_prediction_data(self):
        """Browse for prediction data file."""
        filename = filedialog.askopenfilename(
            title="Select Prediction Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.prediction_data_var.set(filename)
    
    def make_prediction(self):
        """Make prediction with forward pass visualization."""
        if not self.app.selected_model:
            messagebox.showwarning("No Model", "Please select a model first.")
            return
        
        # Validate the selected model and try to find a working one if needed
        if not self._validate_and_fix_model_selection():
            return
        
        # Get prediction data file
        if self.use_current_data_var.get():
            data_file = self.app.current_data_file
        else:
            data_file = self.prediction_data_var.get()
        
        if not data_file or not os.path.exists(data_file):
            messagebox.showwarning("No Data", "Please select a valid prediction data file.")
            return
        
        # Start forward pass visualization
        self.forward_pass_visualizer.start_prediction_mode()
        
        # Get prediction parameters
        params = self.get_prediction_params()
        
        # Start prediction with visualization callback
        if self.app.start_prediction(params, self.on_prediction_progress):
            self.predict_button.config(state="disabled")
            self.prediction_progress_bar.start()
            self.prediction_status_var.set("Making predictions...")
    
    def on_prediction_progress(self, weights, bias, prediction, input_data, progress):
        """Callback for prediction progress with forward pass data."""
        try:
            # Update forward pass visualizer
            self.forward_pass_visualizer.add_forward_pass_data(weights, bias, prediction, input_data)
            
            # Update progress
            self.prediction_progress_var.set(f"Progress: {progress:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error in prediction progress callback: {e}")
    
    def _validate_and_fix_model_selection(self):
        """Validate and fix model selection with enhanced safety."""
        try:
            # Check if a model is selected
            if not self.app.selected_model:
                # DISABLED: Automatic model selection to prevent segmentation faults
                # Users can manually select models from the dropdown
                # working_model = self._find_working_model()
                # if working_model:
                #     self.app.selected_model = working_model
                #     self._update_model_selection_display(working_model)
                #     messagebox.showinfo("Model Fixed", f"Auto-selected working model: {os.path.basename(working_model)}")
                #     return True
                # else:
                #     messagebox.showerror("No Working Model", "No working model found. Please train a new model first.")
                #     return False
                
                messagebox.showwarning("No Model Selected", "Please select a model from the dropdown list.")
                return False
        
            # Check if the model has valid files
            if not self._has_valid_model_files(self.app.selected_model):
                messagebox.showwarning("Invalid Model", f"Selected model appears to be invalid: {self.app.selected_model}")
                
                # DISABLED: Automatic model selection to prevent segmentation faults
                # Users can manually select models from the dropdown
                # working_model = self._find_working_model()
                # if working_model:
                #     self.app.selected_model = working_model
                #     self._update_model_selection_display(working_model)
                #     messagebox.showinfo("Model Fixed", f"Auto-selected working model: {os.path.basename(working_model)}")
                #     return True
                # else:
                #     messagebox.showerror("No Working Model", "No working model found. Please train a new model first.")
                #     return False
                
                messagebox.showwarning("Invalid Model", "Please select a different model from the dropdown list.")
                return False
        
            return True
            
        except Exception as e:
            self.logger.error(f"Error in _validate_and_fix_model_selection: {e}")
            return False
    
    def _has_valid_model_files(self, model_dir):
        """Check if model directory has valid model files."""
        try:
            # Check for essential files - updated to match actual model structure
            required_files = ['stock_model.npz', 'feature_info.json']
            optional_files = ['weights_history', 'plots', 'training_data.csv', 'training_losses.csv']
            
            # Check if all required files exist
            for file in required_files:
                if not os.path.exists(os.path.join(model_dir, file)):
                    self.logger.debug(f"Missing required file: {file} in {model_dir}")
                    return False
            
            # Check if at least one optional directory or file exists
            has_optional = any(os.path.exists(os.path.join(model_dir, file)) for file in optional_files)
            
            if not has_optional:
                self.logger.debug(f"No optional files found in {model_dir}")
            
            return has_optional
            
        except Exception as e:
            self.logger.error(f"Error checking model files: {e}")
            return False
    
    def _find_working_model(self):
        """Find a working model from available models."""
        try:
            models = self.app.model_manager.get_available_models()
            
            # Sort by modification time (newest first)
            models_with_time = []
            for model_path in models:
                if os.path.exists(model_path):
                    mod_time = os.path.getmtime(model_path)
                    models_with_time.append((model_path, mod_time))
            
            # Sort by modification time (newest first)
            models_with_time.sort(key=lambda x: x[1], reverse=True)
            
            # Find first working model
            for model_path, _ in models_with_time:
                if self._has_valid_model_files(model_path):
                    return model_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding working model: {e}")
            return None
    
    def _update_model_selection_display(self, model_path):
        """Update the model selection display with maximum thread safety."""
        try:
            # Ensure we're on the main thread with additional delay
            if hasattr(self, 'app') and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                # Use a longer delay to ensure GUI is completely stable
                self.app.main_window.root.after(150, lambda: self._delayed_safe_update_model_selection_display(model_path))
            else:
                # Fallback to direct call if main window not available
                self._delayed_safe_update_model_selection_display(model_path)
                
        except Exception as e:
            self.logger.error(f"Error in _update_model_selection_display: {e}")
    
    def _delayed_safe_update_model_selection_display(self, model_path):
        """Delayed safe update of model selection display with maximum safety measures."""
        try:
            # Add additional delay for memory stability
            if hasattr(self, 'app') and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                self.app.main_window.root.after(50, lambda: self._final_safe_update_model_selection_display(model_path))
            else:
                self._final_safe_update_model_selection_display(model_path)
                
        except Exception as e:
            self.logger.error(f"Error in delayed_safe_update_model_selection_display: {e}")
    
    def _final_safe_update_model_selection_display(self, model_path):
        """Final safe update of model selection display with comprehensive safety checks."""
        try:
            # Validate model path
            if not model_path or not os.path.exists(model_path):
                self.logger.warning(f"Invalid model path for selection display: {model_path}")
                return
                
            # Check if the widget is still valid
            if not hasattr(self, 'model_var') or self.model_var is None:
                self.logger.warning("Model variable not available for selection display")
                return
                
            # Update the selection with maximum error handling
            try:
                model_name = os.path.basename(model_path)
                if hasattr(self.model_var, 'set'):
                    # Use a try-catch around the actual set operation
                    try:
                        self.model_var.set(model_name)
                        self.logger.info(f"Model selection updated to: {model_name}")
                    except Exception as set_error:
                        self.logger.error(f"Error in model_var.set(): {set_error}")
                        return
                else:
                    self.logger.warning("Model variable set method not available for selection")
            except Exception as e:
                self.logger.error(f"Error updating model selection: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in final_safe_update_model_selection_display: {e}")
    
    def view_results(self):
        """View prediction results."""
        # This will be handled by the main window
        pass
    
    def clear_results(self):
        """Clear prediction results."""
        self.prediction_status_var.set("Ready")
        self.prediction_progress_var.set("")
        self.prediction_progress_bar.stop()
        self.predict_button.config(state="normal")
        
        # Clear forward pass visualization
        self.forward_pass_visualizer.clear_visualization()
    
    def get_prediction_params(self):
        """Get prediction parameters."""
        params = {
            'model_path': self.app.selected_model,
            'data_file': self.prediction_data_var.get() if not self.use_current_data_var.get() else self.app.current_data_file,
            'use_current_data': self.use_current_data_var.get(),
            'batch_size': getattr(self.app, 'prediction_batch_size', 32),
            'confidence_threshold': getattr(self.app, 'prediction_confidence', 0.8),
            'visualization_callback': self.on_prediction_progress
        }
        return params
    
    def update_model_list(self, models):
        """Update the model list in the combo box with maximum thread safety."""
        try:
            # Ensure we're on the main thread with additional delay
            if hasattr(self, 'app') and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                # Use a longer delay to ensure GUI is completely stable
                self.app.main_window.root.after(150, lambda: self._delayed_safe_update_model_list(models))
            else:
                # Fallback to direct call if main window not available
                self._delayed_safe_update_model_list(models)
                
        except Exception as e:
            self.logger.error(f"Error in update_model_list: {e}")
    
    def _delayed_safe_update_model_list(self, models):
        """Delayed safe update of model list with maximum safety measures."""
        try:
            # Add additional delay for memory stability
            if hasattr(self, 'app') and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                self.app.main_window.root.after(50, lambda: self._final_safe_update_model_list(models))
            else:
                self._final_safe_update_model_list(models)
                
        except Exception as e:
            self.logger.error(f"Error in delayed_safe_update_model_list: {e}")
    
    def _final_safe_update_model_list(self, models):
        """Final safe update of model list with comprehensive safety checks."""
        try:
            # Validate models list
            if not models or not isinstance(models, list):
                self.logger.warning("Invalid models list")
                return
                
            # Check if the widget is still valid
            if not hasattr(self, 'model_var') or self.model_var is None:
                self.logger.warning("Model variable not available")
                return
                
            # Get model names with error handling
            try:
                model_names = [os.path.basename(model) for model in models if os.path.exists(model)]
            except Exception as e:
                self.logger.error(f"Error getting model names: {e}")
                return
                
            # Update the combo box with maximum error handling
            try:
                if hasattr(self, 'model_combo') and self.model_combo is not None:
                    # Clear existing values with error handling
                    try:
                        self.model_combo['values'] = ()
                    except Exception as clear_error:
                        self.logger.error(f"Error clearing combo box values: {clear_error}")
                        return
                    
                    # Add new values with error handling
                    if model_names:
                        try:
                            self.model_combo['values'] = model_names
                            self.logger.info(f"Model list updated with {len(model_names)} models")
                        except Exception as set_error:
                            self.logger.error(f"Error setting combo box values: {set_error}")
                            return
                    else:
                        self.logger.warning("No valid models to add to list")
                else:
                    self.logger.warning("Model combo box not available")
            except Exception as e:
                self.logger.error(f"Error updating model combo box: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in final_safe_update_model_list: {e}")
    
    def update_model_info(self, model_path):
        """Update the model information display with maximum thread safety."""
        try:
            # Ensure we're on the main thread with additional delay
            if hasattr(self, 'app') and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                # Use a longer delay to ensure GUI is completely stable
                self.app.main_window.root.after(150, lambda: self._delayed_safe_update_model_info(model_path))
            else:
                # Fallback to direct call if main window not available
                self._delayed_safe_update_model_info(model_path)
                
        except Exception as e:
            self.logger.error(f"Error in update_model_info: {e}")
    
    def _delayed_safe_update_model_info(self, model_path):
        """Delayed safe update of model information with maximum safety measures."""
        try:
            # Add additional delay for memory stability
            if hasattr(self, 'app') and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                self.app.main_window.root.after(50, lambda: self._final_safe_update_model_info(model_path))
            else:
                self._final_safe_update_model_info(model_path)
                
        except Exception as e:
            self.logger.error(f"Error in delayed_safe_update_model_info: {e}")
    
    def _final_safe_update_model_info(self, model_path):
        """Final safe update of model information with comprehensive safety checks."""
        try:
            # Validate model path
            if not model_path or not os.path.exists(model_path):
                self.logger.warning(f"Invalid model path: {model_path}")
                return
                
            # Check if the widget is still valid
            if not hasattr(self, 'model_info_var') or self.model_info_var is None:
                self.logger.warning("Model info variable not available")
                return
                
            # Get model information with error handling
            try:
                model_info = self._get_model_info(model_path)
            except Exception as e:
                self.logger.error(f"Error getting model info: {e}")
                return
                
            # Update the display with maximum error handling
            try:
                if hasattr(self.model_info_var, 'set'):
                    # Use a try-catch around the actual set operation
                    try:
                        self.model_info_var.set(model_info)
                        self.logger.info(f"Model info updated for: {os.path.basename(model_path)}")
                    except Exception as set_error:
                        self.logger.error(f"Error in model_info_var.set(): {set_error}")
                        return
                else:
                    self.logger.warning("Model info variable set method not available")
            except Exception as e:
                self.logger.error(f"Error setting model info: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in final_safe_update_model_info: {e}")
    
    def _get_model_info(self, model_path):
        """Get model information."""
        if not model_path or not os.path.exists(model_path):
            return "Invalid model"
        
        # Get basic model info
        model_name = os.path.basename(model_path)
        mod_time = os.path.getmtime(model_path)
        mod_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(mod_time))
        
        # Check for model parameters
        params_file = os.path.join(model_path, 'model_params.json')
        if os.path.exists(params_file):
            try:
                import json
                with open(params_file, 'r') as f:
                    params = json.load(f)
                
                # Extract key parameters
                epochs = params.get('epochs', 'Unknown')
                learning_rate = params.get('learning_rate', 'Unknown')
                
                info_text = f"{model_name} | Epochs: {epochs} | LR: {learning_rate} | {mod_date}"
            except Exception as json_error:
                self.logger.warning(f"Error reading model params: {json_error}")
                info_text = f"{model_name} | {mod_date}"
        else:
            info_text = f"{model_name} | {mod_date}"
        
        return info_text 