#!/usr/bin/env python3
"""
Test script to verify 3D visualization compatibility files are created.
"""

import os
import sys
import subprocess
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_3d_compatibility():
    """Test that all required files for 3D visualization are created."""
    print("🧪 Testing 3D visualization compatibility...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Copy test data to temp directory
        test_data_file = "training_data_sample.csv"
        if not os.path.exists(test_data_file):
            print(f"❌ Test data file not found: {test_data_file}")
            return False
        
        temp_data_file = os.path.join(temp_dir, "test_data.csv")
        shutil.copy(test_data_file, temp_data_file)
        
        # Create model directory
        model_dir = os.path.join(temp_dir, "test_model")
        
        try:
            # Run training command
            cmd = [
                sys.executable, "train.py",
                "--data_file", temp_data_file,
                "--model_dir", model_dir,
                "--x_features", "open,high,low,vol",
                "--y_feature", "close",
                "--hidden_size", "4",
                "--learning_rate", "0.001",
                "--batch_size", "16"
            ]
            
            print(f"🚀 Running training command...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            print(f"📊 Return code: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ Training completed successfully!")
                
                # Check for all required files for 3D visualization
                required_files = [
                    "stock_model.npz",
                    "feature_info.json",
                    "scaler_mean.csv",
                    "scaler_std.csv",
                    "target_min.csv",
                    "target_max.csv",
                    "training_losses.csv",
                    "training_data.csv"
                ]
                
                missing_files = []
                for file in required_files:
                    file_path = os.path.join(model_dir, file)
                    if os.path.exists(file_path):
                        print(f"✅ Found required file: {file}")
                    else:
                        print(f"❌ Missing required file: {file}")
                        missing_files.append(file)
                
                # Check for weights_history directory
                weights_history_dir = os.path.join(model_dir, "weights_history")
                if os.path.exists(weights_history_dir):
                    weight_files = os.listdir(weights_history_dir)
                    print(f"✅ Found weights_history directory with {len(weight_files)} files")
                else:
                    print(f"❌ Missing weights_history directory")
                    missing_files.append("weights_history/")
                
                if missing_files:
                    print(f"❌ Missing files: {missing_files}")
                    return False
                else:
                    print("✅ All required files for 3D visualization are present!")
                    return True
            else:
                print(f"❌ Training failed with return code {result.returncode}")
                if result.stderr:
                    print(f"📥 stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Training timed out")
            return False
        except Exception as e:
            print(f"❌ Error during training: {e}")
            return False

if __name__ == "__main__":
    success = test_3d_compatibility()
    if success:
        print("\n🎉 3D visualization compatibility test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 3D visualization compatibility test FAILED!")
        sys.exit(1) 