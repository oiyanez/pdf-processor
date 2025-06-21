from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import pytesseract
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extraer_campos(texto: str):
    lineas = texto.split("\n")
    resultados = []
    deposito_regex = re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d{2})\b")
    fecha_regex = re.compile(r"\d{2}/\d{2}/\d{4}")

    for linea in lineas:
        if any(p in linea.lower() for p in ["dep", "abono", "pago", "ingreso"]):
            deposito = deposito_regex.findall(linea)
            fecha = fecha_regex.search(linea)
            resultados.append({
                "fecha": fecha.group() if fecha else None,
                "concepto": linea,
                "deposito": float(deposito[0].replace(',', '')) if deposito else 0.0,
                "saldo_final": float(deposito[1].replace(',', '')) if len(deposito) > 1 else None
            })
    return resultados

@app.post("/leer-imagen")
async def leer_imagen(file: UploadFile = File(...)):
    contenido = await file.read()
    imagen = Image.open(io.BytesIO(contenido))
    texto_extraido = pytesseract.image_to_string(imagen, lang="spa")

    datos = extraer_campos(texto_extraido)

    return {
        "archivo": file.filename,
        "banco": "desconocido",  # puedes inferirlo con lógica adicional
        "datos": datos
    }
