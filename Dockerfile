# Dockerfile

# 1. Usa una imagen oficial de Python como base (elige una versión estable)
FROM python:3.10-slim

# 2. Establece variables de entorno útiles
ENV PYTHONDONTWRITEBYTECODE 1 # Evita que Python escriba archivos .pyc
ENV PYTHONUNBUFFERED 1     # Asegura que los logs de Python salgan directo al terminal Docker

# 3. Crea y establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instala dependencias del sistema si fueran necesarias
#    (Ejemplo: libpq-dev para psycopg2 si no usas -binary)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#       build-essential libpq-dev \
#    && rm -rf /var/lib/apt/lists/*

# 5. Copia el archivo de requerimientos e instala dependencias de Python
#    Se copia solo primero para aprovechar el caché de Docker si no cambian
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia todo el código de tu proyecto al directorio de trabajo en el contenedor
COPY . /app/

# 7. Expone el puerto en el que correrá la aplicación DENTRO del contenedor
EXPOSE 8000

# 8. Comando por defecto para ejecutar la aplicación (para desarrollo)
#    Para producción, lo cambiaríamos por Gunicorn/uWSGI
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]