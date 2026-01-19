# Dockerfile servicio_gestion
# Imagen base de Python
FROM python:3.12-slim
# Directorio de trabajo
WORKDIR /
# Copia servicio_gestion.py a la raiz del contenedor
COPY ../app_gestion.py .
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Crear directorio para la base de datos
RUN mkdir /database
# Directorio de trabajo
WORKDIR /database
# Copia odontocare.db al directorio /data del contenedor
#COPY ../database/odontocare.db .
# Cambiamos el directorio de trabajo para copiar el resto de la aplicación
WORKDIR /app
# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copia el resto de la aplicación
COPY . .
# Expone el puerto 5001
EXPOSE 5001
# Comando para ejecutar la app
CMD ["python", "app_gestion.py"]