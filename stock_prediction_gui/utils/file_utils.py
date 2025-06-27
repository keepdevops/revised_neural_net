"""
File utilities for the Stock Prediction GUI.
"""

import os
import json
import logging
from datetime import datetime

class FileUtils:
    """File utility functions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.history_file = "file_history.json"
        self.max_history_size = 20
        
        # Initialize history
        self.history = self.load_history()
    
    def load_history(self):
        """Load file history from disk."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'data_files': [],
                    'output_dirs': [],
                    'recent_files': []
                }
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            return {
                'data_files': [],
                'output_dirs': [],
                'recent_files': []
            }
    
    def save_history(self):
        """Save file history to disk."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def add_data_file(self, file_path):
        """Add a data file to history."""
        try:
            if file_path and os.path.exists(file_path):
                # Remove if already exists
                if file_path in self.history['data_files']:
                    self.history['data_files'].remove(file_path)
                
                # Add to beginning
                self.history['data_files'].insert(0, file_path)
                
                # Keep only the most recent files
                self.history['data_files'] = self.history['data_files'][:self.max_history_size]
                
                # Also add to recent files
                self.add_recent_file(file_path)
                
                self.save_history()
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
            self.save_history()
        except Exception as e:
            self.logger.error(f"Error clearing data file history: {e}")
    
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