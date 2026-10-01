#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrega sedes que ClinicalTrials.gov enmascara cuando un documento del propio estudio las nombra.

ClinicalTrials.gov esconde el nombre de muchas sedes ("Local Institution", "Chile"), pero el
informe de resultados del patrocinador o el apéndice de la publicación a veces lista los centros
por país. La tercera ronda de ChatGPT (2026-09-30) buscó esos documentos para los 109 ensayos sin
ninguna sede identificada; encontró 10. Los informes de Bristol-Myers Squibb nombran el estudio por
su código de protocolo (CA209-017…), que es el orgStudyId que declara ClinicalTrials.gov, y la sede
por un número que a veces es el mismo de "Local Institution - 0131".

Cada fila de SEDES se verificó abriendo el documento: la cita está copiada de ahí, y la ciudad (y
el código postal, cuando lo hay) calza con la sede enmascarada de ClinicalTrials.gov.
  - Solo instituciones que ya están en la muestra: no crea entidades.
  - No agrega personas, aunque el documento las nombre (y el texto del centro se guarda sin ellas).
  - Si el documento nombra un centro que no se puede identificar sin suponer, no entra: queda en
    NO_RESUELTAS.
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
for _protocolo, _archivo in (("CA209-017", "O-2672461-3-0-73B164-20220816144215"),
                             ("CA209-057", "O-2672461-3-0-621624-20221216083228"),
                             ("CA209-066", "O-2672461-3-0-C9B7D2-20220607144210"),
                             ("CA184-437", "O-2225_01-2-0-0B1D07-20171214093750"),
                             ("CA209-331", "O-2526_01-2-0-93C79C-20230822175952"),
                             ("CA209-9ER", "O-2713432-1-0-D695CA-20220830114625"),
                             ("CA224-047", "O-7007005-1-0-4C3C7D-20230421120631")):
    DOCUMENTOS[_protocolo.lower()] = {
        "url": "https://portal.dimdi.de/data/ctr/%s.pdf" % _archivo,
        "descripcion": "el informe de resultados del patrocinador (Bristol-Myers Squibb, protocolo %s), lista de centros" % _protocolo,
        "consultado": "2026-09-30",
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
    ("NCT01642004", "ciec", "ca209-017",
     "CA209-017-0131: Centro Internacional de Estudios Clinicos (Office), Manzano 343, Oficina 410, Recoleta, Santiago de Chile"),
    ("NCT01642004", "centro-oncologico-norte", "ca209-017",
     "CA209-017-0161: Centro Oncológico Antofagasta (Office), Los Pumas 10255, Chimba Alto, Antofagasta, 240000"),
    ("NCT01673867", "instituto-oncologico-vina", "ca209-057",
     "CA209-057-0012: Instituto Oncologico (Office), Anabaena 336, Jardin Del Mar, Reñaca, Viña Del Mar"),
    ("NCT01673867", "ciec", "ca209-057",
     "CA209-057-0077: Centro Internacional de Estudios Clinicos (Office), Manzano 343, Oficina 410, Recoleta, Santiago de Chile"),
    ("NCT01673867", "falp", "ca209-057", "CA209-057-0134: Fundacion Arturo Lopez Perez (Office), Av. Rancagua 878, Santiago"),
    ("NCT01721772", "instituto-oncologico-vina", "ca209-066",
     "CA209-066-0028: Instituto Oncologico (Office), Anabaena 336, Jardin Del Mar, Reñaca, Viña Del Mar"),
    ("NCT01721772", "falp", "ca209-066", "CA209-066-0029: Fundacion Arturo Lopez Perez (Office), Av. Rancagua 878, Santiago"),
    ("NCT01721772", "hosp-uchile", "ca209-066",
     "CA209-066-0080: Hospital Clinico de la Universidad De Chile (Office), Santos Dumont 999, 5 Piso Sector E, Santiago"),
    ("NCT02279862", "instituto-oncologico-vina", "ca184-437",
     "012 Instituto Oncologico Clinica Renaca (Office), Anabaena 336, Jardin Del Mar, Vina Del Mar, 2540364"),
    ("NCT02279862", "ciec", "ca184-437",
     "015 Centro Internacional de Estudios Clinicos (Office), Manzano 343, Oficina 410, Recoleta, Santiago de Chile"),
    ("NCT02279862", "falp", "ca184-437", "016 Fundacion Arturo Lopez Perez (Office), Av. Rancagua 878, Santiago"),
    ("NCT02481830", "ciec", "ca209-331",
     "CA209-331-0025: Centro Internacional de Estudios Clinicos (Office), Manzano 343, Oficina 410, Recoleta, Santiago de Chile"),
    ("NCT03141177", "ciec", "ca209-9er",
     "CA209-9ER-0045: Centro Internacional de Estudios Clinicos (Office), Manzano 343, Oficina 410, Recoleta, Santiago de Chile"),
    ("NCT03470922", "falp", "ca224-047", "CA224-047-0001: Fundacion Arturo Lopez Perez (Office), Av. Rancagua 878, Santiago"),
]

# Centros que un documento nombra pero que no se pueden ligar sin suponer. No entran a la muestra.
NO_RESUELTAS = [
    ("NCT01721772", "ca209-066", "CA209-066-0085: Centro Investigaciones Clinicas (Office), Av. Americo Vespucio 1314, "
     "3rd Floor, Vitacura, Santiago, 7630370",
     "Es el edificio del IRAM, pero ClinicalTrials.gov usa ese código postal para el IRAM y para el Centro de "
     "Investigaciones Clínicas Viña del Mar. No se sabe cuál de los dos es, o si es otro."),
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
        "centros_nombrados_sin_resolver": ["%s · %s" % (nct, texto) for nct, _, texto, _ in NO_RESUELTAS],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
