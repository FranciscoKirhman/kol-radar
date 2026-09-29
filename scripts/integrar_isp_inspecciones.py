#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Liga ensayos con los centros que nombra la planilla de inspecciones del ISP.

ClinicalTrials.gov oculta la sede de muchos ensayos ("Research Site", "Local Institution") y el
buscador de la CIF solo lista los que reclutan hoy. El Instituto de Salud Pública publica la
planilla "Centros de investigación clínica inspeccionados 2016–2025": por cada inspección, el
centro, el investigador principal, el código de protocolo y el solicitante. El código de protocolo
es el mismo que el patrocinador declara en ClinicalTrials.gov como `orgStudyId` (o entre sus
`secondaryIds`), así que se puede cruzar sin adivinar nada.

Reglas:
  1. Un renglón del ISP se cruza con un ensayo de la muestra solo si su código de protocolo,
     normalizado (sin mayúsculas, espacios, guiones ni paréntesis), es IGUAL al `orgStudyId` o a un
     `secondaryId` de exactamente un ensayo. Un código que calza con dos ensayos no se usa.
  2. El centro se liga a una institución solo por la tabla CENTROS, escrita a mano, con su motivo.
     Un centro que no está en la tabla no crea nada: queda en `cruces.json` como pendiente.
  3. Si el ensayo ya está ligado a esa institución, o a otra de la misma red que la fuente de
     ClinicalTrials.gov ya nombró (MISMA_RED), no se agrega otro vínculo: el ISP corrobora.
  4. Algunos renglones del ISP vienen sin centro ni investigador: son protocolos de la misma
     inspección que el renglón de arriba (la planilla deja las celdas vacías en vez de repetirlas).
     Heredan el centro, marcado como heredado, pero NO el investigador: el renglón de arriba puede
     nombrar a más de una persona y no se sabe cuál corresponde a cada protocolo.
  5. Los investigadores NO crean fichas ni se ligan a fichas existentes: van a
     `investigadores_candidatos.json` con `decision_humana` vacío. Nombrar a una persona exige
     revisar su identidad antes (PENDIENTES_BETA.md).
  6. No se copian la fecha, el tipo de visita, el resultado ni el motivo de la inspección. Son una
     evaluación regulatoria del centro y del investigador, no evidencia de actividad clínica, y
     KOL Radar no publica evaluaciones de desempeño (PRIVACIDAD.md).
  7. Nada se confirma: todo entra `pendiente`. Correrlo dos veces no cambia nada.

Requiere `xlrd` para leer la planilla (.xls de Excel 97): `pip install xlrd`. Es la única
dependencia fuera de la biblioteca estándar y solo la usa este script.

Uso:
    python3 scripts/integrar_isp_inspecciones.py                 # descarga la planilla y consulta la API
    python3 scripts/integrar_isp_inspecciones.py --xls ruta.xls  # usa una planilla ya descargada
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)

MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = datetime.date.today().isoformat()
SALIDA = os.path.join(RAIZ, "data", "pending", "isp-inspecciones-" + FECHA)
PAGINA_ISP = "https://www.ispch.gob.cl/anamed/establecimientos-farmaceuticos-y-cosmeticos/centros-de-investigacion-clinica/"
PLANILLA_ISP = ("https://www.ispch.gob.cl/wp-content/uploads/2026/01/"
                "CENTROS-DE-INVESTIGACION-CLINICA-INSPECCIONADOS_-2016-2025.xls")
API_CTGOV = "https://clinicaltrials.gov/api/v2/studies"
# El servidor del ISP corta la conexión si no reconoce el agente.
AGENTE = "Mozilla/5.0 (compatible; kol-radar; +https://franciscokirhman.github.io/kol-radar/)"

