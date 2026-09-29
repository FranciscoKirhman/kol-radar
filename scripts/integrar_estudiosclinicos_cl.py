#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liga ensayos con los centros que nombra el buscador de la CIF (estudiosclinicos.cl).

ClinicalTrials.gov enmascara la sede de muchos ensayos de la industria ("Research Site", "Local
Institution", "Novartis Investigative Site"): el ensayo existe en Chile pero no se sabe dónde. El
buscador de estudios clínicos de la Cámara de la Innovación Farmacéutica publica, para los ensayos
que hoy reclutan, la lista de centros abiertos por ciudad. Este script cruza por NCT y, para cada
centro que la CIF nombra, agrega el vínculo "sitio del ensayo" con la URL de la ficha de la CIF
como fuente.

Reglas:
  1. Solo se cruzan ensayos que ya están en la muestra (mismo NCT). Los ensayos de la CIF que no
     están en la muestra no entran: son de otras áreas o no aparecieron en la consulta oncológica.
  2. Cada nombre de centro de la CIF se liga a una institución por la tabla CENTROS, escrita a mano.
     Un nombre que no está en la tabla no crea nada: queda listado como pendiente.
  3. El vínculo guarda el texto literal de la CIF y la URL de la ficha. El ensayo recibe un hecho
     con la lista de centros y la misma URL.
  4. Nada se confirma. Correrlo dos veces no cambia nada.

Uso:  python3 scripts/integrar_estudiosclinicos_cl.py data/pending/estudiosclinicos-cl-AAAA-MM-DD/fichas.json
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
DEIS = "https://datos.gob.cl/dataset/establecimientos-de-salud-vigentes"

# Nombre en la CIF → id de la institución en la muestra.
CENTROS = {
    "Bradford Hill": "bradford-hill",
    "FALP": "falp",
    "James Lind Centro de Investigación del Cancer": "james-lind",
    "Oncocentro APYS": "oncocentro",
    "Oncocentro Valdivia": "oncocentro",            # ya era alias de Oncocentro APYS en ClinicalTrials.gov
    "Oncovida": "oncovida",
    "Pontificia Universidad Católica de Chile": "puc",
    "CICUC": "puc",                                  # Centro de Investigación Clínica UC
    "IC La Serena Research": "ic-la-serena",
    "Centro de Investigación y Desarollo Oncologico (CIDO)": "cido",
    "Orlandi Oncologia": "orlandi",
    "Biocenter": "biocenter",
    "ICEGCLINIC": "iceg",
    "Clínica Alemana de Santiago": "clinica-alemana",
    "Centro de Estudios Clinicos SAGA": "saga",
    "Centro de Oncología de Precisión": "centro-precision",
    "Oncología Precisión U. Mayor": "centro-precision",  # cop.umayor.cl: "Centro de Oncología de Precisión"
    "Instituto Nacional del Cáncer": "inc",
    "Clínica Puerto Montt": "clinica-puerto-montt",
    "Centro de Investigaciones Clinicas Viña del Mar": "cic-vina",
    "IRAM Cancer Research": "iram",
    "Instituto de Radiomedicina": "iram",
    "Hospital U. de Chile": "hosp-uchile",
    "Clínica San Carlos de Apoquindo Red Salud UC Christus": "clinica-uc-san-carlos",
    "Clínica Vespucio": "clinica-davila-vespucio",
    "Centro de Investigación Oncológica del Norte": "centro-oncologico-norte",
    "Centro Oncológico Antofagasta": "centro-oncologico-norte",
    "Clinica Universidad Catolia del Maule": "ucm",
    "Centro de Cancer Nuestra Senora de la Esperanza": "centro-cancer-uc",
    "Centro de Cáncer UC": "centro-cancer-uc",
    "Hospital Sótero del Río": "hosp-sotero",
    "Sociedad de Investigaciones Médicas": "sim",
    "Clinical Research Chile SpA": "crchile",
    "Clínica Bupa Reñaca": "instituto-oncologico-vina",
    "Servicios Medicos Urumed": "urumed",
    "Enroll SpA": "enroll",
    "Hospital Clínico Universidad Católica": "hosp-clinico-uc",
    "Inmunocel": "inmunocel",
    "Clínica Las Condes": "clinica-las-condes",
    "Centro de Investigación Clinical del Sur": "cics-temuco",
    "Clínica Alemana de Temuco": "clinica-alemana-temuco",
    "Instituto de Especialidades Urologicas (UROMED)": "uromed",
}

NUEVAS = [
    {"id": "clinica-alemana-temuco", "nombre": "Clínica Alemana de Temuco", "ciudad": "Temuco",
     "alias": ["Clínica Alemana de Temuco"],
     "hechos": [{"tipo": "otro", "hecho": "Registro de establecimientos de salud del DEIS (Minsal): «Clínica Alemana "
                                          "de Temuco», comuna de Temuco, código 121202.", "fuente_url": DEIS}],
     "nota": "Es otra institución que Clínica Alemana de Santiago (otra ficha)."},
    {"id": "uromed", "nombre": "Instituto de Especialidades Urológicas (UROMED)", "ciudad": "Santiago",
     "alias": ["Instituto de Especialidades Urologicas (UROMED)", "UROMED"], "hechos": []},
]
# El texto con que ClinicalTrials.gov nombra a UROMED quedaba en cola sin a quién ligarlo.
PENDIENTES_CTGOV = {"UROMED": "uromed"}


def main():
    # Antes de cualquier consulta: si hay exclusiones y falta la clave, se detiene acá y no al
    # final de la corrida. Ver scripts/exclusiones.py.
    registro = exclusiones.Registro()
    ruta = sys.argv[1] if len(sys.argv) > 1 else None
    if not ruta:
        sys.exit(__doc__)
    cif = json.load(open(ruta, encoding="utf-8"))
    fecha = cif["fecha_consulta"]
    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}

    for n in NUEVAS:
        if n["id"] in por_id:
            continue
        hechos = [dict(h, fecha=fecha, confianza="pendiente") for h in n["hechos"]]
        ficha = {"id": n["id"], "nombre": n["nombre"], "tipo": "institucion", "ciudad": n["ciudad"],
                 "subtitulo": "Centro con sitio de ensayos clínicos en Chile", "alias_en_la_fuente": n["alias"],
                 "hechos": hechos}
        if n.get("nota"):
            ficha["nota_identidad"] = n["nota"]
        ent.append(ficha)
        por_id[n["id"]] = ficha
    for iid in set(CENTROS.values()):
        if iid not in por_id:
            sys.exit("CENTROS apunta a una institución que no existe: " + iid)

    ya = {(v["origen"], v["destino"]) for v in vin}
    nuevos, ensayos_tocados, sin_tabla = 0, set(), {}
    for f in cif["fichas"]:
        nct = (f.get("nct") or "").lower()
        e = por_id.get(nct)
        if not e or e["tipo"] != "ensayo_clinico" or not f["sitios"]:
            continue
        nombres = []
        for s in f["sitios"]:
            iid = CENTROS.get(s["centro"])
            nombres.append(s["centro"] + " (" + s["ciudad"] + ")")
            if not iid:
                sin_tabla[s["centro"]] = sin_tabla.get(s["centro"], 0) + 1
                continue
            inst = por_id[iid]
            if s["centro"] not in inst.setdefault("alias_en_la_fuente", []):
                inst["alias_en_la_fuente"].append(s["centro"])
            if (iid, e["id"]) in ya:
                continue
            vin.append({"origen": iid, "destino": e["id"], "tipo": "sitio del ensayo",
                        "alias_fuente": s["centro"], "fuente_url": f["url"]})
            ya.add((iid, e["id"]))
            nuevos += 1
            ensayos_tocados.add(e["id"])
        if not any(h.get("fuente_url") == f["url"] for h in e["hechos"]):
            e["hechos"].append({
                "tipo": "ensayo_clinico",
                "hecho": "El buscador de estudios clínicos de la Cámara de la Innovación Farmacéutica lo lista "
                         "reclutando en Chile, con estos centros abiertos: " + "; ".join(nombres) + ".",
                "fase": next((h.get("fase") for h in e["hechos"] if h.get("fase")), None),
                "fuente_url": f["url"], "fecha": fecha, "confianza": "pendiente"})
        e["ficha_cif"] = f["url"]

    # Una institución nueva sin registro DEIS existe por lo que dice la CIF: ese es su hecho.
    for n in NUEVAS:
        ficha = por_id[n["id"]]
        if ficha["hechos"]:
            continue
        for f in cif["fichas"]:
            if any(CENTROS.get(s["centro"]) == n["id"] for s in f["sitios"]):
                centro = next(s for s in f["sitios"] if CENTROS.get(s["centro"]) == n["id"])
                ficha["hechos"].append({
                    "tipo": "afiliacion",
                    "hecho": "El buscador de estudios clínicos de la Cámara de la Innovación Farmacéutica lo lista "
                             "como centro abierto en %s, escrito «%s»." % (centro["ciudad"], centro["centro"]),
                    "fuente_url": f["url"], "fecha": fecha, "confianza": "pendiente"})
                break

    for e in ent:
        cola = e.get("sedes_pendientes_resolucion")
        if not cola:
            continue
        quedan = []
        for t in cola:
            iid = PENDIENTES_CTGOV.get(t)
            if not iid:
                quedan.append(t)
                continue
            if (iid, e["id"]) not in ya:
                vin.append({"origen": iid, "destino": e["id"], "tipo": "sitio del ensayo", "alias_fuente": t})
                ya.add((iid, e["id"]))
                nuevos += 1
        if quedan:
            e["sedes_pendientes_resolucion"] = quedan
        else:
            del e["sedes_pendientes_resolucion"]

    exclusiones.guardar_muestra(base, MUESTRA, registro)
    print(json.dumps({"vinculos_nuevos": nuevos, "ensayos_con_sede_nueva": len(ensayos_tocados),
                      "centros_sin_tabla": sin_tabla}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
