from scraping_utils import config, anti_idle, cookies, navegador, scraper, downloader
import os

def main():
    # 1) Anti-idle
    anti_idle.start()

    # 2) Cargar configuración
    cfg = config.load_config()
    base_dir = cfg["BASE_DOWNLOAD_DIR"]
    os.makedirs(base_dir, exist_ok=True)

    # 3) Cargar cookies previas si existen
    cks = cookies.load()

    # 4) Abrir navegador y capturar HTML + cookies si no hay cookies válidas
    search_url, search_html, cks = navegador.ensure_login(
        cfg["CHROMEDRIVER_PATH"],
        cookies_exist=cks
    )

    # 5) Montar sesión requests con cookies
    session, headers = scraper.make_session(cks, search_url)

    # 6) Extraer payload base del formulario
    payload_base, search_action = scraper.extract_payload(search_html, search_url)

    # 7) Bucle Años × Tipos de obligación
    for anio in range(cfg["ANIO_INICIO"], cfg["ANIO_FIN"] + 1):
        print(f"\n📅 Procesando año {anio}...")

        for tipo in cfg["TIPOS_OBLIGACION"]:
            print(f"   ➡️ Procesando tipo obligación {tipo}...")

            download_dir = os.path.join(base_dir, str(anio), tipo)
            os.makedirs(download_dir, exist_ok=True)

            # Preparar payload
            payload = scraper.build_payload(payload_base, cfg["NIT"], tipo, anio)

            # Consultar obligaciones
            soup2, hidden2, action2 = scraper.buscar_obligaciones(session, search_action, payload, headers)
            if not soup2:
                continue

            # Iterar obligaciones y descargar PDFs
            obligaciones = scraper.get_obligaciones(soup2)
            print(f"🔁 Año {anio} Tipo {tipo}: encontradas {len(obligaciones)} obligaciones.")

            for idx, ob in enumerate(obligaciones):
                pdfs = scraper.get_pdfs(session, action2, hidden2, ob, headers)
                for num_doc, content in pdfs:
                    downloader.save_pdf(download_dir, num_doc, content, anio, tipo)

    print(f"\n🎉 Proceso terminado. Revisa los PDFs en `{os.path.abspath(base_dir)}`.")

if __name__ == "__main__":
    main()
