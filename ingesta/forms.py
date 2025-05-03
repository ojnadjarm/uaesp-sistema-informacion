# ingesta/forms.py
from django import forms
from .cabeceras import CABECERAS_PESAJE
from globalfunctions.string_manager import get_string

# Estructura de datos (como la definiste)
PROCESO_DATA = {
    'DISPOSICION_FINAL': {
        'nombre': 'Disposición Final',
        'procesos': {
             'disposicion_final_pesaje': {
                 'nombre': 'Disposición Final - Pesaje',
                 'cabeceras': CABECERAS_PESAJE,
                 'file_type': 'xlsx',
                 'file_start_row': 6,
                 'file_start_col': 'B',
                 'file_end_col': 'Z'
            },
        }
    },
}

# Generar choices para Subsecretarías
SUB_SECRETARIA_CHOICES = [('', '---------')] + [
    (key, data['nombre']) for key, data in PROCESO_DATA.items()
]

# Generar choices para Tipos de Proceso (lista plana por ahora)
TIPO_PROCESO_CHOICES = [('', '---------')]
for sub_key, sub_data in PROCESO_DATA.items():
    for proc_key, proc_data in sub_data.get('procesos', {}).items():
        # Usamos la clave del proceso como valor, y un nombre descriptivo
        TIPO_PROCESO_CHOICES.append((proc_key, proc_data.get('nombre', proc_key)))


class UploadFileForm(forms.Form):
    subsecretaria = forms.ChoiceField(
        label='Subsecretaría de Origen',
        choices=SUB_SECRETARIA_CHOICES, # Usamos la lista generada
        required=True,
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    tipo_proceso = forms.ChoiceField(
        label='Tipo de Proceso/Archivo',
        choices=TIPO_PROCESO_CHOICES, # Usamos la lista generada (plana)
        required=True,
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    file = forms.FileField(
        label='Seleccionar archivo (CSV o XLSX)',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx'})
    )