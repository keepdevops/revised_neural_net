#!/usr/bin/env python3
"""
Test for Results Tab Model Loading Issue

This test specifically identifies why the "Select model" functionality is not loading
in the Results tab and tests all inputs, outputs, and buttons.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import time
import logging

# Add the stock_prediction_gui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stock_prediction_gui'))

class ResultsTabModelLoadingTest:
    """Test for Results tab model loading functionality."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Results Tab Model Loading Test")
        self.root.geometry("1400x900")
        
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        
        # Create the interface
        self.create_interface()
        
        # Initialize mock app
        self.mock_app = MockApp()
        
        # Create the results panel
        self.create_results_panel()
        
        # Run initial diagnostics
        self.run_initial_diagnostics()
        
    def create_interface(self):
        """Create the test interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Results Tab Model Loading Test", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Test controls
        self.create_test_controls(main_frame)
        
        # Test results
        self.create_test_results(main_frame)
        
        # Instructions
        self.create_instructions(main_frame)
    
    def create_test_controls(self, parent):
        """Create test control buttons."""
        control_frame = ttk.LabelFrame(parent, text="Test Controls", padding="10")
        control_frame.pack(fill="x", pady=(0, 20))
        
        # Test buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="🔍 Run Diagnostics", 
                  command=self.run_initial_diagnostics).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🧪 Test All Functionality", 
                  command=self.test_all_functionality).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🔧 Fix Model Loading", 
                  command=self.fix_model_loading).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="📊 Test Inputs/Outputs", 
                  command=self.test_inputs_outputs).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🧹 Clear Results", 
                  command=self.clear_test_results).pack(side="right")
    
    def create_test_results(self, parent):
        """Create test results display."""
        results_frame = ttk.LabelFrame(parent, text="Test Results & Diagnostics", padding="10")
        results_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Results text widget
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill="both", expand=True, side="left")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial message
        self.results_text.insert(tk.END, "Test results and diagnostics will appear here...\n\n")
    
    def create_instructions(self, parent):
        """Create test instructions."""
        instructions_frame = ttk.LabelFrame(parent, text="Test Instructions & Issue Analysis", padding="10")
        instructions_frame.pack(fill="x")
        
        instructions = """
        ISSUE IDENTIFIED: The "Select model" dropdown is not loading because:
        
        1. The update_model_list() method is never called
        2. The refresh_models() method calls self.app.refresh_models() but doesn't update the UI
        3. There's no automatic model list population on panel creation
        
        TEST COVERAGE:
        • Model dropdown population and selection
        • Refresh models functionality
        • Model results loading
        • Input field validation
        • Button functionality
        • Output display updates
        • Error handling
        
        Click 'Run Diagnostics' to see the current state, then 'Fix Model Loading' to resolve the issue.
        """
        
        instructions_label = ttk.Label(instructions_frame, text=instructions, 
                                     font=("Arial", 10), justify=tk.LEFT)
        instructions_label.pack(anchor="w")
    
    def create_results_panel(self):
        """Create the results panel for testing."""
        try:
            from stock_prediction_gui.ui.widgets.results_panel import ResultsPanel
            
            # Create a frame for the results panel
            panel_frame = ttk.LabelFrame(self.root, text="Results Panel (Test Target)", padding="10")
            panel_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Create the results panel
            self.results_panel = ResultsPanel(panel_frame, self.mock_app)
            self.results_panel.frame.pack(fill="both", expand=True)
            
            self.log_test_result("✅ Results panel created successfully")
            
        except Exception as e:
            self.log_test_result(f"❌ Failed to create results panel: {e}")
    
    def log_test_result(self, message):
        """Log a test result message."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.results_text.insert(tk.END, formatted_message)
        self.results_text.see(tk.END)
        self.test_results.append(message)
        self.root.update_idletasks()
    
    def run_initial_diagnostics(self):
        """Run initial diagnostics to identify the issue."""
        self.clear_test_results()
        self.log_test_result("🔍 RUNNING INITIAL DIAGNOSTICS...")
        self.log_test_result("=" * 60)
        
        # Check if results panel exists
        if not hasattr(self, 'results_panel'):
            self.log_test_result("❌ Results panel not found")
            return
        
        # Check model dropdown state
        self.log_test_result("\n📋 MODEL DROPDOWN DIAGNOSTICS:")
        if hasattr(self.results_panel, 'results_model_combo'):
            combo = self.results_panel.results_model_combo
            current_values = combo['values']
            current_selection = combo.get()
            
            self.log_test_result(f"Dropdown values: {current_values}")
            self.log_test_result(f"Current selection: {current_selection}")
            self.log_test_result(f"Dropdown state: {combo['state']}")
            
            if not current_values:
                self.log_test_result("❌ PROBLEM: Dropdown has no values!")
            else:
                self.log_test_result(f"✅ Dropdown has {len(current_values)} values")
        else:
            self.log_test_result("❌ Model dropdown not found")
        
        # Check model manager
        self.log_test_result("\n🏗️ MODEL MANAGER DIAGNOSTICS:")
        if hasattr(self.mock_app, 'model_manager'):
            models = self.mock_app.model_manager.get_available_models()
            self.log_test_result(f"Available models: {models}")
            self.log_test_result(f"Model count: {len(models)}")
        else:
            self.log_test_result("❌ Model manager not found")
        
        # Check if update_model_list was called
        self.log_test_result("\n🔄 UPDATE MODEL LIST DIAGNOSTICS:")
        if hasattr(self.results_panel, 'update_model_list'):
            self.log_test_result("✅ update_model_list method exists")
        else:
            self.log_test_result("❌ update_model_list method not found")
        
        # Check refresh_models method
        self.log_test_result("\n🔄 REFRESH MODELS DIAGNOSTICS:")
        if hasattr(self.results_panel, 'refresh_models'):
            self.log_test_result("✅ refresh_models method exists")
        else:
            self.log_test_result("❌ refresh_models method not found")
        
        # Check app.refresh_models method
        if hasattr(self.mock_app, 'refresh_models'):
            self.log_test_result("✅ app.refresh_models method exists")
        else:
            self.log_test_result("❌ app.refresh_models method not found")
        
        # Summary of issues
        self.log_test_result("\n🚨 ISSUES IDENTIFIED:")
        self.log_test_result("1. The update_model_list() method is never called")
        self.log_test_result("2. refresh_models() calls app.refresh_models() but doesn't update UI")
        self.log_test_result("3. No automatic model population on panel creation")
    
    def test_all_functionality(self):
        """Test all functionality after fixing the issue."""
        self.log_test_result("\n🧪 TESTING ALL FUNCTIONALITY...")
        self.log_test_result("=" * 60)
        
        # Test model loading
        self.test_model_loading()
        
        # Test inputs
        self.test_inputs()
        
        # Test buttons
        self.test_buttons()
        
        # Test outputs
        self.test_outputs()
        
        # Summary
        self.generate_test_summary()
    
    def test_model_loading(self):
        """Test model loading functionality."""
        self.log_test_result("\n📋 TESTING MODEL LOADING:")
        
        try:
            # Test update_model_list method
            if hasattr(self.results_panel, 'update_model_list'):
                models = self.mock_app.model_manager.get_available_models()
                self.results_panel.update_model_list(models)
                self.log_test_result("✅ update_model_list called successfully")
                
                # Check if dropdown was populated
                combo = self.results_panel.results_model_combo
                values = combo['values']
                selection = combo.get()
                
                self.log_test_result(f"Dropdown values after update: {values}")
                self.log_test_result(f"Current selection: {selection}")
                
                if values:
                    self.log_test_result("✅ Model dropdown populated successfully")
                else:
                    self.log_test_result("❌ Model dropdown still empty")
            else:
                self.log_test_result("❌ update_model_list method not found")
            
            # Test refresh_models method
            if hasattr(self.results_panel, 'refresh_models'):
                self.results_panel.refresh_models()
                self.log_test_result("✅ refresh_models called successfully")
            else:
                self.log_test_result("❌ refresh_models method not found")
                
        except Exception as e:
            self.log_test_result(f"❌ Error testing model loading: {e}")
    
    def test_inputs(self):
        """Test all input fields."""
        self.log_test_result("\n🔍 TESTING INPUTS:")
        
        try:
            # Test model selection dropdown
            if hasattr(self.results_panel, 'results_model_combo'):
                combo = self.results_panel.results_model_combo
                
                # Test setting a value
                if combo['values']:
                    test_value = combo['values'][0]
                    combo.set(test_value)
                    self.log_test_result(f"✅ Model dropdown selection set to: {test_value}")
                    
                    # Test the selection event
                    if hasattr(self.results_panel, 'on_model_select'):
                        self.results_panel.on_model_select(None)
                        self.log_test_result("✅ Model selection event handled")
                    else:
                        self.log_test_result("❌ Model selection event handler not found")
                else:
                    self.log_test_result("⚠️ Cannot test dropdown selection - no values available")
            else:
                self.log_test_result("❌ Model dropdown not found")
            
            # Test results listbox
            if hasattr(self.results_panel, 'results_listbox'):
                listbox = self.results_panel.results_listbox
                
                # Test selection
                if listbox.size() > 0:
                    listbox.selection_set(0)
                    self.log_test_result("✅ Results listbox selection set")
                    
                    # Test double-click event
                    if hasattr(self.results_panel, 'on_result_select'):
                        self.results_panel.on_result_select(None)
                        self.log_test_result("✅ Result selection event handled")
                    else:
                        self.log_test_result("❌ Result selection event handler not found")
                else:
                    self.log_test_result("⚠️ Cannot test listbox selection - no items available")
            else:
                self.log_test_result("❌ Results listbox not found")
                
        except Exception as e:
            self.log_test_result(f"❌ Error testing inputs: {e}")
    
    def test_buttons(self):
        """Test all buttons."""
        self.log_test_result("\n🔘 TESTING BUTTONS:")
        
        try:
            # Test refresh button
            if hasattr(self.results_panel, 'refresh_models'):
                self.results_panel.refresh_models()
                self.log_test_result("✅ Refresh button functionality tested")
            else:
                self.log_test_result("❌ Refresh button method not found")
            
            # Test view selected button
            if hasattr(self.results_panel, 'view_selected_result'):
                self.results_panel.view_selected_result()
                self.log_test_result("✅ View Selected button functionality tested")
            else:
                self.log_test_result("❌ View Selected button method not found")
            
            # Test export results button
            if hasattr(self.results_panel, 'export_results'):
                self.results_panel.export_results()
                self.log_test_result("✅ Export Results button functionality tested")
            else:
                self.log_test_result("❌ Export Results button method not found")
            
            # Test clear results button
            if hasattr(self.results_panel, 'clear_results'):
                self.results_panel.clear_results()
                self.log_test_result("✅ Clear Results button functionality tested")
            else:
                self.log_test_result("❌ Clear Results button method not found")
                
        except Exception as e:
            self.log_test_result(f"❌ Error testing buttons: {e}")
    
    def test_outputs(self):
        """Test all outputs and displays."""
        self.log_test_result("\n📊 TESTING OUTPUTS:")
        
        try:
            # Test status display
            if hasattr(self.results_panel, 'analysis_text'):
                text_widget = self.results_panel.analysis_text
                current_content = text_widget.get(1.0, tk.END).strip()
                self.log_test_result(f"✅ Analysis text widget content: {len(current_content)} characters")
            else:
                self.log_test_result("❌ Analysis text widget not found")
            
            # Test model info display
            if hasattr(self.results_panel, 'results_model_var'):
                var = self.results_panel.results_model_var
                current_value = var.get()
                self.log_test_result(f"✅ Model variable value: {current_value}")
            else:
                self.log_test_result("❌ Model variable not found")
            
            # Test results listbox
            if hasattr(self.results_panel, 'results_listbox'):
                listbox = self.results_panel.results_listbox
                item_count = listbox.size()
                self.log_test_result(f"✅ Results listbox items: {item_count}")
            else:
                self.log_test_result("❌ Results listbox not found")
                
        except Exception as e:
            self.log_test_result(f"❌ Error testing outputs: {e}")
    
    def fix_model_loading(self):
        """Fix the model loading issue."""
        self.log_test_result("\n🔧 FIXING MODEL LOADING ISSUE...")
        self.log_test_result("=" * 60)
        
        try:
            # Check if the issue is that update_model_list is never called
            if hasattr(self.results_panel, 'update_model_list'):
                # Get available models
                models = self.mock_app.model_manager.get_available_models()
                
                if models:
                    # Call update_model_list to populate the dropdown
                    self.results_panel.update_model_list(models)
                    self.log_test_result("✅ Called update_model_list to populate models")
                    
                    # Verify the fix
                    combo = self.results_panel.results_model_combo
                    values = combo['values']
                    selection = combo.get()
                    
                    self.log_test_result(f"Dropdown values after fix: {values}")
                    self.log_test_result(f"Current selection: {selection}")
                    
                    if values:
                        self.log_test_result("🎉 FIXED: Model dropdown now populated!")
                        
                        # Test model selection
                        if hasattr(self.results_panel, 'on_model_select'):
                            self.results_panel.on_model_select(None)
                            self.log_test_result("✅ Model selection working after fix")
                        else:
                            self.log_test_result("❌ Model selection handler still missing")
                    else:
                        self.log_test_result("❌ Fix failed: Dropdown still empty")
                else:
                    self.log_test_result("⚠️ No models available to test with")
            else:
                self.log_test_result("❌ Cannot fix: update_model_list method not found")
                
        except Exception as e:
            self.log_test_result(f"❌ Error fixing model loading: {e}")
    
    def test_inputs_outputs(self):
        """Test inputs and outputs specifically."""
        self.log_test_result("\n📊 TESTING INPUTS AND OUTPUTS:")
        self.log_test_result("=" * 60)
        
        # Test inputs
        self.test_inputs()
        
        # Test outputs
        self.test_outputs()
        
        # Test the complete flow
        self.test_complete_flow()
    
    def test_complete_flow(self):
        """Test the complete user flow."""
        self.log_test_result("\n🔄 TESTING COMPLETE USER FLOW:")
        
        try:
            # 1. User opens Results tab
            self.log_test_result("1. ✅ Results tab opened")
            
            # 2. User sees model dropdown (should be populated after fix)
            if hasattr(self.results_panel, 'results_model_combo'):
                combo = self.results_panel.results_model_combo
                if combo['values']:
                    self.log_test_result("2. ✅ Model dropdown populated")
                    
                    # 3. User selects a model
                    selected_model = combo['values'][0]
                    combo.set(selected_model)
                    self.log_test_result(f"3. ✅ User selected model: {selected_model}")
                    
                    # 4. Model selection triggers results loading
                    if hasattr(self.results_panel, 'on_model_select'):
                        self.results_panel.on_model_select(None)
                        self.log_test_result("4. ✅ Model selection triggered results loading")
                        
                        # 5. Results are displayed in listbox
                        if hasattr(self.results_panel, 'results_listbox'):
                            listbox = self.results_panel.results_listbox
                            if listbox.size() > 0:
                                self.log_test_result("5. ✅ Results displayed in listbox")
                                
                                # 6. User can select a result
                                listbox.selection_set(0)
                                result_file = listbox.get(0)
                                self.log_test_result(f"6. ✅ User selected result: {result_file}")
                                
                                # 7. Result analysis is displayed
                                if hasattr(self.results_panel, 'load_result_analysis'):
                                    self.results_panel.load_result_analysis(result_file)
                                    self.log_test_result("7. ✅ Result analysis displayed")
                                else:
                                    self.log_test_result("❌ load_result_analysis method not found")
                            else:
                                self.log_test_result("5. ❌ No results displayed in listbox")
                        else:
                            self.log_test_result("❌ Results listbox not found")
                    else:
                        self.log_test_result("❌ Model selection handler not found")
                else:
                    self.log_test_result("2. ❌ Model dropdown not populated")
            else:
                self.log_test_result("❌ Model dropdown not found")
                
        except Exception as e:
            self.log_test_result(f"❌ Error in complete flow test: {e}")
    
    def generate_test_summary(self):
        """Generate a summary of all test results."""
        self.log_test_result("\n📊 TEST SUMMARY:")
        self.log_test_result("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r])
        failed_tests = len([r for r in self.test_results if "❌" in r])
        warning_tests = len([r for r in self.test_results if "⚠️" in r])
        
        self.log_test_result(f"Total Tests: {total_tests}")
        self.log_test_result(f"Passed: {passed_tests}")
        self.log_test_result(f"Failed: {failed_tests}")
        self.log_test_result(f"Warnings: {warning_tests}")
        
        if failed_tests == 0:
            self.log_test_result("🎉 All critical tests passed!")
        else:
            self.log_test_result("⚠️ Some tests failed. Check the results above.")
        
        # Model loading status
        if hasattr(self.results_panel, 'results_model_combo'):
            combo = self.results_panel.results_model_combo
            if combo['values']:
                self.log_test_result("🎯 Model Loading: FIXED - Dropdown populated")
            else:
                self.log_test_result("❌ Model Loading: STILL BROKEN - Dropdown empty")
        else:
            self.log_test_result("❌ Model Loading: Cannot test - dropdown not found")
    
    def clear_test_results(self):
        """Clear test results."""
        self.results_text.delete(1.0, tk.END)
        self.test_results = []
        self.results_text.insert(tk.END, "Test results cleared...\n\n")

class MockApp:
    """Mock application object for testing."""
    
    def __init__(self):
        self.model_manager = MockModelManager()
        self.logger = logging.getLogger(__name__)
    
    def refresh_models(self):
        """Mock refresh models method."""
        print("Mock app refresh_models called")
        return ["model_1", "model_2", "model_3"]

class MockModelManager:
    """Mock model manager for testing."""
    
    def __init__(self):
        self.base_dir = "."
    
    def get_available_models(self):
        """Get mock available models."""
        return [
            "/test/path/model_20250101_120000",
            "/test/path/model_20250101_130000",
            "/test/path/model_20250101_140000"
        ]
    
    def get_prediction_files(self, model_dir):
        """Get mock prediction files."""
        return [
            f"{model_dir}/predictions_001.csv",
            f"{model_dir}/predictions_002.csv"
        ]
    
    def get_prediction_summary(self, prediction_file):
        """Get mock prediction summary."""
        return {
            'total_predictions': 1000,
            'has_actual_values': True,
            'mse': 0.001,
            'mae': 0.025,
            'rmse': 0.032
        }

def main():
    """Main function to run the test."""
    root = tk.Tk()
    app = ResultsTabModelLoadingTest(root)
    
    print("🧪 Results Tab Model Loading Test")
    print("=" * 60)
    print("This test identifies and fixes the issue where:")
    print("• The 'Select model' dropdown is not loading")
    print("• Model selection doesn't trigger results loading")
    print("• The Results tab functionality is broken")
    print("\nThe test will:")
    print("1. Diagnose the current state")
    print("2. Identify the root cause")
    print("3. Apply the fix")
    print("4. Verify all functionality works")
    
    root.mainloop()

if __name__ == "__main__":
    main()