# Texto del centro en la planilla (espacios colapsados) → (institución, motivo).
CENTROS = {
    "Centro Internacional de Estudios Clínicos": ("ciec", "mismo nombre"),
    "Centro Internacional de Estudios Clínicos (CIEC)": ("ciec", "mismo nombre, con la sigla"),
    "Fundación Arturo López Pérez": ("falp", "mismo nombre"),
    "Fundación Arturo López Pérez (FALP)": ("falp", "mismo nombre, con la sigla"),
    "FALP": ("falp", "sigla"),
    "Orlandi Oncología (Sociedad Prosalud Montes y Orlandi Ltda.)": (
        "orlandi", "nombre comercial seguido de su razón social"),
    "Bradford Hill Centro de Investigaciones Clínicas": ("bradford-hill", "mismo nombre"),
    "Centro de investigación clínica Bradford Hill": ("bradford-hill", "mismo nombre, en otro orden"),
    "Centro Oncológico del Norte": ("centro-oncologico-norte", "mismo nombre"),
    "Sociedad de Investigaciones Médicas Limitada (SIM), Temuco": ("sim", "mismo nombre y ciudad"),
    "Centro de Investigaciones Clínicas Viña del Mar (CICVM)": ("cic-vina", "mismo nombre, con la sigla"),
    "Hospital Clínico Viña del Mar": (
        "cic-vina", "ClinicalTrials.gov ya escribe «Hospital Clinico Vina del Mar» para este centro, y ese "
                    "texto ya estaba ligado a esta ficha"),
    "Oncovida S.A.": ("oncovida", "mismo nombre, con la sociedad"),
    "James Lind Centro de Investigación del Cáncer": ("james-lind", "mismo nombre"),
    "Clínica San Carlos de Apoquindo": ("clinica-uc-san-carlos", "mismo nombre sin «UC CHRISTUS»"),
    "Centro de Cáncer Nuestra Señora de la Esperanza UC": ("centro-cancer-uc", "mismo nombre"),
    "Centro Nuestra Señora de la Esperanza-PUC": ("centro-cancer-uc", "mismo nombre abreviado"),
}

# Instituciones que son parte de otra que ClinicalTrials.gov suele nombrar en su lugar. Si el
# ensayo ya está ligado a la de la derecha, el centro que nombra el ISP es muy probablemente la
# MISMA sede escrita de otra forma: otro vínculo contaría dos veces un solo sitio.
MISMA_RED = {
    "centro-cancer-uc": {"puc", "hosp-clinico-uc"},
    "clinica-uc-san-carlos": {"puc", "hosp-clinico-uc"},
    "hosp-clinico-uc": {"puc"},
}

MOTIVO_HERENCIA = ("renglón sin centro ni investigador en la planilla, debajo de la inspección del renglón %d: "
                   "se hereda el centro, no el investigador")


def texto(v):
    if isinstance(v, float) and v == int(v):
        v = str(int(v))               # Excel guarda "20210096" como número
    return re.sub(r"\s+", " ", str(v)).strip()


def clave_codigo(c):
    c = re.sub(r"\(.*?\)", "", c or "")   # "GS-US-592-6173 (ASCENT-04)" → el código, sin el acrónimo
    return re.sub(r"[^A-Z0-9]", "", c.upper())


def clave_nombre(n):
    s = unicodedata.normalize("NFD", n or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z ]", " ", s).split()


def pedir(url, intentos=3):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
            return urllib.request.urlopen(req, timeout=90).read()
        except urllib.error.URLError as ex:
            if isinstance(ex.reason, ssl.SSLCertVerificationError):
                return pedir_con_curl(url)
            if i == intentos - 1:
                raise
            time.sleep(3 * (i + 1))
        except OSError:
            if i == intentos - 1:
                raise
            time.sleep(3 * (i + 1))


