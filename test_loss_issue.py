#!/usr/bin/env python3
"""
Test script to reproduce the zero loss issue
"""

import numpy as np
import pandas as pd
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_loss_issue():
    """Test to reproduce the zero loss issue."""
    print("🔍 Testing for zero loss issue...")
    
    try:
        from stock_net import StockNet
        
        # Create a scenario that might cause zero loss
        print("\n📊 Creating test scenarios...")
        
        # Scenario 1: Very similar input and target
        print("\nScenario 1: Very similar input and target")
        np.random.seed(42)
        n_samples = 50
        n_features = 3
        
        # Create data where target is very similar to one input feature
        X = np.random.randn(n_samples, n_features) * 10 + 100
        y = X[:, 0:1] + np.random.randn(n_samples, 1) * 0.1  # Target is almost the same as first feature
        
        model = StockNet(input_size=n_features, hidden_size=4)
        X_norm, y_norm = model.normalize(X, y)
        
        print(f"X range: [{X.min():.2f}, {X.max():.2f}]")
        print(f"y range: [{y.min():.2f}, {y.max():.2f}]")
        print(f"y_norm range: [{y_norm.min():.6f}, {y_norm.max():.6f}]")
        
        # Train for a few epochs
        for epoch in range(10):
            output = model.forward(X_norm)
            mse = np.mean((output - y_norm) ** 2)
            model.backward(X_norm, y_norm, output, learning_rate=0.01)
            print(f"Epoch {epoch}: MSE = {mse:.10f}")
            
            if mse < 1e-6:
                print(f"  ⚠️ Very small loss detected at epoch {epoch}")
        
        # Scenario 2: Target values very close to zero after normalization
        print("\nScenario 2: Target values close to zero after normalization")
        X2 = np.random.randn(n_samples, n_features) * 10 + 100
        y2 = np.random.randn(n_samples, 1) * 0.001  # Very small target values
        
        model2 = StockNet(input_size=n_features, hidden_size=4)
        X2_norm, y2_norm = model2.normalize(X2, y2)
        
        print(f"y2 range: [{y2.min():.6f}, {y2.max():.6f}]")
        print(f"y2_norm range: [{y2_norm.min():.6f}, {y2_norm.max():.6f}]")
        
        # Train for a few epochs
        for epoch in range(10):
            output = model2.forward(X2_norm)
            mse = np.mean((output - y2_norm) ** 2)
            model2.backward(X2_norm, y2_norm, output, learning_rate=0.01)
            print(f"Epoch {epoch}: MSE = {mse:.10f}")
            
            if mse < 1e-6:
                print(f"  ⚠️ Very small loss detected at epoch {epoch}")
        
        # Scenario 3: Check if there's an issue with the print formatting
        print("\nScenario 3: Testing print formatting")
        very_small_loss = 1e-10
        print(f"Very small loss: {very_small_loss:.6f}")  # This should show 0.000000
        print(f"Very small loss with more precision: {very_small_loss:.10f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_loss_issue()
    if success:
        print("\n🎉 Loss issue test completed!")
    else:
        print("\n💥 Loss issue test failed!") 