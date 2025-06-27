#!/usr/bin/env python3
"""
Fix the column loading issue in the modular GUI.
"""

import os

def fix_column_loading():
    """Fix the column loading issue by updating the app's load_data_file method."""
    
    app_file = "stock_prediction_gui/core/app.py"
    
    if not os.path.exists(app_file):
        print(f"❌ App file not found: {app_file}")
        return False
    
    print("🔧 Fixing column loading in app.py...")
    
    # Read the current app.py file
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Find the load_data_file method and add the missing column loading
    old_method = '''    def load_data_file(self, file_path):
        """Load a data file."""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return False
            
            # Add to file history
            self.file_utils.add_data_file(file_path)
            
            # Load data using data manager
            success = self.data_manager.load_data(file_path)
            
            if success:
                self.current_data_file = file_path
                self.main_window.update_status(f"Data file loaded: {os.path.basename(file_path)}")
                
                # Update data panel
                data_info = self.data_manager.get_data_info()
                self.main_window.data_panel.update_data_info(data_info)
                
                return True
            else:
                messagebox.showerror("Error", "Failed to load data file")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading data file: {e}")
            messagebox.showerror("Error", f"Failed to load data file: {e}")
            return False'''
    
    new_method = '''    def load_data_file(self, file_path):
        """Load a data file."""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return False
            
            # Add to file history
            self.file_utils.add_data_file(file_path)
            
            # Load data using data manager
            data_info = self.data_manager.load_data(file_path)
            
            if data_info:
                self.current_data_file = file_path
                self.main_window.update_status(f"Data file loaded: {os.path.basename(file_path)}")
                
                # Update data panel
                self.main_window.data_panel.update_data_info(data_info)
                
                # Load columns into feature selectors
                self.load_columns_into_selectors()
                
                return True
            else:
                messagebox.showerror("Error", "Failed to load data file")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading data file: {e}")
            messagebox.showerror("Error", f"Failed to load data file: {e}")
            return False'''
    
    # Replace the old method with the new one
    if old_method in content:
        content = content.replace(old_method, new_method)
        
        # Add the new load_columns_into_selectors method
        new_method_to_add = '''
    def load_columns_into_selectors(self):
        """Load available columns into feature selectors."""
        try:
            # Get current data
            data = self.data_manager.get_current_data()
            if data is None:
                return
            
            # Get numeric columns for features
            numeric_columns = list(data.select_dtypes(include=['number']).columns)
            
            # Update feature selectors in data panel
            if hasattr(self.main_window, 'data_panel') and hasattr(self.main_window.data_panel, 'update_feature_options'):
                self.main_window.data_panel.update_feature_options(numeric_columns, numeric_columns)
                self.logger.info(f"Loaded {len(numeric_columns)} columns into feature selectors")
            else:
                self.logger.warning("Data panel or update_feature_options method not found")
                
        except Exception as e:
            self.logger.error(f"Error loading columns into selectors: {e}")'''
        
        # Add the new method before the last method in the class
        if 'def select_output_directory' in content:
            content = content.replace(
                '    def select_output_directory(self, directory):',
                new_method_to_add + '\n\n    def select_output_directory(self, directory):'
            )
        
        # Write the updated content
        with open(app_file, 'w') as f:
            f.write(content)
        
        print("✅ Column loading fixed in app.py")
        return True
    else:
        print("❌ Could not find load_data_file method to update")
        return False

