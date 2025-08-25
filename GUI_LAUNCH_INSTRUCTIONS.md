# Stock Prediction GUI - Launch Instructions

## 🚀 **How to Launch the GUI**

The Stock Prediction GUI is located in the `stock_prediction_gui` directory. Here are the correct ways to launch it:

### **Method 1: Using the Root Launcher (Recommended)**
```bash
python launch_stock_prediction_gui.py
```

### **Method 2: Direct from stock_prediction_gui Directory**
```bash
cd stock_prediction_gui
python main.py
```

### **Method 3: Using the Safe Launcher**
```bash
cd stock_prediction_gui
python main_safe.py
```

## ❌ **What NOT to Do**

**Don't try to run:**
```bash
# This will fail - wrong directory structure
python stock_prediction_gui/main.py

# This will fail - wrong import paths
python -m stock_prediction_gui.main
```

## 🔧 **Troubleshooting**

### **Import Error: No module named 'stock_net'**
This error occurs when the Python path doesn't include the project root directory where `stock_net.py` is located.

**Solution:** Use one of the launcher scripts above, which properly set up the Python path.

### **File Structure**
```
revised_neural_net/
├── stock_net.py                    # Neural network implementation
├── launch_stock_prediction_gui.py  # Root launcher (recommended)
├── stock_prediction_gui/
│   ├── main.py                    # Main entry point
│   ├── main_safe.py               # Safe launcher
│   ├── core/                      # Core modules
│   │   ├── app.py                 # Main application
│   │   ├── data_manager.py        # Data management
│   │   ├── training_integration.py # Training integration
│   │   └── prediction_integration.py # Prediction integration
│   ├── ui/                        # User interface
│   │   ├── main_window.py         # Main window
│   │   └── widgets/               # UI widgets
│   └── utils/                     # Utilities
└── ...
```

## 📋 **Prerequisites**

Make sure you have the required dependencies installed:
```bash
pip install pandas matplotlib numpy tkinter pillow
```

## 🎯 **Quick Start**

1. **Navigate to the project root:**
   ```bash
   cd /path/to/revised_neural_net
   ```

2. **Launch the GUI:**
   ```bash
   python launch_stock_prediction_gui.py
   ```

3. **The GUI should open with:**
   - Data loading capabilities
   - Training interface
   - Prediction interface
   - 3D visualization
   - Results analysis

## 🔍 **Verification**

If the GUI launches successfully, you should see:
- A window titled "Stock Prediction Neural Network"
- Multiple tabs (Data, Training, Prediction, etc.)
- Control panels and display areas
- Log messages showing successful initialization

## 📞 **Support**

If you encounter issues:
1. Check that `stock_net.py` exists in the project root
2. Verify all dependencies are installed
3. Use the launcher scripts provided
4. Check the console output for error messages
5. Look at the log file: `stock_prediction_gui/stock_prediction_gui.log`

## 🔄 **Alternative GUI**

There's also a different GUI in the `gui` directory that you can run with:
```bash
cd gui
python main_gui.py
```

But the main, modular GUI is in the `stock_prediction_gui` directory. 