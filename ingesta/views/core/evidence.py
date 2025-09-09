import uuid
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from minio.error import S3Error
from coreview.minio_utils import get_minio_client, get_minio_bucket
from coreview.base import get_template_context
from ingesta.models import RegistroCarga, EvidenciaCarga
from ingesta.forms import EvidenceUploadForm
from globalfunctions.string_manager import get_string


minio_client = get_minio_client()
MINIO_BUCKET = get_minio_bucket()


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    return filename[:255]


@login_required
def evidence_list_view(request, file_id):
    registro = get_object_or_404(RegistroCarga, id=file_id)
    evidencias = registro.evidencias.all().order_by('-fecha_hora_subida')

    if request.method == 'POST':
        form = EvidenceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract all files directly from request.FILES (supports multiple)
            files = request.FILES.getlist('files')
            descripcion = form.cleaned_data.get('descripcion')

            if not minio_client:
                messages.error(request, get_string('ingesta.errors.minio_not_configured', 'ingesta'))
                return redirect('ingesta:evidence_list', file_id=registro.id)

            saved_count = 0
            for f in files:
                original_filename = sanitize_filename(f.name)
                object_name = f"{registro.subsecretaria_origen}/{registro.tipo_proceso}/{registro.id}/evidencias/{uuid.uuid4()}-{original_filename}"
                try:
                    # Ensure bucket
                    if not minio_client.bucket_exists(MINIO_BUCKET):
                        minio_client.make_bucket(MINIO_BUCKET)

                    # Upload
                    f.seek(0)
                    minio_client.put_object(
                        bucket_name=MINIO_BUCKET,
                        object_name=object_name,
                        data=f,
                        length=f.size,
                        content_type=getattr(f, 'content_type', 'application/octet-stream')
                    )

                    # Save DB record
                    EvidenciaCarga.objects.create(
                        registro_carga=registro,
                        nombre_archivo_original=original_filename,
                        path_minio=object_name,
                        user=request.user,
                        descripcion=descripcion,
                        size_bytes=getattr(f, 'size', None),
                        content_type=getattr(f, 'content_type', None),
                    )
                    saved_count += 1
                except S3Error as e:
                    messages.error(request, get_string('ingesta.errors.minio_upload', 'ingesta').format(error=str(e)))
                except Exception as e:
                    messages.error(request, get_string('ingesta.errors.unexpected_error', 'ingesta').format(error=str(e)))

            if saved_count:
                messages.success(request, f"{saved_count} evidencia(s) subida(s) correctamente")
            return redirect('ingesta:evidence_list', file_id=registro.id)
    else:
        form = EvidenceUploadForm()

    context = {
        'registro': registro,
        'evidencias': evidencias,
        'form': form,
        'TEMPLATE_EVIDENCE_TITLE': 'Evidencias del Archivo',
        'TEMPLATE_EVIDENCE_DESCRIPTION': 'Suba documentos de respaldo (hasta 10MB por archivo).',
    }
    context.update(get_template_context())
    return render(request, 'ingesta/evidence_list.html', context)


@login_required
def download_evidence(request, evidence_id):
    evidencia = get_object_or_404(EvidenciaCarga, id=evidence_id)
    if not evidencia.path_minio:
        messages.error(request, get_string('ingesta.errors.file_not_available', 'ingesta'))
        return redirect('ingesta:evidence_list', file_id=evidencia.registro_carga_id)

    try:
        response = minio_client.get_object(
            MINIO_BUCKET,
            evidencia.path_minio
        )
        response_data = HttpResponse(
            response.read(),
            content_type=evidencia.content_type or 'application/octet-stream'
        )
        response_data['Content-Disposition'] = f'attachment; filename="{evidencia.nombre_archivo_original}"'
        return response_data
    except S3Error as e:
        messages.error(request, get_string('ingesta.errors.download_error', 'ingesta').format(error=str(e)))
        return redirect('ingesta:evidence_list', file_id=evidencia.registro_carga_id)
    except Exception as e:
        messages.error(request, get_string('ingesta.errors.unexpected_error', 'ingesta').format(error=str(e)))
        return redirect('ingesta:evidence_list', file_id=evidencia.registro_carga_id)


def admin_required(user):
    return user.is_staff or user.is_superuser


@user_passes_test(admin_required)
def delete_evidence(request, evidence_id):
    evidencia = get_object_or_404(EvidenciaCarga, id=evidence_id)
    registro_id = evidencia.registro_carga_id
    try:
        if evidencia.path_minio:
            minio_client.remove_object(MINIO_BUCKET, evidencia.path_minio)
        evidencia.delete()
        messages.success(request, get_string('ingesta.success.file_deleted', 'ingesta'))
    except S3Error as e:
        messages.error(request, get_string('ingesta.errors.minio_delete_error', 'ingesta').format(error=str(e)))
    except Exception as e:
        messages.error(request, get_string('ingesta.errors.unexpected_error', 'ingesta').format(error=str(e)))
    return redirect('ingesta:evidence_list', file_id=registro_id)


