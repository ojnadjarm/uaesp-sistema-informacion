from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from ingesta.models.core.base import TimeStampedModel

# Subdirecciones disponibles según el CSV
SUBDIRECCIONES_CHOICES = [
    ('SSF', 'Subdirección de servicios funerarios'),
    ('RBL', 'Subdirección de RBL'),
    ('SDF', 'Subdirección de Disposición Final'),
    ('SAL', 'Subdirección de Asuntos Legales'),
    ('SA', 'Subdirección de Aprovechamiento'),
    ('SAP', 'Subdirección de Alumbrado Público'),
    ('SAF', 'Subdirección Administrativa y Financiera'),
    ('OCDI', 'Oficina de Control Disciplinario Interno'),
    ('TIC', 'Oficina de TIC'),
    ('OCI', 'Oficina control interno'),
    ('OAP', 'Oficina Asesora de Planeación'),
    ('OACRI', 'Oficina Asesora de Comunicaciones'),
    ('DG', 'Dirección General'),
]

DURACION_INTERVALO_CHOICES = [
    ('dias', 'Días'),
    ('meses', 'Meses'),
    ('años', 'Años'),
]

MESES_CHOICES = [
    ('Enero', 'Enero'),
    ('Febrero', 'Febrero'),
    ('Marzo', 'Marzo'),
    ('Abril', 'Abril'),
    ('Mayo', 'Mayo'),
    ('Junio', 'Junio'),
    ('Julio', 'Julio'),
    ('Agosto', 'Agosto'),
    ('Septiembre', 'Septiembre'),
    ('Octubre', 'Octubre'),
    ('Noviembre', 'Noviembre'),
    ('Diciembre', 'Diciembre'),
]

MODALIDAD_SELECCION_CHOICES = [
    ('Solicitud de información a los Proveedores', 'Solicitud de información a los Proveedores'),
    ('Licitación pública', 'Licitación pública'),
    ('Licitación pública (Obra pública)', 'Licitación pública (Obra pública)'),
    ('Concurso de méritos con precalificación (descontinuado)', 'Concurso de méritos con precalificación (descontinuado)'),
    ('Concurso de méritos abierto (descontinuado)', 'Concurso de méritos abierto (descontinuado)'),
    ('Concurso de méritos abierto', 'Concurso de méritos abierto'),
    ('Contratación directa (con ofertas)', 'Contratación directa (con ofertas)'),
    ('Selección abreviada menor cuantía', 'Selección abreviada menor cuantía'),
    ('Selección Abreviada de Menor Cuantia sin Manifestacion de Interés', 'Selección Abreviada de Menor Cuantia sin Manifestacion de Interés'),
    ('Selección abreviada subasta inversa', 'Selección abreviada subasta inversa'),
    ('Mínima cuantía', 'Mínima cuantía'),
    ('Contratación régimen especial - Selección de comisionista', 'Contratación régimen especial - Selección de comisionista'),
    ('Contratación régimen especial - Enajenación de bienes para intermediarios idóneos', 'Contratación régimen especial - Enajenación de bienes para intermediarios idóneos'),
    ('Contratación régimen especial - Banco multilateral y organismos multilaterales', 'Contratación régimen especial - Banco multilateral y organismos multilaterales'),
    ('Contratación régimen especial (con ofertas)  - Selección de comisionista', 'Contratación régimen especial (con ofertas)  - Selección de comisionista'),
    ('Contratación régimen especial (con ofertas)  - Enajenación de bienes para intermediarios idóneos', 'Contratación régimen especial (con ofertas)  - Enajenación de bienes para intermediarios idóneos'),
    ('Contratación régimen especial (con ofertas)  - Régimen especial', 'Contratación régimen especial (con ofertas)  - Régimen especial'),
    ('Contratación régimen especial (con ofertas)  - Banco multilateral y organismos multilaterales', 'Contratación régimen especial (con ofertas)  - Banco multilateral y organismos multilaterales'),
    ('Contratación directa.', 'Contratación directa.'),
    ('Selección abreviada - acuerdo marco', 'Selección abreviada - acuerdo marco'),
]

