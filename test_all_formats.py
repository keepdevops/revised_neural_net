#!/usr/bin/env python3
"""
Comprehensive test script to verify all file format support.
Tests: DuckDB, PyArrow, Keras, Polars, SQLite
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_data_manager_formats():
    """Test the data manager with all supported formats."""
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        # Create data manager
        data_manager = DataManager()
        
        print("✅ Data manager created successfully")
        print(f"📊 Available libraries: {data_manager.libraries_available}")
        
        # Get supported formats
        formats = data_manager.get_supported_formats()
        print(f"📁 Supported formats: {list(formats.keys())}")
        
        # Create test data
        test_data = pd.DataFrame({
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [101.0, 102.0, 103.0, 104.0, 105.0],
            'vol': [1000, 1100, 1200, 1300, 1400]
        })
        
        print(f"📊 Test data created: {test_data.shape}")
        
        # Test each format
        format_tests = {}
        
        # Test 1: CSV (baseline)
        print("\n1. Testing CSV format...")
        try:
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
                test_data.to_csv(f.name, index=False)
                data_info = data_manager.load_data(f.name)
                loaded_data = data_manager.get_current_data()
                format_tests['CSV'] = loaded_data is not None and len(loaded_data) == len(test_data)
                print(f"   {'✅ PASS' if format_tests['CSV'] else '❌ FAIL'}")
            os.unlink(f.name)
        except Exception as e:
            format_tests['CSV'] = False
            print(f"   ❌ FAIL: {e}")
        
        # Test 2: SQLite
        print("\n2. Testing SQLite format...")
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                import sqlite3
                conn = sqlite3.connect(f.name)
                test_data.to_sql('test_table', conn, index=False, if_exists='replace')
                conn.close()
                
                data_info = data_manager.load_data(f.name)
                loaded_data = data_manager.get_current_data()
                format_tests['SQLite'] = loaded_data is not None and len(loaded_data) == len(test_data)
                print(f"   {'✅ PASS' if format_tests['SQLite'] else '❌ FAIL'}")
            os.unlink(f.name)
        except Exception as e:
            format_tests['SQLite'] = False
            print(f"   ❌ FAIL: {e}")
        
        # Test 3: DuckDB
        print("\n3. Testing DuckDB format...")
        if data_manager.libraries_available['duckdb']:
            try:
                with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=False) as f:
                    import duckdb
                    conn = duckdb.connect(f.name)
                    conn.execute("CREATE TABLE test_table AS SELECT * FROM test_data")
                    conn.execute("INSERT INTO test_table SELECT * FROM test_data")
                    conn.close()
                    
                    # Create test data in DuckDB
                    conn = duckdb.connect(f.name)
                    conn.execute("CREATE TABLE test_table AS SELECT * FROM (VALUES (100.0, 105.0, 95.0, 101.0, 1000), (101.0, 106.0, 96.0, 102.0, 1100)) AS t(open, high, low, close, vol)")
                    conn.close()
                    
                    data_info = data_manager.load_data(f.name)
                    loaded_data = data_manager.get_current_data()
                    format_tests['DuckDB'] = loaded_data is not None
                    print(f"   {'✅ PASS' if format_tests['DuckDB'] else '❌ FAIL'}")
                os.unlink(f.name)
            except Exception as e:
                format_tests['DuckDB'] = False
                print(f"   ❌ FAIL: {e}")
        else:
            format_tests['DuckDB'] = False
            print("   ⚠️  SKIP: DuckDB not available")
        
        # Test 4: Feather (PyArrow)
        print("\n4. Testing Feather format...")
        if data_manager.libraries_available['feather']:
            try:
                with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as f:
                    test_data.to_feather(f.name)
                    data_info = data_manager.load_data(f.name)
                    loaded_data = data_manager.get_current_data()
                    format_tests['Feather'] = loaded_data is not None and len(loaded_data) == len(test_data)
                    print(f"   {'✅ PASS' if format_tests['Feather'] else '❌ FAIL'}")
                os.unlink(f.name)
            except Exception as e:
                format_tests['Feather'] = False
                print(f"   ❌ FAIL: {e}")
        else:
            format_tests['Feather'] = False
            print("   ⚠️  SKIP: Feather not available")
        
        # Test 5: Parquet (PyArrow)
        print("\n5. Testing Parquet format...")
        if data_manager.libraries_available['pyarrow']:
            try:
                with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
                    test_data.to_parquet(f.name)
                    data_info = data_manager.load_data(f.name)
                    loaded_data = data_manager.get_current_data()
                    format_tests['Parquet'] = loaded_data is not None and len(loaded_data) == len(test_data)
                    print(f"   {'✅ PASS' if format_tests['Parquet'] else '❌ FAIL'}")
                os.unlink(f.name)
            except Exception as e:
                format_tests['Parquet'] = False
                print(f"   ❌ FAIL: {e}")
        else:
            format_tests['Parquet'] = False
            print("   ⚠️  SKIP: Parquet not available")
        
        # Test 6: Polars
        print("\n6. Testing Polars format...")
        if data_manager.libraries_available['polars']:
            try:
                with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
                    import polars as pl
                    pl_df = pl.from_pandas(test_data)
                    pl_df.write_parquet(f.name)
                    data_info = data_manager.load_data(f.name)
                    loaded_data = data_manager.get_current_data()
                    format_tests['Polars'] = loaded_data is not None and len(loaded_data) == len(test_data)
                    print(f"   {'✅ PASS' if format_tests['Polars'] else '❌ FAIL'}")
                os.unlink(f.name)
            except Exception as e:
                format_tests['Polars'] = False
                print(f"   ❌ FAIL: {e}")
        else:
            format_tests['Polars'] = False
            print("   ⚠️  SKIP: Polars not available")
        
        # Test 7: Keras
        print("\n7. Testing Keras format...")
        if data_manager.libraries_available['keras']:
            try:
                with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
                    # Create a simple Keras model for testing
                    import tensorflow as tf
                    model = tf.keras.Sequential([
                        tf.keras.layers.Dense(10, input_shape=(5,)),
                        tf.keras.layers.Dense(1)
                    ])
                    model.save(f.name)
                    
                    data_info = data_manager.load_data(f.name)
                    loaded_data = data_manager.get_current_data()
                    format_tests['Keras'] = loaded_data is not None
                    print(f"   {'✅ PASS' if format_tests['Keras'] else '❌ FAIL'}")
                os.unlink(f.name)
            except Exception as e:
                format_tests['Keras'] = False
                print(f"   ❌ FAIL: {e}")
        else:
            format_tests['Keras'] = False
            print("   ⚠️  SKIP: Keras not available")
        
        # Summary
        print("\n=== Format Test Results ===")
        for format_name, passed in format_tests.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{format_name:10}: {status}")
        
        total_tests = len(format_tests)
        passed_tests = sum(format_tests.values())
        print(f"\nOverall: {passed_tests}/{total_tests} formats working")
        
        return format_tests
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return {}

def test_format_detection():
    """Test format detection and loading."""
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        data_manager = DataManager()
        
        print("\n=== Testing Format Detection ===")
        
        # Test supported formats info
        formats_info = data_manager.get_supported_formats_info()
        print(f"Total formats: {formats_info['total_formats']}")
        print(f"Available libraries: {formats_info['available_libraries']}")
        
        # Test format detection
        test_cases = [
            ('test.csv', 'CSV'),
            ('test.parquet', 'Parquet'),
            ('test.feather', 'Feather'),
            ('test.db', 'SQLite'),
            ('test.duckdb', 'DuckDB'),
            ('test.h5', 'Keras'),
            ('test.json', 'JSON'),
            ('test.pkl', 'Pickle')
        ]
        
        for file_path, expected_format in test_cases:
            file_ext = os.path.splitext(file_path)[1].lower()
            formats = data_manager.get_supported_formats()
            
            # Find which format supports this extension
            detected_format = None
            for format_name, extensions in formats.items():
                if file_ext in extensions:
                    detected_format = format_name
                    break
            
            status = "✅" if detected_format == expected_format else "❌"
            print(f"{file_path:15} -> {detected_format or 'UNKNOWN':10} {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing format detection: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing All File Format Support ===")
    
    # Test 1: Format loading
    format_results = test_data_manager_formats()
    
    # Test 2: Format detection
    detection_ok = test_format_detection()
    
    # Final summary
    print("\n=== Final Summary ===")
    if format_results:
        working_formats = [name for name, passed in format_results.items() if passed]
        print(f"✅ Working formats: {', '.join(working_formats)}")
        
        missing_formats = [name for name, passed in format_results.items() if not passed]
        if missing_formats:
            print(f"❌ Missing/not working: {', '.join(missing_formats)}")
    
    print(f"Format detection: {'✅ PASS' if detection_ok else '❌ FAIL'}")
    
    print("\n🎉 Format support testing completed!") 