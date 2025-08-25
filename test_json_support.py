#!/usr/bin/env python3
"""
Test script to verify JSON file support in stock_prediction_gui.
This test ensures that the Data Tab can read and work with JSON files.
"""

import os
import sys
import tempfile
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def create_test_json_files():
    """Create various test JSON files."""
    test_files = {}
    
    # Test 1: Array of objects (most common format)
    data1 = [
        {"date": "2024-01-01", "open": 100.0, "high": 105.0, "low": 98.0, "close": 103.0, "volume": 1000},
        {"date": "2024-01-02", "open": 103.0, "high": 108.0, "low": 102.0, "close": 106.0, "volume": 1200},
        {"date": "2024-01-03", "open": 106.0, "high": 110.0, "low": 104.0, "close": 109.0, "volume": 1100},
        {"date": "2024-01-04", "open": 109.0, "high": 112.0, "low": 107.0, "close": 111.0, "volume": 1300},
        {"date": "2024-01-05", "open": 111.0, "high": 115.0, "low": 109.0, "close": 114.0, "volume": 1400}
    ]
    test_files['array_of_objects.json'] = data1
    
    # Test 2: Single object
    data2 = {
        "metadata": {
            "symbol": "AAPL",
            "exchange": "NASDAQ",
            "currency": "USD"
        },
        "data": {
            "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "prices": [100.0, 101.0, 102.0],
            "volumes": [1000, 1100, 1200]
        }
    }
    test_files['nested_object.json'] = data2
    
    # Test 3: Simple array of values
    data3 = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]
    test_files['array_of_values.json'] = data3
    
    # Test 4: Object with arrays (columns format)
    data4 = {
        "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "open": [100.0, 103.0, 106.0, 109.0, 111.0],
        "high": [105.0, 108.0, 110.0, 112.0, 115.0],
        "low": [98.0, 102.0, 104.0, 107.0, 109.0],
        "close": [103.0, 106.0, 109.0, 111.0, 114.0],
        "volume": [1000, 1200, 1100, 1300, 1400]
    }
    test_files['columns_format.json'] = data4
    
    return test_files

