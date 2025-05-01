import os
import uuid
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required 
from minio import Minio
from minio.error import S3Error
from .forms import UploadFileForm
from .validators import validar_estructura_csv
from .models import RegistroCarga
from .messages import (
    FILE_EXTENSION_ERROR, MINIO_NOT_CONFIGURED, MINIO_UPLOAD_ERROR,
    MINIO_BUCKET_CREATED, MINIO_UPLOAD_SUCCESS, DB_SAVE_ERROR,
    DB_SAVE_SUCCESS, INVALID_FORM, DASHBOARD_ERROR, MINIO_INIT_SUCCESS,
    MINIO_INIT_ERROR, DB_SAVE_PRINT, DB_LOAD_ERROR, PRINT_VALIDATING_FILE,
    PRINT_VALIDATION_SUCCESS, PRINT_DB_ERROR, PRINT_MINIO_ERROR,
    PRINT_GENERAL_ERROR, TEMPLATE_TITLE, TEMPLATE_NAVBAR_BRAND,
    TEMPLATE_DASHBOARD, TEMPLATE_UPLOAD_FILE, TEMPLATE_LOAD_NEW_FILE,
    TEMPLATE_NO_RECORDS, TEMPLATE_UPLOAD_TITLE, TEMPLATE_FILE_HELP,
    TEMPLATE_UPLOAD_BUTTON, TEMPLATE_DASHBOARD_TITLE, TEMPLATE_DATE_TIME,
    TEMPLATE_ORIGINAL_FILE, TEMPLATE_SUBSECRETARY, TEMPLATE_PROCESS_TYPE,
    TEMPLATE_STATUS, TEMPLATE_MINIO_PATH, TEMPLATE_ERROR, TEMPLATE_NA,
    TEMPLATE_DASH
)

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
    print(MINIO_INIT_SUCCESS)
except Exception as e:
    print(MINIO_INIT_ERROR.format(error=e))
    minio_client = None

