from django import forms
from .models import PlanAnualAdquisicion, SolicitudPAA, SUBDIRECCIONES_CHOICES, MESES_CHOICES

class PlanAnualAdquisicionForm(forms.ModelForm):
    """Formulario para crear/editar registros del Plan Anual de Adquisiciones."""
    
    class Meta:
        model = PlanAnualAdquisicion
        fields = [
            'subdireccion',
            'codigos_unspsc',
            'descripcion',
            'fecha_estimada_inicio',
            'fecha_estimada_presentacion_ofertas',
            'duracion_contrato_numero',
            'duracion_contrato_intervalo',
            'modalidad_seleccion',
            'fuente_recursos',
            'valor_total_estimado',
            'valor_estimado_vigencia_actual',
            'requiere_vigencias_futuras',
            'estado_solicitud_vigencias_futuras',
            'correo_responsable',
            'debe_cumplir_30_porciento_alimentos',
            'incluye_bienes_servicios_distintos_alimentos',
            'justificacion',
        ]
        widgets = {
            'subdireccion': forms.Select(attrs={'class': 'form-select'}),
            'codigos_unspsc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese los códigos UNSPSC separados por punto y coma (;)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'fecha_estimada_inicio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_estimada_presentacion_ofertas': forms.Select(attrs={
                'class': 'form-select'
            }),
            'duracion_contrato_numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'duracion_contrato_intervalo': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_seleccion': forms.Select(attrs={'class': 'form-select'}),
            'fuente_recursos': forms.Select(attrs={'class': 'form-select'}),
            'valor_total_estimado': forms.TextInput(attrs={
                'class': 'form-control currency-input',
                'placeholder': 'Ej: 1.000.000'
            }),
            'valor_estimado_vigencia_actual': forms.TextInput(attrs={
                'class': 'form-control currency-input',
                'placeholder': 'Ej: 1.000.000'
            }),
            'requiere_vigencias_futuras': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'estado_solicitud_vigencias_futuras': forms.Select(attrs={
                'class': 'form-select'
            }),
            'correo_responsable': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@uaesp.gov.co'
            }),
            'debe_cumplir_30_porciento_alimentos': forms.Select(attrs={'class': 'form-select'}),
            'incluye_bienes_servicios_distintos_alimentos': forms.Select(attrs={'class': 'form-select'}),
            'justificacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer todos los campos obligatorios excepto el checkbox de vigencias futuras
        for field_name, field in self.fields.items():
            if field_name != 'requiere_vigencias_futuras':
                field.required = True
        
        # El checkbox de vigencias futuras no es obligatorio
        self.fields['requiere_vigencias_futuras'].required = False
        
        # Configurar choices para los campos de meses
        self.fields['fecha_estimada_inicio'].choices = [('', '---------')] + list(MESES_CHOICES)
        self.fields['fecha_estimada_presentacion_ofertas'].choices = [('', '---------')] + list(MESES_CHOICES)
        
        # Formatear valores de moneda si existen (al editar)
        if self.instance and self.instance.pk:
            # Bloquear la subdirección al editar un registro existente
            if 'subdireccion' in self.fields:
                self.fields['subdireccion'].disabled = True
                self.fields['subdireccion'].widget.attrs['disabled'] = True
                self.fields['subdireccion'].widget.attrs['readonly'] = True
            
            if self.instance.valor_total_estimado:
                self.initial['valor_total_estimado'] = f"{int(self.instance.valor_total_estimado):,}".replace(',', '.')
            if self.instance.valor_estimado_vigencia_actual:
                self.initial['valor_estimado_vigencia_actual'] = f"{int(self.instance.valor_estimado_vigencia_actual):,}".replace(',', '.')
        
        # El estado de vigencias futuras solo es requerido si requiere vigencias futuras
        # Lo manejaremos en el clean
        self.fields['estado_solicitud_vigencias_futuras'].required = False
    
    def clean_valor_total_estimado(self):
        """Limpia y convierte el valor total estimado a decimal."""
        valor = self.cleaned_data.get('valor_total_estimado')
        if valor:
            # Remover puntos y convertir a decimal
            valor_limpio = str(valor).replace('.', '').replace(',', '.')
            try:
                return float(valor_limpio)
            except ValueError:
                raise forms.ValidationError('Ingrese un valor numérico válido.')
        return valor
    
    def clean_valor_estimado_vigencia_actual(self):
        """Limpia y convierte el valor estimado vigencia actual a decimal."""
        valor = self.cleaned_data.get('valor_estimado_vigencia_actual')
        if valor:
            # Remover puntos y convertir a decimal
            valor_limpio = str(valor).replace('.', '').replace(',', '.')
            try:
                return float(valor_limpio)
            except ValueError:
                raise forms.ValidationError('Ingrese un valor numérico válido.')
        return valor
    
    def clean(self):
        cleaned_data = super().clean()
        requiere_vigencias = cleaned_data.get('requiere_vigencias_futuras')
        estado_vigencias = cleaned_data.get('estado_solicitud_vigencias_futuras')
        
        # Si requiere vigencias futuras, el estado debe estar presente
        if requiere_vigencias and not estado_vigencias:
            raise forms.ValidationError({
                'estado_solicitud_vigencias_futuras': 'Debe especificar el estado de solicitud de vigencias futuras.'
            })
        
        return cleaned_data


