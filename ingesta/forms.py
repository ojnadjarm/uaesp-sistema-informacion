# ingesta/forms.py
from django import forms

# Opciones para el selector de tipo de proceso
PROCESO_CHOICES = [
    ('', '---------'), # Opción por defecto vacía
    ('disposicion_final_pesaje', 'Disposición Final - Control de Pesaje'),
    # Futuros tipos irán aquí...
]

class UploadFileForm(forms.Form):
    tipo_proceso = forms.ChoiceField(
        label='Tipo de Proceso/Archivo',
        choices=PROCESO_CHOICES,
        required=True,
        # Widget para aplicar clases CSS de Bootstrap al <select>
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    file = forms.FileField(
        label='Seleccionar archivo CSV',
        required=True,
        # Widget para aplicar clases CSS de Bootstrap al <input type="file">
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    # Podrías añadir más campos aquí si fueran necesarios para la ingesta