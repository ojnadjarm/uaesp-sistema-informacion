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
TEMPLATE_TITLE = "UAESP Information System"
TEMPLATE_NAVBAR_BRAND = "UAESP Ingesta"
TEMPLATE_DASHBOARD = "Dashboard"
TEMPLATE_UPLOAD_FILE = "Upload File"
TEMPLATE_LOAD_NEW_FILE = "Go to Upload New File"
TEMPLATE_NO_RECORDS = "No load records yet."
TEMPLATE_UPLOAD_TITLE = "Upload CSV File"
TEMPLATE_FILE_HELP = "Select the CSV file corresponding to the process."
TEMPLATE_UPLOAD_BUTTON = "Upload File"
TEMPLATE_DASHBOARD_TITLE = "Dashboard - Latest File Uploads"
TEMPLATE_DATE_TIME = "Date/Time"
TEMPLATE_ORIGINAL_FILE = "Original File"
TEMPLATE_SUBSECRETARY = "Subsecretary"
TEMPLATE_PROCESS_TYPE = "Process Type"
TEMPLATE_STATUS = "Status"
TEMPLATE_MINIO_PATH = "Path in MinIO"
TEMPLATE_ERROR = "Error"
TEMPLATE_NA = "N/A"
TEMPLATE_DASH = "-" 