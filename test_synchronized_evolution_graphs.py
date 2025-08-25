#!/usr/bin/env python3
"""
Test for Synchronized Evolution Graphs in Neural Network Forward Passes

This test demonstrates how weight adjustments influence bias impacts during prediction,
showing correlations between parameter evolution and network behavior.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import threading
import time
import logging

class SynchronizedEvolutionGraphs:
    """Demonstrates synchronized evolution graphs for neural network analysis."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Neural Network Synchronized Evolution Graphs")
        self.root.geometry("1400x900")
        
        self.logger = logging.getLogger(__name__)
        
        # Neural network state
        self.network_state = {
            'weights': [],
            'biases': [],
            'activations': [],
            'gradients': [],
            'loss_history': []
        }
        
        # Animation state
        self.is_animating = False
        self.animation_thread = None
        
        # Create the interface
        self.create_interface()
        
        # Initialize a simple neural network
        self.initialize_network()
        
    def create_interface(self):
        """Create the main interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Neural Network Synchronized Evolution Analysis", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Graph panel
        self.create_graph_panel(main_frame)
        
        # Status panel
        self.create_status_panel(main_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel."""
        control_frame = ttk.LabelFrame(parent, text="Network Controls", padding="10")
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Network parameters
        param_frame = ttk.Frame(control_frame)
        param_frame.pack(fill="x", pady=(0, 10))
        
        # Layer sizes
        ttk.Label(param_frame, text="Layer Sizes:").pack(side="left")
        self.layer_sizes_var = tk.StringVar(value="2,3,1")
        ttk.Entry(param_frame, textvariable=self.layer_sizes_var, width=15).pack(side="left", padx=(5, 10))
        
        # Learning rate
        ttk.Label(param_frame, text="Learning Rate:").pack(side="left")
        self.lr_var = tk.StringVar(value="0.01")
        ttk.Entry(param_frame, textvariable=self.lr_var, width=10).pack(side="left", padx=(5, 10))
        
        # Epochs
        ttk.Label(param_frame, text="Epochs:").pack(side="left")
        self.epochs_var = tk.StringVar(value="100")
        ttk.Entry(param_frame, textvariable=self.epochs_var, width=10).pack(side="left", padx=(5, 10))
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Initialize Network", 
                  command=self.initialize_network).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Start Training", 
                  command=self.start_training).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Stop Training", 
                  command=self.stop_training).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Single Forward Pass", 
                  command=self.single_forward_pass).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_network).pack(side="right")
    
    def create_graph_panel(self, parent):
        """Create the synchronized graphs panel."""
        graph_frame = ttk.LabelFrame(parent, text="Synchronized Evolution Graphs", padding="10")
        graph_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create matplotlib figure with subplots
        self.fig = Figure(figsize=(14, 8), dpi=100)
        
        # Create synchronized subplots
        self.ax1 = self.fig.add_subplot(2, 3, 1)  # Weights evolution
        self.ax2 = self.fig.add_subplot(2, 3, 2)  # Biases evolution
        self.ax3 = self.fig.add_subplot(2, 3, 3)  # Activations evolution
        self.ax4 = self.fig.add_subplot(2, 3, 4)  # Gradients evolution
        self.ax5 = self.fig.add_subplot(2, 3, 5)  # Loss evolution
        self.ax6 = self.fig.add_subplot(2, 3, 6)  # Correlation matrix
        
        # Set titles
        self.ax1.set_title("Weights Evolution")
        self.ax2.set_title("Biases Evolution")
        self.ax3.set_title("Activations Evolution")
        self.ax4.set_title("Gradients Evolution")
        self.ax5.set_title("Loss Evolution")
        self.ax6.set_title("Parameter Correlations")
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        toolbar.update()
    
    def create_status_panel(self, parent):
        """Create the status panel."""
        status_frame = ttk.LabelFrame(parent, text="Status & Information", padding="10")
        status_frame.pack(fill="x")
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to initialize network")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                font=("Arial", 10), foreground="blue")
        status_label.pack(side="left")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(10, 0))
    
    def initialize_network(self):
        """Initialize the neural network."""
        try:
            # Parse layer sizes
            layer_sizes = [int(x.strip()) for x in self.layer_sizes_var.get().split(',')]
            
            # Initialize weights and biases
            self.network_state['weights'] = []
            self.network_state['biases'] = []
            
            for i in range(len(layer_sizes) - 1):
                # Xavier initialization
                w = np.random.randn(layer_sizes[i + 1], layer_sizes[i]) * np.sqrt(2.0 / (layer_sizes[i] + layer_sizes[i + 1]))
                b = np.zeros((layer_sizes[i + 1], 1))
                
                self.network_state['weights'].append(w)
                self.network_state['biases'].append(b)
            
            # Initialize history arrays
            self.network_state['activations'] = []
            self.network_state['gradients'] = []
            self.network_state['loss_history'] = []
            
            # Create sample data
            self.X = np.random.randn(100, layer_sizes[0])
            self.y = np.random.randn(100, layer_sizes[-1])
            
            self.status_var.set(f"Network initialized with layers: {layer_sizes}")
            self.progress_var.set(0)
            
            # Update graphs
            self.update_graphs()
            
        except Exception as e:
            self.logger.error(f"Error initializing network: {e}")
            messagebox.showerror("Error", f"Failed to initialize network: {e}")
    
    def forward_pass(self, X):
        """Perform a forward pass through the network."""
        activations = [X]
        
        for i, (w, b) in enumerate(zip(self.network_state['weights'], self.network_state['biases'])):
            z = np.dot(w, activations[-1].T) + b
            a = self.relu(z)
            activations.append(a.T)
        
        return activations
    
    def relu(self, x):
        """ReLU activation function."""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """Derivative of ReLU activation function."""
        return np.where(x > 0, 1, 0)
    
    def backward_pass(self, X, y, activations):
        """Perform a backward pass to compute gradients."""
        m = X.shape[0]
        gradients_w = []
        gradients_b = []
        
        # Compute output layer gradient
        delta = activations[-1] - y
        
        for i in range(len(self.network_state['weights']) - 1, -1, -1):
            # Weight gradients
            dw = np.dot(delta.T, activations[i]) / m
            gradients_w.insert(0, dw)
            
            # Bias gradients
            db = np.sum(delta, axis=0, keepdims=True).T / m
            gradients_b.insert(0, db)
            
            # Propagate error to previous layer
            if i > 0:
                delta = np.dot(delta, self.network_state['weights'][i]) * self.relu_derivative(activations[i])
        
        return gradients_w, gradients_b
    
    def update_parameters(self, gradients_w, gradients_b, learning_rate):
        """Update network parameters."""
        for i in range(len(self.network_state['weights'])):
            self.network_state['weights'][i] -= learning_rate * gradients_w[i]
            self.network_state['biases'][i] -= learning_rate * gradients_b[i]
    
    def compute_loss(self, y_pred, y_true):
        """Compute mean squared error loss."""
        return np.mean((y_pred - y_true) ** 2)
    
    def single_forward_pass(self):
        """Perform a single forward pass and update graphs."""
        try:
            if not self.network_state['weights']:
                messagebox.showwarning("Warning", "Please initialize the network first.")
                return
            
            # Perform forward pass
            activations = self.forward_pass(self.X)
            
            # Compute loss
            loss = self.compute_loss(activations[-1], self.y)
            
            # Store activations
            self.network_state['activations'].append(activations)
            self.network_state['loss_history'].append(loss)
            
            # Update graphs
            self.update_graphs()
            
            self.status_var.set(f"Single forward pass completed. Loss: {loss:.6f}")
            self.progress_var.set(100)
            
        except Exception as e:
            self.logger.error(f"Error in single forward pass: {e}")
            messagebox.showerror("Error", f"Forward pass failed: {e}")
    
    def start_training(self):
        """Start training the network."""
        if self.is_animating:
            return
        
        try:
            epochs = int(self.epochs_var.get())
            learning_rate = float(self.lr_var.get())
            
            self.is_animating = True
            self.animation_thread = threading.Thread(target=self.training_loop, 
                                                   args=(epochs, learning_rate), 
                                                   daemon=True)
            self.animation_thread.start()
            
            self.status_var.set("Training started...")
            
        except Exception as e:
            self.logger.error(f"Error starting training: {e}")
            messagebox.showerror("Error", f"Failed to start training: {e}")
    
    def training_loop(self, epochs, learning_rate):
        """Training loop with synchronized updates."""
        try:
            for epoch in range(epochs):
                if not self.is_animating:
                    break
                
                # Forward pass
                activations = self.forward_pass(self.X)
                
                # Backward pass
                gradients_w, gradients_b = self.backward_pass(self.X, self.y, activations)
                
                # Update parameters
                self.update_parameters(gradients_w, gradients_b, learning_rate)
                
                # Store state for analysis
                self.network_state['activations'].append(activations)
                self.network_state['gradients'].append((gradients_w, gradients_b))
                
                # Compute and store loss
                loss = self.compute_loss(activations[-1], self.y)
                self.network_state['loss_history'].append(loss)
                
                # Update progress
                progress = (epoch + 1) / epochs * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # Update status
                self.root.after(0, lambda e=epoch, l=loss: 
                              self.status_var.set(f"Epoch {e+1}/{epochs}, Loss: {l:.6f}"))
                
                # Update graphs every few epochs
                if epoch % 5 == 0 or epoch == epochs - 1:
                    self.root.after(0, self.update_graphs)
                
                # Small delay for visualization
                time.sleep(0.1)
            
            self.root.after(0, lambda: self.status_var.set("Training completed!"))
            self.root.after(0, lambda: self.progress_var.set(100))
            
        except Exception as e:
            self.logger.error(f"Error in training loop: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Training failed: {e}"))
        finally:
            self.is_animating = False
    
    def stop_training(self):
        """Stop training."""
        self.is_animating = False
        self.status_var.set("Training stopped.")
    
    def reset_network(self):
        """Reset the network to initial state."""
        self.stop_training()
        self.network_state['activations'] = []
        self.network_state['gradients'] = []
        self.network_state['loss_history'] = []
        self.progress_var.set(0)
        self.status_var.set("Network reset to initial state.")
        self.update_graphs()
    
    def update_graphs(self):
        """Update all synchronized graphs."""
        try:
            # Clear all axes
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                ax.clear()
            
            if not self.network_state['weights']:
                # Show empty state
                for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
                    ax.text(0.5, 0.5, 'Initialize network to see graphs', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                self.canvas.draw()
                return
            
            # 1. Weights Evolution
            if self.network_state['activations']:
                epochs = range(len(self.network_state['activations']))
                for i, w in enumerate(self.network_state['weights']):
                    w_flat = w.flatten()
                    # Ensure we have the same number of data points
                    w_means = [w_flat.mean() for _ in epochs]
                    self.ax1.plot(epochs, w_means, 
                                label=f'Layer {i+1}', linewidth=2)
                self.ax1.set_title("Weights Evolution (Mean Values)")
                self.ax1.set_xlabel("Forward Pass / Epoch")
                self.ax1.set_ylabel("Weight Value")
                self.ax1.legend()
                self.ax1.grid(True, alpha=0.3)
            
            # 2. Biases Evolution
            if self.network_state['activations']:
                for i, b in enumerate(self.network_state['biases']):
                    b_flat = b.flatten()
                    # Ensure we have the same number of data points
                    b_means = [b_flat.mean() for _ in epochs]
                    self.ax2.plot(epochs, b_means, 
                                label=f'Layer {i+1}', linewidth=2)
                self.ax2.set_title("Biases Evolution (Mean Values)")
                self.ax2.set_xlabel("Forward Pass / Epoch")
                self.ax2.set_ylabel("Bias Value")
                self.ax2.legend()
                self.ax2.grid(True, alpha=0.3)
            
            # 3. Activations Evolution
            if self.network_state['activations']:
                for i in range(len(self.network_state['weights'])):
                    act_means = []
                    for acts in self.network_state['activations']:
                        if i + 1 < len(acts):
                            act_means.append(acts[i + 1].mean())
                        else:
                            act_means.append(0)
                    # Ensure we have the same number of data points
                    if len(act_means) == len(epochs):
                        self.ax3.plot(epochs, act_means, label=f'Layer {i+1}', linewidth=2)
                self.ax3.set_title("Activations Evolution (Mean Values)")
                self.ax3.set_xlabel("Forward Pass / Epoch")
                self.ax3.set_ylabel("Activation Value")
                self.ax3.legend()
                self.ax3.grid(True, alpha=0.3)
            
            # 4. Gradients Evolution
            if self.network_state['gradients']:
                for i in range(len(self.network_state['weights'])):
                    grad_means = []
                    for grads in self.network_state['gradients']:
                        if i < len(grads[0]):
                            grad_means.append(np.abs(grads[0][i]).mean())
                        else:
                            grad_means.append(0)
                    # Ensure we have the same number of data points
                    if len(grad_means) == len(epochs):
                        self.ax4.plot(epochs, grad_means, label=f'Layer {i+1}', linewidth=2)
                self.ax4.set_title("Gradients Evolution (Mean Absolute Values)")
                self.ax4.set_xlabel("Forward Pass / Epoch")
                self.ax4.set_ylabel("Gradient Magnitude")
                self.ax4.legend()
                self.ax4.grid(True, alpha=0.3)
            
            # 5. Loss Evolution
            if self.network_state['loss_history']:
                loss_epochs = range(len(self.network_state['loss_history']))
                self.ax5.plot(loss_epochs, self.network_state['loss_history'], 'r-', linewidth=2)
                self.ax5.set_title("Loss Evolution")
                self.ax5.set_xlabel("Forward Pass / Epoch")
                self.ax5.set_ylabel("Loss Value")
                self.ax5.grid(True, alpha=0.3)
                self.ax5.set_yscale('log')
            
            # 6. Parameter Correlations
            if len(self.network_state['loss_history']) > 1:
                self.plot_correlation_matrix()
            
            # Adjust layout and draw
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Error updating graphs: {e}")
    
    def plot_correlation_matrix(self):
        """Plot correlation matrix between parameters and loss."""
        try:
            # Extract parameter values over time
            param_data = []
            param_names = []
            
            # Get the number of epochs from activations (most reliable)
            num_epochs = len(self.network_state['activations'])
            if num_epochs == 0:
                return
            
            # Weights
            for i, w in enumerate(self.network_state['weights']):
                w_flat = w.flatten()
                # Ensure we have the right number of data points
                w_means = [w_flat.mean() for _ in range(num_epochs)]
                param_data.append(w_means)
                param_names.append(f'W{i+1}_mean')
            
            # Biases
            for i, b in enumerate(self.network_state['biases']):
                b_flat = b.flatten()
                # Ensure we have the right number of data points
                b_means = [b_flat.mean() for _ in range(num_epochs)]
                param_data.append(b_means)
                param_names.append(f'b{i+1}_mean')
            
            # Add loss (ensure same length)
            if len(self.network_state['loss_history']) == num_epochs:
                param_data.append(self.network_state['loss_history'])
                param_names.append('Loss')
            else:
                # Pad or truncate loss to match
                loss_data = self.network_state['loss_history']
                if len(loss_data) > num_epochs:
                    loss_data = loss_data[:num_epochs]
                else:
                    # Pad with last value
                    while len(loss_data) < num_epochs:
                        loss_data.append(loss_data[-1] if loss_data else 0)
                param_data.append(loss_data)
                param_names.append('Loss')
            
            # Convert to numpy array
            param_array = np.array(param_data).T
            
            # Compute correlation matrix
            corr_matrix = np.corrcoef(param_array.T)
            
            # Plot correlation matrix
            im = self.ax6.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            self.ax6.set_title("Parameter Correlations")
            self.ax6.set_xticks(range(len(param_names)))
            self.ax6.set_yticks(range(len(param_names)))
            self.ax6.set_xticklabels(param_names, rotation=45, ha='right')
            self.ax6.set_yticklabels(param_names)
            
            # Add colorbar
            self.fig.colorbar(im, ax=self.ax6, shrink=0.8)
            
            # Add correlation values as text
            for i in range(len(param_names)):
                for j in range(len(param_names)):
                    text = self.ax6.text(j, i, f'{corr_matrix[i, j]:.2f}',
                                       ha="center", va="center", color="black", fontsize=8)
            
        except Exception as e:
            self.logger.error(f"Error plotting correlation matrix: {e}")
            self.ax6.text(0.5, 0.5, f'Error plotting correlations: {e}', 
                         ha='center', va='center', transform=self.ax6.transAxes)

def main():
    """Main function to run the test."""
    root = tk.Tk()
    app = SynchronizedEvolutionGraphs(root)
    
    print("🧪 Neural Network Synchronized Evolution Graphs Test")
    print("=" * 70)
    print("This test demonstrates:")
    print("• How weight adjustments influence bias impacts during forward passes")
    print("• Synchronized evolution of network parameters")
    print("• Correlation analysis between parameters and loss")
    print("• Educational visualization of neural network training dynamics")
    print("\nFeatures:")
    print("• Real-time parameter evolution graphs")
    print("• Synchronized updates across all visualizations")
    print("• Correlation matrix showing parameter relationships")
    print("• Interactive training controls")
    print("• Step-by-step forward pass analysis")
    
    root.mainloop()

if __name__ == "__main__":
    main()
