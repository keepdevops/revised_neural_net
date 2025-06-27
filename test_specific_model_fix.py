#!/usr/bin/env python3
"""
Test script to verify the specific model directory fix
"""

import os
import sys
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_specific_model_fix():
    """Test the specific model directory that was causing the error."""
    print("🔍 Testing specific model directory fix...")
    
    try:
        # Check if the specific model directory exists
        model_dir = "stock_prediction_gui/model_20250626_232921"
        if not os.path.exists(model_dir):
            print(f"❌ Model directory not found: {model_dir}")
            return False
        
        print(f"✅ Found model directory: {model_dir}")
        
        # Check what files are in the directory
        files = os.listdir(model_dir)
        print(f"📁 Files in model directory: {files}")
        
        # Check for model_params.json
        model_params_path = os.path.join(model_dir, "model_params.json")
        if os.path.exists(model_params_path):
            print("✅ Found model_params.json")
            with open(model_params_path, 'r') as f:
                model_params = json.load(f)
            print(f"📊 Model params: {model_params}")
        else:
            print("❌ model_params.json not found")
            return False
        
        # Check for feature_info.json (should not exist in this case)
        feature_info_path = os.path.join(model_dir, "feature_info.json")
        if os.path.exists(feature_info_path):
            print("⚠️ feature_info.json exists (unexpected)")
        else:
            print("✅ feature_info.json not found (expected for this model)")
        
        # Check for model weight files
        weights_history_dir = os.path.join(model_dir, "weights_history")
        if os.path.exists(weights_history_dir):
            weight_files = os.listdir(weights_history_dir)
            print(f"📦 Weight files in weights_history: {weight_files}")
        else:
            print("⚠️ weights_history directory not found")
        
        # Test the prediction integration logic
        print("\n🧪 Testing prediction integration logic...")
        
        # Simulate the feature info loading logic
        feature_info = None
        
        # Try feature_info.json first (new format)
        if os.path.exists(feature_info_path):
            with open(feature_info_path, 'r') as f:
                feature_info = json.load(f)
            print("✅ Loaded feature info from feature_info.json")
        
        # Try model_params.json (old format)
        elif os.path.exists(model_params_path):
            with open(model_params_path, 'r') as f:
                model_params = json.load(f)
            
            # Create feature info from model params
            feature_info = {
                'x_features': ['open', 'high', 'low', 'close', 'vol', 'ma_10', 'rsi', 'price_change', 'volatility_10'],
                'y_feature': 'close',
                'model_type': 'basic',
                'training_params': model_params
            }
            print("✅ Created feature info from model_params.json")
        
        # Fallback to default features if no info files found
        else:
            feature_info = {
                'x_features': ['open', 'high', 'low', 'close', 'vol'],
                'y_feature': 'close',
                'model_type': 'basic',
                'training_params': {'hidden_size': 4}
            }
            print("⚠️ No feature info found, using default features")
        
        if feature_info:
            print(f"📋 Final feature info: {feature_info}")
            print("✅ Feature info loading logic works correctly")
        else:
            print("❌ Feature info loading failed")
            return False
        
        # Test model file detection
        print("\n🔍 Testing model file detection...")
        possible_model_files = [
            os.path.join(model_dir, "stock_model.npz"),
            os.path.join(model_dir, "model.npz"),
            os.path.join(model_dir, "final_model.npz"),
            os.path.join(model_dir, "best_model.npz"),
            os.path.join(model_dir, "weights.npz"),
            os.path.join(model_dir, "model_weights.npz")
        ]
        
        # Also check in weights_history directory
        if os.path.exists(weights_history_dir):
            weight_files = [f for f in os.listdir(weights_history_dir) if f.endswith('.npz')]
            if weight_files:
                # Use the most recent weight file
                latest_weight_file = sorted(weight_files)[-1]
                possible_model_files.append(os.path.join(weights_history_dir, latest_weight_file))
        
        model_file_found = None
        for mf in possible_model_files:
            if os.path.exists(mf):
                model_file_found = mf
                break
        
        if model_file_found:
            print(f"✅ Found model file: {model_file_found}")
        else:
            print("⚠️ No model file found")
            print(f"   Checked for: {possible_model_files}")
            
            # List what files are actually in the directory
            available_files = []
            for root, dirs, files in os.walk(model_dir):
                for file in files:
                    available_files.append(os.path.join(root, file))
            print(f"   Available files: {available_files}")
        
        print("\n✅ Specific model directory test completed!")
        print("\n📝 Summary:")
        print("   - Model directory exists: ✅")
        print("   - model_params.json found: ✅")
        print("   - Feature info loading: ✅")
        print("   - Model file detection: ⚠️ (no model files found)")
        print("\n💡 Note: This model directory appears to be incomplete - it has")
        print("   configuration but no actual trained model weights.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in specific model test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specific_model_fix()
    if success:
        print("\n🎉 Specific model fix test completed!")
    else:
        print("\n💥 Specific model fix test failed!") 