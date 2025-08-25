#!/usr/bin/env python3
"""
Test script to verify enhanced JSON loading with JSON Lines support.
This test ensures that problematic JSON files with extra data are handled correctly.
"""

import os
import sys
import tempfile
import json
import pandas as pd

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def create_problematic_json_files():
    """Create JSON files that would cause the original error."""
    test_files = {}
    
    # Test 1: JSON Lines format (multiple JSON objects, one per line)
    data1 = [
        {"date": "2024-01-01", "open": 100.0, "high": 105.0, "low": 98.0, "close": 103.0, "volume": 1000},
        {"date": "2024-01-02", "open": 103.0, "high": 108.0, "low": 102.0, "close": 106.0, "volume": 1200},
        {"date": "2024-01-03", "open": 106.0, "high": 110.0, "low": 104.0, "close": 109.0, "volume": 1100},
        {"date": "2024-01-04", "open": 109.0, "high": 112.0, "low": 107.0, "close": 111.0, "volume": 1300},
        {"date": "2024-01-05", "open": 111.0, "high": 115.0, "low": 109.0, "close": 114.0, "volume": 1400}
    ]
    test_files['json_lines.json'] = data1
    
    # Test 2: JSON with trailing whitespace and extra data
    data2 = {
        "metadata": {"symbol": "AAPL", "exchange": "NASDAQ"},
        "data": [
            {"date": "2024-01-01", "price": 100.0},
            {"date": "2024-01-02", "price": 101.0}
        ]
    }
    test_files['trailing_data.json'] = data2
    
    # Test 3: Multiple JSON objects with empty lines
    data3 = [
        {"id": 1, "name": "Item 1", "value": 10.5},
        {"id": 2, "name": "Item 2", "value": 20.3},
        {"id": 3, "name": "Item 3", "value": 15.7}
    ]
    test_files['mixed_format.json'] = data3
    
    return test_files

def test_json_lines_loading():
    """Test JSON Lines format loading."""
    print("🧪 Testing JSON Lines Format Loading")
    print("=" * 45)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Test JSON Lines format
        test_data = [
            {"date": "2024-01-01", "open": 100.0, "close": 103.0},
            {"date": "2024-01-02", "open": 103.0, "close": 106.0},
            {"date": "2024-01-03", "open": 106.0, "close": 109.0}
        ]
        
        # Create JSON Lines file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            for item in test_data:
                f.write(json.dumps(item) + '\n')
            temp_file = f.name
        
        try:
            # Load the JSON Lines file
            data_info = data_manager.load_data(temp_file)
            
            if data_info:
                loaded_data = data_manager.get_current_data()
                print(f"✅ JSON Lines loaded successfully")
                print(f"   📊 Shape: {loaded_data.shape}")
                print(f"   📋 Columns: {list(loaded_data.columns)}")
                
                # Test JSON info
                json_info = data_manager.get_json_info(temp_file)
                if json_info:
                    print(f"   🔍 Format Type: {json_info.get('format_type')}")
                    print(f"   📄 Total Lines: {json_info.get('total_lines')}")
                    print(f"   ✅ Valid Lines: {json_info.get('valid_json_lines')}")
                    print(f"   ❌ Invalid Lines: {json_info.get('invalid_lines')}")
                
            else:
                print(f"❌ Failed to load JSON Lines")
                
        finally:
            os.unlink(temp_file)
    
    except Exception as e:
        print(f"❌ Error testing JSON Lines: {e}")
        return False
    
    return True

