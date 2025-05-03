from django.db import models
import uuid
from datetime import datetime

def get_current_timestamp():
    return int(datetime.now().timestamp())

class RegistroCarga(models.Model):
    ESTADOS = (
        ('RECIBIDO', 'Recibido en Django'),
        ('EN_MINIO', 'Subido a MinIO'),
        ('PROCESANDO_NIFI', 'Procesando por NiFi'),
        ('ERROR', 'Error'),
        ('COMPLETADO', 'Completado'),
    )
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_archivo_original = models.CharField(max_length=255)
    path_minio = models.CharField(max_length=500, blank=True, null=True)
    fecha_hora_carga = models.DateTimeField(auto_now_add=True)
    subsecretaria_origen = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='RECIBIDO')
    mensaje_error = models.TextField(blank=True, null=True)
    tipo_proceso = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_archivo_original} ({self.fecha_hora_carga.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ['-fecha_hora_carga']

class DisposicionFinal(models.Model):
    # Fechas y consecutivos
    fecha_entrada = models.DateField(null=True, blank=True)  # Fecha, longitud 30
    hora_entrada = models.TimeField(null=True, blank=True)  # Hora de entrada
    fecha_salida = models.DateField(null=True, blank=True)  # Fecha, longitud 30
    hora_salida = models.TimeField(null=True, blank=True)  # Hora de salida
    epoch_entrada = models.BigIntegerField(null=True, blank=True)  # Epoch time para entrada
    epoch_salida = models.BigIntegerField(null=True, blank=True)  # Epoch time para salida
    consecutivo_entrada = models.CharField(max_length=20, null=True, blank=True)  # Numérico, longitud 20
    consecutivo_salida = models.CharField(max_length=20, null=True, blank=True)  # Numérico, longitud 20
    
    # Información del vehículo
    placa = models.CharField(max_length=20, null=True, blank=True)  # Alfanumérico, longitud 20
    numero_vehiculo = models.CharField(max_length=20, null=True, blank=True)  # Alfanumérico, longitud 20
    
    # Información de ruta
    concesion = models.CharField(max_length=60, null=True, blank=True)  # Alfanumérico, longitud 60
    macroruta = models.CharField(max_length=10, null=True, blank=True)  # Numérico, longitud 10
    microruta = models.CharField(max_length=10, null=True, blank=True)  # Numérico, longitud 10
    ase = models.CharField(max_length=60, null=True, blank=True)  # Alfanumérico, longitud 60
    
    # Información del servicio
    servicio = models.CharField(max_length=60, null=True, blank=True)  # Alfanumérico, longitud 60
    zona_descarga = models.CharField(max_length=60, null=True, blank=True)  # Alfanumérico, longitud 60
    
    # Información de peso (en kilogramos)
    peso_entrada = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)  # Numérico, longitud 30
    peso_salida = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)  # Numérico, longitud 30
    peso_residuos = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)  # Numérico, longitud 30
    
    # Información de personal
    personas_entrada = models.IntegerField(null=True, blank=True)  # Numérico, longitud 10
    personas_salida = models.IntegerField(null=True, blank=True)  # Numérico, longitud 10
    usuario_entrada = models.CharField(max_length=30, null=True, blank=True)  # Alfanumérico, longitud 30
    usuario_salida = models.CharField(max_length=30, null=True, blank=True)  # Alfanumérico, longitud 30
    
    # Observaciones
    observaciones_entrada = models.CharField(max_length=60, blank=True, null=True)  # Alfanumérico, longitud 60
    observaciones_salida = models.CharField(max_length=60, blank=True, null=True)  # Alfanumérico, longitud 60
    observaciones_alerta_tara = models.CharField(max_length=60, blank=True, null=True)  # Alfanumérico, longitud 60
    
    # Otros campos
    opciones = models.CharField(max_length=60, blank=True, null=True)  # Alfanumérico, longitud 60
    imagen_entrada = models.URLField(max_length=500, blank=True, null=True)  # URL de la imagen de entrada
    imagen_salida = models.URLField(max_length=500, blank=True, null=True)  # URL de la imagen de salida

    # Campos de auditoría y relación
    fecha_creacion = models.BigIntegerField(default=get_current_timestamp)
    fecha_actualizacion = models.BigIntegerField(default=get_current_timestamp)
    registro_carga = models.ForeignKey(RegistroCarga, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate epoch time for entrada if both date and time are present
        if self.fecha_entrada and self.hora_entrada:
            entrada_datetime = datetime.combine(self.fecha_entrada, self.hora_entrada)
            self.epoch_entrada = int(entrada_datetime.timestamp())
        
        # Calculate epoch time for salida if both date and time are present
        if self.fecha_salida and self.hora_salida:
            salida_datetime = datetime.combine(self.fecha_salida, self.hora_salida)
            self.epoch_salida = int(salida_datetime.timestamp())
        
        # Update fecha_actualizacion with current timestamp
        self.fecha_actualizacion = int(datetime.now().timestamp())
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.consecutivo_entrada or 'Sin consecutivo'} - {self.placa or 'Sin placa'} ({self.fecha_entrada or 'Sin fecha'})"

    class Meta:
        verbose_name = 'Disposición Final'
        verbose_name_plural = 'Disposiciones Finales'
        ordering = ['-fecha_entrada', 'consecutivo_entrada']
        indexes = [
            models.Index(fields=['epoch_entrada']),
            models.Index(fields=['epoch_salida']),
        ]