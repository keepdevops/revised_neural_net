#!/usr/bin/env python3
"""
Test Training Completion Error Diagnosis
This test helps diagnose the specific error in the training_completed method.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestTrainingCompletionErrorDiagnosis:
    """Test class for diagnosing training completion errors."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Training Completion Error Diagnosis")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Create test controls
        controls_frame = ttk.LabelFrame(main_frame, text="Error Diagnosis Controls", padding="10")
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Test button
        test_button = ttk.Button(controls_frame, text="Test Training Completion Error", command=self.test_training_completion_error)
        test_button.pack(pady=5)
        
        # Results text
        self.results_text = tk.Text(main_frame, height=20, width=80)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        logger.info("Error diagnosis test window created")
    
    def log_result(self, message):
        """Log a result message."""
        logger.info(message)
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def test_training_completed_method(self, model_dir):
        """Test the training_completed method with detailed error tracking."""
        try:
            self.log_result("=== Testing training_completed method ===")
            
            # Step 1: Check root window
            self.log_result("1. Checking root window...")
            if not hasattr(self, 'root'):
                raise Exception("No root attribute")
            if not self.root.winfo_exists():
                raise Exception("Root window does not exist")
            self.log_result("   ✅ Root window is valid")
            
            # Step 2: Check training panel
            self.log_result("2. Checking training panel...")
            if not hasattr(self, 'training_panel'):
                self.log_result("   ⚠️ No training_panel attribute")
            else:
                self.log_result("   ✅ Training panel exists")
            
            # Step 3: Test status update
            self.log_result("3. Testing status update...")
            try:
                # Create a mock status_var if it doesn't exist
                if not hasattr(self, 'status_var'):
                    self.status_var = tk.StringVar(value="Ready")
                self.status_var.set("Training completed successfully")
                self.log_result("   ✅ Status update successful")
            except Exception as e:
                raise Exception(f"Status update failed: {e}")
            
            # Step 4: Test root update
            self.log_result("4. Testing root update...")
            try:
                self.root.update_idletasks()
                self.log_result("   ✅ Root update successful")
            except Exception as e:
                raise Exception(f"Root update failed: {e}")
            
            # Step 5: Test message box
            self.log_result("5. Testing message box...")
            try:
                messagebox.showinfo("Success", f"Training completed!\nModel saved to: {model_dir}")
                self.log_result("   ✅ Message box successful")
            except Exception as e:
                raise Exception(f"Message box failed: {e}")
            
            self.log_result("=== All tests passed ===")
            return True
            
        except Exception as e:
            error_details = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
            self.log_result(f"❌ Test failed: {error_details}")
            return False
    
    def test_training_completion_error(self):
        """Test the training completion error scenario."""
        try:
            self.log_result("=== Starting Error Diagnosis Test ===")
            
            # Test with a sample model directory
            model_dir = "/test/model_20250628_120000"
            
            # Run the test
            success = self.test_training_completed_method(model_dir)
            
            if success:
                self.log_result("✅ All tests passed - no errors detected")
            else:
                self.log_result("❌ Errors detected - check the details above")
            
            self.log_result("=== Error Diagnosis Test Completed ===")
            
        except Exception as e:
            self.log_result(f"❌ Error in diagnosis test: {e}")
            import traceback
            self.log_result(f"Traceback: {traceback.format_exc()}")
    
    def run(self):
        """Run the test."""
        logger.info("Starting training completion error diagnosis...")
        self.log_result("Training Completion Error Diagnosis Started")
        self.log_result("Click 'Test Training Completion Error' to diagnose the issue")
        self.root.mainloop()

def main():
    """Main function."""
    print("Training Completion Error Diagnosis")
    print("This test helps diagnose the specific error in the training_completed method.")
    print("1. Click 'Test Training Completion Error' to run the diagnosis")
    print("2. Watch the results in the text area")
    print("3. Look for specific error messages and tracebacks")
    
    test = TestTrainingCompletionErrorDiagnosis()
    test.run()

if __name__ == "__main__":
    main() 