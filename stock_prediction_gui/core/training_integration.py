"""
Training Integration Module

Handles training operations for the stock prediction GUI.
This module manages model training, parameter validation, and training progress.
"""

import os
import sys
import threading
import time
import json
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import model classes
from stock_net import StockNet
from advanced_stock_net import AdvancedStockNet

# Import Keras integration if available
try:
    from keras_model_integration import KerasModelIntegration
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

class TrainingIntegration:
    """Integration class for training operations."""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Training state
        self.training_thread = None
        self.stop_training = False
        
        # Training manager for live plotting
        try:
            from gui.training.training_manager import TrainingManager
            self.training_manager = TrainingManager(self)
        except ImportError:
            self.training_manager = None
            self.logger.warning("Training manager not available")
    
    def start_training(self, params, progress_callback=None, completion_callback=None):
        """Start training process."""
        try:
            # Validate parameters
            if not self._validate_training_params(params):
                return False
            
            # Create model directory
            model_dir = self._create_model_directory()
            
            # Check if we should use training manager for live plotting
            use_manager = (self.training_manager is not None and 
                          params.get('enable_live_plotting', False))
            
            if use_manager:
                return self._start_training_with_manager(params, model_dir, progress_callback, completion_callback)
            else:
                return self._start_basic_training(params, model_dir, progress_callback, completion_callback)
                
        except Exception as e:
            self.logger.error(f"Error starting training: {e}")
            return False
    
    def _start_training_with_manager(self, params, model_dir, progress_callback, completion_callback):
        """Start training with live plotting manager."""
        try:
            # Prepare training parameters for manager
            training_params = {
                'epochs': params.get('epochs', 100),
                'learning_rate': params.get('learning_rate', 0.001),
                'batch_size': params.get('batch_size', 32),
                'hidden_size': params.get('hidden_size', 64),
                'validation_split': params.get('validation_split', 0.2),
                'early_stopping_patience': params.get('early_stopping_patience', 10),
                'random_seed': params.get('random_seed', 42),
                'save_history': params.get('save_history', True),
                'memory_optimization': params.get('memory_optimization', False),
                'x_features': params['x_features'],
                'y_feature': params['y_feature']
            }
            
            # Define callback for training progress
            def training_callback(event_type, data):
                if event_type == 'progress':
                    epoch, loss, val_loss, progress = data
                    if progress_callback:
                        progress_callback(epoch, loss, val_loss, progress)
                elif event_type == 'completed':
                    if completion_callback:
                        completion_callback(data)  # data is model_dir
                elif event_type == 'error':
                    if completion_callback:
                        completion_callback(None, data)  # data is error message
            
            # Start training with manager
            success = self.training_manager.start_training(training_params, training_callback)
            
            if success:
                # Start actual training in background thread
                self.training_thread = threading.Thread(
                    target=self._training_worker,
                    args=(params, model_dir, progress_callback, completion_callback)
                )
                self.training_thread.daemon = True
                self.training_thread.start()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting training with manager: {e}")
            return False
    
    def _start_basic_training(self, params, model_dir, progress_callback, completion_callback):
        """Start basic training without live plotting."""
        # Start training in a separate thread
        self.training_thread = threading.Thread(
            target=self._training_worker,
            args=(params, model_dir, progress_callback, completion_callback)
        )
        self.training_thread.daemon = True
        self.training_thread.start()
        
        return True
    
    def stop_training_process(self):
        """Stop the training process."""
        self.stop_training = True
        
        # Stop training manager if available
        if self.training_manager:
            self.training_manager.stop_training()
        
        if self.training_thread and self.training_thread.is_alive():
            self.training_thread.join(timeout=5)
    
    def _validate_training_params(self, params):
        """Validate training parameters."""
        required_fields = ['data_file', 'x_features', 'y_feature']
        
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"Missing required parameter: {field}")
                return False
        
        if not os.path.exists(params['data_file']):
            self.logger.error(f"Data file not found: {params['data_file']}")
            return False
        
        return True
    
    def _create_model_directory(self):
        """Create a new model directory with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = os.path.join(self.app.current_output_dir, f"model_{timestamp}")
        os.makedirs(model_dir, exist_ok=True)
        return model_dir
    
    def _training_worker(self, params, model_dir, progress_callback, completion_callback):
        """Training worker function that runs in a separate thread."""
        try:
            self.logger.info(f"Starting training in directory: {model_dir}")
            
            # Load data using the data manager to handle different file formats
            try:
                data_info = self.app.data_manager.load_data(params['data_file'])
                df = self.app.data_manager.get_current_data()
                if df is None:
                    raise ValueError("No data loaded from file")
            except Exception as e:
                raise ValueError(f"Failed to load data from {params['data_file']}: {e}")
            
            X = df[params['x_features']].values
            y = df[params['y_feature']].values.reshape(-1, 1)
            
            # Split data
            from stock_net import train_test_split_manual
            X_train, X_val, y_train, y_val = train_test_split_manual(
                X, y, test_size=params.get('validation_split', 0.2), 
                random_state=params.get('random_seed', 42)
            )
            
            # Choose model type
            model_type = params.get('model_type', 'basic')
            total_epochs = params.get('epochs', 100)
            
            # Create thread-safe progress callback wrapper
            def safe_progress_callback(epoch, loss, val_loss, progress):
                """Thread-safe progress callback that schedules on main thread."""
                if progress_callback and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                    self.app.main_window.root.after(0, lambda: progress_callback(epoch, loss, val_loss, progress))
            
            # Create thread-safe completion callback wrapper
            def safe_completion_callback(model_dir, error=None):
                """Thread-safe completion callback that schedules on main thread."""
                if completion_callback and hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'root'):
                    if error:
                        self.app.main_window.root.after(0, lambda: completion_callback(None, error))
                    else:
                        self.app.main_window.root.after(0, lambda: completion_callback(model_dir))
            
            if model_type == 'keras':
                # Use Keras model
                if not KERAS_AVAILABLE:
                    raise ImportError("TensorFlow/Keras is required for Keras model training")
                
                integration = KerasModelIntegration()
                
                # Prepare model parameters
                model_params = {
                    'hidden_sizes': params.get('hidden_sizes', [64, 32]),
                    'dropout_rate': params.get('dropout_rate', 0.2),
                    'epochs': total_epochs,
                    'batch_size': params.get('batch_size', 32),
                    'learning_rate': params.get('learning_rate', 0.001),
                    'patience': params.get('patience', 10)
                }
                
                # Create custom callback for progress updates
                class ProgressCallback:
                    def __init__(self, progress_callback, total_epochs):
                        self.progress_callback = progress_callback
                        self.total_epochs = total_epochs
                    
                    def on_epoch_end(self, epoch, logs=None):
                        if self.progress_callback:
                            loss = logs.get('loss', 0.0)
                            val_loss = logs.get('val_loss', None)
                            progress = ((epoch + 1) / self.total_epochs) * 100
                            self.progress_callback(epoch + 1, loss, val_loss, progress)
                
                # Train Keras model with progress callback
                progress_cb = ProgressCallback(safe_progress_callback, total_epochs)
                model, history = integration.train_model(
                    X_train, y_train,
                    X_val=X_val, y_val=y_val,
                    model_params=model_params,
                    callbacks=[progress_cb] if safe_progress_callback else None
                )
                
                # Save Keras model
                feature_info = {
                    'x_features': params['x_features'],
                    'y_feature': params['y_feature'],
                    'model_type': 'keras',
                    'training_params': params,
                    'training_history': {
                        'loss': history.history.get('loss', []),
                        'val_loss': history.history.get('val_loss', []),
                        'mae': history.history.get('mae', []),
                        'val_mae': history.history.get('val_mae', [])
                    }
                }
                
                integration.save_model(model, model_dir, feature_info)
                
                # Save training losses for compatibility
                losses_data = np.column_stack([
                    history.history.get('loss', []),
                    history.history.get('val_loss', [])
                ])
                np.savetxt(os.path.join(model_dir, "training_losses.csv"), losses_data, delimiter=',')
                
            elif model_type == 'advanced':
                # Use advanced model
                input_size = len(params['x_features'])
                hidden_size = params.get('hidden_size', 64)
                model = AdvancedStockNet(input_size, hidden_size)
                
                # Create progress callback for advanced model
                def advanced_progress_callback(epoch, loss, val_loss):
                    if safe_progress_callback:
                        progress = ((epoch + 1) / total_epochs) * 100
                        safe_progress_callback(epoch + 1, loss, val_loss, progress)
                
                # Train advanced model with progress callback
                history = model.train(
                    X_train, y_train,
                    epochs=total_epochs,
                    batch_size=params.get('batch_size', 32),
                    validation_split=params.get('validation_split', 0.2),
                    early_stopping_patience=params.get('early_stopping_patience', 10),
                    progress_callback=advanced_progress_callback if safe_progress_callback else None
                )
                
                # Save advanced model
                model.save_model(model_dir)
                
            else:
                # Use basic model
                input_size = len(params['x_features'])
                hidden_size = params.get('hidden_size', 4)
                model = StockNet(input_size, hidden_size, 1)
                
                # Normalize data
                X_train_norm, y_train_norm = model.normalize(X_train, y_train)
                X_val_norm = (X_val - model.X_min) / (model.X_max - model.X_min + 1e-8)
                y_val_norm = (y_val - model.Y_min) / (model.Y_max - model.Y_min + 1e-8) if model.has_target_norm else y_val
                
                # Create progress callback for basic model
                def basic_progress_callback(epoch, train_loss, val_loss):
                    if safe_progress_callback:
                        progress = ((epoch + 1) / total_epochs) * 100
                        safe_progress_callback(epoch + 1, train_loss, val_loss, progress)
                
                # Train basic model with progress callback
                train_losses, val_losses = model.train(
                    X_train_norm, y_train_norm,
                    X_val=X_val_norm, y_val=y_val_norm,
                    learning_rate=params.get('learning_rate', 0.001),
                    batch_size=params.get('batch_size', 32),
                    epochs=total_epochs,
                    save_history=True,
                    history_interval=params.get('history_interval', 50),
                    patience=params.get('patience', 20),
                    progress_callback=basic_progress_callback if safe_progress_callback else None
                )
                
                # Save basic model
                model.save_weights(model_dir, "stock_model")
                
                # Save normalization parameters
                np.savetxt(os.path.join(model_dir, "scaler_mean.csv"), model.X_min, delimiter=',')
                np.savetxt(os.path.join(model_dir, "scaler_std.csv"), model.X_max - model.X_min, delimiter=',')
                
                if model.has_target_norm:
                    np.savetxt(os.path.join(model_dir, "target_min.csv"), [model.Y_min], delimiter=',')
                    np.savetxt(os.path.join(model_dir, "target_max.csv"), [model.Y_max], delimiter=',')
                
                # Save training losses
                losses_data = np.column_stack([train_losses, val_losses])
                np.savetxt(os.path.join(model_dir, "training_losses.csv"), losses_data, delimiter=',')
            
            # Save feature info
            feature_info = {
                'x_features': params['x_features'],
                'y_feature': params['y_feature'],
                'model_type': model_type,
                'training_params': params
            }
            
            with open(os.path.join(model_dir, "feature_info.json"), 'w') as f:
                json.dump(feature_info, f, indent=4)
            
            # Save training data
            df.to_csv(os.path.join(model_dir, "training_data.csv"), index=False)
            
            # Move weight history if it exists (for basic models)
            if model_type == 'basic':
                weights_history_src = os.path.join(os.getcwd(), "weights_history")
                weights_history_dst = os.path.join(model_dir, "weights_history")
                if os.path.exists(weights_history_src):
                    import shutil
                    if os.path.exists(weights_history_dst):
                        shutil.rmtree(weights_history_dst)
                    shutil.move(weights_history_src, weights_history_dst)
            
            self.logger.info(f"Training completed successfully. Model saved to: {model_dir}")
            # Log file path, format, and model type for debugging
            file_path = params.get('data_file', None)
            file_format = None
            if hasattr(self.app, 'file_utils'):
                file_format = self.app.file_utils.get_file_format(file_path)
            self.logger.info(f"Training completed: file={file_path}, format={file_format}, model_type={model_type}")
            
            # Generate 3D animations if enabled
            # DISABLED: 3D animation generation to prevent segmentation faults
            # Users can generate visualizations manually if needed
            if params.get('generate_3d_animations', False):  # Changed from True to False
                self._generate_3d_animations(model_dir, X_train, y_train, params)
            
            # Call completion callback
            safe_completion_callback(model_dir)
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            safe_completion_callback(None, str(e))
    
    def _generate_3d_animations(self, model_dir, X_train, y_train, params):
        """Generate 3D animations (GIF and PNG) from training data."""
        try:
            self.logger.info("Generating 3D animations...")
            
            # Create plots directory if it doesn't exist
            plots_dir = os.path.join(model_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            
            # Import visualization modules
            try:
                import matplotlib.pyplot as plt
                from mpl_toolkits.mplot3d import Axes3D
                import matplotlib.animation as animation
                from matplotlib.animation import PillowWriter
            except ImportError as e:
                self.logger.warning(f"Matplotlib not available for 3D animations: {e}")
                return
            
            # Create 3D scatter plot of training data
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Use first 3 features for 3D visualization
            if X_train.shape[1] >= 3:
                x_feat = X_train[:, 0]
                y_feat = X_train[:, 1]
                z_feat = X_train[:, 2]
            else:
                # If less than 3 features, pad with zeros
                x_feat = X_train[:, 0] if X_train.shape[1] >= 1 else np.zeros(len(X_train))
                y_feat = X_train[:, 1] if X_train.shape[1] >= 2 else np.zeros(len(X_train))
                z_feat = np.zeros(len(X_train))
            
            # Create scatter plot
            scatter = ax.scatter(x_feat, y_feat, z_feat, c=y_train.flatten(), 
                               cmap='viridis', s=20, alpha=0.6)
            
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=20)
            cbar.set_label('Target Value')
            
            # Set labels
            feature_names = params.get('x_features', ['Feature 1', 'Feature 2', 'Feature 3'])
            ax.set_xlabel(feature_names[0] if len(feature_names) > 0 else 'Feature 1')
            ax.set_ylabel(feature_names[1] if len(feature_names) > 1 else 'Feature 2')
            ax.set_zlabel(feature_names[2] if len(feature_names) > 2 else 'Feature 3')
            ax.set_title('3D Training Data Visualization')
            
            # Create animation function
            def animate(frame):
                ax.view_init(elev=20, azim=frame)
                return ax,
            
            # Create animation
            anim = animation.FuncAnimation(fig, animate, frames=360, interval=50, blit=True)
            
            # Save as GIF
            try:
                gif_path = os.path.join(plots_dir, "training_data_3d.gif")
                writer = PillowWriter(fps=20)
                anim.save(gif_path, writer=writer)
                self.logger.info(f"3D animation saved as GIF: {gif_path}")
            except Exception as e:
                self.logger.warning(f"Could not save GIF animation: {e}")
            
            # Save static 3D plot
            static_path = os.path.join(plots_dir, "training_data_3d.png")
            plt.savefig(static_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Static 3D plot saved: {static_path}")
            
            plt.close(fig)
            
            # Create additional 2D plots
            self._generate_2d_plots(plots_dir, X_train, y_train, params)
            
        except Exception as e:
            self.logger.error(f"Error generating 3D animations: {e}")
    
    def _generate_2d_plots(self, plots_dir, X_train, y_train, params):
        """Generate additional 2D plots for training data."""
        try:
            import matplotlib.pyplot as plt
            
            # Feature correlation plot
            if X_train.shape[1] >= 2:
                fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                
                # Plot 1: Feature 1 vs Target
                axes[0, 0].scatter(X_train[:, 0], y_train.flatten(), alpha=0.6)
                axes[0, 0].set_xlabel(params.get('x_features', ['Feature 1'])[0])
                axes[0, 0].set_ylabel(params.get('y_feature', 'Target'))
                axes[0, 0].set_title('Feature 1 vs Target')
                axes[0, 0].grid(True, alpha=0.3)
                
                # Plot 2: Feature 2 vs Target (if available)
                if X_train.shape[1] >= 2:
                    axes[0, 1].scatter(X_train[:, 1], y_train.flatten(), alpha=0.6)
                    axes[0, 1].set_xlabel(params.get('x_features', ['Feature 1', 'Feature 2'])[1])
                    axes[0, 1].set_ylabel(params.get('y_feature', 'Target'))
                    axes[0, 1].set_title('Feature 2 vs Target')
                    axes[0, 1].grid(True, alpha=0.3)
                
                # Plot 3: Feature 1 vs Feature 2
                if X_train.shape[1] >= 2:
                    scatter = axes[1, 0].scatter(X_train[:, 0], X_train[:, 1], 
                                               c=y_train.flatten(), cmap='viridis', alpha=0.6)
                    axes[1, 0].set_xlabel(params.get('x_features', ['Feature 1'])[0])
                    axes[1, 0].set_ylabel(params.get('x_features', ['Feature 1', 'Feature 2'])[1])
                    axes[1, 0].set_title('Feature 1 vs Feature 2')
                    axes[1, 0].grid(True, alpha=0.3)
                    plt.colorbar(scatter, ax=axes[1, 0])
                
                # Plot 4: Target distribution
                axes[1, 1].hist(y_train.flatten(), bins=30, alpha=0.7, edgecolor='black')
                axes[1, 1].set_xlabel(params.get('y_feature', 'Target'))
                axes[1, 1].set_ylabel('Frequency')
                axes[1, 1].set_title('Target Distribution')
                axes[1, 1].grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig(os.path.join(plots_dir, "training_data_analysis.png"), dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                self.logger.info("2D analysis plots generated successfully")
                
        except Exception as e:
            self.logger.error(f"Error generating 2D plots: {e}") 