from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from ingesta.models import Concesion, ASE, Servicio, ZonaDescarga
from ingesta.forms import ConcesionForm, ASEForm, ServicioForm, ZonaDescargaForm
from globalfunctions.string_manager import get_string
from coreview.base import get_template_context

# ============================================================================
# VISTAS PARA CONCESIONES
# ============================================================================

@login_required
def concesion_list(request):
    """Lista de concesiones con búsqueda y paginación."""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    concesiones = Concesion.objects.all()
    
    if search_query:
        concesiones = concesiones.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    paginator = Paginator(concesiones, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'TEMPLATE_TITLE': get_string('catalogos.concesion.title', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.concesion.description', 'ingesta'),
        'TEMPLATE_ADD': get_string('catalogos.concesion.add', 'ingesta'),
        'TEMPLATE_LIST': get_string('catalogos.concesion.list', 'ingesta'),
        'TEMPLATE_NO_RECORDS': get_string('catalogos.concesion.no_records', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/concesion_list.html', context)

@login_required
def concesion_create(request):
    """Crear nueva concesión."""
    if request.method == 'POST':
        form = ConcesionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_saved', 'ingesta'))
            return redirect('ingesta:concesion_list')
    else:
        form = ConcesionForm()
    
    context = {
        'form': form,
        'TEMPLATE_TITLE': get_string('catalogos.concesion.add', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.concesion.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/concesion_form.html', context)

@login_required
def concesion_edit(request, pk):
    """Editar concesión existente."""
    concesion = get_object_or_404(Concesion, pk=pk)
    
    if request.method == 'POST':
        form = ConcesionForm(request.POST, instance=concesion)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_updated', 'ingesta'))
            return redirect('ingesta:concesion_list')
    else:
        form = ConcesionForm(instance=concesion)
    
    context = {
        'form': form,
        'concesion': concesion,
        'TEMPLATE_TITLE': get_string('catalogos.concesion.edit', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.concesion.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/concesion_form.html', context)

@login_required
def concesion_delete(request, pk):
    """Eliminar concesión."""
    concesion = get_object_or_404(Concesion, pk=pk)
    
    if request.method == 'POST':
        concesion.delete()
        messages.success(request, get_string('success.catalog_deleted', 'ingesta'))
        return redirect('ingesta:concesion_list')
    
    context = {
        'concesion': concesion,
        'TEMPLATE_TITLE': get_string('catalogos.concesion.delete', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.concesion.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/concesion_confirm_delete.html', context)

# ============================================================================
# VISTAS PARA ASEs
# ============================================================================

@login_required
def ase_list(request):
    """Lista de ASEs con búsqueda y paginación."""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    ases = ASE.objects.all()
    
    if search_query:
        ases = ases.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    paginator = Paginator(ases, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'TEMPLATE_TITLE': get_string('catalogos.ase.title', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.ase.description', 'ingesta'),
        'TEMPLATE_ADD': get_string('catalogos.ase.add', 'ingesta'),
        'TEMPLATE_LIST': get_string('catalogos.ase.list', 'ingesta'),
        'TEMPLATE_NO_RECORDS': get_string('catalogos.ase.no_records', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/ase_list.html', context)

@login_required
def ase_create(request):
    """Crear nuevo ASE."""
    if request.method == 'POST':
        form = ASEForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_saved', 'ingesta'))
            return redirect('ingesta:ase_list')
    else:
        form = ASEForm()
    
    context = {
        'form': form,
        'TEMPLATE_TITLE': get_string('catalogos.ase.add', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.ase.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/ase_form.html', context)

@login_required
def ase_edit(request, pk):
    """Editar ASE existente."""
    ase = get_object_or_404(ASE, pk=pk)
    
    if request.method == 'POST':
        form = ASEForm(request.POST, instance=ase)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_updated', 'ingesta'))
            return redirect('ingesta:ase_list')
    else:
        form = ASEForm(instance=ase)
    
    context = {
        'form': form,
        'ase': ase,
        'TEMPLATE_TITLE': get_string('catalogos.ase.edit', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.ase.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/ase_form.html', context)

@login_required
def ase_delete(request, pk):
    """Eliminar ASE."""
    ase = get_object_or_404(ASE, pk=pk)
    
    if request.method == 'POST':
        ase.delete()
        messages.success(request, get_string('success.catalog_deleted', 'ingesta'))
        return redirect('ingesta:ase_list')
    
    context = {
        'ase': ase,
        'TEMPLATE_TITLE': get_string('catalogos.ase.delete', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.ase.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/ase_confirm_delete.html', context)

# ============================================================================
# VISTAS PARA SERVICIOS
# ============================================================================

@login_required
def servicio_list(request):
    """Lista de servicios con búsqueda y paginación."""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    servicios = Servicio.objects.all()
    
    if search_query:
        servicios = servicios.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    paginator = Paginator(servicios, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'TEMPLATE_TITLE': get_string('catalogos.servicio.title', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.servicio.description', 'ingesta'),
        'TEMPLATE_ADD': get_string('catalogos.servicio.add', 'ingesta'),
        'TEMPLATE_LIST': get_string('catalogos.servicio.list', 'ingesta'),
        'TEMPLATE_NO_RECORDS': get_string('catalogos.servicio.no_records', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/servicio_list.html', context)

@login_required
def servicio_create(request):
    """Crear nuevo servicio."""
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_saved', 'ingesta'))
            return redirect('ingesta:servicio_list')
    else:
        form = ServicioForm()
    
    context = {
        'form': form,
        'TEMPLATE_TITLE': get_string('catalogos.servicio.add', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.servicio.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/servicio_form.html', context)

@login_required
def servicio_edit(request, pk):
    """Editar servicio existente."""
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_updated', 'ingesta'))
            return redirect('ingesta:servicio_list')
    else:
        form = ServicioForm(instance=servicio)
    
    context = {
        'form': form,
        'servicio': servicio,
        'TEMPLATE_TITLE': get_string('catalogos.servicio.edit', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.servicio.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/servicio_form.html', context)

@login_required
def servicio_delete(request, pk):
    """Eliminar servicio."""
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, get_string('success.catalog_deleted', 'ingesta'))
        return redirect('ingesta:servicio_list')
    
    context = {
        'servicio': servicio,
        'TEMPLATE_TITLE': get_string('catalogos.servicio.delete', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.servicio.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/servicio_confirm_delete.html', context)

# ============================================================================
# VISTAS PARA ZONAS DE DESCARGA
# ============================================================================

@login_required
def zona_descarga_list(request):
    """Lista de zonas de descarga con búsqueda y paginación."""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    zonas = ZonaDescarga.objects.all()
    
    if search_query:
        zonas = zonas.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    paginator = Paginator(zonas, 10)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'TEMPLATE_TITLE': get_string('catalogos.zona_descarga.title', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.zona_descarga.description', 'ingesta'),
        'TEMPLATE_ADD': get_string('catalogos.zona_descarga.add', 'ingesta'),
        'TEMPLATE_LIST': get_string('catalogos.zona_descarga.list', 'ingesta'),
        'TEMPLATE_NO_RECORDS': get_string('catalogos.zona_descarga.no_records', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/zona_descarga_list.html', context)

@login_required
def zona_descarga_create(request):
    """Crear nueva zona de descarga."""
    if request.method == 'POST':
        form = ZonaDescargaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_saved', 'ingesta'))
            return redirect('ingesta:zona_descarga_list')
    else:
        form = ZonaDescargaForm()
    
    context = {
        'form': form,
        'TEMPLATE_TITLE': get_string('catalogos.zona_descarga.add', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.zona_descarga.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/zona_descarga_form.html', context)

@login_required
def zona_descarga_edit(request, pk):
    """Editar zona de descarga existente."""
    zona = get_object_or_404(ZonaDescarga, pk=pk)
    
    if request.method == 'POST':
        form = ZonaDescargaForm(request.POST, instance=zona)
        if form.is_valid():
            form.save()
            messages.success(request, get_string('success.catalog_updated', 'ingesta'))
            return redirect('ingesta:zona_descarga_list')
    else:
        form = ZonaDescargaForm(instance=zona)
    
    context = {
        'form': form,
        'zona': zona,
        'TEMPLATE_TITLE': get_string('catalogos.zona_descarga.edit', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.zona_descarga.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/zona_descarga_form.html', context)

@login_required
def zona_descarga_delete(request, pk):
    """Eliminar zona de descarga."""
    zona = get_object_or_404(ZonaDescarga, pk=pk)
    
    if request.method == 'POST':
        zona.delete()
        messages.success(request, get_string('success.catalog_deleted', 'ingesta'))
        return redirect('ingesta:zona_descarga_list')
    
    context = {
        'zona': zona,
        'TEMPLATE_TITLE': get_string('catalogos.zona_descarga.delete', 'ingesta'),
        'TEMPLATE_DESCRIPTION': get_string('catalogos.zona_descarga.description', 'ingesta'),
    }
    context.update(get_template_context())
    
    return render(request, 'ingesta/catalogos/zona_descarga_confirm_delete.html', context)
