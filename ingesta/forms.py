# ingesta/forms.py
# Este archivo ahora solo importa desde el módulo forms
from .forms import (
    ConcesionForm, ASEForm, ServicioForm, ZonaDescargaForm,
    UploadFileForm, PROCESS_TO_SUBSECRETARIA
)

__all__ = [
    'ConcesionForm', 
    'ASEForm', 
    'ServicioForm', 
    'ZonaDescargaForm',
    'UploadFileForm',
    'PROCESS_TO_SUBSECRETARIA'
]