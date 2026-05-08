import json
import os
from typing import Dict, List


def save_documentos_index(base_dir: str, docs_index: Dict[str, List[str]]) -> str:
    index_path = os.path.join(base_dir, "documentos_encontrados.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(docs_index, f, ensure_ascii=False, indent=2)
    return index_path


def load_documentos_index(base_dir: str) -> Dict[str, List[str]]:
    index_path = os.path.join(base_dir, "documentos_encontrados.json")
    if not os.path.exists(index_path):
        return {}
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_from_index(base_dir: str, prefijo: str):
    data = load_documentos_index(base_dir)
    formatos = []
    documentos = []
    prefijo = str(prefijo)
    formato = int(prefijo)

    for docs in data.values():
        for doc in docs:
            doc_str = str(doc)
            if doc_str.startswith(prefijo):
                formatos.append(formato)
                documentos.append(int(doc_str))
    return formatos, documentos
