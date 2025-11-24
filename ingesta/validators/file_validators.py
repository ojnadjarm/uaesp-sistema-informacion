import io
import pandas as pd
from io import StringIO
from ..forms.upload import PROCESO_DATA
from globalfunctions.string_manager import get_string
from django.db.models import Q
from ingesta.models import DisposicionFinal
from django.apps import apps
from datetime import datetime
from ingesta.validators.catalog_validators import CatalogValidator

def transform_value(value, transform_config):
    """
    Transforma un valor según la configuración para coincidir con el formato de la base de datos.
    """
    if not transform_config:
        return value

    function_name = transform_config.get('function')
    args = transform_config.get('args', {})

    if function_name == 'transform_date':
        try:
            if isinstance(value, str):
                # Intentar analizar la cadena de fecha
                try:
                    # Primero intentar analizar como datetime
                    dt = pd.to_datetime(value)
                    return dt.strftime('%Y-%m-%d')
                except:
                    # Si falla, intentar formatos comunes
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                        try:
                            return datetime.strptime(value, fmt).strftime('%Y-%m-%d')
                        except ValueError:
                            continue
            elif isinstance(value, datetime):
                return value.strftime('%Y-%m-%d')
            return value
        except Exception:
            return value
    elif function_name == 'transform_integer':
        try:
            if isinstance(value, str):
                # Eliminar cualquier carácter no numérico excepto el punto decimal
                cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
                return int(float(cleaned))
            return int(value)
        except (ValueError, TypeError):
            return value
    elif function_name == 'split_text':
        try:
            character = args.get('character', ' ')
            position = args.get('position', 0)
            return value.split(character)[position]
        except (ValueError, TypeError):
            return value
    return value

def validar_registros_existentes(df, proceso_config):
    """
    Valida si algún registro ya existe en la base de datos verificando solo un registro.
    Dado que los archivos provienen de interventoría y cubren meses completos, verificar un registro es suficiente.
    Retorna una tupla (bool, str): (es_valido, mensaje_error)
    """
    # Obtener nombre de tabla de la configuración
    table_name = proceso_config.get('table_name')
    if not table_name:
        return True, None

    # Obtener clase del modelo desde el nombre de la tabla
    try:
        model = apps.get_model('ingesta', table_name)
    except LookupError:
        return True, None

    # Obtener campos de validación de la configuración
    validation_fields = proceso_config.get('validation', [])
    if not validation_fields:
        return True, None

    # Transformar valores según la configuración solo para la primera fila
    if df.empty:
        return True, None
    
    first_row = df.iloc[0]
    transformed_row = {}
    
    for field_config in validation_fields:
        field_name = field_config['field']
        field_type = field_config.get('type')
        transform_config = field_config.get('transform')
        
        if field_name in first_row and pd.notna(first_row[field_name]):
            value = first_row[field_name]
            
            # Aplicar transformación basada en el tipo de campo si no se proporciona una transformación específica
            if not transform_config and field_type:
                if field_type == 'date':
                    transform_config = {'function': 'transform_date'}
                elif field_type == 'integer':
                    transform_config = {'function': 'transform_integer'}
            
            if transform_config:
                value = transform_value(value, transform_config)
            
            transformed_row[field_name] = value

    # Verificar si esta combinación de campos ya existe en la base de datos
    query = Q()
    for field_config in validation_fields:
        field_name = field_config['field']
        db_field = field_config.get('db_field', field_name.lower().replace(' ', '_'))
        
        if field_name in transformed_row:
            query &= Q(**{db_field: transformed_row[field_name]})

    # Si tenemos una consulta válida y existen registros, retornar False
    if query and model.objects.filter(query).exists():
        return False, get_string('errors.file_has_existing_records', 'ingesta')

    return True, None

def get_catalog_error_message(field, value, error_string_key):
    """
    Genera el mensaje de error apropiado para cada tipo de catálogo.
    """
    if 'concesion' in error_string_key:
        return get_string(error_string_key, 'ingesta').format(concesion=value)
    elif 'ase' in error_string_key:
        return get_string(error_string_key, 'ingesta').format(ase=value)
    elif 'zona' in error_string_key:
        return get_string(error_string_key, 'ingesta').format(zona=value)
    else:
        # Fallback para otros tipos
        return get_string(error_string_key, 'ingesta').format(value=value)

