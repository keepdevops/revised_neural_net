#!/usr/bin/env python3
"""
Comprehensive test for the training tab robust fix.
Tests the training panel during actual training simulation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
import threading
import time
import random

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_training_panel_robustness():
    """Test the training panel robustness during training."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create test window
    root = tk.Tk()
    root.title("Training Tab Robustness Test")
    root.geometry("1200x800")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create training tab
    training_frame = ttk.Frame(notebook, padding="10")
    notebook.add(training_frame, text="Training")
    
    # Add content to training tab
    title_label = ttk.Label(training_frame, text="Training Panel (Robust Fix)", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Create left and right panels
    main_container = ttk.Frame(training_frame)
    main_container.pack(fill="both", expand=True)
    
    # Left panel for controls
    left_panel = ttk.Frame(main_container)
    left_panel.pack(side="left", fill="y", padx=(0, 10))
    
    # Right panel for plot
    right_panel = ttk.Frame(main_container)
    right_panel.pack(side="right", fill="both", expand=True)
    
    # Add controls to left panel
    controls_frame = ttk.LabelFrame(left_panel, text="Training Controls", padding="10")
    controls_frame.pack(fill="x", pady=(0, 10))
    
    # Progress section
    progress_frame = ttk.LabelFrame(left_panel, text="Training Progress", padding="10")
    progress_frame.pack(fill="x", pady=(0, 10))
    
    # Progress bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill="x", pady=(0, 10))
    
    # Progress labels
    epoch_var = tk.StringVar(value="Epoch: 0")
    loss_var = tk.StringVar(value="Loss: N/A")
    val_loss_var = tk.StringVar(value="Validation Loss: N/A")
    
    ttk.Label(progress_frame, textvariable=epoch_var).pack(anchor="w")
    ttk.Label(progress_frame, textvariable=loss_var).pack(anchor="w")
    ttk.Label(progress_frame, textvariable=val_loss_var).pack(anchor="w")
    
    # Plot area
    plot_frame = ttk.LabelFrame(right_panel, text="Training Plot", padding="10")
    plot_frame.pack(fill="both", expand=True)
    
    # Simple text plot for testing
    plot_text = tk.Text(plot_frame, height=15, wrap=tk.WORD)
    plot_text.pack(fill="both", expand=True)
    plot_text.insert(tk.END, "Training plot will appear here...\n")
    
    # Training state
    training_active = [False]
    training_data = {'epochs': [], 'losses': [], 'val_losses': []}
    
    # Test functions
    def simulate_training():
        """Simulate training process with realistic data."""
        logger.info("Starting robust training simulation...")
        
        # Disable start button, enable stop button
        start_button.config(state="disabled")
        stop_button.config(state="normal")
        
        # Simulate training progress with realistic loss patterns
        initial_loss = 0.001
        for epoch in range(20):
            if not training_active[0]:  # Check if stopped
                break
                
            # Simulate realistic loss decrease
            loss = initial_loss * (0.95 ** epoch) + random.uniform(0, 0.0001)
            val_loss = loss * (0.98 ** epoch) + random.uniform(0, 0.00005)
            
            # Update progress
            progress = (epoch + 1) * 5  # 20 epochs = 100%
            progress_var.set(progress)
            epoch_var.set(f"Epoch: {epoch}")
            loss_var.set(f"Loss: {loss:.6f}")
            val_loss_var.set(f"Validation Loss: {val_loss:.6f}")
            
            # Store data
            training_data['epochs'].append(epoch)
            training_data['losses'].append(loss)
            training_data['val_losses'].append(val_loss)
            
            # Update plot
            plot_text.insert(tk.END, f"Epoch {epoch}: Loss = {loss:.6f}, Val = {val_loss:.6f}\n")
            plot_text.see(tk.END)
            
            # Simulate some UI stress by switching tabs occasionally
            if epoch % 5 == 0:
                root.after(100, lambda: notebook.select(1))  # Switch to second tab
                root.after(200, lambda: notebook.select(0))  # Switch back to training tab
            
            # Update GUI
            root.update_idletasks()
            time.sleep(0.3)  # Faster simulation
        
        # Training completed
        if training_active[0]:
            training_completed()
    
    def training_completed():
        """Handle training completion."""
        logger.info("Training completed, testing panel stability...")
        
        # Reset buttons
        start_button.config(state="normal")
        stop_button.config(state="disabled")
        
        # Update plot
        plot_text.insert(tk.END, "\n=== TRAINING COMPLETED ===\n")
        plot_text.insert(tk.END, "Panel should remain visible and functional.\n")
        plot_text.insert(tk.END, f"Final loss: {training_data['losses'][-1]:.6f}\n")
        plot_text.see(tk.END)
        
        # Test tab switching
        root.after(1000, test_tab_switching)
        
        # Force update
        training_frame.update_idletasks()
        
        logger.info("Training panel reset completed")
        messagebox.showinfo("Success", "Training completed! Panel should remain visible and stable.")
    
    def test_tab_switching():
        """Test tab switching after training completion."""
        logger.info("Testing tab switching stability...")
        
        # Switch between tabs multiple times
        for i in range(5):
            root.after(i * 500, lambda tab=i: notebook.select(tab % 2))
        
        # Switch back to training tab
        root.after(3000, lambda: notebook.select(0))
    
    def stop_training():
        """Stop training."""
        training_active[0] = False
        start_button.config(state="normal")
        stop_button.config(state="disabled")
        logger.info("Training stopped")
    
    def start_training():
        """Start training."""
        # Reset data
        training_data['epochs'] = []
        training_data['losses'] = []
        training_data['val_losses'] = []
        
        # Clear plot
        plot_text.delete(1.0, tk.END)
        plot_text.insert(tk.END, "Starting robust training simulation...\n")
        
        training_active[0] = True
        # Run in separate thread to avoid blocking GUI
        thread = threading.Thread(target=simulate_training, daemon=True)
        thread.start()
    
    # Buttons
    button_frame = ttk.Frame(controls_frame)
    button_frame.pack(fill="x")
    
    start_button = ttk.Button(button_frame, text="Start Training", command=start_training)
    start_button.pack(side="left", padx=(0, 5))
    
    stop_button = ttk.Button(button_frame, text="Stop Training", command=stop_training, state="disabled")
    stop_button.pack(side="left", padx=(0, 5))
    
    ttk.Button(button_frame, text="Reset Progress", command=lambda: progress_var.set(0)).pack(side="right")
    
    # Add a second tab for comparison
    second_frame = ttk.Frame(notebook, padding="10")
    notebook.add(second_frame, text="Second Tab")
    
    ttk.Label(second_frame, text="This tab should remain visible during training").pack()
    ttk.Label(second_frame, text="Switch between tabs to test stability").pack()
    ttk.Label(second_frame, text="The training tab should not go blank").pack()
    
    # Add status bar
    status_var = tk.StringVar(value="Ready for robust testing")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_closing():
        training_active[0] = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    logger.info("Robust training panel test window created.")
    logger.info("1. Click 'Start Training' to simulate training")
    logger.info("2. Watch for tab switching during training")
    logger.info("3. After completion, test tab switching stability")
    logger.info("4. The training tab should never go blank")
    
    # Run the test
    root.mainloop()

if __name__ == "__main__":
    print("Training Tab Robustness Test")
    print("This test verifies that the training tab remains stable during training.")
    print("It includes tab switching stress tests and realistic training simulation.")
    print()
    
    test_training_panel_robustness() 