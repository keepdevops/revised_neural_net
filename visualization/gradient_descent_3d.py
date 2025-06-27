"""
3D Gradient Descent Visualization

This module creates a 3D visualization of the gradient descent process for neural network training,
emphasizing the loss path as weights are updated, and saves MPEG animations and PNG snapshots.

Supports configuration via JSON file or command line arguments.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import os
import glob
import json
from datetime import datetime
import argparse
import sys

def load_config(config_file=None):
    """Load configuration from JSON file or return default configuration."""
    default_config = {
        "visualization_settings": {
            "model_dir": None,
            "color": "viridis",
            "point_size": 8,
            "line_width": 3,
            "surface_alpha": 0.6,
            "w1_range": [-2.0, 2.0],
            "w2_range": [-2.0, 2.0],
            "n_points": 30,
            "view_elev": 30.0,
            "view_azim": 45.0,
            "fps": 30,
            "save_png": True,
            "save_mpeg": True,
            "output_resolution": [1000, 800],
            "w1_index": 0,
            "w2_index": 0
        }
    }
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"Loaded configuration from {config_file}")
            return config
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
            print("Using default configuration")
    
    return default_config

def find_latest_model_dir():
    """Find the most recent model directory."""
    model_dirs = glob.glob("model_*")
    if not model_dirs:
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        if os.path.exists(models_dir):
            model_dirs = glob.glob(os.path.join(models_dir, "model_*"))
        if not model_dirs:
            raise FileNotFoundError("No model directories found. Please train a model first.")
    return max(model_dirs, key=os.path.getctime)

def load_training_data(model_dir):
    """Load training history and normalization parameters."""
    model_dir = os.path.abspath(model_dir)
    
    scaler_mean_file = os.path.join(model_dir, "scaler_mean.csv")
    scaler_std_file = os.path.join(model_dir, "scaler_std.csv")
    target_min_file = os.path.join(model_dir, "target_min.csv")
    target_max_file = os.path.join(model_dir, "target_max.csv")
    feature_info_file = os.path.join(model_dir, "feature_info.json")
    weights_dir = os.path.join(model_dir, "weights_history")
    
    if not all(os.path.exists(f) for f in [scaler_mean_file, scaler_std_file, feature_info_file]):
        raise FileNotFoundError(f"Normalization parameters not found in {model_dir}")
    
    with open(feature_info_file, 'r') as f:
        feature_info = json.load(f)
    
    X_mean = np.loadtxt(scaler_mean_file, delimiter=',')
    X_range = np.loadtxt(scaler_std_file, delimiter=',')
    Y_min = float(np.loadtxt(target_min_file, delimiter=',')) if os.path.exists(target_min_file) else None
    Y_max = float(np.loadtxt(target_max_file, delimiter=',')) if os.path.exists(target_max_file) else None
    
    norm_params = {
        'X_mean': X_mean.tolist() if X_mean.ndim > 0 else [X_mean.item()],
        'X_range': X_range.tolist() if X_range.ndim > 0 else [X_range.item()],
        'Y_min': Y_min,
        'Y_max': Y_max,
        'x_features': feature_info.get('x_features', []),
        'y_feature': feature_info.get('y_feature', '')
    }
    
    training_losses_file = os.path.join(model_dir, "training_losses.csv")
    if not os.path.exists(training_losses_file):
        raise FileNotFoundError(f"Training history not found in {model_dir}")
    
    losses = np.loadtxt(training_losses_file, delimiter=',')
    if losses.ndim > 1:
        losses = losses[:, 0]  # Use training losses
    else:
        losses = losses
    
    # Load weight history
    weights_files = sorted(glob.glob(os.path.join(weights_dir, "weights_history_*.npz")))
    weights = []
    if weights_files:
        for wf in weights_files:
            with np.load(wf) as data:
                weights.append({
                    'W1': data['W1'],
                    'W2': data['W2']
                })
    else:
        print("No weight history found, using placeholder weights")
        weights = [{'W1': np.zeros((len(norm_params['x_features']), 4)), 
                    'W2': np.zeros((4, 1))} for _ in range(len(losses))]
    
    history = {
        'losses': losses.tolist(),
        'weights': weights,
        'epochs': list(range(len(losses)))
    }
    
    return norm_params, history

def compute_loss_surface(X, y, w1_range, w2_range, n_points=50):
    """Compute the loss surface for visualization."""
    # Ensure inputs are numeric
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    print(f"X shape: {X.shape}, X dtype: {X.dtype}")
    print(f"y shape: {y.shape}, y dtype: {y.dtype}")
    
    w1 = np.linspace(w1_range[0], w1_range[1], n_points)
    w2 = np.linspace(w2_range[0], w2_range[1], n_points)
    W1, W2 = np.meshgrid(w1, w2)
    Z = np.zeros_like(W1)
    
    X_viz = X[:, :2] if X.shape[1] > 2 else X
    print(f"Using first 2 features out of {X.shape[1]} for visualization")
    print(f"X_viz shape: {X_viz.shape}, X_viz dtype: {X_viz.dtype}")
    
    for i in range(n_points):
        for j in range(n_points):
            w = np.array([[W1[i, j]], [W2[i, j]]], dtype=np.float64)
            if w.shape[0] != X_viz.shape[1]:
                w = np.vstack([w, np.zeros((X_viz.shape[1] - w.shape[0], 1), dtype=np.float64)])
            y_pred = X_viz @ w
            Z[i, j] = np.mean((y - y_pred) ** 2)
    
    return W1, W2, Z

def extract_weight_by_index(weights, index, layer='W1'):
    """Extract a specific weight by index from the flattened weight array."""
    try:
        if layer == 'W1':
            w_flat = weights['W1'].flatten()
        else:
            w_flat = weights['W2'].flatten()
        
        if 0 <= index < len(w_flat):
            return w_flat[index]
        else:
            print(f"Warning: Index {index} out of range for {layer} (size: {len(w_flat)}), using index 0")
            return w_flat[0] if len(w_flat) > 0 else 0.0
    except (IndexError, KeyError, AttributeError) as e:
        print(f"Warning: Could not extract weight at index {index} from {layer}: {e}")
        return 0.0

class GradientDescentVisualizer:
    def __init__(self, model_dir=None, w1_range=(-2, 2), w2_range=(-2, 2), n_points=50,
                 view_elev=30, view_azim=45, fps=30, color='viridis', point_size=8, 
                 line_width=3, surface_alpha=0.6, output_resolution=(1200, 800),
                 w1_index=0, w2_index=0):
        self.model_dir = model_dir or find_latest_model_dir()
        self.w1_range = w1_range
        self.w2_range = w2_range
        self.n_points = n_points
        self.view_elev = view_elev
        self.view_azim = view_azim
        self.fps = fps
        self.color = color
        self.point_size = point_size
        self.line_width = line_width
        self.surface_alpha = surface_alpha
        self.output_resolution = output_resolution
        self.w1_index = w1_index
        self.w2_index = w2_index
        
        self.norm_params, self.history = load_training_data(self.model_dir)
        
        data_file = os.path.join(self.model_dir, "training_data.csv")
        if os.path.exists(data_file):
            try:
                df = pd.read_csv(data_file)
                # Ensure we only use numeric columns
                x_features = [f for f in self.norm_params['x_features'] if f in df.columns and df[f].dtype in ['int64', 'float64']]
                if not x_features:
                    raise ValueError("No numeric features found in training data")
                
                X = df[x_features].values.astype(np.float64)
                y = df[self.norm_params['y_feature']].values.astype(np.float64).reshape(-1, 1)
                self.X = X
                self.y = y
                self.has_training_data = True
                print(f"Loaded training data with {X.shape[0]} samples and {X.shape[1]} features")
            except Exception as e:
                print(f"Error loading training data: {e}, creating synthetic visualization...")
                self.X = np.random.randn(100, len(self.norm_params['x_features']))
                self.y = np.random.randn(100, 1)
                self.has_training_data = False
        else:
            print(f"Training data not found in {self.model_dir}, creating synthetic visualization...")
            # Create synthetic data with proper numeric types
            n_features = max(2, len(self.norm_params['x_features']))
            self.X = np.random.randn(100, n_features).astype(np.float64)
            self.y = np.random.randn(100, 1).astype(np.float64)
            self.has_training_data = False
        
        self.W1, self.W2, self.Z = compute_loss_surface(self.X, self.y, w1_range, w2_range, n_points)
        
        # Set figure size based on output_resolution (pixels to inches at 100 DPI)
        dpi = 100
        fig_width = self.output_resolution[0] / dpi
        fig_height = self.output_resolution[1] / dpi
        self.fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.view_init(elev=self.view_elev, azim=self.view_azim)
        
        # Plot loss surface with better visibility
        self.surface = self.ax.plot_surface(self.W1, self.W2, self.Z, 
                                          cmap=self.color, alpha=0.8,  # Increased alpha for better visibility
                                          linewidth=0.5,  # Add grid lines
                                          antialiased=True)  # Enable antialiasing
        
        # Add colorbar for better surface visualization
        self.fig.colorbar(self.surface, ax=self.ax, shrink=0.5, aspect=5)
        
        # Debug information about surface
        print(f"🎨 3D surface created:")
        print(f"   Surface object: {self.surface}")
        print(f"   Surface alpha: 0.8")
        print(f"   Surface cmap: {self.color}")
        print(f"   Z range: {np.min(self.Z):.6f} to {np.max(self.Z):.6f}")
        print(f"   Z std: {np.std(self.Z):.6f}")
        
        # Initialize loss path (thicker line, distinct color)
        self.progress_line = self.ax.plot([], [], [], 'r-', lw=self.line_width, 
                                        label='Loss Path', alpha=0.8)[0]
        self.current_point = self.ax.plot([], [], [], 'ro', markersize=self.point_size, 
                                        label='Current Position')[0]
        
        # Initialize start and end points
        self.start_point = self.ax.plot([], [], [], 'go', markersize=self.point_size + 2, 
                                      label='Start')[0]
        self.end_point = self.ax.plot([], [], [], 'bo', markersize=self.point_size + 2, 
                                    label='End')[0]
        
        self.ax.set_xlabel(f'Weight 1 (Index {w1_index})')
        self.ax.set_ylabel(f'Weight 2 (Index {w2_index})')
        self.ax.set_zlabel('Loss')
        self.ax.legend(loc='upper right')
        
        title_text = f"Gradient Descent Loss Path\nModel: {os.path.basename(self.model_dir)}"
        if not self.has_training_data:
            title_text += " (Synthetic)"
        self.fig.suptitle(title_text, fontsize=14)
        
        self.text = self.fig.text(0.02, 0.02, '', fontsize=10)
        self.animation = None

    def update(self, frame):
        """Update the animation frame with loss path."""
        if frame >= len(self.history['losses']):
            return
        
        if frame == 0:
            self.progress_line.set_data([], [])
            self.progress_line.set_3d_properties([])
            self.current_point.set_data([], [])
            self.current_point.set_3d_properties([])
            self.start_point.set_data([], [])
            self.start_point.set_3d_properties([])
            self.end_point.set_data([], [])
            self.end_point.set_3d_properties([])
        
        # Get weights for current frame with better error handling
        weights = self.history['weights'][min(frame, len(self.history['weights']) - 1)]
        
        # Extract weights using specified indices
        w1 = extract_weight_by_index(weights, self.w1_index, 'W1')
        w2 = extract_weight_by_index(weights, self.w2_index, 'W2')
        
        loss = self.history['losses'][frame]
        
        # Collect path data with better error handling
        x, y = [], []
        for i in range(min(frame + 1, len(self.history['weights']))):
            try:
                w = self.history['weights'][i]
                x_val = extract_weight_by_index(w, self.w1_index, 'W1')
                y_val = extract_weight_by_index(w, self.w2_index, 'W2')
                
                # Clamp values to stay within visualization bounds
                x_val = np.clip(x_val, self.w1_range[0], self.w1_range[1])
                y_val = np.clip(y_val, self.w2_range[0], self.w2_range[1])
                
                x.append(x_val)
                y.append(y_val)
            except (IndexError, KeyError) as e:
                print(f"Warning: Could not extract weights for path point {i}: {e}")
                x.append(0.0)
                y.append(0.0)
        
        z = self.history['losses'][:frame + 1]
        
        # Ensure we have the same number of points
        while len(z) < len(x):
            z.append(z[-1] if z else 0.0)
        while len(x) < len(z):
            x.append(x[-1] if x else 0.0)
            y.append(y[-1] if y else 0.0)
        
        # Clamp current position to bounds as well
        w1_clamped = np.clip(w1, self.w1_range[0], self.w1_range[1])
        w2_clamped = np.clip(w2, self.w2_range[0], self.w2_range[1])
        
        # Update loss path
        if x and y and z:
            self.progress_line.set_data(x, y)
            self.progress_line.set_3d_properties(z)
        
        # Update current position (clamped)
        self.current_point.set_data([w1_clamped], [w2_clamped])
        self.current_point.set_3d_properties([loss])
        
        # Update start point (first epoch)
        if frame == 0 and x:
            self.start_point.set_data([x[0]], [y[0]])
            self.start_point.set_3d_properties([z[0]])
        
        # Update end point (last epoch)
        if frame == len(self.history['losses']) - 1 and x:
            self.end_point.set_data([x[-1]], [y[-1]])
            self.end_point.set_3d_properties([z[-1]])
        
        # Show original values in text, but note if they were clamped
        w1_note = " (clamped)" if w1 != w1_clamped else ""
        w2_note = " (clamped)" if w2 != w2_clamped else ""
        self.text.set_text(f'Epoch: {frame + 1}\nLoss: {loss:.6f}\nW1[{self.w1_index}]: {w1:.4f}{w1_note}\nW2[{self.w2_index}]: {w2:.4f}{w2_note}')
        
        # Return all objects that need to be redrawn, including the surface
        return (self.surface, self.progress_line, self.current_point, self.start_point, self.end_point, self.text)

    def save_plots(self, frames=[0, None, -1], plots_dir=None):
        """Save PNG snapshots of the visualization at specified frames."""
        if plots_dir is None:
            plots_dir = os.path.join(self.model_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # If None is provided, use middle frame
        if None in frames:
            frames[frames.index(None)] = len(self.history['losses']) // 2
        
        for frame in frames:
            if frame < 0:
                frame = len(self.history['losses']) + frame
            if frame >= len(self.history['losses']):
                continue
            
            # Update the plot for this frame
            self.update(frame)
            
            # Save the figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'gradient_descent_3d_frame_{frame}_{timestamp}.png'
            filepath = os.path.join(plots_dir, filename)
            self.fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved plot: {filepath}")

    def save_mpeg_animation(self, plots_dir=None):
        """Save MPEG animation of the gradient descent process using conda ffmpeg."""
        if plots_dir is None:
            plots_dir = os.path.join(self.model_dir, 'plots')
        
        print(f"🎬 save_mpeg_animation() called")
        print(f"📁 Model directory: {self.model_dir}")
        print(f"📂 Plots directory: {plots_dir}")
        
        os.makedirs(plots_dir, exist_ok=True)
        print(f"✅ Plots directory created/verified: {plots_dir}")
        
        try:
            # Create animation
            print(f"🎞️  Creating animation with {len(self.history['losses'])} frames at {self.fps} fps")
            anim = animation.FuncAnimation(
                self.fig, self.update,
                frames=len(self.history['losses']),
                interval=1000/self.fps,
                blit=False,  # Keep False for 3D plots
                repeat=False
            )
            
            # Try to save as MPEG first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f"⏰ Timestamp: {timestamp}")
            
            # Method 1: Try matplotlib ffmpeg writer (uses conda ffmpeg)
            try:
                filename = f'gradient_descent_3d_animation_{timestamp}.mp4'
                filepath = os.path.join(plots_dir, filename)
                print(f"🎬 Attempting to save MP4 using matplotlib ffmpeg (conda): {filepath}")
                
                # Use ffmpeg writer for MPEG output (uses conda ffmpeg)
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=self.fps, metadata=dict(artist='Neural Network Training'), bitrate=1800)
                
                anim.save(filepath, writer=writer, dpi=100)
                print(f"✅ Successfully saved MP4 animation using conda ffmpeg: {filepath}")
                print(f"📊 File size: {os.path.getsize(filepath):,} bytes")
                return filepath
                
            except Exception as mpeg_error:
                print(f"❌ MP4 saving with matplotlib ffmpeg failed: {mpeg_error}")
                print("🔄 Trying imageio-ffmpeg...")
                
                # Method 2: Try imageio-ffmpeg (if available)
                try:
                    filename = f'gradient_descent_3d_animation_{timestamp}.mp4'
                    filepath = os.path.join(plots_dir, filename)
                    print(f"🎬 Attempting to save MP4 using imageio-ffmpeg: {filepath}")
                    
                    # Use imageio-ffmpeg writer for MPEG output
                    import imageio_ffmpeg
                    writer = imageio_ffmpeg.write_frames(filepath, size=(self.output_resolution[0], self.output_resolution[1]), fps=self.fps)
                    writer.send(None)  # Initialize the writer
                    
                    # Save frames
                    print(f"📸 Saving {len(self.history['losses'])} frames...")
                    for frame in range(len(self.history['losses'])):
                        self.update(frame)
                        # Capture the current figure as an image
                        import io
                        buf = io.BytesIO()
                        self.fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                        buf.seek(0)
                        import imageio
                        img = imageio.imread(buf)
                        writer.send(img)
                    
                    writer.close()
                    print(f"✅ Successfully saved MP4 animation using imageio-ffmpeg: {filepath}")
                    print(f"📊 File size: {os.path.getsize(filepath):,} bytes")
                    return filepath
                    
                except ImportError:
                    print("❌ imageio-ffmpeg not available")
                except Exception as mpeg_error2:
                    print(f"❌ MP4 saving with imageio-ffmpeg failed: {mpeg_error2}")
                
                print("🔄 Trying GIF format instead...")
                
                # Method 3: Fallback to GIF
                try:
                    filename = f'gradient_descent_3d_animation_{timestamp}.gif'
                    filepath = os.path.join(plots_dir, filename)
                    print(f"🎬 Attempting to save GIF: {filepath}")
                    
                    # Use Pillow writer for GIF output
                    Writer = animation.writers['pillow']
                    writer = Writer(fps=self.fps)
                    
                    anim.save(filepath, writer=writer, dpi=100)
                    print(f"✅ Successfully saved GIF animation: {filepath}")
                    print(f"📊 File size: {os.path.getsize(filepath):,} bytes")
                    return filepath
                    
                except Exception as gif_error:
                    print(f"❌ GIF saving failed: {gif_error}")
                    print("🔄 Falling back to PNG frame saving...")
                    
                    # Final fallback: save individual frames
                    print(f"📸 Saving PNG frames as fallback...")
                    self.save_plots(frames=range(0, len(self.history['losses']), max(1, len(self.history['losses'])//10)))
                    return None
            
        except Exception as e:
            print(f"❌ Error saving animation: {e}")
            # Fallback to saving individual frames
            print("🔄 Falling back to PNG frame saving...")
            self.save_plots(frames=range(0, len(self.history['losses']), max(1, len(self.history['losses'])//10)))
            return None

    def animate(self, save_png=False, save_mpeg=False):
        """Create and display the animation, optionally saving PNGs and MPEG."""
        if save_png:
            # Save plots at initial, middle, and final frames
            self.save_plots(frames=[0, None, -1])
        
        if save_mpeg:
            # Save MPEG animation
            self.save_mpeg_animation()
        
        # For saving modes, don't show the animation
        if save_png or save_mpeg:
            print("Animation saved. Display not shown in save mode.")
            return
        
        # Create animation with proper settings for 3D plots
        try:
            self.animation = animation.FuncAnimation(
                self.fig, self.update,
                frames=len(self.history['losses']),
                interval=1000/self.fps,
                blit=False,  # Keep False for 3D plots
                repeat=True
            )
            
            plt.show()
        except Exception as e:
            print(f"Error creating animation: {e}")
            # Fallback: just show the final frame
            self.update(len(self.history['losses']) - 1)
            plt.show()

def main():
    print("🎬 gradient_descent_3d.py - Starting 3D Gradient Descent Visualization")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description='3D Gradient Descent Visualization')
    parser.add_argument('--config', type=str, help='Path to JSON configuration file')
    parser.add_argument('--model_dir', type=str, help='Directory containing the model files')
    parser.add_argument('--color', type=str, default='viridis', help='Color map for the surface')
    parser.add_argument('--point_size', type=int, default=8, help='Size of the current point marker')
    parser.add_argument('--line_width', type=int, default=3, help='Width of the gradient descent path')
    parser.add_argument('--surface_alpha', type=float, default=0.6, help='Alpha transparency of the surface')
    parser.add_argument('--w1_range', type=float, nargs=2, default=[-2, 2], help='Range for weight 1')
    parser.add_argument('--w2_range', type=float, nargs=2, default=[-2, 2], help='Range for weight 2')
    parser.add_argument('--n_points', type=int, default=30, help='Number of points in surface grid')
    parser.add_argument('--view_elev', type=float, default=30, help='Initial elevation angle')
    parser.add_argument('--view_azim', type=float, default=45, help='Initial azimuth angle')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second for animation')
    parser.add_argument('--save_png', action='store_true', help='Save PNG snapshots of visualization')
    parser.add_argument('--save_mpeg', action='store_true', help='Save MPEG animation of visualization')
    parser.add_argument('--w1_index', type=int, default=0, help='Index for W1 weight selection')
    parser.add_argument('--w2_index', type=int, default=0, help='Index for W2 weight selection')
    parser.add_argument('--output_resolution', type=int, nargs=2, default=[1200, 800], 
                       help='Output resolution [width, height] in pixels')
    
    args = parser.parse_args()
    
    print(f"📋 Command line arguments:")
    print(f"   --model_dir: {args.model_dir}")
    print(f"   --save_png: {args.save_png}")
    print(f"   --save_mpeg: {args.save_mpeg}")
    print(f"   --fps: {args.fps}")
    print(f"   --output_resolution: {args.output_resolution}")
    
    # Load configuration from file if provided
    config = load_config(args.config)
    viz_settings = config.get('visualization_settings', {})
    
    # Override config with command line arguments
    model_dir = args.model_dir or viz_settings.get('model_dir') or find_latest_model_dir()
    print(f"🎯 Using model directory: {model_dir}")
    
    try:
        print(f"🔧 Creating GradientDescentVisualizer...")
        visualizer = GradientDescentVisualizer(
            model_dir=model_dir,
            w1_range=tuple(args.w1_range),
            w2_range=tuple(args.w2_range),
            n_points=args.n_points,
            view_elev=args.view_elev,
            view_azim=args.view_azim,
            fps=args.fps,
            color=args.color,
            point_size=args.point_size,
            line_width=args.line_width,
            surface_alpha=args.surface_alpha,
            output_resolution=tuple(args.output_resolution),
            w1_index=args.w1_index,
            w2_index=args.w2_index
        )
        print(f"✅ GradientDescentVisualizer created successfully")
        print(f"🎬 Starting animation with save_png={args.save_png}, save_mpeg={args.save_mpeg}")
        visualizer.animate(save_png=args.save_png, save_mpeg=args.save_mpeg)
        print(f"✅ Animation completed successfully")
    except Exception as e:
        print(f"❌ Error creating visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