FUENTE_RECURSOS_CHOICES = [
    ('Recursos propios', 'Recursos propios'),
    ('Presupuesto de entidad nacional', 'Presupuesto de entidad nacional'),
    ('Regalías', 'Regalías'),
    ('Recursos de crédito', 'Recursos de crédito'),
    ('SGP - Sistema General de Participaciones', 'SGP - Sistema General de Participaciones'),
    ('No Aplica', 'No Aplica'),
]

ESTADO_VIGENCIAS_FUTURAS_CHOICES = [
    ('NA', 'NA'),
    ('Solicitadas', 'Solicitadas'),
    ('Aprobadas', 'Aprobadas'),
]

SI_NO_CHOICES = [
    ('Si', 'Si'),
    ('No', 'No'),
]

TIPO_SOLICITUD_CHOICES = [
    ('Nueva', 'Nueva'),
    ('Modificacion', 'Modificación'),
    ('Eliminacion', 'Eliminación'),
]

TIPO_ACCION_CHOICES = [
    ('crear', 'Crear'),
    ('modificar', 'Modificar'),
    ('eliminar', 'Eliminar'),
]

ESTADO_SOLICITUD_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('aprobada', 'Aprobada'),
    ('rechazada', 'Rechazada'),
]


class PlanAnualAdquisicionManager(models.Manager):
    def activos(self):
        """Retorna solo los registros no eliminados."""
        return self.get_queryset().filter(eliminado=False)
    
    def eliminados(self):
        """Retorna solo los registros eliminados."""
        return self.get_queryset().filter(eliminado=True)


