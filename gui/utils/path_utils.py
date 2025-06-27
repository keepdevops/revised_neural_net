
"""
Path Utils Module
"""
import os
import json
import logging

class PathUtils:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_ticker_from_filename(self, filename):
        """Extract ticker symbol from filename."""
        try:
            # Extract ticker from filename patterns like "AAPL_data.csv" or "AAPL_20240101.csv"
            basename = os.path.basename(filename)
            parts = basename.split('_')
            if len(parts) > 0:
                return parts[0].upper()
            return "UNKNOWN"
        except Exception as e:
            self.logger.error(f"Error extracting ticker: {e}")
            return "UNKNOWN"
    
    def validate_path(self, path):
        """Validate if a path exists and is accessible."""
        if not path:
            return False, "Path is empty"
        if not os.path.exists(path):
            return False, "Path does not exist"
        if not os.access(path, os.R_OK):
            return False, "Path is not readable"
        return True, ""
