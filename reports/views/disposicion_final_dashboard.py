from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Max, Min
from datetime import datetime, timedelta
from ingesta.models.disposicion.disposicion_final import DisposicionFinal
from ingesta.models.disposicion.disposicion_final_mensual import DisposicionFinalMensual
from ingesta.models.core.registro_carga import RegistroCarga
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string
from django.utils import formats
from django.db.models.functions import TruncMonth
from .main_dashboard import get_areas_misionales_context
import json
from django.contrib.humanize.templatetags.humanize import intcomma

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
    # Get date range from request or default to current year
    year = int(request.GET.get('year', datetime.now().year))
    end_date = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    # Get date range from main table - single efficient query
    date_range = DisposicionFinal.objects.filter(
        fecha_entrada__year=year
    ).aggregate(
        first_date=Min('fecha_entrada'),
        last_date=Max('fecha_entrada')
    )
    first_date = date_range['first_date']
    last_date = date_range['last_date']

    # Get all aggregated data from monthly table in a single query
    mensual_data = DisposicionFinalMensual.objects.filter(
        year=year,
        zona_descarga='Fase 2 Optimizacion',
        concesion__in=get_bogota_concesiones()
    )

    # Calculate total residues and stats by concesion from monthly data
    total_residuos = mensual_data.aggregate(
        total=Sum('peso_residuos')
    )['total'] or 0

    stats_by_concesion = mensual_data.values('concesion').annotate(
        total_residuos=Sum('peso_residuos')/1000,
        promedio_peso=Avg('peso_residuos')/1000
    ).order_by('total_residuos').reverse()

    # Format stats with thousand separators
    for stat in stats_by_concesion:
        stat['total_residuos'] = intcomma(round(stat['total_residuos'], 2))
        stat['promedio_peso'] = intcomma(round(stat['promedio_peso'], 2))

    # Format dates for display
    fecha_actual_str = formats.date_format(last_date, "DATE_FORMAT") if last_date else "N/A"

    acumulado_texto = get_string('templates.acumulado_anio', 'reports').format(
        year=year,
        date=fecha_actual_str
    )

    # Get monthly totals
    mensual = mensual_data.values('month').annotate(
        total=Sum('peso_residuos')/1000
    ).order_by('month')

    # Calculate average tons per day using the date range
    if last_date and first_date:
        promedio_kg_dia = total_residuos / ((last_date - first_date).days + 1)
    else:
        promedio_kg_dia = 0

    # Format data for chart
    labels = [f"{datetime(year, m['month'], 1).strftime('%b %Y')}" for m in mensual]
    data = [float(m['total']) for m in mensual]

    # Always add January 1st as the first label with 0 ton
    labels = ["Ene 1"] + labels
    data = [0] + data

    poblacion_bogota = 7937898
    context = {
        'start_date': year,
        'end_date': end_date,
        'total_residuos': intcomma(round(total_residuos/1000, 2)),
        'stats_by_concesion': stats_by_concesion,
        'acumulado_texto': acumulado_texto,
        'promedio_toneladas_dia': intcomma(round(promedio_kg_dia/1000, 2)),
        'per_capita': intcomma(round(total_residuos/poblacion_bogota, 2)),
        'labels': labels,
        'data': data,
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