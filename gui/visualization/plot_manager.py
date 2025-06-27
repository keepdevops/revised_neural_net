"""
Plot Manager Module

Handles all plotting and visualization functionality for the stock prediction GUI.
This module centralizes all matplotlib plotting operations and provides
a clean interface for creating and managing various plot types.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import os
import json
import logging
from datetime import datetime
import tempfile
import subprocess
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

class PlotManager:
    """Manages all plotting operations for the stock prediction GUI."""
    
    def __init__(self, parent_gui):
        self.parent_gui = parent_gui
        self.logger = logging.getLogger(__name__)
        
        # Plot state
        self.current_fig = None
        self.current_canvas = None
        self.current_toolbar = None
        self.image_cache = {}
        self.max_cache_size = 10
        
        # Animation state
        self.animation_running = False
        self.current_frame = 0
        self.total_frames = 0
        
        # 3D plot state
        self.gd3d_fig = None
        self.gd3d_ax = None
        self.gd3d_canvas = None
        
    def create_figure_with_toolbar(self, parent, figsize=(10, 6)):
        """Create a matplotlib figure with embedded toolbar."""
        fig = Figure(figsize=figsize)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        
        return fig, canvas, toolbar
    
    def plot_training_results(self, model_dir, parent_frame):
        """Plot training results from a model directory."""
        try:
            # Clear existing plot
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            # Create new figure
            fig, canvas, toolbar = self.create_figure_with_toolbar(parent_frame)
            
            # Load training data
            plots_dir = os.path.join(model_dir, 'plots')
            if not os.path.exists(plots_dir):
                self._show_no_data_message(parent_frame, "No plots directory found")
                return
            
            # Plot actual vs predicted
            actual_vs_pred_file = os.path.join(plots_dir, 'actual_vs_predicted.png')
            if os.path.exists(actual_vs_pred_file):
                self._display_image(actual_vs_pred_file, parent_frame)
            else:
                self._show_no_data_message(parent_frame, "No training plots found")
                
        except Exception as e:
            self.logger.error(f"Error plotting training results: {e}")
            self._show_error_message(parent_frame, f"Error loading plots: {e}")
    
    def plot_prediction_results(self, prediction_file, parent_frame):
        """Plot prediction results from a CSV file."""
        try:
            # Clear existing plot
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            # Load prediction data
            df = pd.read_csv(prediction_file)
            
            # Create new figure
            fig, canvas, toolbar = self.create_figure_with_toolbar(parent_frame)
            
            # Plot predictions
            ax = fig.add_subplot(111)
            
            if 'actual' in df.columns and 'predicted' in df.columns:
                ax.plot(df.index, df['actual'], label='Actual', color='blue')
                ax.plot(df.index, df['predicted'], label='Predicted', color='red')
                ax.set_xlabel('Time Step')
                ax.set_ylabel('Price')
                ax.set_title('Actual vs Predicted Values')
                ax.legend()
                ax.grid(True)
            else:
                # Plot single column if only one exists
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    ax.plot(df.index, df[numeric_cols[0]], label=numeric_cols[0])
                    ax.set_xlabel('Time Step')
                    ax.set_ylabel('Value')
                    ax.set_title('Prediction Results')
                    ax.legend()
                    ax.grid(True)
                else:
                    self._show_no_data_message(parent_frame, "No numeric data found")
                    return
            
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            toolbar.pack(fill="x")
            
        except Exception as e:
            self.logger.error(f"Error plotting prediction results: {e}")
            self._show_error_message(parent_frame, f"Error loading predictions: {e}")
    
    def create_3d_gradient_descent_plot(self, parent_frame, model_dir):
        """Create 3D gradient descent visualization."""
        try:
            # Clear existing plot
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            # Create 3D figure
            self.gd3d_fig = Figure(figsize=(10, 8))
            self.gd3d_ax = self.gd3d_fig.add_subplot(111, projection='3d')
            self.gd3d_canvas = FigureCanvasTkAgg(self.gd3d_fig, master=parent_frame)
            toolbar = NavigationToolbar2Tk(self.gd3d_canvas, parent_frame)
            
            # Load weights history
            weights_dir = os.path.join(model_dir, 'weights_history')
            if not os.path.exists(weights_dir):
                self._show_no_data_message(parent_frame, "No weights history found")
                return
            
            # Load and plot weights
            self._load_and_plot_weights_3d(weights_dir)
            
            self.gd3d_canvas.draw()
            self.gd3d_canvas.get_tk_widget().pack(fill="both", expand=True)
            toolbar.pack(fill="x")
            
        except Exception as e:
            self.logger.error(f"Error creating 3D plot: {e}")
            self._show_error_message(parent_frame, f"Error creating 3D plot: {e}")
    
    def _load_and_plot_weights_3d(self, weights_dir):
        """Load and plot weights in 3D space."""
        try:
            # Load weights files
            weights_files = sorted([f for f in os.listdir(weights_dir) 
                                  if f.endswith('.npz')])
            
            if not weights_files:
                return
            
            # Load first and last weights for comparison
            first_weights = np.load(os.path.join(weights_dir, weights_files[0]))
            last_weights = np.load(os.path.join(weights_dir, weights_files[-1]))
            
            # Extract weight matrices
            w1_start = first_weights['W1'] if 'W1' in first_weights else first_weights['weights']
            w2_start = first_weights['W2'] if 'W2' in first_weights else first_weights['weights']
            
            w1_end = last_weights['W1'] if 'W1' in last_weights else last_weights['weights']
            w2_end = last_weights['W2'] if 'W2' in last_weights else last_weights['weights']
            
            # Create 3D scatter plot
            self.gd3d_ax.clear()
            
            # Plot start weights
            x1, y1, z1 = w1_start.flatten(), w2_start.flatten(), np.zeros_like(w1_start.flatten())
            self.gd3d_ax.scatter(x1, y1, z1, c='blue', marker='o', s=20, alpha=0.6, label='Start')
            
            # Plot end weights
            x2, y2, z2 = w1_end.flatten(), w2_end.flatten(), np.ones_like(w1_end.flatten())
            self.gd3d_ax.scatter(x2, y2, z2, c='red', marker='^', s=20, alpha=0.6, label='End')
            
            self.gd3d_ax.set_xlabel('W1 Weights')
            self.gd3d_ax.set_ylabel('W2 Weights')
            self.gd3d_ax.set_zlabel('Training Step')
            self.gd3d_ax.set_title('Gradient Descent in Weight Space')
            self.gd3d_ax.legend()
            
        except Exception as e:
            self.logger.error(f"Error loading weights for 3D plot: {e}")
    
    def create_live_training_plot(self, parent_frame):
        """Create live training plot window."""
        try:
            # Create new window
            live_window = tk.Toplevel(self.parent_gui.root)
            live_window.title("Live Training Progress")
            live_window.geometry("800x600")
            
            # Create figure
            fig, canvas, toolbar = self.create_figure_with_toolbar(live_window)
            ax = fig.add_subplot(111)
            
            # Initialize plot data
            epochs = []
            losses = []
            
            def update_plot(epoch, loss):
                epochs.append(epoch)
                losses.append(loss)
                
                ax.clear()
                ax.plot(epochs, losses, 'b-')
                ax.set_xlabel('Epoch')
                ax.set_ylabel('Loss')
                ax.set_title('Training Loss')
                ax.grid(True)
                canvas.draw()
            
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            toolbar.pack(fill="x")
            
            return live_window, update_plot
            
        except Exception as e:
            self.logger.error(f"Error creating live training plot: {e}")
            return None, None
    
    def generate_animation(self, model_dir, output_format='mp4'):
        """Generate animation from weights history."""
        try:
            weights_dir = os.path.join(model_dir, 'weights_history')
            if not os.path.exists(weights_dir):
                raise FileNotFoundError("No weights history found")
            
            # Create temporary script for animation
            script_content = self._create_animation_script(model_dir, output_format)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                temp_script = f.name
            
            # Run animation generation
            result = subprocess.run([sys.executable, temp_script], 
                                  capture_output=True, text=True)
            
            # Clean up
            os.unlink(temp_script)
            
            if result.returncode != 0:
                raise RuntimeError(f"Animation generation failed: {result.stderr}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating animation: {e}")
            return False
    
    def _create_animation_script(self, model_dir, output_format):
        """Create temporary script for animation generation."""
        return f"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import glob

# Load weights history
weights_dir = '{model_dir}/weights_history'
weights_files = sorted(glob.glob(os.path.join(weights_dir, '*.npz')))

# Create animation
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

def animate(frame):
    ax.clear()
    weights = np.load(weights_files[frame])
    
    # Extract weights
    w1 = weights['W1'] if 'W1' in weights else weights['weights']
    w2 = weights['W2'] if 'W2' in weights else weights['weights']
    
    # Create scatter plot
    x, y, z = w1.flatten(), w2.flatten(), np.full_like(w1.flatten(), frame)
    ax.scatter(x, y, z, c='blue', alpha=0.6)
    
    ax.set_xlabel('W1 Weights')
    ax.set_ylabel('W2 Weights')
    ax.set_zlabel('Training Step')
    ax.set_title(f'Gradient Descent - Step {{frame}}')

# Create animation
anim = animation.FuncAnimation(fig, animate, frames=len(weights_files), 
                             interval=100, repeat=True)

# Save animation
output_file = '{model_dir}/plots/gradient_descent_3d_animation.{output_format}'
anim.save(output_file, writer='ffmpeg' if output_format == 'mp4' else 'pillow')
plt.close()
"""
    
    def _display_image(self, image_path, parent_frame):
        """Display an image in the parent frame."""
        try:
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            
            label = tk.Label(parent_frame, image=photo)
            label.image = photo  # Keep a reference
            label.pack(fill="both", expand=True)
            
        except Exception as e:
            self.logger.error(f"Error displaying image: {e}")
            self._show_error_message(parent_frame, f"Error loading image: {e}")
    
    def _show_no_data_message(self, parent_frame, message):
        """Show a message when no data is available."""
        label = tk.Label(parent_frame, text=message, 
                        font=("Arial", 12), fg="gray")
        label.pack(expand=True)
    
    def _show_error_message(self, parent_frame, message):
        """Show an error message."""
        label = tk.Label(parent_frame, text=message, 
                        font=("Arial", 12), fg="red")
        label.pack(expand=True)
    
    def clear_cache(self):
        """Clear the image cache."""
        self.image_cache.clear()
    
    def get_cached_image(self, key):
        """Get an image from cache."""
        return self.image_cache.get(key)
    
    def cache_image(self, key, image):
        """Cache an image."""
        if len(self.image_cache) >= self.max_cache_size:
            # Remove oldest item
            oldest_key = next(iter(self.image_cache))
            del self.image_cache[oldest_key]
        
        self.image_cache[key] = image
