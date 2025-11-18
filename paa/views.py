from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .models import PlanAnualAdquisicion, SolicitudPAA, SUBDIRECCIONES_CHOICES
from .forms import PlanAnualAdquisicionForm, SolicitudPAAForm
from accounts.models import UserProfile
from accounts.utils import role_required, user_can_approve_paa, user_can_access_paa
from globalfunctions.string_manager import get_string
from coreview.base import get_template_context


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA, UserProfile.ROLE_MASTER_PAA])
def paa_list(request):
    """Lista de registros del Plan Anual de Adquisiciones con filtro por subdirección, código y fechas."""
    from datetime import datetime
    
    subdireccion_filter = request.GET.get('subdireccion', '')
    codigo_filter = request.GET.get('codigo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    page_number = request.GET.get('page', 1)
    
    # Obtener solo registros activos (no eliminados)
    registros = PlanAnualAdquisicion.objects.activos()
    
    # Aplicar filtro por subdirección si se proporciona
    if subdireccion_filter:
        registros = registros.filter(subdireccion=subdireccion_filter)
    
    # Aplicar filtro por código si se proporciona (búsqueda numérica)
    if codigo_filter:
        try:
            # Buscar códigos que contengan el número (ej: si buscan "001", encuentra SAF-001, SAL-001, etc.)
            registros = registros.filter(codigo__icontains=codigo_filter)
        except ValueError:
            # Si no es un número válido, ignorar el filtro
            pass
    
    # Aplicar filtro por fecha desde
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            # Convertir a timestamp para comparar con fecha_creacion
            timestamp_desde = int(fecha_desde_obj.timestamp())
            registros = registros.filter(fecha_creacion__gte=timestamp_desde)
        except ValueError:
            pass
    
    # Aplicar filtro por fecha hasta
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            # Convertir a timestamp y agregar un día completo (86400 segundos) para incluir todo el día
            timestamp_hasta = int(fecha_hasta_obj.timestamp()) + 86400
            registros = registros.filter(fecha_creacion__lte=timestamp_hasta)
        except ValueError:
            pass
    
    # Ordenar por código
    registros = registros.order_by('codigo')
    
    # Paginación con máximo 50 items por página
    paginator = Paginator(registros, 50)
    page_obj = paginator.get_page(page_number)
    
    # Obtener IDs de registros en la página actual con solicitudes pendientes
    registros_ids = [r.pk for r in page_obj]
    solicitudes_pendientes = SolicitudPAA.objects.filter(
        registro_original_id__in=registros_ids,
        estado='pendiente'
    ).values_list('registro_original_id', flat=True)
    registros_con_solicitud_pendiente = set(solicitudes_pendientes)
    
    context = {
        'page_obj': page_obj,
        'subdireccion_filter': subdireccion_filter,
        'codigo_filter': codigo_filter,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'subdirecciones_choices': SUBDIRECCIONES_CHOICES,
        'registros_con_solicitud_pendiente': registros_con_solicitud_pendiente,
        'TEMPLATE_TITLE': get_string('list.title', 'paa'),
        'TEMPLATE_DESCRIPTION': get_string('list.description', 'paa'),
        'TEMPLATE_FILTER_SUBDIRECCION': get_string('list.filter_subdireccion', 'paa'),
        'TEMPLATE_FILTER_CODE': get_string('list.filter_code', 'paa'),
        'TEMPLATE_FILTER_FECHA_DESDE': get_string('list.filter_fecha_desde', 'paa'),
        'TEMPLATE_FILTER_FECHA_HASTA': get_string('list.filter_fecha_hasta', 'paa'),
        'TEMPLATE_FILTER_ALL': get_string('list.filter_all', 'paa'),
        'TEMPLATE_NO_RECORDS': get_string('list.no_records', 'paa'),
        'TEMPLATE_CODE_LABEL': get_string('form.code_label', 'paa'),
        'TEMPLATE_DESCRIPTION_LABEL': get_string('form.description_label', 'paa'),
        'TEMPLATE_CREATE': get_string('list.create', 'paa'),
        'TEMPLATE_PENDING_REQUEST': get_string('list.pending_request', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/paa_list.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA, UserProfile.ROLE_MASTER_PAA])
def mis_solicitudes(request):
    """Lista de solicitudes del usuario actual."""
    estado_filter = request.GET.get('estado', '')
    page_number = request.GET.get('page', 1)
    
    # Obtener solo las solicitudes del usuario actual
    solicitudes = SolicitudPAA.objects.filter(usuario_solicitante=request.user)
    
    # Aplicar filtro por estado si se proporciona
    if estado_filter:
        solicitudes = solicitudes.filter(estado=estado_filter)
    
    # Ordenar por fecha de creación (más recientes primero)
    solicitudes = solicitudes.order_by('-fecha_creacion')
    
    # Paginación con máximo 50 items por página
    paginator = Paginator(solicitudes, 50)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estado_filter': estado_filter,
        'TEMPLATE_TITLE': get_string('my_requests.title', 'paa'),
        'TEMPLATE_DESCRIPTION': get_string('my_requests.description', 'paa'),
        'TEMPLATE_FILTER_ESTADO': get_string('my_requests.filter_estado', 'paa'),
        'TEMPLATE_FILTER_ALL': get_string('my_requests.filter_all', 'paa'),
        'TEMPLATE_NO_RECORDS': get_string('my_requests.no_records', 'paa'),
        'TEMPLATE_ESTADO_PENDIENTE': get_string('my_requests.estado_pendiente', 'paa'),
        'TEMPLATE_ESTADO_APROBADA': get_string('my_requests.estado_aprobada', 'paa'),
        'TEMPLATE_ESTADO_RECHAZADA': get_string('my_requests.estado_rechazada', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/mis_solicitudes.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA])
