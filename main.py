from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import pytesseract
from io import BytesIO

app = FastAPI()

# CORS settings para permitir acceso desde cualquier origen (opcional según tu arquitectura)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Servidor activo para OCR de imágenes"}

@app.post("/leer-imagen")
async def leer_imagen(file: UploadFile = File(...)):
    try:
        # Leer imagen desde archivo cargado
        image = Image.open(BytesIO(await file.read()))
        text = pytesseract.image_to_string(image)

        # Detectar el banco desde el texto
        banco = "Desconocido"
        texto_lower = text.lower()
        if "banamex" in texto_lower:
            banco = "Banamex"
        elif "bbva" in texto_lower:
            banco = "BBVA"
        elif "santander" in texto_lower:
            banco = "Santander"
        elif "hsbc" in texto_lower:
            banco = "HSBC"

        # Respuesta de ejemplo
        return {
            "archivo": file.filename,
            "banco": banco,
            "texto_extraido": text[:500],  # Solo los primeros 500 caracteres
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar imagen: {str(e)}")
