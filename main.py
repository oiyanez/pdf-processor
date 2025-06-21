
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
from io import BytesIO
import pytesseract
import re

app = FastAPI(
    title="PDF Processor API",
    description="Extrae depósitos y pagos desde PDFs bancarios",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_scanned_pdf(file_bytes):
    try:
        reader = PdfReader(file_bytes)
        for page in reader.pages:
            if page.extract_text():
                return False
        return True
    except:
        return True

def extract_text_from_pdf(file_bytes):
    if is_scanned_pdf(file_bytes):
        file_bytes.seek(0)
        images = convert_from_bytes(file_bytes.read())
        full_text = "\n".join([pytesseract.image_to_string(img) for img in images])
    else:
        file_bytes.seek(0)
        reader = PdfReader(file_bytes)
        full_text = "\n".join([page.extract_text() for page in reader.pages])
    return full_text

def procesar_texto_extraido(texto):
    # Este patrón se puede adaptar según el banco
    patron = re.compile(
        r"(HORA\s+\d{2}:\d{2}|CAJA\s+\d{4})\s+.*?(SUC\s+\d{4}|AUT\s+\d{8})[^\d]*(\d{1,3}(?:,\d{3})*\.\d{2})[^\d]*(\d{1,3}(?:,\d{3})*\.\d{2})",
        re.MULTILINE
    )

    matches = patron.findall(texto)
    depositos = []

    for match in matches:
        fecha, concepto, monto, saldo = match
        try:
            monto_valor = float(monto.replace(",", ""))
            saldo_valor = float(saldo.replace(",", ""))
        except:
            continue
        depositos.append({
            "fecha": fecha,
            "concepto": concepto,
            "monto": monto_valor,
            "saldo_final": saldo_valor
        })

    return {
        "archivo": "extraido.pdf",
        "total_paginas": texto.count("Página") or 1,
        "total_depositos": len(depositos),
        "depositos": depositos
    }

@app.post("/leer-pdf")
async def leer_pdf(file: UploadFile = File(...)):
    file_content = await file.read()
    file_bytes = BytesIO(file_content)

    texto_extraido = extract_text_from_pdf(file_bytes)
    resultado = procesar_texto_extraido(texto_extraido)

    return resultado
