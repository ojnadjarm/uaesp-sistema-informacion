import os
import uuid
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from minio import Minio
from minio.error import S3Error
from .forms import UploadFileForm
from .validators import validar_estructura_csv
from .models import RegistroCarga
from globalfunctions.string_manager import get_string
from django.http import HttpResponse, HttpResponseForbidden

# --- Configuración Cliente MinIO ---
try:
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT_URL', 'minio:9000').split('//')[-1]
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'password_minio')
    MINIO_USE_HTTPS = os.environ.get('MINIO_USE_HTTPS', '0') == '1'
    MINIO_BUCKET = os.environ.get('MINIO_BUCKET_NAME', 'uaesp-ingesta-crudo')

    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_USE_HTTPS
    )
    print(get_string('success.minio_init', 'ingesta'))
except Exception as e:
    print(get_string('errors.minio_init', 'ingesta').format(error=e))
    minio_client = None

# --- Vista para el Dashboard ---
@login_required
def dashboard_view(request):
    """
    Muestra el panel principal con estadísticas y actividad reciente.
    """
    try:
        # Get statistics
        total_files = RegistroCarga.objects.count()
        completed_files = RegistroCarga.objects.filter(estado='COMPLETADO').count()
        success_rate = round((completed_files / total_files * 100) if total_files > 0 else 0)
        recent_uploads = RegistroCarga.objects.filter(
            fecha_hora_carga__gte=datetime.now() - timedelta(hours=24)
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

    except Exception as e:
        print(get_string('errors.db_load', 'ingesta').format(error=e))
        messages.error(request, get_string('errors.dashboard', 'ingesta'))
        total_files = 0
        success_rate = 0
        recent_uploads = 0
        active_processes = 0
        recent_activity = []
        system_services = []

    context = {
        'total_files': total_files,
        'success_rate': success_rate,
        'recent_uploads': recent_uploads,
        'active_processes': active_processes,
        'recent_activity': recent_activity,
        'system_services': system_services,
        'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
        'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
        'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
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
    return render(request, 'ingesta/dashboard.html', context)

# --- Vista para el Historial de Archivos ---
@login_required
def file_history_view(request):
    """
    Muestra una lista completa de las cargas de archivos registradas.
    """
    try:
        cargas = RegistroCarga.objects.all().order_by('-fecha_hora_carga')
    except Exception as e:
        print(get_string('errors.db_load', 'ingesta').format(error=e))
        messages.error(request, get_string('errors.dashboard', 'ingesta'))
        cargas = []

    context = {
        'cargas': cargas,
        'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
        'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
        'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
        'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
        'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
        'TEMPLATE_HISTORY_TITLE': get_string('templates.history_title', 'ingesta'),
        'TEMPLATE_HISTORY_DESCRIPTION': get_string('templates.history_description', 'ingesta'),
        'TEMPLATE_LOAD_NEW_FILE': get_string('templates.load_new_file', 'ingesta'),
        'TEMPLATE_DATE_TIME': get_string('templates.date_time', 'ingesta'),
        'TEMPLATE_ORIGINAL_FILE': get_string('templates.original_file', 'ingesta'),
        'TEMPLATE_SUBSECRETARY': get_string('templates.subsecretary', 'ingesta'),
        'TEMPLATE_PROCESS_TYPE': get_string('templates.process_type', 'ingesta'),
        'TEMPLATE_STATUS': get_string('templates.status', 'ingesta'),
        'TEMPLATE_MINIO_PATH': get_string('templates.minio_path', 'ingesta'),
        'TEMPLATE_ERROR': get_string('templates.error', 'ingesta'),
        'TEMPLATE_NA': get_string('templates.na', 'ingesta'),
        'TEMPLATE_DASH': get_string('templates.dash', 'ingesta'),
        'TEMPLATE_NO_RECORDS': get_string('templates.no_records', 'ingesta'),
        'TEMPLATE_NO_RECORDS_DESCRIPTION': get_string('templates.no_records_description', 'ingesta'),
        'TEMPLATE_CONFIRM_DELETE': get_string('templates.confirm_delete', 'ingesta'),
        'TEMPLATE_CONFIRM_DELETE_MESSAGE': get_string('templates.confirm_delete_message', 'ingesta'),
        'TEMPLATE_CANCEL': get_string('templates.cancel', 'ingesta'),
        'TEMPLATE_DELETE': get_string('templates.delete', 'ingesta')
    }
    return render(request, 'ingesta/file_history.html', context)

# --- Vista Principal de Carga ---
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            subsecretaria_origen = form.cleaned_data['subsecretaria']
            tipo_proceso_seleccionado = form.cleaned_data['tipo_proceso']

            # Validación básica de extensión
            if not (uploaded_file.name.lower().endswith('.csv') or uploaded_file.name.lower().endswith('.xlsx')):
                messages.error(request, get_string('errors.file_extension', 'ingesta'))
                return render(request, 'ingesta/upload_form.html', {
                    'form': form,
                    'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
                    'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
                    'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
                    'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
                    'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
                    'TEMPLATE_UPLOAD_TITLE': get_string('templates.upload_title', 'ingesta'),
                    'TEMPLATE_FILE_HELP': get_string('templates.file_help', 'ingesta'),
                    'TEMPLATE_UPLOAD_BUTTON': get_string('templates.upload_button', 'ingesta')
                })

            # Validación de estructura específica usando la función importada
            print(get_string('messages.validating_file', 'ingesta').format(
                filename=uploaded_file.name,
                process_type=tipo_proceso_seleccionado
            ))
            es_valido, error_validacion = validar_estructura_csv(uploaded_file, subsecretaria_origen, tipo_proceso_seleccionado)

            if not es_valido:
                messages.error(request, error_validacion)
                return render(request, 'ingesta/upload_form.html', {
                    'form': form,
                    'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
                    'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
                    'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
                    'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
                    'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
                    'TEMPLATE_UPLOAD_TITLE': get_string('templates.upload_title', 'ingesta'),
                    'TEMPLATE_FILE_HELP': get_string('templates.file_help', 'ingesta'),
                    'TEMPLATE_UPLOAD_BUTTON': get_string('templates.upload_button', 'ingesta')
                })

            # Si la validación es correcta, proceder
            print(get_string('messages.validation_success', 'ingesta'))
            if not minio_client:
                messages.error(request, get_string('errors.minio_not_configured', 'ingesta'))
                return render(request, 'ingesta/upload_form.html', {
                    'form': form,
                    'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
                    'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
                    'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
                    'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
                    'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
                    'TEMPLATE_UPLOAD_TITLE': get_string('templates.upload_title', 'ingesta'),
                    'TEMPLATE_FILE_HELP': get_string('templates.file_help', 'ingesta'),
                    'TEMPLATE_UPLOAD_BUTTON': get_string('templates.upload_button', 'ingesta')
                })

            # Definir nombre del objeto en MinIO
            original_filename = uploaded_file.name
            timestamp_folder = datetime.now().strftime('%Y/%m/%d')
            unique_id = uuid.uuid4()
            object_name = f"{subsecretaria_origen}/{tipo_proceso_seleccionado}/{timestamp_folder}/{original_filename.replace('.csv', '').replace('.xlsx', '')}_{unique_id}{'.csv' if original_filename.lower().endswith('.csv') else '.xlsx'}"

            # Subir a MinIO y luego guardar en BD
            try:
                # Asegurar que el bucket exista
                found = minio_client.bucket_exists(MINIO_BUCKET)
                if not found:
                    minio_client.make_bucket(MINIO_BUCKET)
                    print(get_string('messages.bucket_created', 'ingesta').format(bucket=MINIO_BUCKET))

                # Volver al inicio del archivo antes de subir
                uploaded_file.seek(0)

                # Subir a MinIO
                minio_client.put_object(
                    bucket_name=MINIO_BUCKET,
                    object_name=object_name,
                    data=uploaded_file,
                    length=uploaded_file.size,
                    content_type='text/csv' if original_filename.lower().endswith('.csv') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                print(get_string('messages.upload_success', 'ingesta').format(object_name=object_name))

                # Si la subida a MinIO fue exitosa, intentar guardar en BD
                try:
                    registro = RegistroCarga(
                        nombre_archivo_original=original_filename,
                        path_minio=object_name,
                        estado='EN_MINIO',
                        tipo_proceso=tipo_proceso_seleccionado,
                        subsecretaria_origen=subsecretaria_origen,
                    )
                    registro.save()
                    print(get_string('messages.db_save_print', 'ingesta').format(id=registro.id))
                    messages.success(request, get_string('messages.db_save_success', 'ingesta').format(
                        filename=original_filename,
                        process_type=tipo_proceso_seleccionado
                    ))

                except Exception as db_error:
                    print(get_string('messages.db_error', 'ingesta').format(error=db_error))
                    messages.error(request, get_string('errors.db_save_error', 'ingesta').format(
                        filename=original_filename,
                        error=str(db_error)
                    ))

            except S3Error as minio_error:
                print(get_string('messages.minio_error', 'ingesta').format(error=minio_error))
                messages.error(request, get_string('errors.upload_error', 'ingesta').format(error=str(minio_error)))
            except Exception as general_error:
                print(get_string('messages.general_error', 'ingesta').format(error=general_error))
                messages.error(request, str(general_error))

            if 'registro' in locals() and registro.pk:
                return redirect('upload_file')

        else:
            messages.error(request, get_string('errors.invalid_form', 'ingesta'))

    else:
        form = UploadFileForm()

    return render(request, 'ingesta/upload_form.html', {
        'form': form,
        'TEMPLATE_TITLE': get_string('templates.title', 'ingesta'),
        'TEMPLATE_NAVBAR_BRAND': get_string('templates.navbar_brand', 'ingesta'),
        'TEMPLATE_DASHBOARD': get_string('templates.dashboard', 'ingesta'),
        'TEMPLATE_UPLOAD_FILE': get_string('templates.upload_file', 'ingesta'),
        'TEMPLATE_FILE_HISTORY': get_string('templates.file_history', 'ingesta'),
        'TEMPLATE_UPLOAD_TITLE': get_string('templates.upload_title', 'ingesta'),
        'TEMPLATE_FILE_HELP': get_string('templates.file_help', 'ingesta'),
        'TEMPLATE_UPLOAD_BUTTON': get_string('templates.upload_button', 'ingesta')
    })

@login_required
def download_file(request, file_id):
    """
    Download a file from MinIO storage.
    """
    carga = get_object_or_404(RegistroCarga, id=file_id)
    
    if not carga.path_minio:
        messages.error(request, get_string('errors.file_not_available', 'ingesta'))
        return redirect('file_history')
    
    try:
        # Get the file from MinIO
        response = minio_client.get_object(
            MINIO_BUCKET,
            carga.path_minio
        )
        
        # Create the response
        response_data = HttpResponse(
            response.read(),
            content_type='application/octet-stream'
        )
        response_data['Content-Disposition'] = f'attachment; filename="{carga.nombre_archivo_original}"'
        
        return response_data
    except S3Error as e:
        messages.error(request, get_string('errors.download_error', 'ingesta').format(error=str(e)))
        return redirect('file_history')
    except Exception as e:
        messages.error(request, get_string('errors.unexpected_error', 'ingesta').format(error=str(e)))
        return redirect('file_history')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_file(request, file_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden(get_string('errors.no_permissions', 'ingesta'))
    
    carga = get_object_or_404(RegistroCarga, id=file_id)
    
    try:
        # Delete from MinIO if path exists
        if carga.path_minio:
            minio_client.remove_object(MINIO_BUCKET, carga.path_minio)
        
        # Delete from database
        carga.delete()
        
        messages.success(request, get_string('success.file_deleted', 'ingesta'))
    except S3Error as e:
        messages.error(request, get_string('errors.minio_delete_error', 'ingesta').format(error=str(e)))
    except Exception as e:
        messages.error(request, get_string('errors.unexpected_error', 'ingesta').format(error=str(e)))
    
    return redirect('file_history')