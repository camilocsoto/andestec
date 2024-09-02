# Usar la imagen base de Python
FROM python:3.11.5

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo
WORKDIR /andes-tech

# Copiar los archivos de requerimientos y luego instalar las dependencias de Python
COPY requirements.txt /andes-tech/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto al contenedor
COPY . /andes-tech/

# Realizar migraciones de base de datos y recopilar archivos estáticos
# RUN python manage.py collectstatic --no-input && \
#    python manage.py migrate

# Exponer el puerto 8000 para que Docker pueda mapearlo a tu máquina host
EXPOSE 8000

# Comando para levantar el servidor (sin Gunicorn por ahora)
CMD ["python3", "andes/manage.py", "runserver", "0.0.0.0:8000"]