# --- Vista para el Dashboard ---
@login_required
def dashboard_view(request):
    """
    Muestra una lista de las últimas cargas de archivos registradas.
    """
    try:
        ultimas_cargas = RegistroCarga.objects.all().order_by('-fecha_hora_carga')[:20]
    except Exception as e:
        print(DB_LOAD_ERROR.format(error=e))
        messages.error(request, DASHBOARD_ERROR)
        ultimas_cargas = []

    context = {
        'cargas': ultimas_cargas,
        'titulo_pagina': TEMPLATE_DASHBOARD_TITLE,
        'TEMPLATE_TITLE': TEMPLATE_TITLE,
        'TEMPLATE_NAVBAR_BRAND': TEMPLATE_NAVBAR_BRAND,
        'TEMPLATE_DASHBOARD': TEMPLATE_DASHBOARD,
        'TEMPLATE_UPLOAD_FILE': TEMPLATE_UPLOAD_FILE,
        'TEMPLATE_LOAD_NEW_FILE': TEMPLATE_LOAD_NEW_FILE,
        'TEMPLATE_NO_RECORDS': TEMPLATE_NO_RECORDS,
        'TEMPLATE_DATE_TIME': TEMPLATE_DATE_TIME,
        'TEMPLATE_ORIGINAL_FILE': TEMPLATE_ORIGINAL_FILE,
        'TEMPLATE_SUBSECRETARY': TEMPLATE_SUBSECRETARY,
        'TEMPLATE_PROCESS_TYPE': TEMPLATE_PROCESS_TYPE,
        'TEMPLATE_STATUS': TEMPLATE_STATUS,
        'TEMPLATE_MINIO_PATH': TEMPLATE_MINIO_PATH,
        'TEMPLATE_ERROR': TEMPLATE_ERROR,
        'TEMPLATE_NA': TEMPLATE_NA,
        'TEMPLATE_DASH': TEMPLATE_DASH
    }
    return render(request, 'ingesta/dashboard.html', context)

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
                messages.error(request, FILE_EXTENSION_ERROR)
                return render(request, 'ingesta/upload_form.html', {
                    'form': form,
                    'TEMPLATE_TITLE': TEMPLATE_TITLE,
                    'TEMPLATE_NAVBAR_BRAND': TEMPLATE_NAVBAR_BRAND,
                    'TEMPLATE_DASHBOARD': TEMPLATE_DASHBOARD,
                    'TEMPLATE_UPLOAD_FILE': TEMPLATE_UPLOAD_FILE,
                    'TEMPLATE_UPLOAD_TITLE': TEMPLATE_UPLOAD_TITLE,
                    'TEMPLATE_FILE_HELP': TEMPLATE_FILE_HELP,
                    'TEMPLATE_UPLOAD_BUTTON': TEMPLATE_UPLOAD_BUTTON
                })

            # Validación de estructura específica usando la función importada
            print(PRINT_VALIDATING_FILE.format(
                filename=uploaded_file.name,
                process_type=tipo_proceso_seleccionado
            ))
            es_valido, error_validacion = validar_estructura_csv(uploaded_file, subsecretaria_origen, tipo_proceso_seleccionado)

            if not es_valido:
                messages.error(request, error_validacion)
                return render(request, 'ingesta/upload_form.html', {
                    'form': form,
                    'TEMPLATE_TITLE': TEMPLATE_TITLE,
                    'TEMPLATE_NAVBAR_BRAND': TEMPLATE_NAVBAR_BRAND,
                    'TEMPLATE_DASHBOARD': TEMPLATE_DASHBOARD,
                    'TEMPLATE_UPLOAD_FILE': TEMPLATE_UPLOAD_FILE,
                    'TEMPLATE_UPLOAD_TITLE': TEMPLATE_UPLOAD_TITLE,
                    'TEMPLATE_FILE_HELP': TEMPLATE_FILE_HELP,
                    'TEMPLATE_UPLOAD_BUTTON': TEMPLATE_UPLOAD_BUTTON
                })

            # Si la validación es correcta, proceder
            print(PRINT_VALIDATION_SUCCESS)
            if not minio_client:
                messages.error(request, MINIO_NOT_CONFIGURED)
                return render(request, 'ingesta/upload_form.html', {
                    'form': form,
                    'TEMPLATE_TITLE': TEMPLATE_TITLE,
                    'TEMPLATE_NAVBAR_BRAND': TEMPLATE_NAVBAR_BRAND,
                    'TEMPLATE_DASHBOARD': TEMPLATE_DASHBOARD,
                    'TEMPLATE_UPLOAD_FILE': TEMPLATE_UPLOAD_FILE,
                    'TEMPLATE_UPLOAD_TITLE': TEMPLATE_UPLOAD_TITLE,
                    'TEMPLATE_FILE_HELP': TEMPLATE_FILE_HELP,
                    'TEMPLATE_UPLOAD_BUTTON': TEMPLATE_UPLOAD_BUTTON
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
                    print(MINIO_BUCKET_CREATED.format(bucket=MINIO_BUCKET))

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
                print(MINIO_UPLOAD_SUCCESS.format(object_name=object_name))

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
                    print(DB_SAVE_PRINT.format(id=registro.id))
                    messages.success(request, DB_SAVE_SUCCESS.format(
                        filename=original_filename,
                        process_type=tipo_proceso_seleccionado
                    ))

                except Exception as db_error:
                    print(PRINT_DB_ERROR.format(error=db_error))
                    messages.error(request, DB_SAVE_ERROR.format(
                        filename=original_filename,
                        error=str(db_error)
                    ))

            except S3Error as minio_error:
                print(PRINT_MINIO_ERROR.format(error=minio_error))
                messages.error(request, MINIO_UPLOAD_ERROR.format(error=str(minio_error)))
            except Exception as general_error:
                print(PRINT_GENERAL_ERROR.format(error=general_error))
                messages.error(request, str(general_error))

            if 'registro' in locals() and registro.pk:
                return redirect('upload_file')

        else:
            messages.error(request, INVALID_FORM)

    else:
        form = UploadFileForm()

    return render(request, 'ingesta/upload_form.html', {
        'form': form,
        'TEMPLATE_TITLE': TEMPLATE_TITLE,
        'TEMPLATE_NAVBAR_BRAND': TEMPLATE_NAVBAR_BRAND,
        'TEMPLATE_DASHBOARD': TEMPLATE_DASHBOARD,
        'TEMPLATE_UPLOAD_FILE': TEMPLATE_UPLOAD_FILE,
        'TEMPLATE_UPLOAD_TITLE': TEMPLATE_UPLOAD_TITLE,
        'TEMPLATE_FILE_HELP': TEMPLATE_FILE_HELP,
        'TEMPLATE_UPLOAD_BUTTON': TEMPLATE_UPLOAD_BUTTON
    })