from scraping_utils import config, cookies, navegador
from scraping_utils import scraper_firmas
from scraping_utils.documentos_index import discover_from_index
from bs4 import BeautifulSoup
import os
from requests.compat import urljoin


def main():
    cfg = config.load_config()
    base_dir = os.path.join(cfg["BASE_DOWNLOAD_DIR"], "firmas")
    os.makedirs(base_dir, exist_ok=True)

    formatos, documentos = discover_from_index(cfg["BASE_DOWNLOAD_DIR"], cfg["FIRMAS_PREFIJO"])
    if not documentos:
        raise RuntimeError(
            "⚠️ No encontré documentos en documentos_encontrados.json para el prefijo configurado. "
            "Ejecuta primero script_documentos.py."
        )

    print(f"📂 Descubiertos {len(documentos)} documentos con prefijo {cfg['FIRMAS_PREFIJO']}")

    cks = cookies.load()
    search_url, search_html, cks = navegador.ensure_login(
        cfg["CHROMEDRIVER_PATH"],
        cookies_exist=cks
    )

    session, headers = scraper_firmas.requests.Session(), {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    for c in cks:
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path"))

    soup = BeautifulSoup(search_html, "html.parser")
    form = soup.find("form", id="vistaConsultarFirmasDoc:frmConsultarFirmasDoc")
    if not form:
        raise RuntimeError("⚠️ No encontré el formulario de firmas en la página inicial.")
    action_url = urljoin(search_url, form["action"])
    payload_base = {inp["name"]: inp.get("value", "") for inp in form.find_all("input") if inp.get("name")}

    for formato, documento in zip(formatos, documentos):
        print(f"\n➡️ Consultando Formato {formato}, Documento {documento}")

        payload = scraper_firmas.build_payload_firmas(payload_base, formato, documento)
        soup_doc, action2, hidden = scraper_firmas.buscar_firmas(session, action_url, payload, headers)

        buttons = scraper_firmas.get_guardar_buttons(soup_doc)
        print(f"   Encontrados {len(buttons)} botones Guardar.")

        for idx, btn in enumerate(buttons):
            btn_name = btn.get("name")
            content = scraper_firmas.descargar_firma(session, action2, soup_doc, btn_name, headers)
            if content:
                fn = os.path.join(base_dir, f"firma_{formato}_{documento}_{idx + 1}.xml")
                with open(fn, "wb") as f:
                    f.write(content)
                print(f"   ✅ Guardado {fn}")

    print(f"\n🎉 Proceso terminado. Revisa los XML en `{os.path.abspath(base_dir)}`.")


if __name__ == "__main__":
    main()
