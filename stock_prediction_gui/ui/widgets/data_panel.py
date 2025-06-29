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
        
        # Load history after all widgets are created
        self.load_all_history()
    
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
        """Create the recent files section with format filtering."""
        recent_frame = ttk.LabelFrame(parent, text="🕒 Recent Files", padding="10")
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        # Format filter frame
        filter_frame = ttk.Frame(recent_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by format:").pack(side=tk.LEFT)
        
        # Format filter combobox
        self.format_filter_var = tk.StringVar(value="All Formats")
        self.format_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.format_filter_var,
            width=15,
            state="readonly"
        )
        self.format_filter_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.format_filter_combo.bind('<<ComboboxSelected>>', self.on_format_filter_change)
        
        # Clear filter button
        clear_filter_button = ttk.Button(
            filter_frame,
            text="Clear Filter",
            command=self.clear_format_filter
        )
        clear_filter_button.pack(side=tk.RIGHT)
        
        # Recent files listbox with format info
        listbox_frame = ttk.Frame(recent_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.recent_files_listbox = tk.Listbox(listbox_frame, height=6)
        recent_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.recent_files_listbox.yview)
        self.recent_files_listbox.configure(yscrollcommand=recent_scrollbar.set)
        
        self.recent_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recent_files_listbox.bind('<Double-Button-1>', self.on_recent_file_select)
        
        # File info label
        self.file_info_label = ttk.Label(recent_frame, text="", font=("Arial", 9))
        self.file_info_label.pack(fill=tk.X, pady=(5, 0))
        
        # Bind selection change to show file info
        self.recent_files_listbox.bind('<<ListboxSelect>>', self.on_file_selection_change)
    
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
        """Create the data information section with format-specific details."""
        info_frame = ttk.LabelFrame(parent, text="📊 Data Information", padding="10")
        info_frame.pack(fill=tk.X)
        
        # Info grid
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        # File format and basic info
        ttk.Label(info_grid, text="File Format:").grid(row=0, column=0, sticky="w", pady=2)
        self.file_format_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.file_format_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="File Size:").grid(row=1, column=0, sticky="w", pady=2)
        self.file_size_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.file_size_var).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Memory Usage:").grid(row=2, column=0, sticky="w", pady=2)
        self.memory_usage_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.memory_usage_var).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Data structure info
        ttk.Label(info_grid, text="Data Shape:").grid(row=3, column=0, sticky="w", pady=2)
        self.data_shape_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.data_shape_var).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Columns:").grid(row=4, column=0, sticky="w", pady=2)
        self.columns_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.columns_var).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Data Types:").grid(row=5, column=0, sticky="w", pady=2)
        self.dtypes_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.dtypes_var).grid(row=5, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Format-specific info
        ttk.Label(info_grid, text="Format Details:").grid(row=6, column=0, sticky="w", pady=2)
        self.format_details_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.format_details_var, font=("Arial", 9)).grid(row=6, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Last accessed info
        ttk.Label(info_grid, text="Last Accessed:").grid(row=7, column=0, sticky="w", pady=2)
        self.last_accessed_var = tk.StringVar(value="Not loaded")
        ttk.Label(info_grid, textvariable=self.last_accessed_var, font=("Arial", 9)).grid(row=7, column=1, sticky="w", padx=(10, 0), pady=2)
    
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
        
        # Save as JSON button
        save_json_button = ttk.Button(
            action_frame, 
            text="💾 Save as JSON", 
            command=self.save_as_json
        )
        save_json_button.pack(side=tk.RIGHT, padx=(5, 0))
        
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
        """Refresh the current data."""
        try:
            if self.app.current_data_file:
                self.load_data_file()
            else:
                self.status_var.set("No data file loaded")
        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
    
    def save_as_json(self):
        """Save current data as JSON file."""
        try:
            # Get current data
            data = self.app.data_manager.get_current_data()
            if data is None:
                messagebox.showwarning("No Data", "No data loaded to save.")
                return
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                title="Save as JSON",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
            
            if not filename:
                return
            
            # Ask user for JSON format options
            format_dialog = JSONFormatDialog(self.parent, filename)
            if format_dialog.result:
                orient, indent = format_dialog.result
                
                # Save the data
                success = self.app.data_manager.save_as_json(
                    data, 
                    filename, 
                    orient=orient, 
                    indent=indent
                )
                
                if success:
                    self.status_var.set(f"Data saved as JSON: {os.path.basename(filename)}")
                    messagebox.showinfo("Success", f"Data saved successfully to:\n{filename}")
                else:
                    messagebox.showerror("Error", "Failed to save JSON file.")
            
        except Exception as e:
            self.logger.error(f"Error saving as JSON: {e}")
            messagebox.showerror("Error", f"Error saving JSON file: {str(e)}")
    
    def update_data_info(self, data_info):
        """Update the data information display with enhanced format-specific details."""
        try:
            if not data_info:
                self.file_size_var.set("No data loaded")
                self.memory_usage_var.set("No data loaded")
                self.data_shape_var.set("No data loaded")
                self.columns_var.set("No data loaded")
                self.dtypes_var.set("No data loaded")
                self.file_format_var.set("Not loaded")
                self.format_details_var.set("Not loaded")
                self.last_accessed_var.set("Not loaded")
                return
            
            # Get file path for format detection
            file_path = data_info.get('file_path', '')
            
            # Update file format information
            if hasattr(self.app, 'file_utils') and file_path:
                file_info = self.app.file_utils.get_file_info(file_path)
                if file_info:
                    self.file_format_var.set(file_info['format'])
                    
                    # Set format-specific details
                    format_details = self.get_format_specific_details(file_info, data_info)
                    self.format_details_var.set(format_details)
                    
                    # Set last accessed time
                    if file_info['last_accessed'] != 'Unknown':
                        try:
                            last_accessed = file_info['last_accessed'][:10]  # Just the date part
                            self.last_accessed_var.set(last_accessed)
                        except:
                            self.last_accessed_var.set("Unknown")
                    else:
                        self.last_accessed_var.set("Unknown")
            
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
            
            # Log format-specific information
            self.log_format_specific_info(data_info)
            
        except Exception as e:
            self.logger.error(f"Error updating data info: {e}")
            self.file_size_var.set("Error")
            self.memory_usage_var.set("Error")
            self.data_shape_var.set("Error")
            self.columns_var.set("Error")
            self.dtypes_var.set("Error")
            self.file_format_var.set("Error")
            self.format_details_var.set("Error")
            self.last_accessed_var.set("Error")
    
    def get_format_specific_details(self, file_info, data_info):
        """Get format-specific details for display."""
        try:
            format_type = file_info['format']
            details = []
            
            if format_type == 'JSON':
                # JSON-specific details
                if data_info.get('file_path', '').endswith('.json'):
                    json_info = self.app.data_manager.get_json_info(data_info.get('file_path'))
                    if json_info:
                        details.append(f"Structure: {json_info.get('structure_type', 'Unknown')}")
                        details.append(f"Format: {json_info.get('format_type', 'Unknown')}")
                        if json_info.get('format_type') == 'json_lines':
                            details.append(f"Lines: {json_info.get('valid_json_lines', 0)} valid")
            
            elif format_type == 'Feather':
                # Feather-specific details
                if hasattr(self.app.data_manager, 'feather_metadata'):
                    feather_info = self.app.data_manager.feather_metadata
                    details.append(f"Schema: {len(feather_info.get('column_names', []))} columns")
                    details.append(f"Rows: {feather_info.get('num_rows', 0):,}")
            
            elif format_type == 'Parquet':
                # Parquet-specific details
                details.append("Columnar format")
                details.append("Compressed storage")
            
            elif format_type == 'HDF5':
                # HDF5-specific details
                details.append("Hierarchical format")
                details.append("Multiple datasets")
            
            elif format_type == 'DuckDB':
                # DuckDB-specific details
                details.append("SQL database")
                details.append("Columnar storage")
            
            elif format_type == 'SQLite':
                # SQLite-specific details
                details.append("SQL database")
                details.append("Single file")
            
            elif format_type == 'Excel':
                # Excel-specific details
                details.append("Spreadsheet format")
                details.append("Multiple sheets")
            
            elif format_type == 'CSV':
                # CSV-specific details
                details.append("Text format")
                details.append("Comma-separated")
            
            elif format_type == 'Pickle':
                # Pickle-specific details
                details.append("Python serialization")
                details.append("Binary format")
            
            elif format_type == 'NumPy':
                # NumPy-specific details
                details.append("Array format")
                details.append("Binary storage")
            
            else:
                details.append("Standard format")
            
            return ' | '.join(details) if details else "Standard format"
            
        except Exception as e:
            self.logger.error(f"Error getting format-specific details: {e}")
            return "Format details unavailable"
    
    def log_format_specific_info(self, data_info):
        """Log format-specific information for debugging."""
        try:
            file_path = data_info.get('file_path', '')
            
            # Log JSON-specific information if it's a JSON file
            if file_path.endswith('.json'):
                json_info = self.app.data_manager.get_json_info(file_path)
                if json_info:
                    self.logger.info(f"JSON Structure: {json_info.get('structure_type')}")
                    self.logger.info(f"JSON Format: {json_info.get('format_type')}")
                    if json_info.get('format_type') == 'json_lines':
                        self.logger.info(f"JSON Lines: {json_info.get('valid_json_lines')} valid, {json_info.get('invalid_lines')} invalid")
            
            # Log Feather-specific information
            elif file_path.endswith(('.feather', '.ftr', '.arrow')):
                if hasattr(self.app.data_manager, 'feather_metadata'):
                    feather_info = self.app.data_manager.feather_metadata
                    self.logger.info(f"Feather Schema: {len(feather_info.get('column_names', []))} columns")
                    self.logger.info(f"Feather Rows: {feather_info.get('num_rows', 0):,}")
            
            # Log other format information
            else:
                format_type = self.app.file_utils.get_file_format(file_path) if hasattr(self.app, 'file_utils') else "Unknown"
                self.logger.info(f"File Format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error logging format-specific info: {e}")
    
    def on_data_file_select(self, event=None):
        """Handle data file selection."""
        self.load_data_file()
    
    def on_output_dir_select(self, event=None):
        """Handle output directory selection."""
        directory = self.output_dir_var.get()
        if directory:
            self.app.current_output_dir = directory
    
    def on_recent_file_select(self, event=None):
        """Handle recent file selection with enhanced file info."""
        try:
            selection = self.recent_files_listbox.curselection()
            if selection:
                selected_item = self.recent_files_listbox.get(selection[0])
                
                # Get the actual file path from file info cache
                if hasattr(self, 'file_info_cache') and selected_item in self.file_info_cache:
                    file_path = self.file_info_cache[selected_item]['path']
                else:
                    # Fallback to old method
                    file_path = selected_item
                
                if os.path.exists(file_path):
                    self.data_file_var.set(file_path)
                    self.load_data_file()
                    self.logger.info(f"Selected recent file: {file_path}")
                else:
                    messagebox.showwarning("File Not Found", f"The file {file_path} no longer exists.")
                    # Remove from display
                    self.update_recent_files_display(self.format_filter_var.get())
                    
        except Exception as e:
            self.logger.error(f"Error selecting recent file: {e}")
    
    def add_to_recent_files(self, file_path):
        """Add file to recent files list with format tracking."""
        try:
            if hasattr(self.app, 'file_utils') and file_path:
                # Add to file utils history (now includes format tracking)
                self.app.file_utils.add_data_file(file_path)
                
                # Update the data file combobox
                recent_files = self.app.file_utils.get_recent_data_files()
                self.data_file_combo['values'] = recent_files
                
                # Update format filter options
                self.load_format_filter_options()
                
                # Update recent files display with current filter
                current_filter = self.format_filter_var.get()
                self.update_recent_files_display(current_filter)
                
                self.logger.info(f"Added file to history: {file_path}")
            else:
                self.logger.warning("App does not have file_utils attribute or no file path provided")
        except Exception as e:
            self.logger.error(f"Error adding to recent files: {e}")
    
    def add_to_recent_dirs(self, directory):
        """Add directory to recent directories list."""
        try:
            if hasattr(self.app, 'file_utils') and directory:
                # Add to file utils history
                self.app.file_utils.add_output_dir(directory)
                
                # Update the output directory combobox
                recent_dirs = self.app.file_utils.get_recent_output_dirs()
                self.output_dir_combo['values'] = recent_dirs
                
                self.logger.info(f"Added directory to history: {directory}")
            else:
                self.logger.warning("App does not have file_utils attribute or no directory provided")
        except Exception as e:
            self.logger.error(f"Error adding to recent directories: {e}")
    
    def load_recent_files(self):
        """Load recent files from the app's file history with format filtering."""
        try:
            if hasattr(self.app, 'file_utils'):
                # Load format filter options
                self.load_format_filter_options()
                
                # Load recent files for the listbox
                self.update_recent_files_display()
                
                # Load recent data files for the data file combobox
                recent_data_files = self.app.file_utils.get_recent_data_files()
                self.data_file_combo['values'] = recent_data_files
                
                # Load recent directories for the output directory combobox
                recent_dirs = self.app.file_utils.get_recent_output_dirs()
                self.output_dir_combo['values'] = recent_dirs
                
                self.logger.info(f"Loaded {len(recent_data_files)} data files and {len(recent_dirs)} directories from history")
            else:
                self.logger.warning("App does not have file_utils attribute")
                
        except Exception as e:
            self.logger.error(f"Error loading recent files: {e}")
    
    def load_format_filter_options(self):
        """Load format filter options from supported formats."""
        try:
            if hasattr(self.app, 'file_utils'):
                # Get format statistics
                format_stats = self.app.file_utils.get_format_statistics()
                supported_formats = self.app.file_utils.get_supported_formats_list()
                
                # Create filter options
                filter_options = ["All Formats"]
                for format_name in supported_formats.keys():
                    count = format_stats.get(format_name, {}).get('count', 0)
                    if count > 0:
                        filter_options.append(f"{format_name} ({count})")
                
                self.format_filter_combo['values'] = filter_options
                
        except Exception as e:
            self.logger.error(f"Error loading format filter options: {e}")
    
    def update_recent_files_display(self, format_filter=None):
        """Update the recent files display with optional format filtering."""
        try:
            if not hasattr(self.app, 'file_utils'):
                return
            
            # Clear current display
            self.recent_files_listbox.delete(0, tk.END)
            
            # Get files based on filter
            if format_filter and format_filter != "All Formats":
                # Extract format name from filter string (e.g., "CSV (5)" -> "CSV")
                format_name = format_filter.split(' (')[0]
                files = self.app.file_utils.get_recent_files_by_format(format_name)
            else:
                files = self.app.file_utils.get_recent_files_by_format()
            
            # Display files with format information
            for file_path in files:
                if os.path.exists(file_path):
                    file_info = self.app.file_utils.get_file_info(file_path)
                    if file_info:
                        # Show filename with format indicator
                        display_name = f"{file_info['name']} [{file_info['format']}]"
                        self.recent_files_listbox.insert(tk.END, display_name)
                        
                        # Store full path as item data
                        self.recent_files_listbox.itemconfig(tk.END, {'bg': 'lightblue'})
                        
                        # Store file info for later use
                        if not hasattr(self, 'file_info_cache'):
                            self.file_info_cache = {}
                        self.file_info_cache[display_name] = file_info
            
        except Exception as e:
            self.logger.error(f"Error updating recent files display: {e}")
    
    def on_format_filter_change(self, event=None):
        """Handle format filter change."""
        try:
            selected_filter = self.format_filter_var.get()
            self.update_recent_files_display(selected_filter)
            self.logger.info(f"Format filter changed to: {selected_filter}")
        except Exception as e:
            self.logger.error(f"Error changing format filter: {e}")
    
    def clear_format_filter(self):
        """Clear the format filter."""
        try:
            self.format_filter_var.set("All Formats")
            self.update_recent_files_display()
            self.logger.info("Format filter cleared")
        except Exception as e:
            self.logger.error(f"Error clearing format filter: {e}")
    
    def on_file_selection_change(self, event=None):
        """Handle file selection change to show file information."""
        try:
            selection = self.recent_files_listbox.curselection()
            if selection and hasattr(self, 'file_info_cache'):
                selected_item = self.recent_files_listbox.get(selection[0])
                file_info = self.file_info_cache.get(selected_item)
                
                if file_info:
                    info_text = f"Size: {file_info['size']} | Format: {file_info['format']} | Modified: {file_info['modified'][:10]}"
                    self.file_info_label.config(text=info_text)
                else:
                    self.file_info_label.config(text="")
            else:
                self.file_info_label.config(text="")
                
        except Exception as e:
            self.logger.error(f"Error handling file selection change: {e}")
    
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
                # Load from app's file history with current filter
                current_filter = self.format_filter_var.get()
                self.update_recent_files_display(current_filter)
                
        except Exception as e:
            self.logger.error(f"Error updating recent files: {e}")
    
    def load_all_history(self):
        """Load all history after all widgets are created."""
        try:
            self.load_recent_files()
        except Exception as e:
            self.logger.error(f"Error loading all history: {e}")


class JSONFormatDialog:
    """Dialog for selecting JSON format options."""
    
    def __init__(self, parent, filename):
        self.parent = parent
        self.filename = filename
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("JSON Format Options")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the dialog widgets."""
        # Title
        title_label = ttk.Label(self.dialog, text="JSON Format Options", font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 10))
        
        # File info
        file_label = ttk.Label(self.dialog, text=f"File: {os.path.basename(self.filename)}", font=("Arial", 10))
        file_label.pack(pady=(0, 20))
        
        # Format options frame
        options_frame = ttk.LabelFrame(self.dialog, text="Format Options", padding="15")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Orientation selection
        ttk.Label(options_frame, text="Orientation:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.orient_var = tk.StringVar(value="records")
        orient_frame = ttk.Frame(options_frame)
        orient_frame.pack(fill=tk.X, pady=(0, 15))
        
        orientations = [
            ("Records (array of objects)", "records"),
            ("Columns (object with arrays)", "columns"),
            ("Index (object with arrays)", "index"),
            ("Values (array of values)", "values"),
            ("Split (object with arrays)", "split"),
            ("Table (object with arrays)", "table")
        ]
        
        for text, value in orientations:
            ttk.Radiobutton(
                orient_frame, 
                text=text, 
                variable=self.orient_var, 
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        # Indentation selection
        ttk.Label(options_frame, text="Indentation:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.indent_var = tk.IntVar(value=2)
        indent_frame = ttk.Frame(options_frame)
        indent_frame.pack(fill=tk.X, pady=(0, 15))
        
        indent_options = [
            ("None (compact)", 0),
            ("2 spaces", 2),
            ("4 spaces", 4),
            ("8 spaces", 8)
        ]
        
        for text, value in indent_options:
            ttk.Radiobutton(
                indent_frame, 
                text=text, 
                variable=self.indent_var, 
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(
            button_frame, 
            text="Save", 
            command=self.save,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.cancel
        ).pack(side=tk.RIGHT)
    
    def save(self):
        """Save with selected options."""
        self.result = (self.orient_var.get(), self.indent_var.get())
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()
