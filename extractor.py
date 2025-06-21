import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import re
import io
from PIL import Image
import pandas as pd

def extraer_movimientos(pdf_path):
    """
    Para cada página:
      - Si tiene texto seleccionable, lo extrae directo.
      - Si no, convierte a imagen y hace OCR.
    Devuelve un DataFrame con columnas: fecha, concepto, importe, saldo.
    """
    doc = fitz.open(pdf_path)
    filas = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        txt = page.get_text().strip()

        if txt:
            # Páginas con capa de texto: usamos regex sobre el texto completo
            lineas = txt.split('\n')
        else:
            # Páginas escaneadas: convertimos a imagen y OCR
            pil_img = convert_from_path(pdf_path, first_page=page_num+1,
                                        last_page=page_num+1, dpi=300)[0]
            # opcional: binarización para mejorar OCR
            buffer = io.BytesIO()
            pil_img.save(buffer, format="PNG")
            image = Image.open(buffer)
            lineas = pytesseract.image_to_string(image, lang="spa").split('\n')

        # Extraer con regex patrón dd/mm/aaaa, texto, importe, saldo
        for ln in lineas:
            m = re.match(
                r'^\s*(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d\.,]+)\s+([\d\.,]+)\s*$',
                ln
            )
            if m:
                filas.append({
                    'fecha': m.group(1),
                    'concepto': m.group(2).strip(),
                    'importe': m.group(3).replace(',', ''),
                    'saldo': m.group(4).replace(',', '')
                })

    # Montar DataFrame y normalizar tipos
    df = pd.DataFrame(filas)
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True)
        df['importe'] = df['importe'].astype(float)
        df['saldo'] = df['saldo'].astype(float)
    return df
