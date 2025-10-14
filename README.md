# Declarations Downloader

Script en **Python + Selenium** para automatizar la descarga de declaraciones desde un portal web oficial.
Soporta múltiples **años** y múltiples **tipos de obligación**, definidos en un archivo de configuración local (`var.json`, **no se sube al repositorio**).

Incluye un **anti-idle** que simula la tecla `Ctrl` cada minuto para evitar que el PC se bloquee durante la ejecución.

---

## 🚀 Requisitos

1. **Python 3.10+** instalado.
2. Clonar este repositorio y crear entorno virtual:

   ```bash
   python -m venv venv
   ```
3. Activar el entorno virtual:

   * Windows:

     ```bash
     venv\Scripts\activate
     ```
   * Linux / Mac:

     ```bash
     source venv/bin/activate
     ```
4. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuración

Debes crear un archivo **`var.json`** en la raíz del proyecto (no está en Git, lo manejas localmente).

El contenido define:

* Ruta al ejecutable del driver del navegador.
* Carpeta base donde se guardarán los PDFs.
* Identificación de la entidad a consultar.
* Lista de obligaciones a descargar.
* Rango de años a procesar.

**Importante:** `var.json` contiene información sensible y no debe compartirse.

---

## ▶️ Ejecución

1. Ejecuta el script con:

   ```bash
   venv\Scripts\python.exe script.py
   ```

   o con doble clic en `run.bat`.

2. Si es la **primera vez**:

   * Se abrirá el navegador.
   * Inicia sesión en el portal.
   * Navega hasta la sección de **Obligación Financiera**.
   * Presiona ENTER en consola para continuar.
   * Se guardarán cookies para próximas ejecuciones (**excluidas de Git**).

3. En ejecuciones siguientes:

   * El script intentará reutilizar cookies para saltar el login.
   * Si expiran → deberás iniciar sesión manualmente otra vez.

---

## 📂 Descargas

Los PDFs se guardan en la carpeta configurada en `var.json` (excluida de Git).
La estructura sigue el patrón:

```
descargas/
├── [año]/
│   ├── [tipo_obligacion]/
│   │   ├── documento1.pdf
│   │   └── documento2.pdf
```

---

## 🖥️ Ejemplo de `run.bat`

Crea un archivo `run.bat` en la raíz del proyecto:

```bat
@echo off
setlocal

REM Ir a la carpeta del proyecto
cd /d "%~dp0"

REM Configuración
set VENV_DIR=venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set SCRIPT=script.py

REM Ejecutar script
%PYTHON_EXE% %SCRIPT%

pause
```

Con doble clic en `run.bat` se abrirá la consola, ejecutará el script dentro del entorno virtual y al final se quedará en pausa para mostrar los mensajes.

---

## 🛠 Notas técnicas

* El script incluye un **anti-idle** que simula la tecla `Ctrl` cada minuto para que el PC no se bloquee.
* **No subas** información sensible (`var.json`, cookies, PDFs). Esto ya está protegido en el `.gitignore`.
* El driver del navegador debe estar alineado con la versión instalada de dicho navegador.
