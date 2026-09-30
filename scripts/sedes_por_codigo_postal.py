#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ubica sedes enmascaradas de ClinicalTrials.gov por el código postal que la propia fuente declara.

Muchos ensayos de la industria esconden el nombre de la sede ("Research Site", "Novartis
Investigative Site", "Local Institution"), pero ClinicalTrials.gov publica igual su ciudad y su
código postal. Si ese código postal es el mismo que la fuente declara, en otros ensayos, para un
centro con nombre, la sede enmascarada es muy probablemente ese centro.

Es una INFERENCIA, no una declaración de la fuente, y se trata como tal:
  1. Solo códigos postales específicos (7 dígitos que no terminan en 0000: esos son genéricos de
     ciudad, como 1240000 para Antofagasta).
  2. El centro tiene que aparecer con ese código en al menos 2 registros con nombre, y concentrar al
     menos el 90% de los registros con nombre de ese código. Si dos centros lo comparten (Bradford Hill
     y CIEC en 8420383), no se asigna: puede ser el mismo edificio y no se sabe cuál.
  3. Solo para ensayos que no tienen ninguna institución.
  4. El vínculo lleva "criterio": "codigo_postal", el texto enmascarado de la fuente y la URL del
     ensayo, y la ficha del ensayo recibe un hecho que explica la inferencia con los registros que la
     sostienen. La interfaz lo muestra como "sede inferida por código postal".
  5. Nada se confirma: todo entra `pendiente`. Correrlo dos veces no cambia nada.

Uso:  python3 scripts/sedes_por_codigo_postal.py [--ubicaciones archivo.json]
"""
import argparse
import collections
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)

MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = datetime.date.today().isoformat()
SALIDA = os.path.join(RAIZ, "data", "pending", "sedes-codigo-postal-" + FECHA)
API = "https://clinicaltrials.gov/api/v2/studies"
MIN_REGISTROS, MIN_PROPORCION = 2, 0.9


def descargar(ncts):
    out = {}
    for i in range(0, len(ncts), 100):
        q = urllib.parse.urlencode({"filter.ids": ",".join(ncts[i:i + 100]), "pageSize": 100,
                                    "fields": "protocolSection.identificationModule,"
                                              "protocolSection.contactsLocationsModule"})
        req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "kol-radar"})
        r = json.load(urllib.request.urlopen(req, timeout=90))
        for s in r["studies"]:
            nct = s["protocolSection"]["identificationModule"]["nctId"]
            locs = s["protocolSection"].get("contactsLocationsModule", {}).get("locations", [])
            out[nct] = [{k: l.get(k) for k in ("facility", "city", "zip")} for l in locs if l.get("country") == "Chile"]
        time.sleep(0.5)
    return out


def codigo(z):
    z = re.sub(r"\D", "", z or "")
    return z if len(z) == 7 and not z.endswith("0000") else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ubicaciones", help="ubicaciones ya descargadas (JSON nct → sedes en Chile)")
    a = ap.parse_args()
    registro = exclusiones.Registro()
    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}
    ensayos = sorted(e["id"].upper() for e in ent if e["tipo"] == "ensayo_clinico")
    U = json.load(open(a.ubicaciones, encoding="utf-8")) if a.ubicaciones else descargar(ensayos)

    # Texto de sede → institución, por los alias ya documentados (nunca por parecido).
    alias = {}
    for e in ent:
        if e["tipo"] == "institucion":
            for t in [e["nombre"]] + list(e.get("alias_en_la_fuente") or []):
                alias[t.strip().lower()] = e["id"]
    for v in vin:
        if v["tipo"] == "sitio del ensayo" and v.get("alias_fuente") and v.get("criterio") != "codigo_postal":
            alias[v["alias_fuente"].strip().lower()] = v["origen"]

    por_codigo = collections.defaultdict(collections.Counter)
    ejemplos = collections.defaultdict(list)
    for nct, locs in U.items():
        for l in locs:
            inst, z = alias.get((l.get("facility") or "").strip().lower()), codigo(l.get("zip"))
            if inst and z:
                por_codigo[z][inst] += 1
                if nct not in ejemplos[(z, inst)]:
                    ejemplos[(z, inst)].append(nct)

    sitios = collections.defaultdict(set)
    for v in vin:
        if v["tipo"] == "sitio del ensayo":
            sitios[v["destino"]].add(v["origen"])
    ya = {(v["origen"], v["destino"]) for v in vin}
    sin_inst = [eid for eid in (x.lower() for x in ensayos)
                if not any(v.get("criterio") != "codigo_postal" for v in vin
                           if v["tipo"] == "sitio del ensayo" and v["destino"] == eid)]

    asignadas, ambiguas = [], []
    for eid in sin_inst:
        e = por_id[eid]
        for l in U.get(eid.upper(), []):
            z = codigo(l.get("zip"))
            if not z or z not in por_codigo:
                continue
            c = por_codigo[z]
            inst, n = c.most_common(1)[0]
            total = sum(c.values())
            fila = {"ensayo": eid.upper(), "sede_en_la_fuente": l.get("facility"), "ciudad": l.get("city"),
                    "codigo_postal": z, "centros_con_ese_codigo": dict(c)}
            if n < MIN_REGISTROS or n / total < MIN_PROPORCION:
                ambiguas.append(fila)
                continue
            respaldo = [x for x in ejemplos[(z, inst)] if x.lower() != eid][:3]
            fila.update({"institucion": inst, "registros_con_nombre": n, "respaldo": respaldo})
            asignadas.append(fila)
            if (inst, eid) not in ya:
                vin.append({"origen": inst, "destino": eid, "tipo": "sitio del ensayo",
                            "alias_fuente": l.get("facility") or "(sin nombre)", "criterio": "codigo_postal",
                            "fuente_url": "https://clinicaltrials.gov/study/" + eid.upper()})
                ya.add((inst, eid))
            hecho = ("ClinicalTrials.gov declara una sede sin nombre de centro («%s», %s, código postal %s). Ese código "
                     "postal es el que la misma fuente declara para %s en %d registro(s) con nombre (por ejemplo %s): "
                     "se infiere que es ese centro." % (l.get("facility") or "sin nombre", l.get("city") or "sin ciudad",
                                                        z, por_id[inst]["nombre"], n, ", ".join(respaldo)))
            if not any(h.get("hecho") == hecho for h in e["hechos"]):
                e["hechos"].append({"tipo": "ensayo_clinico", "hecho": hecho,
                                    "fase": next((h.get("fase") for h in e["hechos"] if h.get("fase")), None),
                                    "fuente_url": "https://clinicaltrials.gov/study/" + eid.upper(),
                                    "fecha": FECHA, "confianza": "pendiente"})

    base["actualizado"] = FECHA
    exclusiones.guardar_muestra(base, MUESTRA, registro)
    con_inst = {v["destino"] for v in vin if v["tipo"] == "sitio del ensayo"}
    resumen = {
        "fecha": FECHA, "criterio": "código postal específico, >= %d registros con nombre y >= %d%% de ellos"
                                    % (MIN_REGISTROS, MIN_PROPORCION * 100),
        "ensayos_sin_sede_nombrada": len(sin_inst),
        "ensayos_con_sede_inferida": len({x["ensayo"] for x in asignadas}),
        "vinculos_inferidos": len({(x["institucion"], x["ensayo"]) for x in asignadas}),
        "sedes_ambiguas": len(ambiguas),
        "ensayos_sin_institucion_despues": sum(1 for e in ent if e["tipo"] == "ensayo_clinico" and e["id"] not in con_inst),
    }
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, obj in (("resumen.json", resumen), ("asignadas.json", asignadas), ("ambiguas.json", ambiguas)):
        with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
