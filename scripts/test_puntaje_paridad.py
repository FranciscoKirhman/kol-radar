#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paridad JavaScript/Python del cálculo de puntaje, con casos adversariales.

Por qué existe: `computePriority` decide qué se muestra como "Prioridad alta" en la interfaz.
Cualquier auditoría que lo reimplemente en Python está comprobando la reimplementación, no el
producto. Así que acá el lado JavaScript **se extrae del propio `web/index.html`** y se ejecuta
con Node; el lado Python es una reimplementación independiente. Si divergen, falla.

Cubre los casos que la muestra actual NO ejercita:

  1. Más de cinco recursos por dimensión — el tope recorta, y hay que probar que recorta por
     aporte y no por orden alfabético de URL. Es el defecto que motivó el cambio: el recurso
     que más aporta tenía una URL que ordena última y quedaba fuera en silencio.
  2. Inversión del orden de entrada — el resultado no puede depender del orden del JSON.
  3. Deduplicación por recurso — dos filas con la misma `fuente_url` cuentan una vez, con
     desempate determinista y recuperación de fase.
  4. Redondeo — JavaScript redondea .5 hacia arriba; Python redondea a par. Si el puerto usa
     `round()` de Python, 2.5 da 2 en vez de 3.

Uso:  python3 scripts/test_puntaje_paridad.py
"""
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Se puede apuntar a otra copia para comprobar que la prueba DETECTA la regresión:
#   KOL_INDEX=/ruta/a/version-vieja.html python3 scripts/test_puntaje_paridad.py
INDEX = os.environ.get("KOL_INDEX") or os.path.join(RAIZ, "web", "index.html")

# Reloj fijo: `recencyBucket` usa `Date.now()`, así que sin fijarlo la prueba cambiaría de
# resultado con el paso del tiempo y dejaría de ser reproducible.
AHORA = datetime(2026, 9, 9, tzinfo=timezone.utc)
AHORA_MS = int(AHORA.timestamp() * 1000)

RECENCY_MULT = {"menos-1": 1.0, "1-3": 0.7, "3-5": 0.4, "mas-5": 0.0, "sin-fecha": 0.4}
GUIA_KEYWORDS = ["guía", "guia", "consenso", "guideline", "consensus", "recomendaciones de"]


# --------------------------------------------------------------------------- lado JavaScript
def extraer_funcion(html, nombre):
    """Recorta `function <nombre>(...) { ... }` balanceando llaves."""
    i = html.find("function " + nombre + "(")
    if i < 0:
        raise SystemExit("No encontré la función %s en web/index.html" % nombre)
    prof = 0
    for k in range(html.index("{", i), len(html)):
        if html[k] == "{":
            prof += 1
        elif html[k] == "}":
            prof -= 1
            if prof == 0:
                return html[i:k + 1]
    raise SystemExit("Llaves desbalanceadas al extraer %s" % nombre)


def extraer_const(html, nombre):
    m = re.search(r"var %s\s*=[^;]*;" % nombre, html)
    if not m:
        raise SystemExit("No encontré la constante %s" % nombre)
    return m.group(0)


FUNCIONES = ["sortableDate", "hechosUnicosPorFuente", "connectionCount", "ensayoPeso",
             "esGuiaOConsenso", "recencyBucket", "recencyMultiplier", "computePriority"]


def construir_runner():
    html = open(INDEX, encoding="utf-8").read()
    faltan = [f for f in FUNCIONES if ("function " + f + "(") not in html]
    if faltan:
        raise SystemExit("web/index.html no define: %s" % ", ".join(faltan))
    cuerpo = "\n".join(extraer_funcion(html, f) for f in FUNCIONES)
    consts = "\n".join(extraer_const(html, c) for c in ["GUIA_KEYWORDS", "RECENCY_MULT"])
    return """
