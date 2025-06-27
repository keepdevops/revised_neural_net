#!/usr/bin/env python3
"""
Test script for HDF5 loading fix
"""

import os
import sys
import tempfile
import numpy as np
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_hdf5_fix():
    """Test the HDF5 loading fix with different file structures."""
    print("🧪 Testing HDF5 loading fix...")
    
    try:
        # Check if h5py is available
        try:
            import h5py
            print("✅ h5py is available")
        except ImportError:
            print("❌ h5py not available - skipping HDF5 tests")
            return True
        
        from stock_prediction_gui.core.data_manager import DataManager
        
        data_manager = DataManager()
        
        # Test 1: HDF5 file with dataset at root level
        print("\n1️⃣ Testing HDF5 file with dataset at root level...")
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            h5_file = f.name
        
        try:
            with h5py.File(h5_file, 'w') as f:
                # Create a simple dataset at root level
                data = np.random.rand(100, 5)
                f.create_dataset('data', data=data)
            
            # Test loading
            df = data_manager._load_hdf5(h5_file)
            print(f"✅ Loaded dataset at root level: {df.shape}")
            
        except Exception as e:
            print(f"❌ Error loading dataset at root level: {e}")
            return False
        finally:
            os.unlink(h5_file)
        
        # Test 2: HDF5 file with dataset in a group
        print("\n2️⃣ Testing HDF5 file with dataset in a group...")
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            h5_file = f.name
        
        try:
            with h5py.File(h5_file, 'w') as f:
                # Create a group and put dataset inside it
                group = f.create_group('my_group')
                data = np.random.rand(100, 5)
                group.create_dataset('data', data=data)
            
            # Test loading
            df = data_manager._load_hdf5(h5_file)
            print(f"✅ Loaded dataset in group: {df.shape}")
            
        except Exception as e:
            print(f"❌ Error loading dataset in group: {e}")
            return False
        finally:
            os.unlink(h5_file)
        
        # Test 3: HDF5 file with multiple groups and datasets
        print("\n3️⃣ Testing HDF5 file with multiple groups and datasets...")
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            h5_file = f.name
        
        try:
            with h5py.File(h5_file, 'w') as f:
                # Create multiple groups
                group1 = f.create_group('group1')
                group2 = f.create_group('group2')
                
                # Create datasets in different groups
                data1 = np.random.rand(50, 3)
                data2 = np.random.rand(50, 4)
                
                group1.create_dataset('data1', data=data1)
                group2.create_dataset('data2', data=data2)
            
            # Test loading
            df = data_manager._load_hdf5(h5_file)
            print(f"✅ Loaded dataset from multiple groups: {df.shape}")
            
        except Exception as e:
            print(f"❌ Error loading from multiple groups: {e}")
            return False
        finally:
            os.unlink(h5_file)
        
        # Test 4: HDF5 file with only groups (no datasets)
        print("\n4️⃣ Testing HDF5 file with only groups (no datasets)...")
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            h5_file = f.name
        
        try:
            with h5py.File(h5_file, 'w') as f:
                # Create only groups, no datasets
                group1 = f.create_group('group1')
                group2 = f.create_group('group2')
                subgroup = group1.create_group('subgroup')
            
            # Test loading - should raise an error
            try:
                df = data_manager._load_hdf5(h5_file)
                print("❌ Should have raised an error for no datasets")
                return False
            except ValueError as e:
                if "No datasets found" in str(e):
                    print("✅ Correctly handled HDF5 file with no datasets")
                else:
                    print(f"❌ Unexpected error: {e}")
                    return False
            
        except Exception as e:
            print(f"❌ Error creating test file: {e}")
            return False
        finally:
            os.unlink(h5_file)
        
        # Test 5: HDF5 file with 1D dataset
        print("\n5️⃣ Testing HDF5 file with 1D dataset...")
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            h5_file = f.name
        
        try:
            with h5py.File(h5_file, 'w') as f:
                # Create a 1D dataset
                data = np.random.rand(100)
                f.create_dataset('data', data=data)
            
            # Test loading
            df = data_manager._load_hdf5(h5_file)
            print(f"✅ Loaded 1D dataset: {df.shape}")
            
        except Exception as e:
            print(f"❌ Error loading 1D dataset: {e}")
            return False
        finally:
            os.unlink(h5_file)
        
        # Test 6: HDF5 file with 3D dataset
        print("\n6️⃣ Testing HDF5 file with 3D dataset...")
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            h5_file = f.name
        
        try:
            with h5py.File(h5_file, 'w') as f:
                # Create a 3D dataset
                data = np.random.rand(20, 10, 5)
                f.create_dataset('data', data=data)
            
            # Test loading
            df = data_manager._load_hdf5(h5_file)
            print(f"✅ Loaded 3D dataset: {df.shape}")
            
        except Exception as e:
            print(f"❌ Error loading 3D dataset: {e}")
            return False
        finally:
            os.unlink(h5_file)
        
        print("\n✅ All HDF5 loading tests passed!")
        print("\n📝 Summary:")
        print("   - Dataset at root level: ✅ Working")
        print("   - Dataset in group: ✅ Working")
        print("   - Multiple groups: ✅ Working")
        print("   - No datasets error handling: ✅ Working")
        print("   - 1D datasets: ✅ Working")
        print("   - 3D datasets: ✅ Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in HDF5 fix test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hdf5_fix()
    if success:
        print("\n🎉 HDF5 fix tests completed!")
    else:
        print("\n💥 HDF5 fix tests failed!") 