import os
import pickle
import re
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from requests.adapters import HTTPAdapter, Retry
import subprocess
import json

# ——————————————————————————————————————————————
# 0) LEER VARIABLES DESDE JSON
# ——————————————————————————————————————————————
with open("var.json", "r", encoding="utf-8") as f:
    config = json.load(f)

CHROMEDRIVER_PATH = config["CHROMEDRIVER_PATH"]
BASE_DOWNLOAD_DIR = config["BASE_DOWNLOAD_DIR"]
NIT = config["NIT"]
TIPO_OBLIGACION = config["TIPO_OBLIGACION"]
ANIO_INICIO = int(config["ANIO_INICIO"])
ANIO_FIN = int(config["ANIO_FIN"])

os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

# ——————————————————————————————————————————————
# 1) LOGIN MANUAL & CAPTURA FORMULARIO DE BÚSQUEDA
# ——————————————————————————————————————————————
# Ejecuta chromedriver con --version
result = subprocess.run([CHROMEDRIVER_PATH, "--version"], capture_output=True, text=True)
print("Versión detectada de chromedriver:", result.stdout.strip())
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)
version = driver.capabilities.get("browserVersion")
driver.quit()

print("Versión de Chrome detectada por Selenium:", version)
opts = webdriver.ChromeOptions()
opts.add_argument("--start-maximized")
opts.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2
})
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
# 3) EXTRAER PAYLOAD BASE DEL FORMULARIO
# ——————————————————————————————————————————————
soup = BeautifulSoup(search_html, "html.parser")
form = soup.find("form", id="vistaObligacionesPorDocumento:frmObligacionesPorDocumento")
if not form:
    raise RuntimeError("No encontré el formulario de búsqueda.")

payload_base = { inp["name"]: inp.get("value","") for inp in form.find_all("input") }
search_action = requests.compat.urljoin(search_url, form["action"])

# ——————————————————————————————————————————————
# 4) BUCLE PARA VARIOS AÑOS (desde JSON)
# ——————————————————————————————————————————————
for anio in range(ANIO_INICIO, ANIO_FIN + 1):
    print(f"\n📅 Procesando año {anio}...")

    download_dir = os.path.join(BASE_DOWNLOAD_DIR, str(anio))
    os.makedirs(download_dir, exist_ok=True)

    payload = payload_base.copy()
    payload.update({
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:txtNit":            NIT,
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:tipOblig":          TIPO_OBLIGACION,
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:annoSeleccionado":  str(anio),
        "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:_idcl":
            "vistaObligacionesPorDocumento:frmObligacionesPorDocumento:lnkBuscarObligaciones"
    })

    resp2 = session.post(search_action, data=payload, headers=headers)
    resp2.raise_for_status()
    soup2 = BeautifulSoup(resp2.text, "html.parser")

    form2 = soup2.find("form", id="vistaObligacionesPorDocumento:frmObligacionesPorDocumento")
    if not form2:
        print(f"⚠️ Año {anio}: no se encontró tabla de resultados.")
        continue

    hidden2 = { inp["name"]: inp.get("value","") for inp in form2.find_all("input") }
    action2 = requests.compat.urljoin(search_url, form2["action"])

    cont_links = soup2.select("a[onclick*='lnkContinuar']")
    print(f"🔁 Año {anio}: encontradas {len(cont_links)} obligaciones.")

    for idx, a in enumerate(cont_links):
        m = re.search(r"value\s*=\s*'([^']+)'", a["onclick"])
        if not m:
            print(f"⚠️ Fila {idx}: no se pudo extraer _idcl.")
            continue
        idcl_value = m.group(1)

        pay_det = hidden2.copy()
        name_idcl = [k for k in pay_det if k.endswith("_idcl")]
        if not name_idcl:
            print("⚠️ No se encontró nombre de campo _idcl.")
            break
        pay_det[name_idcl[0]] = idcl_value

        resp_det = session.post(action2, data=pay_det, headers=headers)
        resp_det.raise_for_status()
        soup_det = BeautifulSoup(resp_det.text, "html.parser")

        form_det = soup_det.find("form", id="vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion")
        if not form_det:
            print(f"⚠️ Obligación {idx}: sin formulario de detalle.")
            continue
        hidden_det = { inp["name"]: inp.get("value","") for inp in form_det.find_all("input") }
        action_det = requests.compat.urljoin(search_url, form_det["action"])

        save_links = soup_det.select("a[onclick*='salvarNumDoc']")
        for sl in save_links:
            m2 = re.search(r"salvarNumDoc\('(\d+)',\s*(\d+),\s*(\d+)\)", sl["onclick"])
            if not m2:
                continue
            num_doc, num_rep, id_formato = m2.groups()

            pay_pdf = hidden_det.copy()
            pay_pdf.update({
                "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddNumDoc":    num_doc,
                "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddNumRep":    num_rep,
                "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:hddIdFormato": id_formato,
            })
            idcl_det = [k for k in pay_pdf if k.endswith("_idcl")]
            pay_pdf[idcl_det[0]] = "vistaLstDocySaldosObligacion:frmLstDocySaldosObligacion:lnkGenerarPdf"

            rpdf = session.post(action_det, data=pay_pdf, headers=headers)
            if rpdf.status_code == 200 and rpdf.headers.get("Content-Type","").startswith("application/pdf"):
                fn = os.path.join(download_dir, f"{num_doc}.pdf")
                with open(fn, "wb") as f:
                    f.write(rpdf.content)
                print(f"✅ [{anio}] PDF {num_doc}.pdf descargado.")
            else:
                print(f"⚠️ [{anio}] Error al bajar PDF {num_doc}: status {rpdf.status_code}")

print(f"\n🎉 Proceso terminado. Revisa los PDFs en `{os.path.abspath(BASE_DOWNLOAD_DIR)}`.")
