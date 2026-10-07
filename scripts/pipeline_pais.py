"""Parámetros y rutas de recolección por país. No decide aprobaciones legales."""
import json
import os
from pathlib import Path

import paises

RAIZ = Path(__file__).resolve().parent.parent


def configurar(iso2):
    iso2 = iso2.upper()
    fila = paises.configuracion().get(iso2)
    if not fila:
        raise ValueError("País sin configuración: %s" % iso2)
    return fila


def nombre_ctgov(fila):
    nombre = fila.get("nombre_ctgov")
    if not nombre and fila["iso2"] in ("CL", "AR"):
        nombre = fila["nombre"]
    if not nombre:
        raise ValueError("Falta nombre_ctgov en paises.json para %s" % fila["iso2"])
    return nombre


def cache(fila):
    # KOL_CACHE facilita pruebas aisladas. Ningún valor permite eludir validar_destino.
    return Path(os.environ.get("KOL_CACHE", str(Path.home() / ".cache" / "kol-radar"))) / fila["iso2"]


def validar_destino(ruta, fila, siempre_privado=False):
    ruta = Path(ruta).expanduser().resolve()
    if siempre_privado or not paises.permitido_publicar_personas(fila["iso2"]):
        if ruta == RAIZ or RAIZ in ruta.parents:
            raise ValueError("Datos personales de %s: la salida debe estar FUERA del repositorio" % fila["iso2"])
    return str(ruta)


def carpeta_pre(fila, fecha):
    raiz = (RAIZ / "data" / "pending" / fila["iso2"] if fila["iso2"] == "CL" and
            paises.permitido_publicar_personas("CL") else cache(fila))
    return raiz / ("preintegracion-clinicaltrials-" + fecha)


def resolver_sede(texto, fila, normalizador):
    # El catálogo legado documenta alias chilenos; jamás lo aplicar a otro país.
    if fila["iso2"] == "CL":
        return normalizador.resolver(texto)
    return None


def cargar_crudo(ruta, fila):
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    for lista in datos.values():
        for ensayo in lista:
            # Compatibilidad con descargas CL anteriores a la parametrización.
            if ensayo.get("pais", "CL") != fila["iso2"]:
                raise ValueError("La descarga no corresponde al país solicitado")
    return datos


def fuente_habilitada(fila, fuente):
    return fuente in fila.get("fuentes_nacionales", [])


def exigir_fuente_chilena(iso2, fuente):
    fila = configurar(iso2)
    if fila["iso2"] != "CL" or not fuente_habilitada(fila, fuente):
        raise SystemExit("%s es una fuente exclusiva de CL; %s no la declara en paises.json" %
                         (fuente, fila["iso2"]))
    return fila
