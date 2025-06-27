#!/usr/bin/env python3
"""
Test script to verify that the training fix works correctly.
"""

import os
import sys
import subprocess
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_training_fix():
    """Test that the training script works with the fix."""
    print("🧪 Testing training fix...")
    
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
            
            print(f"🚀 Running training command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            print(f"📊 Return code: {result.returncode}")
            if result.stdout:
                print(f"📤 stdout: {result.stdout}")
            if result.stderr:
                print(f"📥 stderr: {result.stderr}")
            
            if result.returncode == 0:
                print("✅ Training completed successfully!")
                
                # Check if model files were created
                expected_files = [
                    "stock_model.npz",
                    "feature_info.json"
                ]
                
                for file in expected_files:
                    file_path = os.path.join(model_dir, file)
                    if os.path.exists(file_path):
                        print(f"✅ Found expected file: {file}")
                    else:
                        print(f"❌ Missing expected file: {file}")
                        return False
                
                return True
            else:
                print(f"❌ Training failed with return code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Training timed out")
            return False
        except Exception as e:
            print(f"❌ Error during training: {e}")
            return False

if __name__ == "__main__":
    success = test_training_fix()
    if success:
        print("\n🎉 Training fix test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Training fix test FAILED!")
        sys.exit(1) 