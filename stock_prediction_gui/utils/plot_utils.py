"""
Plot utilities with colorblind-friendly colors.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np

# Colorblind-friendly color scheme for plots
COLORBLIND_COLORS = [
    '#2E8B57',  # Sea Green
    '#FF8C00',  # Dark Orange
    '#9370DB',  # Medium Purple
    '#20B2AA',  # Light Sea Green
    '#FF6347',  # Tomato
    '#32CD32',  # Lime Green
    '#FFD700',  # Gold
    '#8A2BE2',  # Blue Violet
    '#00CED1',  # Dark Turquoise
    '#FF69B4'   # Hot Pink
]

def setup_colorblind_friendly_plots():
    """Setup matplotlib for colorblind-friendly plotting."""
    # Set the default color cycle
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=COLORBLIND_COLORS)
    
    # Set default colormap
    plt.rcParams['image.cmap'] = 'viridis'  # Good for colorblind users
    
    # Set figure and axes colors
    plt.rcParams['figure.facecolor'] = '#F5F5F5'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.edgecolor'] = '#666666'
    plt.rcParams['axes.labelcolor'] = '#2F2F2F'
    plt.rcParams['xtick.color'] = '#2F2F2F'
    plt.rcParams['ytick.color'] = '#2F2F2F'
    plt.rcParams['text.color'] = '#2F2F2F'

def create_colorblind_friendly_plot(fig, ax, title="", xlabel="", ylabel=""):
    """Create a plot with colorblind-friendly styling."""
    # Apply colorblind-friendly colors
    ax.set_facecolor('#FFFFFF')
    ax.grid(True, alpha=0.3, color='#CCCCCC')
    
    # Set labels with good contrast
    if title:
        ax.set_title(title, color='#2F2F2F', fontsize=12, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, color='#2F2F2F', fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color='#2F2F2F', fontsize=10)
    
    # Style the spines
    for spine in ax.spines.values():
        spine.set_color('#666666')
        spine.set_linewidth(0.8)
    
    return fig, ax

def plot_with_colorblind_colors(ax, x, y, label="", color_index=0, **kwargs):
    """Plot data with colorblind-friendly colors."""
    color = COLORBLIND_COLORS[color_index % len(COLORBLIND_COLORS)]
    return ax.plot(x, y, color=color, label=label, **kwargs)

def create_colorblind_friendly_legend(ax, **kwargs):
    """Create a legend with colorblind-friendly styling."""
    legend = ax.legend(**kwargs)
    legend.get_frame().set_facecolor('#F5F5F5')
    legend.get_frame().set_edgecolor('#CCCCCC')
    return legend 