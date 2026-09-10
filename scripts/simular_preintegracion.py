#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simula la integración del artefacto de preintegración SIN tocar la muestra pública.

Responde tres preguntas que no se pueden contestar leyendo el JSON candidato:

  1. ¿Cambia el puntaje de alguna de las 70 personas actuales?
  2. ¿Empiezan a ejercerse los topes por dimensión, que hoy nunca se alcanzan?
  3. ¿De qué tamaño queda el grafo?

Simula dos escenarios, porque tienen consecuencias muy distintas:

  A. Solo ensayos e instituciones — lo único que el umbral de admisión autoriza hoy.
  B. Además, si un revisor humano aprobara las personas propuestas y sus vínculos de
     investigador de sitio. Este escenario NO está autorizado; se calcula para saber qué
     pasaría antes de decidirlo, no para aplicarlo.

Escribe `simulacion.json` en el directorio de preintegración. No modifica
`data/sample/perfiles-muestra.json`.
"""
import collections
import copy
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE = os.path.join(RAIZ, "data", "pending", "preintegracion-clinicaltrials-2026-09-09")
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
INDEX = os.path.join(RAIZ, "web", "index.html")

sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from test_puntaje_paridad import construir_runner  # noqa: E402  (reusa el extractor de JS real)


def puntajes(entidades, vinculos):
    """Corre el computePriority REAL de web/index.html sobre un dataset simulado."""
    personas = [e for e in entidades if e["tipo"] == "persona"]
    with tempfile.TemporaryDirectory() as tmp:
        js = os.path.join(tmp, "r.js")
        datos = os.path.join(tmp, "d.json")
        open(js, "w", encoding="utf-8").write(construir_runner())
        json.dump({"personas": personas, "vinculos": vinculos},
                  open(datos, "w", encoding="utf-8"))
        r = subprocess.run(["node", js, datos], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("Node falló:\n" + r.stderr)
    return {p["id"]: s for p, s in zip(personas, json.loads(r.stdout))}


def fase_legible(fases):
    if not fases:
        return None
    m = {"PHASE1": "Fase I", "PHASE2": "Fase II", "PHASE3": "Fase III", "PHASE4": "Fase IV",
         "EARLY_PHASE1": "Fase I", "NA": None}
    vals = [m.get(f) for f in fases if m.get(f)]
    return vals[-1] if vals else None


def main():
    base = json.load(open(MUESTRA, encoding="utf-8"))
    cand = json.load(open(os.path.join(PRE, "ensayos_candidatos.json"), encoding="utf-8"))
    inst_c = json.load(open(os.path.join(PRE, "instituciones_candidatas.json"), encoding="utf-8"))
    personas_c = json.load(open(os.path.join(PRE, "personas_candidatas.json"), encoding="utf-8"))

    ids = {e["id"] for e in base["entidades"]}
    # Copia PROFUNDA a propósito. Con `dict(e)` la lista `hechos` queda compartida con
    # `base["entidades"]`, y el escenario B —que agrega hechos a fichas reutilizadas— terminaba
    # mutando los datos base. Las mediciones del escenario actual se toman después, así que el
    # artefacto habría reportado una persona sobre el tope de ensayos que en realidad no existe.
    ent = copy.deepcopy(base["entidades"])
    vin = copy.deepcopy(base["vinculos"])

    # ---- Escenario A: ensayos + instituciones ----
    for i in inst_c:
        if i["id_canonico"] in ids:
            continue
        ids.add(i["id_canonico"])
        alias, n = i["alias_textuales_en_la_fuente"][0]
        ent.append({
            "id": i["id_canonico"], "nombre": i["nombre_canonico"], "tipo": "institucion",
            "ciudad": None, "subtitulo": "Sitio de ensayos clínicos en Chile",
            "hechos": [{"tipo": "afiliacion",
                        "hecho": ("Aparece como sede chilena de al menos un ensayo en "
                                  "ClinicalTrials.gov, escrita en la fuente como \"%s\"." % alias),
                        "fuente_url": "https://clinicaltrials.gov/study/%s" % cand[0]["nct"],
                        "fecha": "2026-09-09", "confianza": "pendiente"}],
        })

    nuevos_ensayos = 0
    for e in cand:
        eid = e["nct"].lower()
        if eid in ids:
            continue
        ids.add(eid)
        nuevos_ensayos += 1
        ent.append({
            "id": eid, "nombre": "%s (%s)" % (e["acronimo_fuente"] or e["nct"], e["nct"]),
            "tipo": "ensayo_clinico", "area": e["areas_consultadas"][0],
            "acronimo": e["acronimo_fuente"],
            "hechos": [{"tipo": "ensayo_clinico", "hecho": e["titulo_fuente"],
                        "fase": fase_legible(e["fases_fuente"]),
                        "fuente_url": e["fuente_url"], "fecha": e["ultima_actualizacion_fuente"],
                        "confianza": "pendiente"}],
        })
        for s in e["sitios_chile"]:
            ic = s.get("institucion_canonica")
            if ic:
                vin.append({"origen": ic["id"], "destino": eid, "tipo": "sitio del ensayo"})

    A = {"entidades": len(ent), "vinculos": len(vin),
         "ensayos_nuevos": nuevos_ensayos,
         "instituciones_nuevas": sum(1 for i in inst_c if i["id_canonico"] not in
                                     {x["id"] for x in base["entidades"]})}

    antes = puntajes(base["entidades"], base["vinculos"])
    desp_a = puntajes(ent, vin)
    A["personas_con_puntaje_distinto"] = sum(1 for k in antes if antes[k] != desp_a[k])
    A["tiers"] = dict(collections.Counter(v["tier"] for v in desp_a.values()))
    A["tiers_antes"] = dict(collections.Counter(v["tier"] for v in antes.values()))

    # ---- Escenario B: además, personas aprobadas (NO autorizado; solo cálculo) ----
    entB = copy.deepcopy(ent)
    vinB = copy.deepcopy(vin)
    idsB = set(ids)
    aprobables = [p for p in personas_c
                  if p["clasificacion"] in ("reutilizacion_propuesta", "persona_nueva_propuesta")]
    creadas, reusadas = 0, 0
    por_persona = collections.defaultdict(list)
    for p in aprobables:
        if p["clasificacion"] == "reutilizacion_propuesta":
            pid = p["fichas_existentes_compatibles"][0]["id"]
            reusadas += 1
        else:
            pid = p["nombre_normalizado"].lower().replace(" ", "-")
            if pid not in idsB:
                idsB.add(pid)
                creadas += 1
                entB.append({"id": pid, "nombre": p["nombre_normalizado"], "tipo": "persona",
                             "ciudad": None, "subtitulo": p["institucion_canonica"],
                             "area": None, "hechos": []})
        por_persona[pid].append(p)

    for pid, filas in por_persona.items():
        ficha = next((e for e in entB if e["id"] == pid), None)
        if not ficha:
            continue
        for p in filas:
            ficha.setdefault("hechos", []).append({
                "tipo": "ensayo_clinico",
                "hecho": ("Figura como %s del sitio chileno en ClinicalTrials.gov."
                          % (p["rol_declarado_fuente"] or "contacto")),
                "fase": None, "fuente_url": p["fuente_url"],
                "fecha": "2026-09-09", "confianza": "pendiente"})
            vinB.append({"origen": pid, "destino": p["nct"].lower(),
                         "tipo": "investigador de sitio"})

    desp_b = puntajes(entB, vinB)
    B = {"entidades": len(entB), "vinculos": len(vinB),
         "personas_reutilizadas": reusadas, "personas_creadas": creadas,
         "personas_con_puntaje_distinto": sum(1 for k in antes if k in desp_b and antes[k] != desp_b[k]),
         "tiers": dict(collections.Counter(v["tier"] for v in desp_b.values()))}

    # ---- Activación de topes ----
    def topes(mapa, entidades):
        porid = {e["id"]: e for e in entidades if e["tipo"] == "persona"}
        t = collections.Counter()
        for pid, s in mapa.items():
            e = porid.get(pid)
            if not e:
                continue
            for tipo, campo, cap in (("ensayo_clinico", "nEnsayos", 5),
                                     ("publicacion", "nPub", 5)):
                unicos = len({h.get("fuente_url") for h in e.get("hechos", []) if h["tipo"] == tipo})
                if unicos > cap:
                    t["%s_sobre_tope" % tipo] += 1
            if s["ensayosPts"] >= 20:
                t["ensayosPts_en_el_tope_20"] += 1
            if s["pubPts"] >= 10:
                t["pubPts_en_el_tope_10"] += 1
            if s["redPts"] >= 5:
                t["redPts_en_el_tope_5"] += 1
        return dict(t)

    A["activacion_de_topes"] = topes(desp_a, ent)
    B["activacion_de_topes"] = topes(desp_b, entB)
    base_topes = topes(antes, base["entidades"])

    salida = {
        "fecha": "2026-09-09",
        "advertencia": ("Simulación. No se modificó data/sample/perfiles-muestra.json. "
                        "El escenario B no está autorizado: requiere revisión humana por persona."),
        "actual": {"entidades": len(base["entidades"]), "vinculos": len(base["vinculos"]),
                   "tiers": A["tiers_antes"], "activacion_de_topes": base_topes},
        "escenario_A_solo_ensayos_e_instituciones": A,
        "escenario_B_si_se_aprobaran_las_personas": B,
    }
    with open(os.path.join(PRE, "simulacion.json"), "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    print(json.dumps(salida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
