import re
from datetime import datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from minio.error import S3Error

from accounts.models import UserProfile
from accounts.utils import get_user_role, role_required, user_allowed_subsecretarias
from coreview.base import get_template_context, handle_error
from coreview.minio_utils import get_minio_client, get_minio_bucket
from globalfunctions.string_manager import get_string
from ingesta.decorators import admin_required
from ingesta.forms import PROCESS_TO_SUBSECRETARIA, UploadFileForm
from ingesta.models import RegistroCarga
from ingesta.validators import validar_estructura_csv

minio_client = get_minio_client()
MINIO_BUCKET = get_minio_bucket()

def _get_allowed_subsecretarias(user):
    allowed = user_allowed_subsecretarias(user)
    if allowed is None:
        return None
    return set(allowed)


def _filter_cargas_for_user(user, queryset):
    allowed = _get_allowed_subsecretarias(user)
    if allowed is None:
        return queryset
    if not allowed:
        return queryset.none()
    return queryset.filter(subsecretaria_origen__in=allowed)


def _ensure_registro_access(user, registro):
    allowed = _get_allowed_subsecretarias(user)
    if allowed is None:
        return True
    return registro.subsecretaria_origen in allowed


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_DATA_INGESTOR])
def file_history_view(request):
    """
    Muestra una lista completa de las cargas de archivos registradas.
    """
    try:
        cargas = _filter_cargas_for_user(
            request.user,
            RegistroCarga.objects.all().order_by('-fecha_hora_carga'),
        )
        if get_user_role(request.user) != UserProfile.ROLE_ADMIN:
            cargas = cargas.filter(user=request.user)
        context = {
            'cargas': cargas,
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
            'TEMPLATE_DELETE': get_string('templates.delete', 'ingesta'),
            'TEMPLATE_CONFIRM_FILE_LABEL': get_string('templates.modal_file_label', 'ingesta')
        }
        context.update(get_template_context())
        return render(request, 'ingesta/file_history.html', context)
    except Exception as e:
        print(get_string('errors.db_load', 'ingesta').format(error=e))
        return handle_error(
            request,
            get_string('errors.dashboard', 'ingesta'),
            'ingesta/file_history.html'
        )

def sanitize_filename(filename):
    """Limpia el nombre del archivo para que sea seguro."""
    # Remover caracteres no permitidos
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    # Limitar longitud
    return filename[:255]

