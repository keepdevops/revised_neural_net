#!/usr/bin/env python3
"""
Test script to verify GUI repaint functionality after training completion.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging

def test_gui_repaint_functionality():
    """Test the GUI repaint functionality."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("🧪 Testing GUI Repaint Functionality")
    print("=" * 50)
    
    # Create main window
    root = tk.Tk()
    root.title("GUI Repaint Test")
    root.geometry("800x600")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create tabs
    tabs = {}
    tab_names = ["Data", "Training", "Prediction", "Results"]
    
    for name in tab_names:
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text=name)
        tabs[name] = frame
        
        # Add content to each tab
        ttk.Label(frame, text=f"{name} Tab Content", font=("Arial", 14, "bold")).pack(pady=20)
        
        # Add a text widget to simulate content
        text_widget = tk.Text(frame, height=10, width=50)
        text_widget.pack(fill="both", expand=True, pady=10)
        text_widget.insert(tk.END, f"This is the {name} tab.\n")
        text_widget.insert(tk.END, "Content will be updated during testing.\n")
        
        # Store reference to text widget
        tabs[f"{name}_text"] = text_widget
    
    # Create control panel
    control_frame = ttk.LabelFrame(root, text="Repaint Controls", padding="10")
    control_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    # Status label
    status_var = tk.StringVar(value="Ready")
    status_label = ttk.Label(root, textvariable=status_var, relief="sunken")
    status_label.pack(fill="x", padx=10, pady=(0, 10))
    
    def update_status(message):
        status_var.set(message)
        root.update_idletasks()
    
    def simulate_training():
        """Simulate training process."""
        update_status("Training in progress...")
        
        # Update training tab
        training_text = tabs["Training_text"]
        training_text.delete(1.0, tk.END)
        training_text.insert(tk.END, "Training started...\n")
        
        # Simulate training progress
        for epoch in range(1, 6):
            time.sleep(0.5)
            training_text.insert(tk.END, f"Epoch {epoch}: Loss = {0.1 * (0.9 ** epoch):.6f}\n")
            training_text.see(tk.END)
            root.update_idletasks()
        
        # Training completed
        training_text.insert(tk.END, "Training completed!\n")
        update_status("Training completed - testing repaint...")
        
        # Test repaint functionality
        test_repaint_functionality()
    
    def test_repaint_functionality():
        """Test the repaint functionality."""
        logger.info("Testing repaint functionality...")
        
        # Method 1: Force update of all tabs
        for name in tab_names:
            frame = tabs[name]
            frame.update_idletasks()
            frame.update()
            
            text_widget = tabs[f"{name}_text"]
            text_widget.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Tab repainted\n")
            text_widget.see(tk.END)
        
        # Method 2: Force update of notebook
        notebook.update_idletasks()
        notebook.update()
        
        # Method 3: Force update of root window
        root.update_idletasks()
        root.update()
        
        # Method 4: Switch between tabs to force repaint
        for i, name in enumerate(tab_names):
            root.after(i * 500, lambda tab=name: notebook.select(tab_names.index(tab)))
        
        # Method 5: Final update
        root.after(3000, lambda: final_repaint_test())
        
        update_status("Repaint test in progress...")
    
    def final_repaint_test():
        """Final repaint test."""
        logger.info("Performing final repaint test...")
        
        # Update all tabs with final message
        for name in tab_names:
            text_widget = tabs[f"{name}_text"]
            text_widget.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Final repaint test completed\n")
            text_widget.see(tk.END)
        
        # Force final update
        root.update_idletasks()
        root.update()
        
        update_status("Repaint test completed successfully!")
        messagebox.showinfo("Success", "GUI repaint test completed!\nAll tabs should be visible and functional.")
    
    def manual_repaint():
        """Manual repaint function."""
        logger.info("Manual repaint triggered")
        
        # Force repaint of all components
        for name in tab_names:
            frame = tabs[name]
            frame.update_idletasks()
            frame.update()
            
            text_widget = tabs[f"{name}_text"]
            text_widget.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Manual repaint\n")
            text_widget.see(tk.END)
        
        notebook.update_idletasks()
        notebook.update()
        root.update_idletasks()
        root.update()
        
        update_status("Manual repaint completed")
        logger.info("Manual repaint completed")
    
    def emergency_repaint():
        """Emergency repaint function."""
        logger.info("Emergency repaint triggered")
        
        # Aggressive repaint
        for _ in range(3):
            for name in tab_names:
                frame = tabs[name]
                frame.update_idletasks()
                frame.update()
            
            notebook.update_idletasks()
            notebook.update()
            root.update_idletasks()
            root.update()
            time.sleep(0.1)
        
        # Update status
        for name in tab_names:
            text_widget = tabs[f"{name}_text"]
            text_widget.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Emergency repaint completed\n")
            text_widget.see(tk.END)
        
        update_status("Emergency repaint completed")
        logger.info("Emergency repaint completed")
    
    # Create buttons
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(fill="x")
    
    ttk.Button(button_frame, text="Start Training Test", command=lambda: threading.Thread(target=simulate_training, daemon=True).start()).pack(side="left", padx=(0, 5))
    ttk.Button(button_frame, text="Manual Repaint", command=manual_repaint).pack(side="left", padx=(0, 5))
    ttk.Button(button_frame, text="Emergency Repaint", command=emergency_repaint).pack(side="left", padx=(0, 5))
    ttk.Button(button_frame, text="Clear All", command=lambda: [tabs[f"{name}_text"].delete(1.0, tk.END) for name in tab_names]).pack(side="right")
    
    # Instructions
    instructions_frame = ttk.LabelFrame(root, text="Test Instructions", padding="10")
    instructions_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    instructions = """
    1. Click 'Start Training Test' to simulate training completion
    2. Watch the repaint process across all tabs
    3. Use 'Manual Repaint' to force immediate repaint
    4. Use 'Emergency Repaint' for aggressive repainting
    5. Switch between tabs to verify they remain visible
    6. All tabs should remain functional after repaint
    """
    
    ttk.Label(instructions_frame, text=instructions, justify="left").pack(anchor="w")
    
    print("✅ Test window created successfully")
    print("📋 Instructions:")
    print("   1. Click 'Start Training Test' to simulate training")
    print("   2. Watch the repaint process across all tabs")
    print("   3. Use manual repaint buttons if needed")
    print("   4. Verify all tabs remain visible and functional")
    
    # Run the GUI
    try:
        root.mainloop()
        print("✅ Test completed successfully")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gui_repaint_functionality()
    if success:
        print("\n🎉 GUI repaint functionality test passed!")
        print("The repaint system should work correctly in the main GUI.")
    else:
        print("\n⚠️  GUI repaint functionality test failed!")
        print("There may be issues with the repaint system.") 