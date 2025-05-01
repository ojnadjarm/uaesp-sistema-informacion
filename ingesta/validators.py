import io
import pandas as pd
from .forms import PROCESO_DATA
from .messages import (
    FILE_EMPTY, FILE_FORMAT_ERROR, FILE_ENCODING_ERROR, FILE_UNEXPECTED_ERROR,
    FILE_HEADERS_MISMATCH, FILE_MISSING_COLUMNS, FILE_EXTRA_COLUMNS,
    NO_PROCESS_STRUCTURE, PRINT_HEADERS_EXPECTED, PRINT_HEADERS_FOUND,
    PRINT_UNEXPECTED_ERROR
)

def validar_estructura_csv(uploaded_file, subsecretaria, tipo_proceso):
    # Get process configuration from PROCESO_DATA
    proceso_config = PROCESO_DATA.get(subsecretaria, {}).get('procesos', {}).get(tipo_proceso, {})
    
    if not proceso_config:
        return False, NO_PROCESS_STRUCTURE.format(process_type=tipo_proceso)

    cabeceras_esperadas = proceso_config.get('cabeceras', None)
    file_type = proceso_config.get('file_type', 'csv')
    file_start_row = proceso_config.get('file_start_row', 0)
    file_start_col = proceso_config.get('file_start_col', 'A')
    file_end_col = proceso_config.get('file_end_col', 'Z')

    if not cabeceras_esperadas:
        return False, NO_PROCESS_STRUCTURE.format(process_type=tipo_proceso)

    try:
        uploaded_file.seek(0)
        
        # Check if file type matches configuration
        if uploaded_file.name.lower().endswith('.xlsx') and file_type != 'xlsx':
            return False, FILE_FORMAT_ERROR.format(error="File must be CSV")
        elif uploaded_file.name.lower().endswith('.csv') and file_type != 'csv':
            return False, FILE_FORMAT_ERROR.format(error="File must be XLSX")
        
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
            return False, FILE_EMPTY

        cabeceras_reales = df.columns.tolist()
        if cabeceras_reales != cabeceras_esperadas:
            print(PRINT_HEADERS_EXPECTED.format(
                process_type=tipo_proceso,
                headers=cabeceras_esperadas
            ))
            print(PRINT_HEADERS_FOUND.format(headers=cabeceras_reales))
            
            msg_error = FILE_HEADERS_MISMATCH.format(
                expected_count=len(cabeceras_esperadas),
                found_count=len(cabeceras_reales)
            )

            faltan = set(cabeceras_esperadas) - set(cabeceras_reales)
            sobran = set(cabeceras_reales) - set(cabeceras_esperadas)

            if faltan:
                msg_error += FILE_MISSING_COLUMNS.format(
                    columns=', '.join(list(faltan)[:3]) + ('...' if len(faltan)>3 else '')
                )
            if sobran:
                msg_error += FILE_EXTRA_COLUMNS.format(
                    columns=', '.join(list(sobran)[:3]) + ('...' if len(sobran)>3 else '')
                )
            return False, msg_error

        return True, None

    except pd.errors.EmptyDataError:
        return False, FILE_EMPTY
    except pd.errors.ParserError as e:
        return False, FILE_FORMAT_ERROR.format(error=str(e))
    except UnicodeDecodeError:
        return False, FILE_ENCODING_ERROR
    except Exception as e:
        print(PRINT_UNEXPECTED_ERROR.format(error=e))
        return False, FILE_UNEXPECTED_ERROR.format(error=str(e))