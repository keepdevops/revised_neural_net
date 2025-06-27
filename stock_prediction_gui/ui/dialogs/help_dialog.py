"""
Help dialog for the Stock Prediction GUI.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import webbrowser

class HelpDialog:
    """Help dialog."""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create the dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Help - Stock Prediction GUI")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create widgets
        self.create_widgets()
        
        # Center dialog
        self.center_dialog()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Stock Prediction GUI Help", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Help notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Quick Start tab
        quick_start_frame = ttk.Frame(notebook, padding="10")
        notebook.add(quick_start_frame, text="Quick Start")
        self.create_quick_start_content(quick_start_frame)
        
        # Data tab
        data_frame = ttk.Frame(notebook, padding="10")
        notebook.add(data_frame, text="Data")
        self.create_data_content(data_frame)
        
        # Training tab
        training_frame = ttk.Frame(notebook, padding="10")
        notebook.add(training_frame, text="Training")
        self.create_training_content(training_frame)
        
        # Prediction tab
        prediction_frame = ttk.Frame(notebook, padding="10")
        notebook.add(prediction_frame, text="Prediction")
        self.create_prediction_content(prediction_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side="right")
        ttk.Button(button_frame, text="Open Documentation", command=self.open_documentation).pack(side="left")
    
    def create_quick_start_content(self, parent):
        """Create quick start content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
QUICK START GUIDE

1. LOAD DATA
   - Go to the Data tab
   - Click "Browse" to select your CSV data file
   - The file should contain columns: open, high, low, close, volume
   - Click "Load Data" to load the file

2. TRAIN MODEL
   - Go to the Training tab
   - Set your training parameters (epochs, learning rate, etc.)
   - Select an output directory for the model
   - Click "Start Training"
   - Monitor progress in the status bar

3. MAKE PREDICTIONS
   - Go to the Prediction tab
   - Select a trained model from the dropdown
   - Load prediction data (same format as training data)
   - Click "Make Prediction"
   - View results in the Results tab

4. VIEW RESULTS
   - Go to the Results tab
   - View training plots and prediction results
   - Export results to CSV if needed

TIPS:
- Start with small datasets for testing
- Use validation split to avoid overfitting
- Monitor training loss to ensure convergence
- Save your models for later use
        """
        text.insert("1.0", content)
        text.config(state="disabled")
    
    def create_data_content(self, parent):
        """Create data content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
DATA REQUIREMENTS

CSV File Format:
Your data file should be a CSV with the following columns:
- open: Opening price
- high: Highest price during the period
- low: Lowest price during the period  
- close: Closing price
- volume: Trading volume

Optional columns:
- timestamp: Date/time of the data point
- ticker: Stock symbol

Data Preprocessing:
- The system automatically normalizes your data
- Missing values are handled automatically
- Technical indicators are calculated automatically

Supported Formats:
- CSV files (.csv)
- Excel files (.xlsx, .xls) - will be converted to CSV

Data Validation:
- Minimum 100 data points recommended
- Data should be in chronological order
- Prices should be positive numbers
- Volume should be non-negative
        """
        text.insert("1.0", content)
        text.config(state="disabled")
    
    def create_training_content(self, parent):
        """Create training content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
TRAINING PARAMETERS

Basic Parameters:
- Epochs: Number of training iterations (100-1000 recommended)
- Learning Rate: How fast the model learns (0.001-0.1 recommended)
- Batch Size: Number of samples per training step (32-128 recommended)
- Validation Split: Percentage of data for validation (0.1-0.3 recommended)

Advanced Parameters:
- Hidden Layers: Number of hidden layers (1-3 recommended)
- Neurons per Layer: Number of neurons in each layer (32-128 recommended)
- Dropout Rate: Prevents overfitting (0.1-0.5 recommended)
- Early Stopping: Stops training when validation loss stops improving

Training Process:
1. Data is split into training and validation sets
2. Model is trained on training data
3. Performance is evaluated on validation data
4. Training stops when validation loss stops improving
5. Best model weights are saved

Monitoring:
- Watch the training loss curve
- Validation loss should be similar to training loss
- If validation loss increases while training loss decreases, you may be overfitting
        """
        text.insert("1.0", content)
        text.config(state="disabled")
    
    def create_prediction_content(self, parent):
        """Create prediction content."""
        text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        text.pack(fill="both", expand=True)
        
        content = """
MAKING PREDICTIONS

Selecting a Model:
- Choose a trained model from the dropdown
- Models are saved in timestamped directories
- Each model contains training history and configuration

Prediction Data:
- Use the same format as training data
- Data should be preprocessed the same way
- Can use the same file as training data for testing

Prediction Process:
1. Load prediction data
2. Select trained model
3. Click "Make Prediction"
4. Results are saved to CSV file
5. View results in Results tab

Output Files:
- predictions_[timestamp].csv: Predicted values
- actual_vs_predicted.png: Comparison plot
- error_distribution.png: Error analysis

Interpreting Results:
- Compare predicted vs actual values
- Check error distribution for bias
- Lower error indicates better predictions
- Consider using ensemble methods for better accuracy
        """
        text.insert("1.0", content)
        text.config(state="disabled")
    
    def open_documentation(self):
        """Open online documentation."""
        try:
            webbrowser.open("https://github.com/your-repo/stock-prediction-gui")
        except Exception as e:
            tk.messagebox.showwarning("Error", f"Could not open documentation: {e}")
    
    def center_dialog(self):
        """Center the dialog on the screen."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def show(self):
        """Show the dialog."""
        self.dialog.wait_window()
        return self.result 