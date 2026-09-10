#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el artefacto de PREINTEGRACIÓN de la recolección de ClinicalTrials.gov.

No modifica `data/sample/perfiles-muestra.json`. Produce, bajo `data/pending/`, los archivos
que permiten auditar la recolección antes de decidir si entra a la muestra pública:

  README.md                     metodología, fecha de consulta y límites
  ensayos_candidatos.json       NCT, URL exacta, condición declarada por la fuente, sedes
  instituciones_candidatas.json alias observados -> institución canónica
  sedes_sin_resolver.json       cola de resolución (NO son evidencia negativa)
  placeholders_excluidos.json   marcadores del patrocinador que no crean instituciones
  personas_candidatas.json      contactos clasificados, ninguno aprobado
  simulacion.json               distribución de puntaje, activación de topes y tamaño del grafo

Umbral de admisión aplicado a un ensayo (acumulativo):
  - identidad estable por NCT + URL exacta de ClinicalTrials.gov;
  - la API declara al menos una ubicación con país Chile;
  - al menos una sede chilena con nombre institucional específico resoluble a una institución
    canónica mediante un alias documentado;
  - se conserva el texto original de la sede, el estado y la fecha de recuperación.

Ese umbral admite un ensayo y su vínculo con una institución. NO autoriza crear una persona.
"""
import json, os, re, sys, collections, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
FECHA_CONSULTA = "2026-09-09"
DESTINO = os.path.join(RAIZ, "data", "pending", "preintegracion-clinicaltrials-2026-09-09")

# El normalizador vive junto a la recolección, en el scratchpad de la sesión.
NORM = os.environ.get("KOL_NORMALIZADOR")
CRUDO = os.environ.get("KOL_CRUDO")
if not NORM or not CRUDO:
    sys.exit("Definí KOL_NORMALIZADOR y KOL_CRUDO (ver el informe de esta sesión).")
sys.path.insert(0, os.path.dirname(NORM))
import normalizar  # noqa: E402

# ------------------------------------------------------------------ clasificación de contactos
NO_PERSONA = re.compile(
    r"^(study coordinator|principal investigator|sub[- ]?investigator|site\s*\w*\d+|"
    r"clinical trial|trials? information|information desk|call center|"
    r"boehringer ingelheim|novartis|pfizer|roche|gsk|astrazeneca|msd|merck|lilly|amgen|bayer|"
    r"sanofi|abbvie|takeda|janssen|bms|bristol.*|daiichi|regeneron|beigene|gilead|servier|"
    r"astellas|incyte)\b", re.I)
SUFIJO = re.compile(r",?\s*(m\.?d\.?|ph\.?d\.?|msc|rn|site\s*\d+|m\.d\.)\.?\s*$", re.I)


def limpiar_nombre(bruto):
    n = bruto.strip()
    n = re.sub(r",\s*Site\s*\d+\s*$", "", n, flags=re.I)
    for _ in range(3):
        n2 = SUFIJO.sub("", n).strip()
        if n2 == n:
            break
        n = n2
    n = re.sub(r"^(dr|dra|prof)\.?\s+", "", n, flags=re.I).strip()
    return n


def clave_nombre(n):
    import unicodedata
    s = unicodedata.normalize("NFD", n or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z ]", " ", s).split()


def main():
    crudo = json.load(open(CRUDO, encoding="utf-8"))
    base = json.load(open(os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json"),
                          encoding="utf-8"))
    inst_existentes = {e["id"]: e["nombre"] for e in base["entidades"] if e["tipo"] == "institucion"}
    personas_existentes = {e["id"]: e["nombre"] for e in base["entidades"] if e["tipo"] == "persona"}
    nct_existentes = {e["id"].upper() for e in base["entidades"] if e["tipo"] == "ensayo_clinico"}

    ensayos, alias_por_inst = {}, collections.defaultdict(collections.Counter)
    sin_resolver, placeholders = collections.Counter(), collections.Counter()
    contactos = []

    for area, lista in crudo.items():
        for e in lista:
            nct = e["nct"]
            sitios_ok, sitios_todos = [], []
            for s in e["sitios"]:
                fac = (s.get("facility") or "").strip()
                r = normalizar.resolver(fac)
                registro = {"texto_original_fuente": fac, "ciudad": s.get("city"),
                            "estado_sitio": s.get("status")}
                if r:
                    registro["institucion_canonica"] = {"id": r[0], "nombre": r[1],
                                                        "ya_en_la_muestra": r[0] in inst_existentes}
                    alias_por_inst[(r[0], r[1])][fac] += 1
                    sitios_ok.append(registro)
                elif fac and normalizar.PLACEHOLDER.match(normalizar.norm(fac)):
                    registro["descartado"] = "marcador del patrocinador"
                    placeholders[fac] += 1
                elif fac:
                    registro["descartado"] = "sin alias documentado"
                    sin_resolver[fac] += 1
                sitios_todos.append(registro)

                for c in s.get("contactos", []):
                    bruto = (c.get("name") or "").strip()
                    if not bruto:
                        continue
                    contactos.append({"bruto": bruto, "rol_fuente": c.get("role"),
                                      "nct": nct, "sede_texto": fac,
                                      "institucion": r[1] if r else None,
                                      "institucion_id": r[0] if r else None})

            # UMBRAL DE ADMISIÓN: sin sede resoluble, el ensayo no entra.
            if not sitios_ok:
                continue
            prev = ensayos.get(nct)
            if prev:
                prev["areas_consultadas"].append(area)
                continue
            ensayos[nct] = {
                "nct": nct,
                "fuente_url": "https://clinicaltrials.gov/study/%s" % nct,
                "titulo_fuente": e["titulo"],
                "acronimo_fuente": e.get("acronimo"),
                "fases_fuente": e.get("fases") or [],
                "estado_fuente": e.get("estado"),
                "ultima_actualizacion_fuente": e.get("actualizado"),
                "condiciones_declaradas_fuente": e.get("condiciones") or [],
                "intervenciones_fuente": e.get("intervenciones") or [],
                "areas_consultadas": [area],
                "sitios_chile": sitios_todos,
                "sitios_chile_resolubles": len(sitios_ok),
                "ya_en_la_muestra": nct.upper() in nct_existentes,
                "fecha_recuperacion": FECHA_CONSULTA,
                "confianza": "pendiente",
            }

    # ------------------------------------------------------------------ personas: clasificación
    # Índice por (nombre de pila, CADA apellido). Indexar solo el segundo token dejaba pasar
    # "Hector Gonzalo Galindo Aranibar" como persona nueva pese a existir ya "Héctor Galindo":
    # el segundo token ahí es "Gonzalo", un segundo nombre, no el apellido. Ese fallo habría
    # creado una ficha duplicada del mismo médico.
    apellidos_existentes = collections.defaultdict(list)
    for pid, nom in personas_existentes.items():
        t = clave_nombre(nom)
        for apellido in t[1:]:
            apellidos_existentes[(t[0], apellido)].append((pid, nom))

    candidatos, vistos = [], {}
    for c in contactos:
        limpio = limpiar_nombre(c["bruto"])
        if not limpio or NO_PERSONA.match(limpio) or len(clave_nombre(limpio)) < 2:
            clase, coincide = "no_persona_utilizable", []
        else:
            t = clave_nombre(limpio)
            coincide, ya = [], set()
            for apellido in t[1:]:
                for pid, nom in apellidos_existentes.get((t[0], apellido), []):
                    if pid not in ya:
                        ya.add(pid); coincide.append((pid, nom))
            inst_resuelta = bool(c["institucion_id"])
            inst_conocida = c["institucion_id"] in inst_existentes
            if coincide:
                # Reutilización solo si el nombre completo normalizado es idéntico Y la sede
                # apunta a una institución que ya está en la muestra. Todo lo demás —abreviación,
                # segundo apellido ausente, orden distinto, institución insuficiente— queda como
                # posible coincidencia. Ninguna de las dos se aplica sin aprobación humana.
                identico = any(clave_nombre(n) == t for _, n in coincide)
                clase = ("reutilizacion_propuesta" if (identico and inst_conocida)
                         else "posible_coincidencia")
            elif (c["rol_fuente"] in ("PRINCIPAL_INVESTIGATOR", "SUB_INVESTIGATOR")
                  and inst_resuelta):
                # La fuente lo nombra y le declara un rol individual en una sede chilena
                # resoluble. Sigue siendo una PROPUESTA: la ficha se crea tras revisión humana.
                clase = "persona_nueva_propuesta"
            else:
                # Rol de contacto genérico o sede sin alias documentado: evidencia insuficiente.
                clase = "posible_coincidencia"
        k = (limpio.lower(), c["nct"])
        if k in vistos:
            continue
        vistos[k] = 1
        candidatos.append({
            "nombre_fuente": c["bruto"], "nombre_normalizado": limpio,
            "rol_declarado_fuente": c["rol_fuente"],
            "nct": c["nct"], "fuente_url": "https://clinicaltrials.gov/study/%s" % c["nct"],
            "sede_texto_original": c["sede_texto"], "institucion_canonica": c["institucion"],
            "clasificacion": clase,
            "fichas_existentes_compatibles": [{"id": i, "nombre": n} for i, n in coincide],
            "fecha_recuperacion": FECHA_CONSULTA,
            "confianza": "pendiente",
            "decision_humana": "", "revisor": "", "fecha_decision": "",
        })

    os.makedirs(DESTINO, exist_ok=True)
    def guardar(nombre, obj):
        with open(os.path.join(DESTINO, nombre), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)

    inst_out = []
    for (cid, nom), aliases in sorted(alias_por_inst.items(), key=lambda x: -sum(x[1].values())):
        inst_out.append({"id_canonico": cid, "nombre_canonico": nom,
                         "ya_en_la_muestra": cid in inst_existentes,
                         "sedes_observadas": sum(aliases.values()),
                         "alias_textuales_en_la_fuente": aliases.most_common()})

    guardar("ensayos_candidatos.json", sorted(ensayos.values(), key=lambda e: e["nct"]))
    guardar("instituciones_candidatas.json", inst_out)
    guardar("sedes_sin_resolver.json",
            [{"texto_original": t, "apariciones": n, "estado": "cola de resolución"}
             for t, n in sin_resolver.most_common()])
    guardar("placeholders_excluidos.json",
            [{"texto_original": t, "apariciones": n} for t, n in placeholders.most_common()])
    guardar("personas_candidatas.json", candidatos)

    resumen = {
        "fecha_consulta": FECHA_CONSULTA,
        "ensayos_admitidos": len(ensayos),
        "ensayos_ya_en_la_muestra": sum(1 for e in ensayos.values() if e["ya_en_la_muestra"]),
        "instituciones_canonicas": len(inst_out),
        "instituciones_nuevas": sum(1 for i in inst_out if not i["ya_en_la_muestra"]),
        "sedes_sin_resolver": sum(sin_resolver.values()),
        "placeholders_excluidos": sum(placeholders.values()),
        "personas_candidatas_por_clase": dict(collections.Counter(c["clasificacion"] for c in candidatos)),
        "por_area": {a: sum(1 for e in ensayos.values() if a in e["areas_consultadas"])
                     for a in sorted(crudo)},
        "por_estado": dict(collections.Counter(e["estado_fuente"] for e in ensayos.values())),
    }
    guardar("resumen.json", resumen)
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return resumen


if __name__ == "__main__":
    main()
