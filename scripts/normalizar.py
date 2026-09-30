#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Texto de sede de ClinicalTrials.gov → institución canónica, solo por alias documentado.

integrar_beta.py y preintegracion_clinicaltrials.py importaban un módulo `normalizar` que vivía en el
scratchpad de una sesión y nunca llegó al repositorio, así que ninguna de las dos se podía repetir.
Este archivo lo reconstruye a partir de lo que sí está en el repo:

  - la tabla de alias de la preintegración del 2026-09-09
    (data/pending/preintegracion-clinicaltrials-2026-09-09/instituciones_candidatas.json), y
  - los `alias_en_la_fuente` de cada institución de la muestra, que cada script que liga una sede
    agrega junto con su motivo (resolver_sedes_web.py, integrar_estudiosclinicos_cl.py,
    integrar_isp_inspecciones.py).

Tres cosas, las mismas que usaban los scripts:
  norm(texto)       minúsculas, sin tildes, espacios colapsados.
  PLACEHOLDER       marcadores del patrocinador ("Research Site", "Local Institution - 0024",
                    "Site CL56001"): no nombran una institución y no crean nada.
  resolver(texto)   (id, nombre) de la institución si el texto es un alias documentado, o None.
                    Nunca por parecido: primero el texto exacto (normalizado); si no, el texto sin el
                    código de sitio que agregan los patrocinadores ("FALP ( Site 9999)" → "FALP"), que
                    tiene que ser a su vez un alias documentado.
"""
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE = os.path.join(RAIZ, "data", "pending", "preintegracion-clinicaltrials-2026-09-09", "instituciones_candidatas.json")
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")


def norm(texto):
    s = unicodedata.normalize("NFD", texto or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"\s+", " ", s).strip()


# Reconstruido de los 198 textos que la preintegración descartó como marcadores
# (placeholders_excluidos.json). Algunos llevan el nombre de un centro delante
# ("orlandi oncologia general salvo 159, providencia_investigational site number :1520005"): igual
# se descartaban, porque el alias documentado no incluye esa forma.
PLACEHOLDER = re.compile(
    r"(.*(investigational|investigative) site.*"
    r"|local institution\b.*"
    r"|research site\b.*"
    r"|site cl\d+.*"
    r"|.*\badministrative office\b.*"
    r"|.*\bclinical trials call center\b.*"
    r"|sanofi-aventis( chile)?)$")

CODIGO_SITIO = re.compile(r"\s*(\(\s*site\s*[\w-]+\s*\)|/\s*id#\s*\d+|-\s*site\s*\d+)\s*$", re.I)

_TABLA = None


def _tabla():
    global _TABLA
    if _TABLA is not None:
        return _TABLA
    tabla = {}
    nombres = {}
    if os.path.exists(MUESTRA):
        for e in json.load(open(MUESTRA, encoding="utf-8"))["entidades"]:
            if e["tipo"] != "institucion":
                continue
            nombres[e["id"]] = e["nombre"]
            for t in [e["nombre"]] + list(e.get("alias_en_la_fuente") or []):
                if not PLACEHOLDER.match(norm(t)):
                    tabla.setdefault(norm(t), e["id"])
    if os.path.exists(PRE):
        for inst in json.load(open(PRE, encoding="utf-8")):
            nombres.setdefault(inst["id_canonico"], inst["nombre_canonico"])
            for t, _ in inst["alias_textuales_en_la_fuente"]:
                tabla.setdefault(norm(t), inst["id_canonico"])
    # Los alias NO se recortan: "Centro de Investigaciones ( Site 0511)" es alias de un centro de Viña
    # del Mar, pero "Centro de Investigaciones" a secas no identifica a nadie. Solo se recorta el
    # texto que se busca (ver resolver).
    _TABLA = {t: (iid, nombres.get(iid, iid)) for t, iid in tabla.items()}
    return _TABLA


def resolver(texto):
    t = norm(texto)
    if not t:
        return None
    tabla = _tabla()
    return tabla.get(t) or tabla.get(norm(CODIGO_SITIO.sub("", t)))
