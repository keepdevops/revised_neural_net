"""
Floating 3D Window Module

This module provides a floating window for 3D Matplotlib plots with interactive controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class Floating3DWindow:
    """Floating window for 3D Matplotlib plots."""
    
    def __init__(self, parent, model_path, plot_params, on_close=None):
        """
        Initialize the floating 3D window.
        
        Args:
            parent: Parent window
            model_path: Path to the model directory
            plot_params: Dictionary of plot parameters
            on_close: Callback function when window is closed
        """
        self.parent = parent
        self.model_path = model_path
        self.plot_params = plot_params
        self.on_close = on_close
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        self.animation = None
        self.is_animating = False
        
        # Create the window
        self.create_window()
        
        # Load model data
        self.load_model_data()
        
        # Create the plot
        self.create_plot()
        
        # Setup controls
        self.setup_controls()
    
    def create_window(self):
        """Create the floating window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"3D Plot - {os.path.basename(self.model_path)}")
        self.window.geometry("1000x800")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        # Configure window
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Create plot frame
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.grid(row=0, column=0, sticky="nsew")
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        
        # Create controls frame
        self.controls_frame = ttk.Frame(main_frame)
        self.controls_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.controls_frame.grid_columnconfigure(0, weight=1)
    
    def load_model_data(self):
        """Load data from the model directory."""
        try:
            # Load training data if available
            training_data_file = os.path.join(self.model_path, "training_data.csv")
            if os.path.exists(training_data_file):
                import pandas as pd
                self.training_data = pd.read_csv(training_data_file)
                self.logger.info(f"Loaded training data: {self.training_data.shape}")
            else:
                self.training_data = None
                self.logger.warning("No training data found")
            
            # Load weights history if available
            weights_dir = os.path.join(self.model_path, "weights_history")
            if os.path.exists(weights_dir):
                self.weights_files = sorted([f for f in os.listdir(weights_dir) 
                                           if f.endswith('.npz')])
                self.logger.info(f"Found {len(self.weights_files)} weight files")
            else:
                self.weights_files = []
                self.logger.warning("No weights history found")
            
            # Load feature info
            feature_info_file = os.path.join(self.model_path, "feature_info.json")
            if os.path.exists(feature_info_file):
                import json
                with open(feature_info_file, 'r') as f:
                    self.feature_info = json.load(f)
                self.logger.info("Loaded feature info")
            else:
                self.feature_info = {}
                self.logger.warning("No feature info found")
                
        except Exception as e:
            self.logger.error(f"Error loading model data: {e}")
            self.training_data = None
            self.weights_files = []
            self.feature_info = {}
    
    def create_plot(self):
        """Create the 3D plot."""
        try:
            # Create matplotlib figure
            self.fig = Figure(figsize=(10, 8), dpi=100)
            self.ax = self.fig.add_subplot(111, projection='3d')
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            
            # Create toolbar frame first
            toolbar_frame = tk.Frame(self.plot_frame)
            toolbar_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
            
            # Create navigation toolbar in the dedicated frame
            try:
                self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
                # The toolbar will automatically pack itself in the toolbar_frame
                # which is fine since toolbar_frame uses grid in the parent
            except Exception as toolbar_error:
                self.logger.warning(f"Toolbar creation failed, using fallback: {toolbar_error}")
                # Create a simple fallback toolbar
                fallback_frame = tk.Frame(toolbar_frame)
                fallback_frame.pack(fill="x")
                
                tk.Button(fallback_frame, text="Reset View", 
                         command=lambda: self.ax.view_init(elev=20, azim=45)).pack(side="left", padx=2)
                tk.Button(fallback_frame, text="Home", 
                         command=lambda: self.canvas.draw()).pack(side="left", padx=2)
                self.toolbar = fallback_frame
            
            # Generate plot data
            self.generate_plot_data()
            
            # Draw the plot
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error creating plot: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.show_error_plot(str(e))
    
    def generate_plot_data(self):
        """Generate data for the plot based on plot type."""
        try:
            plot_type = self.plot_params['plot_type']
            
            if plot_type == "3D Scatter":
                self.create_3d_scatter_plot()
            elif plot_type == "3D Surface":
                self.create_3d_surface_plot()
            elif plot_type == "3D Wireframe":
                self.create_3d_wireframe_plot()
            elif plot_type == "3D Gradient Descent":
                self.create_3d_gradient_descent_plot()
            elif plot_type == "2D Scatter":
                self.create_2d_scatter_plot()
            elif plot_type == "1D Line":
                self.create_1d_line_plot()
            else:
                self.create_sample_3d_plot()
                
        except Exception as e:
            self.logger.error(f"Error generating plot data: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.create_sample_3d_plot()
    
    def create_3d_scatter_plot(self):
        """Create a 3D scatter plot."""
        self.ax.clear()
        
        if self.training_data is not None and len(self.training_data.columns) >= 3:
            # Use actual training data
            x = self.training_data.iloc[:, 0].values
            y = self.training_data.iloc[:, 1].values
            z = self.training_data.iloc[:, 2].values
        else:
            # Generate sample data
            n_points = 100
            x = np.random.randn(n_points)
            y = np.random.randn(n_points)
            z = np.random.randn(n_points)
        
        # Get plot parameters with defaults
        point_size = self.plot_params.get('point_size', 50)
        color_scheme = self.plot_params.get('color_scheme', 'viridis')
        
        # Create scatter plot
        scatter = self.ax.scatter(x, y, z, 
                                c=z,  # Color by z-value
                                cmap=color_scheme,
                                s=point_size,
                                alpha=0.7)
        
        # Add colorbar
        self.fig.colorbar(scatter, ax=self.ax, shrink=0.5, aspect=5)
        
        # Set labels
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')
        self.ax.set_title('3D Scatter Plot')
        
        # Set view
        self.ax.view_init(elev=20, azim=45)
    
    def create_3d_surface_plot(self):
        """Create a 3D surface plot."""
        self.ax.clear()
        
        # Generate surface data
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        
        # Create surface plot
        surface = self.ax.plot_surface(X, Y, Z, 
                                     cmap=self.plot_params['color_scheme'],
                                     alpha=0.8)
        
        # Add colorbar
        self.fig.colorbar(surface, ax=self.ax, shrink=0.5, aspect=5)
        
        # Set labels
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')
        self.ax.set_title('3D Surface Plot')
        
        # Set view
        self.ax.view_init(elev=20, azim=45)
    
    def create_3d_wireframe_plot(self):
        """Create a 3D wireframe plot."""
        self.ax.clear()
        
        # Generate wireframe data
        x = np.linspace(-5, 5, 20)
        y = np.linspace(-5, 5, 20)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        
        # Create wireframe plot
        self.ax.plot_wireframe(X, Y, Z, 
                              color='blue',
                              alpha=0.7,
                              linewidth=0.5)
        
        # Set labels
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')
        self.ax.set_title('3D Wireframe Plot')
        
        # Set view
        self.ax.view_init(elev=20, azim=45)
    
    def create_3d_gradient_descent_plot(self):
        """Create a 3D gradient descent plot using the existing gradient descent visualization."""
        try:
            # Import the gradient descent visualization
            import sys
            import os
            
            # Add the visualization directory to the path
            viz_dir = os.path.join(os.path.dirname(__file__), '../../../visualization')
            if viz_dir not in sys.path:
                sys.path.insert(0, viz_dir)
            
            from gradient_descent_3d import GradientDescentVisualizer
            
            # Get gradient descent parameters
            w1_range = self.plot_params.get('w1_range', [-2.0, 2.0])
            w2_range = self.plot_params.get('w2_range', [-2.0, 2.0])
            w1_index = self.plot_params.get('w1_index', 0)
            w2_index = self.plot_params.get('w2_index', 0)
            n_points = self.plot_params.get('n_points', 30)
            line_width = self.plot_params.get('line_width', 3)
            surface_alpha = self.plot_params.get('surface_alpha', 0.6)
            
            # Create the gradient descent visualizer
            gd_viz = GradientDescentVisualizer(
                model_dir=self.model_path,
                w1_range=tuple(w1_range),
                w2_range=tuple(w2_range),
                n_points=n_points,
                view_elev=30,
                view_azim=45,
                fps=30,
                color=self.plot_params['color_scheme'],
                point_size=self.plot_params['point_size'],
                line_width=line_width,
                surface_alpha=surface_alpha,
                w1_index=w1_index,
                w2_index=w2_index
            )
            
            # Clear the current plot and use the gradient descent figure
            self.ax.clear()
            
            # Copy the gradient descent plot to our window
            gd_fig = gd_viz.fig
            gd_ax = gd_viz.ax
            
            # Get the current state of the gradient descent plot
            self.ax.set_xlim(gd_ax.get_xlim())
            self.ax.set_ylim(gd_ax.get_ylim())
            self.ax.set_zlim(gd_ax.get_zlim())
            
            # Recreate the surface plot
            if hasattr(gd_viz, 'W1') and hasattr(gd_viz, 'W2') and hasattr(gd_viz, 'Z'):
                surface = self.ax.plot_surface(gd_viz.W1, gd_viz.W2, gd_viz.Z,
                                             cmap=self.plot_params['color_scheme'],
                                             alpha=surface_alpha)
                self.fig.colorbar(surface, ax=self.ax, shrink=0.5, aspect=5)
            
            # Add the gradient descent path
            if hasattr(gd_viz, 'history') and gd_viz.history['weights']:
                # Extract weight history for visualization
                weights = gd_viz.history['weights']
                losses = gd_viz.history['losses']
                
                # Create path data
                path_x, path_y, path_z = [], [], []
                
                for i, weight in enumerate(weights):
                    try:
                        w1_val = gd_viz.extract_weight_by_index(weight, w1_index, 'W1')
                        w2_val = gd_viz.extract_weight_by_index(weight, w2_index, 'W2')
                        
                        # Clamp values to visualization bounds
                        w1_val = np.clip(w1_val, w1_range[0], w1_range[1])
                        w2_val = np.clip(w2_val, w2_range[0], w2_range[1])
                        
                        path_x.append(w1_val)
                        path_y.append(w2_val)
                        path_z.append(losses[i] if i < len(losses) else 0)
                    except Exception as e:
                        self.logger.warning(f"Error extracting weight at step {i}: {e}")
                        continue
                
                if path_x and path_y and path_z:
                    # Plot the gradient descent path
                    self.ax.plot(path_x, path_y, path_z, 'r-', linewidth=line_width, 
                               label='Gradient Descent Path', alpha=0.8)
                    
                    # Plot start and end points
                    if len(path_x) > 0:
                        self.ax.scatter([path_x[0]], [path_y[0]], [path_z[0]], 
                                      c='green', s=100, marker='o', label='Start')
                        self.ax.scatter([path_x[-1]], [path_y[-1]], [path_z[-1]], 
                                      c='red', s=100, marker='o', label='End')
            
            # Set labels and title
            self.ax.set_xlabel(f'W1 (Index {w1_index})')
            self.ax.set_ylabel(f'W2 (Index {w2_index})')
            self.ax.set_zlabel('Loss')
            self.ax.set_title(f'3D Gradient Descent\n{os.path.basename(self.model_path)}')
            self.ax.legend()
            
            # Set view
            self.ax.view_init(elev=30, azim=45)
            
        except Exception as e:
            self.logger.error(f"Error creating 3D gradient descent plot: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback to sample plot
            self.create_sample_3d_plot()
    
    def create_2d_scatter_plot(self):
        """Create a 2D scatter plot."""
        self.ax.clear()
        
        if self.training_data is not None and len(self.training_data.columns) >= 2:
            # Use actual training data
            x = self.training_data.iloc[:, 0].values
            y = self.training_data.iloc[:, 1].values
        else:
            # Generate sample data
            n_points = 100
            x = np.random.randn(n_points)
            y = np.random.randn(n_points)
        
        # Create 2D scatter plot
        scatter = self.ax.scatter(x, y, 
                                c=y,  # Color by y-value
                                cmap=self.plot_params['color_scheme'],
                                s=self.plot_params['point_size'],
                                alpha=0.7)
        
        # Add colorbar
        self.fig.colorbar(scatter, ax=self.ax, shrink=0.5, aspect=5)
        
        # Set labels
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_title('2D Scatter Plot')
        
        # Remove z-axis for 2D plot
        self.ax.set_zticks([])
    
    def create_1d_line_plot(self):
        """Create a 1D line plot."""
        self.ax.clear()
        
        # Generate line data
        x = np.linspace(0, 10, 100)
        y = np.sin(x) * np.exp(-x/5)
        
        # Create line plot
        self.ax.plot(x, y, 
                    color='blue',
                    linewidth=2,
                    alpha=0.8)
        
        # Set labels
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_title('1D Line Plot')
        
        # Remove z-axis for 1D plot
        self.ax.set_zticks([])
    
    def create_sample_3d_plot(self):
        """Create a sample 3D plot when data is not available."""
        self.ax.clear()
        
        # Generate sample data
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-(X**2 + Y**2) / 10)
        
        # Create surface plot
        surface = self.ax.plot_surface(X, Y, Z, 
                                     cmap=self.plot_params['color_scheme'],
                                     alpha=0.8)
        
        # Add colorbar
        self.fig.colorbar(surface, ax=self.ax, shrink=0.5, aspect=5)
        
        # Set labels
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')
        self.ax.set_title('Sample 3D Plot')
        
        # Set view
        self.ax.view_init(elev=20, azim=45)
    
    def show_error_plot(self, error_message):
        """Show an error message in the plot area."""
        try:
            self.ax.clear()
            self.ax.text2D(0.5, 0.5, f'Error creating plot:\n{error_message}', 
                          ha='center', va='center', transform=self.ax.transAxes,
                          fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
            self.ax.set_title("Plot Error")
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_zticks([])
        except Exception as e:
            # Fallback: create a simple error plot
            self.logger.error(f"Error in show_error_plot: {e}")
            try:
                self.ax.clear()
                # Create a simple surface plot with error message in title
                x = np.linspace(-1, 1, 10)
                y = np.linspace(-1, 1, 10)
                X, Y = np.meshgrid(x, y)
                Z = np.zeros_like(X)
                self.ax.plot_surface(X, Y, Z, color='red', alpha=0.5)
                self.ax.set_title(f"Plot Error: {error_message[:50]}...")
                self.ax.set_xticks([])
                self.ax.set_yticks([])
                self.ax.set_zticks([])
            except Exception as fallback_error:
                self.logger.error(f"Fallback error plot also failed: {fallback_error}")
                # Last resort: just clear the plot
                self.ax.clear()
                self.ax.set_title("Plot Error")
    
    def setup_controls(self):
        """Setup the control panel."""
        # View controls
        view_frame = ttk.LabelFrame(self.controls_frame, text="View Controls", padding="5")
        view_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Button(view_frame, text="Reset View", command=self.reset_view).pack(side="left", padx=(0, 5))
        ttk.Button(view_frame, text="Top View", command=self.top_view).pack(side="left", padx=(0, 5))
        ttk.Button(view_frame, text="Side View", command=self.side_view).pack(side="left", padx=(0, 5))
        ttk.Button(view_frame, text="Isometric", command=self.isometric_view).pack(side="left")
        
        # Animation controls (only show if animation is enabled)
        animation_enabled = self.plot_params.get('animation_enabled', False)
        if animation_enabled:
            anim_frame = ttk.LabelFrame(self.controls_frame, text="Animation", padding="5")
            anim_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
            
            ttk.Button(anim_frame, text="Start Animation", command=self.start_animation).pack(side="left", padx=(0, 5))
            ttk.Button(anim_frame, text="Stop Animation", command=self.stop_animation).pack(side="left")
        
        # Save controls
        save_frame = ttk.LabelFrame(self.controls_frame, text="Save", padding="5")
        save_frame.pack(side="right")
        
        ttk.Button(save_frame, text="Save Plot", command=self.save_plot).pack(side="left", padx=(0, 5))
        ttk.Button(save_frame, text="Save Animation (MP4)", command=self.save_animation_mp4).pack(side="left", padx=(0, 5))
        ttk.Button(save_frame, text="Save Animation (GIF)", command=self.save_animation_gif).pack(side="left", padx=(0, 5))
        ttk.Button(save_frame, text="Close", command=self.close).pack(side="left")
    
    def reset_view(self):
        """Reset the 3D view."""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()
    
    def top_view(self):
        """Set top view."""
        self.ax.view_init(elev=90, azim=0)
        self.canvas.draw()
    
    def side_view(self):
        """Set side view."""
        self.ax.view_init(elev=0, azim=0)
        self.canvas.draw()
    
    def isometric_view(self):
        """Set isometric view."""
        self.ax.view_init(elev=35, azim=45)
        self.canvas.draw()
    
    def start_animation(self):
        """Start the animation."""
        if not self.is_animating:
            self.is_animating = True
            self.animation = animation.FuncAnimation(
                self.fig, self.animate_frame,
                frames=360,  # Full rotation
                interval=50,  # 20 FPS
                repeat=True
            )
    
    def stop_animation(self):
        """Stop the animation."""
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
        self.is_animating = False
    
    def animate_frame(self, frame):
        """Animate frame for rotation."""
        self.ax.view_init(elev=20, azim=frame)
        return self.ax,
    
    def save_plot(self):
        """Save the current plot."""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_type = self.plot_params['plot_type'].replace(" ", "_").lower()
            filename = f"3d_plot_{plot_type}_{timestamp}.png"
            
            # Save to model directory
            plots_dir = os.path.join(self.model_path, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            filepath = os.path.join(plots_dir, filename)
            
            # Save the figure
            self.fig.savefig(filepath, dpi=300, bbox_inches='tight')
            
            messagebox.showinfo("Success", f"Plot saved to:\n{filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving plot: {e}")
            messagebox.showerror("Error", f"Failed to save plot: {e}")
    
    def save_animation_mp4(self):
        """Save a 360-frame rotation animation as MP4 (MPEG4) using ffmpeg writer."""
        try:
            from tkinter import filedialog
            import matplotlib.animation as animation
            
            # Ask user for save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_type = self.plot_params['plot_type'].replace(" ", "_").lower()
            default_filename = f"3d_plot_{plot_type}_{timestamp}.mp4"
            plots_dir = os.path.join(self.model_path, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            default_path = os.path.join(plots_dir, default_filename)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                initialfile=default_filename,
                initialdir=plots_dir,
                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
            )
            if not file_path:
                return
            # Create animation
            anim = animation.FuncAnimation(
                self.fig, self.animate_frame,
                frames=360,  # Full rotation
                interval=50,  # 20 FPS
                repeat=False
            )
            # Try to use ffmpeg writer
            try:
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=20, metadata=dict(artist='3D Plot Animation'), bitrate=1800)
                anim.save(file_path, writer=writer, dpi=100)
                messagebox.showinfo("Success", f"Animation saved to:\n{file_path}")
            except Exception as ffmpeg_error:
                self.logger.error(f"Error saving MP4 animation: {ffmpeg_error}")
                messagebox.showerror("Error", f"Failed to save MP4 animation.\nError: {ffmpeg_error}\n\nMake sure ffmpeg is installed and available in your PATH.")
        except Exception as e:
            self.logger.error(f"Error in save_animation_mp4: {e}")
            messagebox.showerror("Error", f"Failed to save animation: {e}")
    
    def save_animation_gif(self):
        """Save a 360-frame rotation animation as GIF using matplotlib's pillow writer."""
        try:
            from tkinter import filedialog
            import matplotlib.animation as animation
            
            # Ask user for save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_type = self.plot_params['plot_type'].replace(" ", "_").lower()
            default_filename = f"3d_plot_{plot_type}_{timestamp}.gif"
            plots_dir = os.path.join(self.model_path, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            default_path = os.path.join(plots_dir, default_filename)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                initialfile=default_filename,
                initialdir=plots_dir,
                filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
            )
            if not file_path:
                return
            # Create animation
            anim = animation.FuncAnimation(
                self.fig, self.animate_frame,
                frames=360,  # Full rotation
                interval=50,  # 20 FPS
                repeat=False
            )
            # Try to use pillow writer
            try:
                anim.save(file_path, writer='pillow', fps=20)
                messagebox.showinfo("Success", f"Animation saved to:\n{file_path}")
            except Exception as pillow_error:
                self.logger.error(f"Error saving GIF animation: {pillow_error}")
                messagebox.showerror("Error", f"Failed to save GIF animation.\nError: {pillow_error}\n\nMake sure Pillow is installed and available in your PATH.")
        except Exception as e:
            self.logger.error(f"Error in save_animation_gif: {e}")
            messagebox.showerror("Error", f"Failed to save animation: {e}")
    
    def close(self):
        """Close the floating window."""
        try:
            # Stop animation if running
            if self.animation:
                self.stop_animation()
            
            # Call close callback
            if self.on_close:
                self.on_close()
            
            # Destroy window
            self.window.destroy()
            
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
            self.window.destroy() 