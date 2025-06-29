"""
Forward Pass Visualizer for the Stock Prediction GUI.
Shows live visualization of weights and bias during prediction.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import logging
import threading
import time
from collections import deque

class ForwardPassVisualizer:
    """Forward pass visualizer for neural network prediction."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create the visualizer frame
        self.frame = ttk.Frame(parent, padding="5")
        
        # Visualization data
        self.weights_history = deque(maxlen=100)  # Store last 100 weight updates
        self.bias_history = deque(maxlen=100)     # Store last 100 bias updates
        self.prediction_history = deque(maxlen=100)  # Store last 100 predictions
        self.input_history = deque(maxlen=100)    # Store last 100 inputs
        
        # Animation state
        self.is_animating = False
        self.animation_thread = None
        
        # Create the visualization widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Create the visualization widgets."""
        # Title
        title_label = ttk.Label(self.frame, text="Live Forward Pass", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Animation controls
        self.animation_var = tk.BooleanVar(value=False)
        self.animation_check = ttk.Checkbutton(
            control_frame, 
            text="Live Animation", 
            variable=self.animation_var,
            command=self.toggle_animation
        )
        self.animation_check.pack(side="left", padx=(0, 10))
        
        # Clear button
        ttk.Button(control_frame, text="Clear", command=self.clear_visualization).pack(side="right")
        
        # Create matplotlib figure for visualization
        self.create_visualization_plot()
        
        # Status frame
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill="x", pady=(10, 0))
        
        # Status labels
        self.status_var = tk.StringVar(value="Ready for prediction")
        ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 9)).pack(anchor="w")
        
        self.info_var = tk.StringVar(value="No data")
        ttk.Label(status_frame, textvariable=self.info_var, font=("Arial", 8), foreground="gray").pack(anchor="w")
        
    def create_visualization_plot(self):
        """Create the matplotlib visualization plot."""
        # Create figure with subplots
        self.fig = Figure(figsize=(6, 8), dpi=100)
        
        # Weights subplot
        self.weights_ax = self.fig.add_subplot(3, 1, 1)
        self.weights_ax.set_title("Weights Evolution", fontsize=10)
        self.weights_ax.set_ylabel("Weight Value")
        self.weights_ax.grid(True, alpha=0.3)
        
        # Bias subplot
        self.bias_ax = self.fig.add_subplot(3, 1, 2)
        self.bias_ax.set_title("Bias Evolution", fontsize=10)
        self.bias_ax.set_ylabel("Bias Value")
        self.bias_ax.grid(True, alpha=0.3)
        
        # Prediction subplot
        self.pred_ax = self.fig.add_subplot(3, 1, 3)
        self.pred_ax.set_title("Prediction vs Input", fontsize=10)
        self.pred_ax.set_xlabel("Input Value")
        self.pred_ax.set_ylabel("Prediction")
        self.pred_ax.grid(True, alpha=0.3)
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize plots
        self.initialize_plots()
        
    def initialize_plots(self):
        """Initialize the plots with placeholder data."""
        # Weights plot
        self.weights_ax.clear()
        self.weights_ax.set_title("Weights Evolution", fontsize=10)
        self.weights_ax.set_ylabel("Weight Value")
        self.weights_ax.grid(True, alpha=0.3)
        self.weights_ax.text(0.5, 0.5, 'Waiting for prediction...', 
                           ha='center', va='center', transform=self.weights_ax.transAxes,
                           fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        # Bias plot
        self.bias_ax.clear()
        self.bias_ax.set_title("Bias Evolution", fontsize=10)
        self.bias_ax.set_ylabel("Bias Value")
        self.bias_ax.grid(True, alpha=0.3)
        self.bias_ax.text(0.5, 0.5, 'Waiting for prediction...', 
                         ha='center', va='center', transform=self.bias_ax.transAxes,
                         fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        # Prediction plot
        self.pred_ax.clear()
        self.pred_ax.set_title("Prediction vs Input", fontsize=10)
        self.pred_ax.set_xlabel("Input Value")
        self.pred_ax.set_ylabel("Prediction")
        self.pred_ax.grid(True, alpha=0.3)
        self.pred_ax.text(0.5, 0.5, 'Waiting for prediction...', 
                         ha='center', va='center', transform=self.pred_ax.transAxes,
                         fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        self.canvas.draw()
        
    def toggle_animation(self):
        """Toggle live animation on/off."""
        if self.animation_var.get():
            self.start_animation()
        else:
            self.stop_animation()
            
    def start_animation(self):
        """Start the live animation."""
        if not self.is_animating:
            self.is_animating = True
            self.animation_thread = threading.Thread(target=self.animation_loop, daemon=True)
            self.animation_thread.start()
            self.status_var.set("Live animation active")
            
    def stop_animation(self):
        """Stop the live animation."""
        self.is_animating = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
        self.status_var.set("Animation stopped")
        
    def animation_loop(self):
        """Animation loop for live updates."""
        while self.is_animating:
            try:
                self.update_visualization()
                time.sleep(0.1)  # Update every 100ms
            except Exception as e:
                self.logger.error(f"Animation loop error: {e}")
                break
                
    def update_visualization(self):
        """Update the visualization plots."""
        try:
            # Update weights plot
            if len(self.weights_history) > 0:
                self.update_weights_plot()
                
            # Update bias plot
            if len(self.bias_history) > 0:
                self.update_bias_plot()
                
            # Update prediction plot
            if len(self.prediction_history) > 0 and len(self.input_history) > 0:
                self.update_prediction_plot()
                
            # Update info
            self.update_info()
            
            # Redraw canvas
            self.canvas.draw_idle()
            
        except Exception as e:
            self.logger.error(f"Visualization update error: {e}")
            
    def update_weights_plot(self):
        """Update the weights evolution plot."""
        self.weights_ax.clear()
        self.weights_ax.set_title("Weights Evolution", fontsize=10)
        self.weights_ax.set_ylabel("Weight Value")
        self.weights_ax.grid(True, alpha=0.3)
        
        if len(self.weights_history) > 0:
            weights_data = list(self.weights_history)
            x = range(len(weights_data))
            
            # Plot each weight dimension
            weights_array = np.array(weights_data)
            if len(weights_array.shape) > 1:
                for i in range(weights_array.shape[1]):
                    self.weights_ax.plot(x, weights_array[:, i], 
                                       label=f'Weight {i+1}', alpha=0.7, linewidth=1)
                self.weights_ax.legend(fontsize=8)
            else:
                self.weights_ax.plot(x, weights_array, 'b-', alpha=0.7, linewidth=1)
                
        self.weights_ax.set_xlim(0, max(1, len(self.weights_history) - 1))
        
    def update_bias_plot(self):
        """Update the bias evolution plot."""
        self.bias_ax.clear()
        self.bias_ax.set_title("Bias Evolution", fontsize=10)
        self.bias_ax.set_ylabel("Bias Value")
        self.bias_ax.grid(True, alpha=0.3)
        
        if len(self.bias_history) > 0:
            bias_data = list(self.bias_history)
            x = range(len(bias_data))
            self.bias_ax.plot(x, bias_data, 'r-', alpha=0.7, linewidth=1)
            
        self.bias_ax.set_xlim(0, max(1, len(self.bias_history) - 1))
        
    def update_prediction_plot(self):
        """Update the prediction vs input plot."""
        self.pred_ax.clear()
        self.pred_ax.set_title("Prediction vs Input", fontsize=10)
        self.pred_ax.set_xlabel("Input Value")
        self.pred_ax.set_ylabel("Prediction")
        self.pred_ax.grid(True, alpha=0.3)
        
        if len(self.prediction_history) > 0 and len(self.input_history) > 0:
            inputs = list(self.input_history)
            predictions = list(self.prediction_history)
            
            # Use the first input dimension if multiple
            if len(inputs) > 0 and hasattr(inputs[0], '__len__'):
                input_values = [inp[0] if len(inp) > 0 else 0 for inp in inputs]
            else:
                input_values = inputs
            
            # Ensure predictions are scalar values
            prediction_values = []
            for pred in predictions:
                if hasattr(pred, 'item') and hasattr(pred, 'size') and pred.size == 1:
                    prediction_values.append(pred.item())
                elif hasattr(pred, '__len__') and len(pred) > 0:
                    prediction_values.append(pred[0])
                elif hasattr(pred, 'flatten'):
                    # For multi-element arrays, take the first element
                    flattened = pred.flatten()
                    prediction_values.append(flattened[0] if len(flattened) > 0 else 0)
                else:
                    prediction_values.append(pred)
            
            # Ensure input_values are scalar values
            input_scalars = []
            for inp in input_values:
                if hasattr(inp, 'item') and hasattr(inp, 'size') and inp.size == 1:
                    input_scalars.append(inp.item())
                elif hasattr(inp, '__len__') and len(inp) > 0:
                    input_scalars.append(inp[0])
                elif hasattr(inp, 'flatten'):
                    # For multi-element arrays, take the first element
                    flattened = inp.flatten()
                    input_scalars.append(flattened[0] if len(flattened) > 0 else 0)
                else:
                    input_scalars.append(inp)
                
            self.pred_ax.scatter(input_scalars, prediction_values, alpha=0.6, s=20, c='green')
            
            # Add trend line if enough points
            if len(input_scalars) > 2:
                try:
                    # Convert to numpy arrays and ensure they are 1D
                    x_data = np.array(input_scalars).flatten()
                    y_data = np.array(prediction_values).flatten()
                    
                    # Only fit if we have valid numeric data
                    if np.all(np.isfinite(x_data)) and np.all(np.isfinite(y_data)):
                        z = np.polyfit(x_data, y_data, 1)
                        p = np.poly1d(z)
                        x_trend = np.linspace(min(x_data), max(x_data), 100)
                        self.pred_ax.plot(x_trend, p(x_trend), 'r--', alpha=0.5, linewidth=1)
                except Exception as e:
                    # Log the error but don't crash the visualization
                    self.logger.warning(f"Could not fit trend line: {e}")
                
    def update_info(self):
        """Update the information display."""
        info_parts = []
        
        if len(self.weights_history) > 0:
            info_parts.append(f"Steps: {len(self.weights_history)}")
            
        if len(self.prediction_history) > 0:
            recent_pred = self.prediction_history[-1]
            # Handle numpy arrays by extracting scalar value
            if hasattr(recent_pred, 'item') and hasattr(recent_pred, 'size') and recent_pred.size == 1:
                recent_pred = recent_pred.item()
            elif hasattr(recent_pred, '__len__') and len(recent_pred) > 0:
                recent_pred = recent_pred[0]
            elif hasattr(recent_pred, 'flatten'):
                # For multi-element arrays, take the first element
                flattened = recent_pred.flatten()
                recent_pred = flattened[0] if len(flattened) > 0 else 0
            info_parts.append(f"Latest: {recent_pred:.4f}")
            
        if len(self.weights_history) > 0:
            recent_weights = self.weights_history[-1]
            if hasattr(recent_weights, '__len__'):
                info_parts.append(f"Weights: {len(recent_weights)} dims")
            else:
                # Handle numpy arrays by extracting scalar value
                if hasattr(recent_weights, 'item') and hasattr(recent_weights, 'size') and recent_weights.size == 1:
                    recent_weights = recent_weights.item()
                elif hasattr(recent_weights, 'flatten'):
                    # For multi-element arrays, take the first element
                    flattened = recent_weights.flatten()
                    recent_weights = flattened[0] if len(flattened) > 0 else 0
                info_parts.append(f"Weight: {recent_weights:.4f}")
                
        if len(self.bias_history) > 0:
            recent_bias = self.bias_history[-1]
            # Handle numpy arrays by extracting scalar value
            if hasattr(recent_bias, 'item') and hasattr(recent_bias, 'size') and recent_bias.size == 1:
                recent_bias = recent_bias.item()
            elif hasattr(recent_bias, '__len__') and len(recent_bias) > 0:
                recent_bias = recent_bias[0]
            elif hasattr(recent_bias, 'flatten'):
                # For multi-element arrays, take the first element
                flattened = recent_bias.flatten()
                recent_bias = flattened[0] if len(flattened) > 0 else 0
            info_parts.append(f"Bias: {recent_bias:.4f}")
            
        self.info_var.set(" | ".join(info_parts) if info_parts else "No data")
        
    def add_forward_pass_data(self, weights, bias, prediction, input_data):
        """Add new forward pass data to the visualization."""
        try:
            # Add to history
            self.weights_history.append(weights)
            self.bias_history.append(bias)
            self.prediction_history.append(prediction)
            self.input_history.append(input_data)
            
            # Update immediately if animation is off
            if not self.animation_var.get():
                self.update_visualization()
                
        except Exception as e:
            self.logger.error(f"Error adding forward pass data: {e}")
            
    def clear_visualization(self):
        """Clear all visualization data."""
        self.weights_history.clear()
        self.bias_history.clear()
        self.prediction_history.clear()
        self.input_history.clear()
        
        self.initialize_plots()
        self.info_var.set("No data")
        self.status_var.set("Visualization cleared")
        
    def start_prediction_mode(self):
        """Start prediction mode."""
        self.status_var.set("Prediction mode active")
        self.clear_visualization()
        
    def stop_prediction_mode(self):
        """Stop prediction mode."""
        self.status_var.set("Prediction completed")
        self.stop_animation()
        
    def get_frame(self):
        """Get the main frame."""
        return self.frame 