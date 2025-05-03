from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ingesta.models import RegistroCarga
from globalfunctions.string_manager import get_string
from .base import get_template_context, handle_error
from ingesta.minio_utils import get_minio_client

@login_required
def dashboard_view(request):
    """
    Muestra el panel principal con estadísticas y actividad reciente.
    """
    try:
        minio_client = get_minio_client()
        # Get statistics
        total_files = RegistroCarga.objects.count()
        completed_files = RegistroCarga.objects.filter(estado='COMPLETADO').count()
        success_rate = round((completed_files / total_files * 100) if total_files > 0 else 0)
        recent_uploads = RegistroCarga.objects.filter(
            fecha_hora_carga__gte=timezone.now() - timedelta(hours=24)
        ).count()
        active_processes = RegistroCarga.objects.filter(
            estado__in=['EN_MINIO', 'PROCESANDO_NIFI']
        ).count()

        # Get recent activity
        recent_activity = RegistroCarga.objects.all().order_by('-fecha_hora_carga')[:5]

        # System services status
        system_services = [
            {
                'name': 'MinIO Storage',
                'description': 'Servicio de almacenamiento de archivos',
                'status': 'active' if minio_client else 'error',
                'status_display': get_string('templates.active', 'ingesta') if minio_client else get_string('templates.error', 'ingesta')
            },
            {
                'name': 'Base de Datos',
                'description': 'PostgreSQL Database',
                'status': 'active',
                'status_display': get_string('templates.active', 'ingesta')
            },
            {
                'name': 'NiFi Pipeline',
                'description': 'Procesamiento de datos',
                'status': 'active' if active_processes > 0 else 'inactive',
                'status_display': get_string('templates.active', 'ingesta') if active_processes > 0 else get_string('templates.inactive', 'ingesta')
            }
        ]

        context = {
            'total_files': total_files,
            'success_rate': success_rate,
            'recent_uploads': recent_uploads,
            'active_processes': active_processes,
            'recent_activity': recent_activity,
            'system_services': system_services,
            'TEMPLATE_DASHBOARD_TITLE': get_string('templates.dashboard_title', 'ingesta'),
            'TEMPLATE_DASHBOARD_WELCOME': get_string('templates.dashboard_welcome', 'ingesta'),
            'TEMPLATE_DASHBOARD_DESCRIPTION': get_string('templates.dashboard_description', 'ingesta'),
            'TEMPLATE_TOTAL_FILES': get_string('templates.total_files', 'ingesta'),
            'TEMPLATE_SUCCESS_RATE': get_string('templates.success_rate', 'ingesta'),
            'TEMPLATE_RECENT_UPLOADS': get_string('templates.recent_uploads', 'ingesta'),
            'TEMPLATE_ACTIVE_PROCESSES': get_string('templates.active_processes', 'ingesta'),
            'TEMPLATE_QUICK_ACTIONS': get_string('templates.quick_actions', 'ingesta'),
            'TEMPLATE_VIEW_HISTORY': get_string('templates.view_history', 'ingesta'),
            'TEMPLATE_SYSTEM_STATUS': get_string('templates.system_status', 'ingesta'),
            'TEMPLATE_ACTIVITY_OVERVIEW': get_string('templates.activity_overview', 'ingesta'),
            'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
            'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
            'TEMPLATE_DATE_TIME': get_string('templates.date_time', 'ingesta'),
            'TEMPLATE_ORIGINAL_FILE': get_string('templates.original_file', 'ingesta'),
            'TEMPLATE_PROCESS_TYPE': get_string('templates.process_type', 'ingesta'),
            'TEMPLATE_STATUS': get_string('templates.status', 'ingesta'),
            'TEMPLATE_NO_RECORDS': get_string('templates.no_records', 'ingesta'),
            'TEMPLATE_NO_RECORDS_DESCRIPTION': get_string('templates.no_records_description', 'ingesta'),
            'TEMPLATE_MODULE_INGESTA': get_string('modules.ingesta.name', 'ingesta'),
            'TEMPLATE_MODULE_INGESTA_DESC': get_string('modules.ingesta.description', 'ingesta'),
            'TEMPLATE_MODULE_PRESUPUESTO': get_string('modules.presupuesto.name', 'ingesta'),
            'TEMPLATE_MODULE_PRESUPUESTO_DESC': get_string('modules.presupuesto.description', 'ingesta'),
            'TEMPLATE_MODULE_PAA': get_string('modules.paa.name', 'ingesta'),
            'TEMPLATE_MODULE_PAA_DESC': get_string('modules.paa.description', 'ingesta'),
            'TEMPLATE_MODULE_REPORTES': get_string('modules.reportes.name', 'ingesta'),
            'TEMPLATE_MODULE_REPORTES_DESC': get_string('modules.reportes.description', 'ingesta'),
            'TEMPLATE_MODULE_COMING_SOON': get_string('modules.coming_soon.name', 'ingesta'),
            'TEMPLATE_MODULE_COMING_SOON_DESC': get_string('modules.coming_soon.description', 'ingesta')
        }
        context.update(get_template_context())
        return render(request, 'ingesta/dashboard.html', context)

    except Exception as e:
        print(get_string('errors.db_load', 'ingesta').format(error=e))
        return handle_error(
            request,
            get_string('errors.dashboard', 'ingesta'),
            'ingesta/dashboard.html'
        ) 