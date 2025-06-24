#!/usr/bin/env python3
"""
Test matplotlib 3D plotting functionality.
"""

import matplotlib
matplotlib.use('TkAgg')  # Set backend explicitly
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def test_3d_plotting():
    """Test basic 3D plotting functionality."""
    print("🧪 Testing matplotlib 3D plotting...")
    
    try:
        # Create a simple 3D plot
        fig = plt.Figure(figsize=(8, 6))
        print(f"✅ Figure created: {fig}")
        
        ax = fig.add_subplot(111, projection='3d')
        print(f"✅ 3D axes created: {ax}")
        print(f"✅ 3D axes type: {type(ax)}")
        print(f"✅ Has view_init: {hasattr(ax, 'view_init')}")
        
        # Test basic 3D plotting
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        
        ax.plot_surface(X, Y, Z, cmap='viridis')
        print("✅ 3D surface plot created")
        
        # Test view manipulation
        ax.view_init(elev=30, azim=45)
        print("✅ View initialized")
        
        print("✅ All 3D plotting tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in 3D plotting test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_3d_plotting() 