#!/usr/bin/env python3
"""
Comprehensive diagnostic script for training issues
"""

import numpy as np
import pandas as pd
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_training_issue():
    """Comprehensive diagnosis of training issues."""
    print("🔍 Comprehensive Training Issue Diagnosis")
    print("=" * 50)
    
    try:
        from stock_net import StockNet
        
        # Test 1: Check for data leakage
        print("\n1️⃣ Testing for Data Leakage")
        print("-" * 30)
        
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        # Create data where target is directly derived from input
        X = np.random.randn(n_samples, n_features) * 10 + 100
        y = X[:, 0:1] * 0.5 + X[:, 1:2] * 0.3 + np.random.randn(n_samples, 1) * 0.01
        
        model = StockNet(input_size=n_features, hidden_size=4)
        X_norm, y_norm = model.normalize(X, y)
        
        print(f"Target correlation with input features:")
        for i in range(n_features):
            corr = np.corrcoef(X[:, i], y.flatten())[0, 1]
            print(f"  Feature {i}: {corr:.4f}")
        
        # Train and see if loss becomes very small quickly
        print("\nTraining with correlated data:")
        for epoch in range(20):
            output = model.forward(X_norm)
            mse = np.mean((output - y_norm) ** 2)
            model.backward(X_norm, y_norm, output, learning_rate=0.01)
            
            if epoch % 5 == 0:
                print(f"  Epoch {epoch}: MSE = {mse:.10f}")
                if mse < 1e-6:
                    print(f"    ⚠️ Very small loss detected!")
        
        # Test 2: Check for normalization issues
        print("\n2️⃣ Testing Normalization Issues")
        print("-" * 30)
        
        # Test with constant target values
        X_const = np.random.randn(n_samples, n_features) * 10 + 100
        y_const = np.full((n_samples, 1), 50.0)  # Constant target
        
        model_const = StockNet(input_size=n_features, hidden_size=4)
        X_const_norm, y_const_norm = model_const.normalize(X_const, y_const)
        
        print(f"Constant target - Original: {y_const[0, 0]:.2f}, Normalized: {y_const_norm[0, 0]:.6f}")
        
        # Test with very small range target values
        X_small_range = np.random.randn(n_samples, n_features) * 10 + 100
        y_small_range = np.random.randn(n_samples, 1) * 0.001 + 50.0  # Very small range
        
        model_small = StockNet(input_size=n_features, hidden_size=4)
        X_small_norm, y_small_norm = model_small.normalize(X_small_range, y_small_range)
        
        print(f"Small range target - Original range: [{y_small_range.min():.6f}, {y_small_range.max():.6f}]")
        print(f"Small range target - Normalized range: [{y_small_norm.min():.6f}, {y_small_norm.max():.6f}]")
        
        # Test 3: Check for weight initialization issues
        print("\n3️⃣ Testing Weight Initialization")
        print("-" * 30)
        
        model_weights = StockNet(input_size=n_features, hidden_size=4)
        print(f"W1 range: [{model_weights.W1.min():.6f}, {model_weights.W1.max():.6f}]")
        print(f"W2 range: [{model_weights.W2.min():.6f}, {model_weights.W2.max():.6f}]")
        
        # Test 4: Check for vanishing gradients
        print("\n4️⃣ Testing for Vanishing Gradients")
        print("-" * 30)
        
        # Train with very small learning rate
        model_vanishing = StockNet(input_size=n_features, hidden_size=4)
        X_test, y_test = model_vanishing.normalize(X, y)
        
        print("Training with very small learning rate (0.0001):")
        for epoch in range(10):
            output = model_vanishing.forward(X_test)
            mse = np.mean((output - y_test) ** 2)
            model_vanishing.backward(X_test, y_test, output, learning_rate=0.0001)
            
            if epoch % 2 == 0:
                w1_change = np.mean(np.abs(model_vanishing.W1))
                w2_change = np.mean(np.abs(model_vanishing.W2))
                print(f"  Epoch {epoch}: MSE = {mse:.10f}, W1_avg = {w1_change:.6f}, W2_avg = {w2_change:.6f}")
        
        # Test 5: Check for overfitting
        print("\n5️⃣ Testing for Overfitting")
        print("-" * 30)
        
        # Use very small dataset
        X_small = X[:10]  # Only 10 samples
        y_small = y[:10]
        
        model_overfit = StockNet(input_size=n_features, hidden_size=8)  # Larger hidden layer
        X_small_norm, y_small_norm = model_overfit.normalize(X_small, y_small)
        
        print("Training on very small dataset (10 samples) with large hidden layer:")
        for epoch in range(50):
            output = model_overfit.forward(X_small_norm)
            mse = np.mean((output - y_small_norm) ** 2)
            model_overfit.backward(X_small_norm, y_small_norm, output, learning_rate=0.01)
            
            if epoch % 10 == 0:
                print(f"  Epoch {epoch}: MSE = {mse:.10f}")
                if mse < 1e-6:
                    print(f"    ⚠️ Overfitting detected!")
        
        # Test 6: Check print formatting
        print("\n6️⃣ Testing Print Formatting")
        print("-" * 30)
        
        very_small_values = [1e-7, 1e-8, 1e-9, 1e-10, 1e-11]
        print("Testing different precision levels:")
        for val in very_small_values:
            print(f"  {val:.6f} (6 decimal places)")
            print(f"  {val:.10f} (10 decimal places)")
            print(f"  {val:.15f} (15 decimal places)")
            print()
        
        # Summary and recommendations
        print("\n📋 Summary and Recommendations")
        print("=" * 50)
        print("Potential causes of very small loss values:")
        print("1. Data leakage - target is too similar to input features")
        print("2. Overfitting - model memorizes training data")
        print("3. Normalization issues - target values have very small range")
        print("4. Print formatting - loss is small but not actually zero")
        print("5. Vanishing gradients - weights become very small")
        print("6. Learning rate too high - model converges too quickly")
        
        print("\n💡 Recommendations:")
        print("1. Check your data preprocessing and feature selection")
        print("2. Verify target variable is not too similar to input features")
        print("3. Use validation set to detect overfitting")
        print("4. Try different learning rates")
        print("5. Use regularization techniques")
        print("6. Check data quality and remove outliers")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_training_issue()
    if success:
        print("\n🎉 Training diagnosis completed!")
    else:
        print("\n💥 Training diagnosis failed!") 