class PlanAnualAdquisicion(TimeStampedModel):
    """
    Modelo para el Plan Anual de Adquisiciones (PAA).
    """
    # Código autoincrementado por subdirección (ej: SAF-001, SAL-001)
    codigo = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Código')
    
    # Subdirección
    subdireccion = models.CharField(
        max_length=10,
        choices=SUBDIRECCIONES_CHOICES,
        verbose_name='Subdirección'
    )
    
    # Códigos UNSPSC (separados por ;)
    codigos_unspsc = models.TextField(
        verbose_name='Código UNSPSC (cada código separado por ;)',
        help_text='Ingrese los códigos UNSPSC separados por punto y coma (;)'
    )
    
    # Descripción
    descripcion = models.TextField(verbose_name='Descripción')
    
    # Fechas estimadas (meses)
    fecha_estimada_inicio = models.CharField(
        max_length=50,
        choices=MESES_CHOICES,
        verbose_name='Fecha estimada de inicio de proceso de selección (mes)'
    )
    
    fecha_estimada_presentacion_ofertas = models.CharField(
        max_length=50,
        choices=MESES_CHOICES,
        verbose_name='Fecha estimada de presentación de ofertas (mes)'
    )
    
    # Duración del contrato
    duracion_contrato_numero = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Duración del contrato (número)'
    )
    
    duracion_contrato_intervalo = models.CharField(
        max_length=10,
        choices=DURACION_INTERVALO_CHOICES,
        verbose_name='Duración del contrato (intervalo)'
    )
    
    # Modalidad y fuente
    modalidad_seleccion = models.CharField(
        max_length=200,
        choices=MODALIDAD_SELECCION_CHOICES,
        verbose_name='Modalidad de selección'
    )
    
    fuente_recursos = models.CharField(
        max_length=100,
        choices=FUENTE_RECURSOS_CHOICES,
        verbose_name='Fuente de los recursos'
    )
    
    # Valores estimados
    valor_total_estimado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor total estimado'
    )
    
    valor_estimado_vigencia_actual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor estimado en la vigencia actual'
    )
    
    # Vigencias futuras
    requiere_vigencias_futuras = models.BooleanField(
        default=False,
        verbose_name='¿Se requieren vigencias futuras?'
    )
    
    estado_solicitud_vigencias_futuras = models.CharField(
        max_length=20,
        choices=ESTADO_VIGENCIAS_FUTURAS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Estado de solicitud de vigencias futuras'
    )
    
    # Responsable
    correo_responsable = models.EmailField(
        verbose_name='Correo electrónico del responsable'
    )
    
    # Preguntas sobre alimentos
    debe_cumplir_30_porciento_alimentos = models.CharField(
        max_length=2,
        choices=SI_NO_CHOICES,
        verbose_name='¿Debe cumplir con invertir mínimo el 30% de los recursos del presupuesto destinados a comprar alimentos, cumpliendo con lo establecido en la Ley 2046 de 2020, reglamentada por el Decreto 248 de 2021?'
    )
    
    incluye_bienes_servicios_distintos_alimentos = models.CharField(
        max_length=2,
        choices=SI_NO_CHOICES,
        verbose_name='¿El contrato incluye el suministro de bienes y servicios distintos a alimentos?'
    )
    
    # Tipo de solicitud
    tipo_solicitud = models.CharField(
        max_length=20,
        choices=TIPO_SOLICITUD_CHOICES,
        verbose_name='Tipo de solicitud'
    )
    
    # Justificación
    justificacion = models.TextField(verbose_name='Justificación')
    
    # Soft delete
    eliminado = models.BooleanField(default=False, verbose_name='Eliminado')
    
    # Usuario que creó/modificó
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    
    objects = PlanAnualAdquisicionManager()
    
    def save(self, *args, **kwargs):
        """Genera el código automáticamente si es un nuevo registro."""
        if not self.codigo:
            # Obtener el último código de la misma subdirección
            ultimo = PlanAnualAdquisicion.objects.filter(
                subdireccion=self.subdireccion
            ).order_by('-codigo').first()
            
            if ultimo and ultimo.codigo:
                # Extraer el número del último código (ej: SAF-001 -> 1)
                try:
                    ultimo_numero = int(ultimo.codigo.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except (IndexError, ValueError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            # Generar el nuevo código (ej: SAF-001)
            self.codigo = f"{self.subdireccion}-{nuevo_numero:03d}"
        
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Marca el registro como eliminado (soft delete)."""
        self.eliminado = True
        self.tipo_solicitud = 'Eliminacion'
        self.save()
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}"
    
    class Meta:
        verbose_name = 'Plan Anual de Adquisición'
        verbose_name_plural = 'Planes Anuales de Adquisición'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['subdireccion']),
            models.Index(fields=['codigo']),
            models.Index(fields=['eliminado']),
            models.Index(fields=['tipo_solicitud']),
        ]


class SolicitudPAAManager(models.Manager):
    def pendientes(self):
        """Retorna solo las solicitudes pendientes."""
        return self.get_queryset().filter(estado='pendiente')
    
    def aprobadas(self):
        """Retorna solo las solicitudes aprobadas."""
        return self.get_queryset().filter(estado='aprobada')
    
    def rechazadas(self):
        """Retorna solo las solicitudes rechazadas."""
        return self.get_queryset().filter(estado='rechazada')


class SolicitudPAA(TimeStampedModel):
    """
    Modelo para solicitudes de cambios al Plan Anual de Adquisiciones.
    Tabla espejo que mantiene el historial de todas las solicitudes.
    """
    # Tipo de acción solicitada
    tipo_accion = models.CharField(
        max_length=20,
        choices=TIPO_ACCION_CHOICES,
        verbose_name='Tipo de acción'
    )
    
    # Estado de la solicitud
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_SOLICITUD_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    
    # Referencia al registro original (si es modificación o eliminación)
    registro_original = models.ForeignKey(
        'PlanAnualAdquisicion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='solicitudes',
        verbose_name='Registro original'
    )
    
    # Todos los campos del PlanAnualAdquisicion (clon)
    codigo = models.CharField(max_length=20, null=True, blank=True, verbose_name='Código')
    subdireccion = models.CharField(
        max_length=10,
        choices=SUBDIRECCIONES_CHOICES,
        verbose_name='Subdirección'
    )
    codigos_unspsc = models.TextField(
        verbose_name='Código UNSPSC (cada código separado por ;)',
        help_text='Ingrese los códigos UNSPSC separados por punto y coma (;)'
    )
    descripcion = models.TextField(verbose_name='Descripción')
    fecha_estimada_inicio = models.CharField(
        max_length=50,
        choices=MESES_CHOICES,
        verbose_name='Fecha estimada de inicio de proceso de selección (mes)'
    )
    fecha_estimada_presentacion_ofertas = models.CharField(
        max_length=50,
        choices=MESES_CHOICES,
        verbose_name='Fecha estimada de presentación de ofertas (mes)'
    )
    duracion_contrato_numero = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Duración del contrato (número)'
    )
    duracion_contrato_intervalo = models.CharField(
        max_length=10,
        choices=DURACION_INTERVALO_CHOICES,
        verbose_name='Duración del contrato (intervalo)'
    )
    modalidad_seleccion = models.CharField(
        max_length=200,
        choices=MODALIDAD_SELECCION_CHOICES,
        verbose_name='Modalidad de selección'
    )
    fuente_recursos = models.CharField(
        max_length=100,
        choices=FUENTE_RECURSOS_CHOICES,
        verbose_name='Fuente de los recursos'
    )
    valor_total_estimado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor total estimado'
    )
    valor_estimado_vigencia_actual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor estimado en la vigencia actual'
    )
    requiere_vigencias_futuras = models.BooleanField(
        default=False,
        verbose_name='¿Se requieren vigencias futuras?'
    )
    estado_solicitud_vigencias_futuras = models.CharField(
        max_length=20,
        choices=ESTADO_VIGENCIAS_FUTURAS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Estado de solicitud de vigencias futuras'
    )
    correo_responsable = models.EmailField(
        verbose_name='Correo electrónico del responsable'
    )
    debe_cumplir_30_porciento_alimentos = models.CharField(
        max_length=2,
        choices=SI_NO_CHOICES,
        verbose_name='¿Debe cumplir con invertir mínimo el 30% de los recursos del presupuesto destinados a comprar alimentos, cumpliendo con lo establecido en la Ley 2046 de 2020, reglamentada por el Decreto 248 de 2021?'
    )
    incluye_bienes_servicios_distintos_alimentos = models.CharField(
        max_length=2,
        choices=SI_NO_CHOICES,
        verbose_name='¿El contrato incluye el suministro de bienes y servicios distintos a alimentos?'
    )
    tipo_solicitud = models.CharField(
        max_length=20,
        choices=TIPO_SOLICITUD_CHOICES,
        verbose_name='Tipo de solicitud'
    )
    justificacion = models.TextField(verbose_name='Justificación')
    
    # Usuarios
    usuario_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_paa_enviadas',
        verbose_name='Usuario solicitante'
    )
    usuario_aprobador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_paa_aprobadas',
        verbose_name='Usuario aprobador'
    )
    
    # Fechas de aprobación/rechazo
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de aprobación/rechazo')
    
    # Comentarios del aprobador
    comentarios_aprobador = models.TextField(blank=True, null=True, verbose_name='Comentarios del aprobador')
    
    objects = SolicitudPAAManager()
    
    def aprobar(self, usuario_aprobador, comentarios=''):
        """Aprueba la solicitud y aplica los cambios al registro real."""
        from django.utils import timezone
        
        self.estado = 'aprobada'
        self.usuario_aprobador = usuario_aprobador
        self.fecha_aprobacion = timezone.now()
        self.comentarios_aprobador = comentarios
        self.save()
        
        # Aplicar cambios según el tipo de acción
        if self.tipo_accion == 'crear':
            # Crear nuevo registro
            nuevo_registro = PlanAnualAdquisicion(
                subdireccion=self.subdireccion,
                codigos_unspsc=self.codigos_unspsc,
                descripcion=self.descripcion,
                fecha_estimada_inicio=self.fecha_estimada_inicio,
                fecha_estimada_presentacion_ofertas=self.fecha_estimada_presentacion_ofertas,
                duracion_contrato_numero=self.duracion_contrato_numero,
                duracion_contrato_intervalo=self.duracion_contrato_intervalo,
                modalidad_seleccion=self.modalidad_seleccion,
                fuente_recursos=self.fuente_recursos,
                valor_total_estimado=self.valor_total_estimado,
                valor_estimado_vigencia_actual=self.valor_estimado_vigencia_actual,
                requiere_vigencias_futuras=self.requiere_vigencias_futuras,
                estado_solicitud_vigencias_futuras=self.estado_solicitud_vigencias_futuras,
                correo_responsable=self.correo_responsable,
                debe_cumplir_30_porciento_alimentos=self.debe_cumplir_30_porciento_alimentos,
                incluye_bienes_servicios_distintos_alimentos=self.incluye_bienes_servicios_distintos_alimentos,
                tipo_solicitud=self.tipo_solicitud,
                justificacion=self.justificacion,
                user=self.usuario_solicitante,
            )
            nuevo_registro.save()
            # Actualizar el código en la solicitud para referencia
            self.codigo = nuevo_registro.codigo
            self.save()
            
        elif self.tipo_accion == 'modificar' and self.registro_original:
            # Actualizar registro existente
            registro = self.registro_original
            registro.subdireccion = self.subdireccion
            registro.codigos_unspsc = self.codigos_unspsc
            registro.descripcion = self.descripcion
            registro.fecha_estimada_inicio = self.fecha_estimada_inicio
            registro.fecha_estimada_presentacion_ofertas = self.fecha_estimada_presentacion_ofertas
            registro.duracion_contrato_numero = self.duracion_contrato_numero
            registro.duracion_contrato_intervalo = self.duracion_contrato_intervalo
            registro.modalidad_seleccion = self.modalidad_seleccion
            registro.fuente_recursos = self.fuente_recursos
            registro.valor_total_estimado = self.valor_total_estimado
            registro.valor_estimado_vigencia_actual = self.valor_estimado_vigencia_actual
            registro.requiere_vigencias_futuras = self.requiere_vigencias_futuras
            registro.estado_solicitud_vigencias_futuras = self.estado_solicitud_vigencias_futuras
            registro.correo_responsable = self.correo_responsable
            registro.debe_cumplir_30_porciento_alimentos = self.debe_cumplir_30_porciento_alimentos
            registro.incluye_bienes_servicios_distintos_alimentos = self.incluye_bienes_servicios_distintos_alimentos
            registro.tipo_solicitud = self.tipo_solicitud
            registro.justificacion = self.justificacion
            registro.user = self.usuario_solicitante
            registro.save()
            
        elif self.tipo_accion == 'eliminar' and self.registro_original:
            # Eliminar registro (soft delete)
            self.registro_original.soft_delete()
    
    def rechazar(self, usuario_aprobador, comentarios=''):
        """Rechaza la solicitud."""
        from django.utils import timezone
        
        self.estado = 'rechazada'
        self.usuario_aprobador = usuario_aprobador
        self.fecha_aprobacion = timezone.now()
        self.comentarios_aprobador = comentarios
        self.save()
    
    def get_fecha_creacion_datetime(self):
        """Convierte el timestamp a datetime para mostrar en templates."""
        if self.fecha_creacion:
            return datetime.fromtimestamp(self.fecha_creacion)
        return None
    
    def __str__(self):
        accion = dict(TIPO_ACCION_CHOICES).get(self.tipo_accion, self.tipo_accion)
        estado = dict(ESTADO_SOLICITUD_CHOICES).get(self.estado, self.estado)
        codigo = self.codigo or (self.registro_original.codigo if self.registro_original else 'N/A')
        return f"{accion} - {codigo} ({estado})"
    
    class Meta:
        verbose_name = 'Solicitud PAA'
        verbose_name_plural = 'Solicitudes PAA'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_accion']),
            models.Index(fields=['usuario_solicitante']),
            models.Index(fields=['registro_original']),
        ]

