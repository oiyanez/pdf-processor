from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from extractor import extraer_movimientos
import pandas as pd
import json
import tempfile
import os

app = FastAPI(title="Extractor de Movimientos Bancarios")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Guardar temporalmente
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        df = extraer_movimientos(tmp_path)
        if df.empty:
            raise ValueError("No se encontraron movimientos.")
        # Convertir a JSON
        resultados = df.to_dict(orient="records")
        return {"movimientos": resultados}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(tmp_path)
