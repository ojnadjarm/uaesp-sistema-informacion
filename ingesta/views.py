"""
Este módulo se mantiene por compatibilidad con versiones anteriores.
Todas las vistas se han movido a sus respectivos módulos en el directorio de vistas.
"""

from .views import (
    file_history_view,
    upload_file_view,
    download_file,
    download_error_file,
    delete_file,
    evidence_list_view,
    download_evidence,
    delete_evidence
)

__all__ = [
    'file_history_view',
    'upload_file_view',
    'download_file',
    'download_error_file',
    'delete_file',
    'evidence_list_view',
    'download_evidence',
    'delete_evidence'
]