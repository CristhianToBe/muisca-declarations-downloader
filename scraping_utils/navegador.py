from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pickle

def iniciar_driver(chromedriver_path, headless=False):
    opts = webdriver.ChromeOptions()
    if not headless:
        opts.add_argument("--start-maximized")
    opts.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2
    })
    opts.page_load_strategy = "eager"
    return webdriver.Chrome(service=Service(chromedriver_path), options=opts)

def ensure_login(chromedriver_path, cookies_exist=None):
    """
    Abre Chrome con Selenium.
    - Si hay cookies, las inyecta y refresca.
    - Si no, pide login manual hasta 'Obligación Financiera'.
    Retorna: (search_url, search_html, cookies)
    """
    driver = iniciar_driver(chromedriver_path)
    driver.get("https://muisca.dian.gov.co/")

    if cookies_exist:
        driver.delete_all_cookies()
        for c in cookies_exist:
            cookie_dict = {"name": c["name"], "value": c["value"]}
            if "domain" in c and c["domain"]:
                cookie_dict["domain"] = c["domain"]
            if "path" in c and c["path"]:
                cookie_dict["path"] = c["path"]
            driver.add_cookie(cookie_dict)
        driver.refresh()
        print("♻️ Cookies cargadas, revisa si entraste directo al portal.")

    input("🔐 Navega hasta la pestaña 'Obligación Financiera' y pulsa ENTER…")

    search_url = driver.current_url
    search_html = driver.page_source
    cookies = driver.get_cookies()
    driver.quit()

    # Guardar cookies nuevas
    with open("cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)

    print("✅ Cookies actualizadas y HTML listo.")
    return search_url, search_html, cookies