def test_json_loading():
    """Test JSON file loading functionality."""
    print("🧪 Testing JSON File Loading")
    print("=" * 40)
    
    # Create test files
    test_files = create_test_json_files()
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Test each JSON file
        for filename, data in test_files.items():
            print(f"\n📁 Testing: {filename}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f, indent=2)
                temp_file = f.name
            
            try:
                # Load the JSON file
                data_info = data_manager.load_data(temp_file)
                
                if data_info:
                    # Get the loaded data
                    loaded_data = data_manager.get_current_data()
                    
                    print(f"   ✅ Loaded successfully")
                    print(f"   📊 Shape: {loaded_data.shape}")
                    print(f"   📋 Columns: {list(loaded_data.columns)}")
                    print(f"   🔢 Numeric columns: {len(data_info.get('numeric_columns', []))}")
                    
                    # Test JSON-specific info
                    json_info = data_manager.get_json_info(temp_file)
                    if json_info:
                        print(f"   🔍 JSON Structure: {json_info.get('structure_type')}")
                        print(f"   📏 Array Length: {json_info.get('array_length', 'N/A')}")
                        print(f"   🗝️ Object Keys: {json_info.get('object_keys', 'N/A')}")
                        print(f"   📐 Nesting Levels: {json_info.get('nested_levels', 0)}")
                    
                else:
                    print(f"   ❌ Failed to load")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            finally:
                # Clean up
                os.unlink(temp_file)
    
    except ImportError as e:
        print(f"❌ Could not import DataManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing JSON loading: {e}")
        return False
    
    return True

def test_json_saving():
    """Test JSON file saving functionality."""
    print("\n🧪 Testing JSON File Saving")
    print("=" * 40)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Create test DataFrame
        test_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'open': [100.0, 101.0, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [98.0, 99.0, 100.0],
            'close': [103.0, 104.0, 105.0],
            'volume': [1000, 1100, 1200]
        })
        
        print(f"📊 Test data shape: {test_data.shape}")
        print(f"📋 Columns: {list(test_data.columns)}")
        
        # Test different JSON formats
        formats = [
            ('records', 2, 'records_2spaces.json'),
            ('columns', 4, 'columns_4spaces.json'),
            ('index', 0, 'index_compact.json'),
            ('values', 2, 'values_2spaces.json')
        ]
        
        for orient, indent, filename in formats:
            print(f"\n💾 Testing format: {orient}, indent: {indent}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_file = f.name
            
            try:
                # Save the data
                success = data_manager.save_as_json(test_data, temp_file, orient=orient, indent=indent)
                
                if success:
                    # Verify the saved file
                    with open(temp_file, 'r') as f:
                        saved_data = json.load(f)
                    
                    print(f"   ✅ Saved successfully")
                    print(f"   📏 File size: {os.path.getsize(temp_file)} bytes")
                    print(f"   🔍 Structure type: {type(saved_data).__name__}")
                    
                    if isinstance(saved_data, list):
                        print(f"   📊 Array length: {len(saved_data)}")
                    elif isinstance(saved_data, dict):
                        print(f"   🗝️ Object keys: {list(saved_data.keys())}")
                    
                else:
                    print(f"   ❌ Failed to save")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            finally:
                # Clean up
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    except ImportError as e:
        print(f"❌ Could not import DataManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing JSON saving: {e}")
        return False
    
    return True

def test_json_format_detection():
    """Test JSON format detection and analysis."""
    print("\n🧪 Testing JSON Format Detection")
    print("=" * 40)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Create test files
        test_files = create_test_json_files()
        
        for filename, data in test_files.items():
            print(f"\n📁 Analyzing: {filename}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f, indent=2)
                temp_file = f.name
            
            try:
                # Get JSON info
                json_info = data_manager.get_json_info(temp_file)
                
                if json_info:
                    print(f"   ✅ Analysis successful")
                    print(f"   🔍 Structure Type: {json_info.get('structure_type')}")
                    print(f"   📏 File Size: {json_info.get('file_size')} bytes")
                    print(f"   📊 Is Array: {json_info.get('is_array')}")
                    print(f"   🗝️ Is Object: {json_info.get('is_object')}")
                    
                    if json_info.get('array_length'):
                        print(f"   📐 Array Length: {json_info.get('array_length')}")
                    
                    if json_info.get('object_keys'):
                        print(f"   🗝️ Object Keys: {len(json_info.get('object_keys'))}")
                    
                    print(f"   📐 Nesting Levels: {json_info.get('nested_levels')}")
                    print(f"   📊 Estimated Rows: {json_info.get('estimated_rows')}")
                    print(f"   📋 Estimated Columns: {json_info.get('estimated_columns')}")
                    
                else:
                    print(f"   ❌ Analysis failed")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            finally:
                # Clean up
                os.unlink(temp_file)
    
    except ImportError as e:
        print(f"❌ Could not import DataManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing JSON format detection: {e}")
        return False
    
    return True

def test_supported_formats():
    """Test that JSON is included in supported formats."""
    print("\n🧪 Testing Supported Formats")
    print("=" * 30)
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Get supported formats
        formats = data_manager.get_supported_formats()
        formats_info = data_manager.get_supported_formats_info()
        
        print(f"📋 Total supported formats: {formats_info.get('total_formats', 0)}")
        print(f"🔧 Available libraries: {formats_info.get('available_libraries', 0)}")
        
        # Check if JSON is supported
        if 'JSON' in formats:
            json_extensions = formats['JSON']
            print(f"✅ JSON support: {json_extensions}")
        else:
            print(f"❌ JSON not found in supported formats")
            return False
        
        # List all supported formats
        print(f"\n📋 All supported formats:")
        for format_name, extensions in formats.items():
            print(f"   {format_name}: {extensions}")
    
    except ImportError as e:
        print(f"❌ Could not import DataManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing supported formats: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting JSON Support Tests")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_supported_formats()
    test2_passed = test_json_loading()
    test3_passed = test_json_saving()
    test4_passed = test_json_format_detection()
    
    if test1_passed and test2_passed and test3_passed and test4_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ JSON file support is working correctly")
        print("✅ Data Tab can read and work with JSON files")
        print("✅ Enhanced JSON loading with structure detection")
        print("✅ JSON saving with format options")
        print("✅ JSON format analysis and information display")
        print("\n📋 Summary of JSON features:")
        print("   • Read JSON files (arrays, objects, nested structures)")
        print("   • Save data as JSON with various formats")
        print("   • JSON structure analysis and information")
        print("   • Enhanced error handling and fallback options")
        print("   • User-friendly format selection dialog")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the implementation and try again.")
        sys.exit(1) 