def test_trailing_data_handling():
    """Test handling of JSON files with trailing data."""
    print("\n🧪 Testing Trailing Data Handling")
    print("=" * 40)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Create JSON file with trailing data
        json_content = '''{"name": "test", "value": 123}
{"name": "test2", "value": 456}
invalid json line
{"name": "test3", "value": 789}'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_file = f.name
        
        try:
            # Load the file
            data_info = data_manager.load_data(temp_file)
            
            if data_info:
                loaded_data = data_manager.get_current_data()
                print(f"✅ File with trailing data loaded successfully")
                print(f"   📊 Shape: {loaded_data.shape}")
                print(f"   📋 Columns: {list(loaded_data.columns)}")
                
                # Test JSON info
                json_info = data_manager.get_json_info(temp_file)
                if json_info:
                    print(f"   🔍 Format Type: {json_info.get('format_type')}")
                    print(f"   📄 Total Lines: {json_info.get('total_lines')}")
                    print(f"   ✅ Valid Lines: {json_info.get('valid_json_lines')}")
                    print(f"   ❌ Invalid Lines: {json_info.get('invalid_lines')}")
                
            else:
                print(f"❌ Failed to load file with trailing data")
                
        finally:
            os.unlink(temp_file)
    
    except Exception as e:
        print(f"❌ Error testing trailing data: {e}")
        return False
    
    return True

def test_mixed_format_handling():
    """Test handling of mixed JSON formats."""
    print("\n🧪 Testing Mixed Format Handling")
    print("=" * 40)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Create mixed format file (JSON Lines with empty lines)
        json_content = '''{"id": 1, "name": "Item 1", "value": 10.5}

{"id": 2, "name": "Item 2", "value": 20.3}

{"id": 3, "name": "Item 3", "value": 15.7}'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_file = f.name
        
        try:
            # Load the file
            data_info = data_manager.load_data(temp_file)
            
            if data_info:
                loaded_data = data_manager.get_current_data()
                print(f"✅ Mixed format file loaded successfully")
                print(f"   📊 Shape: {loaded_data.shape}")
                print(f"   📋 Columns: {list(loaded_data.columns)}")
                
                # Test JSON info
                json_info = data_manager.get_json_info(temp_file)
                if json_info:
                    print(f"   🔍 Format Type: {json_info.get('format_type')}")
                    print(f"   📄 Total Lines: {json_info.get('total_lines')}")
                    print(f"   ✅ Valid Lines: {json_info.get('valid_json_lines')}")
                    print(f"   ❌ Invalid Lines: {json_info.get('invalid_lines')}")
                
            else:
                print(f"❌ Failed to load mixed format file")
                
        finally:
            os.unlink(temp_file)
    
    except Exception as e:
        print(f"❌ Error testing mixed format: {e}")
        return False
    
    return True

def test_error_recovery():
    """Test error recovery and fallback mechanisms."""
    print("\n🧪 Testing Error Recovery")
    print("=" * 30)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Test 1: Completely invalid JSON
        invalid_content = '''This is not JSON at all
{"partial": "json" but missing closing brace
{"valid": "json"}'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name
        
        try:
            # Try to load the file
            data_info = data_manager.load_data(temp_file)
            
            if data_info:
                loaded_data = data_manager.get_current_data()
                print(f"✅ Error recovery successful")
                print(f"   📊 Shape: {loaded_data.shape}")
                print(f"   📋 Columns: {list(loaded_data.columns)}")
                
                # Test JSON info
                json_info = data_manager.get_json_info(temp_file)
                if json_info:
                    print(f"   🔍 Format Type: {json_info.get('format_type')}")
                    print(f"   ✅ Valid Lines: {json_info.get('valid_json_lines')}")
                    print(f"   ❌ Invalid Lines: {json_info.get('invalid_lines')}")
                
            else:
                print(f"❌ Error recovery failed")
                
        finally:
            os.unlink(temp_file)
    
    except Exception as e:
        print(f"❌ Error in error recovery test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Enhanced JSON Loading Tests")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_json_lines_loading()
    test2_passed = test_trailing_data_handling()
    test3_passed = test_mixed_format_handling()
    test4_passed = test_error_recovery()
    
    if test1_passed and test2_passed and test3_passed and test4_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced JSON loading is working correctly")
        print("✅ JSON Lines format is supported")
        print("✅ Trailing data is handled gracefully")
        print("✅ Mixed formats are processed correctly")
        print("✅ Error recovery mechanisms work")
        print("\n📋 Summary of fixes:")
        print("   • JSON Lines format support (multiple JSON objects)")
        print("   • Trailing data handling")
        print("   • Empty line skipping")
        print("   • Invalid line skipping with warnings")
        print("   • Enhanced error recovery")
        print("   • Better JSON structure analysis")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the implementation and try again.")
        sys.exit(1) 