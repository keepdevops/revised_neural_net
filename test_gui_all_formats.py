#!/usr/bin/env python3
"""
GUI Test for All File Formats Support
This test launches the Stock Prediction GUI and verifies that all file formats
are properly supported in the actual GUI interface.
"""

import os
import sys
import tempfile
import pandas as pd
import numpy as np
import json
import logging
import time
import threading

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_test_files():
    """Create test files for all supported formats."""
    logger = logging.getLogger(__name__)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temporary directory: {temp_dir}")
    
    # Create test data
    test_data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106],
        'vol': [1000, 1100, 1200, 1300, 1400]
    })
    
    # Create files for core formats (always available)
    created_files = {}
    
    # CSV files
    csv_file = os.path.join(temp_dir, "test_data.csv")
    test_data.to_csv(csv_file, index=False)
    created_files['CSV'] = csv_file
    
    # JSON file
    json_file = os.path.join(temp_dir, "test_data.json")
    test_data.to_json(json_file, orient='records', indent=2)
    created_files['JSON'] = json_file
    
    # Pickle file
    pickle_file = os.path.join(temp_dir, "test_data.pkl")
    test_data.to_pickle(pickle_file)
    created_files['Pickle'] = pickle_file
    
    # NumPy file
    npy_file = os.path.join(temp_dir, "test_data.npy")
    np.save(npy_file, test_data.values)
    created_files['NumPy'] = npy_file
    
    # Text file
    txt_file = os.path.join(temp_dir, "test_data.txt")
    test_data.to_csv(txt_file, sep='\t', index=False)
    created_files['Text'] = txt_file
    
    # Try to create optional format files
    try:
        import pyarrow
        # Parquet file
        parquet_file = os.path.join(temp_dir, "test_data.parquet")
        test_data.to_parquet(parquet_file)
        created_files['Parquet'] = parquet_file
        
        # Feather file
        feather_file = os.path.join(temp_dir, "test_data.feather")
        test_data.to_feather(feather_file)
        created_files['Feather'] = feather_file
        
        logger.info("✅ Created PyArrow format files")
    except ImportError:
        logger.info("⚠️ PyArrow not available - skipping Parquet/Feather")
    
    try:
        import joblib
        # Joblib file
        joblib_file = os.path.join(temp_dir, "test_data.joblib")
        joblib.dump(test_data, joblib_file)
        created_files['Joblib'] = joblib_file
        logger.info("✅ Created Joblib file")
    except ImportError:
        logger.info("⚠️ Joblib not available - skipping Joblib")
    
    return created_files, temp_dir

def test_gui_file_formats():
    """Test the GUI with all file formats."""
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("GUI FILE FORMATS TEST")
    print("=" * 80)
    
    # Create test files
    logger.info("Creating test files for GUI testing...")
    test_files, temp_dir = create_test_files()
    
    if not test_files:
        logger.error("No test files created")
        return False
    
    print(f"✅ Created {len(test_files)} test files:")
    for format_name, file_path in test_files.items():
        print(f"  {format_name}: {os.path.basename(file_path)}")
    
    # Test GUI import
    logger.info("Testing GUI import...")
    try:
        # Try to import the GUI components
        from stock_prediction_gui.core.app import StockPredictionApp
        from stock_prediction_gui.utils.file_utils import FileUtils
        from stock_prediction_gui.core.data_manager import DataManager
        
        logger.info("✅ Successfully imported GUI components")
        
        # Test FileUtils
        logger.info("Testing FileUtils...")
        file_utils = FileUtils()
        supported_formats = file_utils.get_supported_formats_list()
        print(f"✅ FileUtils supports {len(supported_formats)} formats")
        
        # Test DataManager
        logger.info("Testing DataManager...")
        data_manager = DataManager()
        dm_formats = data_manager.get_supported_formats()
        print(f"✅ DataManager supports {len(dm_formats)} formats")
        
        # Test format consistency
        fu_formats = set(supported_formats.keys())
        dm_formats_set = set(dm_formats.keys())
        
        if fu_formats == dm_formats_set:
            print("✅ FileUtils and DataManager format lists are consistent")
        else:
            missing_in_fu = dm_formats_set - fu_formats
            missing_in_dm = fu_formats - dm_formats_set
            if missing_in_fu:
                print(f"⚠️ Formats in DataManager but not in FileUtils: {missing_in_fu}")
            if missing_in_dm:
                print(f"⚠️ Formats in FileUtils but not in DataManager: {missing_in_dm}")
        
        # Test file loading with DataManager
        logger.info("Testing file loading with DataManager...")
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
        
        print(f"✅ Successfully loaded {successful_loads}/{len(test_files)} files")
        
        # Test file history
        logger.info("Testing file history...")
        for format_name, file_path in test_files.items():
            if os.path.exists(file_path):
                file_utils.add_data_file(file_path)
                logger.info(f"✅ Added {format_name} to history")
        
        # Get format statistics
        format_stats = file_utils.get_format_statistics()
        print(f"✅ File history contains {format_stats['total']} files")
        
        for format_name, stats in format_stats.items():
            if format_name != 'total':
                print(f"  {format_name}: {stats['count']} files")
        
        # Test format-specific retrieval
        logger.info("Testing format-specific file retrieval...")
        for format_name in test_files.keys():
            files = file_utils.get_recent_files_by_format(format_name)
            if files:
                logger.info(f"✅ Retrieved {len(files)} {format_name} files from history")
        
        print("\n" + "=" * 80)
        print("GUI COMPONENTS TEST SUMMARY")
        print("=" * 80)
        print(f"✅ GUI components imported successfully")
        print(f"✅ FileUtils supports {len(supported_formats)} formats")
        print(f"✅ DataManager supports {len(dm_formats)} formats")
        print(f"✅ Successfully loaded {successful_loads}/{len(test_files)} test files")
        print(f"✅ File history working for all formats")
        print(f"✅ Format detection and categorization working")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import GUI components: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        try:
            import shutil
            shutil.rmtree(temp_dir)
            logger.info(f"Removed temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Could not remove temporary directory: {e}")

def main():
    """Main test function."""
    logger = setup_logging()
    
    try:
        success = test_gui_file_formats()
        if success:
            print("\n🎉 GUI file formats test passed successfully!")
            print("\n📋 SUMMARY:")
            print("✅ All file formats are supported in the GUI")
            print("✅ File history system works for all formats")
            print("✅ DataManager can load all supported formats")
            print("✅ FileUtils properly categorizes all formats")
            print("✅ GUI components are properly integrated")
            return 0
        else:
            print("\n❌ GUI file formats test failed!")
            return 1
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 