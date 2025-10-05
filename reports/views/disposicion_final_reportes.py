from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from globalfunctions.string_manager import get_string
from coreview.base import get_template_context
from .main_dashboard import get_areas_misionales_context
import pandas as pd

@login_required
def disposicion_final_reportes(request):
    """
    Simple report builder using the disposicion_final_detallada view.
    Clean, intuitive interface for filtering data with date ranges and multi-select.
    """
    
    # Get current year for default date range
    current_year = datetime.now().year
    
    # Get filter parameters
    start_year = request.GET.get('start_year', str(current_year))
    end_year = request.GET.get('end_year', str(current_year))
    start_month = request.GET.get('start_month', '1')
    end_month = request.GET.get('end_month', '12')
    
    # Multi-select filters
    concesiones = request.GET.getlist('concesiones')
    servicios = request.GET.getlist('servicios')
    zonas = request.GET.getlist('zonas')
    categorias = request.GET.getlist('categorias')
    origenes = request.GET.getlist('origenes')
    dispuestos_pidj = request.GET.getlist('dispuestos_pidj')
    
    # Get available filter options
    with connection.cursor() as cursor:
        # Get available years
        cursor.execute("SELECT DISTINCT \"AÑO\" FROM disposicion_final_detallada ORDER BY \"AÑO\" DESC")
        years = [row[0] for row in cursor.fetchall()]
        
        # Get available months
        months = [
            {'value': '1', 'name': 'Enero'},
            {'value': '2', 'name': 'Febrero'},
            {'value': '3', 'name': 'Marzo'},
            {'value': '4', 'name': 'Abril'},
            {'value': '5', 'name': 'Mayo'},
            {'value': '6', 'name': 'Junio'},
            {'value': '7', 'name': 'Julio'},
            {'value': '8', 'name': 'Agosto'},
            {'value': '9', 'name': 'Septiembre'},
            {'value': '10', 'name': 'Octubre'},
            {'value': '11', 'name': 'Noviembre'},
            {'value': '12', 'name': 'Diciembre'},
        ]
        
        # Get available concesiones
        cursor.execute("SELECT DISTINCT \"nombre\" FROM ingesta_concesion")
        concesiones_options = [row[0] for row in cursor.fetchall()]
        
        # Get available servicios
        cursor.execute("SELECT DISTINCT \"nombre\" FROM ingesta_servicio")
        servicios_options = [row[0] for row in cursor.fetchall()]
        
        # Get available zonas
        cursor.execute("SELECT DISTINCT \"nombre\" FROM ingesta_zonadescarga")
        zonas_options = [row[0] for row in cursor.fetchall()]
        
        # Get available categorias
        cursor.execute("SELECT DISTINCT \"categoria\" FROM ingesta_servicio")
        categorias_options = [row[0] for row in cursor.fetchall()]
        
        # Get available origenes
        cursor.execute("SELECT DISTINCT \"ORIGEN DEL RESIDUO\" FROM disposicion_final_detallada WHERE \"ORIGEN DEL RESIDUO\" IS NOT NULL ORDER BY \"ORIGEN DEL RESIDUO\"")
        origenes_options = [row[0] for row in cursor.fetchall()]
    
    # Build query with filters
    query = "SELECT * FROM disposicion_final_detallada WHERE 1=1"
    params = []
    
    # Date range filters
    query += " AND \"AÑO\" >= %s AND \"AÑO\" <= %s"
    params.extend([start_year, end_year])
    
    query += " AND \"MES\" >= %s AND \"MES\" <= %s"
    params.extend([start_month, end_month])
    
    # Multi-select filters - only apply if selections are made
    if concesiones and len(concesiones) > 0:
        placeholders = ','.join(['%s'] * len(concesiones))
        query += f" AND \"CONCESION\" IN ({placeholders})"
        params.extend(concesiones)
    
    if servicios and len(servicios) > 0:
        placeholders = ','.join(['%s'] * len(servicios))
        query += f" AND \"SERVICIO\" IN ({placeholders})"
        params.extend(servicios)
    
    if zonas and len(zonas) > 0:
        placeholders = ','.join(['%s'] * len(zonas))
        query += f" AND \"ZONA DESCARGA\" IN ({placeholders})"
        params.extend(zonas)
    
    if categorias and len(categorias) > 0:
        placeholders = ','.join(['%s'] * len(categorias))
        query += f" AND \"CATEGORIA DEL SERVICIO\" IN ({placeholders})"
        params.extend(categorias)
    
    if origenes and len(origenes) > 0:
        placeholders = ','.join(['%s'] * len(origenes))
        query += f" AND \"ORIGEN DEL RESIDUO\" IN ({placeholders})"
        params.extend(origenes)
    
    if dispuestos_pidj and len(dispuestos_pidj) > 0:
        # Handle PIDJ filtering - it's either 'PIDJ' or NULL
        pidj_conditions = []
        for value in dispuestos_pidj:
            if value == 'PIDJ':
                pidj_conditions.append("\"DISPUESTOS PIDJ\" = 'PIDJ'")
            elif value == 'No Aplica':
                pidj_conditions.append("\"DISPUESTOS PIDJ\" <> 'PIDJ'")
        
        if pidj_conditions:
            query += " AND (" + " OR ".join(pidj_conditions) + ")"
    
    query += " ORDER BY \"FECHA ENTRADA\" DESC"
    
    # Execute query and get results
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
    
    # Paginate results
    paginator = Paginator(results, 50)  # 50 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    total_records = len(results)
    total_weight = sum(row[3] for row in results)  # PESO RESIDUOS TON is column 3
    
    context = {
        'page_obj': page_obj,
        'columns': columns,
        'total_records': total_records,
        'total_weight': round(total_weight, 2),
        
        # Filter options
        'years': years,
        'months': months,
        'concesiones_options': concesiones_options,
        'servicios_options': servicios_options,
        'zonas_options': zonas_options,
        'categorias_options': categorias_options,
        'origenes_options': origenes_options,
        
        # Current filters
        'current_start_year': start_year,
        'current_end_year': end_year,
        'current_start_month': start_month,
        'current_end_month': end_month,
        'current_concesiones': json.dumps(concesiones),
        'current_servicios': json.dumps(servicios),
        'current_zonas': json.dumps(zonas),
        'current_categorias': json.dumps(categorias),
        'current_origenes': json.dumps(origenes),
        'current_pidj': json.dumps(dispuestos_pidj),
        
        'TEMPLATE_DASHBOARD_TITLE': 'Constructor de Reportes - Disposición Final',
        'TEMPLATE_DASHBOARD_DESCRIPTION': 'Filtra y explora los datos de disposición final de residuos',
    }
    
    context.update(get_areas_misionales_context())
    context.update(get_template_context())
    
    return render(request, 'reports/disposicion_final_reportes.html', context)

