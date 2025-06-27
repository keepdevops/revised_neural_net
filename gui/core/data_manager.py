"""
Data Manager Module

Handles all data-related operations for the stock prediction GUI.
This module manages data loading, validation, preprocessing, and feature engineering.
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import json
import tkinter as tk
from tkinter import messagebox

class DataManager:
    """Manages data operations for the stock prediction system."""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.logger = logging.getLogger(__name__)
        
        # Data state
        self.current_data = None
        self.data_features = None
        self.data_metadata = {}
        
        # Supported file formats
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        
        # Required columns for stock data
        self.required_columns = ['open', 'high', 'low', 'close', 'vol']
        
        # Optional technical indicators
        self.technical_indicators = [
            'sma_5', 'sma_20', 'ema_12', 'ema_26', 'rsi', 'macd', 
            'bollinger_upper', 'bollinger_lower', 'stoch_k', 'stoch_d'
        ]
    
    def load_data(self, file_path):
        """Load data from file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Data file not found: {file_path}")
            
            # Determine file format
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                data = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                data = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Validate data
            validation_result = self.validate_data(data)
            if not validation_result['valid']:
                raise ValueError(f"Data validation failed: {validation_result['errors']}")
            
            # Store data
            self.current_data = data
            self.data_metadata = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'rows': len(data),
                'columns': list(data.columns),
                'loaded_at': datetime.now()
            }
            
            # Extract features
            self.data_features = self.extract_features(data)
            
            self.logger.info(f"Data loaded successfully: {len(data)} rows, {len(data.columns)} columns")
            return True, "Data loaded successfully"
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return False, str(e)
    
    def validate_data(self, data):
        """Validate loaded data."""
        errors = []
        
        # Check if data is empty
        if len(data) == 0:
            errors.append("Data file is empty")
            return {'valid': False, 'errors': errors}
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in data.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for numeric columns
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) < len(self.required_columns):
            errors.append("Insufficient numeric columns")
        
        # Check for NaN values
        nan_counts = data.isnull().sum()
        if nan_counts.sum() > 0:
            errors.append(f"Data contains NaN values: {nan_counts[nan_counts > 0].to_dict()}")
        
        # Check for duplicate rows
        if data.duplicated().any():
            errors.append("Data contains duplicate rows")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def extract_features(self, data):
        """Extract features from data."""
        try:
            features = {
                'columns': list(data.columns),
                'numeric_columns': list(data.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(data.select_dtypes(include=['object']).columns),
                'total_rows': len(data),
                'missing_values': data.isnull().sum().to_dict(),
                'data_types': data.dtypes.to_dict(),
                'summary_stats': {}
            }
            
            # Add summary statistics for numeric columns
            if len(features['numeric_columns']) > 0:
                features['summary_stats'] = data[features['numeric_columns']].describe().to_dict()
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            return None
    
    def add_technical_indicators(self, data):
        """Add technical indicators to the data."""
        try:
            if self.current_data is None:
                raise ValueError("No data loaded")
            
            # Make a copy to avoid modifying original data
            enhanced_data = data.copy()
            
            # Simple Moving Averages
            if 'close' in enhanced_data.columns:
                enhanced_data['sma_5'] = enhanced_data['close'].rolling(window=5).mean()
                enhanced_data['sma_20'] = enhanced_data['close'].rolling(window=20).mean()
                
                # Exponential Moving Averages
                enhanced_data['ema_12'] = enhanced_data['close'].ewm(span=12).mean()
                enhanced_data['ema_26'] = enhanced_data['close'].ewm(span=26).mean()
                
                # RSI
                delta = enhanced_data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                enhanced_data['rsi'] = 100 - (100 / (1 + rs))
                
                # MACD
                ema_12 = enhanced_data['close'].ewm(span=12).mean()
                ema_26 = enhanced_data['close'].ewm(span=26).mean()
                enhanced_data['macd'] = ema_12 - ema_26
                enhanced_data['macd_signal'] = enhanced_data['macd'].ewm(span=9).mean()
                
                # Bollinger Bands
                sma_20 = enhanced_data['close'].rolling(window=20).mean()
                std_20 = enhanced_data['close'].rolling(window=20).std()
                enhanced_data['bollinger_upper'] = sma_20 + (std_20 * 2)
                enhanced_data['bollinger_lower'] = sma_20 - (std_20 * 2)
                
                # Stochastic Oscillator
                low_14 = enhanced_data['low'].rolling(window=14).min()
                high_14 = enhanced_data['high'].rolling(window=14).max()
                enhanced_data['stoch_k'] = 100 * ((enhanced_data['close'] - low_14) / (high_14 - low_14))
                enhanced_data['stoch_d'] = enhanced_data['stoch_k'].rolling(window=3).mean()
            
            # Remove NaN values
            enhanced_data = enhanced_data.dropna()
            
            self.logger.info(f"Added technical indicators. New shape: {enhanced_data.shape}")
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Error adding technical indicators: {e}")
            return data
    
    def preprocess_data(self, data=None):
        """Preprocess data for training."""
        try:
            if data is None:
                data = self.current_data
                
            if data is None:
                raise ValueError("No data available for preprocessing")
            
            # Add technical indicators
            processed_data = self.add_technical_indicators(data)
            
            # Select features for training
            feature_columns = self.get_feature_columns(processed_data)
            
            # Prepare features and target
            X = processed_data[feature_columns].values
            y = processed_data['close'].values
            
            # Normalize data
            X_min, X_max = X.min(axis=0), X.max(axis=0)
            y_min, y_max = y.min(), y.max()
            
            X_normalized = (X - X_min) / (X_max - X_min)
            y_normalized = (y - y_min) / (y_max - y_min)
            
            # Store normalization parameters
            normalization_params = {
                'X_min': X_min.tolist(),
                'X_max': X_max.tolist(),
                'y_min': float(y_min),
                'y_max': float(y_max),
                'feature_columns': feature_columns
            }
            
            return {
                'X_train': X_normalized,
                'y_train': y_normalized,
                'X_original': X,
                'y_original': y,
                'normalization_params': normalization_params,
                'feature_columns': feature_columns
            }
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            raise
    
    def get_feature_columns(self, data):
        """Get feature columns for training."""
        # Default feature columns
        default_features = ['open', 'high', 'low', 'vol', 'sma_5', 'sma_20', 'rsi', 'macd']
        
        # Check which features are available in the data
        available_features = [col for col in default_features if col in data.columns]
        
        # If we don't have enough features, use basic OHLCV
        if len(available_features) < 4:
            available_features = ['open', 'high', 'low', 'vol']
            available_features = [col for col in available_features if col in data.columns]
        
        return available_features
    
    def get_data_summary(self):
        """Get a summary of the loaded data."""
        if self.current_data is None:
            return "No data loaded"
        
        summary = f"Data Summary:\n"
        summary += f"File: {os.path.basename(self.data_metadata.get('file_path', 'Unknown'))}\n"
        summary += f"Rows: {self.data_metadata.get('rows', 0):,}\n"
        summary += f"Columns: {self.data_metadata.get('columns', 0)}\n"
        summary += f"File Size: {self.data_metadata.get('file_size', 0):,} bytes\n"
        summary += f"Loaded: {self.data_metadata.get('loaded_at', 'Unknown')}\n"
        
        if self.data_features:
            summary += f"Numeric Columns: {len(self.data_features['numeric_columns'])}\n"
            summary += f"Categorical Columns: {len(self.data_features['categorical_columns'])}\n"
        
        return summary
    
    def export_data(self, file_path, data=None):
        """Export data to file."""
        try:
            if data is None:
                data = self.current_data
                
            if data is None:
                raise ValueError("No data to export")
            
            # Determine export format
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                data.to_csv(file_path, index=False)
            elif file_ext == '.xlsx':
                data.to_excel(file_path, index=False)
            else:
                raise ValueError(f"Unsupported export format: {file_ext}")
            
            self.logger.info(f"Data exported to: {file_path}")
            return True, "Data exported successfully"
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return False, str(e)
    
    def clear_data(self):
        """Clear loaded data."""
        self.current_data = None
        self.data_features = None
        self.data_metadata = {}
        self.logger.info("Data cleared")
    
    def get_data_info(self):
        """Get information about the loaded data."""
        if self.current_data is None:
            return None
        
        return {
            'metadata': self.data_metadata,
            'features': self.data_features,
            'shape': self.current_data.shape,
            'columns': list(self.current_data.columns),
            'dtypes': self.current_data.dtypes.to_dict()
        } 