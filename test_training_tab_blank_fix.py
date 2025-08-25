#!/usr/bin/env python3
"""
Test script to reproduce and fix the training tab blank screen issue.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
import threading
import time

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_training_panel_blank_issue():
    """Test to reproduce the training tab blank screen issue."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create test window
    root = tk.Tk()
    root.title("Training Tab Blank Screen Test")
    root.geometry("800x600")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create training tab
    training_frame = ttk.Frame(notebook, padding="10")
    notebook.add(training_frame, text="Training")
    
    # Add some test content to training tab
    title_label = ttk.Label(training_frame, text="Training Panel Test", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Add test controls
    controls_frame = ttk.LabelFrame(training_frame, text="Test Controls", padding="10")
    controls_frame.pack(fill="x", pady=(0, 10))
    
    # Test button that simulates training completion
    def simulate_training_completion():
        logger.info("Simulating training completion...")
        
        # Simulate the issue by clearing the frame
        for widget in training_frame.winfo_children():
            widget.destroy()
        
        # Recreate the content
        title_label = ttk.Label(training_frame, text="Training Panel Test (Recreated)", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        controls_frame = ttk.LabelFrame(training_frame, text="Test Controls (Recreated)", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(controls_frame, text="Training completed! Panel should be visible.").pack()
        
        logger.info("Training panel recreated")
    
    ttk.Button(controls_frame, text="Simulate Training Completion", 
               command=simulate_training_completion).pack()
    
    # Add a second tab for comparison
    second_frame = ttk.Frame(notebook, padding="10")
    notebook.add(second_frame, text="Second Tab")
    
    ttk.Label(second_frame, text="This tab should remain visible").pack()
    
    # Add status bar
    status_var = tk.StringVar(value="Ready for testing")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_closing():
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    logger.info("Test window created. Click 'Simulate Training Completion' to test the issue.")
    
    # Run the test
    root.mainloop()

def fix_training_panel_issue():
    """Fix for the training panel blank screen issue."""
    
    # The issue is likely in the training completion handling
    # Here's the fix pattern:
    
    fix_code = '''
    # In training_panel.py, update the update_progress method:
    
    def update_progress(self, epoch, loss, val_loss, progress):
        """Update training progress display."""
        try:
            self.epoch_var.set(f"Epoch: {epoch}")
            self.loss_var.set(f"Loss: {loss:.6f}")
            self.val_loss_var.set(f"Validation Loss: {val_loss:.6f}")
            self.progress_var.set(progress)
            
            # Add data point to plot
            self.add_data_point(epoch, loss, val_loss)
            
            # Re-enable start button when training completes
            if progress >= 100:
                # Don't set is_training = False here, let the completion callback handle it
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")
                
                # Ensure the plot is updated one final time
                self.update_plot()
                
        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")
    
    # In app.py, update the training completion handler:
    
    def _on_training_completed(self, model_dir, error=None):
        """Handle training completion."""
        try:
            self.is_training = False
            
            if error:
                self.main_window.training_failed(error)
                self.main_window.update_status("Training failed")
            else:
                # Ensure the training panel is properly reset
                if hasattr(self.main_window, 'training_panel'):
                    self.main_window.training_panel.is_training = False
                    self.main_window.training_panel.start_button.config(state="normal")
                    self.main_window.training_panel.stop_button.config(state="disabled")
                
                self.main_window.training_completed(model_dir)
                self.main_window.update_status("Training completed successfully")
                self.refresh_models_and_select_latest()
                
        except Exception as e:
            self.logger.error(f"Error handling training completion: {e}")
    '''
    
    print("Fix for training panel blank screen issue:")
    print(fix_code)

if __name__ == "__main__":
    print("Testing training tab blank screen issue...")
    print("1. Run test to reproduce issue")
    print("2. Show fix for the issue")
    print()
    
    choice = input("Enter choice (1 for test, 2 for fix, 3 for both): ").strip()
    
    if choice == "1":
        test_training_panel_blank_issue()
    elif choice == "2":
        fix_training_panel_issue()
    elif choice == "3":
        fix_training_panel_issue()
        print("\n" + "="*50 + "\n")
        test_training_panel_blank_issue()
    else:
        print("Invalid choice. Running test...")
        test_training_panel_blank_issue() 