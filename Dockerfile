# Usa una imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos y el código de la aplicación
COPY requirements.txt requirements.txt
COPY . .

# Instala las dependencias
RUN pip install -r requirements.txt

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8103

# Especifica el comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8103", "webservice_app:app"]