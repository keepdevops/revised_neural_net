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
                
                # Try to find common stock features
                common_features = ['open', 'high', 'low', 'close', 'vol', 'volume']
                detected_features = [col for col in numeric_columns if col.lower() in common_features]
                
                if len(detected_features) >= 4:
                    x_features = detected_features[:4]  # Use first 4 features
                elif len(numeric_columns) >= 4:
                    x_features = numeric_columns[:4]  # Use first 4 numeric columns
                else:
                    x_features = numeric_columns  # Use all numeric columns
                
                self.logger.info(f"Auto-detected features: {x_features}")
            
            if not y_feature:
                # Auto-detect target feature
                if 'close' in df.columns:
                    y_feature = 'close'
                elif 'price' in df.columns:
                    y_feature = 'price'
                elif len(df.columns) > 0:
                    y_feature = df.columns[-1]  # Use last column as target
                else:
                    raise ValueError("Could not determine target feature")
                
                self.logger.info(f"Auto-detected target feature: {y_feature}")
            
            # Validate features
            if not all(col in df.columns for col in x_features):
                raise ValueError(f"Some features not found in data: {x_features}")
            
            if y_feature not in df.columns:
                raise ValueError(f"Target feature not found in data: {y_feature}")
            
            X = df[x_features].values
            
            # Load model based on type
            model_type = feature_info.get('model_type', 'basic')
            
            if model_type == 'keras':
                # Load Keras model
                if not KERAS_AVAILABLE:
                    raise ImportError("TensorFlow/Keras is required for Keras model prediction")
                
                integration = KerasModelIntegration()
                model, model_feature_info = integration.load_model(model_dir)
                
                # Make predictions
                predictions = integration.predict(model, X, model_feature_info)
                
            elif model_type == 'advanced':
                # Load advanced model
                model = AdvancedStockNet.load_model(model_dir)
                predictions = model.predict(X)
                
            else:
                # Load basic model
                input_size = len(x_features)
                hidden_size = feature_info.get('training_params', {}).get('hidden_size', 4)
                model = StockNet(input_size, hidden_size, 1)
                
                # Load weights
                if model_file:
                    model.load_weights(model_file)
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
                        model.load_weights(model_file_found)
                    else:
                        # Check if there are any .npz files in the project root that might belong to this model
                        project_root = os.path.dirname(model_dir)
                        root_model_files = [f for f in os.listdir(project_root) if f.endswith('.npz')]
                        if root_model_files:
                            # Use the most recent model file from project root
                            root_model_files.sort(key=lambda x: os.path.getctime(os.path.join(project_root, x)), reverse=True)
                            model_file_found = os.path.join(project_root, root_model_files[0])
                            self.logger.info(f"Using model file from project root: {root_model_files[0]}")
                            model.load_weights(model_file_found)
                        else:
                            raise ValueError(
                                f"No model file found in directory: {model_dir}\n"
                                f"Expected files: stock_model.npz, model.npz, final_model.npz, or best_model.npz\n"
                                f"Or weight files in weights_history/ directory\n"
                                f"This model may not have been trained successfully."
                            )
                
                # Load normalization parameters
                scaler_mean_path = os.path.join(model_dir, "scaler_mean.csv")
                scaler_std_path = os.path.join(model_dir, "scaler_std.csv")
                
                if os.path.exists(scaler_mean_path) and os.path.exists(scaler_std_path):
                    model.X_min = np.loadtxt(scaler_mean_path)
                    model.X_max = model.X_min + np.loadtxt(scaler_std_path)
                    
                    # Normalize input data
                    X_norm = (X - model.X_min) / (model.X_max - model.X_min + 1e-8)
                    predictions_norm = model.predict(X_norm)
                    
                    # Denormalize predictions
                    target_min_path = os.path.join(model_dir, "target_min.csv")
                    target_max_path = os.path.join(model_dir, "target_max.csv")
                    
                    if os.path.exists(target_min_path) and os.path.exists(target_max_path):
                        Y_min = np.loadtxt(target_min_path)
                        Y_max = np.loadtxt(target_max_path)
                        predictions = predictions_norm * (Y_max - Y_min) + Y_min
                    else:
                        predictions = predictions_norm
                else:
                    # No normalization parameters, use raw predictions
                    predictions = model.predict(X)
            
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