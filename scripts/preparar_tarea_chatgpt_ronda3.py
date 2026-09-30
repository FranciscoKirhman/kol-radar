#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara la tercera ronda de búsqueda para ChatGPT: lo que no se pudo resolver con fuentes directas.

Tres tareas, con todos los datos dentro del prompt (sin adjuntos):
  A  Instituciones sin dirección citable, con lo que ya se probó y las pistas que hay.
  B  Textos de sede que ClinicalTrials.gov declara en Chile y que no calzan con ninguna institución
     (sin los marcadores obvios del patrocinador, que no se pueden resolver buscando).
  C  Ensayos que siguen sin ninguna institución: la fuente oculta la sede ("Research Site"), y ni la
     CIF, ni el ISP, ni el código postal la dieron. Se busca en otras fuentes que nombren el estudio
     y el centro juntos.

Escribe en data/pending/tarea-chatgpt-<fecha>-ronda3/: PROMPT.md (los mensajes a pegar), los CSV que
usa scripts/validar_respuesta_chatgpt.py para validar la respuesta, y README.md.

Uso:  python3 scripts/preparar_tarea_chatgpt_ronda3.py
"""
import collections
import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
UBIC = os.path.join(RAIZ, "data", "geo", "ubicaciones-instituciones.json")
CODIGOS = os.path.join(RAIZ, "data", "pending", "isp-inspecciones-2026-09-29", "codigos_ctgov.json")
FECHA = "2026-09-29"
SALIDA = os.path.join(RAIZ, "data", "pending", "tarea-chatgpt-%s-ronda3" % FECHA)
API = "https://clinicaltrials.gov/api/v2/studies"

MARCADOR = re.compile(r"^(site\s*\d+|site reference id|exelixis clinical|tanvex investigational|sandoz investigational|"
                      r"sit?e$|clinc?ical study site|for additional information|chile$)", re.I)

# Pistas escritas a mano para la tarea A: qué se probó y qué se sabe.
PISTAS = {
    "sochradioterapia": "Su página de contacto (https://www.sochira.cl/contacto) solo tiene un formulario. Probá el "
                        "domicilio de la persona jurídica en el Registro de Empresas y Sociedades o en estatutos publicados.",
    "crchile": "Su sitio publica dos números incompatibles en la misma calle: Beauchef 683 y Beauchef 638 (Valdivia). "
               "ClinicalTrials.gov declara el código postal 5110683. El DEIS tiene la 'Clínica Ramis' en Beauchef 683. "
               "Confirmá con otra fuente cuál es y si funciona dentro de esa clínica.",
    "cesfam-juan-pablo-ii": "Hay varios CESFAM Juan Pablo II (La Pintana —Red de Salud UC CHRISTUS—, San Bernardo, "
                            "Padre Hurtado, entre otros). ClinicalTrials.gov lo ubica en 'Santiago' con código postal "
                            "8831695. Decidí cuál es con una fuente que lo diga (el registro del ensayo, la red de salud, "
                            "el municipio); no por cercanía del código.",
    "cormun-puente-alto": "Es la corporación municipal de salud, no un establecimiento. ClinicalTrials.gov declara el "
                          "código postal 8210269. Buscá su domicilio en su sitio oficial o en el del municipio.",
    "benef-osorno": "ClinicalTrials.gov la declara en Osorno con código postal 5311092. No está en el DEIS con ese "
                    "nombre: puede ser la persona jurídica dueña de una clínica de Osorno. Buscá qué establecimiento "
                    "opera y su dirección.",
    "clinica-las-nieves": "ClinicalTrials.gov la declara en Santiago, sin código postal. No está en el DEIS con ese nombre.",
    "meditek": "ClinicalTrials.gov declara el código postal 8420383, el mismo del edificio de Bradford Hill y CIEC "
               "(Palestina, ex Manzano, 343, Recoleta). Confirmá si funciona ahí con una fuente propia.",
    "aren-bachero": "ClinicalTrials.gov declara el código postal 8420383, el mismo del edificio de Bradford Hill y CIEC. "
                    "Confirmá con una fuente propia (sitio, Superintendencia, registro de empresas).",
    "health-care-chile": "ClinicalTrials.gov escribe 'Health and Care Chile' con código postal 7500006 (Providencia), "
                         "que también usa Orlandi Oncología.",
    "rey-oreilly": "ClinicalTrials.gov escribe 'Rey y Oreilly Limitada' en Temuco con código postal 4810148, el mismo "
                   "que usa CIDO. ¿Es la razón social de CIDO u otro centro?",
    "ceos": "ClinicalTrials.gov escribe 'Centro de Estudios Oncologicos de Santiago (CEOS) Oncologia' con código postal "
            "7500921, el de la Fundación Arturo López Pérez. ¿Funciona dentro de FALP?",
    "cics-temuco": "ClinicalTrials.gov lo declara en Temuco con códigos postales 4781156 y 4810371.",
    "urumed": "",
    "enroll": "ClinicalTrials.gov lo declara en Providencia con código postal 7500587.",
    "dermovein": "ClinicalTrials.gov declara 'Clinica Dermovein S.A.' en Santiago con código postal 7640881, que también "
                 "usa Clínica Dermacross.",
    "ced-vina": "ClinicalTrials.gov lo declara en Viña del Mar sin código postal útil.",
    "icer-lab": "ClinicalTrials.gov lo declara en Talcahuano, sin código postal.",
}


def ubicaciones(ncts):
    out = {}
    for i in range(0, len(ncts), 100):
        q = urllib.parse.urlencode({"filter.ids": ",".join(ncts[i:i + 100]), "pageSize": 100,
                                    "fields": "protocolSection.identificationModule,"
                                              "protocolSection.contactsLocationsModule"})
        r = json.load(urllib.request.urlopen(urllib.request.Request(API + "?" + q, headers={"User-Agent": "kol-radar"}),
                                             timeout=90))
        for s in r["studies"]:
            nct = s["protocolSection"]["identificationModule"]["nctId"]
            out[nct] = [l for l in s["protocolSection"].get("contactsLocationsModule", {}).get("locations", [])
                        if l.get("country") == "Chile"]
        time.sleep(0.5)
    return out


def escribir_csv(nombre, filas, campos):
    with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in filas:
            w.writerow({k: r.get(k, "") for k in campos})


def main():
    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}
    ubic = json.load(open(UBIC, encoding="utf-8"))
    codigos = json.load(open(CODIGOS, encoding="utf-8")) if os.path.exists(CODIGOS) else {}
    os.makedirs(SALIDA, exist_ok=True)

    # ---------------------------------------------------------------- A
    filas_a = []
    for iid, x in sorted(ubic.get("sin_ubicar", {}).items()):
        filas_a.append({"id": iid, "nombre": x["nombre"], "ciudad_en_la_muestra": x["ciudad_en_la_muestra"],
                        "tarea": "ubicar", "motivo": PISTAS.get(iid) or x.get("motivo") or "",
                        "direccion_actual": "", "fuente_en_la_muestra": x.get("fuente_revisada") or ""})
    escribir_csv("A_instituciones.csv", filas_a, ["id", "nombre", "ciudad_en_la_muestra", "tarea", "motivo",
                                                   "direccion_actual", "fuente_en_la_muestra"])

    # ---------------------------------------------------------------- B y C necesitan las sedes declaradas
    con_inst = {v["destino"] for v in vin if v["tipo"] == "sitio del ensayo"}
    sin_inst = sorted(e["id"].upper() for e in ent if e["tipo"] == "ensayo_clinico" and e["id"] not in con_inst)
    pend = collections.defaultdict(list)
    for e in ent:
        for t in e.get("sedes_pendientes_resolucion") or []:
            pend[t].append(e["id"].upper())
    U = ubicaciones(sorted(set(sin_inst) | {n for ns in pend.values() for n in ns}))

    filas_b = []
    for t, ncts in sorted(pend.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if MARCADOR.match(t.strip()):
            continue
        ciudades = sorted({(l.get("city") or "") + (" " + l["zip"] if l.get("zip") else "")
                           for n in ncts for l in U.get(n, []) if l.get("facility") == t})
        filas_b.append({"texto_sede": t, "apariciones": len(ncts), "ciudades_de_esos_ensayos": " | ".join(ciudades),
                        "ncts": " ".join(ncts),
                        "urls_clinicaltrials": " ".join("https://clinicaltrials.gov/study/" + n for n in ncts[:3])})
    escribir_csv("B_sedes_por_resolver.csv", filas_b, ["texto_sede", "apariciones", "ciudades_de_esos_ensayos",
                                                       "ncts", "urls_clinicaltrials"])

    filas_c = []
    for n in sin_inst:
        e = por_id[n.lower()]
        sedes = sorted({"%s (%s%s)" % (l.get("facility") or "sin nombre", l.get("city") or "sin ciudad",
                                         ", " + l["zip"] if l.get("zip") else "") for l in U.get(n, [])})
        c = codigos.get(n, {})
        filas_c.append({"nct": n, "patrocinador": e.get("patrocinador") or "", "codigo_protocolo": c.get("org_study_id") or "",
                        "titulo": (e.get("titulo_fuente") or e["nombre"])[:160], "estado": e.get("estado_reclutamiento") or "",
                        "sedes_enmascaradas": " | ".join(sedes)})
    escribir_csv("C_ensayos_sin_sede_nombrada.csv", filas_c, ["nct", "patrocinador", "codigo_protocolo", "titulo",
                                                              "estado", "sedes_enmascaradas"])

    filas_e = [{"id": e["id"], "nombre": e["nombre"], "ciudad": e.get("ciudad") or "",
                "alias_en_la_fuente": " | ".join((e.get("alias_en_la_fuente") or [])[:4])}
               for e in sorted(ent, key=lambda x: x["id"]) if e["tipo"] == "institucion"]
    escribir_csv("instituciones_existentes.csv", filas_e, ["id", "nombre", "ciudad", "alias_en_la_fuente"])

    prompt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantilla_tarea_chatgpt_ronda3.md"),
                  encoding="utf-8").read()
    def lineas(filas, campos):
        return "\n".join(" | ".join(str(r.get(k, "")).replace("\n", " ") for k in campos) for r in filas)
    prompt = (prompt.replace("{{N_A}}", str(len(filas_a))).replace("{{N_B}}", str(len(filas_b)))
              .replace("{{N_C}}", str(len(filas_c))).replace("{{N_E}}", str(len(filas_e)))
              .replace("{{CARPETA}}", os.path.relpath(SALIDA, RAIZ))
              .replace("{{LISTA_A}}", lineas(filas_a, ["id", "nombre", "ciudad_en_la_muestra", "motivo"]))
              .replace("{{LISTA_B}}", lineas(filas_b, ["texto_sede", "apariciones", "ciudades_de_esos_ensayos", "ncts"]))
              .replace("{{LISTA_C1}}", lineas(filas_c[:55], ["nct", "patrocinador", "codigo_protocolo", "titulo", "sedes_enmascaradas"]))
              .replace("{{LISTA_C2}}", lineas(filas_c[55:], ["nct", "patrocinador", "codigo_protocolo", "titulo", "sedes_enmascaradas"]))
              .replace("{{LISTA_E}}", lineas(filas_e, ["id", "nombre", "ciudad"])))
    open(os.path.join(SALIDA, "PROMPT.md"), "w", encoding="utf-8").write(prompt)
    resumen = {"fecha": FECHA, "A_instituciones": len(filas_a), "B_sedes": len(filas_b), "C_ensayos": len(filas_c),
               "B_marcadores_omitidos": sum(1 for t in pend if MARCADOR.match(t.strip()))}
    json.dump(resumen, open(os.path.join(SALIDA, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
