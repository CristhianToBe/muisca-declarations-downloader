import requests, re
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

def make_session(cookies, search_url):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5,
                    status_forcelist=[500, 502, 503, 504],
                    allowed_methods=["GET", "POST"])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    for c in cookies:
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path"))

    headers = {
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "es-419,es;q=0.9",
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer":         search_url
    }
    return session, headers

def extract_payload(search_html, search_url):
    soup = BeautifulSoup(search_html, "html.parser")
    form = soup.find("form", id="vistaObligacionesPorDocumento:frmObligacionesPorDocumento")
    if not form:
        raise RuntimeError("⚠️ No encontré el formulario de búsqueda.")
    payload_base = {inp["name"]: inp.get("value", "") for inp in form.find_all("input")}
    search_action = requests.compat.urljoin(search_url, form["action"])
    return payload_base, search_action

def build_payload(payload_base, nit, tipo, anio, periodo):
    payload = payload_base.copy()
    payload.update({
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:txtNit": nit,
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:tipOblig": tipo,
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:annoSeleccionado": str(anio),
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:periodoSel": str(periodo),
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:_idcl":
            "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:lnkBuscarObligaciones"
    })
    return payload

def buscar_obligaciones(session, search_action, payload, headers):
    resp2 = session.post(search_action, data=payload, headers=headers)
    if resp2.status_code != 200:
        print("⚠️ Error al consultar obligaciones.")
        return None, None, None
    soup2 = BeautifulSoup(resp2.text, "html.parser")
    form2 = soup2.find("form", id="vistaObligacionesPorDocumento:frmObligacionesPorDocumento")
    if not form2:
        print("⚠️ No se encontró tabla de resultados.")
        return None, None, None
    hidden2 = {inp["name"]: inp.get("value", "") for inp in form2.find_all("input")}
    action2 = requests.compat.urljoin(search_action, form2["action"])
    return soup2, hidden2, action2

def get_obligaciones(soup2):
    cont_links = soup2.select("a[onclick*='lnkContinuar']")
    obligaciones = []
    for idx, a in enumerate(cont_links):
        m = re.search(r"value\s*=\s*'([^']+)'", a["onclick"])
        if m:
            obligaciones.append(m.group(1))
    return obligaciones

def get_pdfs(session, action2, hidden2, idcl_value, headers):
    pay_det = hidden2.copy()
    name_idcl = [k for k in pay_det if k.endswith("_idcl")]
    if not name_idcl:
        return []

    pay_det[name_idcl[0]] = idcl_value
    resp_det = session.post(action2, data=pay_det, headers=headers)
    soup_det = BeautifulSoup(resp_det.text, "html.parser")

    form_det = soup_det.find("form", id="vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion")
    if not form_det:
        return []

    hidden_det = {inp["name"]: inp.get("value", "") for inp in form_det.find_all("input")}
    action_det = requests.compat.urljoin(action2, form_det["action"])

    results = []
    save_links = soup_det.select("a[onclick*='salvarNumDoc']")
    for sl in save_links:
        m2 = re.search(r"salvarNumDoc\('(\d+)',\s*(\d+),\s*(\d+)\)", sl["onclick"])
        if not m2:
            continue
        num_doc, num_rep, id_formato = m2.groups()

        pay_pdf = hidden_det.copy()
        pay_pdf.update({
            "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddNumDoc": num_doc,
            "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddNumRep": num_rep,
            "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddIdFormato": id_formato,
        })
        idcl_det = [k for k in pay_pdf if k.endswith("_idcl")]
        pay_pdf[idcl_det[0]] = "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:lnkGenerarPdf"

        rpdf = session.post(action_det, data=pay_pdf, headers=headers)
        if rpdf.status_code == 200 and rpdf.headers.get("Content-Type", "").startswith("application/pdf"):
            results.append((num_doc, rpdf.content))
    return results
