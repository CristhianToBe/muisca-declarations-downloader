import time
from bs4 import BeautifulSoup

def get_all_pages(driver, delay: int = 2):
    """
    Recorre automáticamente un paginador con botones 'Siguiente'
    y devuelve una lista de HTMLs de todas las páginas.

    Parámetros
    ----------
    driver : selenium.webdriver.Chrome
        Instancia activa de Selenium ya posicionada en la primera página de resultados.
    delay : int, opcional
        Segundos a esperar después de hacer clic en 'Siguiente' (por defecto 2).

    Retorna
    -------
    list[str]
        Lista de strings, cada uno es el HTML de una página.
    """
    all_pages_html = []

    while True:
        # Guardar HTML actual
        html = driver.page_source
        all_pages_html.append(html)

        try:
            # Ubicar el botón "Siguiente"
            next_btn = driver.find_element("xpath", "//a[contains(text(),'Siguiente')]")

            # Si está deshabilitado, terminar
            if "ui-state-disabled" in next_btn.get_attribute("class"):
                break

            # Ir a la siguiente página
            next_btn.click()
            time.sleep(delay)

        except Exception:
            break

    return all_pages_html


def extract_obligations_from_html(html: str):
    """
    Extrae los links de obligaciones desde un HTML.

    Parámetros
    ----------
    html : str
        Contenido HTML de una página.

    Retorna
    -------
    list[bs4.element.Tag]
        Lista de nodos <a> encontrados que contienen 'lnkContinuar'.
    """
    soup = BeautifulSoup(html, "html.parser")
    cont_links = soup.select("a[onclick*='lnkContinuar']")
    return cont_links

def iterate_pages(driver, delay: int = 2):
    """
    Itera sobre todas las páginas de resultados en el paginador.
    Devuelve un generador de objetos BeautifulSoup (cada página).
    """
    while True:
        html = driver.page_source
        yield BeautifulSoup(html, "html.parser")

        try:
            next_btn = driver.find_element("xpath", "//a[contains(text(),'Siguiente')]")
            if "ui-state-disabled" in next_btn.get_attribute("class"):
                break
            next_btn.click()
            time.sleep(delay)
        except Exception:
            break