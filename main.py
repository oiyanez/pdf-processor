from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from io import BytesIO

app = FastAPI()

# Habilitar CORS por si conectas desde n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/leer-pdf")
async def leer_pdf(file: UploadFile = File(...)):
    contenido = await file.read()
    pdf = PdfReader(BytesIO(contenido))
    texto = ""
    for page in pdf.pages:
        texto += page.extract_text() + "\n"

    return {
        "nombre_archivo": file.filename,
        "texto": texto
    }
