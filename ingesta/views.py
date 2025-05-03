"""
This module is maintained for backward compatibility.
All views have been moved to their respective modules in the views directory.
"""

from .views import (
    file_history_view,
    upload_file_view,
    download_file,
    delete_file
)

__all__ = [
    'file_history_view',
    'upload_file_view',
    'download_file',
    'delete_file'
]