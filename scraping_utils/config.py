import json

def load_config(path="var.json"):
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Normalizar tipos de obligación
    tipos = config["TIPO_OBLIGACION"]
    if isinstance(tipos, str):
        tipos = [tipos]

    # Normalizar periodos
    periodo = config.get("PERIODO", 1)
    if isinstance(periodo, int):
        periodos = [periodo]
    elif isinstance(periodo, list) and len(periodo) == 2 and all(isinstance(x, int) for x in periodo):
        start, end = periodo
        periodos = list(range(start, end + 1))
    elif isinstance(periodo, list):
        periodos = periodo
    else:
        periodos = [1]

    # Normalizar formatos de firmas
    formatos = config.get("FIRMAS_FORMATOS", [])
    if isinstance(formatos, int):
        formatos = [formatos]

    # Normalizar documentos de firmas
    documentos = config.get("FIRMAS_DOCUMENTOS", [])
    if isinstance(documentos, int) or isinstance(documentos, str):
        documentos = [documentos]

    return {
        "CHROMEDRIVER_PATH": config["CHROMEDRIVER_PATH"],
        "BASE_DOWNLOAD_DIR": config["BASE_DOWNLOAD_DIR"],
        "NIT": config["NIT"],
        "TIPOS_OBLIGACION": tipos,
        "ANIO_INICIO": int(config["ANIO_INICIO"]),
        "ANIO_FIN": int(config["ANIO_FIN"]),
        "PERIODOS": periodos,
        "FIRMAS_FORMATOS": formatos,
        "FIRMAS_DOCUMENTOS": documentos,
    }

