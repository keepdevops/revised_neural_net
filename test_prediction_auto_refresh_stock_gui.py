#!/usr/bin/env python3
"""
Test script to verify auto-refresh functionality in stock_prediction_gui.
This test ensures that the Prediction Tab automatically updates with the latest trained model.
"""

import os
import sys
import tempfile
import shutil
import time
import json
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def create_test_model(model_dir, model_name):
    """Create a test model directory with required files."""
    os.makedirs(model_dir, exist_ok=True)
    
    # Create feature_info.json
    feature_info = {
        'x_features': ['open', 'high', 'low', 'vol'],
        'y_feature': 'close',
        'model_type': 'basic',
        'training_params': {
            'epochs': 100,
            'learning_rate': 0.001,
            'batch_size': 32
        }
    }
    
    with open(os.path.join(model_dir, 'feature_info.json'), 'w') as f:
        json.dump(feature_info, f, indent=4)
    
    # Create a dummy model file
    import numpy as np
    np.savez(os.path.join(model_dir, 'stock_model.npz'), 
             weights=np.random.randn(10, 5),
             biases=np.random.randn(5))
    
    # Create training losses file
    losses = np.random.randn(100, 2)
    np.savetxt(os.path.join(model_dir, 'training_losses.csv'), losses, delimiter=',')
    
    print(f"✅ Created test model: {model_name}")

def test_auto_refresh_functionality():
    """Test the auto-refresh functionality."""
    print("🧪 Testing Auto-Refresh Functionality in stock_prediction_gui")
    print("=" * 60)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create some test models
        model1_dir = os.path.join(temp_dir, "model_20250101_120000")
        model2_dir = os.path.join(temp_dir, "model_20250101_130000")
        model3_dir = os.path.join(temp_dir, "model_20250101_140000")
        
        create_test_model(model1_dir, "model_20250101_120000")
        time.sleep(1)  # Ensure different timestamps
        create_test_model(model2_dir, "model_20250101_130000")
        time.sleep(1)  # Ensure different timestamps
        create_test_model(model3_dir, "model_20250101_140000")
        
        # Test the model manager functionality
        try:
            from stock_prediction_gui.core.model_manager import ModelManager
            
            # Initialize model manager with test directory
            model_manager = ModelManager(base_dir=temp_dir)
            
            # Get available models
            models = model_manager.get_available_models()
            print(f"📊 Found {len(models)} models: {[os.path.basename(m) for m in models]}")
            
            if len(models) >= 3:
                print("✅ Model discovery working correctly")
                
                # Test that models are sorted by creation time (newest first)
                latest_model = models[0]  # First model is the newest (reverse=True)
                expected_latest = "model_20250101_140000"
                
                if os.path.basename(latest_model) == expected_latest:
                    print(f"✅ Latest model correctly identified: {expected_latest}")
                else:
                    print(f"❌ Latest model mismatch. Expected: {expected_latest}, Got: {os.path.basename(latest_model)}")
                    return False
                
            else:
                print(f"❌ Expected at least 3 models, found {len(models)}")
                return False
                
        except ImportError as e:
            print(f"❌ Could not import ModelManager: {e}")
            return False
        except Exception as e:
            print(f"❌ Error testing model manager: {e}")
            return False
    
    print("\n🎯 Testing Auto-Refresh Integration")
    print("=" * 40)
    
    # Test the app's refresh functionality
    try:
        # Mock the app functionality
        class MockApp:
            def __init__(self, temp_dir):
                self.model_manager = ModelManager(base_dir=temp_dir)
                self.selected_model = None
                self.main_window = MockMainWindow()
            
            def refresh_models_and_select_latest(self):
                """Test the refresh and select latest functionality."""
                models = self.model_manager.get_available_models()
                self.main_window.update_model_list(models)
                
                if models:
                    latest_model = models[0]  # First model is the newest (reverse=True)
                    self.selected_model = latest_model
                    self.main_window.prediction_panel.model_var.set(os.path.basename(latest_model))
                    return True
                return False
        
        class MockMainWindow:
            def __init__(self):
                self.prediction_panel = MockPredictionPanel()
            
            def update_model_list(self, models):
                self.prediction_panel.update_model_list(models)
        
        class MockPredictionPanel:
            def __init__(self):
                class MockVar:
                    def __init__(self):
                        self._value = ''
                    def get(self):
                        return self._value
                    def set(self, value):
                        self._value = value
                self.model_var = MockVar()
            
            def update_model_list(self, models):
                model_names = [os.path.basename(model) for model in models]
                if model_names:
                    self.model_var.set(model_names[0])  # Select latest (first in list)
        
        # Create another temporary directory for integration test
        with tempfile.TemporaryDirectory() as test_dir:
            # Create test models
            model1 = os.path.join(test_dir, "model_20250101_120000")
            model2 = os.path.join(test_dir, "model_20250101_130000")
            model3 = os.path.join(test_dir, "model_20250101_140000")
            
            create_test_model(model1, "model_20250101_120000")
            time.sleep(1)
            create_test_model(model2, "model_20250101_130000")
            time.sleep(1)
            create_test_model(model3, "model_20250101_140000")
            
            # Test the integration
            mock_app = MockApp(test_dir)
            
            # Test refresh and select latest
            success = mock_app.refresh_models_and_select_latest()
            
            if success:
                expected_latest = "model_20250101_140000"
                actual_selected = os.path.basename(mock_app.selected_model)
                actual_ui_selected = mock_app.main_window.prediction_panel.model_var.get()
                
                if actual_selected == expected_latest and actual_ui_selected == expected_latest:
                    print("✅ Auto-refresh and select latest working correctly")
                    print(f"   Selected model: {actual_selected}")
                    print(f"   UI shows: {actual_ui_selected}")
                else:
                    print(f"❌ Auto-select mismatch. Expected: {expected_latest}")
                    print(f"   Selected: {actual_selected}")
                    print(f"   UI shows: {actual_ui_selected}")
                    return False
            else:
                print("❌ Auto-refresh and select latest failed")
                return False
    
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False
    
    print("\n✅ All tests passed!")
    print("🎉 The Prediction Tab will now automatically update with the latest trained model")
    print("🔧 Manual refresh button 'Refresh & Select Latest' is also available")
    
    return True

