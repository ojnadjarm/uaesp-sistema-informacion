import io
import pandas as pd
from .forms import PROCESO_DATA  # Try relative import from the same package

def validar_estructura_csv(uploaded_file, subsecretaria, tipo_proceso):
    # Busca las cabeceras esperadas en el diccionario
    cabeceras_esperadas = PROCESO_DATA.get(subsecretaria, {}).get('procesos', {}).get(tipo_proceso, {}).get('cabeceras', None)

    if not cabeceras_esperadas:
        return False, f"No se ha definido una estructura esperada para el tipo de proceso '{tipo_proceso}'."

    try:
        uploaded_file.seek(0)
        # Asume delimitador ';' por defecto basado en la imagen, ajusta si es necesario
        df = pd.read_csv(io.BytesIO(uploaded_file.read()), delimiter=';', dtype=str, keep_default_na=False) # Leer todo como texto inicialmente
        uploaded_file.seek(0)

        if df.empty:
            return False, "El archivo CSV está vacío o no tiene datos."

        cabeceras_reales = df.columns.tolist()
        if cabeceras_reales != cabeceras_esperadas:
            print(f"Cabeceras esperadas ({tipo_proceso}): {cabeceras_esperadas}")
            print(f"Cabeceras reales:           {cabeceras_reales}")
            # Podrías calcular qué columnas faltan o sobran para un mensaje más útil
            faltan = set(cabeceras_esperadas) - set(cabeceras_reales)
            sobran = set(cabeceras_reales) - set(cabeceras_esperadas)
            msg_error = f"Las columnas no coinciden. Esperadas: {len(cabeceras_esperadas)}, Encontradas: {len(cabeceras_reales)}."
            if faltan:
                msg_error += f" Faltan: {', '.join(list(faltan)[:3])}{'...' if len(faltan)>3 else ''}."
            if sobran:
                 msg_error += f" Sobran: {', '.join(list(sobran)[:3])}{'...' if len(sobran)>3 else ''}."
            return False, msg_error

        return True, None

    except pd.errors.EmptyDataError:
        return False, "El archivo CSV parece estar vacío."
    except pd.errors.ParserError as e:
        return False, f"Error al procesar el archivo CSV. Verifica formato/delimitador: {e}"
    except UnicodeDecodeError:
        return False, "Error de codificación. Asegúrate que sea UTF-8 o compatible."
    except Exception as e:
        print(f"Error inesperado en validación: {e}")
        return False, f"Error inesperado al validar el archivo: {e}"