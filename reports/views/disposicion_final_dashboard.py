from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Max, Min
from datetime import datetime, timedelta
from ingesta.models.disposicion.disposicion_final import DisposicionFinal
from ingesta.models.disposicion.disposicion_final_mensual import DisposicionFinalMensual
from ingesta.models.core.registro_carga import RegistroCarga
from coreview.base import get_template_context
from globalfunctions.string_manager import get_string
from .main_dashboard import get_areas_misionales_context
import json
from django.contrib.humanize.templatetags.humanize import intcomma

MONTH_ABBREVIATIONS = {
    1: 'Ene',
    2: 'Feb',
    3: 'Mar',
    4: 'Abr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Ago',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dic',
}

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
    ).order_by('total_residuos').reverse()

    concesion_count = stats_by_concesion.count()

    # Format stats with thousand separators
    for stat in stats_by_concesion:
        stat['total_residuos'] = intcomma(round(stat['total_residuos'], 2))

    # Format dates for display
    fecha_actual_str = last_date.strftime('%d/%m/%Y') if last_date else get_string('templates.not_available', 'reports')

    acumulado_texto = get_string('templates.acumulado_anio', 'reports').format(
        year=year,
        date=fecha_actual_str
    )

    # Get monthly totals by concession for chart
    mensual_by_concesion = mensual_data.values('month', 'concesion').annotate(
        total=Sum('peso_residuos')/1000
    ).order_by('month')

    # Get monthly totals (for total line)
    mensual_total = mensual_data.values('month').annotate(
        total=Sum('peso_residuos')/1000
    ).order_by('month')

    # Get all months and concessions
    months = sorted(mensual_data.values_list('month', flat=True).distinct())
    concesiones = get_bogota_concesiones()
    
    # Create chart data structure - add "Ene 1" at the beginning
    labels = ["Ene 1"] + [MONTH_ABBREVIATIONS.get(month, str(month)) for month in months]
    
    # Create datasets for each concession
    chart_datasets = []
    colors = [
        'rgba(54, 162, 235, 1)',    # Blue
        'rgba(255, 99, 132, 1)',    # Red
        'rgba(75, 192, 192, 1)',    # Green
        'rgba(255, 206, 86, 1)',    # Yellow
        'rgba(153, 102, 255, 1)'    # Purple
    ]
    
    # Add individual ASES lines
    for i, concesion in enumerate(concesiones):
        concesion_data = [0] * (len(months) + 1)  # Initialize with zeros (including Ene 1)
        
        # Fill in actual data for this concession (starting from index 1)
        for data_point in mensual_by_concesion:
            if data_point['concesion'] == concesion:
                month_index = months.index(data_point['month']) + 1  # +1 because we added "Ene 1" at index 0
                concesion_data[month_index] = float(data_point['total'])
        
        chart_datasets.append({
            'label': concesion,
            'data': concesion_data,
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)].replace('1)', '0.2)'),
            'fill': False,
            'tension': 0.3,
            'borderWidth': 2
        })
    
    # Add total line (thicker, black)
    total_data = [0] * (len(months) + 1)  # Initialize with zeros (including Ene 1)
    for data_point in mensual_total:
        month_index = months.index(data_point['month']) + 1  # +1 because we added "Ene 1" at index 0
        total_data[month_index] = float(data_point['total'])
    
    chart_datasets.append({
        'label': get_string('templates.chart_total_ases', 'reports'),
        'data': total_data,
        'borderColor': 'rgba(0, 0, 0, 1)',
        'backgroundColor': 'rgba(0, 0, 0, 0.1)',
        'fill': False,
        'tension': 0.3,
        'borderWidth': 4
    })

    # Calculate average tons per day using the date range
    if last_date and first_date:
        promedio_kg_dia = total_residuos / ((last_date - first_date).days + 1)
    else:
        promedio_kg_dia = 0

    poblacion_bogota = 7937898
    context = {
        'start_date': year,
        'end_date': end_date,
        'total_residuos': intcomma(round(total_residuos/1000, 2)),
        'stats_by_concesion': stats_by_concesion,
        'TEMPLATE_DISPOSICION_BREAKDOWN_SUBTITLE': get_string('templates.disposicion_final_breakdown_subtitle', 'reports'),
        'TEMPLATE_DISPOSICION_CONCESION_COUNT': get_string('templates.disposicion_final_concesion_count', 'reports').format(count=concesion_count),
        'acumulado_texto': acumulado_texto,
        'promedio_toneladas_dia': intcomma(round(promedio_kg_dia/1000, 2)),
        'per_capita': intcomma(round(total_residuos/poblacion_bogota, 2)),
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
        'grafico_mensual_datasets': chart_datasets,
        'grafico_mensual_labels_json': json.dumps(labels),
        'grafico_mensual_datasets_json': json.dumps(chart_datasets),
        # Debug info
        'debug_labels': labels,
        'debug_datasets': chart_datasets,
        'HIDE_HEADER_FOOTER': not request.user.is_authenticated,
        'TEMPLATE_REPORT_BUILDER_BUTTON': get_string('templates.dashboard_report_builder_button', 'reports'),
        'TEMPLATE_UNIT_TON': get_string('templates.unit_ton', 'reports'),
        'TEMPLATE_UNIT_KG_PER_CAPITA': get_string('templates.unit_kg_per_capita', 'reports'),
        'TEMPLATE_UNIT_TON_PER_DAY': get_string('templates.unit_ton_per_day', 'reports'),
        'TEMPLATE_NOT_AVAILABLE': get_string('templates.not_available', 'reports'),
    }
    context.update(get_areas_misionales_context())
    context.update(get_template_context())
    return render(request, 'reports/disposicion_final_dashboard.html', context) 