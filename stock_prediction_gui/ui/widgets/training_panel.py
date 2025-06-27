"""
Training panel for the Stock Prediction GUI with live loss plotting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import threading
import time

class TrainingPanel:
    """Training panel with live loss plotting."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Training state
        self.is_training = False
        self.training_thread = None
        
        # Plot data
        self.epochs = []
        self.train_losses = []
        self.val_losses = []
        
        # Create the panel
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
    
    def create_widgets(self):
        """Create the panel widgets with left controls and right plot."""
        # Main container with left and right panels
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)
        
        # Left panel for controls
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        # Right panel for live plot
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Create left panel content
        self.create_left_panel(left_panel)
        
        # Create right panel content
        self.create_right_panel(right_panel)
    
    def create_left_panel(self, parent):
        """Create the left control panel."""
        # Title
        title_label = ttk.Label(parent, text="Model Training", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Training parameters section
        self.create_parameters_section(parent)
        
        # Training progress section
        self.create_progress_section(parent)
        
        # Training controls section
        self.create_controls_section(parent)
    
    def create_parameters_section(self, parent):
        """Create the training parameters section."""
        # Parameters frame
        params_frame = ttk.LabelFrame(parent, text="Training Parameters", padding="10")
        params_frame.pack(fill="x", pady=(0, 10))
        
        # Create parameter inputs
        self.create_parameter_inputs(params_frame)
    
    def create_parameter_inputs(self, parent):
        """Create parameter input fields."""
        # Epochs
        epochs_frame = ttk.Frame(parent)
        epochs_frame.pack(fill="x", pady=2)
        ttk.Label(epochs_frame, text="Epochs:", width=15).pack(side="left")
        self.epochs_var = tk.StringVar(value="100")
        ttk.Entry(epochs_frame, textvariable=self.epochs_var, width=10).pack(side="right")
        
        # Learning rate
        lr_frame = ttk.Frame(parent)
        lr_frame.pack(fill="x", pady=2)
        ttk.Label(lr_frame, text="Learning Rate:", width=15).pack(side="left")
        self.learning_rate_var = tk.StringVar(value="0.001")
        ttk.Entry(lr_frame, textvariable=self.learning_rate_var, width=10).pack(side="right")
        
        # Batch size
        batch_frame = ttk.Frame(parent)
        batch_frame.pack(fill="x", pady=2)
        ttk.Label(batch_frame, text="Batch Size:", width=15).pack(side="left")
        self.batch_size_var = tk.StringVar(value="32")
        ttk.Entry(batch_frame, textvariable=self.batch_size_var, width=10).pack(side="right")
        
        # Hidden size
        hidden_frame = ttk.Frame(parent)
        hidden_frame.pack(fill="x", pady=2)
        ttk.Label(hidden_frame, text="Hidden Size:", width=15).pack(side="left")
        self.hidden_size_var = tk.StringVar(value="64")
        ttk.Entry(hidden_frame, textvariable=self.hidden_size_var, width=10).pack(side="right")
        
        # Validation split
        val_frame = ttk.Frame(parent)
        val_frame.pack(fill="x", pady=2)
        ttk.Label(val_frame, text="Validation Split:", width=15).pack(side="left")
        self.validation_split_var = tk.StringVar(value="0.2")
        ttk.Entry(val_frame, textvariable=self.validation_split_var, width=10).pack(side="right")
        
        # Early stopping patience
        patience_frame = ttk.Frame(parent)
        patience_frame.pack(fill="x", pady=2)
        ttk.Label(patience_frame, text="Early Stopping:", width=15).pack(side="left")
        self.early_stopping_var = tk.StringVar(value="10")
        ttk.Entry(patience_frame, textvariable=self.early_stopping_var, width=10).pack(side="right")
        
        # Random seed
        seed_frame = ttk.Frame(parent)
        seed_frame.pack(fill="x", pady=2)
        ttk.Label(seed_frame, text="Random Seed:", width=15).pack(side="left")
        self.random_seed_var = tk.StringVar(value="42")
        ttk.Entry(seed_frame, textvariable=self.random_seed_var, width=10).pack(side="right")
        
        # Checkboxes
        checkbox_frame = ttk.Frame(parent)
        checkbox_frame.pack(fill="x", pady=(10, 0))
        
        self.save_history_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(checkbox_frame, text="Save Training History", variable=self.save_history_var).pack(anchor="w")
        
        self.memory_optimization_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(checkbox_frame, text="Memory Optimization", variable=self.memory_optimization_var).pack(anchor="w")
    
    def create_progress_section(self, parent):
        """Create the training progress section."""
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Training Progress", padding="10")
        progress_frame.pack(fill="x", pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Progress labels
        self.epoch_var = tk.StringVar(value="Epoch: 0")
        ttk.Label(progress_frame, textvariable=self.epoch_var).pack(anchor="w")
        
        self.loss_var = tk.StringVar(value="Loss: N/A")
        ttk.Label(progress_frame, textvariable=self.loss_var).pack(anchor="w")
        
        self.val_loss_var = tk.StringVar(value="Validation Loss: N/A")
        ttk.Label(progress_frame, textvariable=self.val_loss_var).pack(anchor="w")
    
    def create_controls_section(self, parent):
        """Create the training controls section."""
        # Controls frame
        controls_frame = ttk.LabelFrame(parent, text="Training Controls", padding="10")
        controls_frame.pack(fill="x")
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        self.start_button = ttk.Button(button_frame, text="Start Training", command=self.start_training)
        self.start_button.pack(side="left", padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Training", command=self.stop_training, state="disabled")
        self.stop_button.pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="Reset Progress", command=self.reset_progress).pack(side="right")
    
    def create_right_panel(self, parent):
        """Create the right panel with live matplotlib plot."""
        # Plot frame
        plot_frame = ttk.LabelFrame(parent, text="Live Training Loss", padding="10")
        plot_frame.pack(fill="both", expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Initialize plot
        self.ax.set_xlabel('Epoch')
        self.ax.set_ylabel('Loss')
        self.ax.set_title('Training Progress')
        self.ax.grid(True, alpha=0.3)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.pack(fill="x")
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Plot controls
        plot_controls_frame = ttk.Frame(plot_frame)
        plot_controls_frame.pack(fill="x", pady=(10, 0))
        
        # Auto-scale checkbox
        self.auto_scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(plot_controls_frame, text="Auto-scale", variable=self.auto_scale_var).pack(side="left")
        
        # Clear plot button
        ttk.Button(plot_controls_frame, text="Clear Plot", command=self.clear_plot).pack(side="right")
        
        # Save plot button
        ttk.Button(plot_controls_frame, text="Save Plot", command=self.save_plot).pack(side="right", padx=(0, 5))
    
    def start_training(self):
        """Start training process."""
        # Add debugging
        print(f"Debug - selected_features: {self.app.selected_features}")
        print(f"Debug - selected_target: {self.app.selected_target}")
        print(f"Debug - are_features_locked: {self.app.are_features_locked()}")
        
        if not self.app.current_data_file:
            messagebox.showwarning("No Data", "Please load a data file first.")
            return
        
        if not self.app.current_output_dir:
            messagebox.showwarning("No Output Directory", "Please select an output directory first.")
            return
        
        # Check if columns are locked using the new method
        if not self.app.are_features_locked():
            messagebox.showwarning("Columns Not Locked", 
                                 f"Please select and lock column selection in the Data tab first.\n"
                                 f"Selected features: {self.app.selected_features}\n"
                                 f"Selected target: {self.app.selected_target}")
            return
        
        # Reset plot data
        self.reset_plot_data()
        
        # Get training parameters
        params = self.get_training_params()
        
        # Start training
        if self.app.start_training(params):
            self.is_training = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # Start live plotting thread
            self.start_live_plotting()
    
    def stop_training(self):
        """Stop training process."""
        self.app.stop_training()
        self.is_training = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def reset_progress(self):
        """Reset training progress."""
        self.progress_var.set(0)
        self.epoch_var.set("Epoch: 0")
        self.loss_var.set("Loss: N/A")
        self.val_loss_var.set("Validation Loss: N/A")
        self.reset_plot_data()
    
    def reset_plot_data(self):
        """Reset plot data."""
        self.epochs = []
        self.train_losses = []
        self.val_losses = []
        self.update_plot()
    
    def clear_plot(self):
        """Clear the plot."""
        self.ax.clear()
        self.ax.set_xlabel('Epoch')
        self.ax.set_ylabel('Loss')
        self.ax.set_title('Training Progress')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def save_plot(self):
        """Save the current plot."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filename:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot: {e}")
    
    def start_live_plotting(self):
        """Start the live plotting thread."""
        self.plotting_thread = threading.Thread(target=self.live_plotting_loop, daemon=True)
        self.plotting_thread.start()
    
    def live_plotting_loop(self):
        """Live plotting loop that updates the plot during training."""
        while self.is_training:
            try:
                # Update plot every 0.5 seconds
                time.sleep(0.5)
                
                # Check if we have new data to plot
                if hasattr(self.app, 'training_manager') and self.app.training_manager:
                    # Get current training state
                    current_epoch = getattr(self.app.training_manager, 'current_epoch', 0)
                    current_loss = getattr(self.app.training_manager, 'current_loss', None)
                    current_val_loss = getattr(self.app.training_manager, 'current_val_loss', None)
                    
                    # Update plot if we have new data
                    if current_loss is not None and current_epoch > 0:
                        self.add_data_point(current_epoch, current_loss, current_val_loss)
                
            except Exception as e:
                self.logger.error(f"Error in live plotting: {e}")
                break
    
    def add_data_point(self, epoch, loss, val_loss=None):
        """Add a data point to the plot."""
        if epoch not in self.epochs:
            self.epochs.append(epoch)
            self.train_losses.append(loss)
            if val_loss is not None:
                self.val_losses.append(val_loss)
            else:
                self.val_losses.append(None)
            
            # Update plot in main thread
            self.parent.after(0, self.update_plot)
    
    def update_plot(self):
        """Update the matplotlib plot."""
        try:
            self.ax.clear()
            
            if self.epochs:
                # Plot training loss
                self.ax.plot(self.epochs, self.train_losses, 'b-', label='Training Loss', linewidth=2)
                
                # Plot validation loss if available
                val_losses_clean = [loss for loss in self.val_losses if loss is not None]
                if val_losses_clean and len(val_losses_clean) == len(self.epochs):
                    self.ax.plot(self.epochs, val_losses_clean, 'r-', label='Validation Loss', linewidth=2)
                
                # Set labels and title
                self.ax.set_xlabel('Epoch')
                self.ax.set_ylabel('Loss')
                self.ax.set_title('Live Training Progress')
                self.ax.grid(True, alpha=0.3)
                self.ax.legend()
                
                # Auto-scale if enabled
                if self.auto_scale_var.get():
                    self.ax.relim()
                    self.ax.autoscale_view()
                
                # Update canvas
                self.canvas.draw()
                
        except Exception as e:
            self.logger.error(f"Error updating plot: {e}")
    
    def get_training_params(self):
        """Get training parameters from the UI."""
        return {
            'epochs': int(self.epochs_var.get()),
            'learning_rate': float(self.learning_rate_var.get()),
            'batch_size': int(self.batch_size_var.get()),
            'hidden_size': int(self.hidden_size_var.get()),
            'validation_split': float(self.validation_split_var.get()),
            'early_stopping_patience': int(self.early_stopping_var.get()),
            'random_seed': int(self.random_seed_var.get()),
            'save_history': self.save_history_var.get(),
            'memory_optimization': self.memory_optimization_var.get(),
            'data_file': self.app.current_data_file,
            'output_dir': self.app.current_output_dir,
            'x_features': self.app.selected_features,
            'y_feature': self.app.selected_target
        }
    
    def update_progress(self, epoch, loss, val_loss, progress):
        """Update training progress display."""
        self.epoch_var.set(f"Epoch: {epoch}")
        self.loss_var.set(f"Loss: {loss:.6f}")
        self.val_loss_var.set(f"Validation Loss: {val_loss:.6f}")
        self.progress_var.set(progress)
        
        # Add data point to plot
        self.add_data_point(epoch, loss, val_loss)
        
        # Re-enable start button when training completes
        if progress >= 100:
            self.is_training = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled") 