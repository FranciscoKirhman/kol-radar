#!/usr/bin/env python3
"""Contrasta una muestra determinista de hechos nuevos con la API oficial CT.gov."""
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", default=MUESTRA)
    ap.add_argument("--cantidad", type=int, default=30)
    ap.add_argument("--base", default="main", help="Referencia Git anterior a la expansión")
    a = ap.parse_args()
    base = json.load(open(a.muestra, encoding="utf-8"))
    anterior = json.loads(subprocess.check_output(
        ["git", "show", a.base + ":data/sample/perfiles-muestra.json"], cwd=RAIZ))
    ids_anteriores = {e["id"] for e in anterior["entidades"]}
    candidatos = [e for e in base["entidades"] if e["tipo"] == "ensayo_clinico"
                  and e["id"] not in ids_anteriores
                  and any(h.get("confianza") == "pendiente" and
                          h.get("fuente_url") == "https://clinicaltrials.gov/study/" + e["id"].upper()
                          for h in e.get("hechos", []))]
    if len(candidatos) < a.cantidad:
        raise SystemExit("No hay suficientes ensayos candidatos para la muestra")
    elegidos = sorted(candidatos, key=lambda e: hashlib.sha256(e["id"].encode()).hexdigest())[:a.cantidad]
    fallos = []
    for e in elegidos:
        nct = e["id"].upper()
        url = "https://clinicaltrials.gov/api/v2/studies/" + nct
        req = urllib.request.Request(url, headers={"User-Agent": "kol-radar-source-audit"})
        with urllib.request.urlopen(req, timeout=30) as respuesta:
            protocolo = json.load(respuesta)["protocolSection"]
        titulo = protocolo["identificationModule"]["briefTitle"]
        sedes = protocolo.get("contactsLocationsModule", {}).get("locations", [])
        hechos = [h for h in e.get("hechos", []) if h.get("fuente_url") == "https://clinicaltrials.gov/study/" + nct]
        if (not hechos or titulo != hechos[0].get("hecho") or
                not any(s.get("country") == "Chile" for s in sedes) or
                not hechos[0].get("fecha") or hechos[0].get("confianza") != "pendiente"):
            fallos.append(nct)
        print(nct, "OK" if nct not in fallos else "FALLA", url)
    if fallos:
        raise SystemExit("Fallaron %d/%d: %s" % (len(fallos), a.cantidad, ", ".join(fallos)))
    print("PASA — %d hechos coinciden con la API oficial, con sitio declarado en Chile." % a.cantidad)


if __name__ == "__main__":
    main()
