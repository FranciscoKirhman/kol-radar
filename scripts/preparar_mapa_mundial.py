#!/usr/bin/env python3
"""Convierte Natural Earth 1:110m en trazados SVG livianos por país."""
import argparse
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = "https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson"


def trazado(geometria):
    poligonos = ([geometria["coordinates"]] if geometria["type"] == "Polygon"
                 else geometria["coordinates"])
    partes = []
    for poligono in poligonos:
        for anillo in poligono:
            if not anillo:
                continue
            ruta = []
            previo = None
            for lon, lat in anillo:
                x, y = (lon + 180) * 2, (90 - lat) * 2
                cmd = "M" if previo is None or abs(lon - previo) > 180 else "L"
                ruta.append("%s%.1f %.1f" % (cmd, x, y))
                previo = lon
            partes.append(" ".join(ruta) + " Z")
    return " ".join(partes)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--geojson", required=True)
    ap.add_argument("--salida", default=str(RAIZ / "data" / "geo" / "mundo-paises.json"))
    a = ap.parse_args()
    bruto = Path(a.geojson).read_bytes()
    geo = json.loads(bruto)
    paises = []
    for f in geo["features"]:
        p = f["properties"]
        iso = p.get("ISO_A2_EH") or p.get("ISO_A2")
        if not iso or len(iso) != 2 or iso == "-99":
            continue
        paises.append({"iso2": iso, "nombre": p.get("NAME_ES") or p.get("NAME"),
                       "trazado": trazado(f["geometry"])})
    salida = {"fuente_url": FUENTE, "licencia_url": "https://www.naturalearthdata.com/about/terms-of-use/",
              "sha256_descarga": hashlib.sha256(bruto).hexdigest(), "vista": "equirectangular 720×360",
              "paises": paises}
    Path(a.salida).write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")) + "\n")
    print("%d polígonos de países → %s" % (len(paises), a.salida))


if __name__ == "__main__":
    main()
