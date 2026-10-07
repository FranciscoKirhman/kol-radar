#!/usr/bin/env python3
"""Publica fragmentos por país y área tras validar la barrera legal."""
import argparse
import collections
import datetime
import gzip
import json
import os
from pathlib import Path

import paises
import areas

RAIZ = Path(__file__).resolve().parent.parent
MUESTRA = RAIZ / "data" / "sample" / "perfiles-muestra.json"
DESTINO = RAIZ / "data" / "publicado"


def guardar(ruta, obj):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos = (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    ruta.write_bytes(datos)
    return len(datos), len(gzip.compress(datos, compresslevel=9))


def fragmentos(base, iso):
    entidades = base["entidades"]
    vinculos = base["vinculos"]
    por_id = {e["id"]: e for e in entidades}
    legacy_onco = {d.get("nombre_legacy") for a, d in areas.nodos() if a["id"] == "oncologia"}
    legacy_onco.discard(None)
    ids_basicos = {e["id"] for e in entidades if e["tipo"] != "ensayo_clinico"}
    salida = {}
    for area in areas.cargar():
        aid = area["id"]
        trials = {e["id"] for e in entidades if e["tipo"] == "ensayo_clinico"
                  and (aid in e.get("areas", []) or
                       (aid == "oncologia" and e.get("area") in legacy_onco))}
        ids = set(trials)
        if aid == "oncologia":
            ids |= ids_basicos
        else:
            for v in vinculos:
                if v["destino"] in trials and por_id.get(v["origen"], {}).get("tipo") == "institucion":
                    ids.add(v["origen"])
                if v["origen"] in trials and por_id.get(v["destino"], {}).get("tipo") == "institucion":
                    ids.add(v["destino"])
        salida[aid] = (ids, trials)
    sin_clasificar = {e["id"] for e in entidades if e["tipo"] == "ensayo_clinico"
                       and "areas" in e and not e["areas"]}
    ids = set(sin_clasificar)
    for v in vinculos:
        if v["destino"] in sin_clasificar and por_id.get(v["origen"], {}).get("tipo") == "institucion":
            ids.add(v["origen"])
    salida["sin-clasificar"] = (ids, sin_clasificar)
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pais", default="CL")
    ap.add_argument("--muestra", default=str(MUESTRA))
    ap.add_argument("--destino", default=str(DESTINO))
    a = ap.parse_args()
    iso = a.pais.upper()
    if not paises.permitido_publicar_personas(iso):
        ap.error("El país no tiene aprobación para publicación: " + iso)
    base = json.load(open(a.muestra, encoding="utf-8"))
    problemas = paises.comprobar_publicacion(base)
    if problemas:
        ap.error("Barrera legal: " + "; ".join(problemas[:3]))
    destino = Path(a.destino).resolve()
    por_id = {e["id"]: e for e in base["entidades"]}
    indice_areas = []
    total_gzip = 0
    for aid, (ids, trials) in fragmentos(base, iso).items():
        frag = {"actualizado": base.get("actualizado"), "pais": iso, "area_id": aid,
                "entidades": [e for e in base["entidades"] if e["id"] in ids],
                "vinculos": [v for v in base["vinculos"] if v["origen"] in ids and v["destino"] in ids]}
        if paises.comprobar_publicacion(frag):
            ap.error("Barrera legal en fragmento " + aid)
        ruta = destino / iso / (aid + ".json")
        bruto, comprimido = guardar(ruta, frag)
        total_gzip += comprimido
        indice_areas.append({"id": aid, "nombre": next((x["nombre"] for x in areas.cargar() if x["id"] == aid),
                                                        "Sin clasificar"),
                             "ruta": "../data/publicado/%s/%s.json" % (iso, aid),
                             "entidades": len(frag["entidades"]), "vinculos": len(frag["vinculos"]),
                             "ensayos": len(trials), "bytes": bruto, "gzip_bytes": comprimido})
    pais = paises.configuracion()[iso]
    indice = {"actualizado": datetime.date.today().isoformat(), "version": 1,
              "paises": [{"iso2": iso, "nombre": pais["nombre"], "areas": indice_areas}],
              "area_inicial": "oncologia", "pais_inicial": iso,
              "nota": "Las áreas pueden superponerse. Sin clasificar no significa ausencia de área clínica."}
    guardar(destino / "indice.json", indice)
    print(json.dumps({"pais": iso, "fragmentos": len(indice_areas),
                      "gzip_total_fragmentos": total_gzip,
                      "gzip_inicial_indice_y_oncologia":
                      len(gzip.compress((destino / "indice.json").read_bytes(), compresslevel=9)) +
                      next(x["gzip_bytes"] for x in indice_areas if x["id"] == "oncologia")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
