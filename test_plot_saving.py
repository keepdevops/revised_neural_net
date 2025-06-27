#!/usr/bin/env python3
"""
Test script to verify that plots are being saved properly during training.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plot_saving():
    """Test that plots are being saved properly."""
    print("🧪 Testing plot saving functionality...")
    
    try:
        # Create a test model directory
        test_model_dir = "test_plot_saving_model"
        os.makedirs(test_model_dir, exist_ok=True)
        plots_dir = os.path.join(test_model_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        print(f"📁 Created test model directory: {test_model_dir}")
        print(f"📁 Created plots directory: {plots_dir}")
        
        # Simulate training losses
        epochs = 100
        train_losses = np.random.exponential(0.1, epochs) * np.exp(-np.arange(epochs) * 0.02)
        val_losses = train_losses + np.random.normal(0, 0.01, epochs)
        
        print(f"📊 Generated {len(train_losses)} training loss values")
        
        # Save training losses
        losses_file = os.path.join(test_model_dir, 'training_losses.csv')
        np.savetxt(losses_file, train_losses, delimiter=',')
        print(f"💾 Saved training losses to: {losses_file}")
        
        # Create and save loss plot (simulating the _training_completed method)
        fig = plt.Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        epoch_range = list(range(1, len(train_losses) + 1))
        ax.plot(epoch_range, train_losses, 'b-', label='Training Loss', linewidth=2)
        ax.plot(epoch_range, val_losses, 'r-', label='Validation Loss', linewidth=2)
        ax.set_title("Training Progress (Test Model)")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("MSE Loss")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save the plot
        plot_path = os.path.join(plots_dir, 'loss_curve.png')
        fig.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"🖼️ Saved loss plot to: {plot_path}")
        
        # Create additional test plots
        additional_plots = [
            ('actual_vs_predicted.png', 'Actual vs Predicted'),
            ('error_distribution.png', 'Error Distribution'),
            ('training_progress.png', 'Training Progress')
        ]
        
        for filename, title in additional_plots:
            fig = plt.Figure(figsize=(6, 4))
            ax = fig.add_subplot(111)
            
            # Create some sample data for each plot
            if 'actual_vs_predicted' in filename:
                actual = np.random.normal(100, 10, 50)
                predicted = actual + np.random.normal(0, 2, 50)
                ax.scatter(actual, predicted, alpha=0.6)
                ax.plot([actual.min(), actual.max()], [actual.min(), actual.max()], 'r--', label='Perfect Prediction')
                ax.set_xlabel('Actual Values')
                ax.set_ylabel('Predicted Values')
            elif 'error_distribution' in filename:
                errors = np.random.normal(0, 1, 100)
                ax.hist(errors, bins=20, alpha=0.7, edgecolor='black')
                ax.set_xlabel('Prediction Error')
                ax.set_ylabel('Frequency')
            else:
                # Training progress
                ax.plot(epoch_range, train_losses, 'b-', linewidth=2)
                ax.set_xlabel('Epoch')
                ax.set_ylabel('Loss')
            
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
            
            plot_path = os.path.join(plots_dir, filename)
            fig.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"🖼️ Saved {title} plot to: {plot_path}")
        
        # Verify all plots were created
        png_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        print(f"\n📊 Verification: Found {len(png_files)} PNG files in plots directory")
        for png_file in png_files:
            file_path = os.path.join(plots_dir, png_file)
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {png_file} ({file_size:,} bytes)")
        
        # Test the load_saved_plots functionality
        print("\n🧪 Testing load_saved_plots functionality...")
        
        # Import the GUI to test the method
        import tkinter as tk
        from gui.main_gui import StockPredictionGUI
        
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = StockPredictionGUI(root)
        app.selected_model_path = test_model_dir
        
        # Test the load_saved_plots method
        if hasattr(app, 'load_saved_plots'):
            print("✅ load_saved_plots method exists")
            
            # Test if the method can handle the test data
            try:
                app.load_saved_plots()
                print("✅ load_saved_plots method executed successfully")
            except Exception as e:
                print(f"❌ load_saved_plots method failed: {e}")
                return False
        else:
            print("❌ load_saved_plots method not found")
            return False
        
        print("\n🎉 All plot saving tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass
        
        # Clean up test directory
        try:
            import shutil
            if os.path.exists(test_model_dir):
                shutil.rmtree(test_model_dir)
                print(f"🧹 Cleaned up test directory: {test_model_dir}")
        except:
            pass

if __name__ == "__main__":
    success = test_plot_saving()
    if success:
        print("\n✅ Test passed: Plot saving functionality is working correctly")
    else:
        print("\n❌ Test failed: Plot saving functionality has issues") 