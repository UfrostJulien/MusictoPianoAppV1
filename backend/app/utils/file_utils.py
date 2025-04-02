"""
Utility functions for file operations
"""

import os

def ensure_directory_exists(directory):
    """
    Ensure that a directory exists, creating it if necessary
    
    Args:
        directory (str): Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