def validar_catalogos_y_generar_log(df, proceso_config):
    """
    Valida los catálogos en el archivo y genera un DataFrame con los errores encontrados.
    Retorna una tupla (mensaje_error, dataframe_error).
    """
    from ingesta.models import Concesion, ASE, ZonaDescarga
    
    # Verificar si la validación de catálogos está habilitada para este proceso
    catalog_config = proceso_config.get('catalog_validation', {})
    if not catalog_config.get('enabled', False):
        return None, None
    
    # Obtener configuración específica del proceso
    required_fields = catalog_config.get('required_fields', [])
    optional_fields = catalog_config.get('optional_fields', [])
    field_mapping = catalog_config.get('field_mapping', {})
    
    # Mapeo de nombres de columnas a modelos y strings de error
    catalog_mapping = {}
    error_string_mapping = {}
    for column_name, model_name in field_mapping.items():
        if model_name == 'Concesion':
            catalog_mapping[column_name] = Concesion
            error_string_mapping[column_name] = 'errors.invalid_concesion'
        elif model_name == 'ASE':
            catalog_mapping[column_name] = ASE
            error_string_mapping[column_name] = 'errors.invalid_ase'
        elif model_name == 'ZonaDescarga':
            catalog_mapping[column_name] = ZonaDescarga
            error_string_mapping[column_name] = 'errors.invalid_zona_descarga'
    
    # Validar que la configuración sea correcta
    if not catalog_mapping:
        print(get_string('messages.catalog_mapping_warning', 'ingesta'))
        return None, None
    
    error_rows = []
    total_errors = 0
    
    # Obtener la configuración del archivo para calcular el número de fila correcto
    file_start_row = proceso_config.get('file_start_row', 1)
    
    for index, row in df.iterrows():
        row_errors = []
        # Calcular el número de fila real en el archivo original
        # file_start_row es la fila donde empiezan los datos (1-based)
        # index es el índice del DataFrame (0-based)
        # Sumamos 1 para convertir a 1-based
        row_number = file_start_row + index + 1
        
        # Validar campos requeridos
        for field in required_fields:
            if field in df.columns:
                value = str(row[field]).strip() if pd.notna(row[field]) else ''
                
                if not value:
                    row_errors.append(f"{field.title()}: {get_string('errors.required_field_empty', 'ingesta')}")
                    total_errors += 1
                else:
                    # Verificar si existe en el catálogo
                    model = catalog_mapping[field]
                    exists = model.objects.filter(
                        nombre__iexact=value,
                        activo=True
                    ).exists()
                    if not exists:
                        # Usar el string correspondiente del archivo JSON
                        error_string_key = error_string_mapping[field]
                        error_message = get_catalog_error_message(field, value, error_string_key)
                        row_errors.append(error_message)
                        total_errors += 1

        # Validar campos opcionales
        for field in optional_fields:
            if field in df.columns:
                value = str(row[field]).strip() if pd.notna(row[field]) else ''
                
                if value:  # Solo validar si no está vacío
                    model = catalog_mapping[field]
                    exists = model.objects.filter(
                        nombre__iexact=value,
                        activo=True
                    ).exists()
                    
                    if not exists:
                        # Usar el string correspondiente del archivo JSON
                        error_string_key = error_string_mapping[field]
                        error_message = get_catalog_error_message(field, value, error_string_key)
                        row_errors.append(error_message)
                        total_errors += 1

        # Si hay errores en esta fila, agregarla al reporte
        if row_errors:
            error_row = {
                'Fila': row_number,
                'Cantidad de Errores': len(row_errors),
                'Descripción de Errores': '; '.join(row_errors)
            }
            error_rows.append(error_row)
    # Crear DataFrame de errores
    error_df = pd.DataFrame(error_rows) if error_rows else pd.DataFrame()
    
    # Generar mensaje de error
    if total_errors > 0:
        error_message = get_string('errors.catalog_validation_errors_found', 'ingesta').format(
            error_count=total_errors,
            row_count=len(error_rows)
        )
        return error_message, error_df
    
    return None, None

