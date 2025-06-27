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
            
            if model_type == 'keras':
                # Use Keras model
                if not KERAS_AVAILABLE:
                    raise ImportError("TensorFlow/Keras is required for Keras model training")
                
                integration = KerasModelIntegration()
                
                # Prepare model parameters
                model_params = {
                    'hidden_sizes': params.get('hidden_sizes', [64, 32]),
                    'dropout_rate': params.get('dropout_rate', 0.2),
                    'epochs': params.get('epochs', 100),
                    'batch_size': params.get('batch_size', 32),
                    'learning_rate': params.get('learning_rate', 0.001),
                    'patience': params.get('patience', 10)
                }
                
                # Train Keras model
                model, history = integration.train_model(
                    X_train, y_train,
                    X_val=X_val, y_val=y_val,
                    model_params=model_params
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
                
                # Train advanced model
                history = model.train(
                    X_train, y_train,
                    epochs=params.get('epochs', 100),
                    batch_size=params.get('batch_size', 32),
                    validation_split=params.get('validation_split', 0.2),
                    early_stopping_patience=params.get('early_stopping_patience', 10)
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
                
                # Train basic model
                train_losses, val_losses = model.train(
                    X_train_norm, y_train_norm,
                    X_val=X_val_norm, y_val=y_val_norm,
                    learning_rate=params.get('learning_rate', 0.001),
                    batch_size=params.get('batch_size', 32),
                    epochs=params.get('epochs', 1000),
                    save_history=True,
                    history_interval=params.get('history_interval', 50),
                    patience=params.get('patience', 20)
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
            
            # Call completion callback
            if completion_callback:
                completion_callback(model_dir)
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            if completion_callback:
                completion_callback(None, str(e)) 