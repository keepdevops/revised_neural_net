#!/usr/bin/env python3
"""
Simplified GUI test to isolate segmentation fault.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_step_by_step():
    """Test GUI creation step by step."""
    print("🧪 Step-by-step GUI test")
    print("=" * 40)
    
    try:
        # Step 1: Create root window
        print("Step 1: Creating root window...")
        root = tk.Tk()
        root.title("Test GUI")
        root.geometry("800x600")
        print("✅ Root window created")
        
        # Step 2: Create notebook
        print("Step 2: Creating notebook...")
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        print("✅ Notebook created")
        
        # Step 3: Create tabs
        print("Step 3: Creating tabs...")
        
        # Data tab
        data_frame = ttk.Frame(notebook, padding="10")
        notebook.add(data_frame, text="Data")
        ttk.Label(data_frame, text="Data Tab").pack()
        print("✅ Data tab created")
        
        # Training tab
        training_frame = ttk.Frame(notebook, padding="10")
        notebook.add(training_frame, text="Training")
        ttk.Label(training_frame, text="Training Tab").pack()
        print("✅ Training tab created")
        
        # Prediction tab
        prediction_frame = ttk.Frame(notebook, padding="10")
        notebook.add(prediction_frame, text="Prediction")
        ttk.Label(prediction_frame, text="Prediction Tab").pack()
        print("✅ Prediction tab created")
        
        # Step 4: Test matplotlib integration
        print("Step 4: Testing matplotlib integration...")
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            
            # Create a simple plot in the training tab
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
            ax.set_title('Test Plot')
            
            canvas = FigureCanvasTkAgg(fig, training_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            print("✅ Matplotlib integration successful")
            
        except Exception as e:
            print(f"⚠️  Matplotlib integration failed: {e}")
        
        # Step 5: Test app import
        print("Step 5: Testing app import...")
        try:
            from stock_prediction_gui.core.app import StockPredictionApp
            print("✅ App import successful")
        except Exception as e:
            print(f"❌ App import failed: {e}")
        
        # Step 6: Test training panel import
        print("Step 6: Testing training panel import...")
        try:
            from stock_prediction_gui.ui.widgets.training_panel import TrainingPanel
            print("✅ Training panel import successful")
        except Exception as e:
            print(f"❌ Training panel import failed: {e}")
        
        # Step 7: Update window
        print("Step 7: Updating window...")
        root.update()
        print("✅ Window updated")
        
        # Step 8: Show success message
        messagebox.showinfo("Success", "GUI test completed successfully!")
        
        # Step 9: Cleanup
        print("Step 8: Cleaning up...")
        root.destroy()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_app():
    """Test the full app creation."""
    print("\n🧪 Full app test")
    print("=" * 40)
    
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Import and create app
        from stock_prediction_gui.core.app import StockPredictionApp
        
        print("Creating root window...")
        root = tk.Tk()
        
        print("Creating app...")
        app = StockPredictionApp(root)
        
        print("✅ Full app created successfully")
        
        # Don't run mainloop, just destroy
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Full app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests."""
    print("🧪 Segmentation Fault Isolation Test")
    print("=" * 50)
    
    # Test 1: Step by step
    print("\nTest 1: Step-by-step GUI creation")
    result1 = test_step_by_step()
    
    # Test 2: Full app
    print("\nTest 2: Full app creation")
    result2 = test_full_app()
    
    print("\n" + "=" * 50)
    print("Results:")
    print(f"Step-by-step test: {'✅ PASSED' if result1 else '❌ FAILED'}")
    print(f"Full app test: {'✅ PASSED' if result2 else '❌ FAILED'}")
    
    if result1 and result2:
        print("\n🎉 All tests passed! The issue might be intermittent.")
        print("Try running the main GUI again.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return result1 and result2

if __name__ == "__main__":
    main() 