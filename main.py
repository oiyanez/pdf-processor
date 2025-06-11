from fastapi import FastAPI, UploadFile, File
import pdfplumber
import io

app = FastAPI()

@app.post("/procesar")
async def procesar_pdf(file: UploadFile = File(...)):
    contenido = await file.read()
    data = []
    with pdfplumber.open(io.BytesIO(contenido)) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                for linea in texto.split('\n'):
                    if '202' in linea:
                        partes = linea.split()
                        if len(partes) > 2:
                            data.append({
                                "fecha": partes[0],
                                "descripcion": ' '.join(partes[1:-1]),
                                "monto": partes[-1]
                            })
    return {"items": data}
