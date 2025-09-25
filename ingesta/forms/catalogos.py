from django import forms
from ingesta.models import Concesion, ASE, Servicio, ZonaDescarga
from globalfunctions.string_manager import get_string

class ConcesionForm(forms.ModelForm):
    """Formulario para crear y editar concesiones."""
    
    class Meta:
        model = Concesion
        fields = ['codigo', 'nombre', 'descripcion', 'categoria', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ALDC',
                'maxlength': '20'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre oficial de la concesión',
                'maxlength': '100'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Descripción adicional de la concesión'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: BOGOTÁ, CUNDINAMARCA, PIDJ',
                'maxlength': '100'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'codigo': get_string('catalogos.concesion.codigo_label', 'ingesta'),
            'nombre': get_string('catalogos.concesion.nombre_label', 'ingesta'),
            'descripcion': get_string('catalogos.concesion.descripcion_label', 'ingesta'),
            'categoria': get_string('catalogos.concesion.categoria_label', 'ingesta'),
            'activo': get_string('catalogos.concesion.activo_label', 'ingesta'),
        }
        help_texts = {
            'codigo': get_string('catalogos.concesion.codigo_help', 'ingesta'),
            'nombre': get_string('catalogos.concesion.nombre_help', 'ingesta'),
            'descripcion': get_string('catalogos.concesion.descripcion_help', 'ingesta'),
            'categoria': get_string('catalogos.concesion.categoria_help', 'ingesta'),
            'activo': get_string('catalogos.concesion.activo_help', 'ingesta'),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if codigo:
            codigo = codigo.upper().strip()
            # Verificar que no exista otro registro con el mismo código
            if Concesion.objects.filter(codigo=codigo).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe una concesión con este código.")
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if nombre:
            nombre = nombre.strip()
            # Verificar que no exista otro registro con el mismo nombre
            if Concesion.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe una concesión con este nombre.")
        return nombre

class ASEForm(forms.ModelForm):
    """Formulario para crear y editar ASEs."""
    
    class Meta:
        model = ASE
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: UAESP',
                'maxlength': '20'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre oficial del ASE',
                'maxlength': '100'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Descripción adicional del ASE'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'codigo': get_string('catalogos.ase.codigo_label', 'ingesta'),
            'nombre': get_string('catalogos.ase.nombre_label', 'ingesta'),
            'descripcion': get_string('catalogos.ase.descripcion_label', 'ingesta'),
            'activo': get_string('catalogos.ase.activo_label', 'ingesta'),
        }
        help_texts = {
            'codigo': get_string('catalogos.ase.codigo_help', 'ingesta'),
            'nombre': get_string('catalogos.ase.nombre_help', 'ingesta'),
            'descripcion': get_string('catalogos.ase.descripcion_help', 'ingesta'),
            'activo': get_string('catalogos.ase.activo_help', 'ingesta'),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if codigo:
            codigo = codigo.upper().strip()
            # Verificar que no exista otro registro con el mismo código
            if ASE.objects.filter(codigo=codigo).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe un ASE con este código.")
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if nombre:
            nombre = nombre.strip()
            # Verificar que no exista otro registro con el mismo nombre
            if ASE.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe un ASE con este nombre.")
        return nombre

class ServicioForm(forms.ModelForm):
    """Formulario para crear y editar servicios."""
    
    class Meta:
        model = Servicio
        fields = ['codigo', 'nombre', 'descripcion', 'categoria', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ASEO',
                'maxlength': '20'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre oficial del servicio',
                'maxlength': '100'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Descripción adicional del servicio'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: SERVICIO TARIFA ASEO, MATERIAL APROVECHAMIENTO',
                'maxlength': '100'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'codigo': get_string('catalogos.servicio.codigo_label', 'ingesta'),
            'nombre': get_string('catalogos.servicio.nombre_label', 'ingesta'),
            'descripcion': get_string('catalogos.servicio.descripcion_label', 'ingesta'),
            'categoria': get_string('catalogos.servicio.categoria_label', 'ingesta'),
            'activo': get_string('catalogos.servicio.activo_label', 'ingesta'),
        }
        help_texts = {
            'codigo': get_string('catalogos.servicio.codigo_help', 'ingesta'),
            'nombre': get_string('catalogos.servicio.nombre_help', 'ingesta'),
            'descripcion': get_string('catalogos.servicio.descripcion_help', 'ingesta'),
            'categoria': get_string('catalogos.servicio.categoria_help', 'ingesta'),
            'activo': get_string('catalogos.servicio.activo_help', 'ingesta'),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if codigo:
            codigo = codigo.upper().strip()
            # Verificar que no exista otro registro con el mismo código
            if Servicio.objects.filter(codigo=codigo).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe un servicio con este código.")
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if nombre:
            nombre = nombre.strip()
            # Verificar que no exista otro registro con el mismo nombre
            if Servicio.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe un servicio con este nombre.")
        return nombre

class ZonaDescargaForm(forms.ModelForm):
    """Formulario para crear y editar zonas de descarga."""
    
    class Meta:
        model = ZonaDescarga
        fields = ['codigo', 'nombre', 'descripcion', 'categoria', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: FASE2',
                'maxlength': '20'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre oficial de la zona',
                'maxlength': '100'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Descripción adicional de la zona'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PIDJ, NO APLICA',
                'maxlength': '100'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'codigo': get_string('catalogos.zona_descarga.codigo_label', 'ingesta'),
            'nombre': get_string('catalogos.zona_descarga.nombre_label', 'ingesta'),
            'descripcion': get_string('catalogos.zona_descarga.descripcion_label', 'ingesta'),
            'categoria': get_string('catalogos.zona_descarga.categoria_label', 'ingesta'),
            'activo': get_string('catalogos.zona_descarga.activo_label', 'ingesta'),
        }
        help_texts = {
            'codigo': get_string('catalogos.zona_descarga.codigo_help', 'ingesta'),
            'nombre': get_string('catalogos.zona_descarga.nombre_help', 'ingesta'),
            'descripcion': get_string('catalogos.zona_descarga.descripcion_help', 'ingesta'),
            'categoria': get_string('catalogos.zona_descarga.categoria_help', 'ingesta'),
            'activo': get_string('catalogos.zona_descarga.activo_help', 'ingesta'),
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if codigo:
            codigo = codigo.upper().strip()
            # Verificar que no exista otro registro con el mismo código
            if ZonaDescarga.objects.filter(codigo=codigo).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe una zona de descarga con este código.")
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if nombre:
            nombre = nombre.strip()
            # Verificar que no exista otro registro con el mismo nombre
            if ZonaDescarga.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe una zona de descarga con este nombre.")
        return nombre
