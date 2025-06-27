"""
GUI Utilities Module

Provides utility functions and helper classes for the stock prediction GUI.
This module contains common functionality used across different GUI components.
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime
import glob
import re

class GUIUtils:
    """Utility class for common GUI operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def validate_file_path(file_path, file_type="file"):
        """Validate if a file path exists and is accessible."""
        if not file_path:
            return False, f"No {file_type} path provided"
        
        if not os.path.exists(file_path):
            return False, f"{file_type.capitalize()} does not exist: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return False, f"Cannot read {file_type}: {file_path}"
        
        return True, ""
    
    @staticmethod
    def validate_directory_path(dir_path, create_if_missing=False):
        """Validate if a directory path exists and is accessible."""
        if not dir_path:
            return False, "No directory path provided"
        
        if not os.path.exists(dir_path):
            if create_if_missing:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    return True, ""
                except OSError as e:
                    return False, f"Cannot create directory: {e}"
            else:
                return False, f"Directory does not exist: {dir_path}"
        
        if not os.access(dir_path, os.R_OK | os.W_OK):
            return False, f"Cannot access directory: {dir_path}"
        
        return True, ""
    
    @staticmethod
    def get_file_size_mb(file_path):
        """Get file size in megabytes."""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except OSError:
            return 0
    
    @staticmethod
    def get_dataframe_size_mb(df):
        """Get approximate memory usage of a dataframe in megabytes."""
        try:
            return df.memory_usage(deep=True).sum() / (1024 * 1024)
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_mb):
        """Format file size in human-readable format."""
        if size_mb < 1:
            return f"{size_mb * 1024:.1f} KB"
        elif size_mb < 1024:
            return f"{size_mb:.1f} MB"
        else:
            return f"{size_mb / 1024:.1f} GB"
    
    @staticmethod
    def safe_int_conversion(value, default=0):
        """Safely convert a value to integer."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float_conversion(value, default=0.0):
        """Safely convert a value to float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def validate_numeric_range(value, min_val, max_val, value_type=float):
        """Validate if a value is within a numeric range."""
        try:
            converted_value = value_type(value)
            if min_val <= converted_value <= max_val:
                return True, converted_value
            else:
                return False, f"Value must be between {min_val} and {max_val}"
        except (ValueError, TypeError):
            return False, f"Value must be a valid {value_type.__name__}"

class PathManager:
    """Manages file and directory paths with history."""
    
    def __init__(self, history_file="path_history.json", max_history=10):
        self.history_file = history_file
        self.max_history = max_history
        self.data_file_history = []
        self.output_dir_history = []
        self.load_history()
    
    def load_history(self):
        """Load path history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    self.data_file_history = history.get('data_files', [])
                    self.output_dir_history = history.get('output_dirs', [])
        except Exception as e:
            logging.warning(f"Could not load path history: {e}")
    
    def save_history(self):
        """Save path history to file."""
        try:
            history = {
                'data_files': self.data_file_history,
                'output_dirs': self.output_dir_history
            }
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logging.warning(f"Could not save path history: {e}")
    
    def add_data_file(self, file_path):
        """Add a data file path to history."""
        self._add_to_history(self.data_file_history, file_path)
    
    def add_output_dir(self, dir_path):
        """Add an output directory path to history."""
        self._add_to_history(self.output_dir_history, dir_path)
    
    def _add_to_history(self, history_list, value):
        """Add a value to a history list."""
        if value and value not in history_list:
            history_list.insert(0, value)
            if len(history_list) > self.max_history:
                history_list.pop()
            self.save_history()
    
    def get_data_file_history(self):
        """Get data file history."""
        return self.data_file_history.copy()
    
    def get_output_dir_history(self):
        """Get output directory history."""
        return self.output_dir_history.copy()

class ModelManager:
    """Manages model directories and metadata."""
    
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
    
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
                import shutil
                shutil.rmtree(model_dir)
                return True, ""
            else:
                return False, "Model directory does not exist"
        except Exception as e:
            return False, f"Error deleting model: {e}"

class FeatureManager:
    """Manages feature selection and validation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_data_features(self, data_file):
        """Load and analyze features from a data file."""
        try:
            if not os.path.exists(data_file):
                return None, "Data file does not exist"
            
            # Load data
            df = pd.read_csv(data_file)
            
            if len(df) == 0:
                return None, "Data file is empty"
            
            # Analyze features
            features = {
                'columns': list(df.columns),
                'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(df.select_dtypes(include=['object']).columns),
                'total_rows': len(df),
                'missing_values': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.to_dict()
            }
            
            return features, ""
            
        except Exception as e:
            self.logger.error(f"Error loading data features: {e}")
            return None, f"Error loading data: {e}"
    
    def validate_feature_compatibility(self, data_features, model_features):
        """Validate if data features are compatible with model features."""
        try:
            if not data_features or not model_features:
                return False, "Missing feature information"
            
            data_columns = set(data_features['columns'])
            model_columns = set(model_features['feature_columns'])
            
            missing_features = model_columns - data_columns
            if missing_features:
                return False, f"Missing required features: {list(missing_features)}"
            
            return True, ""
            
        except Exception as e:
            self.logger.error(f"Error validating feature compatibility: {e}")
            return False, f"Error validating features: {e}"
    
    def get_feature_summary(self, features):
        """Get a summary of features for display."""
        if not features:
            return "No features available"
        
        summary = f"Total columns: {len(features['columns'])}\n"
        summary += f"Numeric columns: {len(features['numeric_columns'])}\n"
        summary += f"Categorical columns: {len(features['categorical_columns'])}\n"
        summary += f"Total rows: {features['total_rows']}"
        
        return summary

class AnimationManager:
    """Manages animation generation and playback."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def find_animation_files(self, model_dir, file_types=None):
        """Find animation files in a model directory."""
        if file_types is None:
            file_types = ['*.mp4', '*.gif', '*.avi']
        
        try:
            plots_dir = os.path.join(model_dir, 'plots')
            if not os.path.exists(plots_dir):
                return []
            
            animation_files = []
            for file_type in file_types:
                pattern = os.path.join(plots_dir, file_type)
                animation_files.extend(glob.glob(pattern))
            
            return sorted(animation_files)
            
        except Exception as e:
            self.logger.error(f"Error finding animation files: {e}")
            return []
    
    def generate_animation_script(self, model_dir, output_format='mp4'):
        """Generate a script for creating animations."""
        # This would contain the animation generation logic
        # Implementation depends on the specific animation requirements
        pass
    
    def play_animation(self, animation_file):
        """Play an animation file using the system default player."""
        try:
            import platform
            import subprocess
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(['open', animation_file])
            elif system == "Windows":
                subprocess.run(['start', animation_file], shell=True)
            elif system == "Linux":
                subprocess.run(['xdg-open', animation_file])
            else:
                raise OSError(f"Unsupported operating system: {system}")
                
        except Exception as e:
            self.logger.error(f"Error playing animation: {e}")
            raise 