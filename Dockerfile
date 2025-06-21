FROM python:3.10-slim

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y poppler-utils tesseract-ocr libtesseract-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Crea directorio de trabajo
WORKDIR /app

# Copia archivos al contenedor
COPY . /app

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usará Uvicorn
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
