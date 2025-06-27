"""
Model Manager Module

Handles model-related operations for the stock prediction GUI.
This module manages model directories, metadata, and lifecycle operations.
"""

import os
import sys
import json
import logging
from datetime import datetime
import glob
import shutil

class ModelManager:
    """Manages model directories and metadata."""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.logger = logging.getLogger(__name__)
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
    def get_model_directories(self):
        """Get all model directories sorted by creation time."""
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
            self.logger.error(f"Error getting model directories: {e}")
            return []
    
    def get_model_info(self, model_dir):
        """Get information about a model directory."""
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
    
    def delete_model(self, model_dir):
        """Delete a model directory."""
        try:
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
                return True, ""
            else:
                return False, "Model directory does not exist"
        except Exception as e:
            return False, f"Error deleting model: {e}"
    
    def refresh_models(self, load_plots=False):
        """Refresh the model list."""
        try:
            models = self.get_model_directories()
            self.logger.info(f"Found {len(models)} models")
            return models
        except Exception as e:
            self.logger.error(f"Error refreshing models: {e}")
            return []
    
    def create_model_directory(self, timestamp=None):
        """Create a new model directory with timestamp."""
        try:
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            model_dir = os.path.join(self.base_dir, f"model_{timestamp}")
            os.makedirs(model_dir, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(model_dir, 'plots'), exist_ok=True)
            os.makedirs(os.path.join(model_dir, 'weights_history'), exist_ok=True)
            
            return model_dir
            
        except Exception as e:
            self.logger.error(f"Error creating model directory: {e}")
            return None
    
    def save_model_metadata(self, model_dir, metadata):
        """Save model metadata to JSON file."""
        try:
            metadata_file = os.path.join(model_dir, 'model_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Model metadata saved to: {metadata_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving model metadata: {e}")
            return False
    
    def load_model_metadata(self, model_dir):
        """Load model metadata from JSON file."""
        try:
            metadata_file = os.path.join(model_dir, 'model_metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading model metadata: {e}")
            return None
    
    def get_latest_model(self):
        """Get the most recent model directory."""
        try:
            models = self.get_model_directories()
            return models[0] if models else None
        except Exception as e:
            self.logger.error(f"Error getting latest model: {e}")
            return None
    
    def validate_model_directory(self, model_dir):
        """Validate that a model directory contains required files."""
        try:
            if not os.path.exists(model_dir):
                return False, "Model directory does not exist"
            
            # Check for required files
            required_files = ['feature_info.json']
            missing_files = []
            
            for file_name in required_files:
                file_path = os.path.join(model_dir, file_name)
                if not os.path.exists(file_path):
                    missing_files.append(file_name)
            
            if missing_files:
                return False, f"Missing required files: {missing_files}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating model directory: {e}"
