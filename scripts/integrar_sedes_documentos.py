#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrega sedes que ClinicalTrials.gov enmascara cuando un documento del propio estudio las nombra.

ClinicalTrials.gov esconde el nombre de muchas sedes ("Local Institution", "Chile"), pero el
informe de resultados del patrocinador o el apéndice de la publicación a veces lista los centros
por país. La tercera ronda de ChatGPT (2026-09-30) buscó esos documentos para los 109 ensayos sin
ninguna sede identificada; encontró 3.

Cada fila de SEDES se verificó abriendo el documento: la cita está copiada de ahí, y la ciudad (y
el código postal, cuando lo hay) calza con la sede enmascarada de ClinicalTrials.gov.
  - Solo instituciones que ya están en la muestra: no crea entidades.
  - No agrega personas, aunque el documento las nombre.
  - El vínculo lleva "criterio": "documento_del_estudio" y la URL del documento; la ficha del
    ensayo recibe un hecho que dice qué documento y qué centros. Todo entra `pendiente`.
  - Correrlo dos veces no cambia nada.

Uso:  python3 scripts/integrar_sedes_documentos.py
"""
import datetime
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)

MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = datetime.date.today().isoformat()

DOCUMENTOS = {
    "ibis2-dcis": {
        "url": "https://discovery.ucl.ac.uk/1493474/1/IBIS-II%20DCIS%20trial%20PIIS0140673615011290.pdf",
        "descripcion": "el apéndice de investigadores de la publicación del ensayo (Forbes et al., The Lancet, 2016)",
        "consultado": "2026-09-30",
    },
    "ca180-056": {
        "url": "https://portal.dimdi.de/data/ctr/O-2703363-3-0-48CC42-20190814095642.pdf",
        "descripcion": "el informe de resultados del patrocinador (Bristol-Myers Squibb, protocolo CA180-056), lista de centros",
        "consultado": "2026-09-30",
    },
    "ca184-095": {
        "url": "https://portal.dimdi.de/data/ctr/O-1156_01-2-0-76FC19-20161124160439.pdf",
        "descripcion": "el informe de resultados del patrocinador (Bristol-Myers Squibb, protocolo CA184-095), lista de centros",
        "consultado": "2026-09-30",
    },
}

# (ensayo, institución de la muestra, documento, texto del centro tal como lo escribe el documento)
SEDES = [
    ("NCT00072462", "falp", "ibis2-dcis", "Fundacion Arturo Lopez Perez, Santiago, Chile"),
    ("NCT00072462", "hosp-militar", "ibis2-dcis", "Hospital Militar, Santiago, Chile"),
    ("NCT00072462", "iram", "ibis2-dcis", "Instituto de Radiomedicina, Santiago, Chile"),
    ("NCT00072462", "hosp-san-borja", "ibis2-dcis", "Hospital Clinico San Borja Arriarán, Santiago, Chile"),
    ("NCT00481247", "hosp-salvador", "ca180-056",
     "Hospital Del Salvador (Patient Treatment - Hospital/Medical Center), Av. Salvador 364, Providencia, Santiago"),
    ("NCT01057810", "instituto-oncologico-vina", "ca184-095",
     "Instituto Oncologico (Pt Tx Ctr - Hosp/Med Ctr), Anabaena 336, Jardin Del Mar, Renaca, Vina Del Mar"),
    ("NCT01057810", "icos", "ca184-095",
     "ICOS – Inmunomedica (Pt Tx Ctr - Med Office/Clinic), Lago Puyehue 1745, Temuco"),
    ("NCT01057810", "iram", "ca184-095",
     "IRAM (Pt Tx Ctr - Hosp/Med Ctr), Av. Americo Vespucio Norte, Nro. 1314, Santiago"),
]


def main():
    registro = exclusiones.Registro()
    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}
    ya = {(v["origen"], v["destino"]) for v in vin}

    nuevos, por_ensayo = 0, {}
    for nct, inst, doc, texto in SEDES:
        eid = nct.lower()
        if eid not in por_id or inst not in por_id:
            raise SystemExit("no está en la muestra: %s o %s" % (eid, inst))
        d = DOCUMENTOS[doc]
        por_ensayo.setdefault((eid, doc), []).append(inst)
        if (inst, eid) in ya:
            continue
        vin.append({"origen": inst, "destino": eid, "tipo": "sitio del ensayo", "alias_fuente": texto,
                    "criterio": "documento_del_estudio", "fuente_url": d["url"], "fuente_descripcion": d["descripcion"]})
        ya.add((inst, eid))
        nuevos += 1

    for (eid, doc), insts in por_ensayo.items():
        e, d = por_id[eid], DOCUMENTOS[doc]
        nombres = [por_id[i]["nombre"] for i in insts]
        lista = nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]
        hecho = ("ClinicalTrials.gov no nombra la sede en Chile. La nombra %s: %s." % (d["descripcion"], lista))
        if not any(h.get("hecho") == hecho for h in e["hechos"]):
            e["hechos"].append({"tipo": "ensayo_clinico", "hecho": hecho,
                                "fase": next((h.get("fase") for h in e["hechos"] if h.get("fase")), None),
                                "fuente_url": d["url"], "fecha": d["consultado"], "confianza": "pendiente"})

    base["actualizado"] = FECHA
    exclusiones.guardar_muestra(base, MUESTRA, registro)
    con_inst = {v["destino"] for v in vin if v["tipo"] == "sitio del ensayo"}
    print(json.dumps({
        "vinculos_nuevos": nuevos,
        "ensayos": len({eid for eid, _ in por_ensayo}),
        "ensayos_sin_institucion_despues": sum(1 for e in ent if e["tipo"] == "ensayo_clinico" and e["id"] not in con_inst),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
