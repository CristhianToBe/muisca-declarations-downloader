# Scraper MUISCA DIAN

Este proyecto automatiza la descarga de PDFs de obligaciones financieras desde el portal MUISCA de la DIAN usando Selenium y Requests.

---

## 🚀 Estructura

- `script.py` → flujo principal de ejecución.
- `script_documentos.py` → extrae solo números de documento (sin descargar PDFs).
- `script_firmas_index.py` → descarga XML de firmas usando `documentos_encontrados.json`.
- `scraping_utils/`
  - `config.py` → carga variables desde `var.json`.
  - `anti_idle.py` → mantiene el PC activo.
  - `cookies.py` → maneja cookies de sesión.
  - `navegador.py` → abre Selenium y gestiona login manual.
  - `scraper.py` → funciones para armar payloads, buscar obligaciones y descargar PDFs.
  - `downloader.py` → guarda PDFs en carpetas organizadas.

---

## ⚙️ Configuración

En `var.json` defines:

```json
{
  "CHROMEDRIVER_PATH": "ruta/a/chromedriver.exe",
  "BASE_DOWNLOAD_DIR": "descargas",
  "NIT": "123456789",
  "TIPO_OBLIGACION": ["1007", "1001"],
  "ANIO_INICIO": 2023,
  "ANIO_FIN": 2024,
  "PERIODO": [1, 12]
}
```

### Notas sobre `PERIODO`:
- Un número → solo ese periodo (`"PERIODO": 5`).
- Una lista con dos números → rango inclusivo (`"PERIODO": [1, 12]`).
- Una lista con varios → periodos específicos (`"PERIODO": [1, 3, 5]`).

---

## 🔑 Uso

1. Ejecuta el script con el `.bat` (o directamente con `python script.py`).
2. Se abrirá Chrome con Selenium y deberás **iniciar sesión manualmente en MUISCA**.
3. **Muy importante:** cuando llegues a la pestaña **Obligación Financiera**, **selecciona el impuesto en el menú desplegable** antes de presionar ENTER en la consola.
4. El script tomará la página actual como base y empezará a recorrer años, tipos y periodos, descargando los PDFs.
5. Los archivos quedarán organizados en:  
   ```
   descargas/
     └── 2024/
         └── 1007/
             └── periodo_1/
                 └── xxxx.pdf
   ```

### Flujo alterno solicitado (sin PDFs)

1. Ejecuta `python script_documentos.py` para generar:
   - `BASE_DOWNLOAD_DIR/documentos_encontrados.json`
2. Ejecuta `python script_firmas_index.py` para descargar solo XML de firmas
   usando ese índice de documentos.

---

## 📝 Notas
- Si ya tienes cookies guardadas (`cookies.pkl`), se intentarán reutilizar.
- Si cambias de navegador o vencen las cookies, deberás iniciar sesión de nuevo.
- El script usa `anti_idle.py` para evitar que el equipo se bloquee durante la ejecución.
