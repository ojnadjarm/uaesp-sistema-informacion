import io
import pandas as pd
from io import StringIO
from .forms import PROCESO_DATA
from globalfunctions.string_manager import get_string
from django.db.models import Q
from ingesta.models import DisposicionFinal
from django.apps import apps
from datetime import datetime

def transform_value(value, transform_config):
    """
    Transforms a value according to the configuration to match database format.
    """
    if not transform_config:
        return value

    function_name = transform_config.get('function')
    args = transform_config.get('args', {})

    if function_name == 'transform_date':
        try:
            if isinstance(value, str):
                # Try to parse the date string
                try:
                    # First try to parse as datetime
                    dt = pd.to_datetime(value)
                    return dt.strftime('%Y-%m-%d')
                except:
                    # If that fails, try common formats
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
                # Remove any non-numeric characters except decimal point
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
    Validates if any records already exist in the database based on unique fields.
    Returns (bool, str) tuple: (is_valid, error_message)
    """
    # Get table name from config
    table_name = proceso_config.get('table_name')
    if not table_name:
        return True, None

    # Get model class from table name
    try:
        model = apps.get_model('ingesta', table_name)
    except LookupError:
        return True, None

    # Get validation fields from config
    validation_fields = proceso_config.get('validation', [])
    if not validation_fields:
        return True, None

    # Transform values according to configuration
    transformed_df = df.copy()
    for field_config in validation_fields:
        field_name = field_config['field']
        field_type = field_config.get('type')
        transform_config = field_config.get('transform')
        
        if field_name in transformed_df.columns:
            # Apply transformation based on field type if no specific transform is provided
            if not transform_config and field_type:
                if field_type == 'date':
                    transform_config = {'function': 'transform_date'}
                elif field_type == 'integer':
                    transform_config = {'function': 'transform_integer'}
            
            if transform_config:
                transformed_df[field_name] = transformed_df[field_name].apply(
                    lambda x: transform_value(x, transform_config)
                )

    # Check each row's combination of fields against the database
    for _, row in transformed_df.iterrows():
        query = Q()
        for field_config in validation_fields:
            field_name = field_config['field']
            db_field = field_config.get('db_field', field_name.lower().replace(' ', '_'))
            
            if field_name in row and pd.notna(row[field_name]):
                query &= Q(**{db_field: row[field_name]})

        # If we have a valid query and records exist, return False
        if query and model.objects.filter(query).exists():
            return False, get_string('errors.file_has_existing_records', 'ingesta')

    return True, None

def validar_estructura_csv(uploaded_file, subsecretaria, tipo_proceso):
    # Get process configuration from PROCESO_DATA
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
        
        # Check if file type matches configuration
        if uploaded_file.name.lower().endswith('.xlsx') and file_type != 'xlsx':
            return False, get_string('errors.file_format', 'ingesta').format(
                error=get_string('errors.file_format_csv', 'ingesta')
            )
        elif uploaded_file.name.lower().endswith('.csv') and file_type != 'csv':
            return False, get_string('errors.file_format', 'ingesta').format(
                error=get_string('errors.file_format_excel', 'ingesta')
            )

        # Read file based on configuration
        if file_type == 'xlsx':
            # Read XLSX file with configured start row and columns
            df = pd.read_excel(
                uploaded_file,
                header=file_start_row - 1,  # Convert to 0-based index
                usecols=f"{file_start_col}:{file_end_col}"
            )
        else:
            # For CSV files, keep existing logic
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

        # Validate if any records already exist
        is_valid, error_msg = validar_registros_existentes(df, proceso_config)
        if not is_valid:
            return False, error_msg

        return True, None

    except pd.errors.EmptyDataError:
        return False, get_string('errors.file_empty', 'ingesta')
    except pd.errors.ParserError as e:
        return False, get_string('errors.file_format', 'ingesta').format(error=str(e))
    except UnicodeDecodeError:
        return False, get_string('errors.file_encoding', 'ingesta')
    except Exception as e:
        print(get_string('messages.general_error', 'ingesta').format(error=e))
        return False, get_string('errors.file_unexpected', 'ingesta').format(error=str(e))