import fitz  # PyMuPDF
import re
from pdf2image import convert_from_path
import pytesseract
from datetime import datetime

# Cambiar a la ruta de Tesseract si no está en PATH (Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def es_pdf_con_texto(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        if page.get_text().strip():
            return True
    return False

def extraer_texto_pdf(pdf_path):
    texto_total = ""
    if es_pdf_con_texto(pdf_path):
        doc = fitz.open(pdf_path)
        for page in doc:
            texto_total += page.get_text()
    else:
        imagenes = convert_from_path(pdf_path)
        for img in imagenes:
            texto_total += pytesseract.image_to_string(img)
    return texto_total

def parsear_operaciones(texto):
    operaciones = []
    regex = re.compile(
        r'(?P<fecha>\d{2}[-/][A-Z]{3}[-/]\d{4})\s+'
        r'(?P<folio>\d+)\s+'
        r'(?P<descripcion>.+?)\s+'
        r'(?:(?P<deposito>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+)?'
        r'(?:(?P<retiro>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+)?'
        r'(?P<saldo>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        re.DOTALL
    )

    for match in regex.finditer(texto):
        fecha = match.group('fecha').replace('-', '/').replace('ENE', '01').replace('FEB', '02').replace('MAR', '03').replace('ABR', '04').replace('MAY', '05')  # y así sucesivamente
        try:
            fecha_formateada = datetime.strptime(fecha, '%d/%m/%Y').strftime('%d/%m/%Y')
        except:
            continue

        descripcion = re.sub(r'\s+', ' ', match.group('descripcion')).strip()
        deposito = float(match.group('deposito').replace(',', '')) if match.group('deposito') else None
        retiro = float(match.group('retiro').replace(',', '')) if match.group('retiro') else None
        saldo = float(match.group('saldo').replace(',', ''))

        operaciones.append({
            "fecha": fecha_formateada,
            "tipo": "depósito" if deposito else "pago",
            "monto": deposito if deposito else retiro,
            "descripcion": descripcion,
            "saldo_final": saldo
        })

    return operaciones

def procesar_estado_cuenta(pdf_path, banco="Desconocido"):
    texto = extraer_texto_pdf(pdf_path)
    operaciones = parsear_operaciones(texto)

    if all(k in operaciones[0] for k in ["fecha", "tipo", "monto", "descripcion", "saldo_final"]):
        return {
            "banco": banco,
            "operaciones": operaciones
        }
    else:
        print("Faltan campos clave en algunas operaciones.")
        return None

# 👉 Uso del script
resultado = procesar_estado_cuenta("estado_cuenta.pdf", banco="Santander")
print(resultado)
