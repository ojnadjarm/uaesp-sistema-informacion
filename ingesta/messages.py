# Messages for file validation
FILE_EMPTY = "The file is empty or has no data."
FILE_EXTENSION_ERROR = "Error: The file must have .csv or .xlsx extension"
FILE_FORMAT_ERROR = "Error processing the file. Please check the format: {error}"
FILE_ENCODING_ERROR = "Encoding error. Please ensure it's UTF-8 or compatible."
FILE_UNEXPECTED_ERROR = "Unexpected error validating the file: {error}"
FILE_HEADERS_MISMATCH = "Columns do not match. Expected: {expected_count}, Found: {found_count}."
FILE_MISSING_COLUMNS = " Missing columns: {columns}."
FILE_EXTRA_COLUMNS = " Extra columns: {columns}."

# Messages for MinIO operations
MINIO_NOT_CONFIGURED = "Error: MinIO service not configured."
MINIO_UPLOAD_ERROR = "Error uploading file to storage: {error}"
MINIO_BUCKET_CREATED = "Bucket '{bucket}' created in MinIO."
MINIO_UPLOAD_SUCCESS = "File uploaded successfully to MinIO as {object_name}"
MINIO_INIT_SUCCESS = "MinIO client initialized successfully."
MINIO_INIT_ERROR = "CRITICAL ERROR: Could not configure MinIO client. Check environment variables. Error: {error}"

# Messages for database operations
DB_SAVE_ERROR = "CRITICAL ERROR: The file '{filename}' was uploaded to storage, but failed to register in the database. Please contact the administrator. Error: {error}"
DB_SAVE_SUCCESS = "File '{filename}' (Type: {process_type}) validated and uploaded successfully."
DB_SAVE_PRINT = "Load record saved in DB (ID: {id})"
DB_LOAD_ERROR = "Error getting load records: {error}"

# Messages for form validation
INVALID_FORM = "Invalid form. Please check the fields."
NO_PROCESS_STRUCTURE = "No structure has been defined for the process type '{process_type}'."

# Messages for dashboard
DASHBOARD_ERROR = "Could not get load records."

# Print messages
PRINT_VALIDATING_FILE = "Validating file '{filename}' for process: {process_type}"
PRINT_VALIDATION_SUCCESS = "File validated successfully. Proceeding to upload to server."
PRINT_HEADERS_EXPECTED = "Expected headers ({process_type}): {headers}"
PRINT_HEADERS_FOUND = "Found headers: {headers}"
PRINT_UNEXPECTED_ERROR = "Unexpected error in validation: {error}"
PRINT_DB_ERROR = "ERROR saving to DB after MinIO upload: {error}"
PRINT_MINIO_ERROR = "MinIO/S3 error uploading file: {error}"
PRINT_GENERAL_ERROR = "Unexpected error during upload/save: {error}"

# Template messages
TEMPLATE_TITLE = "Sistema de Información UAESP"
TEMPLATE_NAVBAR_BRAND = "UAESP"
TEMPLATE_DASHBOARD = "Panel Principal"
TEMPLATE_FILE_HISTORY = "Historial de Carga"
TEMPLATE_UPLOAD_FILE = "Cargar Archivo"
TEMPLATE_LOAD_NEW_FILE = "Cargar Nuevo Archivo"
TEMPLATE_NO_RECORDS = "No hay registros de carga."
TEMPLATE_NO_RECORDS_DESCRIPTION = "No se han encontrado registros de carga en el sistema."
TEMPLATE_UPLOAD_TITLE = "Cargar Archivo CSV"
TEMPLATE_FILE_HELP = "Seleccione el archivo CSV correspondiente al proceso."
TEMPLATE_UPLOAD_BUTTON = "Cargar Archivo"

# Module Navigation
TEMPLATE_MODULE_INGESTA = "Ingesta de Datos"
TEMPLATE_MODULE_INGESTA_DESC = "Gestión y monitoreo de carga de archivos"
TEMPLATE_MODULE_PRESUPUESTO = "Presupuesto"
TEMPLATE_MODULE_PRESUPUESTO_DESC = "Gestión presupuestal y financiera"
TEMPLATE_MODULE_PAA = "Plan Anual de Adquisiciones"
TEMPLATE_MODULE_PAA_DESC = "Planificación y seguimiento de adquisiciones"
TEMPLATE_MODULE_REPORTES = "Reportes"
TEMPLATE_MODULE_REPORTES_DESC = "Generación y visualización de reportes"
TEMPLATE_MODULE_COMING_SOON = "Próximamente"
TEMPLATE_MODULE_COMING_SOON_DESC = "Este módulo estará disponible próximamente"

# Dashboard Messages
TEMPLATE_DASHBOARD_TITLE = "Panel de Control"
TEMPLATE_DASHBOARD_WELCOME = "Bienvenido al Sistema de Información UAESP"
TEMPLATE_DASHBOARD_DESCRIPTION = "Gestión y monitoreo de carga de datos"

# Statistics Labels
TEMPLATE_TOTAL_FILES = "Archivos Procesados"
TEMPLATE_SUCCESS_RATE = "Tasa de Éxito"
TEMPLATE_RECENT_UPLOADS = "Cargas Recientes (24h)"
TEMPLATE_ACTIVE_PROCESSES = "Procesos Activos"

# Quick Actions
TEMPLATE_QUICK_ACTIONS = "Acciones Rápidas"
TEMPLATE_VIEW_HISTORY = "Ver Historial"
TEMPLATE_SYSTEM_STATUS = "Estado del Sistema"

# Activity Overview
TEMPLATE_ACTIVITY_OVERVIEW = "Resumen de Actividad"
TEMPLATE_STATUS_DISTRIBUTION = "Distribución de Estados"
TEMPLATE_PROCESSING_TRENDS = "Tendencias de Procesamiento"

# File History Labels
TEMPLATE_HISTORY_TITLE = "Historial de Archivos Cargados"
TEMPLATE_HISTORY_DESCRIPTION = "Registro histórico de archivos procesados"
TEMPLATE_DATE_TIME = "Fecha/Hora"
TEMPLATE_ORIGINAL_FILE = "Archivo Original"
TEMPLATE_SUBSECRETARY = "Subsecretaría"
TEMPLATE_PROCESS_TYPE = "Tipo de Proceso"
TEMPLATE_STATUS = "Estado"
TEMPLATE_MINIO_PATH = "Ruta en MinIO"
TEMPLATE_ERROR = "Error"
TEMPLATE_NA = "N/A"
TEMPLATE_DASH = "-"

# Status Messages
TEMPLATE_ACTIVE = "Activo"
TEMPLATE_INACTIVE = "Inactivo"
TEMPLATE_WARNING = "Advertencia"
TEMPLATE_ERROR = "Error" 