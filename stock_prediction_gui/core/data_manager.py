"""
Enhanced Data Manager for the Stock Prediction GUI.
Supports multiple modern data file formats including Feather.
"""

import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime
import warnings

# Suppress warnings for optional imports
warnings.filterwarnings('ignore', category=ImportWarning)

class DataManager:
    """Manages data operations with support for multiple file formats including Feather."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_data = None
        self.current_data_info = None
        self.data_cache = {}
        
        # Initialize optional libraries
        self._init_optional_libraries()
    
    def _init_optional_libraries(self):
        """Initialize optional data libraries."""
        self.libraries_available = {
            'duckdb': False,
            'pyarrow': False,
            'polars': False,
            'sqlite3': True,  # Built-in
            'h5py': False,
            'pickle': True,   # Built-in
            'joblib': False,
            'keras': False,
            'tensorflow': False,
            'feather': False  # Will be True if pyarrow is available
        }
        
        # Try to import optional libraries
        try:
            import duckdb
            self.libraries_available['duckdb'] = True
            self.logger.info("DuckDB support enabled")
        except ImportError:
            self.logger.info("DuckDB not available - install with: pip install duckdb")
        
        try:
            import pyarrow
            self.libraries_available['pyarrow'] = True
            self.libraries_available['feather'] = True  # Feather requires pyarrow
            self.logger.info("PyArrow support enabled (includes Feather)")
        except ImportError:
            self.logger.info("PyArrow not available - install with: pip install pyarrow")
        
        try:
            import polars
            self.libraries_available['polars'] = True
            self.logger.info("Polars support enabled")
        except ImportError:
            self.logger.info("Polars not available - install with: pip install polars")
        
        try:
            import h5py
            self.libraries_available['h5py'] = True
            self.logger.info("HDF5 support enabled")
        except ImportError:
            self.logger.info("HDF5 not available - install with: pip install h5py")
        
        try:
            import joblib
            self.libraries_available['joblib'] = True
            self.logger.info("Joblib support enabled")
        except ImportError:
            self.logger.info("Joblib not available - install with: pip install joblib")
        
        try:
            import tensorflow as tf
            self.libraries_available['tensorflow'] = True
            self.libraries_available['keras'] = True
            self.logger.info("TensorFlow/Keras support enabled")
        except ImportError:
            self.logger.info("TensorFlow not available - install with: pip install tensorflow")
    
    def get_supported_formats(self):
        """Get list of supported file formats."""
        formats = {
            'CSV': ['.csv'],
            'Excel': ['.xlsx', '.xls', '.xlsm'],
            'Parquet': ['.parquet', '.pq'],
            'Feather': ['.feather', '.ftr', '.arrow'],  # Multiple extensions for Feather
            'HDF5': ['.h5', '.hdf5', '.hdf'],
            'Pickle': ['.pkl', '.pickle'],
            'Joblib': ['.joblib'],
            'JSON': ['.json'],
            'SQLite': ['.db', '.sqlite', '.sqlite3'],
            'DuckDB': ['.duckdb', '.ddb'],
            'Arrow': ['.arrow', '.ipc'],
            'Keras': ['.h5', '.keras'],
            'NumPy': ['.npy', '.npz'],
            'Text': ['.txt', '.tsv', '.tab']
        }
        
        # Filter based on available libraries
        if not self.libraries_available['pyarrow']:
            formats.pop('Parquet', None)
            formats.pop('Feather', None)
            formats.pop('Arrow', None)
        
        if not self.libraries_available['h5py']:
            formats.pop('HDF5', None)
        
        if not self.libraries_available['joblib']:
            formats.pop('Joblib', None)
        
        if not self.libraries_available['duckdb']:
            formats.pop('DuckDB', None)
        
        if not self.libraries_available['keras']:
            formats.pop('Keras', None)
        
        return formats
    
    def load_data(self, file_path):
        """Load data from file with format detection."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check if data is already cached
            if file_path in self.data_cache:
                self.current_data = self.data_cache[file_path]['data']
                self.current_data_info = self.data_cache[file_path]['info']
                self.current_data_info['last_accessed'] = datetime.now()
                return self.current_data_info
            
            # Detect file format and load
            file_ext = os.path.splitext(file_path)[1].lower()
            data = self._load_by_format(file_path, file_ext)
            
            # Validate data
            if data is None or len(data) == 0:
                raise ValueError("Data file is empty or could not be loaded")
            
            # Convert to pandas DataFrame if needed
            if not isinstance(data, pd.DataFrame):
                data = pd.DataFrame(data)
            
            # Store the data
            self.current_data = data
            
            # Analyze data
            self.current_data_info = self.analyze_data(data, file_path)
            
            # Cache the data
            self.data_cache[file_path] = {
                'data': data,
                'info': self.current_data_info
            }
            
            return self.current_data_info
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def _load_by_format(self, file_path, file_ext):
        """Load data based on file format."""
        
        # CSV files
        if file_ext in ['.csv', '.tsv', '.tab']:
            return pd.read_csv(file_path)
        
        # Excel files
        elif file_ext in ['.xlsx', '.xls', '.xlsm']:
            return pd.read_excel(file_path)
        
        # JSON files
        elif file_ext == '.json':
            return pd.read_json(file_path)
        
        # NumPy files
        elif file_ext == '.npy':
            return pd.DataFrame(np.load(file_path))
        elif file_ext == '.npz':
            npz_data = np.load(file_path)
            # Convert to DataFrame with first array
            first_key = list(npz_data.keys())[0]
            return pd.DataFrame(npz_data[first_key])
        
        # Pickle files
        elif file_ext in ['.pkl', '.pickle']:
            return pd.read_pickle(file_path)
        
        # SQLite files
        elif file_ext in ['.db', '.sqlite', '.sqlite3']:
            return self._load_sqlite(file_path)
        
        # Feather files (PyArrow) - Enhanced support
        elif file_ext in ['.feather', '.ftr', '.arrow'] and self.libraries_available['feather']:
            return self._load_feather(file_path)
        
        # Parquet files (PyArrow)
        elif file_ext in ['.parquet', '.pq'] and self.libraries_available['pyarrow']:
            return pd.read_parquet(file_path)
        
        # Arrow files (PyArrow)
        elif file_ext in ['.ipc'] and self.libraries_available['pyarrow']:
            import pyarrow.parquet as pq
            return pq.read_table(file_path).to_pandas()
        
        # HDF5 files
        elif file_ext in ['.h5', '.hdf5', '.hdf'] and self.libraries_available['h5py']:
            return self._load_hdf5(file_path)
        
        # Joblib files
        elif file_ext == '.joblib' and self.libraries_available['joblib']:
            import joblib
            return joblib.load(file_path)
        
        # DuckDB files
        elif file_ext in ['.duckdb', '.ddb'] and self.libraries_available['duckdb']:
            return self._load_duckdb(file_path)
        
        # Keras/TensorFlow files
        elif file_ext in ['.h5', '.keras'] and self.libraries_available['keras']:
            return self._load_keras(file_path)
        
        # Polars files (if available)
        elif self.libraries_available['polars']:
            try:
                import polars as pl
                if file_ext in ['.parquet', '.pq']:
                    return pl.read_parquet(file_path).to_pandas()
                elif file_ext in ['.csv', '.tsv']:
                    return pl.read_csv(file_path).to_pandas()
            except:
                pass
        
        # Text files (fallback)
        elif file_ext in ['.txt']:
            return pd.read_csv(file_path, sep=None, engine='python')
        
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _load_feather(self, file_path):
        """Load data from Feather file with enhanced features."""
        try:
            import pyarrow.feather as feather
            import pyarrow as pa
            
            # Try to read with metadata
            try:
                # Read with metadata to get additional info
                table = feather.read_feather(file_path, memory_map=True)
                data = table.to_pandas()
                
                # Store metadata for analysis
                self.feather_metadata = {
                    'schema': table.schema,
                    'num_rows': table.num_rows,
                    'num_columns': table.num_columns,
                    'column_names': table.column_names
                }
                
                return data
                
            except Exception as e:
                # Fallback to simple read
                self.logger.warning(f"Could not read Feather with metadata: {e}")
                return pd.read_feather(file_path)
                
        except ImportError:
            raise ImportError("PyArrow is required for Feather support. Install with: pip install pyarrow")
    
    def save_as_feather(self, data, file_path, compression='lz4'):
        """Save data as Feather file with compression options."""
        try:
            if not self.libraries_available['feather']:
                raise ImportError("PyArrow is required for Feather support")
            
            import pyarrow as pa
            import pyarrow.feather as feather
            
            # Convert DataFrame to Arrow table
            table = pa.Table.from_pandas(data)
            
            # Save with compression
            feather.write_feather(table, file_path, compression=compression)
            
            self.logger.info(f"Data saved as Feather file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving Feather file: {e}")
            raise
    
    def get_feather_info(self, file_path):
        """Get detailed information about a Feather file."""
        try:
            if not self.libraries_available['feather']:
                return {"error": "PyArrow not available"}
            
            import pyarrow.feather as feather
            import pyarrow as pa
            
            # Read metadata without loading full data
            table = feather.read_feather(file_path, memory_map=True)
            
            info = {
                'format': 'Feather',
                'num_rows': table.num_rows,
                'num_columns': table.num_columns,
                'column_names': table.column_names,
                'schema': str(table.schema),
                'file_size': f"{os.path.getsize(file_path) / (1024*1024):.2f} MB"
            }
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def _load_sqlite(self, file_path):
        """Load data from SQLite database."""
        import sqlite3
        
        # Connect to database
        conn = sqlite3.connect(file_path)
        
        # Get table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            raise ValueError("No tables found in SQLite database")
        
        # Load first table (or let user choose)
        table_name = tables[0][0]
        data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        conn.close()
        return data
    
    def _load_hdf5(self, file_path):
        """Load data from HDF5 file."""
        import h5py
        
        with h5py.File(file_path, 'r') as f:
            # Get dataset names
            datasets = list(f.keys())
            
            if not datasets:
                raise ValueError("No datasets found in HDF5 file")
            
            # Load first dataset
            dataset_name = datasets[0]
            data = f[dataset_name][:]
            
            # Convert to DataFrame
            if len(data.shape) == 1:
                return pd.DataFrame({dataset_name: data})
            elif len(data.shape) == 2:
                return pd.DataFrame(data)
            else:
                # For 3D+ data, flatten
                return pd.DataFrame(data.reshape(data.shape[0], -1))
    
    def _load_duckdb(self, file_path):
        """Load data from DuckDB database."""
        import duckdb
        
        # Connect to database
        conn = duckdb.connect(file_path)
        
        # Get table names
        tables = conn.execute("SHOW TABLES").fetchall()
        
        if not tables:
            raise ValueError("No tables found in DuckDB database")
        
        # Load first table
        table_name = tables[0][0]
        data = conn.execute(f"SELECT * FROM {table_name}").fetchdf()
        
        conn.close()
        return data
    
    def _load_keras(self, file_path):
        """Load data from Keras model file."""
        import tensorflow as tf
        
        try:
            # Try to load as model first
            model = tf.keras.models.load_model(file_path)
            
            # Extract weights as data
            weights_data = {}
            for i, layer in enumerate(model.layers):
                if layer.weights:
                    weights = layer.get_weights()
                    for j, weight in enumerate(weights):
                        weights_data[f'layer_{i}_weight_{j}'] = weight.flatten()
            
            # Convert to DataFrame
            max_length = max(len(v) for v in weights_data.values())
            padded_data = {}
            for key, values in weights_data.items():
                padded_values = np.pad(values, (0, max_length - len(values)), mode='constant', constant_values=np.nan)
                padded_data[key] = padded_values
            
            return pd.DataFrame(padded_data)
            
        except:
            # If not a model, try to load as dataset
            try:
                dataset = tf.data.Dataset.load(file_path)
                # Convert dataset to numpy arrays
                data_list = []
                for batch in dataset.take(100):  # Take first 100 batches
                    if isinstance(batch, (tuple, list)):
                        data_list.extend(batch)
                    else:
                        data_list.append(batch)
                
                # Convert to DataFrame
                if data_list:
                    return pd.DataFrame(data_list)
                else:
                    raise ValueError("Could not extract data from Keras file")
                    
            except:
                raise ValueError("Could not load Keras file as model or dataset")
    
    def analyze_data(self, data, file_path):
        """Analyze the loaded data."""
        try:
            # Basic file info
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # Data info
            rows, columns = data.shape
            numeric_columns = list(data.select_dtypes(include=[np.number]).columns)
            categorical_columns = list(data.select_dtypes(include=['object']).columns)
            datetime_columns = list(data.select_dtypes(include=['datetime']).columns)
            
            # Missing values
            missing_values = data.isnull().sum().to_dict()
            
            # Data types
            data_types = data.dtypes.to_dict()
            
            # Summary statistics for numeric columns
            summary_stats = {}
            if len(numeric_columns) > 0:
                summary_stats = data[numeric_columns].describe().to_dict()
            
            # Memory usage
            memory_usage = data.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
            
            # Feather-specific info
            feather_info = {}
            if hasattr(self, 'feather_metadata'):
                feather_info = {
                    'feather_schema': str(self.feather_metadata.get('schema', '')),
                    'feather_columns': self.feather_metadata.get('column_names', [])
                }
            
            return {
                'file_path': file_path,
                'file_size': f"{file_size_mb:.2f} MB",
                'memory_usage': f"{memory_usage:.2f} MB",
                'rows': rows,
                'columns': columns,
                'shape': (rows, columns),
                'numeric_columns': numeric_columns,
                'categorical_columns': categorical_columns,
                'datetime_columns': datetime_columns,
                'missing_values': missing_values,
                'data_types': data_types,
                'summary_stats': summary_stats,
                'feather_info': feather_info,
                'last_accessed': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing data: {e}")
            raise
    
    def get_data_info(self):
        """Get information about the currently loaded data."""
        if self.current_data_info is None:
            return {
                'file_path': 'No data loaded',
                'file_size': 'N/A',
                'rows': 0,
                'columns': 0,
                'shape': (0, 0),
                'numeric_columns': [],
                'categorical_columns': [],
                'datetime_columns': [],
                'missing_values': {},
                'data_types': {},
                'summary_stats': {},
                'feather_info': {}
            }
        return self.current_data_info
    
    def get_current_data(self):
        """Get the currently loaded data."""
        return self.current_data
    
    def get_supported_formats_info(self):
        """Get information about supported formats and available libraries."""
        formats = self.get_supported_formats()
        info = {
            'formats': formats,
            'libraries': self.libraries_available,
            'total_formats': len(formats),
            'available_libraries': sum(self.libraries_available.values()),
            'feather_available': self.libraries_available['feather']
        }
        return info
    
    def validate_data(self, file_path):
        """Validate data file."""
        try:
            data_info = self.load_data(file_path)
            
            # Check for required columns (basic OHLCV)
            required_columns = ['open', 'high', 'low', 'close', 'vol']
            available_columns = [col.lower() for col in data_info.get('numeric_columns', [])]
            missing_required = [col for col in required_columns if col not in available_columns]
            
            if missing_required:
                return False, f"Missing required columns: {missing_required}"
            
            # Check for sufficient data
            if data_info['rows'] < 100:
                return False, "Insufficient data (need at least 100 rows)"
            
            # Check for too many missing values
            total_missing = sum(data_info['missing_values'].values())
            missing_percentage = (total_missing / (data_info['rows'] * data_info['columns'])) * 100
            
            if missing_percentage > 10:
                return False, f"Too many missing values: {missing_percentage:.1f}%"
            
            return True, "Data validation passed"
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return False, f"Validation error: {e}"
    
    def get_feature_columns(self):
        """Get available feature columns."""
        if self.current_data is None:
            return []
        
        # Return numeric columns as potential features
        return list(self.current_data.select_dtypes(include=[np.number]).columns)
    
    def get_target_columns(self):
        """Get available target columns."""
        if self.current_data is None:
            return []
        
        # Return numeric columns as potential targets
        return list(self.current_data.select_dtypes(include=[np.number]).columns)
    
    def clear_cache(self):
        """Clear the data cache."""
        self.data_cache.clear()
        self.logger.info("Data cache cleared") 