@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_DATA_INGESTOR])
def upload_file_view(request):
    allowed_subsecretarias = _get_allowed_subsecretarias(request.user)
    form_kwargs = {}
    if allowed_subsecretarias is not None:
        form_kwargs['allowed_subsecretarias'] = list(allowed_subsecretarias)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES, **form_kwargs)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            tipo_proceso_seleccionado = form.cleaned_data['tipo_proceso']
            subsecretaria_origen = PROCESS_TO_SUBSECRETARIA.get(tipo_proceso_seleccionado)

            if allowed_subsecretarias is not None and subsecretaria_origen not in allowed_subsecretarias:
                messages.error(request, get_string('errors.no_permissions', 'ingesta'))
                return redirect('ingesta:upload_file')

            # Sanitizar nombre del archivo
            original_filename = sanitize_filename(uploaded_file.name)

            # Validación básica de extensión
            if not (uploaded_file.name.lower().endswith('.csv') or uploaded_file.name.lower().endswith('.xlsx')):
                messages.error(request, get_string('errors.file_extension', 'ingesta'))
                return render_upload_form(request, form)
            
            # Validación de estructura específica
            print(get_string('messages.validating_file', 'ingesta').format(
                filename=original_filename,
                process_type=tipo_proceso_seleccionado
            ))
            validation_result = validar_estructura_csv(uploaded_file, subsecretaria_origen, tipo_proceso_seleccionado)

            # Verificar si es un error simple (2 elementos)
            if len(validation_result) == 2:
                es_valido, error_validacion = validation_result
                if not es_valido:
                    messages.error(request, error_validacion)
                    # Redirigir en lugar de renderizar para evitar reenvío del formulario
                    return redirect('ingesta:upload_file')
                # Si es válido, continuar con el proceso
            # Verificar si es un error con archivo de errores (3 elementos)
            elif len(validation_result) == 3:
                es_valido, error_validacion, error_df = validation_result
                if not es_valido:
                    # Guardar el DataFrame de errores en la sesión para descarga
                    if error_df is not None and not error_df.empty:
                        import base64
                        import io
                        
                        # Crear el archivo CSV en memoria
                        csv_buffer = io.StringIO()
                        
                        # Agregar información del reporte al inicio
                        from datetime import datetime
                        csv_buffer.write(get_string('errors.report_title', 'ingesta') + "\n")
                        csv_buffer.write(get_string('errors.report_original_file', 'ingesta').format(filename=original_filename) + "\n")
                        csv_buffer.write(get_string('errors.report_validation_date', 'ingesta').format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
                        csv_buffer.write(get_string('errors.report_total_rows_with_errors', 'ingesta').format(count=len(error_df)) + "\n")
                        csv_buffer.write(get_string('errors.report_total_errors_found', 'ingesta').format(count=error_df['Cantidad de Errores'].sum()) + "\n")
                        csv_buffer.write("\n")
                        
                        # Escribir el DataFrame de errores con codificación UTF-8 explícita
                        error_df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8')
                        csv_content = csv_buffer.getvalue()
                        csv_buffer.close()
                        
                        # Agregar BOM UTF-8 al inicio para compatibilidad con Excel
                        csv_content = '\ufeff' + csv_content
                        
                        # Codificar el contenido en base64
                        encoded_content = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
                        
                        # Guardar en la sesión
                        request.session['error_file_content'] = encoded_content
                        request.session['error_file_name'] = f"{get_string('errors.error_file_name_prefix', 'ingesta')}{original_filename.replace('.xlsx', '.csv').replace('.csv', '_errores.csv')}"
                        request.session['has_validation_errors'] = True
                    messages.error(request, error_validacion)
                    # Redirigir en lugar de renderizar para evitar reenvío del formulario
                    return redirect('ingesta:upload_file')
                # Si es válido, continuar con el proceso
            else:
                # Caso inesperado
                messages.error(request, get_string('errors.unexpected_error', 'ingesta').format(error="validación del archivo"))
                # Redirigir en lugar de renderizar para evitar reenvío del formulario
                return redirect('ingesta:upload_file')

            # Si la validación es correcta, proceder
            print(get_string('messages.validation_success', 'ingesta'))
            if not minio_client:
                messages.error(request, get_string('errors.minio_not_configured', 'ingesta'))
                # Redirigir en lugar de renderizar para evitar reenvío del formulario
                return redirect('ingesta:upload_file')

            try:
                with transaction.atomic():
                    # Crear registro en la base de datos
                    registro = RegistroCarga(
                        nombre_archivo_original=original_filename,
                        path_minio="temp_path",
                        estado='CARGADO',
                        tipo_proceso=tipo_proceso_seleccionado,
                        subsecretaria_origen=subsecretaria_origen,
                        user=request.user
                    )
                    registro.save()

                    # Definir nombre del objeto en MinIO
                    object_name = f"{subsecretaria_origen}/{tipo_proceso_seleccionado}/{registro.id}/{original_filename}"

                    # Asegurar que el bucket exista
                    if not minio_client.bucket_exists(MINIO_BUCKET):
                        minio_client.make_bucket(MINIO_BUCKET)
                        print(get_string('messages.bucket_created', 'ingesta').format(bucket=MINIO_BUCKET))

                    # Agregar mensaje de subida a almacenamiento
                    messages.info(request, get_string('errors.uploading_to_storage', 'ingesta'))
                    
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

                    # Actualizar registro en la base de datos
                    registro.path_minio = object_name
                    registro.estado = 'EN_MINIO'
                    registro.save()
                    print(get_string('messages.db_save_print', 'ingesta').format(id=registro.id))

                    # Agregar mensaje de procesamiento completado
                    messages.success(request, get_string('errors.processing_complete', 'ingesta'))
                    messages.success(request, get_string('messages.db_save_success', 'ingesta').format(
                        filename=original_filename,
                        process_type=tipo_proceso_seleccionado
                    ))

            except S3Error as minio_error:
                print(get_string('messages.minio_error', 'ingesta').format(error=minio_error))
                messages.error(request, get_string('errors.upload_error', 'ingesta').format(error=str(minio_error)))
                # Intentar limpiar el registro si existe
                if 'registro' in locals():
                    try:
                        registro.delete()
                    except Exception as e:
                        print(f"Error al limpiar registro: {e}")
            except Exception as general_error:
                print(get_string('messages.general_error', 'ingesta').format(error=general_error))
                messages.error(request, str(general_error))
                # Intentar limpiar el registro si existe
                if 'registro' in locals():
                    try:
                        registro.delete()
                    except Exception as e:
                        print(f"Error al limpiar registro: {e}")

            return redirect('ingesta:upload_file')

        else:
            messages.error(request, get_string('errors.invalid_form', 'ingesta'))
            # Redirigir en lugar de renderizar para evitar reenvío del formulario
            return redirect('ingesta:upload_file')

    else:
        # Solo limpiar errores si no hay errores activos (GET request normal)
        # Si hay errores activos, mantenerlos para mostrar el botón de descarga
        if not request.session.get('has_validation_errors', False):
            if 'error_file_content' in request.session:
                del request.session['error_file_content']
            if 'error_file_name' in request.session:
                del request.session['error_file_name']
            
        form = UploadFileForm(**form_kwargs)
        return render_upload_form(request, form)

def render_upload_form(request, form):
    """Función auxiliar para renderizar el formulario de carga."""
    context = {
        'form': form,
        'TEMPLATE_UPLOAD_TITLE': get_string('templates.upload_title', 'ingesta'),
        'TEMPLATE_FILE_HELP': get_string('templates.file_help', 'ingesta'),
        'TEMPLATE_UPLOAD_BUTTON': get_string('templates.upload_button', 'ingesta'),
        'TEMPLATE_DOWNLOAD_ERROR_FILE': get_string('errors.download_error_file', 'ingesta'),
        'TEMPLATE_PROCESSING_MODAL_TITLE': get_string('templates.processing_modal_title', 'ingesta'),
        'TEMPLATE_PROCESSING_SPINNER': get_string('templates.processing_spinner', 'ingesta'),
        'TEMPLATE_PROCESSING_INITIAL': get_string('templates.processing_initial_message', 'ingesta'),
        'TEMPLATE_PROCESSING_WARNING': get_string('templates.processing_warning', 'ingesta'),
        'TEMPLATE_PROCESSING_FILE_TEMPLATE': get_string('templates.processing_file_template', 'ingesta'),
        'TEMPLATE_PROCESSING_DEFAULT_FILENAME': get_string('templates.processing_default_filename', 'ingesta')
    }
    context.update(get_template_context())
    return render(request, 'ingesta/upload_form.html', context)

@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_DATA_INGESTOR])
def download_file(request, file_id):
    """
    Download a file from MinIO storage.
    """
    carga = get_object_or_404(RegistroCarga, id=file_id)

    if not _ensure_registro_access(request.user, carga):
        raise PermissionDenied
    
    if not carga.path_minio:
        messages.error(request, get_string('errors.file_not_available', 'ingesta'))
        return redirect('ingesta:file_history')

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
        return redirect('ingesta:file_history')
    except Exception as e:
        messages.error(request, get_string('errors.unexpected_error', 'ingesta').format(error=str(e)))
        return redirect('ingesta:file_history')

