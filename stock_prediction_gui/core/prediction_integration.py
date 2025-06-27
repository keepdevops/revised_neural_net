"""
Prediction integration module for connecting the GUI to existing prediction scripts.
"""

import os
import sys
import threading
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from stock_net import StockNet
from advanced_stock_net import AdvancedStockNet

class PredictionIntegration:
    """Integrates the GUI with existing prediction functionality."""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.prediction_thread = None
        self.stop_prediction = False
        
    def start_prediction(self, params, progress_callback=None, completion_callback=None):
        """Start prediction with the given parameters."""
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
        required_fields = ['model_path', 'data_file']
        
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"Missing required parameter: {field}")
                return False
        
        if not os.path.exists(params['model_path']):
            self.logger.error(f"Model path not found: {params['model_path']}")
            return False
        
        if not os.path.exists(params['data_file']):
            self.logger.error(f"Data file not found: {params['data_file']}")
            return False
        
        return True
    
    def _prediction_worker(self, params, progress_callback, completion_callback):
        """Prediction worker function that runs in a separate thread."""
        try:
            self.logger.info(f"Starting prediction with model: {params['model_path']}")
            
            # Determine model directory and file
            if os.path.isdir(params['model_path']):
                # Model path is a directory (advanced models)
                model_dir = params['model_path']
                model_file = None
            else:
                # Model path is a file (basic models)
                model_dir = os.path.dirname(params['model_path'])
                model_file = params['model_path']
            
            # Load model info
            feature_info_path = os.path.join(model_dir, "feature_info.json")
            
            if not os.path.exists(feature_info_path):
                raise ValueError(f"Feature info not found: {feature_info_path}")
            
            with open(feature_info_path, 'r') as f:
                feature_info = json.load(f)
            
            # Load data using the data manager to handle different file formats
            try:
                data_info = self.app.data_manager.load_data(params['data_file'])
                df = self.app.data_manager.get_current_data()
                if df is None:
                    raise ValueError("No data loaded from file")
            except Exception as e:
                raise ValueError(f"Failed to load data from {params['data_file']}: {e}")
            
            # Validate features
            x_features = feature_info['x_features']
            y_feature = feature_info['y_feature']
            
            if not all(col in df.columns for col in x_features):
                raise ValueError(f"Some features not found in data: {x_features}")
            
            X = df[x_features].values
            
            # Load model
            model_type = feature_info.get('model_type', 'basic')
            
            if model_type == 'advanced':
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
                    
                    if model_file_found:
                        model.load_weights(model_file_found)
                    else:
                        raise ValueError(f"No model file found in directory: {model_dir}")
                
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