class SolicitudPAAForm(forms.ModelForm):
    """Formulario para editar solicitudes del Plan Anual de Adquisiciones."""
    
    class Meta:
        model = SolicitudPAA
        fields = [
            'subdireccion',
            'codigos_unspsc',
            'descripcion',
            'fecha_estimada_inicio',
            'fecha_estimada_presentacion_ofertas',
            'duracion_contrato_numero',
            'duracion_contrato_intervalo',
            'modalidad_seleccion',
            'fuente_recursos',
            'valor_total_estimado',
            'valor_estimado_vigencia_actual',
            'requiere_vigencias_futuras',
            'estado_solicitud_vigencias_futuras',
            'correo_responsable',
            'debe_cumplir_30_porciento_alimentos',
            'incluye_bienes_servicios_distintos_alimentos',
            'justificacion',
        ]
        widgets = {
            'subdireccion': forms.Select(attrs={'class': 'form-select'}),
            'codigos_unspsc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese los códigos UNSPSC separados por punto y coma (;)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'fecha_estimada_inicio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_estimada_presentacion_ofertas': forms.Select(attrs={
                'class': 'form-select'
            }),
            'duracion_contrato_numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'duracion_contrato_intervalo': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_seleccion': forms.Select(attrs={'class': 'form-select'}),
            'fuente_recursos': forms.Select(attrs={'class': 'form-select'}),
            'valor_total_estimado': forms.TextInput(attrs={
                'class': 'form-control currency-input',
                'placeholder': 'Ej: 1.000.000'
            }),
            'valor_estimado_vigencia_actual': forms.TextInput(attrs={
                'class': 'form-control currency-input',
                'placeholder': 'Ej: 1.000.000'
            }),
            'requiere_vigencias_futuras': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'estado_solicitud_vigencias_futuras': forms.Select(attrs={
                'class': 'form-select'
            }),
            'correo_responsable': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@uaesp.gov.co'
            }),
            'debe_cumplir_30_porciento_alimentos': forms.Select(attrs={'class': 'form-select'}),
            'incluye_bienes_servicios_distintos_alimentos': forms.Select(attrs={'class': 'form-select'}),
            'justificacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer todos los campos obligatorios excepto el checkbox de vigencias futuras
        for field_name, field in self.fields.items():
            if field_name != 'requiere_vigencias_futuras':
                field.required = True
        
        # El checkbox de vigencias futuras no es obligatorio
        self.fields['requiere_vigencias_futuras'].required = False
        
        # Configurar choices para los campos de meses
        self.fields['fecha_estimada_inicio'].choices = [('', '---------')] + list(MESES_CHOICES)
        self.fields['fecha_estimada_presentacion_ofertas'].choices = [('', '---------')] + list(MESES_CHOICES)
        
        # Bloquear la subdirección (no se puede modificar al editar una solicitud)
        # Siempre bloquearla porque este formulario solo se usa para editar solicitudes existentes
        if 'subdireccion' in self.fields:
            self.fields['subdireccion'].disabled = True
            self.fields['subdireccion'].widget.attrs['disabled'] = True
            self.fields['subdireccion'].widget.attrs['readonly'] = True
        
        # Formatear valores de moneda si existen
        if self.instance and self.instance.pk:
            if self.instance.valor_total_estimado:
                self.initial['valor_total_estimado'] = f"{int(self.instance.valor_total_estimado):,}".replace(',', '.')
            if self.instance.valor_estimado_vigencia_actual:
                self.initial['valor_estimado_vigencia_actual'] = f"{int(self.instance.valor_estimado_vigencia_actual):,}".replace(',', '.')
        
        # El estado de vigencias futuras solo es requerido si requiere vigencias futuras
        self.fields['estado_solicitud_vigencias_futuras'].required = False
    
    def clean_valor_total_estimado(self):
        """Limpia y convierte el valor total estimado a decimal."""
        valor = self.cleaned_data.get('valor_total_estimado')
        if valor:
            # Remover puntos y convertir a decimal
            valor_limpio = str(valor).replace('.', '').replace(',', '.')
            try:
                return float(valor_limpio)
            except ValueError:
                raise forms.ValidationError('Ingrese un valor numérico válido.')
        return valor
    
    def clean_valor_estimado_vigencia_actual(self):
        """Limpia y convierte el valor estimado vigencia actual a decimal."""
        valor = self.cleaned_data.get('valor_estimado_vigencia_actual')
        if valor:
            # Remover puntos y convertir a decimal
            valor_limpio = str(valor).replace('.', '').replace(',', '.')
            try:
                return float(valor_limpio)
            except ValueError:
                raise forms.ValidationError('Ingrese un valor numérico válido.')
        return valor
    
    def clean(self):
        cleaned_data = super().clean()
        requiere_vigencias = cleaned_data.get('requiere_vigencias_futuras')
        estado_vigencias = cleaned_data.get('estado_solicitud_vigencias_futuras')
        
        # Si requiere vigencias futuras, el estado debe estar presente
        if requiere_vigencias and not estado_vigencias:
            raise forms.ValidationError({
                'estado_solicitud_vigencias_futuras': 'Debe especificar el estado de solicitud de vigencias futuras.'
            })
        
        return cleaned_data
