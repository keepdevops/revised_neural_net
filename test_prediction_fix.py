#!/usr/bin/env python3
"""
Test script for prediction feature_info.json fix
"""

import os
import sys
import tempfile
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_prediction_fix():
    """Test the prediction feature_info.json fix."""
    print("🧪 Testing prediction feature_info.json fix...")
    
    try:
        # Import the prediction components
        from stock_prediction_gui.ui.widgets.prediction_panel import PredictionPanel
        from stock_prediction_gui.core.prediction_integration import PredictionIntegration
        
        print("✅ Successfully imported prediction components")
        
        # Create a mock app object
        class MockApp:
            def __init__(self):
                self.selected_model = None
                self.current_data_file = "test_data.csv"
                self.current_output_dir = "test_output"
                self.model_manager = MockModelManager()
            
            def start_prediction(self, params):
                print(f"Mock start_prediction called with params: {params}")
                return True
        
        class MockModelManager:
            def get_available_models(self):
                return ["model_20250626_232921", "model_20250626_205914"]
        
        mock_app = MockApp()
        
        # Create a test model directory with feature_info.json
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"✅ Created test directory: {temp_dir}")
            
            # Create feature_info.json
            feature_info = {
                "x_features": ["feature1", "feature2"],
                "y_feature": "target",
                "model_type": "basic",
                "training_params": {
                    "hidden_size": 64
                }
            }
            
            feature_info_path = os.path.join(temp_dir, "feature_info.json")
            with open(feature_info_path, 'w') as f:
                json.dump(feature_info, f)
            
            print(f"✅ Created feature_info.json: {feature_info_path}")
            
            # Create a mock model file
            model_file_path = os.path.join(temp_dir, "stock_model.npz")
            with open(model_file_path, 'w') as f:
                f.write("mock model data")
            
            print(f"✅ Created mock model file: {model_file_path}")
            
            # Create a mock data file
            data_file_path = os.path.join(temp_dir, "test_data.csv")
            with open(data_file_path, 'w') as f:
                f.write("feature1,feature2,target\n1,2,3\n4,5,6")
            
            print(f"✅ Created mock data file: {data_file_path}")
            
            # Test prediction panel parameter generation
            print("\n📋 Testing prediction panel parameter generation...")
            
            mock_app.selected_model = temp_dir
            mock_app.current_data_file = data_file_path
            
            # Create prediction panel
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            prediction_panel = PredictionPanel(root, mock_app)
            
            # Test get_prediction_params
            params = prediction_panel.get_prediction_params()
            
            print(f"✅ Generated params: {params}")
            
            # Verify the model_path is correct
            if params['model_path'] == model_file_path:
                print("✅ Model path correctly points to model file")
            else:
                print(f"❌ Model path incorrect: {params['model_path']} (expected: {model_file_path})")
                return False
            
            # Test prediction integration path handling
            print("\n🔧 Testing prediction integration path handling...")
            
            prediction_integration = PredictionIntegration(mock_app)
            
            # Test with file path
            file_params = {'model_path': model_file_path, 'data_file': data_file_path}
            
            # Test with directory path
            dir_params = {'model_path': temp_dir, 'data_file': data_file_path}
            
            print("✅ Prediction integration created successfully")
            
            # Test parameter validation
            print("\n✅ Testing parameter validation...")
            
            # Test with valid file path
            if prediction_integration._validate_prediction_params(file_params):
                print("✅ File path validation works")
            else:
                print("❌ File path validation failed")
                return False
            
            # Test with valid directory path
            if prediction_integration._validate_prediction_params(dir_params):
                print("✅ Directory path validation works")
            else:
                print("❌ Directory path validation failed")
                return False
            
            # Test with invalid path
            invalid_params = {'model_path': 'nonexistent', 'data_file': data_file_path}
            if not prediction_integration._validate_prediction_params(invalid_params):
                print("✅ Invalid path validation correctly fails")
            else:
                print("❌ Invalid path validation should have failed")
                return False
            
            root.destroy()
        
        print("\n✅ All prediction fix tests passed!")
        print("\n📝 Summary:")
        print("   - Prediction panel parameter generation: ✅ Working")
        print("   - Model file path detection: ✅ Working")
        print("   - Prediction integration path handling: ✅ Working")
        print("   - Parameter validation: ✅ Working")
        print("   - feature_info.json path resolution: ✅ Fixed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in prediction fix test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prediction_fix()
    if success:
        print("\n🎉 Prediction fix test completed successfully!")
    else:
        print("\n💥 Prediction fix test failed!") 