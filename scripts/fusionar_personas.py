#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Une fichas de persona que son la misma persona, con la evidencia escrita en FUSIONES.

Las revistas chilenas abrevian el apellido materno ("Fernando Saldías P.") y PubMed indexa por
apellido e iniciales, así que la misma persona entra dos veces si la recolección la encuentra por
SciELO y por PubMed. Unirlas es una decisión de identidad: nunca la toma el código por parecido de
nombre. Cada fusión de abajo trae la evidencia que la sostiene, con su URL, y la ficha que queda lo
dice en su nota de identidad.

Qué hace con cada fusión:
  1. Pasa los hechos de la ficha absorbida a la que queda (sin repetir los que ya están).
  2. Reescribe los vínculos de la absorbida hacia la que queda, sin duplicados ni lazos consigo misma.
  3. Agrega un hecho por cada evidencia, `pendiente`: la fusión no la revisó todavía una persona.
  4. Guarda el nombre absorbido en `alias_en_la_fuente` y borra la ficha absorbida.

Correrlo dos veces no cambia nada: una fusión ya hecha (la absorbida no existe) se salta.

Uso:  python3 scripts/fusionar_personas.py
"""
import datetime
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)

MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = "2026-09-29"
QUIEN = ("La decidió Claude por encargo de Francisco (2026-09-29), con la evidencia citada; todavía no la "
         "revisó una persona.")

FUSIONES = [
    {
        "queda": "francisco-aguayo", "absorbe": "francisco-aguayo-g", "nombre": "Francisco Aguayo",
        "por_que": ("«Francisco Aguayo G.» (SciELO 2006, Instituto Nacional del Tórax) y «Francisco Aguayo» "
                    "(PubMed 2022 y 2024, Universidad de Tarapacá) son la misma persona: el artículo de 2006 y el "
                    "de PubMed de 2007 sobre metilación de p16 en cáncer de pulmón en Chile comparten coautores "
                    "(Darwins Castillo, Leda Guzmán) y tema, y el registro ORCID de Francisco Aguayo González, de "
                    "la Universidad de Tarapacá, reclama como propio el de 2007. La «G.» es González."),
        "evidencia": [
            {"url": "https://orcid.org/0000-0002-9619-7535",
             "hecho": "El registro ORCID 0000-0002-9619-7535 corresponde a Francisco Aguayo González, con empleo en "
                      "el Departamento de Ciencias Biomédicas de la Universidad de Tarapacá, y reclama como obra "
                      "propia el artículo de PubMed 18449464 (2007)."},
            {"url": "https://pubmed.ncbi.nlm.nih.gov/18449464/",
             "hecho": "«High frequency of p16 promoter methylation in non-small cell lung carcinomas from Chile» "
                      "(Biol Res, 2007) lo firma «Aguayo FR» junto a Castillo D y Guzman LM, los mismos coautores "
                      "del artículo de SciELO de 2006 sobre p16INK4a en cáncer escamoso de pulmón."},
        ],
    },
    {
        "queda": "juan-carlos-diaz-patino", "absorbe": "juan-carlos-diaz-p", "nombre": "Juan Carlos Díaz Patiño",
        "por_que": ("«Juan Carlos Díaz P.» (Rev Med Chile 2016, Radiología del Hospital Clínico U. de Chile, TC de "
                    "tórax en EPOC) y «Juan Carlos Díaz Patiño» (Rev Med Chile 2018, Imágenes de Clínica Alemana, "
                    "neoplasia pulmonar quística) son la misma persona: la Facultad de Medicina de la U. de Chile "
                    "lista a «Dr. Juan Carlos Díaz Patiño, Prof. Asociado» como docente de su programa de "
                    "imagenología de tórax. La «P.» es Patiño; la doble afiliación universidad–clínica privada es "
                    "habitual. No es la misma persona que Orlando Díaz P., broncopulmonar de la PUC."),
        "evidencia": [
            {"url": "https://medichi.uchile.cl/estada-de-perfeccionamiento-en-imagenologia-de-torax-y-cardiovascular/",
             "hecho": "La Facultad de Medicina de la Universidad de Chile lista a «Dr. Juan Carlos Díaz Patiño — Prof. "
                      "Asociado — Facultad de Medicina U. de Chile» entre los docentes de su Estada de "
                      "Perfeccionamiento en Imagenología de Tórax y Cardiovascular."},
        ],
    },
]


def fusionar(base, f):
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}
    a, b = por_id.get(f["queda"]), por_id.get(f["absorbe"])
    if not a:
        sys.exit("No existe la ficha que queda: " + f["queda"])
    if not b:
        # Ya fusionada en una corrida anterior. Solo se asegura que la ficha que quedó recuerde el id
        # absorbido, para que los enlaces compartidos (#ficha=<id viejo>) sigan funcionando.
        if f["absorbe"] not in a.setdefault("ids_anteriores", []):
            a["ids_anteriores"].append(f["absorbe"])
            return True
        return False
    if a["tipo"] != "persona" or b["tipo"] != "persona":
        sys.exit("Solo se fusionan personas: %s, %s" % (a["id"], b["id"]))
    vistos = {(h.get("fuente_url"), h.get("hecho")) for h in a["hechos"]}
    for h in b["hechos"]:
        if (h.get("fuente_url"), h.get("hecho")) not in vistos:
            a["hechos"].append(h)
            vistos.add((h.get("fuente_url"), h.get("hecho")))
    for ev in f["evidencia"]:
        if (ev["url"], ev["hecho"]) not in vistos:
            a["hechos"].append({"tipo": "afiliacion", "hecho": ev["hecho"], "fuente_url": ev["url"],
                                "fecha": FECHA, "confianza": "pendiente"})
    ids = a.setdefault("ids_anteriores", [])
    for i in [b["id"]] + list(b.get("ids_anteriores") or []):
        if i not in ids:
            ids.append(i)
    alias = a.setdefault("alias_en_la_fuente", [])
    for n in [b["nombre"]] + list(b.get("alias_en_la_fuente") or []):
        if n not in alias and n != f["nombre"]:
            alias.append(n)
    a["nombre"] = f["nombre"]
    nota = "Ficha unificada el %s: %s %s" % (FECHA, f["por_que"], QUIEN)
    # Las notas que presentaban a las dos fichas como candidatas separadas ("NO se fusionan") son
    # justo lo que esta fusión resuelve: dejarlas contradiría a la nota nueva.
    previas = [x for x in (a.get("nota_identidad"), b.get("nota_identidad"))
               if x and "no se fusionan" not in x.lower()]
    a["nota_identidad"] = " ".join(previas + [nota])
    nuevos, claves = [], set()
    for v in vin:
        v = dict(v)
        if v["origen"] == b["id"]:
            v["origen"] = a["id"]
        if v["destino"] == b["id"]:
            v["destino"] = a["id"]
        if v["origen"] == v["destino"]:
            continue                     # dos fichas de la misma persona "coautoras" entre sí
        if a["id"] in (v["origen"], v["destino"]):
            # Solo se deduplican los vínculos de la ficha que queda: el resto de la base no se toca.
            k = (min(v["origen"], v["destino"]), max(v["origen"], v["destino"]), v["tipo"])
            if k in claves:
                continue
            claves.add(k)
        nuevos.append(v)
    vin[:] = nuevos
    ent[:] = [e for e in ent if e["id"] != b["id"]]
    return True


def main():
    registro = exclusiones.Registro()
    base = json.load(open(MUESTRA, encoding="utf-8"))
    hechas = [f["absorbe"] + " → " + f["queda"] for f in FUSIONES if fusionar(base, f)]
    if hechas:
        base["actualizado"] = datetime.date.today().isoformat()
        exclusiones.guardar_muestra(base, MUESTRA, registro)
    print("Fusiones aplicadas: %d%s" % (len(hechas), "".join("\n  " + h for h in hechas)))


if __name__ == "__main__":
    main()
