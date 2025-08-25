#!/usr/bin/env python3
"""
Minimal test to isolate segmentation fault issue.
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_basic_imports():
    """Test basic imports."""
    print("Testing basic imports...")
    
    try:
        import tkinter as tk
        print("✅ Tkinter imported")
    except Exception as e:
        print(f"❌ Tkinter import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ Matplotlib imported")
    except Exception as e:
        print(f"❌ Matplotlib import failed: {e}")
        return False
    
    try:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        print("✅ FigureCanvasTkAgg imported")
    except Exception as e:
        print(f"❌ FigureCanvasTkAgg import failed: {e}")
        return False
    
    return True

def test_training_panel_import():
    """Test training panel import."""
    print("\nTesting training panel import...")
    
    try:
        from stock_prediction_gui.ui.widgets.training_panel import TrainingPanel
        print("✅ TrainingPanel imported")
        return True
    except Exception as e:
        print(f"❌ TrainingPanel import failed: {e}")
        return False

def test_app_creation():
    """Test app creation without GUI."""
    print("\nTesting app creation...")
    
    try:
        from stock_prediction_gui.core.app import StockPredictionApp
        print("✅ StockPredictionApp imported")
        return True
    except Exception as e:
        print(f"❌ StockPredictionApp import failed: {e}")
        return False

def test_minimal_gui():
    """Test minimal GUI creation."""
    print("\nTesting minimal GUI creation...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create minimal window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create a simple frame
        frame = ttk.Frame(root)
        frame.pack()
        
        # Create a simple label
        label = ttk.Label(frame, text="Test")
        label.pack()
        
        # Update the window
        root.update()
        
        # Destroy the window
        root.destroy()
        
        print("✅ Minimal GUI created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Minimal GUI creation failed: {e}")
        return False

def test_matplotlib_integration():
    """Test matplotlib integration with tkinter."""
    print("\nTesting matplotlib integration...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        
        # Create minimal window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create a simple frame
        frame = ttk.Frame(root)
        frame.pack()
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title('Test Plot')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack()
        
        # Update the window
        root.update()
        
        # Destroy the window
        root.destroy()
        
        print("✅ Matplotlib integration successful")
        return True
        
    except Exception as e:
        print(f"❌ Matplotlib integration failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Segmentation Fault Diagnostic Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Training Panel Import", test_training_panel_import),
        ("App Creation", test_app_creation),
        ("Minimal GUI", test_minimal_gui),
        ("Matplotlib Integration", test_matplotlib_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The issue might be elsewhere.")
        print("Try running the main GUI again.")
    else:
        print("⚠️  Some tests failed. This indicates the source of the segmentation fault.")
        print("Check the failed tests above for more details.")
    
    return all_passed

if __name__ == "__main__":
    main() 