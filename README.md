# Declaraciones - Scraper DIAN

Este proyecto automatiza la descarga de obligaciones financieras desde el portal **MUISCA de la DIAN**.  
El flujo combina **Selenium** (para login manual y captura de cookies) con **Requests + BeautifulSoup** (para navegar formularios y descargar PDFs).

---

## 🚀 Requisitos

- **Python 3.10+**
- Google Chrome instalado
- `chromedriver.exe` correspondiente a tu versión de Chrome
- Archivo de configuración `var.json` en el raíz con esta estructura:

```json
{
    "CHROMEDRIVER_PATH": "chromedriver.exe",
    "BASE_DOWNLOAD_DIR": "descargas",
    "NIT": "123456789",
    "TIPO_OBLIGACION": ["01", "21"],
    "ANIO_INICIO": 2020,
    "ANIO_FIN": 2024
}

▶️ Uso rápido en Windows

Ejecuta el archivo `run.bat`:
```bash
run.bat

La primera vez, abre Chrome y haz login manualmente hasta la pestaña Obligación Financiera.

El sistema guardará las cookies automáticamente.

En ejecuciones posteriores, las cookies se reutilizan y el flujo continúa sin login.

Los PDFs descargados se guardan en la carpeta indicada en var.json (por defecto descargas/).

📂 Estructura del proyecto

php
Copiar código
Declaraciones/
├── descargas/            # PDFs descargados
├── scraping_utils/       # Módulos reutilizables
│   ├── anti_idle.py      # Previene que la sesión se cierre
│   ├── config.py         # Carga y normaliza la configuración desde var.json
│   ├── cookies.py        # Maneja carga/guardado de cookies
│   ├── navegador.py      # Selenium: abre Chrome, inyecta cookies y captura HTML
│   ├── scraper.py        # Lógica de requests + BeautifulSoup (payloads, parsing)
│   └── downloader.py     # Guarda PDFs en disco
├── script.py             # Orquestador principal del flujo
├── run.bat               # Ejecución rápida en Windows
├── requirements.txt      # Dependencias
├── var.json              # Configuración
└── README.md

📘 Descripción de cada módulo

script.py → el orquestador. Ejecuta todo el proceso de forma secuencial.

anti_idle.py → lanza un hilo que presiona Ctrl cada minuto para evitar que la sesión expire por inactividad.

config.py → carga var.json y devuelve la configuración normalizada (rutas, años, tipos de obligación, NIT).

cookies.py → abstrae el manejo de cookies.pkl (guardar y cargar cookies de sesión).

navegador.py → controla Selenium:

Abre Chrome.

Inyecta cookies si existen.

Pide login manual si no hay cookies válidas.

Captura HTML y cookies actualizadas.

scraper.py → funciones para scraping con requests:

Construye la sesión con cookies y headers.

Extrae formularios y payloads.

Ejecuta consultas de obligaciones.

Itera y obtiene enlaces a PDFs.

downloader.py → recibe el contenido de los PDFs y los guarda en el directorio correspondiente, con nombres organizados por año y tipo de obligación.

📝 Notas

El login es manual: no se automatiza usuario/contraseña.

Si cambia la versión de Chrome, actualiza chromedriver.exe.

Si quieres reiniciar sesión, borra el archivo cookies.pkl.

