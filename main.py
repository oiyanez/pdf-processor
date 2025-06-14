from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from io import BytesIO
import re

app = FastAPI(title="PDF Processor API", version="1.1")

# Permitir CORS para llamadas externas (como desde n8n)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/leer-pdf")
async def leer_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        contenido = await file.read()
        pdf = PdfReader(BytesIO(contenido))

        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

        # Extraer depósitos con regex
        depositos = extraer_depositos(texto)

        return {
            "archivo": file.filename,
            "total_paginas": len(pdf.pages),
            "total_depositos": len(depositos),
            "depositos": depositos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

def extraer_depositos(texto: str):
    """
    Extrae líneas de texto que contengan depósitos,
    asumiendo que aparecen después de 'Detalle de Operaciones'
    """
    depositos = []
    pattern = re.compile(r"(?P<fecha>\d{2} \w{3}) (?P<concepto>.+?)\s+(?P<monto>\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+(?P<saldo>\d{1,3}(?:,\d{3})*(?:\.\d{2}))")

    for match in pattern.finditer(texto):
        concepto = match.group("concepto").strip()
        monto = match.group("monto").replace(",", "")
        saldo = match.group("saldo").replace(",", "")

        # Condición: si monto está en la penúltima columna, asumimos que es un depósito
        # Por ejemplo: RETIROS VACÍO - MONTO DEPÓSITO PRESENTE
        try:
            monto_float = float(monto)
            saldo_float = float(saldo)
            if monto_float > 0 and "PAGO RECIBIDO" in concepto.upper() or "ABONO" in concepto.upper():
                depositos.append({
                    "fecha": match.group("fecha"),
                    "concepto": concepto,
                    "monto": monto_float,
                    "saldo_final": saldo_float
                })
        except:
            continue

    return depositos