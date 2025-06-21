FROM python:3.11-slim

# Tesseract para OCR
RUN apt-get update && \
    apt-get install -y tesseract-ocr libsm6 libxrender1 libxext6 poppler-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
