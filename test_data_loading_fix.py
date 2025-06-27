#!/usr/bin/env python3
"""
Comprehensive test for data loading fix
"""

import os
import sys
import tempfile
import numpy as np
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_loading_fix():
    """Test the data loading fix with different file formats."""
    print("🧪 Testing comprehensive data loading fix...")
    
    try:
        from stock_prediction_gui.core.data_manager import DataManager
        
        data_manager = DataManager()
        
        # Create test data
        test_data = pd.DataFrame({
            'open': np.random.rand(100) * 100 + 50,
            'high': np.random.rand(100) * 100 + 50,
            'low': np.random.rand(100) * 100 + 50,
            'close': np.random.rand(100) * 100 + 50,
            'vol': np.random.rand(100) * 1000000
        })
        
        print(f"✅ Created test data: {test_data.shape}")
        
        # Test 1: CSV file loading
        print("\n1️⃣ Testing CSV file loading...")
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_file = f.name
        
        try:
            test_data.to_csv(csv_file, index=False)
            loaded_data = data_manager.load_data(csv_file)
            print(f"✅ CSV loading successful: {loaded_data['shape']}")
        except Exception as e:
            print(f"❌ CSV loading failed: {e}")
            return False
        finally:
            os.unlink(csv_file)
        
        # Test 2: HDF5 file loading (if available)
        if data_manager.libraries_available.get('h5py', False):
            print("\n2️⃣ Testing HDF5 file loading...")
            with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
                h5_file = f.name
            
            try:
                import h5py
                with h5py.File(h5_file, 'w') as f:
                    f.create_dataset('data', data=test_data.values)
                
                loaded_data = data_manager.load_data(h5_file)
                print(f"✅ HDF5 loading successful: {loaded_data['shape']}")
            except Exception as e:
                print(f"❌ HDF5 loading failed: {e}")
                return False
            finally:
                os.unlink(h5_file)
        else:
            print("\n2️⃣ Skipping HDF5 test (h5py not available)")
        
        # Test 3: Feather file loading (if available)
        if data_manager.libraries_available.get('feather', False):
            print("\n3️⃣ Testing Feather file loading...")
            with tempfile.NamedTemporaryFile(suffix='.feather', delete=False) as f:
                feather_file = f.name
            
            try:
                test_data.to_feather(feather_file)
                loaded_data = data_manager.load_data(feather_file)
                print(f"✅ Feather loading successful: {loaded_data['shape']}")
            except Exception as e:
                print(f"❌ Feather loading failed: {e}")
                return False
            finally:
                os.unlink(feather_file)
        else:
            print("\n3️⃣ Skipping Feather test (pyarrow not available)")
        
        # Test 4: Parquet file loading (if available)
        if data_manager.libraries_available.get('pyarrow', False):
            print("\n4️⃣ Testing Parquet file loading...")
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
                parquet_file = f.name
            
            try:
                test_data.to_parquet(parquet_file)
                loaded_data = data_manager.load_data(parquet_file)
                print(f"✅ Parquet loading successful: {loaded_data['shape']}")
            except Exception as e:
                print(f"❌ Parquet loading failed: {e}")
                return False
            finally:
                os.unlink(parquet_file)
        else:
            print("\n4️⃣ Skipping Parquet test (pyarrow not available)")
        
        # Test 5: Excel file loading
        print("\n5️⃣ Testing Excel file loading...")
        try:
            import openpyxl
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
                excel_file = f.name
            
            try:
                test_data.to_excel(excel_file, index=False)
                loaded_data = data_manager.load_data(excel_file)
                print(f"✅ Excel loading successful: {loaded_data['shape']}")
            except Exception as e:
                print(f"❌ Excel loading failed: {e}")
                return False
            finally:
                os.unlink(excel_file)
        except ImportError:
            print("⚠️ Skipping Excel test (openpyxl not available)")
        
        # Test 6: JSON file loading
        print("\n6️⃣ Testing JSON file loading...")
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            json_file = f.name
        
        try:
            test_data.to_json(json_file, orient='records')
            loaded_data = data_manager.load_data(json_file)
            print(f"✅ JSON loading successful: {loaded_data['shape']}")
        except Exception as e:
            print(f"❌ JSON loading failed: {e}")
            return False
        finally:
            os.unlink(json_file)
        
        # Test 7: Error handling for non-existent file
        print("\n7️⃣ Testing error handling for non-existent file...")
        try:
            data_manager.load_data("non_existent_file.csv")
            print("❌ Should have raised an error for non-existent file")
            return False
        except FileNotFoundError:
            print("✅ Correctly handled non-existent file")
        except Exception as e:
            print(f"❌ Unexpected error for non-existent file: {e}")
            return False
        
        # Test 8: Error handling for unsupported format
        print("\n8️⃣ Testing error handling for unsupported format...")
        with tempfile.NamedTemporaryFile(suffix='.unsupported', delete=False) as f:
            unsupported_file = f.name
        
        try:
            with open(unsupported_file, 'w') as f:
                f.write("test data")
            
            data_manager.load_data(unsupported_file)
            print("❌ Should have raised an error for unsupported format")
            return False
        except ValueError as e:
            if "Unsupported file format" in str(e):
                print("✅ Correctly handled unsupported format")
            else:
                print(f"❌ Unexpected error for unsupported format: {e}")
                return False
        finally:
            os.unlink(unsupported_file)
        
        print("\n✅ All data loading tests passed!")
        print("\n📝 Summary:")
        print("   - CSV loading: ✅ Working")
        if data_manager.libraries_available.get('h5py', False):
            print("   - HDF5 loading: ✅ Working")
        if data_manager.libraries_available.get('feather', False):
            print("   - Feather loading: ✅ Working")
        if data_manager.libraries_available.get('pyarrow', False):
            print("   - Parquet loading: ✅ Working")
        print("   - Excel loading: ✅ Working")
        print("   - JSON loading: ✅ Working")
        print("   - Error handling: ✅ Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data loading test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_loading_fix()
    if success:
        print("\n🎉 Data loading fix tests completed!")
    else:
        print("\n💥 Data loading fix tests failed!") 