def fix_data_panel_column_selection():
    """Fix the column selection section in data panel."""
    
    data_panel_file = "stock_prediction_gui/ui/widgets/data_panel.py"
    
    if not os.path.exists(data_panel_file):
        print(f"❌ Data panel file not found: {data_panel_file}")
        return False
    
    print("🔧 Fixing column selection section in data panel...")
    
    # Read the current data panel file
    with open(data_panel_file, 'r') as f:
        content = f.read()
    
    # Find and fix the column selection section
    old_column_section = '''    def create_column_selection_section(self):
        """Create column selection section."""
        # Column selection frame
        column_frame = ttk.LabelFrame(self.frame, text="Feature Selection", padding="10")
        column_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input features (X) selection
        input_frame = ttk.Frame(column_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Input Features (X):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Input features listbox
        input_list_frame = ttk.Frame(input_frame)
        input_list_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_features_listbox = tk.Listbox(
            input_list_frame, 
            height=4, 
            selectmode=tk.MULTIPLE,
            exportselection=0
        )
        input_scrollbar = ttk.Scrollbar(input_list_frame, orient=tk.VERTICAL, command=self.input_features_listbox.yview)
        self.input_features_listbox.configure(yscrollcommand=input_scrollbar.set)
        
        self.input_features_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Target feature (Y) selection
        target_frame = ttk.Frame(column_frame)
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
        button_frame = ttk.Frame(column_frame)
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
            column_frame, 
            textvariable=self.feature_status_var, 
            foreground="blue",
            font=("Arial", 9)
        )
        status_label.pack(pady=(10, 0))'''
    
    new_column_section = '''    def create_column_selection_section(self):
        """Create column selection section."""
        # Column selection frame
        column_frame = ttk.LabelFrame(self.frame, text="Feature Selection", padding="10")
        column_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input features (X) selection
        input_frame = ttk.Frame(column_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Input Features (X):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Input features listbox
        input_list_frame = ttk.Frame(input_frame)
        input_list_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.feature_listbox = tk.Listbox(
            input_list_frame, 
            height=4, 
            selectmode=tk.MULTIPLE,
            exportselection=0
        )
        input_scrollbar = ttk.Scrollbar(input_list_frame, orient=tk.VERTICAL, command=self.feature_listbox.yview)
        self.feature_listbox.configure(yscrollcommand=input_scrollbar.set)
        
        self.feature_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Target feature (Y) selection
        target_frame = ttk.Frame(column_frame)
        target_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(target_frame, text="Target Feature (Y):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Target feature combobox
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(
            target_frame, 
            textvariable=self.target_var,
            width=30,
            state="readonly"
        )
        self.target_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Feature control buttons
        button_frame = ttk.Frame(column_frame)
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
            command=self.clear_all_features,
            width=12
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Lock features button
        self.lock_button = ttk.Button(
            button_frame, 
            text="🔒 Lock Features", 
            command=self.lock_column_selection,
            style="Success.TButton"
        )
        self.lock_button.pack(pady=(10, 0))
        
        # Feature status
        self.column_status_var = tk.StringVar(value="No features selected")
        status_label = ttk.Label(
            column_frame, 
            textvariable=self.column_status_var, 
            foreground="blue",
            font=("Arial", 9)
        )
        status_label.pack(pady=(10, 0))'''
    
    # Replace the old section with the new one
    if old_column_section in content:
        content = content.replace(old_column_section, new_column_section)
        
        # Write the updated content
        with open(data_panel_file, 'w') as f:
            f.write(content)
        
        print("✅ Column selection section fixed in data panel")
        return True
    else:
        print("❌ Could not find column selection section to update")
        return False

def main():
    """Main function to fix column loading issues."""
    print("🔧 Fixing column loading issues...")
    
    success1 = fix_column_loading()
    success2 = fix_data_panel_column_selection()
    
    if success1 and success2:
        print("\n🎉 Column loading issues fixed successfully!")
        print("The modular GUI now supports:")
        print("✅ Automatic column loading when data is loaded")
        print("✅ Input Features (X) - Multi-select listbox")
        print("✅ Target Feature (Y) - Dropdown selection")
        print("✅ Default OHLC feature selection")
        print("✅ Feature locking for training")
        print("\nRestart the modular GUI to see the changes:")
        print("cd stock_prediction_gui && PYTHONPATH=.. python main.py")
    else:
        print("\n❌ Failed to fix some column loading issues.")

if __name__ == "__main__":
    main() 