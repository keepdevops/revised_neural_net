# Forward Pass Visualizer Polynomial Fitting Fix

## Issue Description

The forward pass visualizer was encountering polynomial fitting errors when trying to plot trend lines in the prediction vs input plot:

```
2025-06-28 23:41:53,333 - stock_prediction_gui.ui.widgets.forward_pass_visualizer - ERROR - Visualization update error: Polynomial must be 1d only.
```

## Root Cause

The error occurred in the `update_prediction_plot()` method of `ForwardPassVisualizer` when trying to fit polynomial trend lines using `np.polyfit()`. The issue happened when:

1. **Input values** were numpy arrays instead of 1-dimensional arrays
2. **Prediction values** were numpy arrays instead of 1-dimensional arrays
3. **Mixed data types** were passed to `np.polyfit()` without proper conversion
4. **NaN/Inf values** were present in the data

The `np.polyfit()` function requires 1-dimensional arrays, but the visualizer was receiving multi-dimensional numpy arrays, lists, or mixed data types.

## Solution Applied

Modified the `update_prediction_plot()` method to properly handle all data types:

### 1. **Scalar Value Extraction**
```python
# Ensure predictions are scalar values
prediction_values = []
for pred in predictions:
    if hasattr(pred, 'item'):
        prediction_values.append(pred.item())
    elif hasattr(pred, '__len__') and len(pred) > 0:
        prediction_values.append(pred[0])
    else:
        prediction_values.append(pred)

# Ensure input_values are scalar values
input_scalars = []
for inp in input_values:
    if hasattr(inp, 'item'):
        input_scalars.append(inp.item())
    elif hasattr(inp, '__len__') and len(inp) > 0:
        input_scalars.append(inp[0])
    else:
        input_scalars.append(inp)
```

### 2. **Array Flattening and Validation**
```python
# Convert to numpy arrays and ensure they are 1D
x_data = np.array(input_scalars).flatten()
y_data = np.array(prediction_values).flatten()

# Only fit if we have valid numeric data
if np.all(np.isfinite(x_data)) and np.all(np.isfinite(y_data)):
    z = np.polyfit(x_data, y_data, 1)
    p = np.poly1d(z)
    x_trend = np.linspace(min(x_data), max(x_data), 100)
    self.pred_ax.plot(x_trend, p(x_trend), 'r--', alpha=0.5, linewidth=1)
```

### 3. **Error Handling**
```python
try:
    # Polynomial fitting code
    ...
except Exception as e:
    # Log the error but don't crash the visualization
    self.logger.warning(f"Could not fit trend line: {e}")
```

## Data Types Handled

The fix now properly handles:

1. **Python scalars**: `float`, `int`
2. **Numpy scalar arrays**: `np.array(42.0)`
3. **Numpy arrays**: `np.array([1, 2, 3, 4])`
4. **Python lists**: `[1, 2, 3, 4]`
5. **Mixed data types**: Combinations of the above
6. **NaN/Inf values**: Gracefully skipped during fitting
7. **Empty data**: Handled without errors

## Testing

Created comprehensive test script `test_forward_pass_polynomial_fix.py` that verifies:

- ✅ Scalar polynomial fitting
- ✅ Numpy scalar polynomial fitting  
- ✅ Numpy array polynomial fitting
- ✅ Mixed types polynomial fitting
- ✅ NaN/Inf value handling
- ✅ Empty data handling

## Benefits

1. **Robust Data Handling**: Works with any data type combination
2. **Error Prevention**: No more polynomial fitting crashes
3. **Graceful Degradation**: Falls back gracefully when fitting fails
4. **Better Visualization**: Trend lines appear when data is valid
5. **Improved User Experience**: No more error messages during visualization

## Files Modified

- `stock_prediction_gui/ui/widgets/forward_pass_visualizer.py`
  - Updated `update_prediction_plot()` method
  - Added robust data type handling
  - Added error handling for polynomial fitting

## Test Files Created

- `test_forward_pass_polynomial_fix.py`
  - Comprehensive test suite for polynomial fitting
  - Tests all data type combinations
  - Interactive GUI for manual testing

## Impact

This fix ensures that the forward pass visualizer can handle any data format without crashing, providing a stable and reliable visualization experience for users analyzing neural network training progress. 