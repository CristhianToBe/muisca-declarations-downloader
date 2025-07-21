import os
import pickle
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from requests.adapters import HTTPAdapter, Retry
import re

# ——————————————————————————————————————————————
# CONFIG
# ——————————————————————————————————————————————
CHROMEDRIVER_PATH = r"D:\Code\Downloadings\Declaraciones\chromedriver.exe"
DOWNLOAD_DIR      = "descargas"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ——————————————————————————————————————————————
# 1) LOGIN MANUAL & CAPTURA FORMULARIO DE BÚSQUEDA
# ——————————————————————————————————————————————
opts = webdriver.ChromeOptions()
opts.add_argument("--start-maximized")
# acelera quitando imágenes
opts.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2
})
# carga rápida
opts.page_load_strategy = "eager"

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
driver.get("https://muisca.dian.gov.co/")

input("🔐 Inicia sesión y navega al formulario de búsqueda. Pulsa ENTER…")

search_url  = driver.current_url
search_html = driver.page_source
cookies      = driver.get_cookies()
driver.quit()

with open("cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)
print("✅ Cookies y HTML de búsqueda listos.")

# ——————————————————————————————————————————————
# 2) MONTAR SESSION con RETRIES y COOKIES
# ——————————————————————————————————————————————
session = requests.Session()
retries = Retry(
    total=5, backoff_factor=0.5,
    status_forcelist=[500,502,503,504],
    allowed_methods=["GET","POST"]
)
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

# ——————————————————————————————————————————————
# 3) ENVIAR EL FORMULARIO DE BÚSQUEDA
# ——————————————————————————————————————————————
soup = BeautifulSoup(search_html, "html.parser")
form = soup.find("form", id="vistaObligacionesPorDocumento:frmObligacionesPorDocumento")
if not form:
    raise RuntimeError("No encontré el formulario de búsqueda.")

# inputs ocultos
payload = { inp["name"]: inp.get("value","") for inp in form.find_all("input") }
# tus datos
payload.update({
    "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:txtNit":            "901716185",
    "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:tipOblig":          "1003",
    "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:annoSeleccionado":  "2024",
    # disparador de búsqueda
    "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:_idcl":
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:lnkBuscarObligaciones"
})

search_action = requests.compat.urljoin(search_url, form["action"])
resp2 = session.post(search_action, data=payload, headers=headers)
resp2.raise_for_status()
soup2 = BeautifulSoup(resp2.text, "html.parser")

# ——————————————————————————————————————————————
# 4) ITERAR CADA “AL DÍA” (lnkContinuar) Y DESCARGAR DETALLES + PDFs
# ——————————————————————————————————————————————
# volver a extraer la misma forma (ahora con la tabla de obligaciones)
form2 = soup2.find("form", id="vistaObligacionesPorDocumento:frmObligacionesPorDocumento")
if not form2:
    raise RuntimeError("No vi la tabla de resultados en la búsqueda.")

# inputs ocultos de la segunda forma
hidden2 = { inp["name"]: inp.get("value","") for inp in form2.find_all("input") }
action2 = requests.compat.urljoin(search_url, form2["action"])

# cada enlace de “AL DÍA”
cont_links = soup2.select("a[onclick*='lnkContinuar']")
print(f"🔁 Encontré {len(cont_links)} obligaciones. Procesando…")

for idx, a in enumerate(cont_links):
    # extraer el valor que se asigna a _idcl
    m = re.search(r"value\s*=\s*'([^']+)'", a["onclick"])
    if not m:
        print(f"⚠️ Fila {idx}: no pude extraer el _idcl.")
        continue
    idcl_value = m.group(1)

    # payload para el detalle
    pay_det = hidden2.copy()
    # sobreescribimos sólo el campo _idcl
    name_idcl = [k for k in pay_det if k.endswith("_idcl")]
    if not name_idcl:
        print("⚠️ No encontré el nombre del campo _idcl.")
        break
    pay_det[name_idcl[0]] = idcl_value

    # post para obtener la página de detalle
    resp_det = session.post(action2, data=pay_det, headers=headers)
    resp_det.raise_for_status()
    soup_det = BeautifulSoup(resp_det.text, "html.parser")

    # parsear el formulario de detalle y extraer sus inputs ocultos
    form_det = soup_det.find("form", id="vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion")
    if not form_det:
        print(f"⚠️ Obligación {idx}: no encontré el formulario de detalle.")
        continue
    hidden_det = { inp["name"]: inp.get("value","") for inp in form_det.find_all("input") }
    action_det = requests.compat.urljoin(search_url, form_det["action"])

    # cada enlace salvarNumDoc(...) en detalle
    save_links = soup_det.select("a[onclick*='salvarNumDoc']")
    for sl in save_links:
        m2 = re.search(r"salvarNumDoc\('(\d+)',\s*(\d+),\s*(\d+)\)", sl["onclick"])
        if not m2:
            continue
        num_doc, num_rep, id_formato = m2.groups()

        pay_pdf = hidden_det.copy()
        pay_pdf.update({
            # valores para el PDF
            "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddNumDoc":    num_doc,
            "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddNumRep":    num_rep,
            "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddIdFormato": id_formato,
        })
        # detectar el nombre real de _idcl en detalle
        idcl_det = [k for k in pay_pdf if k.endswith("_idcl")]
        pay_pdf[idcl_det[0]] = "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:lnkGenerarPdf"

        rpdf = session.post(action_det, data=pay_pdf, headers=headers)
        if rpdf.status_code == 200 and rpdf.headers.get("Content-Type","").startswith("application/pdf"):
            fn = os.path.join(DOWNLOAD_DIR, f"{num_doc}.pdf")
            with open(fn, "wb") as f:
                f.write(rpdf.content)
            print(f"✅ [{idx}] PDF {num_doc}.pdf descargado.")
        else:
            print(f"⚠️ [{idx}] Error al bajar PDF {num_doc}: status {rpdf.status_code}")

print(f"🎉 Proceso terminado. Revisa los PDFs en `{os.path.abspath(DOWNLOAD_DIR)}`.")
