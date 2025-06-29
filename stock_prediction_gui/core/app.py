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

from ..ui.main_window import MainWindow
from .data_manager import DataManager
from .model_manager import ModelManager
from ..utils.file_utils import FileUtils
from ..utils.validation import ValidationUtils
from .training_integration import TrainingIntegration
from .prediction_integration import PredictionIntegration

class StockPredictionApp:
    """Main application class."""
    
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.data_manager = DataManager()
        # Initialize model manager with the correct base directory (project root)
        # This ensures it can find model directories created outside the stock_prediction_gui folder
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        self.model_manager = ModelManager(base_dir=project_root)
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
    
    def refresh_models_and_select_latest(self):
        """Refresh models and select the latest one."""
        try:
            # Get available models
            models = self.model_manager.get_available_models()
            
            if not models:
                self.logger.warning("No models found")
                return
            
            # Update model list in main window
            if hasattr(self, 'main_window'):
                self.main_window.update_model_list(models)
            
            # DISABLED: Auto-selection to prevent segmentation faults
            # Users can manually select models from the dropdown
            # latest_model = models[-1]  # Get the latest model
            # if latest_model and os.path.exists(latest_model):
            #     model_name = os.path.basename(latest_model)
            #     self.logger.info(f"Auto-selected latest model: {model_name}")
            #     
            #     # Update the selected model
            #     self.selected_model = latest_model
            #     
            #     # Update prediction panel
            #     if hasattr(self, 'main_window'):
            #         self.main_window.root.after(100, lambda: self._safe_update_prediction_panel_model(latest_model))
            
            self.logger.info(f"Model list refreshed with {len(models)} models")
            
        except Exception as e:
            self.logger.error(f"Error refreshing models: {e}")
    
    def _safe_update_prediction_panel_model(self, model_path):
        """Safely update prediction panel model selection with additional safety measures."""
        try:
            # Add a small delay to ensure GUI is stable
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
                self.main_window.root.after(100, lambda: self._delayed_update_prediction_panel_model(model_path))
            else:
                self.logger.warning("Main window not available for delayed model update")
                
        except Exception as e:
            self.logger.error(f"Error in safe_update_prediction_panel_model: {e}")
    
    def _delayed_update_prediction_panel_model(self, model_path):
        """Delayed update of prediction panel model with comprehensive safety checks."""
        try:
            # Final validation checks
            if not hasattr(self, 'main_window') or not hasattr(self.main_window, 'prediction_panel'):
                self.logger.warning("Main window or prediction panel not available for delayed model update")
                return
                
            if not model_path or not os.path.exists(model_path):
                self.logger.warning(f"Invalid model path for delayed update: {model_path}")
                return
                
            # Check if root window is still valid
            try:
                if not hasattr(self.main_window, 'root') or not self.main_window.root.winfo_exists():
                    self.logger.warning("Root window no longer exists for delayed model update")
                    return
            except:
                self.logger.warning("Root window check failed for delayed model update")
                return
                
            model_name = os.path.basename(model_path)
            
            # Safely set the model variable with additional checks
            if hasattr(self.main_window.prediction_panel, 'model_var'):
                try:
                    # Check if the variable is still valid
                    if hasattr(self.main_window.prediction_panel.model_var, 'set'):
                        # Use a try-catch around the actual set operation
                        try:
                            self.main_window.prediction_panel.model_var.set(model_name)
                            self.logger.info(f"Model variable updated to: {model_name}")
                        except Exception as set_error:
                            self.logger.error(f"Error in model_var.set(): {set_error}")
                            return
                    else:
                        self.logger.warning("Model variable is not valid")
                        return
                except Exception as e:
                    self.logger.error(f"Error setting model variable: {e}")
                    return
            else:
                self.logger.warning("Prediction panel model_var not available")
                return
                
            # Update model info with additional safety and delay
            try:
                if hasattr(self.main_window.prediction_panel, 'update_model_info'):
                    # Add a small delay before updating model info to prevent race conditions
                    if hasattr(self.main_window, 'root'):
                        self.main_window.root.after(100, lambda: self._safe_update_model_info_final(model_path))
                    else:
                        self._safe_update_model_info_final(model_path)
                else:
                    self.logger.warning("Prediction panel update_model_info method not available")
            except Exception as e:
                self.logger.error(f"Error updating model info: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in delayed_update_prediction_panel_model: {e}")
    
    def _safe_update_model_info_final(self, model_path):
        """Final safe update of model info with maximum error handling."""
        try:
            # Final validation
            if not hasattr(self, 'main_window') or not hasattr(self.main_window, 'prediction_panel'):
                self.logger.warning("Main window or prediction panel not available for final model info update")
                return
                
            if not model_path or not os.path.exists(model_path):
                self.logger.warning(f"Invalid model path for final update: {model_path}")
                return
                
            # Check if root window is still valid
            try:
                if not hasattr(self.main_window, 'root') or not self.main_window.root.winfo_exists():
                    self.logger.warning("Root window no longer exists for final model info update")
                    return
            except:
                self.logger.warning("Root window check failed for final model info update")
                return
                
            # Update model info with maximum error handling
            try:
                if hasattr(self.main_window.prediction_panel, 'update_model_info'):
                    # Use a try-catch around the actual update call
                    try:
                        self.main_window.prediction_panel.update_model_info(model_path)
                        self.logger.info(f"Model info updated for: {os.path.basename(model_path)}")
                    except Exception as update_error:
                        self.logger.error(f"Error in update_model_info call: {update_error}")
                        return
                else:
                    self.logger.warning("Prediction panel update_model_info method not available for final update")
            except Exception as e:
                self.logger.error(f"Error in final model info update: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in safe_update_model_info_final: {e}")
    
    def _safe_refresh_models_and_select_latest(self):
        """Safely refresh models and select latest with comprehensive error handling."""
        try:
            # Add a delay to ensure GUI is stable before refresh
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
                self.main_window.root.after(200, self._delayed_refresh_models_and_select_latest)
            else:
                self.logger.warning("Main window not available for delayed model refresh")
                
        except Exception as e:
            self.logger.error(f"Error in safe_refresh_models_and_select_latest: {e}")
    
    def _delayed_refresh_models_and_select_latest(self):
        """Delayed refresh of models with comprehensive safety checks."""
        try:
            # Final check before proceeding
            if not hasattr(self, 'main_window') or not hasattr(self.main_window, 'root'):
                self.logger.warning("Main window not available for delayed model refresh")
                return
                
            # Check if the GUI is still valid
            try:
                if not self.main_window.root.winfo_exists():
                    self.logger.warning("Root window no longer exists for delayed model refresh")
                    return
            except:
                self.logger.warning("Root window check failed for delayed model refresh")
                return
                
            # Get available models with error handling
            try:
                models = self.model_manager.get_available_models()
            except Exception as e:
                self.logger.error(f"Error getting available models: {e}")
                return
                
            if not models:
                self.logger.warning("No models available for refresh")
                return
                
            # Update model list in main window with error handling
            try:
                if hasattr(self, 'main_window') and hasattr(self.main_window, 'update_model_list'):
                    self.main_window.update_model_list(models)
                else:
                    self.logger.warning("Main window or update_model_list method not available")
            except Exception as e:
                self.logger.error(f"Error updating model list: {e}")
                return
                
            # DISABLED: Auto-selection to prevent segmentation faults
            # Users can manually select models from the dropdown
            # try:
            #     latest_model = models[-1]  # Get the latest model
            #     if latest_model and os.path.exists(latest_model):
            #         model_name = os.path.basename(latest_model)
            #         self.logger.info(f"Auto-selected latest model: {model_name}")
            #         
            #         # Update the selected model
            #         self.selected_model = latest_model
            #         
            #         # Update prediction panel with additional delay
            #         if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
            #             self.main_window.root.after(50, lambda: self._safe_update_prediction_panel_model(latest_model))
            #         else:
            #             self.logger.warning("Main window not available for prediction panel update")
            #             
            #     else:
            #         self.logger.warning("Latest model is not valid")
            #         
            # except Exception as e:
            #     self.logger.error(f"Error auto-selecting latest model: {e}")
            
            self.logger.info(f"Model list refreshed with {len(models)} models (manual selection available)")
                
        except Exception as e:
            self.logger.error(f"Error in delayed_refresh_models_and_select_latest: {e}")
    
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
    
    def start_prediction(self, prediction_params, progress_callback=None):
        """Start the prediction process."""
        try:
            # Validate prediction parameters
            if not self.validation.validate_prediction_params(prediction_params):
                return False
            
            # Use provided progress callback or default to internal one
            if progress_callback is None:
                progress_callback = self._on_prediction_progress
            
            # Start prediction using integration
            success = self.prediction_integration.start_prediction(
                prediction_params,
                progress_callback=progress_callback,
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
    
    def _on_training_completed(self, model_dir):
        """Handle training completion."""
        try:
            self.is_training = False
            
            # Schedule all GUI updates on the main thread
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
                self.main_window.root.after(0, lambda: self._handle_training_completion_gui(model_dir))
            else:
                # Fallback if main window not available
                self.logger.warning("Main window not available for training completion")
                
        except Exception as e:
            self.logger.error(f"Error handling training completion: {e}")
    
    def _handle_training_completion_gui(self, model_dir):
        """Handle training completion GUI updates on main thread."""
        try:
            # Check if main window is still valid
            if not hasattr(self, 'main_window') or self.main_window is None:
                self.logger.warning("Main window not available for training completion")
                return
            
            # Check if root window is still valid
            try:
                if not hasattr(self.main_window, 'root') or not self.main_window.root.winfo_exists():
                    self.logger.warning("Root window no longer exists")
                    return
            except:
                self.logger.warning("Root window check failed")
                return
            
            # Update main window with error handling
            try:
                self.main_window.training_completed(model_dir)
            except Exception as e:
                self.logger.error(f"Error calling training_completed: {e}")
            
            # DISABLED: Automatic model refresh to prevent segmentation faults
            # Users can manually refresh models using the refresh button in prediction panel
            # try:
            #     # Add a delay to ensure the training panel reset is complete
            #     self.main_window.root.after(200, lambda: self._safe_refresh_models_and_select_latest())
            # except Exception as e:
            #     self.logger.error(f"Error scheduling model refresh: {e}")
            
            self.logger.info(f"Training completed successfully. Model saved to: {model_dir}")
            self.logger.info("Manual model refresh available in Prediction tab")
            
        except Exception as e:
            self.logger.error(f"Error in training completion GUI handler: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def force_gui_repaint(self):
        """Simple GUI update without forced repaint."""
        try:
            # Just do a simple update
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
                self.main_window.root.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error in simple GUI update: {e}")
    
    def _repaint_all_panels(self):
        """Simple panel update without forced repaint."""
        try:
            # Just do a simple update
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
                self.main_window.root.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error in simple panel update: {e}")
    
    def emergency_repaint(self):
        """Simple emergency update without forced repaint."""
        try:
            self.logger.info("Simple emergency update triggered")
            
            # Simple update
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'root'):
                self.main_window.root.update_idletasks()
            
            self.logger.info("Simple emergency update completed")
            
        except Exception as e:
            self.logger.error(f"Error in simple emergency update: {e}")
    
    def _on_prediction_progress(self, weights, bias, prediction, input_data, progress):
        """Handle prediction progress updates with forward pass visualization."""
        try:
            # Update prediction progress in the main window
            if hasattr(self.main_window, 'prediction_panel'):
                # Call the prediction panel's progress callback if it exists
                if hasattr(self.main_window.prediction_panel, 'on_prediction_progress'):
                    self.main_window.prediction_panel.on_prediction_progress(
                        weights, bias, prediction, input_data, progress
                    )
            
            # Update status
            self.main_window.update_status(f"Prediction progress: {progress:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error updating prediction progress: {e}")
    
    def _on_prediction_completed(self, output_file, error=None):
        """Handle prediction completion."""
        try:
            self.is_predicting = False
            
            if error:
                self.main_window.prediction_failed(error)
                self.logger.error(f"Prediction failed: {error}")
            else:
                self.main_window.prediction_completed(output_file)
                self.logger.info(f"Prediction completed successfully. Results saved to: {output_file}")
                
        except Exception as e:
            self.logger.error(f"Error handling prediction completion: {e}")
            import traceback
            self.logger.error(f"Prediction completion error traceback: {traceback.format_exc()}")
            
            # Try to provide more context about what failed
            try:
                if hasattr(self, 'main_window'):
                    self.logger.error(f"Main window exists: {self.main_window is not None}")
                    if hasattr(self.main_window, 'prediction_panel'):
                        self.logger.error(f"Prediction panel exists: {self.main_window.prediction_panel is not None}")
                    else:
                        self.logger.error("Main window has no prediction_panel attribute")
                else:
                    self.logger.error("App has no main_window attribute")
            except Exception as context_error:
                self.logger.error(f"Error getting context info: {context_error}")
    
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
    
    def _update_prediction_panel_model(self, model_path):
        """Update prediction panel model selection on main thread."""
        try:
            if not hasattr(self, 'main_window') or not hasattr(self.main_window, 'prediction_panel'):
                self.logger.warning("Main window or prediction panel not available for model update")
                return
                
            if not model_path or not os.path.exists(model_path):
                self.logger.warning(f"Invalid model path: {model_path}")
                return
                
            model_name = os.path.basename(model_path)
            
            # Safely set the model variable with additional checks
            if hasattr(self.main_window.prediction_panel, 'model_var'):
                try:
                    # Check if the model_var is valid
                    if self.main_window.prediction_panel.model_var is not None:
                        self.main_window.prediction_panel.model_var.set(model_name)
                        self.logger.info(f"Model variable updated to: {model_name}")
                    else:
                        self.logger.warning("Model variable is None")
                except Exception as e:
                    self.logger.error(f"Error setting model variable: {e}")
            else:
                self.logger.warning("Prediction panel has no model_var attribute")
            
            # Update model info with additional safety
            if hasattr(self.main_window.prediction_panel, 'update_model_info'):
                try:
                    self.main_window.prediction_panel.update_model_info(model_path)
                    self.logger.info(f"Model info updated for: {model_name}")
                except Exception as e:
                    self.logger.error(f"Error updating model info: {e}")
            else:
                self.logger.warning("Prediction panel has no update_model_info method")
                    
        except Exception as e:
            self.logger.error(f"Error updating prediction panel model: {e}")
            # Don't let this crash the application
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}") 