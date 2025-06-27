"""
Model manager for the Stock Prediction GUI.
"""

import os
import json
import logging
from datetime import datetime
import glob

class ModelManager:
    """Manages model operations."""
    
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
    
    def get_available_models(self):
        """Get all available model directories."""
        try:
            model_dirs = []
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path) and item.startswith('model_'):
                    model_dirs.append(item_path)
            
            # Sort by creation time (newest first)
            model_dirs.sort(key=lambda x: os.path.getctime(x), reverse=True)
            return model_dirs
            
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return []
    
    def get_model_info(self, model_dir):
        """Get information about a model."""
        try:
            if not os.path.exists(model_dir):
                return None
            
            info = {
                'path': model_dir,
                'name': os.path.basename(model_dir),
                'created': datetime.fromtimestamp(os.path.getctime(model_dir)),
                'modified': datetime.fromtimestamp(os.path.getmtime(model_dir)),
                'has_feature_info': False,
                'has_plots': False,
                'has_weights': False,
                'has_predictions': False
            }
            
            # Check for feature info
            feature_info_path = os.path.join(model_dir, 'feature_info.json')
            if os.path.exists(feature_info_path):
                info['has_feature_info'] = True
                try:
                    with open(feature_info_path, 'r') as f:
                        feature_info = json.load(f)
                    info['feature_columns'] = feature_info.get('feature_columns', [])
                    info['target_column'] = feature_info.get('target_column', '')
                except Exception:
                    pass
            
            # Check for plots directory
            plots_dir = os.path.join(model_dir, 'plots')
            if os.path.exists(plots_dir):
                info['has_plots'] = True
                info['plot_files'] = os.listdir(plots_dir)
            
            # Check for weights
            weights_dir = os.path.join(model_dir, 'weights_history')
            if os.path.exists(weights_dir):
                info['has_weights'] = True
                info['weight_files'] = len(os.listdir(weights_dir))
            
            # Check for predictions
            prediction_files = glob.glob(os.path.join(model_dir, 'predictions_*.csv'))
            if prediction_files:
                info['has_predictions'] = True
                info['prediction_files'] = [os.path.basename(f) for f in prediction_files]
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {e}")
            return None
    
    def create_model_directory(self, params):
        """Create a new model directory."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_dir = os.path.join(self.base_dir, f"model_{timestamp}")
            os.makedirs(model_dir, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(model_dir, 'plots'), exist_ok=True)
            os.makedirs(os.path.join(model_dir, 'weights_history'), exist_ok=True)
            
            # Save model parameters
            params_file = os.path.join(model_dir, 'model_params.json')
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=2)
            
            self.logger.info(f"Created model directory: {model_dir}")
            return model_dir
            
        except Exception as e:
            self.logger.error(f"Error creating model directory: {e}")
            return None
    
    def get_prediction_files(self, model_dir):
        """Get prediction files for a model."""
        try:
            if not os.path.exists(model_dir):
                return []
            
            prediction_files = glob.glob(os.path.join(model_dir, 'predictions_*.csv'))
            prediction_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return prediction_files
            
        except Exception as e:
            self.logger.error(f"Error getting prediction files: {e}")
            return []
    
    def get_prediction_summary(self, prediction_file):
        """Get summary statistics for prediction results."""
        try:
            import pandas as pd
            import numpy as np
            
            if not os.path.exists(prediction_file):
                return None
            
            # Load the CSV file
            df = pd.read_csv(prediction_file)
            
            summary = {
                'total_predictions': len(df),
                'has_actual_values': 'actual' in df.columns,
                'columns': list(df.columns)
            }
            
            if 'actual' in df.columns and 'predicted' in df.columns:
                errors = df['actual'] - df['predicted']
                summary.update({
                    'mse': float(np.mean(errors ** 2)),
                    'mae': float(np.mean(np.abs(errors))),
                    'rmse': float(np.sqrt(np.mean(errors ** 2))),
                    'mean_actual': float(df['actual'].mean()),
                    'mean_predicted': float(df['predicted'].mean()),
                    'std_actual': float(df['actual'].std()),
                    'std_predicted': float(df['predicted'].std())
                })
                
                if 'error_percent' in df.columns:
                    summary['mape'] = float(np.mean(np.abs(df['error_percent'])))
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting prediction summary: {e}")
            return None
    
    def delete_model(self, model_dir):
        """Delete a model directory."""
        try:
            if os.path.exists(model_dir):
                import shutil
                shutil.rmtree(model_dir)
                self.logger.info(f"Deleted model: {model_dir}")
                return True, ""
            else:
                return False, "Model directory does not exist"
                
        except Exception as e:
            self.logger.error(f"Error deleting model: {e}")
            return False, f"Error deleting model: {e}" 