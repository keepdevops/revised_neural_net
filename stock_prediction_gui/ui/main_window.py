"""
Main window interface for the Stock Prediction GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
from datetime import datetime

from .widgets.data_panel import DataPanel
from .widgets.training_panel import TrainingPanel
from .widgets.prediction_panel import PredictionPanel
from .widgets.results_panel import ResultsPanel
from .widgets.control_plots_panel import ControlPlotsPanel
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.help_dialog import HelpDialog

# Import colorblind-friendly color scheme
from ..utils.color_scheme import ColorScheme

class MainWindow:
    """Main window class."""
    
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create the main interface
        self.create_interface()
        
        # Setup event handlers
        self.setup_event_handlers()
    
    def create_interface(self):
        """Create the main interface."""
        # Create main menu
        self.create_menu()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_data_tab()
        self.create_training_tab()
        self.create_prediction_tab()
        self.create_results_tab()
        self.create_control_plots_tab()
        
        # Create status bar
        self.create_status_bar()
    
    def create_menu(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Data File", command=self.open_data_file)
        file_menu.add_command(label="Select Output Directory", command=self.select_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.app.on_closing)
        
        # Training menu
        training_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Training", menu=training_menu)
        training_menu.add_command(label="Start Training", command=self.start_training)
        training_menu.add_command(label="Stop Training", command=self.stop_training)
        training_menu.add_separator()
        training_menu.add_command(label="Refresh Models", command=self.refresh_models)
        
        # Prediction menu
        prediction_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Prediction", menu=prediction_menu)
        prediction_menu.add_command(label="Make Prediction", command=self.make_prediction)
        prediction_menu.add_command(label="View Results", command=self.view_results)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        tools_menu.add_command(label="Clear Cache", command=self.clear_cache)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_data_tab(self):
        """Create the data management tab."""
        self.data_panel = DataPanel(self.notebook, self.app)
        self.notebook.add(self.data_panel.frame, text="Data")
    
    def create_training_tab(self):
        """Create the training tab."""
        self.training_panel = TrainingPanel(self.notebook, self.app)
        self.notebook.add(self.training_panel.frame, text="Training")
    
    def create_prediction_tab(self):
        """Create the prediction tab."""
        self.prediction_panel = PredictionPanel(self.notebook, self.app)
        self.notebook.add(self.prediction_panel.frame, text="Prediction")
    
    def create_results_tab(self):
        """Create the results tab."""
        self.results_panel = ResultsPanel(self.notebook, self.app)
        self.notebook.add(self.results_panel.frame, text="Results")
    
    def create_control_plots_tab(self):
        """Create the control plots tab."""
        self.control_plots_panel = ControlPlotsPanel(self.notebook, self.app)
        self.notebook.add(self.control_plots_panel.frame, text="Control Plots")
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_event_handlers(self):
        """Setup event handlers."""
        # Tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Handle tab change events."""
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")
        self.update_status(f"Switched to {tab_name} tab")
    
    # Menu command handlers
    def open_data_file(self):
        """Open a data file."""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.app.load_data_file(filename)
    
    def select_output_dir(self):
        """Select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.app.select_output_directory(directory)
    
    def start_training(self):
        """Start training process."""
        if not self.app.current_data_file:
            messagebox.showwarning("No Data", "Please load a data file first.")
            return
        
        if not self.app.current_output_dir:
            messagebox.showwarning("No Output Directory", "Please select an output directory first.")
            return
        
        # Get training parameters from the training panel
        params = self.training_panel.get_training_params()
        self.app.start_training(params)
    
    def stop_training(self):
        """Stop training process."""
        self.app.stop_training()
    
    def make_prediction(self):
        """Make prediction."""
        if not self.app.selected_model:
            messagebox.showwarning("No Model", "Please select a model first.")
            return
        
        # Get prediction parameters from the prediction panel
        params = self.prediction_panel.get_prediction_params()
        self.app.start_prediction(params)
    
    def view_results(self):
        """View prediction results."""
        self.results_panel.refresh_results()
    
    def refresh_models(self):
        """Refresh model list."""
        # DISABLED: Automatic model list updates to prevent segmentation faults
        # Users can manually refresh models using the refresh button in prediction panel
        # self.app.refresh_models()
        
        # Just log that manual refresh is available
        self.logger.info("Manual model refresh available in Prediction tab")
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.root, self.app)
        dialog.show()
    
    def show_help(self):
        """Show help dialog."""
        dialog = HelpDialog(self.root)
        dialog.show()
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
Stock Prediction Neural Network GUI
Version 2.0

A modern, clean interface for training neural networks
to predict stock prices using technical analysis indicators.

Features:
• Intuitive data management
• Real-time training progress
• Advanced visualization
• Model comparison tools
• Batch prediction support
• Export capabilities

Built with Python and Tkinter.
"""
        messagebox.showinfo("About", about_text)
    
    def clear_cache(self):
        """Clear application cache."""
        try:
            # Clear any cached data
            self.app.data_manager.clear_cache()
            self.update_status("Cache cleared")
            messagebox.showinfo("Success", "Cache cleared successfully.")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            messagebox.showerror("Error", f"Error clearing cache: {e}")
    
    # Update methods for the app to call
    def update_status(self, message):
        """Update the status bar."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_data_info(self, data_info):
        """Update data information display."""
        self.data_panel.update_data_info(data_info)
    
    def update_output_dir(self, directory):
        """Update output directory display."""
        self.data_panel.update_output_dir(directory)
    
    def update_model_list(self, models):
        """Update the model list."""
        # DISABLED: Automatic model list updates to prevent segmentation faults
        # Users can manually refresh models using the refresh button in prediction panel
        # self.prediction_panel.update_model_list(models)
        # self.results_panel.update_model_list(models)
        
        # Just log that models are available for manual refresh
        if models:
            self.logger.info(f"Models available for manual refresh: {len(models)} models")
        else:
            self.logger.info("No models available for manual refresh")
    
    def update_recent_files(self, recent_files):
        """Update recent files list."""
        try:
            if hasattr(self, 'data_panel') and self.data_panel is not None:
                if hasattr(self.data_panel, 'update_recent_files'):
                    self.data_panel.update_recent_files(recent_files)
                else:
                    self.logger.warning("DataPanel missing update_recent_files method")
            else:
                self.logger.warning("DataPanel not yet initialized")
        except Exception as e:
            self.logger.error(f"Error updating recent files: {e}")
    
    def update_training_progress(self, epoch, loss, val_loss, progress):
        """Update training progress."""
        self.training_panel.update_progress(epoch, loss, val_loss, progress)
    
    def training_completed(self, model_dir):
        """Handle training completion."""
        try:
            # Check if root window is still valid
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                self.logger.warning("Root window no longer exists, skipping training completion")
                return
            
            # Ensure training panel is properly reset
            if hasattr(self, 'training_panel'):
                self.training_panel.reset_training_state()
            
            # Simple update without forced repaint
            self.root.update_idletasks()
            
            self.update_status("Training completed successfully")
            
            # REMOVED: refresh_models() call to prevent segmentation faults
            # Users can manually refresh models using the refresh button in prediction panel
            
            # Schedule message box on main thread to avoid threading issues
            self.root.after(100, lambda: self._show_training_completion_message(model_dir))
            
        except Exception as e:
            import traceback
            error_details = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
            self.logger.error(f"Error in training_completed: {error_details}")
            self.update_status("Training completed with errors")
            
            # Schedule warning message on main thread
            self.root.after(200, lambda: self._show_training_completion_warning(str(e)))
    
    def _show_training_completion_message(self, model_dir):
        """Show training completion message box safely."""
        try:
            messagebox.showinfo("Success", f"Training completed!\nModel saved to: {model_dir}")
        except Exception as e:
            self.logger.warning(f"Could not show success message box: {e}")
            # Fallback: just update status
            self.update_status(f"Training completed! Model: {os.path.basename(model_dir)}")
    
    def _show_training_completion_warning(self, error_msg):
        """Show training completion warning message box safely."""
        try:
            messagebox.showwarning("Warning", f"Training completed but there were some issues: {error_msg}")
        except Exception as e:
            self.logger.warning(f"Could not show warning message box: {e}")
            # Fallback: just log the error
            self.logger.error(f"Training completion error: {error_msg}")
    
    def force_complete_repaint(self):
        """Simple GUI update without forced repaint."""
        try:
            # Just do a simple update
            self.root.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error in simple GUI update: {e}")
    
    def _repaint_all_tabs(self):
        """Simple tab update without forced repaint."""
        try:
            # Just do simple updates
            if hasattr(self, 'data_panel') and self.data_panel and hasattr(self.data_panel, 'frame'):
                self.data_panel.frame.update_idletasks()
            
            if hasattr(self, 'training_panel') and self.training_panel and hasattr(self.training_panel, 'frame'):
                self.training_panel.frame.update_idletasks()
            
            if hasattr(self, 'prediction_panel') and self.prediction_panel and hasattr(self.prediction_panel, 'frame'):
                self.prediction_panel.frame.update_idletasks()
            
            if hasattr(self, 'results_panel') and self.results_panel and hasattr(self.results_panel, 'frame'):
                self.results_panel.frame.update_idletasks()
            
            if hasattr(self, 'control_plots_panel') and self.control_plots_panel and hasattr(self.control_plots_panel, 'frame'):
                self.control_plots_panel.frame.update_idletasks()
                    
        except Exception as e:
            self.logger.error(f"Error in simple tab updates: {e}")
    
    def _repaint_all_canvases(self):
        """Simple canvas update without forced repaint."""
        try:
            # Just do simple canvas updates
            if hasattr(self, 'training_panel') and self.training_panel and hasattr(self.training_panel, 'canvas'):
                try:
                    self.training_panel.canvas.draw()
                except Exception as e:
                    self.logger.warning(f"Could not update training canvas: {e}")
            
            if hasattr(self, 'results_panel') and self.results_panel and hasattr(self.results_panel, 'canvas'):
                try:
                    self.results_panel.canvas.draw()
                except Exception as e:
                    self.logger.warning(f"Could not update results canvas: {e}")
            
            if hasattr(self, 'control_plots_panel') and self.control_plots_panel and hasattr(self.control_plots_panel, 'canvas'):
                try:
                    self.control_plots_panel.canvas.draw()
                except Exception as e:
                    self.logger.warning(f"Could not update control plots canvas: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error in simple canvas updates: {e}")
    
    def refresh_all_displays(self):
        """Refresh all displays with simple updates."""
        try:
            self.logger.info("Refreshing all displays...")
            
            # Refresh model lists
            self.refresh_models()
            
            # Simple update
            self.root.update_idletasks()
            
            # Update status
            self.update_status("All displays refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing displays: {e}")
    
    def training_failed(self, error):
        """Handle training failure."""
        self.update_status("Training failed")
        messagebox.showerror("Error", f"Training failed: {error}")
    
    def prediction_completed(self, output_file):
        """Handle prediction completion."""
        self.update_status("Prediction completed successfully")
        self.results_panel.add_result_file(output_file)
        messagebox.showinfo("Success", f"Prediction completed!\nResults saved to: {output_file}")
    
    def prediction_failed(self, error):
        """Handle prediction failure."""
        self.update_status("Prediction failed")
        messagebox.showerror("Error", f"Prediction failed: {error}")

    def update_time(self):
        """Update the time display."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_var.set(f"⟳ {current_time}")
        self.root.after(1000, self.update_time)

    def toggle_colorblind_mode(self):
        """Toggle colorblind-friendly mode."""
        # This could be used to switch between different color schemes
        messagebox.showinfo("Colorblind Mode", "Colorblind-friendly colors are always enabled in this version.")

    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.app.cleanup()
            self.root.destroy()

    def run(self):
        """Run the main window."""
        self.root.mainloop() 