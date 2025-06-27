import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from gui.components.grid_matplotlib_toolbar import GridMatplotlibToolbar
from gui.theme import *

class DisplayPanel:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.frame = ttk.LabelFrame(master, text="Results", padding="10")
        self.setup_ui()

    def setup_ui(self):
        """Create the right display panel for plots and results (now using grid)"""
        # Configure grid weights
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Create notebook for different displays
        self.app.display_notebook = ttk.Notebook(self.frame)
        self.app.display_notebook.grid(row=0, column=0, sticky="nsew")
        
        self.create_training_results_tab()
        self.create_prediction_results_tab()
        # Removed Live Training and 3D Gradient Descent tabs from Results Panel
        # self.create_gradient_descent_tab()
        # self.create_3d_gradient_descent_tab()
        self.create_plots_tab()
        self.create_saved_plots_tab()
        self.create_live_training_plot_tab()

    def create_training_results_tab(self):
        # Training Results Tab
        train_results_frame = ttk.Frame(self.app.display_notebook)
        self.app.display_notebook.add(train_results_frame, text="Training Results")
        train_results_frame.grid_columnconfigure(0, weight=1)
        train_results_frame.grid_rowconfigure(0, weight=0)  # Controls
        train_results_frame.grid_rowconfigure(1, weight=1)  # Plot canvas
        train_results_frame.grid_rowconfigure(2, weight=0)  # Log frame
        train_results_frame.grid_rowconfigure(3, weight=0)  # Toolbar
        
        # Add controls frame for training results
        train_controls_frame = ttk.Frame(train_results_frame)
        train_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        train_controls_frame.grid_columnconfigure(0, weight=1)
        
        # Add refresh button for training results
        self.app.refresh_train_btn = ttk.Button(train_controls_frame, text="🔄 Refresh Training Results", 
                                          command=self.app.refresh_training_results)
        self.app.refresh_train_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Add status label for training results
        self.app.train_status_label = ttk.Label(train_controls_frame, text="Training results will appear here", 
                                          foreground=TEXT_COLOR, background=FRAME_COLOR)
        self.app.train_status_label.grid(row=1, column=0, padx=5, pady=5)
        
        # Create matplotlib figure for training results
        self.app.results_fig = plt.Figure(figsize=(8, 4))
        self.app.results_ax = self.app.results_fig.add_subplot(111)
        
        # Create canvas and embed in the tab using grid
        self.app.results_canvas = FigureCanvasTkAgg(self.app.results_fig, train_results_frame)
        self.app.results_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        
        # Add live training log text widget
        log_frame = ttk.LabelFrame(train_results_frame, text="Live Training Log", padding="5")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar for live training messages
        self.app.training_log_text = tk.Text(log_frame, height=8, bg="#222222", fg="#CCCCCC", 
                                        font=("Consolas", 9), state="disabled")
        self.app.training_log_text.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Add scrollbar for the text widget
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.app.training_log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.app.training_log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Add toolbar using grid
        toolbar = GridMatplotlibToolbar(self.app.results_canvas, train_results_frame)
        toolbar.grid(row=3, column=0, sticky="ew")
        
        # Initialize with a placeholder plot
        self.app.results_ax.text(0.5, 0.5, 'Training results will appear here', 
                            ha='center', va='center', transform=self.app.results_ax.transAxes,
                            fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        self.app.results_ax.set_title("Training Results")
        
        try:
            self.app.results_canvas.draw_idle()
        except Exception as canvas_error:
            print(f"Canvas update error in training results initialization: {canvas_error}")
        
        print("Training Results tab created successfully")

    def create_prediction_results_tab(self):
        # Prediction Results Tab
        pred_results_frame = ttk.Frame(self.app.display_notebook)
        self.app.display_notebook.add(pred_results_frame, text="Prediction Results")
        pred_results_frame.grid_columnconfigure(0, weight=1)
        pred_results_frame.grid_rowconfigure(0, weight=0)  # Controls
        pred_results_frame.grid_rowconfigure(1, weight=1)  # Plot canvas
        pred_results_frame.grid_rowconfigure(2, weight=0)  # Data table
        pred_results_frame.grid_rowconfigure(3, weight=0)  # Toolbar
        
        # Add controls frame for prediction results
        pred_controls_frame = ttk.Frame(pred_results_frame)
        pred_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        pred_controls_frame.grid_columnconfigure(0, weight=1)
        
        # Add refresh button for prediction results
        self.app.refresh_pred_btn = ttk.Button(pred_controls_frame, text="🔄 Refresh Prediction Results", 
                                          command=self.app.update_prediction_results)
        self.app.refresh_pred_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Add status label for prediction results
        self.app.pred_status_label = ttk.Label(pred_controls_frame, text="Select a model to view prediction results", 
                                          foreground=TEXT_COLOR, background=FRAME_COLOR)
        self.app.pred_status_label.grid(row=1, column=0, padx=5, pady=5)
        
        # Create figure for prediction plot
        self.app.pred_fig = plt.Figure(figsize=(8, 4), dpi=100)
        self.app.pred_ax = self.app.pred_fig.add_subplot(111)
        self.app.pred_canvas = FigureCanvasTkAgg(self.app.pred_fig, master=pred_results_frame)
        self.app.pred_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        
        # Add data table frame
        data_table_frame = ttk.LabelFrame(pred_results_frame, text="Prediction Data", padding="5")
        data_table_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        data_table_frame.grid_columnconfigure(0, weight=1)
        data_table_frame.grid_rowconfigure(0, weight=1)
        
        # Create treeview for data display
        self.app.pred_tree = ttk.Treeview(data_table_frame, height=6, show="headings")
        self.app.pred_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Add scrollbar for treeview
        pred_tree_scrollbar = ttk.Scrollbar(data_table_frame, orient="vertical", command=self.app.pred_tree.yview)
        pred_tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.app.pred_tree.configure(yscrollcommand=pred_tree_scrollbar.set)
        
        # Add horizontal scrollbar for treeview
        pred_tree_h_scrollbar = ttk.Scrollbar(data_table_frame, orient="horizontal", command=self.app.pred_tree.xview)
        pred_tree_h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.app.pred_tree.configure(xscrollcommand=pred_tree_h_scrollbar.set)
        
        # Add toolbar for prediction results
        pred_toolbar = GridMatplotlibToolbar(self.app.pred_canvas, pred_results_frame)
        pred_toolbar.grid(row=3, column=0, sticky="ew")
        
        # Initialize with a placeholder plot
        self.app.pred_ax.text(0.5, 0.5, 'Select a model and data file to view predictions', 
                         ha='center', va='center', transform=self.app.pred_ax.transAxes,
                         fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        self.app.pred_ax.set_title("Prediction Results")
        self.app.pred_ax.axis('off')
        
        try:
            self.app.pred_canvas.draw_idle()
        except Exception as canvas_error:
            print(f"Canvas update error in prediction results initialization: {canvas_error}")
        
        print("Prediction Results tab created successfully")

    def create_plots_tab(self):
        # Plots Tab
        plots_frame = ttk.Frame(self.app.display_notebook)
        self.app.display_notebook.add(plots_frame, text="Plots")
        plots_frame.grid_columnconfigure(0, weight=1)
        plots_frame.grid_rowconfigure(0, weight=1)
        
        # Create matplotlib figure for plots
        self.app.plots_fig = plt.Figure(figsize=(8, 6))
        self.app.plots_ax = self.app.plots_fig.add_subplot(111)
        
        # Create canvas and embed in the tab using grid
        self.app.plots_canvas = FigureCanvasTkAgg(self.app.plots_fig, plots_frame)
        self.app.plots_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Add toolbar using grid
        toolbar = GridMatplotlibToolbar(self.app.plots_canvas, plots_frame)
        
        # Initialize with a placeholder plot
        self.app.plots_ax.text(0.5, 0.5, 'Model plots will appear here', 
                          ha='center', va='center', transform=self.app.plots_ax.transAxes,
                          fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        self.app.plots_ax.set_title("Model Plots")
        
        try:
            self.app.plots_canvas.draw_idle()
        except Exception as canvas_error:
            print(f"Canvas update error in plots initialization: {canvas_error}")

    def create_saved_plots_tab(self):
        # Saved Plots Tab (New)
        saved_plots_frame = ttk.Frame(self.app.display_notebook)
        self.app.display_notebook.add(saved_plots_frame, text="Saved Plots")
        saved_plots_frame.grid_columnconfigure(0, weight=1)
        saved_plots_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable canvas for images using grid
        self.app.saved_plots_canvas = tk.Canvas(saved_plots_frame, bg=FRAME_COLOR)
        self.app.saved_plots_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar using grid
        scrollbar = ttk.Scrollbar(saved_plots_frame, orient="vertical", command=self.app.saved_plots_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.app.saved_plots_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas to hold images
        self.app.saved_plots_inner_frame = ttk.Frame(self.app.saved_plots_canvas)
        self.app.saved_plots_canvas.create_window((0, 0), window=self.app.saved_plots_inner_frame, anchor="nw")
        
        # Placeholder label using grid
        self.app.saved_plots_placeholder = ttk.Label(self.app.saved_plots_inner_frame, 
                                                text="Select a model to view saved plots", 
                                                foreground=TEXT_COLOR, background=FRAME_COLOR)
        self.app.saved_plots_placeholder.grid(row=0, column=0, pady=20)
        
        # Bind canvas resizing
        self.app.saved_plots_inner_frame.bind("<Configure>", lambda e: self.app.saved_plots_canvas.configure(
            scrollregion=self.app.saved_plots_canvas.bbox("all")))
        
        print("Saved Plots tab created successfully")

    def create_live_training_plot_tab(self):
        # Live Training Plot Tab (New)
        live_plot_frame = ttk.Frame(self.app.display_notebook)
        self.app.display_notebook.add(live_plot_frame, text="Live Training Plot")
        live_plot_frame.grid_columnconfigure(0, weight=1)
        live_plot_frame.grid_rowconfigure(1, weight=1)  # Row 1 for the plot
        
        # Create frame for live plot controls
        live_controls_frame = ttk.Frame(live_plot_frame)
        live_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        live_controls_frame.grid_columnconfigure(0, weight=1)
        live_controls_frame.grid_columnconfigure(1, weight=1)
        
        # Add live training status label
        self.app.live_training_status = ttk.Label(live_controls_frame, 
                                                text="Live training plot ready", 
                                                foreground=TEXT_COLOR, background=FRAME_COLOR)
        self.app.live_training_status.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Add refresh button for live training plot
        self.app.refresh_live_plot_btn = ttk.Button(live_controls_frame, text="🔄 Refresh Live Plot", 
                                              command=self.app.refresh_live_training_plot)
        self.app.refresh_live_plot_btn.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        
        # Create matplotlib figure for live training plot
        self.app.live_training_fig = plt.Figure(figsize=(8, 6))
        self.app.live_training_ax = self.app.live_training_fig.add_subplot(111)
        
        # Create canvas and embed in the tab using grid
        self.app.live_training_canvas = FigureCanvasTkAgg(self.app.live_training_fig, live_plot_frame)
        self.app.live_training_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        
        # Add toolbar using grid
        live_toolbar = GridMatplotlibToolbar(self.app.live_training_canvas, live_plot_frame)
        live_toolbar.grid(row=2, column=0, sticky="ew")
        
        # Initialize with a placeholder plot
        self.app.live_training_ax.text(0.5, 0.5, 'Live training progress will appear here\nStart training to see real-time updates', 
                                  ha='center', va='center', transform=self.app.live_training_ax.transAxes,
                                  fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
        self.app.live_training_ax.set_title("Live Training Progress")
        self.app.live_training_ax.set_xlabel("Epoch")
        self.app.live_training_ax.set_ylabel("Loss")
        self.app.live_training_ax.grid(True, alpha=0.3)
        
        try:
            self.app.live_training_canvas.draw_idle()
        except Exception as canvas_error:
            print(f"Canvas update error in live training plot initialization: {canvas_error}")
        
        print("Live Training Plot tab created successfully") 