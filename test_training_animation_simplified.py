#!/usr/bin/env python3
"""
Test script to verify simplified training animation generation (GIF and PNG only).
"""

import os
import sys
import tempfile
import numpy as np

def test_simplified_training_animation():
    """Test the simplified training animation generation."""
    print("🧪 Testing simplified training animation generation...")
    
    try:
        # Add the project root to the Python path
        project_root = os.path.abspath(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Import the training integration
        from stock_prediction_gui.core.training_integration import TrainingIntegration
        
        print("✅ Training integration imported successfully")
        
        # Create a mock training integration instance
        class MockApp:
            def __init__(self):
                self.logger = type('MockLogger', (), {
                    'info': lambda self, msg: print(f"   INFO: {msg}"),
                    'warning': lambda self, msg: print(f"   WARNING: {msg}"),
                    'error': lambda self, msg: print(f"   ERROR: {msg}")
                })()
        
        mock_app = MockApp()
        training_integration = TrainingIntegration(mock_app)
        
        print("✅ Training integration instance created")
        
        # Test the simplified animation generation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock training data
            X_train = np.random.randn(100, 3)
            y_train = np.random.randn(100, 1)
            params = {
                'x_features': ['Feature 1', 'Feature 2', 'Feature 3'],
                'y_feature': 'Target',
                'generate_3d_animations': True
            }
            
            # Create plots directory
            plots_dir = os.path.join(temp_dir, "plots")
            os.makedirs(plots_dir, exist_ok=True)
            
            print("   Testing simplified 3D animation generation...")
            
            # Call the _generate_3d_animations method
            training_integration._generate_3d_animations(temp_dir, X_train, y_train, params)
            
            # Check if files were created
            gif_file = os.path.join(plots_dir, "training_data_3d.gif")
            png_file = os.path.join(plots_dir, "training_data_3d.png")
            analysis_file = os.path.join(plots_dir, "training_data_analysis.png")
            
            results = {
                'gif': os.path.exists(gif_file),
                'png': os.path.exists(png_file),
                'analysis': os.path.exists(analysis_file)
            }
            
            print(f"   Results:")
            print(f"   - GIF: {'✅' if results['gif'] else '❌'}")
            print(f"   - PNG: {'✅' if results['png'] else '❌'}")
            print(f"   - Analysis: {'✅' if results['analysis'] else '❌'}")
            
            # Check file sizes
            if results['gif']:
                gif_size = os.path.getsize(gif_file)
                print(f"   - GIF size: {gif_size:,} bytes")
            
            if results['png']:
                png_size = os.path.getsize(png_file)
                print(f"   - PNG size: {png_size:,} bytes")
            
            if results['analysis']:
                analysis_size = os.path.getsize(analysis_file)
                print(f"   - Analysis size: {analysis_size:,} bytes")
            
            return results
            
    except ImportError as e:
        print(f"❌ Could not import training integration: {e}")
        return None
    except Exception as e:
        print(f"❌ Error testing training integration: {e}")
        return None

def test_floating_window_simplified():
    """Test that the floating 3D window no longer has MPEG4 export option."""
    print("\n🧪 Testing floating 3D window simplified controls...")
    
    try:
        # Import the floating 3D window
        from stock_prediction_gui.ui.windows.floating_3d_window import Floating3DWindow
        
        print("✅ Floating 3D window imported successfully")
        
        # Check if the save_animation_mp4 method has been removed
        if hasattr(Floating3DWindow, 'save_animation_mp4'):
            print("❌ save_animation_mp4 method still exists")
            return False
        else:
            print("✅ save_animation_mp4 method has been removed")
        
        # Check if save_animation_gif method still exists
        if hasattr(Floating3DWindow, 'save_animation_gif'):
            print("✅ save_animation_gif method still exists")
            return True
        else:
            print("❌ save_animation_gif method is missing")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import floating 3D window: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing floating window: {e}")
        return False

def main():
    """Run all simplified animation tests."""
    print("Testing simplified training animation generation...")
    print("=" * 60)
    
    # Test 1: Simplified training animation
    training_results = test_simplified_training_animation()
    
    # Test 2: Floating window simplified
    floating_ok = test_floating_window_simplified()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    if training_results:
        print(f"training integration:")
        print(f"  - GIF export: {'✅ PASS' if training_results['gif'] else '❌ FAIL'}")
        print(f"  - PNG export: {'✅ PASS' if training_results['png'] else '❌ FAIL'}")
        print(f"  - Analysis export: {'✅ PASS' if training_results['analysis'] else '❌ FAIL'}")
    else:
        print(f"training integration: ❌ FAIL")
    
    print(f"floating window simplified: {'✅ PASS' if floating_ok else '❌ FAIL'}")
    
    # Overall result
    all_tests_passed = (training_results and all(training_results.values()) and floating_ok)
    
    if all_tests_passed:
        print("\n🎉 All tests passed! Simplified animation generation is working.")
        print("Training will now generate:")
        print("- GIF animation (web-friendly, smaller size)")
        print("- Static PNG plot (high quality)")
        print("- 2D analysis plots (feature correlations)")
        print("\nNo more MPEG4 export issues or ffmpeg dependencies!")
    else:
        print("\n⚠️  Some tests failed. Animation generation may not work properly.")
    
    return all_tests_passed

if __name__ == "__main__":
    main() 