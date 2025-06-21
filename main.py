from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import os
from procesador import procesar_estado_cuenta

app = FastAPI()

@app.post("/leer-imagen")
async def leer_pdf(file: UploadFile = File(...)):
    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    resultado = procesar_estado_cuenta(path)
    os.remove(path)

    if not resultado:
        return JSONResponse(status_code=400, content={"error": "No se pudieron extraer datos"})

    return resultado

# Opcional para correr localmente con `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
