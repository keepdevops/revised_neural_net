"""
Advanced Stock Price Prediction Neural Network

This script implements an advanced neural network for stock price prediction
with improved architecture, regularization, and optimization techniques.
"""

import numpy as np
import pandas as pd
import argparse
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

def sigmoid(x):
    """Sigmoid activation function."""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_derivative(x):
    """Derivative of sigmoid function."""
    s = sigmoid(x)
    return s * (1 - s)

def relu(x):
    """ReLU activation function."""
    return np.maximum(0, x)

def relu_derivative(x):
    """Derivative of ReLU function."""
    return np.where(x > 0, 1, 0)

def compute_rsi(prices, period=14):
    """Compute Relative Strength Index."""
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gains = pd.Series(gains).rolling(window=period).mean().values
    avg_losses = pd.Series(losses).rolling(window=period).mean().values
    
    rs = avg_gains / (avg_losses + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    return np.concatenate([[np.nan], rsi])

def add_technical_indicators(df):
    """Add comprehensive technical indicators."""
    df_enhanced = df.copy()
    
    # Basic moving averages
    df_enhanced['ma_5'] = df_enhanced['close'].rolling(window=5).mean()
    df_enhanced['ma_10'] = df_enhanced['close'].rolling(window=10).mean()
    df_enhanced['ma_20'] = df_enhanced['close'].rolling(window=20).mean()
    df_enhanced['ma_50'] = df_enhanced['close'].rolling(window=50).mean()
    
    # Exponential moving averages
    df_enhanced['ema_12'] = df_enhanced['close'].ewm(span=12).mean()
    df_enhanced['ema_26'] = df_enhanced['close'].ewm(span=26).mean()
    
    # RSI
    df_enhanced['rsi'] = compute_rsi(df_enhanced['close'], 14)
    
    # Price changes and returns
    df_enhanced['price_change'] = df_enhanced['close'].pct_change()
    df_enhanced['price_change_5'] = df_enhanced['close'].pct_change(periods=5)
    df_enhanced['price_change_10'] = df_enhanced['close'].pct_change(periods=10)
    
    # Volatility measures
    df_enhanced['volatility_10'] = df_enhanced['close'].rolling(window=10).std()
    df_enhanced['volatility_20'] = df_enhanced['close'].rolling(window=20).std()
    
    # Bollinger Bands
    df_enhanced['bb_middle'] = df_enhanced['close'].rolling(window=20).mean()
    bb_std = df_enhanced['close'].rolling(window=20).std()
    df_enhanced['bb_upper'] = df_enhanced['bb_middle'] + (bb_std * 2)
    df_enhanced['bb_lower'] = df_enhanced['bb_middle'] - (bb_std * 2)
    df_enhanced['bb_width'] = (df_enhanced['bb_upper'] - df_enhanced['bb_lower']) / df_enhanced['bb_middle']
    df_enhanced['bb_position'] = (df_enhanced['close'] - df_enhanced['bb_lower']) / (df_enhanced['bb_upper'] - df_enhanced['bb_lower'])
    
    # MACD
    exp1 = df_enhanced['close'].ewm(span=12).mean()
    exp2 = df_enhanced['close'].ewm(span=26).mean()
    df_enhanced['macd'] = exp1 - exp2
    df_enhanced['macd_signal'] = df_enhanced['macd'].ewm(span=9).mean()
    df_enhanced['macd_histogram'] = df_enhanced['macd'] - df_enhanced['macd_signal']
    
    # Stochastic Oscillator
    low_min = df_enhanced['low'].rolling(window=14).min()
    high_max = df_enhanced['high'].rolling(window=14).max()
    df_enhanced['stoch_k'] = 100 * (df_enhanced['close'] - low_min) / (high_max - low_min)
    df_enhanced['stoch_d'] = df_enhanced['stoch_k'].rolling(window=3).mean()
    
    # Williams %R
    df_enhanced['williams_r'] = -100 * (high_max - df_enhanced['close']) / (high_max - low_min)
    
    # Volume indicators
    df_enhanced['volume_ma'] = df_enhanced['vol'].rolling(window=10).mean()
    df_enhanced['volume_ratio'] = df_enhanced['vol'] / df_enhanced['volume_ma']
    df_enhanced['volume_sma_ratio'] = df_enhanced['vol'] / df_enhanced['vol'].rolling(window=20).mean()
    
    # Price momentum
    df_enhanced['momentum_5'] = df_enhanced['close'] - df_enhanced['close'].shift(5)
    df_enhanced['momentum_10'] = df_enhanced['close'] - df_enhanced['close'].shift(10)
    
    # Rate of change
    df_enhanced['roc_5'] = ((df_enhanced['close'] - df_enhanced['close'].shift(5)) / df_enhanced['close'].shift(5)) * 100
    df_enhanced['roc_10'] = ((df_enhanced['close'] - df_enhanced['close'].shift(10)) / df_enhanced['close'].shift(10)) * 100
    
    # Average True Range (ATR)
    high_low = df_enhanced['high'] - df_enhanced['low']
    high_close = np.abs(df_enhanced['high'] - df_enhanced['close'].shift())
    low_close = np.abs(df_enhanced['low'] - df_enhanced['close'].shift())
    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    df_enhanced['atr'] = true_range.rolling(window=14).mean()
    
    # Commodity Channel Index (CCI)
    typical_price = (df_enhanced['high'] + df_enhanced['low'] + df_enhanced['close']) / 3
    sma_tp = typical_price.rolling(window=20).mean()
    mad = typical_price.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())))
    df_enhanced['cci'] = (typical_price - sma_tp) / (0.015 * mad)
    
    # Money Flow Index (MFI)
    typical_price = (df_enhanced['high'] + df_enhanced['low'] + df_enhanced['close']) / 3
    money_flow = typical_price * df_enhanced['vol']
    
    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(window=14).sum()
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(window=14).sum()
    
    mfi_ratio = positive_flow / negative_flow
    df_enhanced['mfi'] = 100 - (100 / (1 + mfi_ratio))
    
    # Support and Resistance levels
    df_enhanced['support_20'] = df_enhanced['low'].rolling(window=20).min()
    df_enhanced['resistance_20'] = df_enhanced['high'].rolling(window=20).max()
    df_enhanced['price_to_support'] = (df_enhanced['close'] - df_enhanced['support_20']) / df_enhanced['support_20']
    df_enhanced['price_to_resistance'] = (df_enhanced['resistance_20'] - df_enhanced['close']) / df_enhanced['close']
    
    return df_enhanced

