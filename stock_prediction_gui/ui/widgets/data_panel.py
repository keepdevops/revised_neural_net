"""
Consolidated Data Management Panel for the Stock Prediction GUI.
Provides a clean, organized interface for data loading and feature selection.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging

class DataPanel:
    """Consolidated data management panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create the main panel
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
    
    def create_widgets(self):
        """Create the consolidated panel widgets."""
        # Main title
        title_label = ttk.Label(self.frame, text="Data Management", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Create main container with two columns
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Data Loading
        self.create_left_column(main_container)
        
        # Right column - Feature Selection & Info
        self.create_right_column(main_container)
        
        # Bottom section - Actions
        self.create_bottom_section()
    
    def create_left_column(self, parent):
        """Create the left column for data loading."""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Data File Section
        self.create_data_file_section(left_frame)
        
        # Output Directory Section
        self.create_output_dir_section(left_frame)
        
        # Recent Files Section
        self.create_recent_files_section(left_frame)
    
    def create_right_column(self, parent):
        """Create the right column for feature selection and info."""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Feature Selection Section
        self.create_feature_selection_section(right_frame)
        
        # Data Information Section
        self.create_data_info_section(right_frame)
    
    def create_data_file_section(self, parent):
        """Create the data file selection section."""
        file_frame = ttk.LabelFrame(parent, text="📁 Data File", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection with dropdown
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_select_frame, text="Select Data File:").pack(anchor=tk.W)
        
        # File combobox with history
        self.data_file_var = tk.StringVar()
        self.data_file_combo = ttk.Combobox(
            file_select_frame, 
            textvariable=self.data_file_var,
            width=40,
            state="readonly"
        )
        self.data_file_combo.pack(fill=tk.X, pady=(5, 5))
        self.data_file_combo.bind('<<ComboboxSelected>>', self.on_data_file_select)
        
        # Browse button
        browse_button = ttk.Button(
            file_select_frame, 
            text="Browse Files", 
            command=self.browse_data_file
        )
        browse_button.pack(pady=(5, 0))
        
        # Load button
        load_button = ttk.Button(
            file_select_frame, 
            text="Load Data", 
            command=self.load_data_file,
            style="Accent.TButton"
        )
        load_button.pack(pady=(5, 0))
    
    def create_output_dir_section(self, parent):
        """Create the output directory selection section."""
        output_frame = ttk.LabelFrame(parent, text="�� Output Directory", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Directory selection
        dir_select_frame = ttk.Frame(output_frame)
        dir_select_frame.pack(fill=tk.X)
        
        ttk.Label(dir_select_frame, text="Select Output Directory:").pack(anchor=tk.W)
        
        # Directory combobox with history
        self.output_dir_var = tk.StringVar()
        self.output_dir_combo = ttk.Combobox(
            dir_select_frame, 
            textvariable=self.output_dir_var,
            width=40,
            state="readonly"
        )
        self.output_dir_combo.pack(fill=tk.X, pady=(5, 5))
        self.output_dir_combo.bind('<<ComboboxSelected>>', self.on_output_dir_select)
        
        # Browse button
        browse_dir_button = ttk.Button(
            dir_select_frame, 
            text="Browse Directory", 
            command=self.browse_output_dir
        )
        browse_dir_button.pack(pady=(5, 0))
    
    def create_recent_files_section(self, parent):
        """Create the recent files section."""
        recent_frame = ttk.LabelFrame(parent, text="🕒 Recent Files", padding="10")
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        # Recent files listbox
        self.recent_files_listbox = tk.Listbox(recent_frame, height=6)
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_files_listbox.yview)
        self.recent_files_listbox.configure(yscrollcommand=recent_scrollbar.set)
        
        self.recent_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recent_files_listbox.bind('<Double-Button-1>', self.on_recent_file_select)
        
        # Load recent files
        self.load_recent_files()
    
    def create_feature_selection_section(self, parent):
        """Create the feature selection section."""
        feature_frame = ttk.LabelFrame(parent, text="🎯 Feature Selection", padding="10")
        feature_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input features (X) selection
        input_frame = ttk.Frame(feature_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(input_frame, text="Input Features (X):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Input features listbox with scrollbar
        input_list_frame = ttk.Frame(input_frame)
        input_list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.input_features_listbox = tk.Listbox(
            input_list_frame, 
            height=6, 
            selectmode=tk.MULTIPLE,
            exportselection=0
        )
        input_scrollbar = ttk.Scrollbar(input_list_frame, orient=tk.VERTICAL, command=self.input_features_listbox.yview)
        self.input_features_listbox.configure(yscrollcommand=input_scrollbar.set)
        
        self.input_features_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Target feature (Y) selection
        target_frame = ttk.Frame(feature_frame)
        target_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(target_frame, text="Target Feature (Y):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Target feature combobox
        self.target_feature_var = tk.StringVar()
        self.target_feature_combo = ttk.Combobox(
            target_frame, 
            textvariable=self.target_feature_var,
            width=30,
            state="readonly"
        )
        self.target_feature_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Feature control buttons
        button_frame = ttk.Frame(feature_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Quick action buttons
        quick_frame = ttk.Frame(button_frame)
        quick_frame.pack(fill=tk.X)
        
        default_button = ttk.Button(
            quick_frame, 
            text="Set OHLC", 
            command=self.set_default_features,
            width=12
        )
        default_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = ttk.Button(
            quick_frame, 
            text="Clear All", 
            command=self.clear_feature_selection,
            width=12
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Lock features button
        self.lock_button = ttk.Button(
            button_frame, 
            text="🔒 Lock Features", 
            command=self.lock_features,
            style="Success.TButton"
        )
        self.lock_button.pack(pady=(10, 0))
        
        # Feature status
        self.feature_status_var = tk.StringVar(value="No features selected")
        status_label = ttk.Label(
            feature_frame, 
            textvariable=self.feature_status_var, 
            foreground="blue",
            font=("Arial", 9)
        )
        status_label.pack(pady=(10, 0))
    
    def create_data_info_section(self, parent):
        """Create the data information section."""
        info_frame = ttk.LabelFrame(parent, text="�� Data Information", padding="10")
        info_frame.pack(fill=tk.X)
        
        # Info grid
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        # File info
        ttk.Label(info_grid, text="File Size:").grid(row=0, column=0, sticky="w", pady=2)
        self.file_size_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.file_size_var).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Memory Usage:").grid(row=1, column=0, sticky="w", pady=2)
        self.memory_usage_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.memory_usage_var).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Data Shape:").grid(row=2, column=0, sticky="w", pady=2)
        self.data_shape_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.data_shape_var).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Columns:").grid(row=3, column=0, sticky="w", pady=2)
        self.columns_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.columns_var).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Data Types:").grid(row=4, column=0, sticky="w", pady=2)
        self.dtypes_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.dtypes_var).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=2)
    
    def create_bottom_section(self):
        """Create the bottom action section."""
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to load data")
        status_label = ttk.Label(
            bottom_frame, 
            textvariable=self.status_var,
            font=("Arial", 9),
            foreground="gray"
        )
        status_label.pack(side=tk.LEFT)
        
        # Action buttons
        action_frame = ttk.Frame(bottom_frame)
        action_frame.pack(side=tk.RIGHT)
        
        unlock_button = ttk.Button(
            action_frame, 
            text="🔓 Unlock Features", 
            command=self.unlock_features
        )
        unlock_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        refresh_button = ttk.Button(
            action_frame, 
            text="🔄 Refresh", 
            command=self.refresh_data
        )
        refresh_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    def browse_data_file(self):
        """Browse for data file with enhanced format support."""
        try:
            # Get supported formats from data manager
            formats_info = self.app.data_manager.get_supported_formats_info()
            formats = formats_info['formats']
            
            # Create file type filter
            file_types = []
            for format_name, extensions in formats.items():
                extensions_str = " ".join([f"*{ext}" for ext in extensions])
                file_types.append((f"{format_name} files", extensions_str))
            
            # Add "All supported files" option
            all_extensions = []
            for extensions in formats.values():
                all_extensions.extend(extensions)
            all_extensions_str = " ".join([f"*{ext}" for ext in all_extensions])
            file_types.insert(0, ("All supported files", all_extensions_str))
            
            # Add "All files" option
            file_types.append(("All files", "*.*"))
            
            filename = filedialog.askopenfilename(
                title="Select Data File",
                filetypes=file_types
            )
            
            if filename:
                self.data_file_var.set(filename)
                self.add_to_recent_files(filename)
                self.load_data_file()
                
        except Exception as e:
            self.logger.error(f"Error browsing for file: {e}")
            messagebox.showerror("Error", f"Error browsing for file: {str(e)}")
    
    def browse_output_dir(self):
        """Browse for output directory."""
        try:
            directory = filedialog.askdirectory(title="Select Output Directory")
            if directory:
                self.output_dir_var.set(directory)
                self.add_to_recent_dirs(directory)
                self.app.current_output_dir = directory
                
        except Exception as e:
            self.logger.error(f"Error browsing for directory: {e}")
            messagebox.showerror("Error", f"Error browsing for directory: {str(e)}")
    
    def load_data_file(self):
        """Load the selected data file."""
        try:
            file_path = self.data_file_var.get()
            if not file_path or not os.path.exists(file_path):
                self.status_var.set("No valid file selected")
                return
            
            self.status_var.set("Loading data file...")
            
            # Load data using data manager
            data_info = self.app.data_manager.load_data(file_path)
            
            if data_info:
                # Update data information display
                self.update_data_info(data_info)
                
                # Load columns into feature selectors
                self.load_columns_into_selectors()
                
                # Update app state
                self.app.current_data_file = file_path
                
                self.status_var.set(f"Data loaded successfully: {os.path.basename(file_path)}")
                self.logger.info(f"Data file loaded successfully: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading data file: {e}")
            self.status_var.set(f"Error loading data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load data file: {str(e)}")
    
    def load_columns_into_selectors(self):
        """Load available columns into feature selectors."""
        try:
            # Get current data
            data = self.app.data_manager.get_current_data()
            if data is None:
                return
            
            # Get numeric columns for features
            numeric_columns = list(data.select_dtypes(include=['number']).columns)
            
            # Update input features listbox
            self.input_features_listbox.delete(0, tk.END)
            for col in numeric_columns:
                self.input_features_listbox.insert(tk.END, col)
            
            # Update target feature combobox
            self.target_feature_combo['values'] = numeric_columns
            if numeric_columns:
                self.target_feature_combo.set(numeric_columns[0])
            
            # Update status
            self.feature_status_var.set(f"{len(numeric_columns)} numeric columns available")
            
            self.logger.info(f"Loaded {len(numeric_columns)} columns into selectors")
            
        except Exception as e:
            self.logger.error(f"Error loading columns into selectors: {e}")
    
    def set_default_features(self):
        """Set default OHLC features."""
        try:
            # Default OHLC features
            default_features = ['open', 'high', 'low', 'vol']
            default_target = 'close'
            
            # Select default features in listbox
            self.input_features_listbox.selection_clear(0, tk.END)
            for i, col in enumerate(self.input_features_listbox.get(0, tk.END)):
                if col.lower() in default_features:
                    self.input_features_listbox.selection_set(i)
            
            # Set default target
            if default_target in self.target_feature_combo['values']:
                self.target_feature_combo.set(default_target)
            
            # Update status
            selected_count = len(self.input_features_listbox.curselection())
            self.feature_status_var.set(f"OHLC features selected ({selected_count} input, 1 target)")
            
            self.logger.info("Default OHLC features set")
            
        except Exception as e:
            self.logger.error(f"Error setting default features: {e}")
    
    def clear_feature_selection(self):
        """Clear feature selection."""
        try:
            self.input_features_listbox.selection_clear(0, tk.END)
            self.target_feature_var.set("")
            self.feature_status_var.set("Feature selection cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing feature selection: {e}")
    
    def lock_features(self):
        """Lock the selected features for training."""
        try:
            # Get selected input features
            selected_indices = self.input_features_listbox.curselection()
            selected_features = [self.input_features_listbox.get(i) for i in selected_indices]
            
            # Get target feature
            target_feature = self.target_feature_var.get()
            
            if not selected_features:
                messagebox.showwarning("No Features Selected", "Please select input features first.")
                return
            
            if not target_feature:
                messagebox.showwarning("No Target Selected", "Please select a target feature first.")
                return
            
            # Store selected features in app using the proper setter methods
            self.app.set_selected_features(selected_features)
            self.app.set_selected_target(target_feature)
            
            # Update UI
            self.lock_button.config(text="🔒 Features Locked", state="disabled")
            self.feature_status_var.set(f"Features locked: {len(selected_features)} input, 1 target")
            
            # Disable feature selection
            self.input_features_listbox.config(state="disabled")
            self.target_feature_combo.config(state="disabled")
            
            self.status_var.set("Features locked and ready for training")
            
            self.logger.info(f"Features locked: {selected_features} -> {target_feature}")
            
        except Exception as e:
            self.logger.error(f"Error locking features: {e}")
            messagebox.showerror("Error", f"Failed to lock features: {str(e)}")
    
    def unlock_features(self):
        """Unlock features for editing."""
        try:
            # Clear selected features using the proper setter methods
            self.app.set_selected_features([])
            self.app.set_selected_target(None)
            
            # Update UI
            self.lock_button.config(text="🔒 Lock Features", state="normal")
            self.feature_status_var.set("Features unlocked")
            
            # Enable feature selection
            self.input_features_listbox.config(state="normal")
            self.target_feature_combo.config(state="readonly")
            
            self.status_var.set("Features unlocked for editing")
            
            self.logger.info("Features unlocked")
            
        except Exception as e:
            self.logger.error(f"Error unlocking features: {e}")
    
    def refresh_data(self):
        """Refresh data and feature selection."""
        try:
            if self.app.current_data_file:
                self.load_data_file()
                self.status_var.set("Data refreshed")
            else:
                self.status_var.set("No data file to refresh")
                
        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
    
    def update_data_info(self, data_info):
        """Update data information display."""
        try:
            # Update file info
            if 'file_size' in data_info:
                self.file_size_var.set(data_info['file_size'])
            
            if 'memory_usage' in data_info:
                self.memory_usage_var.set(data_info['memory_usage'])
            
            if 'shape' in data_info:
                rows, cols = data_info['shape']
                self.data_shape_var.set(f"{rows:,} rows × {cols} columns")
            
            if 'numeric_columns' in data_info:
                numeric_cols = data_info['numeric_columns']
                categorical_cols = data_info.get('categorical_columns', [])
                datetime_cols = data_info.get('datetime_columns', [])
                
                total_cols = len(numeric_cols) + len(categorical_cols) + len(datetime_cols)
                col_types = []
                if numeric_cols:
                    col_types.append(f"{len(numeric_cols)} numeric")
                if categorical_cols:
                    col_types.append(f"{len(categorical_cols)} categorical")
                if datetime_cols:
                    col_types.append(f"{len(datetime_cols)} datetime")
                
                self.columns_var.set(f"{total_cols} columns ({', '.join(col_types)})")
            
            if 'data_types' in data_info:
                dtypes = data_info['data_types']
                dtype_str = ', '.join([f"{col}: {dtype}" for col, dtype in list(dtypes.items())[:3]])
                if len(dtypes) > 3:
                    dtype_str += '...'
                self.dtypes_var.set(dtype_str)
                
        except Exception as e:
            self.logger.error(f"Error updating data info: {e}")
    
    def on_data_file_select(self, event=None):
        """Handle data file selection."""
        self.load_data_file()
    
    def on_output_dir_select(self, event=None):
        """Handle output directory selection."""
        directory = self.output_dir_var.get()
        if directory:
            self.app.current_output_dir = directory
    
    def on_recent_file_select(self, event=None):
        """Handle recent file selection."""
        try:
            selection = self.recent_files_listbox.curselection()
            if selection:
                file_path = self.recent_files_listbox.get(selection[0])
                self.data_file_var.set(file_path)
                self.load_data_file()
                
        except Exception as e:
            self.logger.error(f"Error selecting recent file: {e}")
    
    def add_to_recent_files(self, file_path):
        """Add file to recent files list."""
        try:
            # This would integrate with the app's file history system
            pass
        except Exception as e:
            self.logger.error(f"Error adding to recent files: {e}")
    
    def add_to_recent_dirs(self, directory):
        """Add directory to recent directories list."""
        try:
            # This would integrate with the app's directory history system
            pass
        except Exception as e:
            self.logger.error(f"Error adding to recent directories: {e}")
    
    def load_recent_files(self):
        """Load recent files from the app's file history."""
        try:
            if hasattr(self.app, 'file_utils'):
                recent_files = self.app.file_utils.get_recent_files()
                self.recent_files_listbox.delete(0, tk.END)
                
                for file_path in recent_files:
                    if os.path.exists(file_path):
                        # Show just the filename, not the full path
                        filename = os.path.basename(file_path)
                        self.recent_files_listbox.insert(tk.END, filename)
                        # Store the full path as item data
                        self.recent_files_listbox.itemconfig(tk.END, {'bg': 'lightblue'})
                
                # Also load recent directories
                recent_dirs = self.app.file_utils.get_recent_output_dirs()
                self.output_dir_combo['values'] = recent_dirs
            else:
                self.logger.warning("App does not have file_utils attribute")
                
        except Exception as e:
            self.logger.error(f"Error loading recent files: {e}")
    
    def update_recent_files(self, recent_files=None):
        """Update the recent files display."""
        try:
            if recent_files is not None:
                # Update with provided recent files
                self.recent_files_listbox.delete(0, tk.END)
                
                for file_path in recent_files:
                    if os.path.exists(file_path):
                        # Show just the filename, not the full path
                        filename = os.path.basename(file_path)
                        self.recent_files_listbox.insert(tk.END, filename)
                        # Store the full path as item data
                        self.recent_files_listbox.itemconfig(tk.END, {'bg': 'lightblue'})
            else:
                # Load from app's file history
                self.load_recent_files()
                
        except Exception as e:
            self.logger.error(f"Error updating recent files: {e}")
