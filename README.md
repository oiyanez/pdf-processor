# Extractor de Movimientos Bancarios

## Descripción
Servicio FastAPI que recibe un PDF, lo convierte a imagen si es necesario, extrae movimientos y devuelve JSON.

## Despliegue en Railway
1. Conecta tu repo a Railway.
2. Selecciona el proyecto y añade:
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Asegúrate de tener `PORT` asignado.
3. Railway detectará el `Dockerfile` y hará build automáticamente.

## Uso
```bash
curl -X POST "https://<tu-app>.railway.app/upload/" \
  -F "file=@/ruta/a/estado_de_cuenta.pdf"
