#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clasifica cada fármaco por tipo usando el NCI Thesaurus (NCIt).

Un MSL filtra fármacos por tipo —inmunoterapia, terapia dirigida, quimioterapia, conjugado
anticuerpo-fármaco— y esa clasificación no se puede inventar ni deducir del nombre. El NCI
Thesaurus del Instituto Nacional del Cáncer de EE. UU. la publica para cada agente, incluidos los
que todavía están en investigación, con una jerarquía navegable ("Pembrolizumab > Anti-PD1
Monoclonal Antibody > PD1 Inhibitor > Immune Checkpoint Inhibitor > ...").

Reglas:
  1. Se busca el concepto por el nombre de la ficha; si no aparece, por cada nombre con que la
     fuente lo escribe (marcas, códigos). Solo se acepta una coincidencia exacta (type=match).
  2. Se leen todos los caminos del concepto hasta la raíz, y la clase se asigna por la PRIMERA regla
     de CLASES cuyos ancestros aparecen en algún camino. El orden importa y es explícito: un
     conjugado anticuerpo-fármaco también es anticuerpo y también lleva un citotóxico, así que va
     primero.
  3. La ficha guarda la clase, el padre inmediato en el NCIt (lo más específico: "Anti-PD1
     Monoclonal Antibody") y un hecho con la URL del concepto. Si no hay concepto, queda
     "Sin clasificar" — no se adivina.
  4. "Sin clasificar" quiere decir que el tesauro no lo tiene, no que la consulta falló. Si la API
     no responde para un fármaco, ese fármaco conserva la clase que ya tenía, la corrida lo lista y
     termina con código de salida 1: una corrida sin red no puede borrar clasificaciones en silencio.
  5. Nada se confirma: todo entra `pendiente`.

Se corre DESPUÉS de integrar_farmacos_ctgov.py, que recrea los fármacos desde cero.

Uso:  python3 scripts/clasificar_farmacos_ncit.py [carpeta_cache]
"""
import datetime
import json
import os
import re
import socket
import sys
import time
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = datetime.date.today().isoformat()
SALIDA = os.path.join(RAIZ, "data", "pending", "clases-ncit-" + FECHA)
API = "https://api-evsrest.nci.nih.gov/api/v1/concept/ncit"
PAGINA = "https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/"

# La API responde por IPv4 en un segundo; por IPv6 la conexión queda colgada hasta el timeout
# (medido: 81 s por consulta desde Python, 1 s con curl). Se fuerza IPv4.
_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = lambda host, *a, **k: [r for r in _getaddrinfo(host, *a, **k) if r[0] == socket.AF_INET] or _getaddrinfo(host, *a, **k)

# (clase visible, patrones sobre los nombres de ancestros). Primera que calza, gana. El orden es
# la decisión: el tesauro cuelga las antraciclinas también de "Signal Transduction Inhibitor", así
# que quimioterapia va antes que terapia dirigida; y un factor estimulante de colonias es también
# "Immunotherapeutic Agent", así que el soporte específico va antes que "otra inmunoterapia".
CLASES = [
    ("Conjugado anticuerpo-fármaco", [r"antibody-drug conjugate", r"^antibody drug conjugate"]),
    ("Inmunoterapia (checkpoint)", [r"immune checkpoint inhibitor"]),
    ("Anticuerpo biespecífico", [r"bispecific antibody", r"t-cell engaging"]),
    ("Terapia celular, génica o vacuna", [r"vaccine", r"cell therapy",
                                           r"cellular therapy", r"gene therapy", r"oncolytic virus", r"car t"]),
    ("Radiofármaco", [r"radiopharmaceutical", r"radioconjugate", r"radioisotope"]),
    ("Quimioterapia", [r"cytotoxic chemotherapeutic agent", r"antimetabolite", r"alkylating agent",
                       r"topoisomerase inhibitor", r"antimitotic", r"anthracycline", r"regimen", r"asparaginase"]),
    ("Terapia hormonal", [r"hormone therapy", r"hormonal", r"antiandrogen", r"androgen receptor",
                          r"aromatase inhibitor", r"estrogen receptor", r"gonadotropin", r"gnrh", r"lhrh",
                          r"antiestrogen", r"steroid synthesis inhibitor", r"cyp17", r"cyp11a1"]),
    ("Soporte", [r"colony[- ]stimulating factor", r"erythropoie", r"antiemetic", r"bisphosphonate",
                 r"folic acid derivative", r"^adjuvant$", r"hyaluronidase"]),
    ("Terapia dirigida", [r"targeted therapy agent", r"kinase inhibitor", r"poly \(adp-ribose\) polymerase inhibitor",
                          r"antineoplastic antibody", r"proteasome inhibitor", r"kras", r"bcl-2", r"hif-2",
                          r"angiogenesis inhibitor", r"signal transduction inhibitor", r"mtor", r"hedgehog",
                          r"histone deacetylase", r"hdac", r"cdk", r"ezh2", r"menin", r"idh", r"prmt5",
                          r"protein degrader", r"antineoplastic enzyme inhibitor"]),
    ("Otra inmunoterapia", [r"immunotherapeutic agent", r"immunomodulat", r"cytokine", r"interleukin", r"interferon"]),
    # Lo que el tesauro conoce pero no calza en ninguna clase de arriba: un agente en investigación
    # con un mecanismo nuevo, por ejemplo. Antes caía en "Soporte y otros", que lo hacía pasar por
    # un medicamento de soporte.
    ("Otros agentes", [r".*"]),
]
# Calificativos que la fuente agrega al nombre y que el tesauro no tiene: si el nombre entero no
# aparece, se busca sin ellos ("Bevacizumab biosimilar" → "Bevacizumab").
CALIFICATIVOS = r"\b(biosimilar|weekly|combined|sequential|combination|co-formulation|fixed[- ]dose|for injection|" \
                r"injection|hydrochloride|hcl|itu|for subcutaneous administration|of)\b"


FALLAS = []   # URL que no respondieron en esta corrida


def pedir(url, cache):
    clave = os.path.join(cache, re.sub(r"[^A-Za-z0-9]+", "_", url)[-180:] + ".json") if cache else None
    if clave and os.path.exists(clave):
        return json.load(open(clave, encoding="utf-8"))
    for intento in range(3):
        try:
            d = json.load(urllib.request.urlopen(url, timeout=40))
            break
        except Exception:
            time.sleep(2 + intento * 3)
    else:
        FALLAS.append(url)
        return None
    time.sleep(0.25)
    if clave:
        json.dump(d, open(clave, "w", encoding="utf-8"))
    return d


def buscar(termino, cache):
    q = urllib.parse.urlencode({"term": termino, "type": "match", "pageSize": 5})
    d = pedir(API + "/search?" + q, cache)
    conceptos = (d or {}).get("concepts") or []
    exactos = [c for c in conceptos if c["name"].lower() == termino.lower()]
    return (exactos or conceptos or [None])[0]


def clasificar(caminos):
    ancestros = {x["name"].lower() for p in caminos for x in p[1:]}
    for clase, patrones in CLASES:
        for a in sorted(ancestros):
            if any(re.search(pt, a) for pt in patrones):
                return clase, a
    return "Sin clasificar", None


def main():
    # Antes de cualquier consulta: si hay exclusiones y falta la clave, se detiene acá y no al
    # final de la corrida. Ver scripts/exclusiones.py.
    registro = exclusiones.Registro()
    cache = sys.argv[1] if len(sys.argv) > 1 else None
    if cache:
        os.makedirs(cache, exist_ok=True)
    base = json.load(open(MUESTRA, encoding="utf-8"))
    decisiones, no_consultados = [], []
    for f in [e for e in base["entidades"] if e["tipo"] == "farmaco"]:
        fallas_antes = len(FALLAS)
        previo = {k: f[k] for k in ("clase", "clase_ncit", "ncit") if k in f}
        previos_hechos = list(f["hechos"])
        f["hechos"] = [h for h in f["hechos"] if not (h.get("fuente_url") or "").startswith(PAGINA)]
        for k in ("clase", "clase_ncit", "ncit"):
            f.pop(k, None)
        concepto, termino = None, None
        limpio = re.sub(r"\s+", " ", re.sub(CALIFICATIVOS, " ", f["nombre"], flags=re.I)).strip(" -")
        palabras = [w for w in re.split(r"[\s/-]+", limpio) if len(w) >= 6 and w.isalpha()]
        directos = [f["nombre"]] + list(f.get("alias_en_la_fuente") or [])
        for t in directos + [limpio] + palabras:
            concepto = buscar(t, cache)
            if not concepto:
                continue
            # Por una palabra suelta, solo vale un concepto que el tesauro clasifique como sustancia
            # farmacológica: "Liposomal", de "Liposomal doxorubicin", es un tipo de micela.
            if t not in directos:
                cam = pedir(API + "/" + concepto["code"] + "/pathsToRoot", cache) or []
                if not any(x["name"] == "Pharmacologic Substance" for p in cam for x in p):
                    concepto = None
                    continue
            termino = t
            break
        fila = {"id": f["id"], "nombre": f["nombre"], "buscado_como": termino}
        if len(FALLAS) > fallas_antes:
            # La API no respondió para este fármaco: no se sabe si el tesauro lo tiene. Se deja
            # como estaba y se informa, en vez de marcarlo "Sin clasificar".
            f.update(previo)
            f["hechos"] = previos_hechos
            fila["clase"] = "No consultado (se mantiene: %s)" % previo.get("clase", "sin clase previa")
            no_consultados.append(f["nombre"])
            decisiones.append(fila)
            continue
        if not concepto:
            f["clase"] = "Sin clasificar"
            fila["clase"] = "Sin clasificar"
            decisiones.append(fila)
            continue
        caminos = pedir(API + "/" + concepto["code"] + "/pathsToRoot", cache) or []
        clase, por = clasificar(caminos)
        padres = sorted({p[1]["name"] for p in caminos if len(p) > 1})
        f["clase"] = clase
        f["ncit"] = concepto["code"]
        f["clase_ncit"] = padres[:3]
        f["hechos"].append({
            "tipo": "otro",
            "hecho": "El NCI Thesaurus lo registra como «%s» (%s), dentro de: %s. Clase asignada: %s." % (
                concepto["name"], concepto["code"], "; ".join(padres[:3]) or "sin clase padre", clase.lower()),
            "fuente_url": PAGINA + concepto["code"],
            "fecha": FECHA,
            "confianza": "pendiente",
        })
        fila.update({"ncit": concepto["code"], "nombre_ncit": concepto["name"], "padres": padres, "clase": clase,
                     "por_ancestro": por})
        decisiones.append(fila)
    exclusiones.guardar_muestra(base, MUESTRA, registro)
    os.makedirs(SALIDA, exist_ok=True)
    json.dump(decisiones, open(os.path.join(SALIDA, "decisiones.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cuenta = {}
    for d in decisiones:
        cuenta[d["clase"]] = cuenta.get(d["clase"], 0) + 1
    print(json.dumps(dict(sorted(cuenta.items(), key=lambda kv: -kv[1])), ensure_ascii=False, indent=1))
    if no_consultados:
        print("\n%d fármaco(s) sin respuesta de la API; conservan su clase anterior. Volver a correr:\n  %s"
              % (len(no_consultados), "\n  ".join(no_consultados)), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
