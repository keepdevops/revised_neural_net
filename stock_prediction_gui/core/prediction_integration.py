"""
Prediction Integration Module

Handles prediction operations for the stock prediction GUI.
This module manages model loading, prediction generation, and result handling.
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

# Import model classes
from stock_net import StockNet
from advanced_stock_net import AdvancedStockNet

# Import Keras integration if available
try:
    from keras_model_integration import KerasModelIntegration
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

class PredictionIntegration:
    """Integration class for prediction operations."""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Prediction state
        self.prediction_thread = None
        self.stop_prediction = False
    
    def start_prediction(self, params, progress_callback=None, completion_callback=None):
        """Start prediction process."""
        try:
            # Validate parameters
            if not self._validate_prediction_params(params):
                return False
            
            # Start prediction in a separate thread
            self.prediction_thread = threading.Thread(
                target=self._prediction_worker,
                args=(params, progress_callback, completion_callback)
            )
            self.prediction_thread.daemon = True
            self.prediction_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting prediction: {e}")
            return False
    
    def stop_prediction_process(self):
        """Stop the prediction process."""
        self.stop_prediction = True
        
        if self.prediction_thread and self.prediction_thread.is_alive():
            self.prediction_thread.join(timeout=5)
    
    def _validate_prediction_params(self, params):
        """Validate prediction parameters."""
        required_fields = ['data_file', 'model_path']
        
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"Missing required parameter: {field}")
                return False
        
        if not os.path.exists(params['data_file']):
            self.logger.error(f"Data file not found: {params['data_file']}")
            return False
        
        if not os.path.exists(params['model_path']):
            self.logger.error(f"Model path not found: {params['model_path']}")
            return False
        
        return True
    
    def _prediction_worker(self, params, progress_callback, completion_callback):
        """Prediction worker function that runs in a separate thread."""
        try:
            self.logger.info(f"Starting prediction with model: {params['model_path']}")
            
            # Determine model directory and file
            if os.path.isdir(params['model_path']):
                # Model path is a directory (advanced models)
                model_dir = os.path.abspath(params['model_path'])
                model_file = None
            else:
                # Model path is a file (basic models)
                model_dir = os.path.abspath(os.path.dirname(params['model_path']))
                model_file = os.path.abspath(params['model_path'])
            
            # Load model info - try both feature_info.json and model_params.json
            feature_info = None
            
            # Try feature_info.json first (newer format)
            feature_info_path = os.path.join(model_dir, "feature_info.json")
            if os.path.exists(feature_info_path):
                with open(feature_info_path, 'r') as f:
                    feature_info = json.load(f)
                self.logger.info(f"Loaded feature info from: {feature_info_path}")
            
            # Try model_params.json if feature_info.json not found (older format)
            if feature_info is None:
                model_params_path = os.path.join(model_dir, "model_params.json")
                if os.path.exists(model_params_path):
                    with open(model_params_path, 'r') as f:
                        model_params = json.load(f)
                    
                    # Convert model_params to feature_info format
                    feature_info = {
                        'x_features': [],  # Will need to be determined from data
                        'y_feature': None,  # Will need to be determined from data
                        'model_type': 'basic',
                        'training_params': model_params
                    }
                    self.logger.info(f"Loaded model params from: {model_params_path}")
            
            if feature_info is None:
                # No model info files found - create a basic feature info structure
                self.logger.warning(f"No feature_info.json or model_params.json found in: {model_dir}")
                self.logger.info("Will attempt to auto-detect features from data")
                
                feature_info = {
                    'x_features': [],  # Will be determined from data
                    'y_feature': None,  # Will be determined from data
                    'model_type': 'basic',
                    'training_params': {'hidden_size': 4}  # Default parameters
                }
            
            # Load data using the data manager to handle different file formats
            try:
                data_info = self.app.data_manager.load_data(params['data_file'])
                df = self.app.data_manager.get_current_data()
                if df is None:
                    raise ValueError("No data loaded from file")
            except Exception as e:
                raise ValueError(f"Failed to load data from {params['data_file']}: {e}")
            
            # If we don't have feature info, try to determine features from the data
            x_features = feature_info.get('x_features', [])
            y_feature = feature_info.get('y_feature')
            
            if not x_features:
                # Auto-detect features from data
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_columns) >= 4:
                    # Use first 4 numeric columns as features
                    x_features = numeric_columns[:4]
                    y_feature = numeric_columns[4] if len(numeric_columns) > 4 else numeric_columns[0]
                else:
                    raise ValueError("Insufficient numeric columns for prediction")
            
            if not y_feature:
                # Use the last numeric column as target
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                y_feature = numeric_columns[-1] if numeric_columns else None
                if not y_feature:
                    raise ValueError("No target column found")
            
            # Prepare input data
            X = df[x_features].values
            y = df[y_feature].values if y_feature in df.columns else None
            
            # Determine model type
            model_type = feature_info.get('model_type', 'basic')
            
            # Load model and make predictions with forward pass visualization
            if model_type == 'keras':
                # Load Keras model
                if not KERAS_AVAILABLE:
                    raise ImportError("TensorFlow/Keras is required for Keras model prediction")
                
                integration = KerasModelIntegration()
                model, model_feature_info = integration.load_model(model_dir)
                
                # Make predictions with visualization
                predictions = self._predict_with_visualization(
                    model, X, model_feature_info, progress_callback, 
                    model_type='keras', integration=integration
                )
                
            elif model_type == 'advanced':
                # Load advanced model
                model = AdvancedStockNet.load_model(model_dir)
                predictions = self._predict_with_visualization(
                    model, X, None, progress_callback, 
                    model_type='advanced'
                )
                
            else:
                # Load basic model
                input_size = len(x_features)
                
                # Get hidden size from training parameters in feature_info
                training_params = feature_info.get('training_params', {})
                hidden_size = training_params.get('hidden_size', 4)
                
                # Log the hidden size being used
                self.logger.info(f"Using hidden size from training parameters: {hidden_size}")
                
                # Load weights using the class method
                if model_file:
                    # If a specific model file is provided, load it
                    model = StockNet.load_weights(model_dir, prefix=os.path.splitext(os.path.basename(model_file))[0])
                else:
                    # Try to find the model file in the directory
                    possible_model_files = [
                        os.path.join(model_dir, "stock_model.npz"),
                        os.path.join(model_dir, "model.npz"),
                        os.path.join(model_dir, "final_model.npz"),
                        os.path.join(model_dir, "best_model.npz")
                    ]
                    
                    model_file_found = None
                    for mf in possible_model_files:
                        if os.path.exists(mf):
                            model_file_found = mf
                            break
                    
                    # If no main model file found, try weights_history directory
                    if not model_file_found:
                        weights_history_dir = os.path.join(model_dir, "weights_history")
                        if os.path.exists(weights_history_dir):
                            weight_files = [f for f in os.listdir(weights_history_dir) if f.endswith('.npz')]
                            if weight_files:
                                # Use the most recent weight file
                                weight_files.sort(key=lambda x: os.path.getctime(os.path.join(weights_history_dir, x)), reverse=True)
                                model_file_found = os.path.join(weights_history_dir, weight_files[0])
                                self.logger.info(f"Using weight file from history: {weight_files[0]}")
                    
                    if model_file_found:
                        # Load model using the class method with the found file
                        model = StockNet.load_weights(model_dir, prefix=os.path.splitext(os.path.basename(model_file_found))[0])
                    else:
                        # Try enhanced model file search
                        model_file_found = self._find_model_file_enhanced(model_dir)
                        if model_file_found:
                            # Load model using the class method with the found file
                            model_dir_found = os.path.dirname(model_file_found)
                            model = StockNet.load_weights(model_dir_found, prefix=os.path.splitext(os.path.basename(model_file_found))[0])
                        else:
                            # Generate detailed error message
                            error_msg = self._generate_model_not_found_error(model_dir)
                            raise FileNotFoundError(error_msg)
                
                # Check for normalization parameters
                scaler_mean_path = os.path.join(model_dir, "scaler_mean.csv")
                scaler_std_path = os.path.join(model_dir, "scaler_std.csv")
                
                if os.path.exists(scaler_mean_path) and os.path.exists(scaler_std_path):
                    model.X_min = np.loadtxt(scaler_mean_path)
                    model.X_max = model.X_min + np.loadtxt(scaler_std_path)
                    
                    # Normalize input data
                    X_norm = (X - model.X_min) / (model.X_max - model.X_min + 1e-8)
                    predictions = self._predict_with_visualization(
                        model, X_norm, None, progress_callback, 
                        model_type='basic', original_X=X
                    )
                    
                    # Denormalize predictions
                    target_min_path = os.path.join(model_dir, "target_min.csv")
                    target_max_path = os.path.join(model_dir, "target_max.csv")
                    
                    if os.path.exists(target_min_path) and os.path.exists(target_max_path):
                        Y_min = np.loadtxt(target_min_path)
                        Y_max = np.loadtxt(target_max_path)
                        predictions = predictions * (Y_max - Y_min) + Y_min
                else:
                    # No normalization parameters, use raw predictions
                    predictions = self._predict_with_visualization(
                        model, X, None, progress_callback, 
                        model_type='basic'
                    )
            
            # Create output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(model_dir, f"predictions_{timestamp}.csv")
            
            # Save predictions
            results_df = df.copy()
            results_df['predicted_' + y_feature] = predictions.flatten()
            
            if y_feature in df.columns:
                results_df['actual_' + y_feature] = df[y_feature]
                results_df['error'] = results_df['actual_' + y_feature] - results_df['predicted_' + y_feature]
            
            results_df.to_csv(output_file, index=False)
            
            self.logger.info(f"Prediction completed successfully. Results saved to: {output_file}")
            
            # Call completion callback
            if completion_callback:
                completion_callback(output_file)
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            if completion_callback:
                completion_callback(None, str(e))
    
    def _predict_with_visualization(self, model, X, feature_info, progress_callback, 
                                  model_type='basic', integration=None, original_X=None):
        """Make predictions with forward pass visualization."""
        try:
            total_samples = len(X)
            batch_size = 32  # Default batch size
            
            # Determine batch size from params if available
            if hasattr(self.app, 'prediction_batch_size'):
                batch_size = self.app.prediction_batch_size
            
            predictions = []
            
            # Process in batches for visualization
            for i in range(0, total_samples, batch_size):
                if self.stop_prediction:
                    break
                
                batch_end = min(i + batch_size, total_samples)
                X_batch = X[i:batch_end]
                
                # Make prediction for this batch
                if model_type == 'keras':
                    batch_predictions = integration.predict(model, X_batch, feature_info)
                else:
                    # For StockNet models, use forward method instead of predict
                    batch_predictions = model.forward(X_batch)
                
                predictions.extend(batch_predictions.flatten())
                
                # Calculate progress
                progress = (batch_end / total_samples) * 100
                
                # Get model weights and bias for visualization
                weights, bias = self._extract_model_parameters(model, model_type)
                
                # Use original X for visualization if available (for normalized data)
                input_data = original_X[i:batch_end] if original_X is not None else X_batch
                
                # Call progress callback with visualization data
                if progress_callback:
                    # Use the first prediction of the batch for visualization
                    sample_prediction = batch_predictions[0] if len(batch_predictions) > 0 else 0
                    sample_input = input_data[0] if len(input_data) > 0 else X_batch[0]
                    
                    progress_callback(weights, bias, sample_prediction, sample_input, progress)
                
                # Small delay for visualization
                time.sleep(0.01)
            
            return np.array(predictions)
            
        except Exception as e:
            self.logger.error(f"Error in prediction with visualization: {e}")
            raise
    
    def _extract_model_parameters(self, model, model_type):
        """Extract weights and bias from the model for visualization."""
        try:
            if model_type == 'keras':
                # For Keras models, get weights from the first layer
                if hasattr(model, 'layers') and len(model.layers) > 0:
                    first_layer = model.layers[0]
                    if hasattr(first_layer, 'get_weights'):
                        weights = first_layer.get_weights()[0]  # Weight matrix
                        bias = first_layer.get_weights()[1] if len(first_layer.get_weights()) > 1 else 0
                        return weights.flatten(), bias.flatten() if hasattr(bias, 'flatten') else bias
                return np.array([0]), 0
                
            elif model_type == 'advanced':
                # For advanced models, get weights from the model
                if hasattr(model, 'weights'):
                    weights = model.weights
                    bias = model.bias if hasattr(model, 'bias') else 0
                    return weights, bias
                return np.array([0]), 0
                
            else:
                # For basic StockNet models
                if hasattr(model, 'W1') and hasattr(model, 'W2'):
                    # StockNet stores weights as W1, W2, b1, b2
                    weights = np.concatenate([model.W1.flatten(), model.W2.flatten()])
                    bias = np.concatenate([model.b1.flatten(), model.b2.flatten()])
                    return weights, bias
                elif hasattr(model, 'weights'):
                    weights = model.weights
                    bias = model.bias if hasattr(model, 'bias') else 0
                    return weights, bias
                return np.array([0]), 0
                
        except Exception as e:
            self.logger.error(f"Error extracting model parameters: {e}")
            return np.array([0]), 0
    
    def _find_model_file_enhanced(self, model_dir):
        """Enhanced model file search that looks in multiple locations."""
        try:
            # 1. Check project root (parent of stock_prediction_gui)
            project_root = os.path.dirname(os.path.dirname(model_dir))  # Go up two levels
            if os.path.exists(project_root):
                root_model_files = [f for f in os.listdir(project_root) if f.endswith('.npz')]
                if root_model_files:
                    # Use the most recent model file from project root
                    root_model_files.sort(key=lambda x: os.path.getctime(os.path.join(project_root, x)), reverse=True)
                    model_file_found = os.path.join(project_root, root_model_files[0])
                    self.logger.info(f"Using model file from project root: {root_model_files[0]}")
                    return model_file_found
            
            # 2. Check other model directories in the same parent directory
            parent_dir = os.path.dirname(model_dir)
            if os.path.exists(parent_dir):
                for item in os.listdir(parent_dir):
                    item_path = os.path.join(parent_dir, item)
                    if os.path.isdir(item_path) and item.startswith('model_'):
                        # Check for model files in this directory
                        possible_files = [
                            os.path.join(item_path, "stock_model.npz"),
                            os.path.join(item_path, "model.npz"),
                            os.path.join(item_path, "final_model.npz"),
                            os.path.join(item_path, "best_model.npz")
                        ]
                        for mf in possible_files:
                            if os.path.exists(mf):
                                self.logger.info(f"Using model file from other model directory: {mf}")
                                return mf
                        
                        # Check weights_history in this directory
                        weights_history_dir = os.path.join(item_path, "weights_history")
                        if os.path.exists(weights_history_dir):
                            weight_files = [f for f in os.listdir(weights_history_dir) if f.endswith('.npz')]
                            if weight_files:
                                weight_files.sort(key=lambda x: os.path.getctime(os.path.join(weights_history_dir, x)), reverse=True)
                                model_file_found = os.path.join(weights_history_dir, weight_files[0])
                                self.logger.info(f"Using weight file from other model directory: {weight_files[0]}")
                                return model_file_found
            
            # 3. Check the main project root (one level up from stock_prediction_gui)
            main_project_root = os.path.dirname(parent_dir)
            if os.path.exists(main_project_root):
                for item in os.listdir(main_project_root):
                    item_path = os.path.join(main_project_root, item)
                    if os.path.isdir(item_path) and item.startswith('model_'):
                        # Check for model files in this directory
                        possible_files = [
                            os.path.join(item_path, "stock_model.npz"),
                            os.path.join(item_path, "model.npz"),
                            os.path.join(item_path, "final_model.npz"),
                            os.path.join(item_path, "best_model.npz")
                        ]
                        for mf in possible_files:
                            if os.path.exists(mf):
                                self.logger.info(f"Using model file from main project root: {mf}")
                                return mf
                        
                        # Check weights_history in this directory
                        weights_history_dir = os.path.join(item_path, "weights_history")
                        if os.path.exists(weights_history_dir):
                            weight_files = [f for f in os.listdir(weights_history_dir) if f.endswith('.npz')]
                            if weight_files:
                                weight_files.sort(key=lambda x: os.path.getctime(os.path.join(weights_history_dir, x)), reverse=True)
                                model_file_found = os.path.join(weights_history_dir, weight_files[0])
                                self.logger.info(f"Using weight file from main project root: {weight_files[0]}")
                                return model_file_found
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in enhanced model file search: {e}")
            return None
    
    def _generate_model_not_found_error(self, model_dir):
        """Generate a detailed error message when no model files are found."""
        try:
            # Check what files actually exist in the model directory
            existing_files = []
            if os.path.exists(model_dir):
                existing_files = os.listdir(model_dir)
            
            # Check for other model directories
            parent_dir = os.path.dirname(model_dir)
            other_models = []
            if os.path.exists(parent_dir):
                for item in os.listdir(parent_dir):
                    item_path = os.path.join(parent_dir, item)
                    if os.path.isdir(item_path) and item.startswith('model_'):
                        # Check if this model has actual model files
                        has_model_files = False
                        possible_files = [
                            os.path.join(item_path, "stock_model.npz"),
                            os.path.join(item_path, "model.npz"),
                            os.path.join(item_path, "final_model.npz"),
                            os.path.join(item_path, "best_model.npz")
                        ]
                        for mf in possible_files:
                            if os.path.exists(mf):
                                has_model_files = True
                                break
                        
                        # Check weights_history
                        weights_history_dir = os.path.join(item_path, "weights_history")
                        if os.path.exists(weights_history_dir):
                            weight_files = [f for f in os.listdir(weights_history_dir) if f.endswith('.npz')]
                            if weight_files:
                                has_model_files = True
                        
                        if has_model_files:
                            other_models.append(item)
            
            # Build error message
            error_msg = f"No model files found in: {model_dir}\n\n"
            
            if existing_files:
                error_msg += f"Files found in directory:\n"
                for file in existing_files[:10]:  # Show first 10 files
                    error_msg += f"  - {file}\n"
                if len(existing_files) > 10:
                    error_msg += f"  ... and {len(existing_files) - 10} more files\n"
            else:
                error_msg += "Directory is empty or does not exist.\n"
            
            if other_models:
                error_msg += f"\nOther available models:\n"
                for model in other_models[:5]:  # Show first 5 models
                    error_msg += f"  - {model}\n"
                if len(other_models) > 5:
                    error_msg += f"  ... and {len(other_models) - 5} more models\n"
            
            error_msg += f"\nPlease ensure you have trained a model first, or select a different model directory."
            
            return error_msg
            
        except Exception as e:
            self.logger.error(f"Error generating model not found error: {e}")
            return f"No model files found in: {model_dir}" 