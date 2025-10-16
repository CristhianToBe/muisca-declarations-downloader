import tkinter as tk
from tkinter import filedialog, messagebox
import json
import subprocess
import os

VAR_FILE = "var.json"

# Campos básicos del JSON
DEFAULT_FIELDS = {
    "CHROMEDRIVER_PATH": "",
    "BASE_DOWNLOAD_DIR": "descargas",
    "NIT": "",
    "TIPO_OBLIGACION": ["1007"],
    "ANIO_INICIO": 2024,
    "ANIO_FIN": 2024,
    "PERIODO": [1],
    "FIRMAS_PREFIJO": 410
}

class App:
    def __init__(self, root):
        self.root = root
        root.title("Scraper MUISCA")

        # Cargar JSON existente si hay
        if os.path.exists(VAR_FILE):
            with open(VAR_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = DEFAULT_FIELDS.copy()

        # Selector de script
        self.script_choice = tk.StringVar(value="obligaciones")
        tk.Label(root, text="Selecciona el script:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Radiobutton(root, text="Obligaciones", variable=self.script_choice, value="obligaciones").pack(anchor="w", padx=20)
        tk.Radiobutton(root, text="Firmas", variable=self.script_choice, value="firmas").pack(anchor="w", padx=20)

        # Campos dinámicos
        self.entries = {}
        for key, val in self.config.items():
            frame = tk.Frame(root)
            frame.pack(fill="x", padx=10, pady=2)

            tk.Label(frame, text=key, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(frame)
            entry.insert(0, str(val))
            entry.pack(side="left", fill="x", expand=True)
            self.entries[key] = entry

        # Botón aceptar
        tk.Button(root, text="Aceptar", command=self.run).pack(pady=15)

    def run(self):
        # Guardar valores en var.json
        new_config = {}
        for key, entry in self.entries.items():
            text = entry.get().strip()
            try:
                new_config[key] = json.loads(text)  # intenta parsear listas/números
            except:
                new_config[key] = text  # si falla, lo guarda como string

        with open(VAR_FILE, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)

        # Seleccionar script
        if self.script_choice.get() == "obligaciones":
            script = "script.py"
        else:
            script = "script_firmas.py"

        # Ejecutar script
        try:
            subprocess.run(["python", script], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"El script falló:\n{e}")
            return

        messagebox.showinfo("Éxito", f"Se ejecutó correctamente {script}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
