from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO
import re

app = FastAPI(title="PDF Processor with OCR", version="1.0")

# Permitir CORS si usas Make o n8n externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image, lang="spa") + "\n"
    return text.strip()

def parse_transactions(text: str):
    lines = text.split("\n")
    results = []

    pattern = re.compile(
        r"(?P<fecha>\bHORA\s\d{2}:\d{2}|\b\d{2}/\d{2}/\d{4}|\b\d{8})[^\d]*(?P<concepto>CAJA.*?|SUC.*?)\s+.*?(?P<monto>\d{1,3}(?:[\.,]\d{3})*[\.,]\d{2})[^\d]*(?P<saldo>\d{1,3}(?:[\.,]\d{3})*[\.,]\d{2})"
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            monto = float(match.group("monto").replace(",", "").replace(".", "", match.group("monto").count(".") - 1))
            saldo = float(match.group("saldo").replace(",", "").replace(".", "", match.group("saldo").count(".") - 1))
            results.append({
                "fecha": match.group("fecha"),
                "concepto": match.group("concepto").strip(),
                "monto": monto,
                "saldo_final": saldo,
            })

    return results

@app.post("/leer-pdf")
async def leer_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF.")

    pdf_bytes = await file.read()

    # Intentar extraer texto normal
    text = extract_text_from_pdf(pdf_bytes)

    # Si no hay texto, aplicar OCR
    if len(text.strip()) < 100:
        text = extract_text_with_ocr(pdf_bytes)

    transacciones = parse_transactions(text)

    return {
        "archivo": file.filename,
        "total_paginas": len(PdfReader(BytesIO(pdf_bytes)).pages),
        "total_depositos": len(transacciones),
        "depositos": transacciones,
    }
