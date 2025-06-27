import matplotlib.pyplot as plt

def plot_wireframe(ax, X, Y, Z, color='blue', alpha=0.7, linewidth=0.5, rstride=1, cstride=1, **kwargs):
    """
    Draw a 3D wireframe plot on the given axes.
    Args:
        ax: Matplotlib 3D axis
        X, Y, Z: Meshgrid data
        color: Wireframe color
        alpha: Transparency
        linewidth: Line width
        rstride, cstride: Stride arguments for wireframe
        **kwargs: Additional arguments for plot_wireframe
    """
    ax.clear()
    ax.plot_wireframe(X, Y, Z, color=color, alpha=alpha, linewidth=linewidth, rstride=rstride, cstride=cstride, **kwargs)
    ax.set_title("3D Wireframe Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
