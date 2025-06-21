FROM python:3.10-slim

# Evita errores interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependencias necesarias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
