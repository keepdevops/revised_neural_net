"""
Enhanced File utilities for the Stock Prediction GUI.
Supports organized file history by format type.
"""

import os
import json
import logging
from datetime import datetime
from collections import defaultdict

class FileUtils:
    """Enhanced file utility functions with format-specific organization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.history_file = "file_history.json"
        self.max_history_size = 20
        
        # Define supported file formats and their extensions
        self.supported_formats = {
            'CSV': ['.csv', '.tsv', '.tab'],
            'Excel': ['.xlsx', '.xls', '.xlsm'],
            'Parquet': ['.parquet', '.pq'],
            'Feather': ['.feather', '.ftr', '.arrow'],
            'HDF5': ['.h5', '.hdf5', '.hdf'],
            'Pickle': ['.pkl', '.pickle'],
            'Joblib': ['.joblib'],
            'JSON': ['.json', '.jsonl'],
            'SQLite': ['.db', '.sqlite', '.sqlite3'],
            'DuckDB': ['.duckdb', '.ddb'],
            'Arrow': ['.arrow', '.ipc'],
            'Keras': ['.h5', '.keras'],
            'NumPy': ['.npy', '.npz'],
            'Text': ['.txt', '.tsv', '.tab']
        }
        
        # Initialize history
        self.history = self.load_history()
    
    def load_history(self):
        """Load file history from disk with format-specific organization."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    
                    # Ensure all required fields exist
                    if 'format_history' not in history:
                        history['format_history'] = defaultdict(list)
                    
                    if 'last_accessed' not in history:
                        history['last_accessed'] = {}
                    
                    # Migrate old format if needed
                    if 'data_files' in history and not history['format_history']:
                        for file_path in history['data_files']:
                            format_type = self.get_file_format(file_path)
                            if format_type:
                                history['format_history'][format_type].append(file_path)
                    
                    return history
            else:
                return {
                    'data_files': [],
                    'output_dirs': [],
                    'recent_files': [],
                    'format_history': defaultdict(list),
                    'last_accessed': {}
                }
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            return {
                'data_files': [],
                'output_dirs': [],
                'recent_files': [],
                'format_history': defaultdict(list),
                'last_accessed': {}
            }
    
    def save_history(self):
        """Save file history to disk."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def get_file_format(self, file_path):
        """Get the format type of a file based on its extension."""
        try:
            if not file_path:
                return None
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            for format_name, extensions in self.supported_formats.items():
                if file_ext in extensions:
                    return format_name
            
            return "Unknown"
        except Exception as e:
            self.logger.error(f"Error getting file format: {e}")
            return "Unknown"
    
    def add_data_file(self, file_path):
        """Add a data file to history with format-specific organization."""
        try:
            if file_path and os.path.exists(file_path):
                # Get file format
                format_type = self.get_file_format(file_path)
                
                # Add to general data files list (backward compatibility)
                if file_path in self.history['data_files']:
                    self.history['data_files'].remove(file_path)
                self.history['data_files'].insert(0, file_path)
                self.history['data_files'] = self.history['data_files'][:self.max_history_size]
                
                # Add to format-specific history
                if format_type and format_type != "Unknown":
                    if file_path in self.history['format_history'][format_type]:
                        self.history['format_history'][format_type].remove(file_path)
                    self.history['format_history'][format_type].insert(0, file_path)
                    self.history['format_history'][format_type] = self.history['format_history'][format_type][:self.max_history_size]
                
                # Update last accessed time
                self.history['last_accessed'][file_path] = datetime.now().isoformat()
                
                # Also add to recent files
                self.add_recent_file(file_path)
                
                self.save_history()
                self.logger.info(f"Added {format_type} file to history: {file_path}")
        except Exception as e:
            self.logger.error(f"Error adding data file to history: {e}")
    
    def add_output_dir(self, directory):
        """Add an output directory to history."""
        try:
            if directory and os.path.exists(directory):
                # Remove if already exists
                if directory in self.history['output_dirs']:
                    self.history['output_dirs'].remove(directory)
                
                # Add to beginning
                self.history['output_dirs'].insert(0, directory)
                
                # Keep only the most recent directories
                self.history['output_dirs'] = self.history['output_dirs'][:self.max_history_size]
                
                self.save_history()
        except Exception as e:
            self.logger.error(f"Error adding output directory to history: {e}")
    
    def add_recent_file(self, file_path):
        """Add a file to recent files list."""
        try:
            if file_path and os.path.exists(file_path):
                # Remove if already exists
                if file_path in self.history['recent_files']:
                    self.history['recent_files'].remove(file_path)
                
                # Add to beginning
                self.history['recent_files'].insert(0, file_path)
                
                # Keep only the most recent files
                self.history['recent_files'] = self.history['recent_files'][:self.max_history_size]
                
                self.save_history()
        except Exception as e:
            self.logger.error(f"Error adding recent file: {e}")
    
    def get_recent_data_files(self):
        """Get list of recent data files."""
        try:
            # Filter out non-existent files
            valid_files = [f for f in self.history['data_files'] if os.path.exists(f)]
            self.history['data_files'] = valid_files
            self.save_history()
            return valid_files
        except Exception as e:
            self.logger.error(f"Error getting recent data files: {e}")
            return []
    
    def get_recent_files_by_format(self, format_type=None):
        """Get recent files filtered by format type."""
        try:
            if format_type:
                # Get files of specific format
                files = self.history['format_history'].get(format_type, [])
            else:
                # Get all files from format history
                files = []
                for format_files in self.history['format_history'].values():
                    files.extend(format_files)
            
            # Filter out non-existent files
            valid_files = [f for f in files if os.path.exists(f)]
            
            # Sort by last accessed time
            valid_files.sort(key=lambda x: self.history['last_accessed'].get(x, ''), reverse=True)
            
            return valid_files[:self.max_history_size]
        except Exception as e:
            self.logger.error(f"Error getting recent files by format: {e}")
            return []
    
    def get_format_statistics(self):
        """Get statistics about file formats in history."""
        try:
            stats = {}
            total_files = 0
            
            for format_type, files in self.history['format_history'].items():
                valid_files = [f for f in files if os.path.exists(f)]
                count = len(valid_files)
                if count > 0:
                    stats[format_type] = {
                        'count': count,
                        'files': valid_files
                    }
                    total_files += count
            
            stats['total'] = total_files
            return stats
        except Exception as e:
            self.logger.error(f"Error getting format statistics: {e}")
            return {'total': 0}
    
    def get_supported_formats_list(self):
        """Get list of supported formats with their extensions."""
        return self.supported_formats.copy()
    
    def get_recent_output_dirs(self):
        """Get list of recent output directories."""
        try:
            # Filter out non-existent directories
            valid_dirs = [d for d in self.history['output_dirs'] if os.path.exists(d)]
            self.history['output_dirs'] = valid_dirs
            self.save_history()
            return valid_dirs
        except Exception as e:
            self.logger.error(f"Error getting recent output directories: {e}")
            return []
    
    def get_recent_files(self):
        """Get list of recent files."""
        try:
            # Filter out non-existent files
            valid_files = [f for f in self.history['recent_files'] if os.path.exists(f)]
            self.history['recent_files'] = valid_files
            self.save_history()
            return valid_files
        except Exception as e:
            self.logger.error(f"Error getting recent files: {e}")
            return []
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        try:
            self.history['recent_files'] = []
            self.save_history()
        except Exception as e:
            self.logger.error(f"Error clearing recent files: {e}")
    
    def clear_data_file_history(self):
        """Clear the data file history."""
        try:
            self.history['data_files'] = []
            self.history['format_history'] = defaultdict(list)
            self.history['last_accessed'] = {}
            self.save_history()
        except Exception as e:
            self.logger.error(f"Error clearing data file history: {e}")
    
    def clear_format_history(self, format_type=None):
        """Clear history for a specific format or all formats."""
        try:
            if format_type:
                if format_type in self.history['format_history']:
                    del self.history['format_history'][format_type]
            else:
                self.history['format_history'] = defaultdict(list)
            
            self.save_history()
        except Exception as e:
            self.logger.error(f"Error clearing format history: {e}")
    
    def clear_output_dir_history(self):
        """Clear the output directory history."""
        try:
            self.history['output_dirs'] = []
            self.save_history()
        except Exception as e:
            self.logger.error(f"Error clearing output directory history: {e}")
    
    def validate_file_path(self, file_path):
        """Validate if a file path exists and is accessible."""
        try:
            return os.path.exists(file_path) and os.path.isfile(file_path)
        except Exception as e:
            self.logger.error(f"Error validating file path: {e}")
            return False
    
    def validate_directory_path(self, directory):
        """Validate if a directory path exists and is accessible."""
        try:
            return os.path.exists(directory) and os.path.isdir(directory)
        except Exception as e:
            self.logger.error(f"Error validating directory path: {e}")
            return False
    
    def get_file_size(self, file_path):
        """Get file size in human-readable format."""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return self.format_file_size(size_bytes)
            return "Unknown"
        except Exception as e:
            self.logger.error(f"Error getting file size: {e}")
            return "Unknown"
    
    def format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            while size_bytes >= 1024 and i < len(size_names) - 1:
                size_bytes /= 1024.0
                i += 1
            
            return f"{size_bytes:.1f} {size_names[i]}"
        except Exception as e:
            self.logger.error(f"Error formatting file size: {e}")
            return "Unknown"
    
    def get_file_info(self, file_path):
        """Get comprehensive file information."""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            format_type = self.get_file_format(file_path)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'format': format_type,
                'size': self.format_file_size(stat.st_size),
                'size_bytes': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'last_accessed': self.history['last_accessed'].get(file_path, 'Unknown')
            }
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None 