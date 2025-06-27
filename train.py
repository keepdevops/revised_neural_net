"""
Training script for Stock Price Prediction Neural Network

Usage:
    python train.py --data_file <path_to_csv> --model_dir <model_directory> --x_features <features> --y_feature <target>
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from stock_net import StockNet

def str2bool(v):
    """Convert string to boolean for argument parsing."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def train_model(data_file, model_dir, x_features, y_feature, hidden_size=4, learning_rate=0.001, 
                batch_size=32, epochs=1000, patience=20, history_interval=50, random_seed=42, 
                save_history=True, memory_opt=True, validation_split=0.2):
    """
    Train a neural network model for stock price prediction.
    
    Args:
        data_file (str): Path to the input CSV data file
        model_dir (str): Directory to save the trained model
        x_features (list): List of input feature names
        y_feature (str): Name of the target feature
        hidden_size (int): Size of the hidden layer
        learning_rate (float): Learning rate for weight updates
        batch_size (int): Size of mini-batches for training
        epochs (int): Maximum number of training epochs
        patience (int): Early stopping patience
        history_interval (int): How often to save weight history
        random_seed (int): Random seed for reproducibility
        save_history (bool): Whether to save weight history
        memory_opt (bool): Whether to enable memory optimization
        validation_split (float): Validation split ratio
    """
    print(f"\nTraining parameters:")
    print(f"Data File: {data_file}")
    print(f"Model Dir: {model_dir}")
    print(f"X Features: {x_features}")
    print(f"Y Feature: {y_feature}")
    print(f"Hidden Size: {hidden_size}")
    print(f"Learning Rate: {learning_rate}")
    print(f"Batch Size: {batch_size}")
    print(f"Epochs: {epochs}")
    print(f"Patience: {patience}")
    print(f"History Interval: {history_interval}")
    print(f"Random Seed: {random_seed}")
    print(f"Save History: {save_history}")
    print(f"Memory Optimization: {memory_opt}")
    print(f"Validation Split: {validation_split}")
    
    # Set random seed for reproducibility
    np.random.seed(random_seed)
    
    try:
        # Validate input paths
        if not os.path.exists(data_file):
            raise ValueError(f"Data file not found: {data_file}")
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Load and preprocess data
        print("\nLoading data...")
        df = pd.read_csv(data_file)
        
        # Validate features
        if not all(col in df.columns for col in x_features):
            raise ValueError(f"Some X features not found in data: {x_features}")
        if y_feature not in df.columns:
            raise ValueError(f"Y feature not found in data: {y_feature}")
        
        X = df[x_features].values
        y = df[y_feature].values.reshape(-1, 1)
        
        # Memory management: check data size
        data_size_mb = (X.nbytes + y.nbytes) / (1024 * 1024)
        print(f"Data size: {data_size_mb:.2f} MB")
        
        if memory_opt and data_size_mb > 100:  # If data is larger than 100MB and memory optimization is enabled
            print("Large dataset detected, reducing batch size for memory efficiency")
            batch_size = min(batch_size, 16)
        
        # Split data for validation if validation_split > 0
        if validation_split > 0:
            from stock_net import train_test_split_manual
            X_train, X_val, y_train, y_val = train_test_split_manual(X, y, test_size=validation_split, random_state=random_seed)
            print(f"Data split: {len(X_train)} training samples, {len(X_val)} validation samples")
        else:
            X_train, y_train = X, y
            X_val, y_val = None, None
            print(f"Using all {len(X_train)} samples for training (no validation split)")
        
        # Initialize neural network
        input_size = len(x_features)
        net = StockNet(input_size, hidden_size, 1)
        
        # Normalize data using the network's built-in normalization
        X_train_norm, y_train_norm = net.normalize(X_train, y_train)
        
        # Normalize validation data if it exists
        if X_val is not None and y_val is not None:
            X_val_norm = (X_val - net.X_min) / (net.X_max - net.X_min + 1e-8)
            y_val_norm = (y_val - net.Y_min) / (net.Y_max - net.Y_min + 1e-8) if net.has_target_norm else y_val
        else:
            X_val_norm, y_val_norm = None, None
        
        # Train the model
        print(f"\nTraining model with parameters:")
        print(f"Hidden Size: {hidden_size}")
        print(f"Learning Rate: {learning_rate}")
        print(f"Batch Size: {batch_size}")
        print(f"Input Features: {x_features}")
        print(f"Target Feature: {y_feature}")
        print(f"Data File: {data_file}")
        print(f"Model Directory: {model_dir}")
        
        # Train the model with validation data
        train_losses, val_losses = net.train(X_train_norm, y_train_norm, 
                 X_val=X_val_norm, y_val=y_val_norm,
                 learning_rate=learning_rate,
                 batch_size=batch_size,
                 epochs=epochs,
                 save_history=save_history,
                 history_interval=history_interval,
                 patience=patience)
        
        # Save model
        model_path = os.path.join(model_dir, "stock_model.npz")
        net.save_weights(model_dir, "stock_model")
        
        # Save normalization parameters in CSV format for 3D visualization compatibility
        # Extract normalization parameters from the network
        X_min = net.X_min
        X_max = net.X_max
        Y_min = net.Y_min if net.has_target_norm else None
        Y_max = net.Y_max if net.has_target_norm else None
        
        # Save as CSV files for 3D visualization compatibility
        np.savetxt(os.path.join(model_dir, "scaler_mean.csv"), X_min, delimiter=',')
        np.savetxt(os.path.join(model_dir, "scaler_std.csv"), X_max - X_min, delimiter=',')
        
        if Y_min is not None and Y_max is not None:
            np.savetxt(os.path.join(model_dir, "target_min.csv"), [Y_min], delimiter=',')
            np.savetxt(os.path.join(model_dir, "target_max.csv"), [Y_max], delimiter=',')
        
        # Save training losses for 3D visualization
        losses_data = np.column_stack([train_losses, val_losses])
        np.savetxt(os.path.join(model_dir, "training_losses.csv"), losses_data, delimiter=',')
        
        # Save training data for 3D visualization
        df.to_csv(os.path.join(model_dir, "training_data.csv"), index=False)
        
        # Move weight history to model directory for 3D visualization
        weights_history_src = os.path.join(os.getcwd(), "weights_history")
        weights_history_dst = os.path.join(model_dir, "weights_history")
        if os.path.exists(weights_history_src):
            import shutil
            if os.path.exists(weights_history_dst):
                shutil.rmtree(weights_history_dst)
            shutil.move(weights_history_src, weights_history_dst)
        
        # Save feature info for compatibility with other scripts
        feature_info = {
            'x_features': x_features,
            'y_feature': y_feature
        }
        
        with open(os.path.join(model_dir, "feature_info.json"), 'w') as f:
            json.dump(feature_info, f, indent=4)
        
        print(f"\nModel training completed successfully!")
        print(f"Model saved to: {model_path}")
        
        # Force garbage collection
        import gc
        gc.collect()
        
    except Exception as e:
        print(f"\nTraining failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a stock price prediction model")
    parser.add_argument("--data_file", type=str, required=True, help="Path to input CSV data file")
    parser.add_argument("--model_dir", type=str, required=True, help="Directory to save the trained model")
    parser.add_argument("--x_features", type=str, required=True, help="Comma-separated list of input features")
    parser.add_argument("--y_feature", type=str, required=True, help="Target feature name")
    parser.add_argument("--hidden_size", type=int, default=4, help="Size of hidden layer")
    parser.add_argument("--learning_rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--epochs", type=int, default=1000, help="Maximum number of training epochs")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience")
    parser.add_argument("--history_interval", type=int, default=50, help="How often to save weight history")
    parser.add_argument("--random_seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--save_history", type=str2bool, default=True, help="Whether to save weight history")
    parser.add_argument("--memory_opt", type=str2bool, default=True, help="Whether to enable memory optimization")
    parser.add_argument("--validation_split", type=float, default=0.2, help="Validation split ratio")
    
    args = parser.parse_args()
    
    print(f"\nReceived arguments:")
    print(f"Data File: {args.data_file}")
    print(f"Model Dir: {args.model_dir}")
    print(f"X Features: {args.x_features}")
    print(f"Y Feature: {args.y_feature}")
    print(f"Hidden Size: {args.hidden_size}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Epochs: {args.epochs}")
    print(f"Patience: {args.patience}")
    print(f"History Interval: {args.history_interval}")
    print(f"Random Seed: {args.random_seed}")
    print(f"Save History: {args.save_history}")
    print(f"Memory Optimization: {args.memory_opt}")
    print(f"Validation Split: {args.validation_split}")
    
    # Convert x_features from comma-separated string to list
    x_features = args.x_features.split(',')
    
    # Validate features
    if not x_features:
        raise ValueError("No input features specified")
    
    # Run training
    train_model(args.data_file, args.model_dir, x_features, args.y_feature,
               args.hidden_size, args.learning_rate, args.batch_size,
               args.epochs, args.patience, args.history_interval, args.random_seed,
               args.save_history, args.memory_opt, args.validation_split)
