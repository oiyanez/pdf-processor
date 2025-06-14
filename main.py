from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from io import BytesIO

app = FastAPI(title="Lector de PDFs", description="API para extraer texto de archivos PDF", version="1.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto si usarás dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/leer-pdf")
async def leer_pdf(file: UploadFile = File(...)):
    """
    Extrae texto de un archivo PDF cargado.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        contenido = await file.read()
        pdf = PdfReader(BytesIO(contenido))
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

        return {
            "nombre_archivo": file.filename,
            "paginas": len(pdf.pages),
            "fragmento_texto": texto[:500],  # solo muestra los primeros 500 caracteres
            "texto_completo": texto
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")
