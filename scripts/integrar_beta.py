#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integra la recolección de ClinicalTrials.gov a la muestra, para la beta.

Reglas aplicadas, todas explícitas:

  1. Entra TODO ensayo que la API declare con al menos una ubicación en el país solicitado. Cada uno conserva
     su NCT, su URL exacta y la fecha de recuperación.
  2. Los que resuelven a una institución canónica reciben el vínculo, y el vínculo guarda el
     ALIAS TEXTUAL con el que la fuente escribió esa sede.
  3. Los que no resuelven entran igual, sin institución, y conservan el texto original de sus
     sedes en `sedes_pendientes_resolucion`. No son evidencia negativa: son cola de trabajo.
  4. Los marcadores del patrocinador NO crean instituciones ni vínculos, pero se conservan
     listados aparte para que se vea qué se descartó y por qué.
  5. Solo se crean fichas de persona cuando la fuente NOMBRA a alguien y le DECLARA un rol
     individual (investigador principal o subinvestigador) y no existe ya una ficha compatible.
     La creación pública requiere país de afiliación y fuente explícitos.
     Ninguna fusión es automática: los candidatos que coinciden con una ficha existente quedan
     en la cola de revisión, sin tocar la ficha.
  6. Nada se marca como confirmado. Todo entra como `pendiente`.

