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
    print("Cliente MinIO inicializado correctamente.")
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo configurar el cliente MinIO. Verifica variables de entorno. Error: {e}")
    minio_client = None

# --- Vista para el Dashboard ---
@login_required
def dashboard_view(request):
    """
    Muestra una lista de las últimas cargas de archivos registradas.
    """
    # Obtiene los últimos 20 registros de carga, ordenados por fecha descendente
    try:
        ultimas_cargas = RegistroCarga.objects.all().order_by('-fecha_hora_carga')[:20]
    except Exception as e:
        # Manejo básico de error si la tabla no existe o hay otro problema
        print(f"Error al obtener registros de carga: {e}")
        messages.error(request, "No se pudieron obtener los registros de carga.")
        ultimas_cargas = [] # Envía una lista vacía a la plantilla

    # Prepara el contexto para la plantilla
    context = {
        'cargas': ultimas_cargas,
        'titulo_pagina': 'Dashboard de Cargas' # Ejemplo de otra variable de contexto
    }
    # Renderiza la plantilla HTML del dashboard
    return render(request, 'ingesta/dashboard.html', context)

# --- Vista Principal de Carga ---
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            tipo_proceso_seleccionado = form.cleaned_data['tipo_proceso']

            # Validación básica de extensión
            if not uploaded_file.name.lower().endswith('.csv'):
                messages.error(request, 'Error: El archivo debe tener extensión .csv')
                return render(request, 'ingesta/upload_form.html', {'form': form})

            # Validación de estructura específica usando la función importada
            print(f"Validando archivo '{uploaded_file.name}' para el proceso: {tipo_proceso_seleccionado}")
            es_valido, error_validacion = validar_estructura_csv(uploaded_file, tipo_proceso_seleccionado)

            if not es_valido:
                messages.error(request, f"Error de formato en '{uploaded_file.name}': {error_validacion}")
                return render(request, 'ingesta/upload_form.html', {'form': form})

            # Si la validación es correcta, proceder
            print(f"Archivo validado correctamente. Procediendo a subir a MinIO.")
            if not minio_client:
                 messages.error(request, 'Error: Servicio MinIO no configurado.')
                 return render(request, 'ingesta/upload_form.html', {'form': form})

            # Definir nombre del objeto en MinIO
            original_filename = uploaded_file.name
            timestamp_folder = datetime.now().strftime('%Y/%m/%d')
            unique_id = uuid.uuid4()
            object_name = f"csv_entrantes/{tipo_proceso_seleccionado}/{timestamp_folder}/{original_filename.replace('.csv', '')}_{unique_id}.csv"

            # Subir a MinIO y luego guardar en BD
            try:
                # Asegurar que el bucket exista (opcional pero recomendado)
                found = minio_client.bucket_exists(MINIO_BUCKET)
                if not found:
                    minio_client.make_bucket(MINIO_BUCKET)
                    print(f"Bucket '{MINIO_BUCKET}' creado en MinIO.")

                # Volver al inicio del archivo antes de subir
                uploaded_file.seek(0)

                # Subir a MinIO
                minio_client.put_object(
                    bucket_name=MINIO_BUCKET,
                    object_name=object_name,
                    data=uploaded_file,
                    length=uploaded_file.size,
                    content_type='text/csv' # Forzar tipo correcto
                )
                print(f"Archivo subido exitosamente a MinIO como {object_name}")

                # Si la subida a MinIO fue exitosa, intentar guardar en BD
                try:
                    registro = RegistroCarga(
                        nombre_archivo_original=original_filename,
                        path_minio=object_name,
                        estado='EN_MINIO', # Estado actualizado
                        tipo_proceso=tipo_proceso_seleccionado # Guardamos el tipo
                        # subsecretaria_origen = ... # Añadir si se captura
                    )
                    registro.save()
                    print(f"Registro de carga guardado en BD (ID: {registro.id})")
                    # Mensaje final de éxito solo si todo funcionó
                    messages.success(request, f'Archivo "{original_filename}" (Tipo: {tipo_proceso_seleccionado}) validado y subido correctamente.')

                except Exception as db_error:
                    # Error SÓLO al guardar en BD (ya subió a MinIO)
                    print(f"ERROR al guardar en BD después de subir a MinIO: {db_error}")
                    messages.error(request, f"Error CRÍTICO: El archivo '{original_filename}' se subió al almacenamiento, pero falló el registro en la base de datos. Contacta al administrador. Error: {db_error}")
                    # Considerar qué hacer aquí. ¿Dejar el archivo en MinIO? ¿Intentar borrarlo?
                    # Por ahora, informamos el error grave. No redirigimos.

            except S3Error as minio_error:
                # Error durante la subida a MinIO
                print(f"Error de MinIO/S3 al subir archivo: {minio_error}")
                messages.error(request, f"Error al subir archivo al almacenamiento: {minio_error}")
            except Exception as general_error:
                # Otro error inesperado
                print(f"Error inesperado durante la subida/guardado: {general_error}")
                messages.error(request, f"Error inesperado al procesar el archivo: {general_error}")

            # Redirigir SOLO si todo el bloque try/except anidado fue exitoso
            # Si hubo error de BD, no se llega aquí. Si hubo error de MinIO, tampoco.
            if 'registro' in locals() and registro.pk: # Verifica si se creó el registro
                 return redirect('upload_file')
            # Si no se guardó en BD (por el error específico de BD), no redirige

        else: # Formulario no válido (campos faltantes, etc.)
             messages.error(request, 'Formulario inválido. Revisa los campos.')

    else: # Petición GET
        form = UploadFileForm()

    # Renderizar la plantilla en caso de GET o si hubo errores que no redirigieron
    return render(request, 'ingesta/upload_form.html', {'form': form})