def paa_create(request):
    """Crear solicitud para nuevo registro del Plan Anual de Adquisiciones."""
    if request.method == 'POST':
        form = PlanAnualAdquisicionForm(request.POST)
        if form.is_valid():
            # Crear solicitud en lugar de guardar directamente
            solicitud = SolicitudPAA(
                tipo_accion='crear',
                usuario_solicitante=request.user,
                subdireccion=form.cleaned_data['subdireccion'],
                codigos_unspsc=form.cleaned_data['codigos_unspsc'],
                descripcion=form.cleaned_data['descripcion'],
                fecha_estimada_inicio=form.cleaned_data['fecha_estimada_inicio'],
                fecha_estimada_presentacion_ofertas=form.cleaned_data['fecha_estimada_presentacion_ofertas'],
                duracion_contrato_numero=form.cleaned_data['duracion_contrato_numero'],
                duracion_contrato_intervalo=form.cleaned_data['duracion_contrato_intervalo'],
                modalidad_seleccion=form.cleaned_data['modalidad_seleccion'],
                fuente_recursos=form.cleaned_data['fuente_recursos'],
                valor_total_estimado=form.cleaned_data['valor_total_estimado'],
                valor_estimado_vigencia_actual=form.cleaned_data['valor_estimado_vigencia_actual'],
                requiere_vigencias_futuras=form.cleaned_data['requiere_vigencias_futuras'],
                estado_solicitud_vigencias_futuras=form.cleaned_data.get('estado_solicitud_vigencias_futuras'),
                correo_responsable=form.cleaned_data['correo_responsable'],
                debe_cumplir_30_porciento_alimentos=form.cleaned_data['debe_cumplir_30_porciento_alimentos'],
                incluye_bienes_servicios_distintos_alimentos=form.cleaned_data['incluye_bienes_servicios_distintos_alimentos'],
                tipo_solicitud='Nueva',  # Siempre es "Nueva" al crear
                justificacion=form.cleaned_data['justificacion'],
            )
            solicitud.save()
            messages.success(request, get_string('success.request_created', 'paa'))
            return redirect('paa:my_requests')
    else:
        form = PlanAnualAdquisicionForm()
    
    context = {
        'form': form,
        'TEMPLATE_TITLE': get_string('form.create_title', 'paa'),
        'TEMPLATE_DESCRIPTION': get_string('form.create_description', 'paa'),
        'TEMPLATE_FORM_TITLE': get_string('form.form_title', 'paa'),
        'TEMPLATE_CODE_LABEL': get_string('form.code_label', 'paa'),
        'TEMPLATE_BACK': get_string('form.back', 'paa'),
        'TEMPLATE_SAVE': get_string('form.save', 'paa'),
        'is_create': True,
    }
    context.update(get_template_context())
    
    return render(request, 'paa/paa_form.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA])
def paa_edit(request, pk):
    """Crear solicitud para modificar registro existente del Plan Anual de Adquisiciones."""
    registro = get_object_or_404(PlanAnualAdquisicion, pk=pk)
    
    # Verificar que el registro no esté eliminado
    if registro.eliminado:
        messages.error(request, get_string('errors.record_deleted', 'paa'))
        return redirect('paa:create')
    
    if request.method == 'POST':
        form = PlanAnualAdquisicionForm(request.POST, instance=registro)
        if form.is_valid():
            # Crear solicitud de modificación
            # La subdirección no se puede modificar, usar la del registro original
            solicitud = SolicitudPAA(
                tipo_accion='modificar',
                registro_original=registro,
                usuario_solicitante=request.user,
                codigo=registro.codigo,
                subdireccion=registro.subdireccion,  # Usar la subdirección original, no la del formulario
                codigos_unspsc=form.cleaned_data['codigos_unspsc'],
                descripcion=form.cleaned_data['descripcion'],
                fecha_estimada_inicio=form.cleaned_data['fecha_estimada_inicio'],
                fecha_estimada_presentacion_ofertas=form.cleaned_data['fecha_estimada_presentacion_ofertas'],
                duracion_contrato_numero=form.cleaned_data['duracion_contrato_numero'],
                duracion_contrato_intervalo=form.cleaned_data['duracion_contrato_intervalo'],
                modalidad_seleccion=form.cleaned_data['modalidad_seleccion'],
                fuente_recursos=form.cleaned_data['fuente_recursos'],
                valor_total_estimado=form.cleaned_data['valor_total_estimado'],
                valor_estimado_vigencia_actual=form.cleaned_data['valor_estimado_vigencia_actual'],
                requiere_vigencias_futuras=form.cleaned_data['requiere_vigencias_futuras'],
                estado_solicitud_vigencias_futuras=form.cleaned_data.get('estado_solicitud_vigencias_futuras'),
                correo_responsable=form.cleaned_data['correo_responsable'],
                debe_cumplir_30_porciento_alimentos=form.cleaned_data['debe_cumplir_30_porciento_alimentos'],
                incluye_bienes_servicios_distintos_alimentos=form.cleaned_data['incluye_bienes_servicios_distintos_alimentos'],
                tipo_solicitud='Modificacion',  # Siempre es "Modificación" al editar un registro
                justificacion=form.cleaned_data['justificacion'],
            )
            solicitud.save()
            messages.success(request, get_string('success.request_created', 'paa'))
            return redirect('paa:my_requests')
    else:
        form = PlanAnualAdquisicionForm(instance=registro)
    
    context = {
        'form': form,
        'registro': registro,
        'TEMPLATE_TITLE': get_string('form.edit_title', 'paa'),
        'TEMPLATE_DESCRIPTION': get_string('form.edit_description', 'paa'),
        'TEMPLATE_FORM_TITLE': get_string('form.form_title', 'paa'),
        'TEMPLATE_CODE_LABEL': get_string('form.code_label', 'paa'),
        'TEMPLATE_BACK': get_string('form.back', 'paa'),
        'TEMPLATE_SAVE': get_string('form.save', 'paa'),
        'is_create': False,
    }
    context.update(get_template_context())
    
    return render(request, 'paa/paa_form.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA])
def paa_delete(request, pk):
    """Crear solicitud para eliminar registro."""
    registro = get_object_or_404(PlanAnualAdquisicion, pk=pk)
    
    if request.method == 'POST':
        # Crear solicitud de eliminación
        solicitud = SolicitudPAA(
            tipo_accion='eliminar',
            registro_original=registro,
            usuario_solicitante=request.user,
            codigo=registro.codigo,
            subdireccion=registro.subdireccion,
            codigos_unspsc=registro.codigos_unspsc,
            descripcion=registro.descripcion,
            fecha_estimada_inicio=registro.fecha_estimada_inicio,
            fecha_estimada_presentacion_ofertas=registro.fecha_estimada_presentacion_ofertas,
            duracion_contrato_numero=registro.duracion_contrato_numero,
            duracion_contrato_intervalo=registro.duracion_contrato_intervalo,
            modalidad_seleccion=registro.modalidad_seleccion,
            fuente_recursos=registro.fuente_recursos,
            valor_total_estimado=registro.valor_total_estimado,
            valor_estimado_vigencia_actual=registro.valor_estimado_vigencia_actual,
            requiere_vigencias_futuras=registro.requiere_vigencias_futuras,
            estado_solicitud_vigencias_futuras=registro.estado_solicitud_vigencias_futuras,
            correo_responsable=registro.correo_responsable,
            debe_cumplir_30_porciento_alimentos=registro.debe_cumplir_30_porciento_alimentos,
            incluye_bienes_servicios_distintos_alimentos=registro.incluye_bienes_servicios_distintos_alimentos,
            tipo_solicitud='Eliminacion',
            justificacion=registro.justificacion,
        )
        solicitud.save()
        messages.success(request, get_string('success.request_created', 'paa'))
        return redirect('paa:create')
    
    context = {
        'registro': registro,
        'TEMPLATE_TITLE': get_string('form.delete_title', 'paa'),
        'TEMPLATE_CONFIRM_MESSAGE': get_string('form.delete_confirm', 'paa'),
        'TEMPLATE_CODE_LABEL': get_string('form.code_label', 'paa'),
        'TEMPLATE_DESCRIPTION_LABEL': get_string('form.description_label', 'paa'),
        'TEMPLATE_CANCEL': get_string('form.cancel', 'paa'),
        'TEMPLATE_DELETE': get_string('form.delete', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/paa_confirm_delete.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_MASTER_PAA])
def paa_approval_list(request):
    """Lista de solicitudes pendientes de aprobación."""
    solicitudes = SolicitudPAA.objects.pendientes().order_by('-fecha_creacion')
    
    context = {
        'solicitudes': solicitudes,
        'TEMPLATE_TITLE': get_string('approval.list_title', 'paa'),
        'TEMPLATE_DESCRIPTION': get_string('approval.list_description', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/paa_approval_list.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_MASTER_PAA])
def paa_approval_detail(request, pk):
    """Detalle de solicitud para aprobar/rechazar."""
    solicitud = get_object_or_404(SolicitudPAA, pk=pk)
    
    if solicitud.estado != 'pendiente':
        messages.error(request, get_string('approval.already_processed', 'paa'))
        return redirect('paa:approval_list')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        comentarios = request.POST.get('comentarios', '')
        
        if accion == 'aprobar':
            solicitud.aprobar(request.user, comentarios)
            messages.success(request, get_string('approval.approved', 'paa'))
        elif accion == 'rechazar':
            solicitud.rechazar(request.user, comentarios)
            messages.success(request, get_string('approval.rejected', 'paa'))
        
        return redirect('paa:approval_list')
    
    # Obtener datos del registro original si existe
    registro_original = None
    if solicitud.registro_original:
        registro_original = solicitud.registro_original
    
    context = {
        'solicitud': solicitud,
        'registro_original': registro_original,
        'TEMPLATE_TITLE': get_string('approval.detail_title', 'paa'),
        'TEMPLATE_APPROVE': get_string('approval.approve', 'paa'),
        'TEMPLATE_REJECT': get_string('approval.reject', 'paa'),
        'TEMPLATE_COMMENTS': get_string('approval.comments', 'paa'),
        'TEMPLATE_BACK': get_string('form.back', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/paa_approval_detail.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA])
def solicitud_edit(request, pk):
    """Editar una solicitud pendiente o rechazada."""
    solicitud = get_object_or_404(SolicitudPAA, pk=pk)
    
    # Verificar que el usuario sea el propietario de la solicitud
    if solicitud.usuario_solicitante != request.user:
        messages.error(request, 'No tiene permiso para editar esta solicitud.')
        return redirect('paa:my_requests')
    
    # Solo se pueden editar solicitudes pendientes o rechazadas
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede editar una solicitud aprobada.')
        return redirect('paa:my_requests')
    
    if request.method == 'POST':
        form = SolicitudPAAForm(request.POST, instance=solicitud)
        if form.is_valid():
            # Actualizar los campos
            # La subdirección no se puede modificar, mantener la original
            # solicitud.subdireccion = form.cleaned_data['subdireccion']  # No modificar
            solicitud.codigos_unspsc = form.cleaned_data['codigos_unspsc']
            solicitud.descripcion = form.cleaned_data['descripcion']
            solicitud.fecha_estimada_inicio = form.cleaned_data['fecha_estimada_inicio']
            solicitud.fecha_estimada_presentacion_ofertas = form.cleaned_data['fecha_estimada_presentacion_ofertas']
            solicitud.duracion_contrato_numero = form.cleaned_data['duracion_contrato_numero']
            solicitud.duracion_contrato_intervalo = form.cleaned_data['duracion_contrato_intervalo']
            solicitud.modalidad_seleccion = form.cleaned_data['modalidad_seleccion']
            solicitud.fuente_recursos = form.cleaned_data['fuente_recursos']
            solicitud.valor_total_estimado = form.cleaned_data['valor_total_estimado']
            solicitud.valor_estimado_vigencia_actual = form.cleaned_data['valor_estimado_vigencia_actual']
            solicitud.requiere_vigencias_futuras = form.cleaned_data['requiere_vigencias_futuras']
            solicitud.estado_solicitud_vigencias_futuras = form.cleaned_data.get('estado_solicitud_vigencias_futuras')
            solicitud.correo_responsable = form.cleaned_data['correo_responsable']
            solicitud.debe_cumplir_30_porciento_alimentos = form.cleaned_data['debe_cumplir_30_porciento_alimentos']
            solicitud.incluye_bienes_servicios_distintos_alimentos = form.cleaned_data['incluye_bienes_servicios_distintos_alimentos']
            # El tipo_solicitud se mantiene según el tipo_accion de la solicitud
            if solicitud.tipo_accion == 'crear':
                solicitud.tipo_solicitud = 'Nueva'
            elif solicitud.tipo_accion == 'modificar':
                solicitud.tipo_solicitud = 'Modificacion'
            elif solicitud.tipo_accion == 'eliminar':
                solicitud.tipo_solicitud = 'Eliminacion'
            solicitud.justificacion = form.cleaned_data['justificacion']
            
            # Si estaba rechazada, volver a estado pendiente
            if solicitud.estado == 'rechazada':
                solicitud.estado = 'pendiente'
                solicitud.usuario_aprobador = None
                solicitud.fecha_aprobacion = None
                solicitud.comentarios_aprobador = ''
            
            solicitud.save()
            messages.success(request, get_string('success.request_updated', 'paa'))
            return redirect('paa:my_requests')
    else:
        form = SolicitudPAAForm(instance=solicitud)
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'TEMPLATE_TITLE': get_string('my_requests.edit_title', 'paa'),
        'TEMPLATE_DESCRIPTION': get_string('my_requests.edit_description', 'paa'),
        'TEMPLATE_FORM_TITLE': get_string('form.form_title', 'paa'),
        'TEMPLATE_BACK': get_string('form.back', 'paa'),
        'TEMPLATE_SAVE': get_string('form.save', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/solicitud_form.html', context)


@role_required([UserProfile.ROLE_ADMIN, UserProfile.ROLE_EDITOR_PAA])
def solicitud_delete(request, pk):
    """Eliminar una solicitud pendiente o rechazada."""
    solicitud = get_object_or_404(SolicitudPAA, pk=pk)
    
    # Verificar que el usuario sea el propietario de la solicitud
    if solicitud.usuario_solicitante != request.user:
        messages.error(request, 'No tiene permiso para eliminar esta solicitud.')
        return redirect('paa:my_requests')
    
    # Solo se pueden eliminar solicitudes pendientes o rechazadas
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede eliminar una solicitud aprobada.')
        return redirect('paa:my_requests')
    
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, get_string('success.request_deleted', 'paa'))
        return redirect('paa:my_requests')
    
    context = {
        'solicitud': solicitud,
        'TEMPLATE_TITLE': get_string('my_requests.delete_title', 'paa'),
        'TEMPLATE_CONFIRM_MESSAGE': get_string('my_requests.delete_confirm', 'paa'),
        'TEMPLATE_DELETE': get_string('form.delete', 'paa'),
        'TEMPLATE_CANCEL': get_string('form.cancel', 'paa'),
    }
    context.update(get_template_context())
    
    return render(request, 'paa/solicitud_confirm_delete.html', context)
