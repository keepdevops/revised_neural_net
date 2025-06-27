"""
Training Manager Module

Handles all training-related operations for the stock prediction GUI.
This module manages model training, parameter validation, and training progress.
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
import queue
import tempfile

class TrainingManager:
    """Manages training operations for the stock prediction system."""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.logger = logging.getLogger(__name__)
        
        # Training state
        self.training_process = None
        self.training_thread = None
        self.training_queue = queue.Queue()
        self.is_training = False
        
        # Current training state for live plotting
        self.current_epoch = 0
        self.current_loss = None
        self.current_val_loss = None
        self.total_epochs = 0
        
        # Training parameters
        self.default_params = {
            'epochs': 100,
            'learning_rate': 0.001,
            'batch_size': 32,
            'hidden_size': 64,
            'validation_split': 0.2,
            'early_stopping_patience': 10,
            'history_save_interval': 10,
            'random_seed': 42,
            'save_history': True,
            'memory_optimization': False
        }
    
    def validate_training_parameters(self, params):
        """Validate training parameters."""
        errors = []
        
        # Check required parameters
        required_params = ['data_file', 'output_dir', 'epochs', 'learning_rate', 
                          'batch_size', 'hidden_size']
        
        for param in required_params:
            if param not in params or not params[param]:
                errors.append(f"Missing required parameter: {param}")
        
        # Validate numeric parameters
        numeric_params = {
            'epochs': (int, 1, 10000),
            'learning_rate': (float, 0.0001, 1.0),
            'batch_size': (int, 1, 1000),
            'hidden_size': (int, 1, 1000),
            'validation_split': (float, 0.0, 0.5),
            'early_stopping_patience': (int, 1, 100),
            'history_save_interval': (int, 1, 100),
            'random_seed': (int, 0, 999999)
        }
        
        for param, (param_type, min_val, max_val) in numeric_params.items():
            if param in params:
                try:
                    value = param_type(params[param])
                    if value < min_val or value > max_val:
                        errors.append(f"{param} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"{param} must be a valid {param_type.__name__}")
        
        # Validate file paths
        if 'data_file' in params and params['data_file']:
            if not os.path.exists(params['data_file']):
                errors.append("Data file does not exist")
        
        if 'output_dir' in params and params['output_dir']:
            if not os.path.exists(params['output_dir']):
                try:
                    os.makedirs(params['output_dir'])
                except OSError:
                    errors.append("Cannot create output directory")
        
        return errors
    
    def start_training(self, params, callback=None):
        """Start training process."""
        try:
            # Validate parameters
            errors = self.validate_training_parameters(params)
            if errors:
                error_msg = "\n".join(errors)
                messagebox.showerror("Validation Error", f"Invalid parameters:\n{error_msg}")
                return False
            
            # Check if already training
            if self.is_training:
                messagebox.showwarning("Training in Progress", 
                                     "Training is already in progress. Please wait.")
                return False
            
            # For now, just show a success message and simulate training
            # In a real implementation, this would start the actual training process
            self.is_training = True
            
            # Simulate training progress
            def simulate_training():
                try:
                    self.total_epochs = params['epochs']
                    
                    for epoch in range(1, min(params['epochs'], 5) + 1):  # Limit to 5 epochs for demo
                        time.sleep(1)  # Simulate training time
                        loss = 0.1 + (0.9 * np.exp(-epoch / 2))  # Simulate decreasing loss
                        val_loss = loss + 0.05  # Simulate validation loss
                        
                        # Update current training state
                        self.current_epoch = epoch
                        self.current_loss = loss
                        self.current_val_loss = val_loss
                        
                        if callback:
                            progress = (epoch / min(params['epochs'], 5)) * 100
                            callback('progress', (epoch, loss, val_loss, progress))
                    
                    # Training completed
                    model_dir = os.path.join(params['output_dir'], f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    os.makedirs(model_dir, exist_ok=True)
                    
                    if callback:
                        callback('completed', model_dir)
                    
                except Exception as e:
                    if callback:
                        callback('error', str(e))
                finally:
                    self.is_training = False
                    # Reset current state
                    self.current_epoch = 0
                    self.current_loss = None
                    self.current_val_loss = None
            
            # Start training in background thread
            self.training_thread = threading.Thread(target=simulate_training)
            self.training_thread.daemon = True
            self.training_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting training: {e}")
            messagebox.showerror("Training Error", f"Failed to start training: {e}")
            return False
    
    def stop_training(self):
        """Stop the current training process."""
        if self.training_process and self.is_training:
            try:
                self.training_process.terminate()
                self.training_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.training_process.kill()
            finally:
                self.is_training = False
    
    def get_training_status(self):
        """Get current training status."""
        return {
            'is_training': self.is_training,
            'process_active': self.training_process is not None
        }
    
    def cleanup(self):
        """Clean up training resources."""
        self.stop_training()
        if self.training_thread and self.training_thread.is_alive():
            self.training_thread.join(timeout=1) 