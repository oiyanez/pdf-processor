FROM python:3.10-slim

# Evita prompts durante apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Instala paquetes del sistema, incluyendo tesseract y poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copia dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la app
COPY . /app
WORKDIR /app

# Puerto que espera Railway
ENV PORT 8000
EXPOSE 8000

# Comando para lanzar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



