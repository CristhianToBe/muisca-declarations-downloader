import os

def save_pdf(download_dir, num_doc, content, anio, tipo):
    fn = os.path.join(download_dir, f"{num_doc}.pdf")
    with open(fn, "wb") as f:
        f.write(content)
    print(f"✅ [{anio}] Tipo {tipo} - PDF {num_doc}.pdf descargado.")
