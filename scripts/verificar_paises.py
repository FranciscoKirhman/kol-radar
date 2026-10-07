#!/usr/bin/env python3
"""Comprueba que los JSON publicados y las bandejas nuevas respeten la barrera legal."""
import argparse
import hashlib
import json
import os
import sys

import paises

RAIZ = paises.RAIZ
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
PENDING = os.path.join(RAIZ, "data", "pending")
PUBLICADO = os.path.join(RAIZ, "data", "publicado")
LEGACY = os.path.join(RAIZ, "data", "config", "pending_chile_legacy.json")


def _personales(obj):
    """Ubica objetos que contienen datos personales, incluso candidatos sin tipo persona."""
    if isinstance(obj, dict):
        if obj.get("tipo") == "persona" or any(paises.CLAVES_PERSONALES.search(k) for k in obj):
            yield obj
        for valor in obj.values():
            yield from _personales(valor)
    elif isinstance(obj, list):
        for valor in obj:
            yield from _personales(valor)


def verificar_muestra(ruta):
    with open(ruta, encoding="utf-8") as f:
        return paises.comprobar_publicacion(json.load(f))


def verificar_pendientes():
    with open(LEGACY, encoding="utf-8") as f:
        huellas = json.load(f)["archivos"]
    errores = []
    for carpeta, _, archivos in os.walk(PENDING):
        for nombre in archivos:
            ruta = os.path.join(carpeta, nombre)
            rel = os.path.relpath(ruta, RAIZ)
            digest = hashlib.sha256(open(ruta, "rb").read()).hexdigest()
            if huellas.get(rel) == digest:
                continue
            partes = rel.split(os.sep)
            # Los nuevos artefactos personales solo se aceptan bajo data/pending/ISO2/.
            iso = partes[2].upper() if len(partes) > 3 and len(partes[2]) == 2 else None
            if not paises.permitido_publicar_personas(iso):
                errores.append("%s: bandeja nueva fuera de un país aprobado; usar almacenamiento privado" % rel)
                continue
            if not nombre.endswith(".json"):
                errores.append("%s: archivo pendiente nuevo sin revisión de país" % rel)
                continue
            try:
                obj = json.load(open(ruta, encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errores.append("%s: JSON ilegible: %s" % (rel, exc))
                continue
            for personal in _personales(obj):
                declarado = paises.pais_registro(personal)
                if declarado and not paises.permitido_publicar_personas(declarado):
                    errores.append("%s: dato personal de país no aprobado" % rel)
    return errores


def verificar_publicado():
    errores = []
    if not os.path.isdir(PUBLICADO):
        return errores
    for carpeta, _, archivos in os.walk(PUBLICADO):
        for nombre in archivos:
            if not nombre.endswith(".json"):
                continue
            ruta = os.path.join(carpeta, nombre)
            obj = json.load(open(ruta, encoding="utf-8"))
            if isinstance(obj, dict) and "entidades" in obj:
                errores += [os.path.relpath(ruta, RAIZ) + ": " + e
                            for e in paises.comprobar_publicacion(obj)]
            elif any(_personales(obj)):
                errores.append(os.path.relpath(ruta, RAIZ) + ": datos personales fuera del esquema comprobado")
    return errores


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--muestra", default=MUESTRA, help="JSON de prueba; también revisa pending y publicado")
    a = ap.parse_args()
    errores = verificar_muestra(a.muestra) + verificar_pendientes() + verificar_publicado()
    for error in errores:
        print("ERROR: " + error, file=sys.stderr)
    if errores:
        return 1
    print("OK — ningún dato personal detectado de país no aprobado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
