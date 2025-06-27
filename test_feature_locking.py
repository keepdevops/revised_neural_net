#!/usr/bin/env python3
"""
Test script to debug feature locking functionality in the Data Selection tab.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import pandas as pd

# Add the gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

from main_gui import StockPredictionGUI

def test_feature_locking():
    """Test the feature locking functionality."""
    print("🧪 Testing feature locking functionality...")
    
    try:
        root = tk.Tk()
        root.title("Feature Locking Test")
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
            
        if hasattr(app, 'feature_status_var'):
            print("✅ feature_status_var exists")
        else:
            print("❌ feature_status_var does not exist")
            
        if hasattr(app, 'status_var'):
            print("✅ status_var exists")
        else:
            print("❌ status_var does not exist")
        
        # Check if there are any CSV files available
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        print(f"📁 Found {len(csv_files)} CSV files: {csv_files}")
        
        if csv_files:
            # Test with the first CSV file
            test_file = csv_files[0]
            print(f"🧪 Testing with file: {test_file}")
            
            # Load features first
            app.data_file = test_file
            app.data_file_var.set(test_file)
            app.load_data_features()
            
            print(f"📋 Feature list: {app.feature_list}")
            
            # Test feature selection
            if hasattr(app, 'feature_listbox') and app.feature_listbox:
                try:
                    # Select the first feature
                    app.feature_listbox.selection_set(0)
                    selected_indices = app.feature_listbox.curselection()
                    print(f"🔍 Selected feature index: {selected_indices}")
                    
                    if selected_indices:
                        selected_feature = app.feature_list[selected_indices[0]]
                        print(f"📋 Selected feature: {selected_feature}")
                        
                        # Test lock_features method
                        print("🔒 Testing lock_features()...")
                        app.lock_features()
                        
                        # Check if features were locked
                        print(f"🔒 Locked features: {app.locked_features}")
                        print(f"🔒 Features locked: {app.features_locked}")
                        
                        # Test unlock_features method
                        print("🔓 Testing unlock_features()...")
                        app.unlock_features()
                        
                        # Check if features were unlocked
                        print(f"🔓 Locked features after unlock: {app.locked_features}")
                        print(f"🔓 Features locked after unlock: {app.features_locked}")
                        
                        # Test multiple feature selection
                        print("🔒 Testing multiple feature selection...")
                        app.feature_listbox.selection_set(0, 2)  # Select first 3 features
                        selected_indices = app.feature_listbox.curselection()
                        print(f"🔍 Selected multiple features: {selected_indices}")
                        
                        app.lock_features()
                        print(f"🔒 Multiple locked features: {app.locked_features}")
                        
                    else:
                        print("❌ Could not select feature")
                        
                except Exception as e:
                    print(f"❌ Error testing feature selection: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Feature listbox not available for testing")
        else:
            print("⚠️ No CSV files found for testing")
        
        print("✅ Feature locking test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in feature locking test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🚀 Starting feature locking debug test...")
    print()
    
    success = test_feature_locking()
    
    print()
    print("=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ Feature locking test - COMPLETED")
        print("\n🔍 Check the output above for any issues with feature locking.")
        print("\n📋 To test in the GUI:")
        print("1. Select a data file from the dropdown")
        print("2. Select one or more features in the Features listbox")
        print("3. Click 'Lock Selected' button")
        print("4. Check the Lock Status display")
        print("5. Click 'Unlock All' button")
    else:
        print("❌ Feature locking test - FAILED")
        print("\n⚠️ There are issues with the feature locking functionality.")

if __name__ == "__main__":
    main() 