from django import forms
from globalfunctions.string_manager import get_string


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    def to_python(self, data):
        # Accept a list/tuple from the widget and pick the first file to satisfy FileField
        if isinstance(data, (list, tuple)):
            if not data:
                return None
            data = data[0]
        return super().to_python(data)


class EvidenceUploadForm(forms.Form):
    descripcion = forms.CharField(
        label='Descripción',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    files = MultiFileField(
        label='Archivos de evidencia (máx 10MB c/u)',
        widget=MultiFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=True
    )

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def clean_files(self):
        files = self.files.getlist('files') if hasattr(self.files, 'getlist') else []
        if not files:
            raise forms.ValidationError(get_string('ingesta.errors.file_required', 'ingesta'))
        for f in files:
            if f.size and f.size > self.MAX_FILE_SIZE:
                raise forms.ValidationError(f"Archivo '{f.name}' excede el límite de 10MB")
        # Return first file to satisfy FileField, view will read all from request.FILES
        return files[0]


