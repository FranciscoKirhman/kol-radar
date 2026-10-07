#!/usr/bin/env python3
"""Prepara ADM1 por país desde geoBoundaries; CL conserva su archivo ADM1/ADM3 legado."""
import argparse
import datetime
import json
from pathlib import Path
import sys
import urllib.request

import pipeline_pais
import preparar_limites_chile as chile


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pais", default="CL")
    ap.add_argument("--salida")
    ap.add_argument("archivos", nargs="*")
    a = ap.parse_args()
    config = pipeline_pais.configurar(a.pais)
    iso = config["iso2"]
    if iso == "CL":
        if len(a.archivos) not in (0, 2):
            ap.error("CL admite ADM1 y ADM3 locales juntos")
        if a.salida:
            chile.SALIDA = str(Path(a.salida).resolve())
        sys.argv = [sys.argv[0]] + a.archivos
        chile.main()
        return
    if len(a.archivos) > 1:
        ap.error("Para otros países solo se admite un archivo ADM1 local")
    codigo = config.get("adm_geoboundaries") or config["iso3"]
    api = "https://www.geoboundaries.org/api/current/gbOpen/%s/ADM1/" % codigo
    licencia, recurso = None, None
    if a.archivos:
        with open(a.archivos[0], encoding="utf-8") as f:
            geo = json.load(f)
        recurso = "copia local de " + Path(a.archivos[0]).name
    else:
        req = urllib.request.Request(api, headers={"User-Agent": chile.USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as r:
            meta = json.load(r)
        licencia = meta.get("boundaryLicense")
        recurso = meta["simplifiedGeometryGeoJSON"]
        with urllib.request.urlopen(urllib.request.Request(recurso, headers={"User-Agent": chile.USER_AGENT}), timeout=300) as r:
            geo = json.load(r)
    divisiones = [{"nombre": f["properties"]["shapeName"],
                   "anillos": chile.anillos_de(f["geometry"], chile.TOL_REGION)}
                  for f in geo["features"]]
    datos = {"pais": iso, "nivel": "ADM1", "divisiones": divisiones,
             "regiones": divisiones, "comunas": [], "fuente": "geoBoundaries gbOpen",
             "fuente_url": api, "licencia": licencia, "recursos": [recurso],
             "fecha": datetime.date.today().isoformat(),
             "nota": "ADM1 simplificado para dibujo. Licencia desconocida si se usó un archivo local sin metadatos."}
    salida = Path(a.salida or pipeline_pais.RAIZ / "data" / "geo" / (iso.lower() + "-adm1.json"))
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, separators=(",", ":"))
    print("%s: %d divisiones ADM1 → %s" % (iso, len(divisiones), salida))


if __name__ == "__main__":
    main()
