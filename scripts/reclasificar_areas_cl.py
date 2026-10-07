#!/usr/bin/env python3
"""Amplía áreas desde condiciones de CTGov declaradas; conserva etiquetas existentes.

No lee títulos. Requiere el registro privado de exclusiones antes de escribir.
"""
import collections
import datetime
import json
from pathlib import Path

import areas
import exclusiones

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample" / "perfiles-muestra.json"


def main():
    registro = exclusiones.Registro()
    base = json.loads(SAMPLE.read_text(encoding="utf-8"))
    antes = collections.Counter()
    despues = collections.Counter()
    nuevos = 0
    for trial in base["entidades"]:
        if trial.get("tipo") != "ensayo_clinico" or not trial.get("condiciones_fuente"):
            continue
        condiciones = trial["condiciones_fuente"]
        anteriores = set(trial.get("areas") or [])
        if not anteriores:
            antes["sin_clasificar"] += 1
        matches = areas.desde_condiciones(condiciones)
        trial["areas"] = sorted(anteriores | {a["id"] for a, _ in matches})
        trial["enfermedades"] = sorted(set(trial.get("enfermedades") or []) |
                                        {e["id"] for _, e in matches})
        if not trial.get("area") and matches:
            trial["area"] = matches[0][1]["nombre"]
        if not anteriores and trial["areas"]:
            nuevos += 1
        if not trial["areas"]:
            despues["sin_clasificar"] += 1
    base["actualizado"] = datetime.date.today().isoformat()
    exclusiones.guardar_muestra(base, SAMPLE, registro)
    print(json.dumps({"antes_sin_clasificar_con_condiciones": antes["sin_clasificar"],
                      "reasignados_por_condicion": nuevos,
                      "quedan_sin_clasificar_con_condiciones": despues["sin_clasificar"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