@login_required
def export_report_csv(request):
    """
    Export filtered report data to CSV
    """
    # Get the same filters as the main view
    start_year = request.GET.get('start_year', str(datetime.now().year))
    end_year = request.GET.get('end_year', str(datetime.now().year))
    start_month = request.GET.get('start_month', '1')
    end_month = request.GET.get('end_month', '12')
    
    concesiones = request.GET.getlist('concesiones')
    servicios = request.GET.getlist('servicios')
    zonas = request.GET.getlist('zonas')
    categorias = request.GET.getlist('categorias')
    origenes = request.GET.getlist('origenes')
    dispuestos_pidj = request.GET.getlist('dispuestos_pidj')
    
    # Build the same query
    query = "SELECT * FROM disposicion_final_detallada WHERE 1=1"
    params = []
    
    # Date range filters
    query += " AND \"AÑO\" >= %s AND \"AÑO\" <= %s"
    params.extend([start_year, end_year])
    
    query += " AND \"MES\" >= %s AND \"MES\" <= %s"
    params.extend([start_month, end_month])
    
    # Multi-select filters - only apply if selections are made
    if concesiones and len(concesiones) > 0:
        placeholders = ','.join(['%s'] * len(concesiones))
        query += f" AND \"CONCESION\" IN ({placeholders})"
        params.extend(concesiones)
    
    if servicios and len(servicios) > 0:
        placeholders = ','.join(['%s'] * len(servicios))
        query += f" AND \"SERVICIO\" IN ({placeholders})"
        params.extend(servicios)
    
    if zonas and len(zonas) > 0:
        placeholders = ','.join(['%s'] * len(zonas))
        query += f" AND \"ZONA DESCARGA\" IN ({placeholders})"
        params.extend(zonas)
    
    if categorias and len(categorias) > 0:
        placeholders = ','.join(['%s'] * len(categorias))
        query += f" AND \"CATEGORIA DEL SERVICIO\" IN ({placeholders})"
        params.extend(categorias)
    
    if origenes and len(origenes) > 0:
        placeholders = ','.join(['%s'] * len(origenes))
        query += f" AND \"ORIGEN DEL RESIDUO\" IN ({placeholders})"
        params.extend(origenes)
    
    if dispuestos_pidj and len(dispuestos_pidj) > 0:
        # Handle PIDJ filtering - it's either 'PIDJ' or NULL
        pidj_conditions = []
        for value in dispuestos_pidj:
            if value == 'PIDJ':
                pidj_conditions.append("\"DISPUESTOS PIDJ\" = 'PIDJ'")
            elif value == 'NON_PIDJ':
                pidj_conditions.append("\"DISPUESTOS PIDJ\" IS NULL")
        
        if pidj_conditions:
            query += " AND (" + " OR ".join(pidj_conditions) + ")"
    
    query += " ORDER BY \"FECHA ENTRADA\" DESC"
    
    # Execute query
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
    
    # Create DataFrame
    df = pd.DataFrame(results, columns=columns)
    
    # Create Excel file in memory
    excel_buffer = BytesIO()
    
    # Write to Excel with formatting
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reporte Disposición Final', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Reporte Disposición Final']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Style the header row
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
    
    # Prepare response
    excel_buffer.seek(0)
    response = HttpResponse(
        excel_buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_disposicion_final.xlsx"'
    
    return response
