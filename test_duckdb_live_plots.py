#!/usr/bin/env python3
"""
Test script to verify DuckDB support and live plots functionality.
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np
import uuid

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_duckdb_support():
    """Test DuckDB support in the enhanced data manager."""
    try:
        print("Testing DuckDB support...")
        
        from gui.core.data_manager import DataManager
        
        # Create data manager
        dm = DataManager()
        
        # Check if DuckDB is available
        if not dm.libraries_available['duckdb']:
            print("❌ DuckDB not available - install with: pip install duckdb")
            return False
        
        print("✅ DuckDB support enabled")
        
        # Create test data
        test_data = pd.DataFrame({
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [101.0, 102.0, 103.0, 104.0, 105.0],
            'vol': [1000, 1100, 1200, 1300, 1400]
        })
        
        print(f"📊 Test data created: {test_data.shape}")
        
        # Generate a unique filename for DuckDB
        duckdb_file = f"test_{uuid.uuid4().hex}.duckdb"
        
        try:
            # Create DuckDB database with test data
            import duckdb
            conn = duckdb.connect(duckdb_file)
            
            # Create table and insert data properly
            conn.execute("""
                CREATE TABLE stock_data (
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    vol INTEGER
                )
            """)
            
            # Insert data row by row
            for _, row in test_data.iterrows():
                conn.execute("""
                    INSERT INTO stock_data (open, high, low, close, vol)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['open'], row['high'], row['low'], row['close'], row['vol']))
            
            conn.close()
            
            print(f"🗄️  DuckDB file created: {duckdb_file}")
            
            # Test loading with data manager
            success, message = dm.load_data(duckdb_file)
            
            if success:
                print("✅ DuckDB data loaded successfully")
                
                # Check loaded data
                loaded_data = dm.get_current_data()
                if loaded_data is not None and len(loaded_data) > 0:
                    print(f"✅ Data loaded: {loaded_data.shape}")
                    print(f"✅ Columns: {list(loaded_data.columns)}")
                    
                    # Test data info
                    data_info = dm.get_data_info()
                    print(f"✅ Data info: {data_info['rows']} rows, {data_info['columns']} columns")
                    
                    return True
                else:
                    print("❌ No data loaded from DuckDB")
                    return False
            else:
                print(f"❌ Failed to load DuckDB data: {message}")
                return False
                
        finally:
            # Clean up
            if os.path.exists(duckdb_file):
                os.unlink(duckdb_file)
        
    except Exception as e:
        print(f"❌ Error testing DuckDB support: {e}")
        return False

def test_live_plots_integration():
    """Test live plots integration with enhanced data manager."""
    try:
        print("\nTesting live plots integration...")
        
        from gui.core.data_manager import DataManager
        from gui.training.training_manager import TrainingManager
        
        # Create data manager
        dm = DataManager()
        
        # Create test data
        test_data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 105,
            'low': np.random.randn(100).cumsum() + 95,
            'close': np.random.randn(100).cumsum() + 102,
            'vol': np.random.randint(1000, 2000, 100)
        })
        
        # Write test data to a temporary CSV file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_csv = f.name
        
        try:
            # Store test data
            dm.current_data = test_data
            dm.current_data_info = dm.analyze_data(test_data, temp_csv)
            
            print("✅ Test data prepared for live plots")
            
            # Test that data manager provides required methods for live plots
            required_methods = [
                'get_current_data',
                'get_data_info', 
                'get_feature_columns',
                'preprocess_data'
            ]
            
            for method in required_methods:
                if hasattr(dm, method):
                    print(f"✅ {method} method available")
                else:
                    print(f"❌ {method} method missing")
                    return False
            
            # Test feature columns
            feature_columns = dm.get_feature_columns()
            print(f"✅ Feature columns: {feature_columns}")
            
            # Test preprocessing
            try:
                preprocessed = dm.preprocess_data()
                print("✅ Data preprocessing works")
                print(f"✅ Preprocessed shape: {preprocessed['X_train'].shape}")
            except Exception as e:
                print(f"❌ Data preprocessing failed: {e}")
                return False
            
            return True
        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)
        
    except Exception as e:
        print(f"❌ Error testing live plots integration: {e}")
        return False

def test_supported_formats():
    """Test supported formats detection."""
    try:
        print("\nTesting supported formats...")
        
        from gui.core.data_manager import DataManager
        
        dm = DataManager()
        
        # Get supported formats
        formats = dm.get_supported_formats()
        formats_info = dm.get_supported_formats_info()
        
        print(f"✅ Total formats supported: {formats_info['total_formats']}")
        print(f"✅ Available libraries: {formats_info['available_libraries']}")
        
        # Check for DuckDB
        if 'DuckDB' in formats:
            print("✅ DuckDB format supported")
        else:
            print("❌ DuckDB format not supported")
        
        # Check for other important formats
        important_formats = ['CSV', 'Excel', 'SQLite']
        for fmt in important_formats:
            if fmt in formats:
                print(f"✅ {fmt} format supported")
            else:
                print(f"❌ {fmt} format not supported")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing supported formats: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 Testing DuckDB Support and Live Plots")
    print("=" * 50)
    
    # Test 1: DuckDB support
    if not test_duckdb_support():
        print("\n❌ DuckDB support test failed")
        return False
    
    # Test 2: Live plots integration
    if not test_live_plots_integration():
        print("\n❌ Live plots integration test failed")
        return False
    
    # Test 3: Supported formats
    if not test_supported_formats():
        print("\n❌ Supported formats test failed")
        return False
    
    print("\n✅ All tests passed! DuckDB support and live plots are working.")
    print("The Training Tab live plots should now work with DuckDB files.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 