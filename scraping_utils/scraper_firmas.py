# scraping_utils/scraper_firmas.py
from bs4 import BeautifulSoup
import requests

def build_payload_firmas(payload_base, num_formato, num_documento):
    """
    Arma el payload para consultar firmas de un documento.
    """
    payload = payload_base.copy()
    payload.update({
        "vistaConsultarFirmasDoc:frmConsultarFirmasDoc:txtNumFormato": str(num_formato),
        "vistaConsultarFirmasDoc:frmConsultarFirmasDoc:txtNumDocumento": str(num_documento),
        "vistaConsultarFirmasDoc:frmConsultarFirmasDoc:_id49.x": "14",
        "vistaConsultarFirmasDoc:frmConsultarFirmasDoc:_id49.y": "13",
    })
    return payload

def buscar_firmas(session, action_url, payload, headers):
    """
    Envía la consulta de firmas y devuelve el HTML con los botones de descarga.
    """
    resp = session.post(action_url, data=payload, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    form = soup.find("form", id="vistaConsultarFirmasDoc:frmConsultarFirmasDoc")
    if not form:
        raise RuntimeError("⚠️ No encontré el formulario de firmas.")
    action2 = requests.compat.urljoin(action_url, form["action"])

    # Extraer todos los inputs hidden de nuevo
    hidden = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        value = inp.get("value", "")
        hidden[name] = value

    # Normalizar ViewState si existe
    if "com.sun.faces.VIEW" in hidden:
        hidden["javax.faces.ViewState"] = hidden["com.sun.faces.VIEW"]

    return soup, action2, hidden

def get_guardar_buttons(soup):
    """
    Devuelve los botones 'Guardar' (tipo image) para descargar documentos firmados.
    """
    return soup.select("input[id*='btnGuardar'][type='image']")

def descargar_firma(session, action_url, soup, btn_name, headers):
    """
    Descarga el documento firmado (XML) asociado a un botón Guardar.
    """
    # Recolectar hidden inputs del form actual
    form = soup.find("form", id="vistaConsultarFirmasDoc:frmConsultarFirmasDoc")
    hidden = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        hidden[name] = inp.get("value", "")

    # Normalizar ViewState
    if "com.sun.faces.VIEW" in hidden:
        hidden["javax.faces.ViewState"] = hidden["com.sun.faces.VIEW"]

    # Añadir clic del botón image
    payload = hidden.copy()
    payload[btn_name + ".x"] = "10"
    payload[btn_name + ".y"] = "10"

    resp = session.post(action_url, data=payload, headers=headers)
    ctype = resp.headers.get("Content-Type", "")
    if resp.status_code == 200 and ("xml" in ctype or ctype.startswith("application/octet-stream")):
        return resp.content
    else:
        print(f"⚠️ Respuesta inesperada: status={resp.status_code}, Content-Type={ctype}, len={len(resp.content)}")
        return None

