#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga de ClinicalTrials.gov los ensayos oncológicos con sede en Chile, en el formato crudo que
leen preintegracion_clinicaltrials.py e integrar_beta.py (variable KOL_CRUDO).

La descarga del 2026-09-09 se hizo en una sesión y no quedó en el repositorio; este script la
reproduce con la consulta documentada en
data/pending/preintegracion-clinicaltrials-2026-09-09/README.md, una por área:

    AREA[LocationCountry]Chile AND AREA[ConditionSearch]"<condición en inglés>"

Formato de salida: {área: [ensayo, ...]}, y cada ensayo
    {"nct", "titulo", "acronimo", "fases", "estado", "actualizado", "condiciones", "intervenciones",
     "sitios": [{"facility", "city", "zip", "status", "contactos": [{"name", "role"}]}]}
con solo las sedes en Chile. Un ensayo aparece en cada área cuya consulta lo devuelve.

El archivo pesa varios MB y cambia con cada consulta: va fuera del repositorio por defecto.

Uso:  python3 scripts/descargar_ctgov.py [--salida ruta.json]
"""
import argparse
import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://clinicaltrials.gov/api/v2/studies"
# Área de la muestra → condición en inglés que se consulta.
CONSULTAS = {
    "cáncer de pulmón": "lung cancer", "cáncer de mama": "breast cancer", "cáncer gástrico": "gastric cancer",
    "cáncer colorrectal": "colorectal cancer", "cáncer de próstata": "prostate cancer", "melanoma": "melanoma",
    "linfoma": "lymphoma", "leucemia": "leukemia", "mieloma múltiple": "multiple myeloma",
    "cáncer de ovario": "ovarian cancer", "cáncer de páncreas": "pancreatic cancer", "cáncer renal": "renal cancer",
    "cáncer de vejiga": "bladder cancer", "cáncer de hígado": "liver cancer", "sarcoma": "sarcoma",
    "cáncer de cabeza y cuello": "head and neck cancer", "cáncer cervicouterino": "cervical cancer",
    "cáncer de endometrio": "endometrial cancer",
    # "brain tumor" no devuelve el ensayo de glioblastoma NCT01450449; "glioma" sí, y es el término
    # con que integrar_beta.py asigna esta área.
    "tumor cerebral": "glioma",
}
CAMPOS = ",".join(["protocolSection.identificationModule", "protocolSection.statusModule",
                   "protocolSection.designModule.phases", "protocolSection.conditionsModule.conditions",
                   "protocolSection.armsInterventionsModule.interventions",
                   "protocolSection.contactsLocationsModule.locations"])


def pedir(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kol-radar"})
            return json.load(urllib.request.urlopen(req, timeout=120))
        except OSError:
            if intento == 2:
                raise
            time.sleep(3 * (intento + 1))


def ensayo(s):
    p = s["protocolSection"]
    im, st = p["identificationModule"], p.get("statusModule", {})
    sitios = []
    for l in p.get("contactsLocationsModule", {}).get("locations", []):
        if l.get("country") != "Chile":
            continue
        sitios.append({"facility": l.get("facility"), "city": l.get("city"), "zip": l.get("zip"),
                       "status": l.get("status"),
                       "contactos": [{"name": c.get("name"), "role": c.get("role")} for c in l.get("contacts") or []]})
    return {"nct": im["nctId"], "titulo": im.get("briefTitle"), "acronimo": im.get("acronym"),
            "fases": p.get("designModule", {}).get("phases") or [], "estado": st.get("overallStatus"),
            "actualizado": (st.get("lastUpdatePostDateStruct") or {}).get("date"),
            "condiciones": p.get("conditionsModule", {}).get("conditions") or [],
            "intervenciones": [i.get("name") for i in p.get("armsInterventionsModule", {}).get("interventions") or []],
            "sitios": sitios}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--salida", default=os.path.join(os.path.expanduser("~"), ".cache", "kol-radar",
                                                     "ctgov-crudo-%s.json" % datetime.date.today().isoformat()))
    a = ap.parse_args()
    crudo = {}
    for area, condicion in CONSULTAS.items():
        params = {"query.term": 'AREA[LocationCountry]Chile AND AREA[ConditionSearch]"%s"' % condicion,
                  "fields": CAMPOS, "pageSize": 200}
        lista = []
        while True:
            r = pedir(params)
            lista += [ensayo(s) for s in r.get("studies", [])]
            if not r.get("nextPageToken"):
                break
            params["pageToken"] = r["nextPageToken"]
            time.sleep(0.4)
        crudo[area] = [e for e in lista if e["sitios"]]
        print("%-28s %4d ensayos" % (area, len(crudo[area])), file=sys.stderr)
    os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
    json.dump(crudo, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False)
    total = {e["nct"] for l in crudo.values() for e in l}
    print("%d ensayos distintos → %s" % (len(total), a.salida))


if __name__ == "__main__":
    main()
