#!/usr/bin/env python3
"""
Wireframe 3D Plot Module

This module provides wireframe visualization functionality for 3D plots.
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

def plot_wireframe(ax, X, Y, Z, color='viridis', alpha=0.7, linewidth=0.5, rstride=1, cstride=1, **kwargs):
    """
    Draw a 3D wireframe plot on the given axes.
    
    Args:
        ax: Matplotlib 3D axis
        X, Y, Z: Meshgrid data
        color: Wireframe color or colormap name
        alpha: Transparency
        linewidth: Line width
        rstride: Row stride for wireframe
        cstride: Column stride for wireframe
        **kwargs: Additional arguments passed to plot_wireframe
    """
    try:
        # Check if color is a valid colormap
        valid_colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'coolwarm', 'RdBu_r', 'Reds', 'Blues', 'Greens']
        
        if color in valid_colormaps:
            # Use colormap for wireframe - simpler approach
            wireframe = ax.plot_wireframe(X, Y, Z, 
                                         cmap=color,
                                         alpha=alpha, 
                                         linewidth=linewidth,
                                         rstride=rstride, 
                                         cstride=cstride, 
                                         **kwargs)
        else:
            # Use solid color
            wireframe = ax.plot_wireframe(X, Y, Z, 
                                         color=color, 
                                         alpha=alpha, 
                                         linewidth=linewidth,
                                         rstride=rstride, 
                                         cstride=cstride, 
                                         **kwargs)
        
        # Set labels and title
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'3D Wireframe Plot - {color}')
        
        # Add grid
        ax.grid(True)
        
        return wireframe
        
    except Exception as e:
        print(f"Error creating wireframe plot: {e}")
        # Fallback to basic wireframe
        ax.plot_wireframe(X, Y, Z, color='red', alpha=0.5)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Wireframe Plot (Fallback)')

def create_sample_wireframe(ax, resolution=30, x_range=(-5, 5), y_range=(-5, 5)):
    """
    Create a sample wireframe plot for testing.
    
    Args:
        ax: Matplotlib 3D axis
        resolution: Grid resolution
        x_range: X-axis range
        y_range: Y-axis range
    """
    try:
        # Create meshgrid
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)
        
        # Create Z values (example function)
        Z = np.sin(np.sqrt(X**2 + Y**2))
        
        # Plot wireframe
        plot_wireframe(ax, X, Y, Z)
        
    except Exception as e:
        print(f"Error creating sample wireframe: {e}")

if __name__ == "__main__":
    # Test the module
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    create_sample_wireframe(ax)
    plt.show() 