def validar_estructura_csv(uploaded_file, subsecretaria, tipo_proceso):
    # Obtener configuración del proceso de PROCESO_DATA
    proceso_config = PROCESO_DATA.get(subsecretaria, {}).get('procesos', {}).get(tipo_proceso, {})

    if not proceso_config:
        return False, get_string('errors.no_process_structure', 'ingesta').format(process_type=tipo_proceso)

    cabeceras_esperadas = proceso_config.get('header', None)
    file_type = proceso_config.get('file_type', 'csv')
    file_start_row = proceso_config.get('file_start_row', 0)
    file_start_col = proceso_config.get('file_start_col', 'A')
    file_end_col = proceso_config.get('file_end_col', 'Z')

    if not cabeceras_esperadas:
        return False, get_string('errors.no_process_structure', 'ingesta').format(process_type=tipo_proceso)

    try:
        uploaded_file.seek(0)
        
        # Verificar si el tipo de archivo coincide con la configuración
        if uploaded_file.name.lower().endswith('.xlsx') and file_type != 'xlsx':
            return False, get_string('errors.file_format', 'ingesta').format(
                error=get_string('errors.file_format_csv', 'ingesta')
            )
        elif uploaded_file.name.lower().endswith('.csv') and file_type != 'csv':
            return False, get_string('errors.file_format', 'ingesta').format(
                error=get_string('errors.file_format_excel', 'ingesta')
            )

        # Leer archivo basado en la configuración
        if file_type == 'xlsx':
            # Leer archivo XLSX con fila de inicio y columnas configuradas
            df = pd.read_excel(
                uploaded_file,
                header=file_start_row - 1,  # Convertir a índice basado en 0
                usecols=f"{file_start_col}:{file_end_col}"
            )
        else:
            # Para archivos CSV, mantener la lógica existente
            df = pd.read_csv(io.BytesIO(uploaded_file.read()), delimiter=';', dtype=str, keep_default_na=False)
        
        uploaded_file.seek(0)

        if df.empty:
            return False, get_string('errors.file_empty', 'ingesta')

        cabeceras_reales = df.columns.tolist()
        if cabeceras_reales != cabeceras_esperadas:
            print(get_string('messages.headers_expected', 'ingesta').format(
                process_type=tipo_proceso,
                headers=cabeceras_esperadas
            ))
            print(get_string('messages.headers_found', 'ingesta').format(headers=cabeceras_reales))
            
            msg_error = get_string('errors.headers_mismatch', 'ingesta').format(
                expected_count=len(cabeceras_esperadas),
                found_count=len(cabeceras_reales)
            )

            faltan = set(cabeceras_esperadas) - set(cabeceras_reales)
            sobran = set(cabeceras_reales) - set(cabeceras_esperadas)

            if faltan:
                msg_error += get_string('errors.missing_columns', 'ingesta').format(
                    columns=', '.join(list(faltan)[:3]) + ('...' if len(faltan)>3 else '')
                )
            if sobran:
                msg_error += get_string('errors.extra_columns', 'ingesta').format(
                    columns=', '.join(list(sobran)[:3]) + ('...' if len(sobran)>3 else '')
                )
            return False, msg_error

        # Validar si algún registro ya existe
        is_valid, error_msg = validar_registros_existentes(df, proceso_config)
        if not is_valid:
            return False, error_msg

        # Validar valores de catálogos y generar reporte de errores
        catalog_errors, error_df = validar_catalogos_y_generar_log(df, proceso_config)

        if catalog_errors:
            return False, catalog_errors, error_df

        return True, None

    except pd.errors.EmptyDataError:
        return False, get_string('errors.file_empty', 'ingesta')
    except pd.errors.ParserError as e:
        # Verificar errores específicos relacionados con columnas
        error_str = str(e)
        if "out-of-bounds indices" in error_str or "usecols" in error_str:
            return False, get_string('errors.file_structure_mismatch', 'ingesta')
        else:
            return False, get_string('errors.file_format', 'ingesta').format(
                error=get_string('errors.file_format_generic', 'ingesta')
            )
    except UnicodeDecodeError:
        return False, get_string('errors.file_encoding', 'ingesta')
    except Exception as e:
        print(get_string('messages.general_error', 'ingesta').format(error=e))
        # Proporcionar un mensaje de error más amigable para el usuario
        error_str = str(e)
        if "out-of-bounds" in error_str or "usecols" in error_str:
            return False, get_string('errors.file_structure_mismatch', 'ingesta')
        else:
            return False, get_string('errors.file_unexpected', 'ingesta').format(
                error=get_string('errors.file_structure_generic', 'ingesta')
            )
