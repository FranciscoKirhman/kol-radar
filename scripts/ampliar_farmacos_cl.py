#!/usr/bin/env python3
"""Incorpora fármacos regenerados sin borrar fichas, hechos ni vínculos publicados.

Uso: KOL_MUESTRA=/tmp/candidatos.json python3 scripts/integrar_farmacos_ctgov.py
     python3 scripts/ampliar_farmacos_cl.py /tmp/candidatos.json
"""
import collections
import datetime
import json
import sys
from pathlib import Path

import exclusiones

RAIZ = Path(__file__).resolve().parent.parent
MUESTRA = RAIZ / "data/sample/perfiles-muestra.json"
FECHA = datetime.date.today().isoformat()


def incluir_sin_repetir(destino, candidatos):
    vistos = set(destino)
    for valor in candidatos:
        if valor not in vistos:
            destino.append(valor)
            vistos.add(valor)


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: ampliar_farmacos_cl.py candidatos.json")
    registro = exclusiones.Registro()
    base = json.loads(MUESTRA.read_text(encoding="utf-8"))
    candidatos = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    existentes = {e["id"]: e for e in base["entidades"]}
    farmacos_anteriores = sum(e["tipo"] == "farmaco" for e in base["entidades"])
    ensayos = {e["id"] for e in base["entidades"] if e["tipo"] == "ensayo_clinico"}
    por_nombre = collections.defaultdict(list)
    for e in base["entidades"]:
        if e["tipo"] == "farmaco":
            por_nombre[e["nombre"].casefold().strip()].append(e)
    equivalencias = {}
    nuevos = nuevos_hechos = 0
    nuevos_ids = []
    for f in [e for e in candidatos["entidades"] if e["tipo"] == "farmaco"]:
        anterior = existentes.get(f["id"])
        if anterior and anterior["tipo"] != "farmaco":
            sys.exit("ID de fármaco en uso por otra entidad: " + f["id"])
        if not anterior:
            iguales = por_nombre[f["nombre"].casefold().strip()]
            if len(iguales) == 1:
                anterior = iguales[0]
        if anterior:
            equivalencias[f["id"]] = anterior["id"]
            claves = {(h.get("tipo"), h.get("fuente_url")) for h in anterior.get("hechos", [])}
            for h in f.get("hechos", []):
                clave = (h.get("tipo"), h.get("fuente_url"))
                if clave not in claves:
                    anterior.setdefault("hechos", []).append(h)
                    claves.add(clave)
                    nuevos_hechos += 1
            for campo in ("areas", "patrocinadores", "alias_en_la_fuente"):
                if f.get(campo):
                    incluir_sin_repetir(anterior.setdefault(campo, []), f[campo])
        else:
            equivalencias[f["id"]] = f["id"]
            base["entidades"].append(f)
            existentes[f["id"]] = f
            por_nombre[f["nombre"].casefold().strip()].append(f)
            nuevos += 1
            nuevos_ids.append(f["id"])
    claves_v = {(v.get("origen"), v.get("destino"), v.get("tipo")) for v in base["vinculos"]}
    nuevos_v = 0
    for v in candidatos["vinculos"]:
        if v.get("tipo") != "intervención":
            continue
        origen = v["origen"]
        destino = equivalencias.get(v["destino"])
        if origen not in ensayos or not destino:
            sys.exit("Vínculo a entidad ausente: " + repr(v))
        clave = (origen, destino, "intervención")
        if clave in claves_v:
            continue
        nuevo = dict(v, destino=destino, fuente_url="https://clinicaltrials.gov/study/" + origen.upper(),
                     fecha=FECHA, confianza="pendiente")
        base["vinculos"].append(nuevo)
        claves_v.add(clave)
        nuevos_v += 1
    base["actualizado"] = FECHA
    exclusiones.guardar_muestra(base, str(MUESTRA), registro)
    salida = RAIZ / "data/pending/CL" / ("farmacos-nuevos-" + FECHA + ".json")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(nuevos_ids, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"farmacos_anteriores": farmacos_anteriores,
                      "farmacos_nuevos": nuevos, "hechos_nuevos_en_farmacos_existentes": nuevos_hechos,
                      "vinculos_nuevos": nuevos_v}, ensure_ascii=False))


if __name__ == "__main__":
    main()