class AdvancedStockNet:
    """Advanced neural network for stock price prediction."""
    
    def __init__(self, input_size, hidden_sizes, learning_rate=0.001, dropout_rate=0.2, l2_reg=0.01):
        """
        Initialize the advanced neural network.
        
        Args:
            input_size (int): Number of input features
            hidden_sizes (list): List of hidden layer sizes
            learning_rate (float): Learning rate
            dropout_rate (float): Dropout rate for regularization
            l2_reg (float): L2 regularization coefficient
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.l2_reg = l2_reg
        
        # Initialize weights and biases
        self.weights = []
        self.biases = []
        self.layer_sizes = [input_size] + hidden_sizes + [1]
        
        for i in range(len(self.layer_sizes) - 1):
            # Xavier/Glorot initialization
            scale = np.sqrt(2.0 / (self.layer_sizes[i] + self.layer_sizes[i + 1]))
            W = np.random.randn(self.layer_sizes[i], self.layer_sizes[i + 1]) * scale
            b = np.zeros((1, self.layer_sizes[i + 1]))
            
            self.weights.append(W)
            self.biases.append(b)
        
        # Adam optimizer parameters
        self.m = [np.zeros_like(w) for w in self.weights]
        self.v = [np.zeros_like(w) for w in self.weights]
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.t = 0
        
        # Training history
        self.training_losses = []
        self.validation_losses = []
        
    def forward(self, X, training=True):
        """Forward pass with dropout."""
        self.activations = [X]
        self.z_values = []
        self.dropout_masks = []
        
        # Hidden layers
        for i in range(len(self.weights) - 1):
            z = np.dot(self.activations[-1], self.weights[i]) + self.biases[i]
            self.z_values.append(z)
            
            # ReLU activation for hidden layers
            a = relu(z)
            
            # Dropout
            if training and self.dropout_rate > 0:
                mask = np.random.binomial(1, 1 - self.dropout_rate, size=a.shape) / (1 - self.dropout_rate)
                a *= mask
                self.dropout_masks.append(mask)
            else:
                self.dropout_masks.append(None)
            
            self.activations.append(a)
        
        # Output layer (linear activation)
        z = np.dot(self.activations[-1], self.weights[-1]) + self.biases[-1]
        self.z_values.append(z)
        self.activations.append(z)  # Linear activation
        
        return self.activations[-1]
    
    def backward(self, X, y, output):
        """Backward pass with L2 regularization."""
        m = X.shape[0]
        
        # Compute gradients
        delta = output - y
        
        # Backpropagate through layers
        for i in range(len(self.weights) - 1, -1, -1):
            # Weight gradients with L2 regularization
            dW = np.dot(self.activations[i].T, delta) / m + self.l2_reg * self.weights[i]
            db = np.sum(delta, axis=0, keepdims=True) / m
            
            # Update weights and biases using Adam
            self.t += 1
            
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * dW
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (dW ** 2)
            
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            
            self.weights[i] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)
            self.biases[i] -= self.learning_rate * db
            
            # Compute delta for next layer
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * relu_derivative(self.z_values[i - 1])
                
                # Apply dropout mask
                if self.dropout_masks[i - 1] is not None:
                    delta *= self.dropout_masks[i - 1]
    
    def train(self, X, y, epochs=100, batch_size=32, validation_split=0.2, early_stopping_patience=10, progress_callback=None):
        """Train the model with early stopping."""
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split, random_state=42)
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Shuffle training data
            indices = np.random.permutation(len(X_train))
            X_train_shuffled = X_train[indices]
            y_train_shuffled = y_train[indices]
            
            # Mini-batch training
            train_losses = []
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train_shuffled[i:i + batch_size]
                batch_y = y_train_shuffled[i:i + batch_size]
                
                # Forward pass
                output = self.forward(batch_X, training=True)
                
                # Compute loss
                loss = np.mean((output - batch_y) ** 2)
                train_losses.append(loss)
                
                # Backward pass
                self.backward(batch_X, batch_y, output)
            
            # Validation
            val_output = self.forward(X_val, training=False)
            val_loss = np.mean((val_output - y_val) ** 2)
            
            # Store losses
            self.training_losses.append(np.mean(train_losses))
            self.validation_losses.append(val_loss)
            
            # Call progress callback if provided
            if progress_callback:
                try:
                    progress_callback(epoch, np.mean(train_losses), val_loss)
                except Exception as e:
                    print(f"Warning: Progress callback failed: {e}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.save_best_weights()
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping at epoch {epoch}")
                    self.load_best_weights()
                    break
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Train Loss = {np.mean(train_losses):.6f}, Val Loss = {val_loss:.6f}")
    
    def save_best_weights(self):
        """Save the best weights."""
        self.best_weights = [w.copy() for w in self.weights]
        self.best_biases = [b.copy() for b in self.biases]
    
    def load_best_weights(self):
        """Load the best weights."""
        if hasattr(self, 'best_weights'):
            self.weights = [w.copy() for w in self.best_weights]
            self.biases = [b.copy() for b in self.best_biases]
    
    def predict(self, X):
        """Make predictions."""
        return self.forward(X, training=False)
    
    def save_model(self, model_dir):
        """Save the trained model."""
        os.makedirs(model_dir, exist_ok=True)
        
        # Save weights and biases as separate arrays
        weights_data = {}
        biases_data = {}
        
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            weights_data[f'W{i+1}'] = w
            biases_data[f'b{i+1}'] = b
        
        # Save weights and biases
        np.savez(os.path.join(model_dir, 'weights.npz'), **weights_data)
        np.savez(os.path.join(model_dir, 'biases.npz'), **biases_data)
        
        # Save model configuration
        model_config = {
            'layer_sizes': self.layer_sizes,
            'input_size': self.input_size,
            'hidden_sizes': self.hidden_sizes,
            'learning_rate': self.learning_rate,
            'dropout_rate': self.dropout_rate,
            'l2_reg': self.l2_reg
        }
        
        with open(os.path.join(model_dir, 'model_config.json'), 'w') as f:
            json.dump(model_config, f, indent=2)
        
        # Save training history
        history_df = pd.DataFrame({
            'epoch': range(len(self.training_losses)),
            'training_loss': self.training_losses,
            'validation_loss': self.validation_losses
        })
        history_df.to_csv(os.path.join(model_dir, 'training_history.csv'), index=False)
        
        # Plot training history
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.training_losses, label='Training Loss')
        plt.plot(self.validation_losses, label='Validation Loss')
        plt.title('Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(self.training_losses[-100:], label='Training Loss (Last 100)')
        plt.plot(self.validation_losses[-100:], label='Validation Loss (Last 100)')
        plt.title('Recent Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(model_dir, 'training_history.png'), dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train advanced stock prediction model')
    parser.add_argument('--data_file', type=str, required=True, help='Input CSV file')
    parser.add_argument('--x_features', type=str, default='open,high,low,vol', help='Input features')
    parser.add_argument('--y_feature', type=str, default='close', help='Target feature')
    parser.add_argument('--hidden_sizes', type=str, default='64,32', help='Hidden layer sizes')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--dropout_rate', type=float, default=0.2, help='Dropout rate')
    parser.add_argument('--l2_reg', type=float, default=0.01, help='L2 regularization')
    parser.add_argument('--epochs', type=int, default=200, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--validation_split', type=float, default=0.2, help='Validation split')
    parser.add_argument('--early_stopping_patience', type=int, default=15, help='Early stopping patience')
    
    args = parser.parse_args()
    
    # Load and prepare data
    print("Loading data...")
    df = pd.read_csv(args.data_file)
    
    # Add technical indicators
    print("Adding technical indicators...")
    df = add_technical_indicators(df)
    
    # Select features
    x_features = args.x_features.split(',')
    y_feature = args.y_feature
    
    # Remove rows with NaN values
    df = df.dropna()
    
    # Prepare X and y
    X = df[x_features].values
    y = df[y_feature].values.reshape(-1, 1)
    
    # Normalize data
    print("Normalizing data...")
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y)
    
    # Create model
    hidden_sizes = [int(x) for x in args.hidden_sizes.split(',')]
    model = AdvancedStockNet(
        input_size=len(x_features),
        hidden_sizes=hidden_sizes,
        learning_rate=args.learning_rate,
        dropout_rate=args.dropout_rate,
        l2_reg=args.l2_reg
    )
    
    # Train model
    print("Training model...")
    model.train(
        X_scaled, y_scaled,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=args.validation_split,
        early_stopping_patience=args.early_stopping_patience
    )
    
    # Create model directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_dir = f"advanced_model_{timestamp}"
    
    # Save model
    print("Saving model...")
    model.save_model(model_dir)
    
    # Save scalers and feature info
    np.save(os.path.join(model_dir, 'scaler_X.npy'), scaler_X)
    np.save(os.path.join(model_dir, 'scaler_y.npy'), scaler_y)
    
    feature_info = {
        'x_features': x_features,
        'y_feature': y_feature,
        'input_size': len(x_features),
        'hidden_sizes': hidden_sizes
    }
    
    with open(os.path.join(model_dir, 'feature_info.json'), 'w') as f:
        json.dump(feature_info, f, indent=2)
    
    print(f"Model saved to: {model_dir}")
    print(f"Final training loss: {model.training_losses[-1]:.6f}")
    print(f"Best validation loss: {min(model.validation_losses):.6f}")

if __name__ == "__main__":
    main() 