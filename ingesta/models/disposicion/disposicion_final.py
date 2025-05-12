from django.db import models
from datetime import datetime
from ingesta.models.core.base import TimeStampedModel
from ingesta.models.core.registro_carga import RegistroCarga

class DisposicionFinalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def por_fecha(self, fecha_inicio, fecha_fin):
        return self.get_queryset().filter(
            fecha_entrada__gte=fecha_inicio,
            fecha_entrada__lte=fecha_fin
        )

    def por_vehiculo(self, placa):
        return self.get_queryset().filter(placa=placa)

    def por_concesion(self, concesion):
        return self.get_queryset().filter(concesion=concesion)

class DisposicionFinal(TimeStampedModel):
    """
    Modelo para registrar las disposiciones finales de residuos.
    """
    # Fechas y consecutivos
    fecha_entrada = models.DateField(null=True, blank=True)
    hora_entrada = models.TimeField(null=True, blank=True)
    fecha_salida = models.DateField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    epoch_entrada = models.BigIntegerField(null=True, blank=True)
    epoch_salida = models.BigIntegerField(null=True, blank=True)
    consecutivo_entrada = models.CharField(max_length=20, null=True, blank=True)
    consecutivo_salida = models.CharField(max_length=20, null=True, blank=True)
    
    # Información del vehículo
    placa = models.CharField(max_length=20, null=True, blank=True)
    numero_vehiculo = models.CharField(max_length=20, null=True, blank=True)
    
    # Información de ruta
    concesion = models.CharField(max_length=60, null=True, blank=True)
    macroruta = models.CharField(max_length=10, null=True, blank=True)
    microruta = models.CharField(max_length=10, null=True, blank=True)
    ase = models.CharField(max_length=60, null=True, blank=True)
    
    # Información del servicio
    servicio = models.CharField(max_length=60, null=True, blank=True)
    zona_descarga = models.CharField(max_length=60, null=True, blank=True)
    
    # Información de peso (en kilogramos)
    peso_entrada = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    peso_salida = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    peso_residuos = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    
    # Información de personal
    personas_entrada = models.IntegerField(null=True, blank=True)
    personas_salida = models.IntegerField(null=True, blank=True)
    usuario_entrada = models.CharField(max_length=30, null=True, blank=True)
    usuario_salida = models.CharField(max_length=30, null=True, blank=True)
    
    # Observaciones
    observaciones_entrada = models.CharField(max_length=500, blank=True, null=True)
    observaciones_salida = models.CharField(max_length=500, blank=True, null=True)
    observaciones_alerta_tara = models.CharField(max_length=500, blank=True, null=True)
    
    # Otros campos
    opciones = models.CharField(max_length=500, blank=True, null=True)
    imagen_entrada = models.URLField(max_length=500, blank=True, null=True)
    imagen_salida = models.URLField(max_length=500, blank=True, null=True)

    # Relación con registro de carga
    registro_carga = models.ForeignKey(RegistroCarga, on_delete=models.SET_NULL, null=True, blank=True)

    #equipo de pesaje
    equipo_pesaje = models.CharField(max_length=60, null=True, blank=True)
    ajuste_peso_salida = models.CharField(max_length=60, null=True, blank=True)
    tpo_vehiculo = models.CharField(max_length=60, null=True, blank=True)
    novedades = models.CharField(max_length=60, null=True, blank=True)

    # Proceso
    tipo_proceso = models.CharField(max_length=60, null=True, blank=True)

    objects = DisposicionFinalManager()

    def save(self, *args, **kwargs):
        # Calculate epoch time for entrada if both date and time are present
        if self.fecha_entrada and self.hora_entrada:
            entrada_datetime = datetime.combine(self.fecha_entrada, self.hora_entrada)
            self.epoch_entrada = int(entrada_datetime.timestamp())
        
        # Calculate epoch time for salida if both date and time are present
        if self.fecha_salida and self.hora_salida:
            salida_datetime = datetime.combine(self.fecha_salida, self.hora_salida)
            self.epoch_salida = int(salida_datetime.timestamp())
        
        # Calculate peso_residuos if both weights are present
        if self.peso_entrada is not None and self.peso_salida is not None:
            self.peso_residuos = self.peso_entrada - self.peso_salida
        
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
            models.Index(fields=['placa']),
            models.Index(fields=['concesion']),
            models.Index(fields=['fecha_entrada']),
        ]
        unique_together = ['fecha_entrada', 'hora_entrada', 'consecutivo_entrada']