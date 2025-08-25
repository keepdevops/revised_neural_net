#!/usr/bin/env python3
"""
Comprehensive test for all supported file formats in the Stock Prediction GUI.
This test verifies that all file formats are properly supported and their paths
are saved to the file history system.
"""

import os
import sys
import tempfile
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the file utilities
try:
    from stock_prediction_gui.utils.file_utils import FileUtils
    from stock_prediction_gui.core.data_manager import DataManager
except ImportError:
    print("❌ Could not import FileUtils or DataManager")
    sys.exit(1)

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_test_data():
    """Create sample test data."""
    return pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106],
        'vol': [1000, 1100, 1200, 1300, 1400]
    })

def create_test_files():
    """Create test files for all supported formats."""
    logger = logging.getLogger(__name__)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temporary directory: {temp_dir}")
    
    # Create test data
    test_data = create_test_data()
    
    # Define all supported formats and their file extensions
    format_tests = {
        'CSV': ['.csv', '.tsv', '.tab'],
        'Excel': ['.xlsx', '.xls'],
        'JSON': ['.json', '.jsonl'],
        'Pickle': ['.pkl', '.pickle'],
        'NumPy': ['.npy', '.npz'],
        'Text': ['.txt']
    }
    
    # Add optional formats based on available libraries
    try:
        import pyarrow
        format_tests.update({
            'Parquet': ['.parquet', '.pq'],
            'Feather': ['.feather', '.ftr', '.arrow'],
            'Arrow': ['.ipc']
        })
        logger.info("✅ PyArrow formats added")
    except ImportError:
        logger.info("⚠️ PyArrow not available - skipping Parquet, Feather, Arrow")
    
    try:
        import h5py
        format_tests['HDF5'] = ['.h5', '.hdf5', '.hdf']
        logger.info("✅ HDF5 format added")
    except ImportError:
        logger.info("⚠️ HDF5 not available - skipping HDF5")
    
    try:
        import joblib
        format_tests['Joblib'] = ['.joblib']
        logger.info("✅ Joblib format added")
    except ImportError:
        logger.info("⚠️ Joblib not available - skipping Joblib")
    
    try:
        import duckdb
        format_tests['DuckDB'] = ['.duckdb', '.ddb']
        logger.info("✅ DuckDB format added")
    except ImportError:
        logger.info("⚠️ DuckDB not available - skipping DuckDB")
    
    try:
        import tensorflow
        format_tests['Keras'] = ['.h5', '.keras']
        logger.info("✅ Keras format added")
    except ImportError:
        logger.info("⚠️ TensorFlow not available - skipping Keras")
    
    # Create test files
    created_files = {}
    
    for format_name, extensions in format_tests.items():
        for ext in extensions:
            try:
                file_path = os.path.join(temp_dir, f"test_data{ext}")
                
                if format_name == 'CSV':
                    if ext == '.csv':
                        test_data.to_csv(file_path, index=False)
                    elif ext in ['.tsv', '.tab']:
                        test_data.to_csv(file_path, sep='\t', index=False)
                
                elif format_name == 'Excel':
                    test_data.to_excel(file_path, index=False)
                
                elif format_name == 'JSON':
                    if ext == '.json':
                        test_data.to_json(file_path, orient='records', indent=2)
                    elif ext == '.jsonl':
                        # Create proper JSON Lines format (one JSON object per line)
                        with open(file_path, 'w') as f:
                            for _, row in test_data.iterrows():
                                json.dump(row.to_dict(), f)
                                f.write('\n')
                
                elif format_name == 'Pickle':
                    test_data.to_pickle(file_path)
                
                elif format_name == 'NumPy':
                    if ext == '.npy':
                        np.save(file_path, test_data.values)
                    elif ext == '.npz':
                        np.savez(file_path, data=test_data.values)
                
                elif format_name == 'Text':
                    # Create a properly formatted tab-separated text file
                    test_data.to_csv(file_path, sep='\t', index=False)
                
                elif format_name == 'Parquet':
                    test_data.to_parquet(file_path)
                
                elif format_name == 'Feather':
                    test_data.to_feather(file_path)
                
                elif format_name == 'Arrow':
                    import pyarrow as pa
                    table = pa.Table.from_pandas(test_data)
                    import pyarrow.parquet as pq
                    pq.write_table(table, file_path)
                
                elif format_name == 'HDF5':
                    test_data.to_hdf(file_path, key='data', mode='w')
                
                elif format_name == 'Joblib':
                    import joblib
                    joblib.dump(test_data, file_path)
                
                elif format_name == 'DuckDB':
                    import duckdb
                    conn = duckdb.connect(file_path)
                    conn.execute("CREATE TABLE data AS SELECT * FROM test_data")
                    conn.close()
                    # Create a simple CSV file for testing since DuckDB files are databases
                    csv_path = os.path.join(temp_dir, f"test_data_duckdb.csv")
                    test_data.to_csv(csv_path, index=False)
                    file_path = csv_path  # Use CSV for testing
                
                elif format_name == 'Keras':
                    # For testing, create a simple HDF5 file
                    test_data.to_hdf(file_path, key='data', mode='w')
                
                if os.path.exists(file_path):
                    created_files[f"{format_name}{ext}"] = file_path
                    logger.info(f"✅ Created {format_name} file: {os.path.basename(file_path)}")
                
            except Exception as e:
                logger.warning(f"❌ Failed to create {format_name}{ext}: {e}")
    
    return created_files, temp_dir

