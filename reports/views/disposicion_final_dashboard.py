from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Max, Min
from datetime import datetime, timedelta
from ingesta.models.disposicion.disposicion_final import DisposicionFinal
from ingesta.models.core.registro_carga import RegistroCarga
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string
from django.utils import formats
from django.db.models.functions import TruncMonth
from .main_dashboard import get_areas_misionales_context
import json

def get_bogota_concesiones():
    concesiones = [
        'Area Limpia DC',
        'Bogota Limpia SAS ESP',
        'CIUDAD LIMPIA S.A.',
        'LIME S.A E.S.P.',
        'PROMOAMBIENTAL DISTRITO SAS ESP',
    ]
    return concesiones

def disposicion_final_dashboard(request):
    """
    Dashboard de indicadores para Disposición Final.
    """
    bogota_concesiones = get_bogota_concesiones()
    end_date = datetime.now()
    start_date = datetime.now().replace(day=1, month=1, year=2025)
    disposiciones = DisposicionFinal.objects.filter(
        concesion__in=bogota_concesiones,
        fecha_entrada__range=[start_date, end_date]
    )
    total_residuos = disposiciones.filter(
        zona_descarga='Fase 2 Optimizacion'
    ).aggregate(
        total=Sum('peso_residuos')
    )['total'] or 0

    stats_by_concesion = disposiciones.values('concesion').annotate(
        total_residuos=Sum('peso_residuos')/1000,
        total_vehiculos=Count('placa', distinct=True),
        promedio_peso=Avg('peso_residuos')/1000
    )

    fecha_actual = disposiciones.aggregate(ultima=Max('fecha_entrada'))['ultima']
    fecha_actual_str = formats.date_format(fecha_actual, "DATE_FORMAT") if fecha_actual else "N/A"
    acumulado_texto = get_string('templates.acumulado_anio', 'reports').format(
        year=start_date.year,
        date=fecha_actual_str
    )
    mensual = disposiciones.annotate(
        mes=TruncMonth('fecha_entrada')
    ).values('mes').annotate(
        total=Sum('peso_residuos')/1000
    ).order_by('mes')

    # Calculate average tons per day.
    lastupdate = fecha_actual
    firstupdate = disposiciones.aggregate(first=Min('fecha_entrada'))['first']
    if lastupdate and firstupdate:
        promedio_kg_dia = total_residuos / ((lastupdate - firstupdate).days + 1)
    else:
        promedio_kg_dia = 0

    # Get data from the query
    labels = [m['mes'].strftime('%b %Y') for m in mensual if m['mes']]
    data = [float(m['total']) for m in mensual]

    # Always add January 1st as the first label with 0 ton
    labels = ["Ene 1"] + labels
    data = [0] + data

    poblacion_bogota = 7937898
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_residuos': total_residuos/1000,
        'stats_by_concesion': stats_by_concesion,
        'per_capita': total_residuos/poblacion_bogota,
        'promedio_toneladas_dia': promedio_kg_dia/1000,
        'TEMPLATE_TONELADAS_DIA': get_string('templates.promedio_toneladas_dia', 'reports'),
        'TEMPLATE_DASHBOARD_TITLE': get_string('templates.disposicion_final', 'reports'),
        'TEMPLATE_DASHBOARD_DESCRIPTION': get_string('templates.disposicion_final_desc', 'reports'),
        'TEMPLATE_TOTAL_RESIDUOS': get_string('templates.total_residuos', 'reports'),
        'TEMPLATE_PER_CAPITA': get_string('templates.per_capita', 'reports'),
        'TEMPLATE_STATS_CONCESION': get_string('templates.stats_concesion', 'reports'),
        'TEMPLATE_CONCESION': get_string('templates.concesion', 'reports'),
        'TEMPLATE_TOTAL_RESIDUOS_KG': get_string('templates.total_residuos_ton', 'reports'),
        'TEMPLATE_ACUMULADO_ANIO': acumulado_texto,
        'TEMPLATE_EVOLUCION_MENSUAL': get_string('templates.evolucion_mensual', 'reports'),
        'grafico_mensual_labels': labels,
        'grafico_mensual_data': data,
        'grafico_mensual_labels_json': json.dumps(labels),
        'grafico_mensual_data_json': json.dumps(data),
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
    }
    context.update(get_areas_misionales_context())
    context.update(get_template_context())
    return render(request, 'reports/disposicion_final_dashboard.html', context) 