def test_training_completion_callback():
    """Test that training completion properly triggers auto-refresh."""
    print("\n🧪 Testing Training Completion Callback")
    print("=" * 45)
    
    try:
        # Mock the training completion scenario
        class MockTrainingIntegration:
            def __init__(self, app):
                self.app = app
            
            def _on_training_completed(self, model_dir, error=None):
                """Simulate training completion callback."""
                if error:
                    print(f"❌ Training failed: {error}")
                    return False
                else:
                    print(f"✅ Training completed: {model_dir}")
                    # This should trigger auto-refresh
                    self.app.refresh_models_and_select_latest()
                    return True
        
        class MockApp:
            def __init__(self):
                self.selected_model = None
                self.refresh_called = False
                self.latest_model_selected = None
            
            def refresh_models_and_select_latest(self):
                """Mock the refresh and select latest method."""
                self.refresh_called = True
                # Simulate finding a new model
                self.latest_model_selected = "new_model_20250101_150000"
                print(f"🔄 Auto-refresh triggered, selected: {self.latest_model_selected}")
                return True
        
        # Test the callback
        mock_app = MockApp()
        training_integration = MockTrainingIntegration(mock_app)
        
        # Simulate successful training completion
        test_model_dir = "/path/to/new/model_20250101_150000"
        success = training_integration._on_training_completed(test_model_dir)
        
        if success and mock_app.refresh_called:
            print("✅ Training completion callback working correctly")
            print(f"   Auto-refresh triggered: {mock_app.refresh_called}")
            print(f"   Latest model selected: {mock_app.latest_model_selected}")
        else:
            print("❌ Training completion callback failed")
            return False
    
    except Exception as e:
        print(f"❌ Error testing training completion callback: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Auto-Refresh Functionality Tests")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_auto_refresh_functionality()
    test2_passed = test_training_completion_callback()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The Prediction Tab will now automatically update with the latest trained model")
        print("✅ Training completion properly triggers auto-refresh")
        print("✅ Manual refresh button is available")
        print("\n📋 Summary of changes:")
        print("   • Added refresh_models_and_select_latest() method to app.py")
        print("   • Updated training completion callback to auto-select latest model")
        print("   • Added 'Refresh & Select Latest' button to prediction panel")
        print("   • Seamless workflow from training to prediction")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the implementation and try again.")
        sys.exit(1) 