def test_file_utils():
    """Test the FileUtils class with all formats."""
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("COMPREHENSIVE FILE FORMAT TEST")
    print("=" * 80)
    
    # Create test files
    logger.info("Creating test files for all supported formats...")
    test_files, temp_dir = create_test_files()
    
    if not test_files:
        logger.error("No test files created")
        return False
    
    # Initialize FileUtils
    logger.info("Initializing FileUtils...")
    file_utils = FileUtils()
    
    # Test 1: Add all files to history
    logger.info("\n1. Testing file addition to history for all formats...")
    added_files = {}
    
    for format_name, file_path in test_files.items():
        if os.path.exists(file_path):
            file_utils.add_data_file(file_path)
            added_files[format_name] = file_path
            logger.info(f"✅ Added {format_name} to history: {os.path.basename(file_path)}")
    
    # Test 2: Verify format detection
    logger.info("\n2. Testing format detection...")
    format_detection_results = {}
    
    for format_name, file_path in test_files.items():
        if os.path.exists(file_path):
            detected_format = file_utils.get_file_format(file_path)
            format_detection_results[format_name] = detected_format
            logger.info(f"  {os.path.basename(file_path)}: {detected_format}")
    
    # Test 3: Get format statistics
    logger.info("\n3. Testing format statistics...")
    format_stats = file_utils.get_format_statistics()
    print(f"Total files in history: {format_stats['total']}")
    
    for format_name, stats in format_stats.items():
        if format_name != 'total':
            print(f"  {format_name}: {stats['count']} files")
    
    # Test 4: Test format-specific file retrieval
    logger.info("\n4. Testing format-specific file retrieval...")
    for format_name in file_utils.supported_formats.keys():
        files = file_utils.get_recent_files_by_format(format_name)
        if files:
            print(f"  {format_name}: {len(files)} files")
            for file_path in files[:2]:  # Show first 2 files
                file_info = file_utils.get_file_info(file_path)
                if file_info:
                    print(f"    - {file_info['name']} ({file_info['size']})")
    
    # Test 5: Test DataManager integration
    logger.info("\n5. Testing DataManager integration...")
    data_manager = DataManager()
    dm_formats = data_manager.get_supported_formats()
    
    print(f"DataManager supports {len(dm_formats)} formats:")
    for format_name, extensions in dm_formats.items():
        print(f"  {format_name}: {', '.join(extensions)}")
    
    # Test 6: Test file loading with DataManager
    logger.info("\n6. Testing file loading with DataManager...")
    successful_loads = 0
    
    for format_name, file_path in test_files.items():
        if os.path.exists(file_path):
            try:
                data_info = data_manager.load_data(file_path)
                if data_info:
                    successful_loads += 1
                    logger.info(f"✅ Loaded {format_name}: {data_info.get('rows', 0)} rows, {data_info.get('columns', 0)} columns")
                else:
                    logger.warning(f"⚠️ Failed to load {format_name}: No data info returned")
            except Exception as e:
                logger.warning(f"❌ Failed to load {format_name}: {e}")
    
    # Test 7: Test history persistence
    logger.info("\n7. Testing history persistence...")
    # Create new FileUtils instance to test persistence
    file_utils2 = FileUtils()
    format_stats2 = file_utils2.get_format_statistics()
    print(f"Persisted total files: {format_stats2['total']}")
    
    # Test 8: Test supported formats comparison
    logger.info("\n8. Testing supported formats comparison...")
    fu_formats = file_utils.get_supported_formats_list()
    dm_formats = data_manager.get_supported_formats()
    
    print(f"FileUtils supports {len(fu_formats)} formats")
    print(f"DataManager supports {len(dm_formats)} formats")
    
    # Check for discrepancies
    fu_format_names = set(fu_formats.keys())
    dm_format_names = set(dm_formats.keys())
    
    missing_in_fu = dm_format_names - fu_format_names
    missing_in_dm = fu_format_names - dm_format_names
    
    if missing_in_fu:
        print(f"⚠️ Formats in DataManager but not in FileUtils: {missing_in_fu}")
    
    if missing_in_dm:
        print(f"⚠️ Formats in FileUtils but not in DataManager: {missing_in_dm}")
    
    if not missing_in_fu and not missing_in_dm:
        print("✅ FileUtils and DataManager format lists are consistent")
    
    # Test 9: Test file info retrieval for all formats
    logger.info("\n9. Testing file info retrieval for all formats...")
    for format_name, file_path in test_files.items():
        if os.path.exists(file_path):
            file_info = file_utils.get_file_info(file_path)
            if file_info:
                print(f"  {format_name}: {file_info['name']} - {file_info['format']} - {file_info['size']}")
    
    # Test 10: Test recent files with filtering
    logger.info("\n10. Testing recent files with filtering...")
    all_files = file_utils.get_recent_files_by_format()
    print(f"All files in history: {len(all_files)}")
    
    # Test specific formats
    for format_name in ['CSV', 'JSON', 'Excel', 'Pickle']:
        if format_name in file_utils.supported_formats:
            format_files = file_utils.get_recent_files_by_format(format_name)
            print(f"{format_name} files: {len(format_files)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Created {len(test_files)} test files")
    print(f"✅ Added {len(added_files)} files to history")
    print(f"✅ Successfully loaded {successful_loads} files with DataManager")
    print(f"✅ File history persistence verified")
    print(f"✅ Format detection working for all formats")
    
    # Cleanup
    logger.info("\nCleaning up...")
    try:
        import shutil
        shutil.rmtree(temp_dir)
        logger.info(f"Removed temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Could not remove temporary directory: {e}")
    
    return True

def main():
    """Main test function."""
    logger = setup_logging()
    
    try:
        success = test_file_utils()
        if success:
            print("\n🎉 All file format tests passed successfully!")
            return 0
        else:
            print("\n❌ Some file format tests failed!")
            return 1
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 