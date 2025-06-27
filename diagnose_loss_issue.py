#!/usr/bin/env python3
"""
Diagnostic script to identify loss calculation issues
"""

import numpy as np
import pandas as pd
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_loss_issue():
    """Diagnose why loss is showing as 0.000000."""
    print("🔍 Diagnosing loss calculation issue...")
    
    try:
        from stock_net import StockNet
        
        # Create a simple test case
        print("\n📊 Creating test data...")
        
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create realistic stock-like data
        X = np.random.randn(n_samples, n_features) * 10 + 100  # Stock prices around 100
        y = np.random.randn(n_samples, 1) * 5 + 100  # Target prices
        
        print(f"X shape: {X.shape}, X range: [{X.min():.2f}, {X.max():.2f}]")
        print(f"y shape: {y.shape}, y range: [{y.min():.2f}, {y.max():.2f}]")
        
        # Test normalization
        print("\n🔧 Testing normalization...")
        model = StockNet(input_size=n_features, hidden_size=4)
        
        # Test normalization
        X_norm, y_norm = model.normalize(X, y)
        print(f"X_norm range: [{X_norm.min():.6f}, {X_norm.max():.6f}]")
        print(f"y_norm range: [{y_norm.min():.6f}, {y_norm.max():.6f}]")
        
        # Test forward pass
        print("\n🚀 Testing forward pass...")
        output = model.forward(X_norm)
        print(f"Output shape: {output.shape}")
        print(f"Output range: [{output.min():.6f}, {output.max():.6f}]")
        
        # Test loss calculation
        print("\n📈 Testing loss calculation...")
        mse = np.mean((output - y_norm) ** 2)
        print(f"Calculated MSE: {mse:.10f}")
        
        # Test with different data ranges
        print("\n🔄 Testing with different data ranges...")
        
        # Test with very small values
        X_small = np.random.randn(n_samples, n_features) * 0.001
        y_small = np.random.randn(n_samples, 1) * 0.001
        model_small = StockNet(input_size=n_features, hidden_size=4)
        X_small_norm, y_small_norm = model_small.normalize(X_small, y_small)
        output_small = model_small.forward(X_small_norm)
        mse_small = np.mean((output_small - y_small_norm) ** 2)
        print(f"Small values MSE: {mse_small:.10f}")
        
        # Test with very large values
        X_large = np.random.randn(n_samples, n_features) * 10000
        y_large = np.random.randn(n_samples, 1) * 10000
        model_large = StockNet(input_size=n_features, hidden_size=4)
        X_large_norm, y_large_norm = model_large.normalize(X_large, y_large)
        output_large = model_large.forward(X_large_norm)
        mse_large = np.mean((output_large - y_large_norm) ** 2)
        print(f"Large values MSE: {mse_large:.10f}")
        
        # Test with zero values
        X_zero = np.zeros((n_samples, n_features))
        y_zero = np.zeros((n_samples, 1))
        model_zero = StockNet(input_size=n_features, hidden_size=4)
        X_zero_norm, y_zero_norm = model_zero.normalize(X_zero, y_zero)
        output_zero = model_zero.forward(X_zero_norm)
        mse_zero = np.mean((output_zero - y_zero_norm) ** 2)
        print(f"Zero values MSE: {mse_zero:.10f}")
        
        # Test weight initialization
        print("\n⚖️ Testing weight initialization...")
        print(f"W1 shape: {model.W1.shape}, W1 range: [{model.W1.min():.6f}, {model.W1.max():.6f}]")
        print(f"W2 shape: {model.W2.shape}, W2 range: [{model.W2.min():.6f}, {model.W2.max():.6f}]")
        
        # Test a few training steps
        print("\n🎯 Testing training steps...")
        for epoch in range(5):
            # Forward pass
            output = model.forward(X_norm)
            
            # Calculate loss
            mse = np.mean((output - y_norm) ** 2)
            
            # Backward pass
            model.backward(X_norm, y_norm, output, learning_rate=0.001)
            
            print(f"Epoch {epoch}: MSE = {mse:.10f}")
            
            # Check if weights are changing
            if epoch > 0:
                w1_change = np.mean(np.abs(model.W1 - prev_w1))
                w2_change = np.mean(np.abs(model.W2 - prev_w2))
                print(f"  Weight changes: W1={w1_change:.10f}, W2={w2_change:.10f}")
            
            prev_w1 = model.W1.copy()
            prev_w2 = model.W2.copy()
        
        # Check for potential issues
        print("\n⚠️ Potential issues identified:")
        
        if mse < 1e-10:
            print("  - Loss is extremely small (< 1e-10)")
            print("  - This could indicate:")
            print("    * Data normalization issues")
            print("    * Target values too close to predictions")
            print("    * Numerical precision issues")
        
        if np.allclose(output, y_norm, atol=1e-6):
            print("  - Predictions are very close to targets")
            print("  - This could indicate overfitting or data leakage")
        
        if np.allclose(model.W1, 0, atol=1e-6) or np.allclose(model.W2, 0, atol=1e-6):
            print("  - Weights are very close to zero")
            print("  - This could indicate vanishing gradients")
        
        print("\n💡 Recommendations:")
        print("  1. Check your data preprocessing")
        print("  2. Verify target variable selection")
        print("  3. Try different learning rates")
        print("  4. Check for data leakage")
        print("  5. Use different weight initialization")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_loss_issue()
    if success:
        print("\n🎉 Loss diagnosis completed!")
    else:
        print("\n💥 Loss diagnosis failed!") 