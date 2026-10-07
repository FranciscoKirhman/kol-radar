#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recolecta el buscador de estudios clínicos de la Cámara de la Innovación Farmacéutica (CIF).

https://estudiosclinicos.cl publica, por cada ensayo que un laboratorio socio tiene reclutando en
Chile, su NCT, el laboratorio, la fase y la lista de ciudades con los centros abiertos. Es la
fuente que nombra los centros que ClinicalTrials.gov oculta detrás de "Research Site" o
"Local Institution": el patrocinador enmascara la sede en el registro internacional, pero la
declara en el buscador chileno.

Qué guarda: URL de la ficha, NCT, laboratorio, fase, código de estudio, estado, y cada par
(ciudad, centro) tal como lo escribe la página. Qué NO guarda: el correo o teléfono de contacto
para inscribirse, que es de una persona del laboratorio y no tiene nada que hacer acá.

robots.txt del sitio: "User-agent: * / Disallow:" (sin restricciones). Igual se pide una página
cada 1,5 segundos.

Uso:  python3 scripts/recolectar_estudiosclinicos_cl.py [carpeta_cache_html]
"""
import argparse
import datetime
import html
import json
import os
import re
import sys
import time
import urllib.request
import pipeline_pais

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FECHA = datetime.date.today().isoformat()
SALIDA = os.path.join(RAIZ, "data", "pending", "estudiosclinicos-cl-" + FECHA)
SITEMAP = "https://estudiosclinicos.cl/estudios-sitemap.xml"
AGENTE = "KOL-Radar/1.0 (+https://github.com/FranciscoKirhman/kol-radar)"


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


def texto(fragmento):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def leer_ficha(url, h):
    nct = re.search(r"(NCT\d{8})", h)
    ficha = {"url": url, "nct": nct.group(1) if nct else None}
    m = re.search(r"<h1>(.*?)</h1>\s*<span>Estado:\s*(.*?)</span>\s*<p>(.*?)</p>", h, re.S)
    if m:
        ficha["area_en_la_fuente"] = texto(m.group(1))
        ficha["estado"] = texto(m.group(2))
        ficha["titulo"] = texto(m.group(3))
    for etiqueta, clave in (("Laboratorio", "laboratorio"), ("Fase del estudio", "fase"),
                            ("Código de Estudio", "codigo"), ("Área Terapéutica", "area_terapeutica")):
        m = re.search(r"<span>" + etiqueta + r":</span><span>(.*?)</span>", h, re.S)
        ficha[clave] = texto(m.group(1)) if m else None
    sitios = []
    bloque = h.split("page__single__ciudades", 1)
    if len(bloque) == 2:
        for ciudad, lista in re.findall(r'--item-ciudad">\s*<div>\s*<span>(.*?)</span>\s*<ul>(.*?)</ul>', bloque[1], re.S):
            for centro in re.findall(r"<li>(.*?)</li>", lista, re.S):
                sitios.append({"ciudad": texto(ciudad), "centro": texto(centro)})
    ficha["sitios"] = sitios
    return ficha


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cache", nargs="?")
    ap.add_argument("--pais", default="CL")
    a = ap.parse_args()
    pipeline_pais.exigir_fuente_chilena(a.pais, "CIF")
    cache = a.cache
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", bajar(SITEMAP)) if u.rstrip("/") != "https://estudiosclinicos.cl/ensayos"]
    fichas = []
    for i, url in enumerate(urls):
        ruta = os.path.join(cache, re.sub(r"[^a-z0-9]+", "_", url.lower()) + ".html") if cache else None
        if ruta and os.path.exists(ruta):
            h = open(ruta, encoding="utf-8").read()
        else:
            h = bajar(url)
            if ruta:
                open(ruta, "w", encoding="utf-8").write(h)
            time.sleep(1.5)
        fichas.append(leer_ficha(url, h))
        if i % 25 == 0:
            print(i, len(urls), url, flush=True)
    os.makedirs(SALIDA, exist_ok=True)
    doc = {"fuente": "https://estudiosclinicos.cl/", "editor": "Cámara de la Innovación Farmacéutica (CIF)",
           "fecha_consulta": FECHA, "nota": "No se guardan los contactos de inscripción de cada ficha.",
           "fichas": fichas}
    json.dump(doc, open(os.path.join(SALIDA, "fichas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(fichas), "fichas;", sum(1 for f in fichas if f["nct"]), "con NCT;",
          sum(len(f["sitios"]) for f in fichas), "pares ciudad-centro")


if __name__ == "__main__":
    main()