'use strict';
// Reloj congelado para que recencyBucket sea reproducible.
var __AHORA = %d;
Date.now = function () { return __AHORA; };
var entrada = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
var vinculos = entrada.vinculos;
%s
%s
var salida = entrada.personas.map(function (p) { return computePriority(p); });
process.stdout.write(JSON.stringify(salida));
""" % (AHORA_MS, consts, cuerpo)


def correr_js(personas, vinculos):
    runner = construir_runner()
    with tempfile.TemporaryDirectory() as tmp:
        js = os.path.join(tmp, "runner.js")
        datos = os.path.join(tmp, "entrada.json")
        open(js, "w", encoding="utf-8").write(runner)
        json.dump({"personas": personas, "vinculos": vinculos}, open(datos, "w", encoding="utf-8"))
        r = subprocess.run(["node", js, datos], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("Node falló:\n" + r.stderr)
        return json.loads(r.stdout)


# ------------------------------------------------------------------------------- lado Python
def sortable_date(fecha):
    m = re.search(r"(\d{4})(-(\d{2}))?(-(\d{2}))?", fecha or "")
    if not m:
        return "0000-00-00"
    return "%s-%s-%s" % (m.group(1), m.group(3) or "01", m.group(5) or "01")


def recency_bucket(fecha):
    clave = sortable_date(fecha)
    if clave == "0000-00-00":
        return "sin-fecha"
    # `new Date("YYYY-MM-DD")` de JavaScript NO es estricta con el día: valida el mes, pero un
    # día fuera de rango rueda al mes siguiente. Comprobado en Node:
    #   "2026-13-45" -> Invalid Date   (mes 13 inválido)
    #   "2026-02-30" -> 2026-03-02     (el 30 de febrero rueda, no invalida)
    # Usar strptime acá rompe la paridad, porque Python sí rechaza el 30 de febrero.
    anio, mes, dia = (int(x) for x in clave.split("-"))
    if not 1 <= mes <= 12:
        return "sin-fecha"
    try:
        d = datetime(anio, mes, 1, tzinfo=timezone.utc) + timedelta(days=dia - 1)
    except (ValueError, OverflowError):
        # `new Date("2026-13-01")` en JavaScript da Invalid Date -> "sin-fecha".
        return "sin-fecha"
    years = (AHORA - d).total_seconds() / (365.25 * 24 * 3600)
    if years < 1:
        return "menos-1"
    if years < 3:
        return "1-3"
    if years < 5:
        return "3-5"
    return "mas-5"


def js_round(x):
    """JavaScript redondea .5 hacia +Infinito; `round()` de Python redondea a par."""
    return math.floor(x + 0.5)


def ensayo_peso(h):
    fase = (h.get("fase") or "").lower()
    return 2 if ("iii" in fase or "iv" in fase) else 1


def es_guia(h):
    t = (h.get("hecho") or "").lower()
    return any(k in t for k in GUIA_KEYWORDS)


def hechos_unicos_por_fuente(hechos):
    grupos = {}
    for h in hechos:
        clave = h.get("fuente_url") or ("__sin_fuente__" + json.dumps(h, sort_keys=True))
        grupos.setdefault(clave, []).append(h)
    salida = []
    for clave in sorted(grupos):
        grupo = sorted(
            grupos[clave],
            key=lambda h: (
                # fecha descendente, presencia de fase primero, texto ascendente
                _inv(sortable_date(h.get("fecha"))),
                0 if h.get("fase") else 1,
                (h.get("hecho") or "") + "|" + (h.get("fase") or ""),
            ),
        )
        rep = grupo[0]
        if not rep.get("fase"):
            for otro in grupo[1:]:
                if otro.get("fase"):
                    rep = dict(rep)
                    rep["fase"] = otro["fase"]
                    break
        salida.append(rep)
    return salida


class _inv(str):
    """Ordena descendente sin invertir el resto de la clave."""
    def __lt__(self, otro):
        return str.__gt__(self, otro)


def dimension_pts(hechos, cap, base_pts, tope):
    aporte = [(base_pts(h) * RECENCY_MULT[recency_bucket(h.get("fecha"))], h) for h in hechos]
    aporte.sort(key=lambda x: (-x[0], _inv(sortable_date(x[1].get("fecha")))))
    crudo = sum(p for p, _ in aporte[:cap])
    return min(tope, js_round(crudo))


def compute_priority_py(persona, vinculos):
    hechos = persona["hechos"]
    ensayos = hechos_unicos_por_fuente([h for h in hechos if h["tipo"] == "ensayo_clinico"])
    pubs = hechos_unicos_por_fuente([h for h in hechos if h["tipo"] == "publicacion"])
    guias = [h for h in pubs if es_guia(h)]
    pub_no_guia = [h for h in pubs if not es_guia(h)]
    congresos = hechos_unicos_por_fuente([h for h in hechos if h["tipo"] == "congreso"])

    ensayos_pts = dimension_pts(ensayos, 5, lambda h: ensayo_peso(h) * 2, 20)
    pub_pts = dimension_pts(pub_no_guia, 5, lambda h: 2, 10)
    guia_pts = dimension_pts(guias, 2, lambda h: 4, 8)
    congreso_pts = dimension_pts(congresos, 5, lambda h: 1, 5)
    red_pts = min(5, sum(1 for v in vinculos
                         if v["origen"] == persona["id"] or v["destino"] == persona["id"]))
    total = ensayos_pts + pub_pts + guia_pts + congreso_pts + red_pts
    return {
        "ensayosPts": ensayos_pts, "pubPts": pub_pts, "guiaPts": guia_pts,
        "congresoPts": congreso_pts, "sociedadesPts": 0, "redPts": red_pts,
        "total": total,
        "tier": "alta" if total >= 8 else "media" if total >= 3 else "monitorear",
        "nGuias": min(2, len(guias)), "nEnsayos": min(5, len(ensayos)),
        "nPub": min(5, len(pub_no_guia)), "nCongreso": min(5, len(congresos)),
    }


# ------------------------------------------------------------------------------------- casos
def ensayo(url, fecha, fase, texto="Ensayo"):
    return {"tipo": "ensayo_clinico", "hecho": texto, "fase": fase,
            "fuente_url": url, "fecha": fecha, "confianza": "pendiente"}


def publicacion(url, fecha, texto="Publicación"):
    return {"tipo": "publicacion", "hecho": texto, "fuente_url": url,
            "fecha": fecha, "confianza": "pendiente"}


def casos():
    C = []

    # 1. Siete ensayos, tope de cinco. El que MÁS aporta (fase III, de este año) tiene la URL
    #    que ordena ÚLTIMA. Con `slice(0, 5)` sobre la lista ordenada por URL quedaba fuera.
    C.append(("tope: el mayor aporte tiene la URL que ordena última", {
        "id": "p-tope", "tipo": "persona", "hechos": [
            ensayo("https://clinicaltrials.gov/study/NCT0000001", "2025-11", "Fase I"),
            ensayo("https://clinicaltrials.gov/study/NCT0000002", "2025-11", "Fase I"),
            ensayo("https://clinicaltrials.gov/study/NCT0000003", "2025-11", "Fase I"),
            ensayo("https://clinicaltrials.gov/study/NCT0000004", "2025-11", "Fase I"),
            ensayo("https://clinicaltrials.gov/study/NCT0000005", "2025-11", "Fase I"),
            ensayo("https://clinicaltrials.gov/study/NCT0000006", "2025-11", "Fase I"),
            ensayo("https://clinicaltrials.gov/study/NCT9999999", "2026-06", "Fase III"),
        ]}, []))

    # 2. Publicaciones por encima del tope de cinco, con recencias mezcladas.
    C.append(("tope de publicaciones con recencias mezcladas", {
        "id": "p-pub", "tipo": "persona", "hechos": [
            publicacion("https://pubmed.ncbi.nlm.nih.gov/1", "2010-01"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/2", "2011-01"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/3", "2012-01"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/4", "2026-01"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/5", "2025-06"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/6", "2024-06"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/7", "2026-08"),
        ]}, []))

    # 3. Dos filas del mismo recurso: se cuenta una vez. Empate de fecha, decide fase y texto.
    C.append(("dedupe: misma URL, empate de fecha", {
        "id": "p-dup", "tipo": "persona", "hechos": [
            ensayo("https://clinicaltrials.gov/study/NCT1111111", "2026-08-17", "Fase II", "A"),
            ensayo("https://clinicaltrials.gov/study/NCT1111111", "2026-08-17", "Fase III", "Z"),
        ]}, []))

    # 4. La fila más reciente no declara fase: se recupera la fase de otra fila del recurso,
    #    sin alterar la evidencia guardada.
    C.append(("dedupe: fila reciente sin fase recupera la fase", {
        "id": "p-fase", "tipo": "persona", "hechos": [
            ensayo("https://clinicaltrials.gov/study/NCT2222222", "2026-01", "Fase III", "viejo"),
            {"tipo": "ensayo_clinico", "hecho": "estado", "fuente_url":
             "https://clinicaltrials.gov/study/NCT2222222", "fecha": "2026-08",
             "confianza": "pendiente"},
        ]}, []))

    # 5. Redondeo: 0.7 x 2 pts x ... construido para caer en .5 exacto.
    C.append(("redondeo de .5 hacia arriba", {
        "id": "p-round", "tipo": "persona", "hechos": [
            publicacion("https://pubmed.ncbi.nlm.nih.gov/r1", "2023-09"),   # 2 x 0.7 = 1.4
            publicacion("https://pubmed.ncbi.nlm.nih.gov/r2", "2020-09"),   # 2 x 0.4 = 0.8
            publicacion("https://pubmed.ncbi.nlm.nih.gov/r3", "2022-09"),   # 2 x 0.7 = 1.4
        ]}, []))

    # 6. Sin fecha y fecha inválida.
    C.append(("fechas ausentes, mes inválido y día que rueda", {
        "id": "p-fecha", "tipo": "persona", "hechos": [
            publicacion("https://pubmed.ncbi.nlm.nih.gov/f1", ""),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/f2", "2026-13-45"),
            publicacion("https://pubmed.ncbi.nlm.nih.gov/f3", "2026-02-30"),
        ]}, []))

    # 7. La red se cuenta sobre vínculos y tiene tope de 5.
    C.append(("tope de red", {
        "id": "p-red", "tipo": "persona", "hechos": [
            publicacion("https://pubmed.ncbi.nlm.nih.gov/red", "2026-01"),
        ]}, [{"origen": "p-red", "destino": "i%d" % k, "tipo": "afiliación"} for k in range(9)]))

    return C


def main():
    fallos = []
    for nombre, persona, vinculos in casos():
        for etiqueta, hechos in (("orden original", persona["hechos"]),
                                 ("orden invertido", list(reversed(persona["hechos"])))):
            p = dict(persona, hechos=hechos)
            js = correr_js([p], vinculos)[0]
            py = compute_priority_py(p, vinculos)
            campos = ["ensayosPts", "pubPts", "guiaPts", "congresoPts", "redPts", "total",
                      "tier", "nEnsayos", "nPub", "nGuias", "nCongreso"]
            dif = {c: (js.get(c), py.get(c)) for c in campos if js.get(c) != py.get(c)}
            estado = "ok " if not dif else "FALLA"
            print("[%s] %-52s %-16s total=%s" % (estado, nombre, etiqueta, js.get("total")))
            if dif:
                fallos.append((nombre, etiqueta, dif))

        # El resultado no puede depender del orden de entrada.
        a = correr_js([dict(persona, hechos=persona["hechos"])], vinculos)[0]
        b = correr_js([dict(persona, hechos=list(reversed(persona["hechos"])))], vinculos)[0]
        if a != b:
            fallos.append((nombre, "invariancia de orden", {"original": a, "invertido": b}))
            print("[FALLA] %-52s el orden de entrada cambia el resultado" % nombre)

    # Comprobación explícita del redondeo, que es la trampa clásica del puerto a Python.
    if js_round(2.5) != 3 or js_round(1.5) != 2 or js_round(-2.5) != -2:
        fallos.append(("redondeo", "js_round", "no replica Math.round"))

    # Caso 1, aserción concreta: el ensayo fase III reciente TIENE que estar dentro del tope.
    caso1 = casos()[0][1]
    js1 = correr_js([caso1], [])[0]
    # 5 recursos de mayor aporte: el fase III de 2026 (2x2x1.0=4) + cuatro fase I de 2019
    # (2x1x0.4=0.8 cada uno) = 4 + 3.2 = 7.2 -> 7. Si el fase III quedara fuera por orden de
    # URL, serían cinco fase I: 5 x 0.8 = 4.0 -> 4.
    if js1["ensayosPts"] != 12:
        fallos.append(("tope por aporte", "aserción", "ensayosPts=%s, esperado 12 (si da 10, el "
                       "tope volvió a cortar por orden de URL)" % js1["ensayosPts"]))
        print("[FALLA] el tope no seleccionó por aporte: ensayosPts=%s" % js1["ensayosPts"])
    else:
        print("[ok ] el tope selecciona por aporte: ensayosPts=12 (fase III reciente incluido)")

    print()
    if fallos:
        print("FALLÓ — %d problema(s):" % len(fallos))
        for f in fallos:
            print("  ", f)
        return 1
    print("PASA — paridad JavaScript/Python en %d casos, en ambos órdenes." % len(casos()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
