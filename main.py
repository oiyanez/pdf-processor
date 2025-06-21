import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import re
import tempfile
import os
from PIL import Image


def extraer_texto_pdf(path_pdf):
    texto_total = ''
    doc = fitz.open(path_pdf)
    for pagina in doc:
        texto = pagina.get_text()
        texto_total += texto
    doc.close()
    return texto_total


def texto_invalido(texto):
    return '�' in texto or len(texto.strip()) < 20


def ocr_pdf(path_pdf):
    texto_total = ''
    with tempfile.TemporaryDirectory() as temp_dir:
        imagenes = convert_from_path(path_pdf, dpi=300, output_folder=temp_dir)
        for img in imagenes:
            texto = pytesseract.image_to_string(img, lang='spa')
            texto_total += texto + '\n'
    return texto_total


def clasificar_operacion(descripcion):
    descripcion = descripcion.lower()
    if 'abono' in descripcion or 'deposito' in descripcion:
        return 'depósito'
    elif 'retiro' in descripcion or 'pago' in descripcion or 'compra' in descripcion:
        return 'pago'
    return 'pago'


def extraer_operaciones(texto):
    operaciones = []
    regex = re.compile(
        r'(?P<fecha>\d{2}-[A-Z]{3}-\d{4})\s+.*?\s+(?P<deposito>\d{1,3}(?:,\d{3})*(?:\.\d{2}))?\s+(?P<retiro>\d{1,3}(?:,\d{3})*(?:\.\d{2}))?\s+(?P<saldo>\d{1,3}(?:,\d{3})*(?:\.\d{2}))',
        re.DOTALL
    )

    matches = regex.finditer(texto)
    for match in matches:
        fecha = match.group('fecha').replace('-', '/')
        deposito = match.group('deposito')
        retiro = match.group('retiro')
        saldo = match.group('saldo')
        descripcion = match.group(0)

        tipo = clasificar_operacion(descripcion)
        monto = float(deposito.replace(',', '')) if deposito else float(retiro.replace(',', ''))
        operaciones.append({
            "fecha": fecha,
            "tipo": tipo,
            "monto": monto,
            "descripcion": descripcion.strip(),
            "saldo_final": float(saldo.replace(',', '')) if saldo else 0.0
        })

    return operaciones


def procesar_estado_cuenta(path_pdf, banco="BBVA"):
    texto = extraer_texto_pdf(path_pdf)
    if texto_invalido(texto):
        texto = ocr_pdf(path_pdf)

    operaciones = extraer_operaciones(texto)
    if not operaciones:
        return None

    return {
        "banco": banco,
        "operaciones": operaciones
    }
