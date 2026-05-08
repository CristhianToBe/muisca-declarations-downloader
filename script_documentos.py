from scraping_utils import config, anti_idle, cookies, navegador, scraper
from scraping_utils.documentos_index import save_documentos_index
import os
import re
from bs4 import BeautifulSoup


def get_documentos(session, action2, hidden2, idcl_value, headers):
    pay_det = hidden2.copy()
    name_idcl = [k for k in pay_det if k.endswith("_idcl")]
    if not name_idcl:
        return []

    pay_det[name_idcl[0]] = idcl_value
    resp_det = session.post(action2, data=pay_det, headers=headers)
    soup_det = BeautifulSoup(resp_det.text, "html.parser")

    documentos = []
    save_links = soup_det.select("a[onclick*='salvarNumDoc']")
    for sl in save_links:
        m2 = re.search(r"salvarNumDoc\('(\d+)',\s*(\d+),\s*(\d+)\)", sl["onclick"])
        if not m2:
            continue
        num_doc, _, _ = m2.groups()
        documentos.append(num_doc)

    return documentos


def main():
    anti_idle.start()
    cfg = config.load_config()
    base_dir = cfg["BASE_DOWNLOAD_DIR"]
    os.makedirs(base_dir, exist_ok=True)

    cks = cookies.load()
    search_url, search_html, cks = navegador.ensure_login(
        cfg["CHROMEDRIVER_PATH"],
        cookies_exist=cks
    )
    session, headers = scraper.make_session(cks, search_url)

    docs_index = {}

    for anio in range(cfg["ANIO_INICIO"], cfg["ANIO_FIN"] + 1):
        print(f"\n📅 Procesando año {anio}...")

        for tipo in cfg["TIPOS_OBLIGACION"]:
            for periodo in cfg["PERIODOS"]:
                print(f"   ➡️ Procesando tipo {tipo}, periodo {periodo}...")

                payload_base, search_action = scraper.extract_payload(search_html, search_url)
                payload = scraper.build_payload(payload_base, cfg["NIT"], tipo, anio, periodo)

                soup2, hidden2, action2 = scraper.buscar_obligaciones(session, search_action, payload, headers)
                if not soup2:
                    print(f"⚠️ Año {anio}, tipo {tipo}, periodo {periodo}: sin resultados.")
                    continue

                obligaciones = scraper.get_obligaciones(soup2)
                print(f"🔁 Año {anio}, tipo {tipo}, periodo {periodo}: {len(obligaciones)} obligaciones encontradas.")

                key = f"{anio}|{tipo}|{periodo}"
                docs_index[key] = []

                for ob in obligaciones:
                    documentos = get_documentos(session, action2, hidden2, ob, headers)
                    docs_index[key].extend(documentos)
                    for num_doc in documentos:
                        print(f"✅ [{anio}] Tipo {tipo} - Documento {num_doc} encontrado.")

                docs_index[key] = sorted(set(docs_index[key]))

    index_path = save_documentos_index(base_dir, docs_index)
    print(f"\n🎉 Proceso terminado. Revisa los documentos en `{os.path.abspath(index_path)}`.")


if __name__ == "__main__":
    main()
