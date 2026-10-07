#!/usr/bin/env python3
"""Agrega identificadores confirmados por fuente primaria sin fusionar entidades."""
import argparse
import collections
import datetime
import json
import os
import re
import urllib.parse
import urllib.request

import exclusiones
import normalizar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
ORCID = re.compile(r"^https://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])$")


def api(url, accept=None):
    cabeceras = {"User-Agent": "kol-radar-identifier-audit"}
    if accept:
        cabeceras["Accept"] = accept
    with urllib.request.urlopen(urllib.request.Request(url, headers=cabeceras), timeout=30) as respuesta:
        return json.load(respuesta)


def hecho(e, tipo, valor, url, fecha):
    if any(h.get("tipo") == "identificador" and h.get("fuente_url") == url for h in e.get("hechos", [])):
        return
    e.setdefault("hechos", []).append({"tipo": "identificador", "hecho": "%s: %s" % (tipo, valor),
                                        "fuente_url": url, "fecha": fecha, "confianza": "pendiente"})


def enriquecer(base, fecha):
    stats = collections.Counter()
    propuestas = []
    for e in base["entidades"]:
        if e["tipo"] != "institucion" or e.get("ror_id"):
            continue
        url = "https://api.ror.org/v2/organizations?" + urllib.parse.urlencode({"query": e["nombre"]})
        items = api(url).get("items", [])
        exactos = [i for i in items if i.get("status") == "active"
                   and any(normalizar.norm(n["value"]) == normalizar.norm(e["nombre"])
                           and ("label" in n.get("types", []) or "ror_display" in n.get("types", []))
                           for n in i.get("names", []))
                   and any(l.get("geonames_details", {}).get("country_code") == "CL"
                           for l in i.get("locations", []))]
        if len(exactos) == 1:
            rid = exactos[0]["id"]
            e["ror_id"] = rid
            hecho(e, "ROR", rid, rid, fecha)
            stats["ror"] += 1
        else:
            propuestas.append({"institucion_id": e["id"], "resultado": "sin_correspondencia_exacta"
                               if not exactos else "ambiguo", "candidatos": [i["id"] for i in exactos]})

    for e in base["entidades"]:
        if e["tipo"] != "persona":
            continue
        propios = sorted({m.group(1) for h in e.get("hechos", [])
                          for m in [ORCID.match(h.get("fuente_url", ""))] if m})
        if len(propios) != 1:
            continue
        oid = propios[0]
        url_orcid = "https://orcid.org/" + oid
        persona = api("https://pub.orcid.org/v3.0/" + oid + "/person", "application/json")
        nombres = [persona.get("name", {}).get("credit-name", {}).get("value"),
                   " ".join((persona.get("name", {}).get("given-names", {}).get("value") or "",
                             persona.get("name", {}).get("family-name", {}).get("value") or ""))]
        nombres += [n.get("content") for n in persona.get("other-names", {}).get("other-name", [])]
        if normalizar.norm(e["nombre"]) not in {normalizar.norm(n) for n in nombres if n}:
            propuestas.append({"persona_id": e["id"], "resultado": "nombre_orcid_no_exacto", "orcid": oid})
            continue
        e["orcid"] = oid
        hecho(e, "ORCID", oid, url_orcid, fecha)
        stats["orcid"] += 1
        url_oa = "https://api.openalex.org/authors?" + urllib.parse.urlencode(
            {"filter": "orcid:" + url_orcid, "per-page": "10"})
        autores = [a for a in api(url_oa).get("results", []) if a.get("orcid") == url_orcid]
        if len(autores) == 1:
            e["openalex_id"] = autores[0]["id"]
            hecho(e, "OpenAlex", autores[0]["id"], autores[0]["id"], fecha)
            stats["openalex"] += 1
        elif autores:
            propuestas.append({"persona_id": e["id"], "resultado": "openalex_ambiguo",
                               "candidatos": [a["id"] for a in autores]})
    return stats, propuestas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", default=MUESTRA)
    ap.add_argument("--salida", default=MUESTRA)
    ap.add_argument("--propuestas", default=os.path.join(RAIZ, "data", "pending", "CL", "identificadores-2026-10-07.json"))
    args = ap.parse_args()
    fecha = datetime.date.today().isoformat()
    base = json.load(open(args.muestra, encoding="utf-8"))
    stats, propuestas = enriquecer(base, fecha)
    exclusiones.guardar_muestra(base, args.salida, exclusiones.Registro())
    os.makedirs(os.path.dirname(args.propuestas), exist_ok=True)
    with open(args.propuestas, "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "estado": "propuestas no aplicadas", "propuestas": propuestas},
                  f, ensure_ascii=False, indent=2)
    print(json.dumps({"agregados": dict(stats), "propuestas": len(propuestas)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
