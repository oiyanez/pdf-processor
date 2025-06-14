from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from io import BytesIO
import re

app = FastAPI(
    title="PDF Processor API",
    description="Extrae texto y depósitos desde un PDF bancario",
    version="1.1"
)

# Configuración CORS para permitir acceso desde n8n u otras apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto si quieres restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/leer-pdf")
async def leer_pdf(file: UploadFile = File(...)):
    """
    Endpoint principal para cargar un PDF, extraer texto y detectar depósitos.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        contenido = await file.read()
        pdf = PdfReader(BytesIO(contenido))

        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

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
    Extrae todos los depósitos (líneas con monto en la columna de depósitos).
    """
    depositos = []
    lineas = texto.split("\n")

    for linea in lineas:
        if re.search(r'\d{2} \w{3}', linea):  # Buscar línea con fecha
            partes = linea.strip().split()
            if len(partes) >= 4:
                try:
                    fecha = partes[0] + " " + partes[1]  # Ej: 20 MAR
                    # Buscar montos numéricos tipo 15,000.00
                    numeros = [p for p in partes if re.match(r'^\d{1,3}(?:,\d{3})*(?:\.\d{2})$', p)]
                    if len(numeros) >= 2:
                        monto = float(numeros[-2].replace(",", ""))
                        saldo = float(numeros[-1].replace(",", ""))
                        concepto = " ".join(partes[2:-2])
                        if monto > 0:
                            depositos.append({
                                "fecha": fecha,
                                "concepto": concepto,
                                "monto": monto,
                                "saldo_final": saldo
                            })
                except:
                    continue
    return depositos
