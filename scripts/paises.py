#!/usr/bin/env python3
"""Puerta de publicación por país de afiliación, cerrada por defecto.

La aprobación es una decisión humana en data/config/paises.json. La lista legacy
solo reconoce las fichas chilenas que ya estaban en main; ninguna ficha nueva
puede omitir pais_afiliacion.
"""
import json
import os
import re
import hashlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(RAIZ, "data", "config", "paises.json")
LEGACY = os.path.join(RAIZ, "data", "config", "personas_chile_legacy.json")
APROBADOS = ("allowed", "allowed_with_conditions")
ESTADOS = APROBADOS + ("blocked",)


def configuracion():
    with open(CONFIG, encoding="utf-8") as f:
        filas = json.load(f)
    if not isinstance(filas, list):
        raise ValueError("paises.json debe contener una lista")
    salida = {}
    for fila in filas:
        iso = fila.get("iso2")
        if not isinstance(iso, str) or len(iso) != 2 or iso != iso.upper() or iso in salida:
            raise ValueError("ISO2 inválido o duplicado en paises.json: %r" % iso)
        if fila.get("estado_propuesto") not in ESTADOS or fila.get("estado_aprobado") not in ESTADOS + (None,):
            raise ValueError("Estado inválido para %s" % iso)
        salida[iso] = fila
    return salida


def estado(iso2):
    """Estado aprobado; país desconocido, no aprobado o mal formado = blocked."""
    if not isinstance(iso2, str):
        return "blocked"
    fila = configuracion().get(iso2.upper())
    return fila["estado_aprobado"] if fila and fila["estado_aprobado"] in APROBADOS else "blocked"


def permitido_publicar_personas(iso2):
    return estado(iso2) in APROBADOS


def paises_activos():
    return [f for f in configuracion().values() if f["estado_aprobado"] in APROBADOS]


def pais_afiliacion(entidad):
    """La ubicación del usuario o del ensayo nunca sustituye la afiliación personal."""
    iso = entidad.get("pais_afiliacion")
    if isinstance(iso, str) and len(iso) == 2:
        return iso.upper()
    with open(LEGACY, encoding="utf-8") as f:
        nombres = json.load(f)["sha256_nombre_por_id"]
    nombre = entidad.get("nombre")
    if (isinstance(nombre, str) and
            nombres.get(entidad.get("id")) == hashlib.sha256(nombre.casefold().encode()).hexdigest()):
        return "CL"
    return None


def pais_registro(obj):
    """País asociado a un hecho, vínculo o entidad no personal, si está declarado."""
    iso = obj.get("pais_afiliacion") or obj.get("pais")
    return iso.upper() if isinstance(iso, str) and len(iso) == 2 else None


CLAVES_PERSONALES = re.compile(r"(investig|contact|person|autor|researcher|physician|doctor)", re.I)


def _textos(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for valor in obj.values():
            yield from _textos(valor)
    elif isinstance(obj, list):
        for valor in obj:
            yield from _textos(valor)


def comprobar_publicacion(base):
    """Devuelve errores; nunca elimina datos en silencio para que el editor revise."""
    errores = []
    entidades = base.get("entidades", [])
    personas = {e.get("id"): e for e in entidades if e.get("tipo") == "persona"}
    bloqueadas = []
    for e in entidades:
        iso = pais_afiliacion(e) if e.get("tipo") == "persona" else pais_registro(e)
        if e.get("tipo") == "persona" and not permitido_publicar_personas(iso):
            bloqueadas.append(e)
            errores.append("persona %s: país de afiliación %s no aprobado" % (e.get("id"), iso))
        if e.get("tipo") != "persona" and iso and not permitido_publicar_personas(iso):
            for clave in e:
                if CLAVES_PERSONALES.search(clave):
                    errores.append("%s: campo personal %s en país no aprobado" % (e.get("id"), clave))
            if e.get("hechos"):
                errores.append("%s: hechos narrativos de país no aprobado requieren revisión antes de publicar" % e.get("id"))
    for v in base.get("vinculos", []):
        iso = pais_registro(v)
        if iso and not permitido_publicar_personas(iso) and (
                v.get("origen") in personas or v.get("destino") in personas or
                any(CLAVES_PERSONALES.search(k) for k in v)):
            errores.append("vínculo personal de país no aprobado: %s" % v.get("origen"))
    for persona in bloqueadas:
        nombre = persona.get("nombre")
        if not nombre:
            continue
        for e in entidades:
            if e is persona:
                continue
            if any(nombre.casefold() in t.casefold() for t in _textos(e)):
                errores.append("%s: menciona a persona de país no aprobado" % e.get("id"))
        for v in base.get("vinculos", []):
            if any(nombre.casefold() in t.casefold() for t in _textos(v)):
                errores.append("vínculo menciona a persona de país no aprobado")
    return sorted(set(errores))
