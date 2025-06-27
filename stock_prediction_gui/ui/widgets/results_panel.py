"""
Results panel for the Stock Prediction GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging

class ResultsPanel:
    """Results panel."""
    
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
        title_label = ttk.Label(self.frame, text="Results & Analysis", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Model selection section
        self.create_model_section()
        
        # Results section
        self.create_results_section()
        
        # Analysis section
        self.create_analysis_section()
    
    def create_model_section(self):
        """Create the model selection section."""
        # Model frame
        model_frame = ttk.LabelFrame(self.frame, text="Select Model", padding="10")
        model_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(model_frame, text="Model:").pack(anchor="w")
        
        # Model selection
        model_select_frame = ttk.Frame(model_frame)
        model_select_frame.pack(fill="x", pady=(5, 0))
        
        self.results_model_var = tk.StringVar()
        self.results_model_combo = ttk.Combobox(model_select_frame, textvariable=self.results_model_var, state="readonly")
        self.results_model_combo.pack(side="left", fill="x", expand=True)
        self.results_model_combo.bind('<<ComboboxSelected>>', self.on_model_select)
        
        ttk.Button(model_select_frame, text="Refresh", command=self.refresh_models).pack(side="right", padx=(5, 0))
    
    def create_results_section(self):
        """Create the results section."""
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Prediction Results", padding="10")
        results_frame.pack(fill="x", pady=(0, 10))
        
        # Results listbox
        ttk.Label(results_frame, text="Available Results:").pack(anchor="w")
        
        self.results_listbox = tk.Listbox(results_frame, height=6)
        self.results_listbox.pack(fill="x", pady=(5, 0))
        self.results_listbox.bind('<Double-Button-1>', self.on_result_select)
        
        # Buttons
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(button_frame, text="View Selected", command=self.view_selected_result).pack(side="left")
        ttk.Button(button_frame, text="Export Results", command=self.export_results).pack(side="left", padx=(5, 0))
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side="right")
    
    def create_analysis_section(self):
        """Create the analysis section."""
        # Analysis frame
        analysis_frame = ttk.LabelFrame(self.frame, text="Results Analysis", padding="10")
        analysis_frame.pack(fill="both", expand=True)
        
        # Analysis text widget
        self.analysis_text = tk.Text(analysis_frame, wrap=tk.WORD)
        self.analysis_text.pack(fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.analysis_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.analysis_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial message
        self.analysis_text.insert(tk.END, "No results selected.\n\nSelect a prediction result to view analysis.")
        self.analysis_text.config(state=tk.DISABLED)
    
    def on_model_select(self, event):
        """Handle model selection."""
        selected_model = self.results_model_var.get()
        if selected_model:
            # Find the full path of the selected model
            models = self.app.model_manager.get_available_models()
            for model_path in models:
                if os.path.basename(model_path) == selected_model:
                    self.load_model_results(model_path)
                    break
    
    def on_result_select(self, event):
        """Handle result selection."""
        selection = self.results_listbox.curselection()
        if selection:
            result_file = self.results_listbox.get(selection[0])
            self.load_result_analysis(result_file)
    
    def refresh_models(self):
        """Refresh the model list."""
        self.app.refresh_models()
    
    def load_model_results(self, model_path):
        """Load results for the selected model."""
        try:
            # Clear current results
            self.results_listbox.delete(0, tk.END)
            
            # Get prediction files for this model
            prediction_files = self.app.model_manager.get_prediction_files(model_path)
            
            for file_path in prediction_files:
                filename = os.path.basename(file_path)
                self.results_listbox.insert(tk.END, filename)
            
            if prediction_files:
                self.results_listbox.selection_set(0)
                self.load_result_analysis(prediction_files[0])
            else:
                self.analysis_text.config(state=tk.NORMAL)
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, "No prediction results found for this model.")
                self.analysis_text.config(state=tk.DISABLED)
                
        except Exception as e:
            self.logger.error(f"Error loading model results: {e}")
    
    def load_result_analysis(self, result_file):
        """Load analysis for the selected result."""
        try:
            # Get the full path
            selected_model = self.results_model_var.get()
            models = self.app.model_manager.get_available_models()
            model_path = None
            for path in models:
                if os.path.basename(path) == selected_model:
                    model_path = path
                    break
            
            if not model_path:
                return
            
            full_path = os.path.join(model_path, result_file)
            
            # Load and analyze the results
            summary = self.app.model_manager.get_prediction_summary(full_path)
            
            # Update analysis display
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            
            analysis_text = f"Results Analysis: {result_file}\n"
            analysis_text += "=" * 50 + "\n\n"
            
            if summary:
                analysis_text += f"Total Predictions: {summary['total_predictions']:,}\n"
                analysis_text += f"Has Actual Values: {summary['has_actual_values']}\n\n"
                
                if summary['has_actual_values']:
                    analysis_text += "Performance Metrics:\n"
                    analysis_text += f"  Mean Squared Error (MSE): {summary.get('mse', 'N/A'):.6f}\n"
                    analysis_text += f"  Mean Absolute Error (MAE): {summary.get('mae', 'N/A'):.6f}\n"
                    analysis_text += f"  Root Mean Squared Error (RMSE): {summary.get('rmse', 'N/A'):.6f}\n"
                    
                    if 'mape' in summary:
                        analysis_text += f"  Mean Absolute Percentage Error (MAPE): {summary['mape']:.2f}%\n"
                    
                    analysis_text += "\nStatistics:\n"
                    analysis_text += f"  Mean Actual: {summary.get('mean_actual', 'N/A'):.4f}\n"
                    analysis_text += f"  Mean Predicted: {summary.get('mean_predicted', 'N/A'):.4f}\n"
                    analysis_text += f"  Std Actual: {summary.get('std_actual', 'N/A'):.4f}\n"
                    analysis_text += f"  Std Predicted: {summary.get('std_predicted', 'N/A'):.4f}\n"
                else:
                    analysis_text += "No actual values available for comparison.\n"
                    analysis_text += "Only predicted values are shown.\n"
            else:
                analysis_text += "Could not load result analysis.\n"
            
            self.analysis_text.insert(tk.END, analysis_text)
            self.analysis_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error loading result analysis: {e}")
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, f"Error loading analysis: {e}")
            self.analysis_text.config(state=tk.DISABLED)
    
    def view_selected_result(self):
        """View the selected result."""
        selection = self.results_listbox.curselection()
        if selection:
            result_file = self.results_listbox.get(selection[0])
            self.load_result_analysis(result_file)
        else:
            messagebox.showwarning("No Selection", "Please select a result to view.")
    
    def export_results(self):
        """Export the selected results."""
        selection = self.results_listbox.curselection()
        if selection:
            # In a real implementation, this would export the results
            messagebox.showinfo("Export", "Export functionality would be implemented here.")
        else:
            messagebox.showwarning("No Selection", "Please select a result to export.")
    
    def clear_results(self):
        """Clear the results display."""
        self.results_listbox.delete(0, tk.END)
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "No results selected.\n\nSelect a prediction result to view analysis.")
        self.analysis_text.config(state=tk.DISABLED)
    
    def update_model_list(self, models):
        """Update the model list."""
        model_names = [os.path.basename(model) for model in models]
        self.results_model_combo['values'] = model_names
        
        if model_names:
            self.results_model_combo.set(model_names[0])
    
    def add_result_file(self, result_file):
        """Add a new result file to the list."""
        filename = os.path.basename(result_file)
        self.results_listbox.insert(0, filename)
        self.results_listbox.selection_set(0)
        self.load_result_analysis(result_file)
    
    def refresh_results(self):
        """Refresh the results display."""
        if self.results_model_var.get():
            # Reload results for the current model
            selected_model = self.results_model_var.get()
            models = self.app.model_manager.get_available_models()
            for model_path in models:
                if os.path.basename(model_path) == selected_model:
                    self.load_model_results(model_path)
                    break 