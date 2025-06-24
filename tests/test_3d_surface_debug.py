#!/usr/bin/env python3
"""
Test to debug 3D surface visibility in gradient descent visualization.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gradient_descent_3d import GradientDescentVisualizer, compute_loss_surface

def test_3d_surface_visibility():
    """Test if the 3D surface is being created and is visible."""
    print("🧪 Testing 3D surface visibility...")
    
    # Find a model directory
    model_dirs = [d for d in os.listdir('.') if d.startswith('model_')]
    if not model_dirs:
        print("❌ No model directories found")
        return False
    
    model_dir = sorted(model_dirs)[-1]  # Use most recent
    print(f"📁 Using model directory: {model_dir}")
    
    try:
        # Create visualizer
        visualizer = GradientDescentVisualizer(
            model_dir=model_dir,
            w1_range=(-2, 2),
            w2_range=(-2, 2),
            n_points=30,
            surface_alpha=0.8,  # Increase alpha for better visibility
            color='viridis'
        )
        
        print("✅ Visualizer created successfully")
        
        # Check if surface data exists
        print(f"📊 Surface data shapes:")
        print(f"   W1: {visualizer.W1.shape}")
        print(f"   W2: {visualizer.W2.shape}")
        print(f"   Z: {visualizer.Z.shape}")
        
        # Check surface values
        print(f"📈 Surface value statistics:")
        print(f"   Z min: {np.min(visualizer.Z):.6f}")
        print(f"   Z max: {np.max(visualizer.Z):.6f}")
        print(f"   Z mean: {np.mean(visualizer.Z):.6f}")
        print(f"   Z std: {np.std(visualizer.Z):.6f}")
        
        # Check if surface has variation
        if np.std(visualizer.Z) < 1e-10:
            print("⚠️  Warning: Surface has very little variation (appears flat)")
        else:
            print("✅ Surface has good variation")
        
        # Check if surface object exists
        if hasattr(visualizer, 'surface') and visualizer.surface is not None:
            print("✅ Surface object created")
        else:
            print("❌ Surface object not found")
        
        # Test surface computation directly
        print("\n🔍 Testing surface computation directly...")
        X_test = np.random.randn(50, 2).astype(np.float64)
        y_test = np.random.randn(50, 1).astype(np.float64)
        
        W1_test, W2_test, Z_test = compute_loss_surface(X_test, y_test, (-2, 2), (-2, 2), 20)
        
        print(f"📊 Test surface statistics:")
        print(f"   Z min: {np.min(Z_test):.6f}")
        print(f"   Z max: {np.max(Z_test):.6f}")
        print(f"   Z mean: {np.mean(Z_test):.6f}")
        print(f"   Z std: {np.std(Z_test):.6f}")
        
        # Create a simple test plot
        print("\n🎨 Creating test plot...")
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot surface with different settings
        surface = ax.plot_surface(W1_test, W2_test, Z_test, 
                                cmap='viridis', alpha=0.8, linewidth=0.5)
        
        ax.set_xlabel('Weight 1')
        ax.set_ylabel('Weight 2')
        ax.set_zlabel('Loss')
        ax.set_title('Test 3D Loss Surface')
        
        # Add colorbar
        fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
        
        # Save test plot
        test_plot_path = 'test_3d_surface.png'
        plt.savefig(test_plot_path, dpi=150, bbox_inches='tight')
        print(f"✅ Test plot saved: {test_plot_path}")
        
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing 3D surface: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_3d_surface_visibility()
    if success:
        print("\n✅ 3D surface test completed successfully")
    else:
        print("\n❌ 3D surface test failed") 