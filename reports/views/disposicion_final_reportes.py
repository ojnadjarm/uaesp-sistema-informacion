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
        cursor.execute("SELECT DISTINCT \"nombre\" FROM ingesta_concesion ORDER BY \"nombre\"")
        concesiones_options = [row[0] for row in cursor.fetchall()]
        
        # Get available servicios
        cursor.execute("SELECT DISTINCT \"nombre\" FROM ingesta_servicio ORDER BY \"nombre\"")
        servicios_options = [row[0] for row in cursor.fetchall()]
        
        # Get available zonas
        cursor.execute("SELECT DISTINCT \"nombre\" FROM ingesta_zonadescarga ORDER BY \"nombre\"")
        zonas_options = [row[0] for row in cursor.fetchall()]
        
        # Get available categorias
        cursor.execute("SELECT DISTINCT \"categoria\" FROM ingesta_servicio WHERE \"categoria\" IS NOT NULL ORDER BY \"categoria\"")
        categorias_options = [row[0] for row in cursor.fetchall()]
        
        # Get available origenes
        cursor.execute("SELECT DISTINCT \"categoria\" FROM ingesta_concesion WHERE \"categoria\" IS NOT NULL ORDER BY \"categoria\"")
        origenes_options = [row[0] for row in cursor.fetchall()]
    
    # Build direct query to base tables (much faster than using the view)
    query = """
    SELECT
        EXTRACT(YEAR FROM df.fecha_entrada) AS "AÑO",
        EXTRACT(MONTH FROM df.fecha_entrada) AS "MES",
        EXTRACT(DAY FROM df.fecha_entrada) AS "DÍA",
        ROUND(df.peso_residuos / 1000.0, 2) AS "PESO RESIDUOS TON",
        df.fecha_entrada AS "FECHA ENTRADA",
        df.fecha_salida AS "FECHA SALIDA",
        df.consecutivo_entrada AS "CONSECUTIVO ENTRADA",
        df.consecutivo_salida AS "CONSECUTIVO SALIDA",
        df.placa AS "PLACA",
        df.numero_vehiculo AS "NUMERO VEHICULO",
        UPPER(TRIM(df.concesion)) AS "CONCESION",
        df.macroruta AS "MACRORUTA",
        df.microruta AS "MICRORUTA",
        UPPER(TRIM(df.ase)) AS "ASE",
        UPPER(TRIM(df.servicio)) AS "SERVICIO",
        UPPER(TRIM(df.zona_descarga)) AS "ZONA DESCARGA",
        df.peso_entrada AS "PESO ENTRADA",
        df.peso_salida AS "PESO SALIDA",
        df.peso_residuos AS "PESO RESIDUOS",
        s.categoria AS "CATEGORIA DEL SERVICIO",
        c.categoria AS "ORIGEN DEL RESIDUO",
        CASE
            WHEN zd.categoria = 'PIDJ' THEN 'PIDJ'
            ELSE NULL
        END AS "DISPUESTOS PIDJ"
    FROM
        ingesta_disposicionfinal df
    LEFT JOIN
        ingesta_concesion c ON UPPER(TRIM(df.concesion)) = UPPER(TRIM(c.nombre))
    LEFT JOIN
        ingesta_servicio s ON UPPER(TRIM(df.servicio)) = UPPER(TRIM(s.nombre))
    LEFT JOIN
        ingesta_zonadescarga zd ON UPPER(TRIM(df.zona_descarga)) = UPPER(TRIM(zd.nombre))
    LEFT JOIN
        ingesta_ase a ON UPPER(TRIM(df.ase)) = UPPER(TRIM(a.nombre))
    WHERE
        df.fecha_entrada IS NOT NULL
    """
    params = []
    
    # Date range filters - use direct date comparison instead of extracted year/month
    query += " AND df.fecha_entrada >= %s AND df.fecha_entrada <= %s"
    params.extend([f"{start_year}-{start_month.zfill(2)}-01", f"{end_year}-{end_month.zfill(2)}-31"])
    
    # Multi-select filters - only apply if selections are made
    if concesiones and len(concesiones) > 0:
        placeholders = ','.join(['%s'] * len(concesiones))
        query += f" AND UPPER(TRIM(df.concesion)) IN ({placeholders})"
        params.extend([concesion.upper().strip() for concesion in concesiones])
    
    if servicios and len(servicios) > 0:
        placeholders = ','.join(['%s'] * len(servicios))
        query += f" AND UPPER(TRIM(df.servicio)) IN ({placeholders})"
        params.extend([servicio.upper().strip() for servicio in servicios])
    
    if zonas and len(zonas) > 0:
        placeholders = ','.join(['%s'] * len(zonas))
        query += f" AND UPPER(TRIM(df.zona_descarga)) IN ({placeholders})"
        params.extend([zona.upper().strip() for zona in zonas])
    
    if categorias and len(categorias) > 0:
        placeholders = ','.join(['%s'] * len(categorias))
        query += f" AND s.categoria IN ({placeholders})"
        params.extend(categorias)
    
    if origenes and len(origenes) > 0:
        placeholders = ','.join(['%s'] * len(origenes))
        query += f" AND c.categoria IN ({placeholders})"
        params.extend(origenes)
    
    if dispuestos_pidj and len(dispuestos_pidj) > 0:
        # Handle PIDJ filtering - it's either 'PIDJ' or NULL
        pidj_conditions = []
        for value in dispuestos_pidj:
            if value == 'PIDJ':
                pidj_conditions.append("zd.categoria = 'PIDJ'")
            elif value == 'No Aplica':
                pidj_conditions.append("(zd.categoria IS NULL OR zd.categoria <> 'PIDJ')")
        
        if pidj_conditions:
            query += " AND (" + " OR ".join(pidj_conditions) + ")"
    
    query += " ORDER BY df.fecha_entrada DESC"
    
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
    
    # Build the same direct query as the main view
    query = """
    SELECT
        EXTRACT(YEAR FROM df.fecha_entrada) AS "AÑO",
        EXTRACT(MONTH FROM df.fecha_entrada) AS "MES",
        EXTRACT(DAY FROM df.fecha_entrada) AS "DÍA",
        ROUND(df.peso_residuos / 1000.0, 2) AS "PESO RESIDUOS TON",
        df.fecha_entrada AS "FECHA ENTRADA",
        df.fecha_salida AS "FECHA SALIDA",
        df.consecutivo_entrada AS "CONSECUTIVO ENTRADA",
        df.consecutivo_salida AS "CONSECUTIVO SALIDA",
        df.placa AS "PLACA",
        df.numero_vehiculo AS "NUMERO VEHICULO",
        UPPER(TRIM(df.concesion)) AS "CONCESION",
        df.macroruta AS "MACRORUTA",
        df.microruta AS "MICRORUTA",
        UPPER(TRIM(df.ase)) AS "ASE",
        UPPER(TRIM(df.servicio)) AS "SERVICIO",
        UPPER(TRIM(df.zona_descarga)) AS "ZONA DESCARGA",
        df.peso_entrada AS "PESO ENTRADA",
        df.peso_salida AS "PESO SALIDA",
        df.peso_residuos AS "PESO RESIDUOS",
        s.categoria AS "CATEGORIA DEL SERVICIO",
        c.categoria AS "ORIGEN DEL RESIDUO",
        CASE
            WHEN zd.categoria = 'PIDJ' THEN 'PIDJ'
            ELSE NULL
        END AS "DISPUESTOS PIDJ"
    FROM
        ingesta_disposicionfinal df
    LEFT JOIN
        ingesta_concesion c ON UPPER(TRIM(df.concesion)) = UPPER(TRIM(c.nombre))
    LEFT JOIN
        ingesta_servicio s ON UPPER(TRIM(df.servicio)) = UPPER(TRIM(s.nombre))
    LEFT JOIN
        ingesta_zonadescarga zd ON UPPER(TRIM(df.zona_descarga)) = UPPER(TRIM(zd.nombre))
    LEFT JOIN
        ingesta_ase a ON UPPER(TRIM(df.ase)) = UPPER(TRIM(a.nombre))
    WHERE
        df.fecha_entrada IS NOT NULL
    """
    params = []
    
    # Date range filters - use direct date comparison instead of extracted year/month
    query += " AND df.fecha_entrada >= %s AND df.fecha_entrada <= %s"
    params.extend([f"{start_year}-{start_month.zfill(2)}-01", f"{end_year}-{end_month.zfill(2)}-31"])
    
    # Multi-select filters - only apply if selections are made
    if concesiones and len(concesiones) > 0:
        placeholders = ','.join(['%s'] * len(concesiones))
        query += f" AND UPPER(TRIM(df.concesion)) IN ({placeholders})"
        params.extend([concesion.upper().strip() for concesion in concesiones])
    
    if servicios and len(servicios) > 0:
        placeholders = ','.join(['%s'] * len(servicios))
        query += f" AND UPPER(TRIM(df.servicio)) IN ({placeholders})"
        params.extend([servicio.upper().strip() for servicio in servicios])
    
    if zonas and len(zonas) > 0:
        placeholders = ','.join(['%s'] * len(zonas))
        query += f" AND UPPER(TRIM(df.zona_descarga)) IN ({placeholders})"
        params.extend([zona.upper().strip() for zona in zonas])
    
    if categorias and len(categorias) > 0:
        placeholders = ','.join(['%s'] * len(categorias))
        query += f" AND s.categoria IN ({placeholders})"
        params.extend(categorias)
    
    if origenes and len(origenes) > 0:
        placeholders = ','.join(['%s'] * len(origenes))
        query += f" AND c.categoria IN ({placeholders})"
        params.extend(origenes)
    
    if dispuestos_pidj and len(dispuestos_pidj) > 0:
        # Handle PIDJ filtering - it's either 'PIDJ' or NULL
        pidj_conditions = []
        for value in dispuestos_pidj:
            if value == 'PIDJ':
                pidj_conditions.append("zd.categoria = 'PIDJ'")
            elif value == 'No Aplica':
                pidj_conditions.append("(zd.categoria IS NULL OR zd.categoria <> 'PIDJ')")
        
        if pidj_conditions:
            query += " AND (" + " OR ".join(pidj_conditions) + ")"
    
    query += " ORDER BY df.fecha_entrada DESC"
    
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
