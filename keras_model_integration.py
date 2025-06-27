"""
Keras Model Integration Module

This module provides integration for Keras models in the stock prediction system.
It handles both training new Keras models and loading existing Keras models for prediction.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

try:
    import tensorflow as tf
    from tensorflow import keras
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("Warning: TensorFlow/Keras not available. Keras model integration disabled.")

class KerasModelIntegration:
    """Integration class for Keras models in the stock prediction system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not KERAS_AVAILABLE:
            raise ImportError("TensorFlow/Keras is required for Keras model integration")
    
    def create_model(self, input_size: int, hidden_sizes: List[int] = [64, 32], 
                    output_size: int = 1, dropout_rate: float = 0.2) -> keras.Model:
        """
        Create a Keras model for stock prediction.
        
        Args:
            input_size: Number of input features
            hidden_sizes: List of hidden layer sizes
            output_size: Number of output neurons (usually 1 for regression)
            dropout_rate: Dropout rate for regularization
            
        Returns:
            keras.Model: Compiled Keras model
        """
        model = keras.Sequential()
        
        # Input layer
        model.add(keras.layers.Dense(hidden_sizes[0], activation='relu', 
                                   input_shape=(input_size,)))
        model.add(keras.layers.Dropout(dropout_rate))
        
        # Hidden layers
        for hidden_size in hidden_sizes[1:]:
            model.add(keras.layers.Dense(hidden_size, activation='relu'))
            model.add(keras.layers.Dropout(dropout_rate))
        
        # Output layer (linear activation for regression)
        model.add(keras.layers.Dense(output_size, activation='linear'))
        
        # Compile model with string loss function to avoid serialization issues
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mean_squared_error',  # Use string instead of function
            metrics=['mae']
        )
        
        return model
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray,
                   X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
                   model_params: Dict[str, Any] = None) -> Tuple[keras.Model, keras.callbacks.History]:
        """
        Train a Keras model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            model_params: Model parameters
            
        Returns:
            Tuple of (trained_model, training_history)
        """
        if model_params is None:
            model_params = {}
        
        # Default parameters
        hidden_sizes = model_params.get('hidden_sizes', [64, 32])
        dropout_rate = model_params.get('dropout_rate', 0.2)
        epochs = model_params.get('epochs', 100)
        batch_size = model_params.get('batch_size', 32)
        learning_rate = model_params.get('learning_rate', 0.001)
        patience = model_params.get('patience', 10)
        
        # Create model
        model = self.create_model(
            input_size=X_train.shape[1],
            hidden_sizes=hidden_sizes,
            dropout_rate=dropout_rate
        )
        
        # Set up callbacks
        callbacks = []
        
        # Early stopping
        if X_val is not None and y_val is not None:
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True
            )
            callbacks.append(early_stopping)
        
        # Model checkpoint
        checkpoint = keras.callbacks.ModelCheckpoint(
            'best_model.keras',  # Use .keras format
            monitor='val_loss' if X_val is not None else 'loss',
            save_best_only=True,
            save_weights_only=False
        )
        callbacks.append(checkpoint)
        
        # Train model
        if X_val is not None and y_val is not None:
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
        else:
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
        
        return model, history
    
    def save_model(self, model: keras.Model, model_dir: str, 
                  feature_info: Dict[str, Any], scaler_X=None, scaler_y=None) -> str:
        """
        Save a trained Keras model with metadata.
        
        Args:
            model: Trained Keras model
            model_dir: Directory to save the model
            feature_info: Feature information dictionary
            scaler_X: Input feature scaler (optional)
            scaler_y: Target scaler (optional)
            
        Returns:
            Path to the saved model file
        """
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the Keras model using the newer .keras format
        model_path = os.path.join(model_dir, 'model.keras')
        model.save(model_path)
        
        # Save feature info
        feature_info_path = os.path.join(model_dir, 'feature_info.json')
        with open(feature_info_path, 'w') as f:
            json.dump(feature_info, f, indent=4)
        
        # Save scalers if provided
        if scaler_X is not None:
            scaler_X_path = os.path.join(model_dir, 'scaler_X.npy')
            np.save(scaler_X_path, scaler_X)
        
        if scaler_y is not None:
            scaler_y_path = os.path.join(model_dir, 'scaler_y.npy')
            np.save(scaler_y_path, scaler_y)
        
        # Save model summary
        summary_path = os.path.join(model_dir, 'model_summary.txt')
        with open(summary_path, 'w') as f:
            model.summary(print_fn=lambda x: f.write(x + '\n'))
        
        self.logger.info(f"Keras model saved to: {model_path}")
        return model_path
    
    def load_model(self, model_dir: str) -> Tuple[keras.Model, Dict[str, Any]]:
        """
        Load a saved Keras model.
        
        Args:
            model_dir: Directory containing the model
            
        Returns:
            Tuple of (loaded_model, feature_info)
        """
        # Try to load the Keras model - check both .keras and .h5 formats
        model_paths = [
            os.path.join(model_dir, 'model.keras'),
            os.path.join(model_dir, 'model.h5')
        ]
        
        model_path = None
        for path in model_paths:
            if os.path.exists(path):
                model_path = path
                break
        
        if model_path is None:
            raise FileNotFoundError(f"Keras model not found in {model_dir}")
        
        # Load the model
        try:
            model = keras.models.load_model(model_path)
        except Exception as e:
            # If loading fails, try with custom_objects
            self.logger.warning(f"Failed to load model normally: {e}")
            try:
                model = keras.models.load_model(model_path, compile=False)
                # Recompile with string loss function
                model.compile(
                    optimizer=keras.optimizers.Adam(learning_rate=0.001),
                    loss='mean_squared_error',
                    metrics=['mae']
                )
            except Exception as e2:
                raise ValueError(f"Failed to load Keras model: {e2}")
        
        # Load feature info
        feature_info_path = os.path.join(model_dir, 'feature_info.json')
        if os.path.exists(feature_info_path):
            with open(feature_info_path, 'r') as f:
                feature_info = json.load(f)
        else:
            feature_info = {}
        
        # Load scalers if they exist
        scaler_X_path = os.path.join(model_dir, 'scaler_X.npy')
        scaler_y_path = os.path.join(model_dir, 'scaler_y.npy')
        
        if os.path.exists(scaler_X_path):
            feature_info['scaler_X'] = np.load(scaler_X_path, allow_pickle=True).item()
        
        if os.path.exists(scaler_y_path):
            feature_info['scaler_y'] = np.load(scaler_y_path, allow_pickle=True).item()
        
        return model, feature_info
    
    def predict(self, model: keras.Model, X: np.ndarray, 
               feature_info: Dict[str, Any]) -> np.ndarray:
        """
        Make predictions using a Keras model.
        
        Args:
            model: Loaded Keras model
            X: Input features
            feature_info: Feature information including scalers
            
        Returns:
            Predictions
        """
        # Apply input scaling if available
        if 'scaler_X' in feature_info:
            X_scaled = feature_info['scaler_X'].transform(X)
        else:
            X_scaled = X
        
        # Make predictions
        predictions_scaled = model.predict(X_scaled, verbose=0)
        
        # Apply output scaling if available
        if 'scaler_y' in feature_info:
            predictions = feature_info['scaler_y'].inverse_transform(predictions_scaled)
        else:
            predictions = predictions_scaled
        
        return predictions.flatten()
    
    def convert_npz_to_keras(self, npz_model_path: str, output_dir: str) -> str:
        """
        Convert a StockNet .npz model to Keras format.
        
        Args:
            npz_model_path: Path to the .npz model file
            output_dir: Directory to save the Keras model
            
        Returns:
            Path to the converted Keras model
        """
        # Load the NPZ model
        with np.load(npz_model_path) as data:
            W1 = data['W1']
            b1 = data['b1']
            W2 = data['W2']
            b2 = data['b2']
            input_size = int(data['input_size'])
            hidden_size = int(data['hidden_size'])
        
        # Create Keras model with same architecture
        model = keras.Sequential([
            keras.layers.Dense(hidden_size, activation='sigmoid', 
                             input_shape=(input_size,)),
            keras.layers.Dense(1, activation='linear')
        ])
        
        # Set weights manually
        model.layers[0].set_weights([W1, b1.flatten()])
        model.layers[1].set_weights([W2, b2.flatten()])
        
        # Compile model with string loss function
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
        
        # Save as Keras model
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, 'converted_model.keras')
        model.save(model_path)
        
        # Save feature info
        feature_info = {
            'x_features': ['feature_' + str(i) for i in range(input_size)],
            'y_feature': 'target',
            'model_type': 'keras',
            'converted_from': 'npz',
            'original_architecture': {
                'input_size': input_size,
                'hidden_size': hidden_size,
                'output_size': 1
            }
        }
        
        feature_info_path = os.path.join(output_dir, 'feature_info.json')
        with open(feature_info_path, 'w') as f:
            json.dump(feature_info, f, indent=4)
        
        self.logger.info(f"Converted NPZ model to Keras format: {model_path}")
        return model_path

def test_keras_integration():
    """Test the Keras model integration."""
    if not KERAS_AVAILABLE:
        print("TensorFlow/Keras not available. Skipping test.")
        return
    
    try:
        # Create test data
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randn(100, 1)
        
        # Create integration instance
        integration = KerasModelIntegration()
        
        # Train model
        model, history = integration.train_model(
            X, y,
            model_params={
                'hidden_sizes': [32, 16],
                'epochs': 10,
                'batch_size': 16
            }
        )
        
        # Save model
        model_dir = 'test_keras_model'
        feature_info = {
            'x_features': ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5'],
            'y_feature': 'target',
            'model_type': 'keras'
        }
        
        model_path = integration.save_model(model, model_dir, feature_info)
        
        # Load model
        loaded_model, loaded_feature_info = integration.load_model(model_dir)
        
        # Make predictions
        predictions = integration.predict(loaded_model, X, loaded_feature_info)
        
        print(f"✅ Keras integration test passed!")
        print(f"Model saved to: {model_path}")
        print(f"Predictions shape: {predictions.shape}")
        
        # Clean up
        import shutil
        shutil.rmtree(model_dir)
        
    except Exception as e:
        print(f"❌ Keras integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keras_integration() 