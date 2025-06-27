"""
Colorblind-friendly color scheme for the Stock Prediction GUI.
Uses colors that are distinguishable for people with various types of colorblindness.
"""

# Colorblind-friendly color palette
# Avoids red/blue combinations that are problematic for colorblind users

class ColorScheme:
    """Colorblind-friendly color scheme."""
    
    # Primary colors (distinguishable for most colorblind users)
    PRIMARY = "#2E8B57"      # Sea Green - good for colorblind users
    SECONDARY = "#FF8C00"    # Dark Orange - distinguishable from green
    ACCENT = "#9370DB"       # Medium Purple - distinct from green/orange
    
    # Success/Error colors (colorblind-friendly alternatives)
    SUCCESS = "#228B22"      # Forest Green - instead of red
    WARNING = "#FFA500"      # Orange - instead of yellow
    ERROR = "#8B4513"        # Saddle Brown - instead of red
    INFO = "#4682B4"         # Steel Blue - instead of blue
    
    # Background colors
    BG_PRIMARY = "#F5F5F5"   # Light Gray
    BG_SECONDARY = "#FFFFFF" # White
    BG_ACCENT = "#E8F5E8"    # Light Green
    
    # Text colors
    TEXT_PRIMARY = "#2F2F2F" # Dark Gray
    TEXT_SECONDARY = "#666666" # Medium Gray
    TEXT_LIGHT = "#999999"   # Light Gray
    
    # Chart colors (colorblind-friendly)
    CHART_COLORS = [
        "#2E8B57",  # Sea Green
        "#FF8C00",  # Dark Orange  
        "#9370DB",  # Medium Purple
        "#20B2AA",  # Light Sea Green
        "#FF6347",  # Tomato (orange-red, distinguishable)
        "#32CD32",  # Lime Green
        "#FFD700",  # Gold
        "#8A2BE2",  # Blue Violet
        "#00CED1",  # Dark Turquoise
        "#FF69B4"   # Hot Pink
    ]
    
    # Status colors
    STATUS_RUNNING = "#FF8C00"    # Orange
    STATUS_SUCCESS = "#228B22"    # Green
    STATUS_ERROR = "#8B4513"      # Brown
    STATUS_WAITING = "#4682B4"    # Steel Blue
    
    @classmethod
    def get_chart_color(cls, index):
        """Get a chart color by index."""
        return cls.CHART_COLORS[index % len(cls.CHART_COLORS)]
    
    @classmethod
    def apply_theme(cls, root):
        """Apply the colorblind-friendly theme to a tkinter root."""
        style = ttk.Style()
        
        # Configure styles with colorblind-friendly colors
        style.configure("TFrame", background=cls.BG_PRIMARY)
        style.configure("TLabel", background=cls.BG_PRIMARY, foreground=cls.TEXT_PRIMARY)
        style.configure("TButton", background=cls.PRIMARY, foreground="white")
        style.configure("Accent.TButton", background=cls.SECONDARY, foreground="white")
        style.configure("Success.TButton", background=cls.SUCCESS, foreground="white")
        style.configure("Warning.TButton", background=cls.WARNING, foreground="black")
        style.configure("Error.TButton", background=cls.ERROR, foreground="white")
        
        # Configure notebook tabs
        style.configure("TNotebook", background=cls.BG_PRIMARY)
        style.configure("TNotebook.Tab", background=cls.BG_SECONDARY, foreground=cls.TEXT_PRIMARY)
        style.map("TNotebook.Tab", 
                 background=[("selected", cls.PRIMARY), ("active", cls.BG_ACCENT)])
        
        # Configure entry fields
        style.configure("TEntry", fieldbackground=cls.BG_SECONDARY, foreground=cls.TEXT_PRIMARY)
        
        # Configure combobox
        style.configure("TCombobox", fieldbackground=cls.BG_SECONDARY, foreground=cls.TEXT_PRIMARY)
        
        # Configure progress bar
        style.configure("TProgressbar", background=cls.PRIMARY, troughcolor=cls.BG_SECONDARY) 