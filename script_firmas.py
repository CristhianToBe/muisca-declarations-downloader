# script_firmas.py
from scraping_utils import config, cookies, navegador
from scraping_utils import scraper_firmas
from bs4 import BeautifulSoup
import os
from requests.compat import urljoin

def main():
    # 1) Cargar configuración
    cfg = config.load_config()
    base_dir = os.path.join(cfg["BASE_DOWNLOAD_DIR"], "firmas")
    os.makedirs(base_dir, exist_ok=True)

    # 2) Cargar cookies previas si existen
    cks = cookies.load()

    # 3) Abrir navegador y capturar driver
    search_url, search_html, cks = navegador.ensure_login(
        cfg["CHROMEDRIVER_PATH"],
        cookies_exist=cks
    )

    # 4) Montar sesión requests con cookies
    session, headers = scraper_firmas.requests.Session(), {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    for c in cks:
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path"))

    # 5) Extraer formulario base de la página
    soup = BeautifulSoup(search_html, "html.parser")
    form = soup.find("form", id="vistaConsultarFirmasDoc:frmConsultarFirmasDoc")
    if not form:
        raise RuntimeError("⚠️ No encontré el formulario de firmas en la página inicial.")
    action_url = urljoin(search_url, form["action"])   # ✅ aquí el cambio
    payload_base = {inp["name"]: inp.get("value","") for inp in form.find_all("input") if inp.get("name")}


    # 6) Iterar sobre formatos y documentos desde var.json
    for formato, documento in zip(cfg["FIRMAS_FORMATOS"], cfg["FIRMAS_DOCUMENTOS"]):
        print(f"\n➡️ Consultando Formato {formato}, Documento {documento}")

        payload = scraper_firmas.build_payload_firmas(payload_base, formato, documento)
        soup, action2, hidden = scraper_firmas.buscar_firmas(session, action_url, payload, headers)

        buttons = scraper_firmas.get_guardar_buttons(soup)
        print(f"   Encontrados {len(buttons)} botones Guardar.")

        for idx, btn in enumerate(buttons):
            btn_name = btn.get("name")
            content = scraper_firmas.descargar_firma(session, action2, soup, btn_name, headers)
            if content:
                fn = os.path.join(base_dir, f"firma_{formato}_{documento}_{idx+1}.xml")
                with open(fn, "wb") as f:
                    f.write(content)
                print(f"   ✅ Guardado {fn}")
    print(f"\n🎉 Proceso terminado. Revisa los PDFs en `{os.path.abspath(base_dir)}`.")

if __name__ == "__main__":
    main()
