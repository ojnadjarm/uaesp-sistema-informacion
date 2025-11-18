from django.contrib import admin
from .models import PlanAnualAdquisicion, SolicitudPAA

@admin.register(PlanAnualAdquisicion)
class PlanAnualAdquisicionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'subdireccion', 'descripcion', 'tipo_solicitud', 'eliminado', 'fecha_creacion')
    list_filter = ('subdireccion', 'tipo_solicitud', 'eliminado')
    search_fields = ('codigo', 'descripcion', 'correo_responsable')
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_actualizacion')

@admin.register(SolicitudPAA)
class SolicitudPAAAdmin(admin.ModelAdmin):
    list_display = ('tipo_accion', 'codigo', 'subdireccion', 'estado', 'usuario_solicitante', 'fecha_creacion', 'fecha_aprobacion')
    list_filter = ('estado', 'tipo_accion', 'subdireccion')
    search_fields = ('codigo', 'descripcion', 'usuario_solicitante__username')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'fecha_aprobacion')