@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_DATA_INGESTOR])
def download_error_file(request):
    """
    Download the error file from session if it exists and belongs to the current user.
    """
    if ('error_file_content' not in request.session or 
        'error_file_name' not in request.session or 
        'has_validation_errors' not in request.session):
        messages.error(request, get_string('errors.no_error_file_available', 'ingesta'))
        return redirect('ingesta:upload_file')
    
    try:
        import base64
        
        # Obtener contenido del archivo de la sesión
        encoded_content = request.session['error_file_content']
        filename = request.session['error_file_name']
        
        # Decodificar contenido
        file_content = base64.b64decode(encoded_content)
        
        # Crear respuesta HTTP con codificación UTF-8 explícita
        response = HttpResponse(file_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Encoding'] = 'utf-8'
        
        # Limpiar la sesión después de descargar
        del request.session['error_file_content']
        del request.session['error_file_name']
        del request.session['has_validation_errors']
        
        # Agregar mensaje de confirmación
        messages.success(request, get_string('success.error_file_downloaded', 'ingesta'))
        
        return response
        
    except Exception as e:
        messages.error(request, get_string('errors.error_file_download_error', 'ingesta').format(error=str(e)))
        return redirect('ingesta:upload_file')

@admin_required
def delete_file(request, file_id):
    
    carga = get_object_or_404(RegistroCarga, id=file_id)
    
    try:
        # Delete related evidences from MinIO
        for ev in getattr(carga, 'evidencias', []).all():
            try:
                if ev.path_minio:
                    minio_client.remove_object(MINIO_BUCKET, ev.path_minio)
            except S3Error as e:
                messages.error(request, get_string('errors.minio_delete_error', 'ingesta').format(error=str(e)))
            except Exception as e:
                messages.error(request, get_string('errors.unexpected_error', 'ingesta').format(error=str(e)))

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
    
    return redirect('ingesta:file_history') 