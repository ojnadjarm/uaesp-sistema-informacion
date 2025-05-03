import os
from minio import Minio
from globalfunctions.string_manager import get_string

def get_minio_client():
    try:
        MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT_URL', 'minio:9000').split('//')[-1]
        MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
        MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'password_minio')
        MINIO_USE_HTTPS = os.environ.get('MINIO_USE_HTTPS', '0') == '1'

        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_USE_HTTPS
        )
        print(get_string('success.minio_init', 'ingesta'))
        return minio_client
    except Exception as e:
        print(get_string('errors.minio_init', 'ingesta').format(error=e))
        return None

def get_minio_bucket():
    return os.environ.get('MINIO_BUCKET_NAME', 'uaesp-ingesta-crudo') 