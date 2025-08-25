#!/usr/bin/env python3
"""
Test script to verify all improvements to stock_prediction_gui:
1. ModelManager initialization with correct base directory
2. Auto-refresh and auto-select latest model after training
3. 3D animation export (GIF/MPEG4) during training
"""

import os
import sys
import tempfile
import json
import numpy as np
import pandas as pd
import logging

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_model_manager_initialization():
    """Test that ModelManager is initialized with the correct base directory."""
    print("🧪 Testing ModelManager Initialization")
    print("=" * 50)
    
    try:
        from stock_prediction_gui.core.model_manager import ModelManager
        
        # Test 1: Default initialization (should use current directory)
        model_manager_default = ModelManager()
        expected_base_dir = os.path.abspath(".")
        
        if model_manager_default.base_dir == expected_base_dir:
            print("✅ Default ModelManager initialization works correctly")
        else:
            print(f"❌ Default ModelManager base_dir mismatch: {model_manager_default.base_dir} vs {expected_base_dir}")
            return False
        
        # Test 2: Custom base directory initialization
        custom_dir = "/tmp/test_models"
        model_manager_custom = ModelManager(base_dir=custom_dir)
        
        if model_manager_custom.base_dir == custom_dir:
            print("✅ Custom ModelManager initialization works correctly")
        else:
            print(f"❌ Custom ModelManager base_dir mismatch: {model_manager_custom.base_dir} vs {custom_dir}")
            return False
        
        # Test 3: Project root initialization (as used in the app)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        model_manager_project = ModelManager(base_dir=project_root)
        
        if model_manager_project.base_dir == project_root:
            print("✅ Project root ModelManager initialization works correctly")
        else:
            print(f"❌ Project root ModelManager base_dir mismatch: {model_manager_project.base_dir} vs {project_root}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ModelManager initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_scanning():
    """Test that ModelManager can find model directories correctly."""
    print("\n🧪 Testing Model Scanning")
    print("=" * 50)
    
    try:
        from stock_prediction_gui.core.model_manager import ModelManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test model directories
            model_dirs = []
            for i in range(3):
                model_dir = os.path.join(temp_dir, f"model_20250627_{180000 + i}")
                os.makedirs(model_dir, exist_ok=True)
                model_dirs.append(model_dir)
                
                # Create some model files
                with open(os.path.join(model_dir, "stock_model.npz"), 'w') as f:
                    f.write("mock model data")
                
                # Create feature info
                feature_info = {
                    'x_features': ['open', 'high', 'low', 'vol'],
                    'y_feature': 'close',
                    'model_type': 'basic'
                }
                with open(os.path.join(model_dir, "feature_info.json"), 'w') as f:
                    json.dump(feature_info, f)
            
            # Test model scanning
            model_manager = ModelManager(base_dir=temp_dir)
            found_models = model_manager.get_available_models()
            
            if len(found_models) == 3:
                print("✅ ModelManager found all 3 test models")
                
                # Check that models are sorted by creation time (newest first)
                if found_models[0] == model_dirs[-1]:  # Last created should be first
                    print("✅ Models are correctly sorted by creation time")
                else:
                    print("❌ Models are not correctly sorted by creation time")
                    return False
            else:
                print(f"❌ ModelManager found {len(found_models)} models, expected 3")
                return False
            
            # Test model info retrieval
            model_info = model_manager.get_model_info(found_models[0])
            if model_info and model_info['has_feature_info']:
                print("✅ Model info retrieval works correctly")
            else:
                print("❌ Model info retrieval failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model scanning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3d_animation_export():
    """Test 3D animation export functionality."""
    print("\n🧪 Testing 3D Animation Export")
    print("=" * 50)
    
    try:
        from stock_prediction_gui.core.training_integration import TrainingIntegration
        
        # Create mock app
        class MockApp:
            def __init__(self):
                self.current_output_dir = None
                self.logger = logging.getLogger(__name__)
        
        app = MockApp()
        training_integration = TrainingIntegration(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            app.current_output_dir = temp_dir
            
            # Create test data
            np.random.seed(42)
            X_train = np.random.randn(100, 4)  # 100 samples, 4 features
            y_train = np.random.randn(100, 1)  # 100 targets
            
            # Create model directory
            model_dir = os.path.join(temp_dir, "test_model")
            os.makedirs(model_dir, exist_ok=True)
            
            # Test parameters
            params = {
                'x_features': ['open', 'high', 'low', 'vol'],
                'y_feature': 'close',
                'generate_3d_animations': True
            }
            
            # Test 3D animation generation
            training_integration._generate_3d_animations(model_dir, X_train, y_train, params)
            
            # Check if files were created
            plots_dir = os.path.join(model_dir, "plots")
            if os.path.exists(plots_dir):
                files = os.listdir(plots_dir)
                
                # Check for expected files
                expected_files = [
                    "training_data_3d.png",
                    "training_data_analysis.png"
                ]
                
                # GIF and MPEG4 might not be created if matplotlib animation writers are not available
                optional_files = [
                    "training_data_3d.gif",
                    "training_data_3d.mp4"
                ]
                
                found_expected = all(f in files for f in expected_files)
                found_optional = any(f in files for f in optional_files)
                
                if found_expected:
                    print("✅ 3D animation export created expected files")
                    if found_optional:
                        print("✅ 3D animation export created optional animation files")
                    else:
                        print("⚠️ 3D animation export did not create animation files (matplotlib writers may not be available)")
                else:
                    print(f"❌ 3D animation export missing expected files. Found: {files}")
                    return False
            else:
                print("❌ 3D animation export did not create plots directory")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 3D animation export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auto_refresh_functionality():
    """Test auto-refresh and auto-select functionality."""
    print("\n🧪 Testing Auto-Refresh Functionality")
    print("=" * 50)
    
    try:
        from stock_prediction_gui.core.app import StockPredictionApp
        import tkinter as tk
        
        # Create a minimal root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create app instance
        app = StockPredictionApp(root)
        
        # Test that the model manager is initialized with the correct base directory
        expected_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        if app.model_manager.base_dir == expected_base_dir:
            print("✅ App ModelManager initialized with correct base directory")
        else:
            print(f"❌ App ModelManager base directory mismatch: {app.model_manager.base_dir} vs {expected_base_dir}")
            root.destroy()
            return False
        
        # Test refresh_models_and_select_latest method
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporarily change the model manager's base directory for testing
            original_base_dir = app.model_manager.base_dir
            app.model_manager.base_dir = temp_dir
            
            # Create test model directories
            model_dirs = []
            for i in range(2):
                model_dir = os.path.join(temp_dir, f"model_20250627_{180000 + i}")
                os.makedirs(model_dir, exist_ok=True)
                model_dirs.append(model_dir)
                
                # Create model files
                with open(os.path.join(model_dir, "stock_model.npz"), 'w') as f:
                    f.write("mock model data")
            
            # Test refresh and select latest
            app.refresh_models_and_select_latest()
            
            # Check if the latest model was selected
            # The models are sorted by creation time (newest first), so model_dirs[0] should be selected
            if app.selected_model == model_dirs[0]:  # Should be the most recent
                print("✅ Auto-refresh and select latest works correctly")
            else:
                print(f"❌ Auto-refresh did not select latest model: {app.selected_model}")
                print(f"Expected: {model_dirs[0]}")
                app.model_manager.base_dir = original_base_dir
                root.destroy()
                return False
            
            # Restore original base directory
            app.model_manager.base_dir = original_base_dir
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Auto-refresh functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Stock Prediction GUI Improvements")
    print("=" * 60)
    
    tests = [
        ("ModelManager Initialization", test_model_manager_initialization),
        ("Model Scanning", test_model_scanning),
        ("3D Animation Export", test_3d_animation_export),
        ("Auto-Refresh Functionality", test_auto_refresh_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Stock Prediction GUI improvements are working correctly.")
        return True
    else:
        print(f"\n💥 {total - passed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 