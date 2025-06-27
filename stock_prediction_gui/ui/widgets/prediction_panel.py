"""
Prediction panel for the Stock Prediction GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging

class PredictionPanel:
    """Prediction panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create the panel
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
    
    def create_widgets(self):
        """Create the panel widgets."""
        # Title
        title_label = ttk.Label(self.frame, text="Model Prediction", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Model selection section
        self.create_model_section()
        
        # Prediction data section
        self.create_prediction_data_section()
        
        # Prediction controls section
        self.create_controls_section()
        
        # Prediction status section
        self.create_status_section()
    
    def create_model_section(self):
        """Create the model selection section."""
        # Model frame
        model_frame = ttk.LabelFrame(self.frame, text="Model Selection", padding="10")
        model_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(model_frame, text="Select Model:").pack(anchor="w")
        
        # Model selection
        model_select_frame = ttk.Frame(model_frame)
        model_select_frame.pack(fill="x", pady=(5, 0))
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_select_frame, textvariable=self.model_var, state="readonly")
        self.model_combo.pack(side="left", fill="x", expand=True)
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_select)
        
        ttk.Button(model_select_frame, text="Refresh", command=self.refresh_models).pack(side="right", padx=(5, 0))
        
        # Model info
        self.model_info_frame = ttk.Frame(model_frame)
        self.model_info_frame.pack(fill="x", pady=(10, 0))
        
        self.model_info_text = tk.Text(self.model_info_frame, height=4, wrap=tk.WORD)
        self.model_info_text.pack(fill="x")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.model_info_frame, orient="vertical", command=self.model_info_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.model_info_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial message
        self.model_info_text.insert(tk.END, "No model selected.\n\nPlease select a trained model to make predictions.")
        self.model_info_text.config(state=tk.DISABLED)
    
    def create_prediction_data_section(self):
        """Create the prediction data section."""
        # Prediction data frame
        data_frame = ttk.LabelFrame(self.frame, text="Prediction Data", padding="10")
        data_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(data_frame, text="Select Prediction Data File:").pack(anchor="w")
        
        # Data file selection
        data_select_frame = ttk.Frame(data_frame)
        data_select_frame.pack(fill="x", pady=(5, 0))
        
        self.prediction_data_var = tk.StringVar()
        self.prediction_data_entry = ttk.Entry(data_select_frame, textvariable=self.prediction_data_var, state="readonly")
        self.prediction_data_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(data_select_frame, text="Browse", command=self.browse_prediction_data).pack(side="right", padx=(5, 0))
        
        # Use current data checkbox
        self.use_current_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(data_frame, text="Use currently loaded data", variable=self.use_current_data_var, 
                       command=self.on_use_current_data_change).pack(anchor="w", pady=(10, 0))
    
    def create_controls_section(self):
        """Create the prediction controls section."""
        # Controls frame
        controls_frame = ttk.LabelFrame(self.frame, text="Prediction Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        self.predict_button = ttk.Button(button_frame, text="Make Prediction", command=self.make_prediction)
        self.predict_button.pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="View Results", command=self.view_results).pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side="right")
    
    def create_status_section(self):
        """Create the prediction status section."""
        # Status frame
        status_frame = ttk.LabelFrame(self.frame, text="Prediction Status", padding="10")
        status_frame.pack(fill="x")
        
        # Status labels
        self.prediction_status_var = tk.StringVar(value="Ready to make predictions")
        ttk.Label(status_frame, textvariable=self.prediction_status_var).pack(anchor="w")
        
        self.prediction_progress_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.prediction_progress_var).pack(anchor="w")
        
        # Progress bar
        self.prediction_progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.prediction_progress_bar.pack(fill="x", pady=(5, 0))
    
    def on_model_select(self, event):
        """Handle model selection."""
        selected_model = self.model_var.get()
        if selected_model:
            # Find the full path of the selected model
            models = self.app.model_manager.get_available_models()
            for model_path in models:
                if os.path.basename(model_path) == selected_model:
                    self.app.selected_model = model_path
                    self.update_model_info(model_path)
                    break
    
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
        """Refresh the model list."""
        self.app.refresh_models()
    
    def browse_prediction_data(self):
        """Browse for prediction data file."""
        filename = filedialog.askopenfilename(
            title="Select Prediction Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.prediction_data_var.set(filename)
    
    def make_prediction(self):
        """Make prediction."""
        if not self.app.selected_model:
            messagebox.showwarning("No Model", "Please select a model first.")
            return
        
        # Get prediction data file
        if self.use_current_data_var.get():
            data_file = self.app.current_data_file
        else:
            data_file = self.prediction_data_var.get()
        
        if not data_file or not os.path.exists(data_file):
            messagebox.showwarning("No Data", "Please select a valid prediction data file.")
            return
        
        # Get prediction parameters
        params = self.get_prediction_params()
        
        # Start prediction
        if self.app.start_prediction(params):
            self.predict_button.config(state="disabled")
            self.prediction_progress_bar.start()
            self.prediction_status_var.set("Making predictions...")
    
    def view_results(self):
        """View prediction results."""
        # This will be handled by the main window
        pass
    
    def clear_results(self):
        """Clear prediction results."""
        self.prediction_status_var.set("Ready to make predictions")
        self.prediction_progress_var.set("")
        self.prediction_progress_bar.stop()
        self.predict_button.config(state="normal")
    
    def get_prediction_params(self):
        """Get prediction parameters."""
        if self.use_current_data_var.get():
            data_file = self.app.current_data_file
        else:
            data_file = self.prediction_data_var.get()
        
        # Determine the correct model file path
        model_dir = self.app.selected_model
        model_file = None
        
        # Check for different model file types
        possible_model_files = [
            os.path.join(model_dir, "stock_model.npz"),
            os.path.join(model_dir, "advanced_stock_model.npz"),
            os.path.join(model_dir, "model.npz"),
            os.path.join(model_dir, "final_model.npz"),
            os.path.join(model_dir, "best_model.npz")
        ]
        
        for model_file_path in possible_model_files:
            if os.path.exists(model_file_path):
                model_file = model_file_path
                break
        
        # If no model file found, use the directory (for advanced models that don't use .npz files)
        if model_file is None:
            model_file = model_dir
        
        return {
            'model_path': model_file,
            'data_file': data_file,
            'output_dir': self.app.current_output_dir
        }
    
    def update_model_list(self, models):
        """Update the model list."""
        model_names = [os.path.basename(model) for model in models]
        self.model_combo['values'] = model_names
        
        if model_names:
            self.model_combo.set(model_names[0])
            if self.app.selected_model is None:
                self.app.selected_model = models[0]
                self.update_model_info(models[0])
    
    def update_model_info(self, model_path):
        """Update model information display."""
        try:
            model_info = self.app.model_manager.get_model_info(model_path)
            
            self.model_info_text.config(state=tk.NORMAL)
            self.model_info_text.delete(1.0, tk.END)
            
            if model_info:
                info_text = f"Model: {model_info['name']}\n"
                info_text += f"Created: {model_info['created'].strftime('%Y-%m-%d %H:%M')}\n"
                info_text += f"Modified: {model_info['modified'].strftime('%Y-%m-%d %H:%M')}\n\n"
                
                if model_info['has_feature_info']:
                    info_text += f"Features: {len(model_info.get('feature_columns', []))}\n"
                    info_text += f"Target: {model_info.get('target_column', 'Unknown')}\n"
                
                if model_info['has_plots']:
                    info_text += f"Plots: {len(model_info.get('plot_files', []))}\n"
                
                if model_info['has_weights']:
                    info_text += f"Weight files: {model_info.get('weight_files', 0)}\n"
                
                if model_info['has_predictions']:
                    info_text += f"Predictions: {len(model_info.get('prediction_files', []))}\n"
            else:
                info_text = "Model information not available."
            
            self.model_info_text.insert(tk.END, info_text)
            self.model_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error updating model info: {e}") 