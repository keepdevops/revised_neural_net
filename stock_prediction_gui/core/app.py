"""
Main application class for the Stock Prediction GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from stock_prediction_gui.ui.main_window import MainWindow
from stock_prediction_gui.core.data_manager import DataManager
from stock_prediction_gui.core.model_manager import ModelManager
from stock_prediction_gui.utils.file_utils import FileUtils
from stock_prediction_gui.utils.validation import ValidationUtils
from stock_prediction_gui.core.training_integration import TrainingIntegration
from stock_prediction_gui.core.prediction_integration import PredictionIntegration

class StockPredictionApp:
    """Main application class."""
    
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.data_manager = DataManager()
        self.model_manager = ModelManager()
        self.file_utils = FileUtils()
        self.validation = ValidationUtils()
        
        # Initialize integrations
        self.training_integration = TrainingIntegration(self)
        self.prediction_integration = PredictionIntegration(self)
        
        # Application state
        self.current_data_file = None
        self.current_output_dir = None
        self.selected_model = None
        self.is_training = False
        self.is_predicting = False
        
        # Add missing attributes for feature selection
        self.selected_features = []
        self.selected_target = None
        
        # Setup the main window
        self.setup_main_window()
        
        # Load initial state
        self.load_initial_state()
        
        self.logger.info("Application initialized successfully")
    
    def setup_main_window(self):
        """Setup the main application window."""
        # Configure the main window
        self.root.title("Stock Prediction Neural Network")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '../resources/icons/app_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            self.logger.warning(f"Could not load application icon: {e}")
        
        # Create the main window interface
        self.main_window = MainWindow(self.root, self)
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_initial_state(self):
        """Load initial application state."""
        try:
            # Load settings
            self.load_settings()
            
            # Refresh model list
            self.refresh_models()
            
            # Load recent files
            self.load_recent_files()
            
        except Exception as e:
            self.logger.error(f"Error loading initial state: {e}")
    
    def load_settings(self):
        """Load application settings."""
        try:
            settings_file = "gui_settings.json"
            if os.path.exists(settings_file):
                import json
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Apply settings
                    self.current_output_dir = settings.get('default_output_dir', '')
                    
        except Exception as e:
            self.logger.warning(f"Could not load settings: {e}")
    
    def save_settings(self):
        """Save application settings."""
        try:
            settings = {
                'default_output_dir': self.current_output_dir or '',
                'last_used_data_file': self.current_data_file or '',
                'window_geometry': self.root.geometry(),
                'last_accessed': datetime.now().isoformat()
            }
            
            import json
            with open("gui_settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Could not save settings: {e}")
    
    def refresh_models(self):
        """Refresh the list of available models."""
        try:
            models = self.model_manager.get_available_models()
            self.main_window.update_model_list(models)
        except Exception as e:
            self.logger.error(f"Error refreshing models: {e}")
    
    def load_recent_files(self):
        """Load recent data files."""
        try:
            if hasattr(self, 'main_window') and self.main_window is not None:
                recent_files = self.file_utils.get_recent_files()
                self.main_window.update_recent_files(recent_files)
            else:
                self.logger.warning("Main window not yet initialized, skipping recent files load")
        except Exception as e:
            self.logger.error(f"Error loading recent files: {e}")
    
    def on_closing(self):
        """Handle application closing."""
        try:
            # Save settings
            self.save_settings()
            
            # Clean up resources
            self.cleanup()
            
            # Close the application
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during application closing: {e}")
            self.root.destroy()
    
    def cleanup(self):
        """Clean up application resources."""
        try:
            # Stop any running processes
            if self.is_training:
                self.stop_training()
            
            if self.is_predicting:
                self.stop_prediction()
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def start_training(self, training_params):
        """Start the training process."""
        try:
            # Validate training parameters
            if not self.validation.validate_training_params(training_params):
                return False
            
            # Start training using integration
            success = self.training_integration.start_training(
                training_params,
                progress_callback=self._on_training_progress,
                completion_callback=self._on_training_completed
            )
            
            if success:
                self.is_training = True
                self.main_window.update_status("Training started...")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting training: {e}")
            messagebox.showerror("Training Error", f"Failed to start training: {e}")
            return False
    
    def stop_training(self):
        """Stop the training process."""
        try:
            self.training_integration.stop_training_process()
            self.is_training = False
            self.main_window.update_status("Training stopped")
        except Exception as e:
            self.logger.error(f"Error stopping training: {e}")
    
    def start_prediction(self, prediction_params):
        """Start the prediction process."""
        try:
            # Validate prediction parameters
            if not self.validation.validate_prediction_params(prediction_params):
                return False
            
            # Start prediction using integration
            success = self.prediction_integration.start_prediction(
                prediction_params,
                progress_callback=self._on_prediction_progress,
                completion_callback=self._on_prediction_completed
            )
            
            if success:
                self.is_predicting = True
                self.main_window.update_status("Prediction started...")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting prediction: {e}")
            messagebox.showerror("Prediction Error", f"Failed to start prediction: {e}")
            return False
    
    def stop_prediction(self):
        """Stop the prediction process."""
        try:
            self.prediction_integration.stop_prediction_process()
            self.is_predicting = False
            self.main_window.update_status("Prediction stopped")
        except Exception as e:
            self.logger.error(f"Error stopping prediction: {e}")
    
    def _on_training_progress(self, epoch, loss, val_loss, progress):
        """Handle training progress updates."""
        try:
            self.main_window.update_training_progress(epoch, loss, val_loss, progress)
        except Exception as e:
            self.logger.error(f"Error updating training progress: {e}")
    
    def _on_training_completed(self, model_dir, error=None):
        """Handle training completion."""
        try:
            self.is_training = False
            
            if error:
                self.main_window.training_failed(error)
                self.main_window.update_status("Training failed")
            else:
                self.main_window.training_completed(model_dir)
                self.main_window.update_status("Training completed successfully")
                self.refresh_models()
        except Exception as e:
            self.logger.error(f"Error handling training completion: {e}")
    
    def _on_prediction_progress(self, progress):
        """Handle prediction progress updates."""
        try:
            self.main_window.update_status(f"Prediction progress: {progress:.1f}%")
        except Exception as e:
            self.logger.error(f"Error updating prediction progress: {e}")
    
    def _on_prediction_completed(self, output_file, error=None):
        """Handle prediction completion."""
        try:
            self.is_predicting = False
            
            if error:
                self.main_window.prediction_failed(error)
                self.main_window.update_status("Prediction failed")
            else:
                self.main_window.prediction_completed(output_file)
                self.main_window.update_status("Prediction completed successfully")
        except Exception as e:
            self.logger.error(f"Error handling prediction completion: {e}")
    
    def load_data_file(self, file_path):
        """Load a data file."""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return False
            
            # Add to file history
            self.file_utils.add_data_file(file_path)
            
            # Load data using data manager
            success = self.data_manager.load_data(file_path)
            
            if success:
                self.current_data_file = file_path
                self.main_window.update_status(f"Data file loaded: {os.path.basename(file_path)}")
                
                # Update data panel
                data_info = self.data_manager.get_data_info()
                self.main_window.data_panel.update_data_info(data_info)
                
                return True
            else:
                messagebox.showerror("Error", "Failed to load data file")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading data file: {e}")
            messagebox.showerror("Error", f"Failed to load data file: {e}")
            return False
    
    def select_output_directory(self, directory):
        """Select output directory for models and results."""
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            self.current_output_dir = directory
            self.main_window.update_output_dir(directory)
            self.main_window.update_status(f"Output directory: {directory}")
            
        except Exception as e:
            self.logger.error(f"Error selecting output directory: {e}")
            messagebox.showerror("Error", f"Failed to set output directory: {e}")
    
    def set_selected_features(self, features):
        """Set the selected input features."""
        self.selected_features = features
        self.logger.info(f"Selected features updated: {features}")
    
    def set_selected_target(self, target):
        """Set the selected target feature."""
        self.selected_target = target
        self.logger.info(f"Selected target updated: {target}")
    
    def get_selected_features(self):
        """Get the selected input features."""
        return self.selected_features
    
    def get_selected_target(self):
        """Get the selected target feature."""
        return self.selected_target
    
    def are_features_locked(self):
        """Check if features and target are properly selected and locked."""
        return (self.selected_features is not None and 
                len(self.selected_features) > 0 and 
                self.selected_target is not None and 
                self.selected_target != '') 