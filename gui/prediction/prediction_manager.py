#Test
"""
Prediction Manager Module

Handles all prediction-related operations for the stock prediction GUI.
This module manages model loading, prediction generation, and result handling.
"""

import os
import sys
import subprocess
import threading
import time
import json
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox
import tempfile

class PredictionManager:
    """Manages prediction operations for the stock prediction system."""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.logger = logging.getLogger(__name__)
        
        # Prediction state
        self.prediction_process = None
        self.prediction_thread = None
        self.is_predicting = False
        
        # Model cache
        self.model_cache = {}
        self.feature_info_cache = {}
    
    def load_model_info(self, model_dir):
        """Load model information and feature details."""
        try:
            # Check if model directory exists
            if not os.path.exists(model_dir):
                raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
            # Load feature info
            feature_info_path = os.path.join(model_dir, 'feature_info.json')
            if not os.path.exists(feature_info_path):
                raise FileNotFoundError(f"Feature info not found: {feature_info_path}")
            
            with open(feature_info_path, 'r') as f:
                feature_info = json.load(f)
            
            # Cache the feature info
            self.feature_info_cache[model_dir] = feature_info
            
            return feature_info
            
        except Exception as e:
            self.logger.error(f"Error loading model info: {e}")
            raise
    
    def validate_prediction_data(self, data_file, model_dir):
        """Validate that prediction data is compatible with the model."""
        try:
            # Load model feature info
            feature_info = self.load_model_info(model_dir)
            required_features = feature_info['feature_columns']
            
            # Load data
            data = pd.read_csv(data_file)
            
            # Check if required features exist
            missing_features = [f for f in required_features if f not in data.columns]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")
            
            # Check for sufficient data
            if len(data) == 0:
                raise ValueError("No data found in file")
            
            # Check for NaN values
            data_subset = data[required_features]
            if data_subset.isnull().any().any():
                raise ValueError("Data contains NaN values")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating prediction data: {e}")
            raise
    
    def make_prediction(self, model_dir, data_file, callback=None):
        """Make predictions using the specified model."""
        try:
            # Validate inputs
            if not os.path.exists(model_dir):
                raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
            if not os.path.exists(data_file):
                raise FileNotFoundError(f"Data file not found: {data_file}")
            
            # Validate data compatibility
            self.validate_prediction_data(data_file, model_dir)
            
            # Check if already predicting
            if self.is_predicting:
                messagebox.showwarning("Prediction in Progress", 
                                     "Prediction is already in progress. Please wait.")
                return False
            
            # Prepare prediction script
            script_path = self._prepare_prediction_script(model_dir, data_file)
            if not script_path:
                return False
            
            # Start prediction in background thread
            self.is_predicting = True
            self.prediction_thread = threading.Thread(
                target=self._run_prediction_process,
                args=(script_path, model_dir, data_file, callback)
            )
            self.prediction_thread.daemon = True
            self.prediction_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting prediction: {e}")
            messagebox.showerror("Prediction Error", f"Failed to start prediction: {e}")
            return False
    
    def _prepare_prediction_script(self, model_dir, data_file):
        """Prepare the prediction script."""
        try:
            # Create prediction script content
            script_content = self._create_prediction_script(model_dir, data_file)
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            return script_path
            
        except Exception as e:
            self.logger.error(f"Error preparing prediction script: {e}")
            return None
    
    def _create_prediction_script(self, model_dir, data_file):
        """Create the prediction script content."""
        return f"""
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime
import json

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from stock_net import StockNet, add_technical_indicators
except ImportError:
    print("Error: stock_net module not found")
    sys.exit(1)

def main():
    # Load model info
    feature_info_path = os.path.join('{model_dir}', 'feature_info.json')
    with open(feature_info_path, 'r') as f:
        feature_info = json.load(f)
    
    # Load data
    print("Loading data...")
    data = pd.read_csv('{data_file}')
    
    # Add technical indicators if not present
    required_features = feature_info['feature_columns']
    missing_features = [f for f in required_features if f not in data.columns]
    
    if missing_features:
        print("Adding missing technical indicators...")
        data = add_technical_indicators(data)
    
    # Prepare features
    X = data[required_features].values
    
    # Remove rows with NaN values
    valid_mask = ~np.isnan(X).any(axis=1)
    X = X[valid_mask]
    data_clean = data[valid_mask].copy()
    
    if len(X) == 0:
        print("Error: No valid data after preprocessing")
        return
    
    # Normalize features
    norm_info = feature_info['normalization']
    X_min = np.array(norm_info['X_min'])
    X_max = np.array(norm_info['X_max'])
    
    X_normalized = (X - X_min) / (X_max - X_min)
    
    # Load model
    print("Loading model...")
    input_size = X_normalized.shape[1]
    hidden_size = 64  # Default, should match training
    output_size = 1
    
    model = StockNet(input_size, hidden_size, output_size)
    
    # Load weights
    model_path = os.path.join('{model_dir}', 'final_model.npz')
    if not os.path.exists(model_path):
        model_path = os.path.join('{model_dir}', 'best_model.npz')
    
    if not os.path.exists(model_path):
        print("Error: No model weights found")
        return
    
    model.load_weights(model_path)
    
    # Make predictions
    print("Making predictions...")
    predictions_normalized = model.predict(X_normalized)
    
    # Denormalize predictions
    y_min = norm_info['y_min']
    y_max = norm_info['y_max']
    predictions = predictions_normalized * (y_max - y_min) + y_min
    
    # Create results dataframe
    results = data_clean.copy()
    results['predicted'] = predictions
    
    # Add actual values if available
    target_column = feature_info['target_column']
    if target_column in results.columns:
        results['actual'] = results[target_column]
        results['error'] = results['actual'] - results['predicted']
        results['error_percent'] = (results['error'] / results['actual']) * 100
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join('{model_dir}', f'predictions_{{timestamp}}.csv')
    
    results.to_csv(output_file, index=False)
    print(f"Predictions saved to: {{output_file}}")
    
    # Print summary statistics
    if 'actual' in results.columns:
        mse = np.mean(results['error'] ** 2)
        mae = np.mean(np.abs(results['error']))
        mape = np.mean(np.abs(results['error_percent']))
        
        print(f"\\nPrediction Summary:")
        print(f"Mean Squared Error: {{mse:.6f}}")
        print(f"Mean Absolute Error: {{mae:.6f}}")
        print(f"Mean Absolute Percentage Error: {{mape:.2f}}%")
    
    return output_file

if __name__ == "__main__":
    main()
"""
    
    def _run_prediction_process(self, script_path, model_dir, data_file, callback):
        """Run the prediction process in a separate thread."""
        try:
            # Run the prediction script
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.prediction_process = process
            
            # Monitor output
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    print(output.strip())  # Print to console
            
            # Get return code
            return_code = process.poll()
            
            # Handle completion
            if return_code == 0:
                # Find the output file from the last line
                output_file = None
                for line in reversed(output_lines):
                    if "Predictions saved to:" in line:
                        output_file = line.split(": ")[1]
                        break
                
                self._prediction_completed_success(output_file, callback)
            else:
                stderr = process.stderr.read()
                self._prediction_completed_error(stderr, callback)
                
        except Exception as e:
            self.logger.error(f"Error in prediction process: {e}")
            self._prediction_completed_error(str(e), callback)
        finally:
            self.is_predicting = False
            if os.path.exists(script_path):
                os.unlink(script_path)
    
    def _prediction_completed_success(self, output_file, callback):
        """Handle successful prediction completion."""
        try:
            # Update GUI
            if callback:
                callback('completed', output_file)
            
            # Show success message
            self.parent_gui.root.after(0, lambda: messagebox.showinfo(
                "Prediction Complete", 
                f"Prediction completed successfully!\nResults saved to: {output_file}"
            ))
            
        except Exception as e:
            self.logger.error(f"Error handling prediction completion: {e}")
    
    def _prediction_completed_error(self, error_msg, callback):
        """Handle prediction error completion."""
        try:
            # Update GUI
            if callback:
                callback('error', error_msg)
            
            # Show error message
            self.parent_gui.root.after(0, lambda: messagebox.showerror(
                "Prediction Error", 
                f"Prediction failed:\n{error_msg}"
            ))
            
        except Exception as e:
            self.logger.error(f"Error handling prediction error: {e}")
    
    def get_prediction_files(self, model_dir):
        """Get list of prediction files for a model."""
        try:
            if not os.path.exists(model_dir):
                return []
            
            # Look for prediction CSV files
            prediction_files = []
            for file in os.listdir(model_dir):
                if file.startswith('predictions_') and file.endswith('.csv'):
                    file_path = os.path.join(model_dir, file)
                    prediction_files.append(file_path)
            
            # Sort by modification time (newest first)
            prediction_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return prediction_files
            
        except Exception as e:
            self.logger.error(f"Error getting prediction files: {e}")
            return []
    
    def load_prediction_results(self, prediction_file):
        """Load prediction results from a CSV file."""
        try:
            if not os.path.exists(prediction_file):
                raise FileNotFoundError(f"Prediction file not found: {prediction_file}")
            
            # Load the CSV file
            df = pd.read_csv(prediction_file)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading prediction results: {e}")
            raise
    
    def get_prediction_summary(self, prediction_file):
        """Get summary statistics for prediction results."""
        try:
            df = self.load_prediction_results(prediction_file)
            
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
            raise