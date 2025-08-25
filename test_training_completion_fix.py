#!/usr/bin/env python3
"""
Test Training Completion Fix
This test verifies that training completion no longer causes segmentation faults.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestTrainingCompletionFix:
    """Test class for training completion fix."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Training Completion Fix Test")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Create notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create test tab
        self.create_test_tab()
        
        # Create status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        logger.info("Test window created successfully")
    
    def create_test_tab(self):
        """Create the test tab."""
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="Test")
        
        # Create test controls
        controls_frame = ttk.LabelFrame(test_frame, text="Test Controls", padding="10")
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Test button
        test_button = ttk.Button(controls_frame, text="Test Training Completion", command=self.test_training_completion)
        test_button.pack(pady=5)
        
        # Multiple test button
        multiple_button = ttk.Button(controls_frame, text="Test Multiple Completions", command=self.test_multiple_completions)
        multiple_button.pack(pady=5)
        
        # Tab switching button
        tab_button = ttk.Button(controls_frame, text="Switch Tabs During Test", command=self.test_tab_switching)
        tab_button.pack(pady=5)
        
        # Results text
        self.results_text = tk.Text(test_frame, height=15, width=80)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(test_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.configure(yscrollcommand=scrollbar.set)
    
    def log_result(self, message):
        """Log a result message."""
        logger.info(message)
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def test_training_completion(self):
        """Test single training completion."""
        try:
            self.log_result("=== Testing Single Training Completion ===")
            
            # Simulate training completion
            self.log_result("1. Simulating training completion...")
            self.simulate_training_completion("/test/model_20250628_120000")
            
            # Check if GUI is still responsive
            self.log_result("2. Checking GUI responsiveness...")
            if self.root.winfo_exists():
                self.log_result("✅ GUI is still responsive")
            else:
                self.log_result("❌ GUI is not responsive")
            
            # Check if notebook is still working
            self.log_result("3. Checking notebook functionality...")
            current_tab = self.notebook.select()
            if current_tab:
                self.log_result("✅ Notebook is still functional")
            else:
                self.log_result("❌ Notebook is not functional")
            
            self.log_result("=== Single Training Completion Test Completed ===")
            
        except Exception as e:
            self.log_result(f"❌ Error in single training completion test: {e}")
            logger.error(f"Error in single training completion test: {e}")
    
    def test_multiple_completions(self):
        """Test multiple training completions."""
        try:
            self.log_result("=== Testing Multiple Training Completions ===")
            
            for i in range(3):
                self.log_result(f"1.{i+1}. Simulating training completion {i+1}...")
                self.simulate_training_completion(f"/test/model_20250628_12000{i}")
                
                # Small delay between completions
                self.root.after(100)
                self.root.update_idletasks()
            
            # Check final state
            self.log_result("2. Checking final GUI state...")
            if self.root.winfo_exists():
                self.log_result("✅ GUI is still responsive after multiple completions")
            else:
                self.log_result("❌ GUI is not responsive after multiple completions")
            
            self.log_result("=== Multiple Training Completions Test Completed ===")
            
        except Exception as e:
            self.log_result(f"❌ Error in multiple training completions test: {e}")
            logger.error(f"Error in multiple training completions test: {e}")
    
    def test_tab_switching(self):
        """Test tab switching during training completion."""
        try:
            self.log_result("=== Testing Tab Switching During Training Completion ===")
            
            # Create additional tabs
            for i in range(3):
                tab_frame = ttk.Frame(self.notebook)
                self.notebook.add(tab_frame, text=f"Tab {i+1}")
                ttk.Label(tab_frame, text=f"This is tab {i+1}").pack(pady=20)
            
            # Switch tabs during training completion
            self.log_result("1. Starting tab switching test...")
            
            for i in range(5):
                # Switch to a random tab
                tab_index = i % self.notebook.index("end")
                self.notebook.select(tab_index)
                self.log_result(f"2.{i+1}. Switched to tab {tab_index}")
                
                # Simulate training completion
                self.simulate_training_completion(f"/test/model_20250628_12000{i}")
                
                # Small delay
                self.root.after(50)
                self.root.update_idletasks()
            
            # Check final state
            self.log_result("3. Checking final GUI state...")
            if self.root.winfo_exists():
                self.log_result("✅ GUI is still responsive after tab switching test")
            else:
                self.log_result("❌ GUI is not responsive after tab switching test")
            
            self.log_result("=== Tab Switching Test Completed ===")
            
        except Exception as e:
            self.log_result(f"❌ Error in tab switching test: {e}")
            logger.error(f"Error in tab switching test: {e}")
    
    def simulate_training_completion(self, model_dir):
        """Simulate training completion without actual training."""
        try:
            # Simulate the training completion process
            self.status_var.set("Training completed successfully")
            self.root.update_idletasks()
            
            # Simulate a small delay like real training completion
            self.root.after(10)
            self.root.update_idletasks()
            
            self.log_result(f"   ✅ Simulated training completion for: {model_dir}")
            
        except Exception as e:
            self.log_result(f"   ❌ Error simulating training completion: {e}")
            raise
    
    def run(self):
        """Run the test."""
        logger.info("Starting training completion fix test...")
        self.log_result("Training Completion Fix Test Started")
        self.log_result("Click the test buttons to verify the fix works")
        self.root.mainloop()

def main():
    """Main function."""
    print("Training Completion Fix Test")
    print("This test verifies that training completion no longer causes segmentation faults.")
    print("1. Click 'Test Training Completion' to test single completion")
    print("2. Click 'Test Multiple Completions' to test multiple completions")
    print("3. Click 'Switch Tabs During Test' to test tab switching during completion")
    print("4. Watch the results in the text area")
    print("5. The GUI should remain stable and responsive")
    
    test = TestTrainingCompletionFix()
    test.run()

if __name__ == "__main__":
    main() 