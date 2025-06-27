# Feature Locking Guide

## How to Select and Lock Features for Training

The issue you encountered ("Please select at least one input feature") has been fixed! Here's how to properly select and lock features for training:

### Step-by-Step Process:

1. **Start the GUI**
   ```bash
   python gui/main_gui.py
   ```

2. **Data File Selection**
   - The GUI will automatically load `training_data_sample.csv` on startup
   - You should see 5 features in the Features listbox: `['open', 'high', 'low', 'vol', 'close']`
   - The Target Feature dropdown should automatically select "close"

3. **Select Input Features**
   - In the "Features" listbox, click on the features you want to use as inputs
   - For your case, select: `open`, `high`, `low`, `vol`
   - **Important**: Hold Ctrl (or Cmd on Mac) to select multiple features
   - You should see the selected features highlighted

4. **Lock the Features**
   - Click the "Lock Selected" button
   - You should see a confirmation message and the lock status should turn red
   - The status bar should show: "Locked features: open, high, low, vol"

5. **Verify Target Feature**
   - Make sure the "Target Feature" dropdown shows "close"
   - This is your output/target variable

6. **Start Training**
   - Click "Start Training" or "📊 Live Training (Error Loss)"
   - The training should now work with your selected features

### What Was Fixed:

- **Feature Selection**: The training method now properly uses locked features instead of the old selection system
- **Debug Output**: Added console output to help track what features are being selected and locked
- **Fallback Logic**: If no features are locked, it falls back to the old system

### Expected Console Output:

When you lock features, you should see:
```
🔍 Selected indices: (0, 1, 2, 3)
🔍 Available features: ['open', 'high', 'low', 'vol', 'close']
✅ Successfully locked 4 features: ['open', 'high', 'low', 'vol']
```

When you start training, you should see:
```
🔒 Using locked features: ['open', 'high', 'low', 'vol']
🎯 Target feature: close
📊 Input features: ['open', 'high', 'low', 'vol']
🎯 Target feature: close
🎯 Training with 4 input features and [X] samples
```

### Troubleshooting:

- **No features selected**: Make sure to click on features in the listbox before locking
- **Wrong target**: Verify the "Target Feature" dropdown shows "close"
- **Lock status**: The lock status should show "Locked" in red when features are locked
- **Console output**: Check the terminal for debug messages to see what's happening

### Alternative Data Files:

You can also use the dropdown to select different data files:
- `test_sample_data.csv` - Simple OHLCV data
- `training_data_sample.csv` - Normalized OHLCV data (recommended)

The refresh button (🔄) will scan for new CSV files in the directory. 