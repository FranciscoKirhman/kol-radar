"""Taxonomía MeSH y asignación desde condiciones/descriptores declarados por la fuente."""
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(RAIZ, "data", "config", "areas.json")


def cargar():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)["areas"]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto or "").casefold()
    return re.sub(r"\s+", " ", "".join(c for c in texto if unicodedata.category(c) != "Mn")).strip()


def nodos():
    for area in cargar():
        for enfermedad in area["enfermedades"]:
            yield area, enfermedad


def desde_condiciones(condiciones):
    """No consulta títulos: exige término MeSH o consulta en una condición de CT.gov."""
    declaradas = [normalizar(c) for c in condiciones or []]
    salida = []
    for area, enfermedad in nodos():
        terminos = (enfermedad["mesh_label"], enfermedad["consulta_ctgov"])
        if any(normalizar(t) in c for c in declaradas for t in terminos):
            salida.append((area, enfermedad))
    return salida


def desde_mesh(descriptores):
    """PubMed: IDs MeSH declarados explícitamente; no analiza el título."""
    ids = set(descriptores or [])
    return [(a, e) for a, e in nodos() if e["mesh_id"] in ids]