def pedir_con_curl(url):
    # www.ispch.gob.cl no envía su certificado intermedio (AlphaSSL). El OpenSSL de Python no lo va
    # a buscar y falla; curl con los certificados del sistema sí completa la cadena. Se verifica
    # igual: no se desactiva la comprobación en ningún caso.
    try:
        return subprocess.run(["curl", "-sSfL", "--max-time", "120", "-A", AGENTE, url],
                              check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as ex:
        sys.exit("No se pudo verificar el certificado de %s (%s). Bajá la planilla con el navegador desde\n"
                 "%s y pasala con --xls." % (url, ex, PAGINA_ISP))


def leer_planilla(ruta):
    try:
        import xlrd
    except ImportError:
        sys.exit("Falta xlrd para leer la planilla del ISP (.xls): pip install xlrd")
    hoja = xlrd.open_workbook(ruta).sheet_by_index(0)
    enc = [texto(c.value).lower() for c in hoja.row(0)]
    # Se ubica cada columna por su encabezado, no por posición: si el ISP agrega una columna, un
    # índice fijo leería otra cosa sin avisar.
    def col(prefijo):
        for i, h in enumerate(enc):
            if h.startswith(prefijo):
                return i
        sys.exit("La planilla ya no tiene la columna «%s…»: revisar el formato antes de seguir." % prefijo)
    c = {"anio": col("año"), "centro": col("centro"), "pi": col("investigador"),
         "estudio": col("nombre estudio"), "protocolo": col("número protocolo"), "solicitante": col("solicitante")}
    filas, arriba = [], None
    for r in range(1, hoja.nrows):
        f = {k: texto(hoja.cell_value(r, i)) for k, i in c.items()}
        if not f["protocolo"]:
            continue
        f["fila"] = r + 1                          # como la numera Excel
        if f["centro"]:
            arriba = f
            f["heredado_de_fila"] = None
        elif arriba:
            f["anio"], f["centro"], f["pi"] = arriba["anio"], arriba["centro"], ""
            f["heredado_de_fila"] = arriba["fila"]
        else:
            continue
        filas.append(f)
    return filas


def codigos_ctgov(ncts):
    """orgStudyId y secondaryIds de cada ensayo, de a 100 por consulta."""
    out = {}
    socket.setdefaulttimeout(90)
    for i in range(0, len(ncts), 100):
        lote = ncts[i:i + 100]
        q = urllib.parse.urlencode({"filter.ids": ",".join(lote), "pageSize": 100,
                                    "fields": "protocolSection.identificationModule"})
        r = json.loads(pedir(API_CTGOV + "?" + q))
        for s in r.get("studies", []):
            im = s["protocolSection"]["identificationModule"]
            out[im["nctId"]] = {"org_study_id": (im.get("orgStudyIdInfo") or {}).get("id"),
                                "secondary_ids": [x.get("id") for x in im.get("secondaryIdInfos") or []]}
        time.sleep(0.5)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--xls", help="planilla del ISP ya descargada")
    ap.add_argument("--codigos", help="JSON de códigos de ClinicalTrials.gov de una corrida anterior")
    a = ap.parse_args()
    registro = exclusiones.Registro()

    if a.xls:
        crudo = open(a.xls, "rb").read()
        ruta_xls = a.xls
    else:
        crudo = pedir(PLANILLA_ISP)
        ruta_xls = os.path.join(tempfile.mkdtemp(), "isp.xls")
        open(ruta_xls, "wb").write(crudo)
    sha = hashlib.sha256(crudo).hexdigest()
    filas = leer_planilla(ruta_xls)

    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}
    for iid, _ in CENTROS.values():
        if por_id.get(iid, {}).get("tipo") != "institucion":
            sys.exit("CENTROS apunta a una institución que no existe: " + iid)
    ncts = sorted(e["id"].upper() for e in ent if e["tipo"] == "ensayo_clinico")
    codigos = json.load(open(a.codigos, encoding="utf-8")) if a.codigos else codigos_ctgov(ncts)

    indice = collections.defaultdict(set)
    for nct, c in codigos.items():
        for x in [c["org_study_id"]] + c["secondary_ids"]:
            k = clave_codigo(x)
            if len(k) >= 5:          # "2023" como secondaryId calzaría con cualquier cosa
                indice[k].add(nct)

    # El resumen describe el ESTADO (qué vínculos vienen del ISP), no lo que hizo esta corrida: así
    # una segunda corrida, que no cambia nada, deja el mismo registro de auditoría que la primera.
    ya = {(v["origen"], v["destino"]): v for v in vin}
    sitios = collections.defaultdict(set)
    for v in vin:
        if v["tipo"] == "sitio del ensayo":
            sitios[v["destino"]].add(v["origen"])

    cruces, candidatos = [], []
    stats = collections.Counter()
    for f in filas:
        k = clave_codigo(f["protocolo"])
        hits = sorted(indice.get(k, ())) if len(k) >= 5 else []
        if not hits:
            continue
        cruce = {"fila_planilla": f["fila"], "anio": f["anio"], "centro_en_la_fuente": f["centro"],
                 "centro_heredado": (MOTIVO_HERENCIA % f["heredado_de_fila"]) if f["heredado_de_fila"] else None,
                 "numero_protocolo": f["protocolo"], "solicitante": f["solicitante"],
                 "nombre_estudio_en_la_fuente": f["estudio"], "ensayos": hits}
        cruces.append(cruce)
        if len(hits) > 1:
            cruce["decision"] = "no se usa: el código calza con más de un ensayo"
            stats["codigos_ambiguos"] += 1
            continue
        eid = hits[0].lower()
        e = por_id[eid]
        cruce["patrocinador_ctgov"] = e.get("patrocinador")
        iid, motivo = CENTROS.get(f["centro"], (None, None))
        cruce["institucion"], cruce["motivo_alias"] = iid, motivo
        if not iid:
            cruce["decision"] = "pendiente: el centro no está en la tabla CENTROS"
            stats["centros_sin_tabla"] += 1
        elif (iid, eid) in ya and ya[(iid, eid)].get("fuente_url") == PLANILLA_ISP:
            cruce["decision"] = "vínculo del ISP: sitio del ensayo"
            stats["vinculos_del_isp"] += 1
        elif (iid, eid) in ya:
            cruce["decision"] = "corrobora: el ensayo ya estaba ligado a este centro por otra fuente"
            stats["corroboran"] += 1
        elif sitios[eid] & MISMA_RED.get(iid, set()):
            cruce["decision"] = ("corrobora: el ensayo ya está ligado a %s, de la misma red; otro vínculo contaría "
                                 "dos veces la misma sede" % ", ".join(sorted(sitios[eid] & MISMA_RED[iid])))
            stats["corroboran"] += 1
        else:
            v = {"origen": iid, "destino": eid, "tipo": "sitio del ensayo",
                 "alias_fuente": f["centro"], "fuente_url": PLANILLA_ISP}
            vin.append(v)
            ya[(iid, eid)] = v
            sitios[eid].add(iid)
            cruce["decision"] = "vínculo del ISP: sitio del ensayo"
            stats["vinculos_del_isp"] += 1
            stats["vinculos_creados_en_esta_corrida"] += 1
        if iid and f["centro"] not in por_id[iid].setdefault("alias_en_la_fuente", []):
            por_id[iid]["alias_en_la_fuente"].append(f["centro"])
        centro_txt = por_id[iid]["nombre"] if iid else f["centro"]
        hecho = ("La planilla «Centros de investigación clínica inspeccionados 2016–2025» del ISP registra este "
                 "estudio, con el código de protocolo «%s», en %s (escrito «%s»), en una inspección de %s."
                 % (f["protocolo"], centro_txt, f["centro"], f["anio"]))
        if not any(h.get("fuente_url") == PLANILLA_ISP and f["protocolo"] in h.get("hecho", "") and
                   f["centro"] in h.get("hecho", "") for h in e["hechos"]):
            e["hechos"].append({"tipo": "ensayo_clinico", "hecho": hecho,
                                "fase": next((h.get("fase") for h in e["hechos"] if h.get("fase")), None),
                                "fuente_url": PLANILLA_ISP, "fecha": f["anio"], "confianza": "pendiente"})

        if f["pi"]:
            excluida = registro.estado_persona(nombre=f["pi"])
            if excluida == "exacta":
                continue       # pidió no aparecer: tampoco en la bandeja de revisión, que es pública
            t = clave_nombre(f["pi"])
            compatibles = [{"id": p["id"], "nombre": p["nombre"]} for p in ent if p["tipo"] == "persona"
                           and clave_nombre(p["nombre"])[:1] == t[:1]
                           and set(clave_nombre(p["nombre"])[1:]) & set(t[1:])]
            candidatos.append({
                "nombre_en_la_fuente": f["pi"],
                "rol_declarado_fuente": "investigador principal del estudio en el centro inspeccionado",
                "puede_ser_mas_de_una_persona": len(t) > 4,
                "centro_en_la_fuente": f["centro"], "institucion": iid, "ensayo": hits[0],
                "numero_protocolo": f["protocolo"], "anio": f["anio"], "fuente_url": PLANILLA_ISP,
                "fichas_existentes_compatibles": compatibles,
                "posible_persona_excluida": excluida == "posible",
                "confianza": "pendiente", "decision_humana": "", "revisor": "", "fecha_decision": ""})

    base["actualizado"] = FECHA
    exclusiones.guardar_muestra(base, MUESTRA, registro)

    ensayos = [e for e in ent if e["tipo"] == "ensayo_clinico"]
    con_inst = {e for e, s in sitios.items() if s}
    solo_isp = sorted(eid.upper() for eid in con_inst
                      if all(ya[(i, eid)].get("fuente_url") == PLANILLA_ISP for i in sitios[eid]))
    resumen = {
        "fecha": FECHA,
        "fuente": {"pagina": PAGINA_ISP, "planilla": PLANILLA_ISP, "sha256": sha,
                   "renglones_con_protocolo": len(filas)},
        "renglones_que_calzan_con_un_ensayo": len(cruces),
        "vinculos_del_isp": stats["vinculos_del_isp"],
        "corroboran_un_vinculo_de_otra_fuente": stats["corroboran"],
        "centros_sin_tabla": stats["centros_sin_tabla"],
        "codigos_ambiguos": stats["codigos_ambiguos"],
        "hechos_del_isp": sum(1 for e in ensayos for h in e["hechos"] if h.get("fuente_url") == PLANILLA_ISP),
        "ensayos_cuya_unica_institucion_viene_del_isp": solo_isp,
        "ensayos_sin_institucion": sum(1 for e in ensayos if e["id"] not in con_inst),
        "investigadores_candidatos": len(candidatos),
        "de_ellos_con_ficha_compatible": sum(1 for c in candidatos if c["fichas_existentes_compatibles"]),
        "columnas_no_copiadas": ["Fecha de Inspección", "Tipo de Visita", "Resultado de Inspección", "Motivo"],
    }
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, obj in (("resumen.json", resumen), ("cruces.json", cruces),
                        ("investigadores_candidatos.json", candidatos), ("codigos_ctgov.json", codigos)):
        with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    print("En esta corrida: %d vínculo(s) creados." % stats["vinculos_creados_en_esta_corrida"])


if __name__ == "__main__":
    main()
