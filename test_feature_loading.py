#!/usr/bin/env python3
"""
Test script to debug feature loading issue in the Data Selection tab.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
import pandas as pd

# Add the gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from main_gui import StockPredictionGUI

def test_feature_loading():
    """Test the feature loading functionality."""
    print("🧪 Testing feature loading functionality...")
    
    try:
        root = tk.Tk()
        root.title("Feature Loading Test")
        root.geometry("1200x800")
        
        # Create the GUI application
        app = StockPredictionGUI(root)
        
        print("✅ GUI created successfully")
        
        # Check if widgets exist
        print("🔍 Checking widget existence...")
        
        if hasattr(app, 'feature_listbox'):
            print("✅ feature_listbox exists")
        else:
            print("❌ feature_listbox does not exist")
            
        if hasattr(app, 'target_combo'):
            print("✅ target_combo exists")
        else:
            print("❌ target_combo does not exist")
            
        if hasattr(app, 'data_file_var'):
            print("✅ data_file_var exists")
        else:
            print("❌ data_file_var does not exist")
        
        # Check if there are any CSV files available
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        print(f"📁 Found {len(csv_files)} CSV files: {csv_files}")
        
        if csv_files:
            # Test with the first CSV file
            test_file = csv_files[0]
            print(f"🧪 Testing with file: {test_file}")
            
            # Try to load the file directly with pandas
            try:
                df = pd.read_csv(test_file)
                print(f"✅ Successfully loaded {test_file} with pandas")
                print(f"📊 File has {len(df.columns)} columns: {list(df.columns)}")
                
                # Test the load_data_features method directly
                app.data_file = test_file
                app.data_file_var.set(test_file)
                
                print("🔄 Calling load_data_features()...")
                app.load_data_features()
                
                print(f"📋 Feature list: {app.feature_list}")
                
                # Check if widgets were updated
                if hasattr(app, 'feature_listbox') and app.feature_listbox:
                    try:
                        feature_count = app.feature_listbox.size()
                        print(f"✅ Feature listbox updated with {feature_count} features")
                        
                        # Get the first few features
                        features = []
                        for i in range(min(5, feature_count)):
                            features.append(app.feature_listbox.get(i))
                        print(f"📋 First few features: {features}")
                        
                    except Exception as e:
                        print(f"❌ Error checking feature listbox: {e}")
                else:
                    print("❌ Feature listbox not available or not updated")
                
                if hasattr(app, 'target_combo') and app.target_combo:
                    try:
                        target_values = app.target_combo['values']
                        current_target = app.target_combo.get()
                        print(f"✅ Target combo updated - values: {target_values}")
                        print(f"📋 Current target: {current_target}")
                    except Exception as e:
                        print(f"❌ Error checking target combo: {e}")
                else:
                    print("❌ Target combo not available or not updated")
                
            except Exception as e:
                print(f"❌ Error testing with {test_file}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ No CSV files found for testing")
        
        print("✅ Feature loading test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in feature loading test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🚀 Starting feature loading debug test...")
    print()
    
    success = test_feature_loading()
    
    print()
    print("=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ Feature loading test - COMPLETED")
        print("\n🔍 Check the output above for any issues with feature loading.")
    else:
        print("❌ Feature loading test - FAILED")
        print("\n⚠️ There are issues with the feature loading functionality.")

if __name__ == "__main__":
    main() 