No inventa ningún dato: cada campo sale del JSON crudo de la API o del artefacto de
preintegración ya auditado.
"""
import argparse
import collections
import datetime
import glob
import json
import os
import re
import sys
import urllib.parse
import pipeline_pais

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones  # noqa: E402  (todo lo que escribe la muestra pasa por acá)
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
# La descarga cruda la genera scripts/descargar_ctgov.py. KOL_NORMALIZADOR solo hace falta para usar
# otro normalizador que el del repositorio (scripts/normalizar.py).
CRUDO = os.environ.get("KOL_CRUDO")
if os.environ.get("KOL_NORMALIZADOR"):
    sys.path.insert(0, os.path.dirname(os.environ["KOL_NORMALIZADOR"]))
import normalizar  # noqa: E402

ESTADO = {
    "RECRUITING": "Reclutando", "ACTIVE_NOT_RECRUITING": "Activo, sin reclutar",
    "COMPLETED": "Completado", "TERMINATED": "Terminado",
    "NOT_YET_RECRUITING": "Aún no recluta", "WITHDRAWN": "Retirado",
    "SUSPENDED": "Suspendido", "ENROLLING_BY_INVITATION": "Recluta por invitación",
    "UNKNOWN": "Estado no declarado",
}
FASE = {"PHASE1": "Fase I", "PHASE2": "Fase II", "PHASE3": "Fase III", "PHASE4": "Fase IV",
        "EARLY_PHASE1": "Fase I", "NA": None}
# Término en inglés con el que se consultó cada área, para asignar el área por la condición
# que declara la fuente y no por el orden en que se recolectó.
TERMINO = {
    "cáncer colorrectal": "colorectal", "cáncer de próstata": "prostate", "melanoma": "melanoma",
    "linfoma": "lymphoma", "leucemia": "leukemia", "mieloma múltiple": "myeloma",
    "cáncer de ovario": "ovarian", "cáncer de páncreas": "pancrea", "cáncer renal": "renal",
    "cáncer de vejiga": "bladder", "cáncer de hígado": "hepato", "sarcoma": "sarcoma",
    "cáncer de cabeza y cuello": "head and neck", "cáncer cervicouterino": "cervical",
    "cáncer de endometrio": "endometri", "tumor cerebral": "glioma",
    "cáncer de pulmón": "lung", "cáncer de mama": "breast", "cáncer gástrico": "gastric",
}


def fase_legible(fases):
    vals = [FASE.get(f) for f in (fases or []) if FASE.get(f)]
    return vals[-1] if vals else None


def nombre_presentable(n):
    """ClinicalTrials.gov escribe algunos nombres en mayúsculas ("Myriam CAMPBELL BULL"). Se
    normaliza solo la caja: no se cambia, traduce ni completa ninguna palabra, y el texto
    literal de la fuente queda igual dentro del hecho."""
    def caja(t):
        return t.capitalize() if (t.isupper() and len(t) > 1) else t
    return " ".join(caja(t) for t in n.split())


def _ciudad_de(ent, nombre_inst, inst_c):
    """La ciudad de una persona es la de su institución, si la fuente la declaró para esa sede."""
    if not nombre_inst:
        return None
    cid = next((i["id_canonico"] for i in inst_c if i["nombre_canonico"] == nombre_inst), None)
    if not cid:
        return None
    return next((e.get("ciudad") for e in ent if e["id"] == cid), None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pais", default="CL")
    ap.add_argument("--crudo", default=CRUDO)
    ap.add_argument("--preintegracion")
    ap.add_argument("--muestra", default=MUESTRA)
    ap.add_argument("--salida")
    a = ap.parse_args()
    config = pipeline_pais.configurar(a.pais)
    iso = config["iso2"]
    permitido = pipeline_pais.paises.permitido_publicar_personas(iso)
    if not a.crudo:
        ap.error("Definí KOL_CRUDO o --crudo")
    pre = a.preintegracion or os.environ.get("KOL_PREINTEGRACION")
    if not pre:
        raiz_pre = (os.path.join(RAIZ, "data", "pending", iso) if iso == "CL" else str(pipeline_pais.cache(config)))
        opciones = sorted(glob.glob(os.path.join(raiz_pre, "preintegracion-clinicaltrials-*")))
        if not opciones and iso == "CL":
            opciones = sorted(glob.glob(os.path.join(RAIZ, "data", "pending", "preintegracion-clinicaltrials-*")))
        pre = opciones[-1] if opciones else None
    if not pre:
        ap.error("Falta --preintegracion para %s" % iso)
    fecha = os.environ.get("KOL_FECHA") or re.sub(r"^.*preintegracion-clinicaltrials-", "", pre) or datetime.date.today().isoformat()
    salida = pipeline_pais.validar_destino(a.salida or
        (a.muestra if iso == "CL" and permitido else pipeline_pais.cache(config) / "integracion.json"), config)
    resumen_pre = os.path.join(pre, "resumen.json")
    if os.path.exists(resumen_pre):
        with open(resumen_pre, encoding="utf-8") as f:
            pais_pre = json.load(f).get("pais", "CL")
        if pais_pre != iso:
            ap.error("La preintegración corresponde a %s, no a %s" % (pais_pre, iso))
    # Antes de cualquier consulta: si hay exclusiones y falta la clave, se detiene acá y no al
    # final de la corrida. Ver scripts/exclusiones.py.
    registro = exclusiones.Registro()
    base = json.load(open(a.muestra, encoding="utf-8"))
    crudo = pipeline_pais.cargar_crudo(a.crudo, config)
    inst_c = json.load(open(os.path.join(pre, "instituciones_candidatas.json"), encoding="utf-8"))
    pers_c = json.load(open(os.path.join(pre, "personas_candidatas.json"), encoding="utf-8"))

    ent = base["entidades"]
    vin = base["vinculos"]
    ids = {e["id"] for e in ent}
    inst_existentes = {e["id"] for e in ent if e["tipo"] == "institucion"}

    # ---------------------------------------------------------------- 1. ensayos, todos
    por_nct, areas_por_nct = {}, collections.defaultdict(set)
    for area, lista in crudo.items():
        for e in lista:
            areas_por_nct[e["nct"]].add(area)
            if e["nct"] not in por_nct:
                por_nct[e["nct"]] = e

    tamano_area = collections.Counter()
    for nct, areas in areas_por_nct.items():
        for a in areas:
            tamano_area[a] += 1

    def elegir_area(nct):
        """El área se decide por la condición que DECLARA la fuente, no por el orden de la
        recolección. Si empatan, gana el área con menos ensayos: así una patología chica no
        queda vacía porque sus ensayos se los llevó una grande."""
        cands = areas_por_nct[nct]
        if len(cands) == 1:
            return next(iter(cands))
        cond = " ".join(por_nct[nct].get("condiciones") or []).lower()
        puntaje = {a: cond.count(TERMINO.get(a, "\0")) for a in cands}
        mejor = max(puntaje.values())
        empatados = sorted(a for a in cands if puntaje[a] == mejor)
        return min(empatados, key=lambda a: (tamano_area[a], a))

    # Ciudad de cada institución tomada de las sedes que la fuente declara: es dato de la
    # API, no una inferencia. Se usa la más frecuente.
    ciudad_inst = collections.defaultdict(collections.Counter)
    nuevos_ensayos = 0
    sin_institucion = 0
    stats = collections.Counter()
    vinculos_nuevos = []

    for nct in sorted(por_nct):
        e = por_nct[nct]
        eid = nct.lower()
        url = "https://clinicaltrials.gov/study/%s" % nct
        resueltos, pendientes, ciudades, reclutando = [], [], [], 0
        for s in e["sitios"]:
            fac = (s.get("facility") or "").strip()
            if s.get("city"):
                ciudades.append(s["city"])
            if (s.get("status") or "").upper() == "RECRUITING":
                reclutando += 1
            r = pipeline_pais.resolver_sede(fac, config, normalizar)
            if r:
                resueltos.append((r[0], r[1], fac))
                if s.get("city"):
                    ciudad_inst[r[0]][s["city"]] += 1
            elif fac and normalizar.PLACEHOLDER.match(normalizar.norm(fac)):
                stats["sedes_placeholder"] += 1     # no crea institución ni vínculo
            elif fac:
                pendientes.append(fac)

        if eid in ids:
            stats["ensayos_ya_existentes"] += 1
        else:
            fase = fase_legible(e.get("fases"))
            estado = ESTADO.get(e.get("estado"), e.get("estado"))
            sub = " · ".join([x for x in (fase, estado) if x])
            ciudad = None
            if ciudades:
                u = sorted(set(ciudades))
                ciudad = u[0] + (" (+%d sitios)" % (len(ciudades) - 1) if len(ciudades) > 1 else "")
            nodo = {
                "id": eid,
                "nombre": ("%s (%s)" % (e["acronimo"], nct)) if e.get("acronimo") else nct,
                "tipo": "ensayo_clinico",
                "ciudad": ciudad,
                "subtitulo": sub or "Ensayo clínico con sitio en %s" % config["nombre"],
                "area": elegir_area(nct),
                "acronimo": e.get("acronimo"),
                "intervenciones": [i for i in (e.get("intervenciones") or []) if i][:4],
                "estado_reclutamiento": estado,
                "sitios_chile": len(e["sitios"]),
                "sitios_chile_reclutando": reclutando,
                "hechos": [{
                    "tipo": "ensayo_clinico",
                    "hecho": e["titulo"],
                    "fase": fase,
                    "fuente_url": url,
                    "fecha": e.get("actualizado") or fecha,
                    "confianza": "pendiente",
                }],
            }
            if iso != "CL":
                nodo["pais"] = iso
                nodo["sitios_pais"] = nodo.pop("sitios_chile")
                nodo["sitios_pais_reclutando"] = nodo.pop("sitios_chile_reclutando")
            if pendientes:
                # Cola de resolución, no evidencia negativa: la sede existe y está declarada,
                # solo que todavía no tenemos un alias que la ligue a una institución canónica.
                nodo["sedes_pendientes_resolucion"] = sorted(set(pendientes))
            if not resueltos:
                sin_institucion += 1
            ent.append(nodo)
            ids.add(eid)
            nuevos_ensayos += 1

        for cid, nombre, alias in resueltos:
            if cid not in inst_existentes and cid not in ids:
                continue  # la institución se crea abajo; el vínculo se agrega en la 2ª pasada
        vinculos_nuevos.append((eid, resueltos))

    # ---------------------------------------------------------------- 2. instituciones
    nuevas_inst = 0
    for i in inst_c:
        cid = i["id_canonico"]
        if cid in ids:
            continue
        alias_top = i["alias_textuales_en_la_fuente"][0][0]
        ciudades = ciudad_inst.get(cid)
        ent.append({
            "id": cid, "nombre": i["nombre_canonico"], "tipo": "institucion",
            "ciudad": ciudades.most_common(1)[0][0] if ciudades else None,
            "subtitulo": "Centro con sitio de ensayos clínicos en %s" % config["nombre"],
            "alias_en_la_fuente": [a for a, _ in i["alias_textuales_en_la_fuente"]],
            "hechos": [{
                "tipo": "afiliacion",
                "hecho": (("Figura como sede chilena de ensayos clínicos en ClinicalTrials.gov, " if iso == "CL" else
                           "Figura como sede de ensayos clínicos en ClinicalTrials.gov, ") +
                          "escrita en la fuente como \"%s\"." % alias_top),
                "fuente_url": ("https://clinicaltrials.gov/search?locStr=Chile&term=%s" % alias_top.replace(" ", "+")
                               if iso == "CL" else "https://clinicaltrials.gov/search?%s" % urllib.parse.urlencode({
                                   "locStr": pipeline_pais.nombre_ctgov(config), "term": alias_top})),
                "fecha": fecha, "confianza": "pendiente",
            }],
        })
        ids.add(cid)
        nuevas_inst += 1

    # ---------------------------------------------------------------- 3. vínculos sede→ensayo
    existentes = {(v["origen"], v["destino"], v["tipo"]) for v in vin}
    n_vin = 0
    for eid, resueltos in vinculos_nuevos:
        vistos = set()
        for cid, nombre, alias in resueltos:
            if cid not in ids or (cid, eid) in vistos:
                continue
            vistos.add((cid, eid))
            k = (cid, eid, "sitio del ensayo")
            if k in existentes:
                continue
            existentes.add(k)
            vin.append({"origen": cid, "destino": eid, "tipo": "sitio del ensayo",
                        "alias_fuente": alias})
            n_vin += 1

    # ---------------------------------------------------------------- 4. personas
    creadas = 0
    for p in pers_c:
        # País del sitio no demuestra afiliación. Un humano debe documentarla antes
        # de crear una ficha pública. No se infiere del país pedido por CLI.
        if (not p.get("pais_afiliacion") or not p.get("pais_afiliacion_fuente") or
                not p.get("decision_humana") == "aprobada" or not p.get("revisor") or
                not p.get("fecha_decision")):
            stats["personas_en_cola_por_pais_afiliacion"] += 1
            continue
        if not str(p["pais_afiliacion_fuente"]).startswith("https://"):
            stats["personas_en_cola_por_fuente_afiliacion"] += 1
            continue
        if permitido and not pipeline_pais.paises.permitido_publicar_personas(p["pais_afiliacion"]):
            stats["personas_en_cola_por_pais_no_aprobado"] += 1
            continue
        if p["rol_declarado_fuente"] not in ("PRINCIPAL_INVESTIGATOR", "SUB_INVESTIGATOR"):
            continue
        excluida = registro.estado_persona(nombre=p["nombre_normalizado"])
        if excluida == "exacta":
            stats["personas_excluidas_por_solicitud"] += 1
            continue          # pidió no aparecer: ver scripts/exclusiones.py
        if excluida == "posible":
            stats["personas_en_cola_por_posible_exclusion"] += 1
            continue          # puede ser un homónimo; lo decide una persona, no el script
        if p["fichas_existentes_compatibles"]:
            stats["personas_en_cola_por_posible_fusion"] += 1
            continue          # fusionar es decisión humana: no se toca la ficha existente
        pid = re.sub(r"[^a-z0-9]+", "-", p["nombre_normalizado"].lower()).strip("-")
        eid = p["nct"].lower()
        if pid not in ids:
            rol = ("investigador principal" if p["rol_declarado_fuente"] == "PRINCIPAL_INVESTIGATOR"
                   else "subinvestigador")
            ent.append({
                "id": pid, "nombre": nombre_presentable(p["nombre_normalizado"]), "tipo": "persona",
                "pais_afiliacion": p["pais_afiliacion"],
                "pais_afiliacion_fuente": p["pais_afiliacion_fuente"],
                # Si la sede no resolvió a una institución canónica, se muestra el texto
                # literal con que la fuente la nombra: es un dato real, y decir "sin resolver"
                # escondía información que sí teníamos.
                "subtitulo": p["institucion_canonica"] or p["sede_texto_original"],
                "ciudad": _ciudad_de(ent, p["institucion_canonica"], inst_c),
                "subtitulo_fuente": p["fuente_url"],
                "area": next((x.get("area") for x in ent
                              if x["id"] == eid and x["tipo"] == "ensayo_clinico"), None),
                "nota_identidad": (
                    "Ficha creada a partir de un contacto de sitio de ClinicalTrials.gov: la "
                    "fuente la nombra y le declara el rol de %s. No hay ORCID ni segunda fuente "
                    "que confirme la identidad, y no se comprobó su condición de médico, su "
                    "afiliación vigente ni ningún rol clínico más allá de lo que declara ese "
                    "registro." % rol),
                "hechos": [{
                    "tipo": "ensayo_clinico",
                    "hecho": (("ClinicalTrials.gov la nombra como %s del sitio chileno " if iso == "CL" else
                               "ClinicalTrials.gov la nombra como %s del sitio ") +
                              "declarado como \"%s\"." % (rol, p["sede_texto_original"])),
                    "fase": None, "fuente_url": p["fuente_url"],
                    "fecha": fecha, "confianza": "pendiente",
                }],
            })
            ids.add(pid)
            creadas += 1
        if eid in ids:
            k = (pid, eid, "investigador de sitio")
            if k not in existentes:
                existentes.add(k)
                vin.append({"origen": pid, "destino": eid, "tipo": "investigador de sitio"})
        if p["institucion_canonica"]:
            icid = next((i["id_canonico"] for i in inst_c
                         if i["nombre_canonico"] == p["institucion_canonica"]), None)
            if icid and icid in ids:
                k = (pid, icid, "afiliación")
                if k not in existentes:
                    existentes.add(k)
                    vin.append({"origen": pid, "destino": icid, "tipo": "afiliación",
                                "alias_fuente": p["sede_texto_original"]})

    base["actualizado"] = datetime.date.today().isoformat()
    base["especialidad_muestra"] = "oncología (19 áreas)"
    base["nota_beta"] = (
        "Beta. La expansión del 2026-09-09 sumó ensayos de ClinicalTrials.gov con al menos una "
        "ubicación declarada en Chile. Ningún hecho pasó revisión humana: todos entran como "
        "'pendiente'. Las sedes que no se pudieron ligar a una institución conocida quedan "
        "listadas en el propio ensayo como pendientes de resolución, no descartadas.")
    if iso != "CL":
        base["pais_recoleccion"] = iso
        base["nota_beta"] = "Integración de revisión privada por país; no publicada."
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    exclusiones.guardar_muestra(base, salida, registro)

    c = collections.Counter(e["tipo"] for e in ent)
    print(json.dumps({
        "entidades": len(ent), "vinculos": len(vin), "por_tipo": dict(c),
        "ensayos_nuevos": nuevos_ensayos,
        "ensayos_sin_institucion_canonica": sin_institucion,
        "instituciones_nuevas": nuevas_inst,
        "vinculos_sede_ensayo_nuevos": n_vin,
        "personas_creadas": creadas,
        "otros": dict(stats),
        "por_area": dict(collections.Counter(e.get("area") for e in ent if e["tipo"] == "ensayo_clinico")),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
