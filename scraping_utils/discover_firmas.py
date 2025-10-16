# scraping_utils/discover_firmas.py
import os

def discover_from_pdfs(base_dir, prefijo):
    """
    Escanea la carpeta base_dir en busca de PDFs cuyo nombre comience
    con el prefijo dado y arma listas de formatos y documentos.
    
    Ejemplo:
    - prefijo = "410"
    - archivos encontrados:
        4108604352618.pdf
        4108604359876.pdf
    Retorna:
        formatos = [410, 410]
        documentos = [4108604352618, 4108604359876]
    """
    formatos = []
    documentos = []
    prefijo = str(prefijo)

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".pdf") and file.startswith(prefijo):
                num_doc = os.path.splitext(file)[0]
                try:
                    formato = int(prefijo)
                    documento = int(num_doc)
                    formatos.append(formato)
                    documentos.append(documento)
                except ValueError:
                    continue

    return formatos, documentos
