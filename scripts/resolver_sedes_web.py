#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resuelve sedes de ensayos que quedaron "en cola de resolución", con evidencia buscada en la web.

La beta dejó 262 ensayos sin institución: ClinicalTrials.gov declara una sede en Chile, pero su
texto ("CIDO SpA-Oncology ( Site 0302)", "Instituto Oncologico, Clinica Renaca") no calzaba con
ningún alias documentado. Este script aplica una tabla escrita a mano después de buscar cada
sede en fuentes públicas, con la misma regla de siempre: un texto se liga a una institución solo
por un alias explícito, con su motivo, y cada institución nueva trae la URL que la respalda.

Hay dos tablas:

  ALIAS_EXISTENTES  texto de la fuente → institución que ya estaba en la muestra, con el motivo.
  NUEVAS            instituciones que no estaban. Cada una con los textos que la nombran en
                    ClinicalTrials.gov, su evidencia (registro DEIS del Minsal cuando existe,
                    página oficial o de un tercero cuando no), y avisos cuando algo no cierra.

Lo que NO se resuelve queda en la cola, a propósito: marcadores del patrocinador ("Site 122",
"Exelixis Clinical Site #100"), nombres de personas escritos como sede ("Karol Ramírez"), textos
truncados, y sedes que la fuente declara en Chile pero cuyo nombre es de otro país ("Hospital
Amaral Carvalho", que está en Jaú, Brasil).

Nada se confirma: todo entra `pendiente`. Correrlo dos veces no cambia nada.

Uso:  python3 scripts/resolver_sedes_web.py
"""
import collections
import datetime
import json
import os
import urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = "2026-09-28"
SALIDA = os.path.join(RAIZ, "data", "pending", "sedes-web-" + FECHA)
DEIS = "https://datos.gob.cl/dataset/establecimientos-de-salud-vigentes"
SUB_SITIO = "Centro con sitio de ensayos clínicos en Chile"

ALIAS_EXISTENTES = {
    "Instituto Nacional de Cancer": ("inc", "misma institución sin tilde ni artículo"),
    "Cilnica Santa Maria": ("clinica-santa-maria", "errata de «Clínica»; la fuente la ubica en Providencia, "
                                                  "donde está Clínica Santa María"),
    "Fundación Arturo Pérez López": ("falp", "apellidos del fundador en orden invertido"),
    "Hospital Salvador": ("hosp-salvador", "mismo nombre sin el artículo; Santiago"),
    "IRAM": ("iram", "sigla del Instituto de Radiomedicina"),
    "IRAM - Chile": ("iram", "sigla del Instituto de Radiomedicina"),
    "IRAM - Instituto de Radio Medicina": ("iram", "mismo nombre, separado en dos palabras"),
    "Instituto de Radiomedicine": ("iram", "nombre a medio traducir"),
    "Clinica IRAM": ("iram", "sigla del Instituto de Radiomedicina; la fuente lo ubica en Vitacura"),
    "Iram Cancer Research ( Site 0198)": ("iram", "sigla del Instituto de Radiomedicina + código de sitio"),
    "Iram Cancer Research ( Site 0909)": ("iram", "sigla del Instituto de Radiomedicina + código de sitio"),
    "Iram Cancer Research ( Site 2809)": ("iram", "sigla del Instituto de Radiomedicina + código de sitio"),
    "INTOP": ("itop", "sigla del Instituto de Terapias Oncológicas Providencia"),
    "Instituto de Tereplas Oncologicas Providencia INTOP": ("itop", "errata de «Terapias», con la sigla"),
    "Instituto de Terapias Oncologicas": ("itop", "mismo nombre sin la comuna"),
    "Hosp Regional de Concepcion": ("hosp-concepcion", "abreviatura de Hospital Clínico Regional de Concepción"),
    "Hospital Base de Puerto Montt": ("hosp-puerto-montt", "único hospital base de Puerto Montt"),
    "Hospital de Puerto Montt": ("hosp-puerto-montt", "mismo hospital, sin «Base»"),
    "Universidad de Concepción": ("udec", "mismo nombre"),
    "Faculty of Medicine, University of Chile": ("uchile", "Facultad de Medicina de la Universidad de Chile"),
    "Department of Surgery, Clinical Hospital, University of Chile": (
        "hosp-uchile", "Departamento de Cirugía del Hospital Clínico de la Universidad de Chile"),
    "Servicio de Oncologia-Hospital Clinico Unversidad de Chile": (
        "hosp-uchile", "errata de «Universidad»; la fuente lo ubica en Independencia, donde está el hospital"),
    "Pontifica Universidad Catolica De Chile": ("puc", "errata de «Pontificia»"),
    "Facultad de medicina UC": ("puc", "Facultad de Medicina de la Pontificia Universidad Católica"),
    "Centro de Investigaciones Clinicas de la Universidad Catolica": ("puc", "unidad de la Universidad Católica"),
    "Instituto de Salud Publica": ("isp", "mismo nombre sin «de Chile»"),
    "Centro de Investigaciones Clinicas": ("cic-vina", "la fuente lo ubica en Viña del Mar: es el nombre del "
                                                       "centro sin la ciudad"),
    "Medical Research Limited Society": ("sim", "traducción literal de «Sociedad de Investigaciones Médicas "
                                                "Limitada»; misma ciudad, Temuco"),
    "Instituto Clinico Oncologico": ("icos", "nombre de ICOS sin «del Sur»; misma ciudad, Temuco"),
    "ACEREY Centro de Investigación Clínica Oncológica": (
        "oncocentro", "la propia fuente escribe «ONCOCENTRO APYS-ACEREY» en otro ensayo; misma ciudad, Viña del Mar"),
}


def deis(codigo, glosa, comuna):
    return {"url": DEIS, "tipo": "otro",
            "hecho": "Registro de establecimientos de salud del DEIS (Minsal): «%s», comuna de %s, código %s."
                     % (glosa, comuna, codigo)}


NUEVAS = [
    {"id": "cido", "nombre": "CIDO — Centro de Investigación y Desarrollo Oncológico", "ciudad": "Temuco",
     "deis": "200602",
     "textos": ["CIDO SpA-Oncology ( Site 0302)", "CIDO SpA ( Site 0212)", "CIDO SpA ( Site 1509)",
                "CIDO SpA-Oncology ( Site 0508)", "CIDO SpA-Oncology ( Site 0608)", "CIDO SpA-Oncology ( Site 0707)",
                "CIDO SpA-Oncology ( Site 0708)", "CIDO SpA-Oncology ( Site 2106)", "CIDO SpA-Oncology ( Site 2256)",
                "CIDO SpA-Oncology ( Site 4106)", "Centro de Investigacion y Desarrollo Oncologico",
                "Centro de Investigacion y desarrollo Oncologico SpA - CIDO SpA ( Site 0380)",
                "Centro de Investigacion y desarrollo Oncologico SpA - CIDO SpA ( Site 2808)",
                "Centro de investigacion y desarrollo oncolgico Spa", "Clinica CIDO"],
     "evidencia": [deis("200602", "Clínica Oncológica CIDO SpA", "Temuco"),
                   {"url": "https://estudiosclinicos.cl/category/establecimiento/centro-de-investigacion-y-desarollo-oncologico-cido/",
                    "tipo": "otro",
                    "hecho": "El buscador de estudios clínicos de la Cámara de la Innovación Farmacéutica lista a "
                             "«Centro de Investigación y Desarollo Oncologico (CIDO)» como establecimiento."}]},
    {"id": "instituto-oncologico-vina", "nombre": "Instituto Oncológico — Clínica Bupa Reñaca",
     "ciudad": "Viña del Mar", "deis": "107206",
     "textos": ["Instituto Oncologico", "Instituto Oncologico Ltda.", "Instituto Oncologico Clinica Renaca",
                "Instituto Oncologico, Clinica Renaca", "Clinica Renaca", "Clinica Renaca - Gocchi"],
     "evidencia": [{"url": "https://www.clinicabuparenaca.cl/unidades-clinicas-y-servicios/centro-de-oncologia",
                    "tipo": "otro",
                    "hecho": "Clínica Bupa Reñaca: «La radioterapia se realiza gracias al convenio vigente con el "
                             "Instituto Oncológico que funciona en dependencias del 2º piso de Clínica Bupa Reñaca»."},
                   deis("107206", "Clínica Reñaca", "Viña del Mar")],
     "avisos": ["Los textos «Instituto Oncologico» y «Clinica Renaca» se ligan al mismo centro porque la clínica "
                "declara que el Instituto funciona en su edificio y la fuente los ubica en Reñaca / Viña del Mar. "
                "No se verificó que cada ensayo corra en el Instituto y no en otra unidad de la clínica."]},
    {"id": "centro-oncologico-norte", "nombre": "Centro Oncológico del Norte", "ciudad": "Antofagasta",
     "deis": "200508",
     "textos": ["Centro Oncologico del Norte", "Centro Oncológico del Norte",
                "Centro de Investigación Oncológica del Norte ( Site 0504)", "Centro Oncologico Antofagasta",
                "Centro Oncologico Antofagasta ( Site 0206)", "Centro Oncologico Antofagasta ( Site 0386)",
                "Centro Oncologico Antofagasta ( Site 0914)", "Centro Oncologico Antofagasta ( Site 2804)",
                "Centro Oncológico Antofagasta"],
     "evidencia": [deis("200508", "Centro Oncológico del Norte (CON)", "Antofagasta"),
                   {"url": "https://centrooncologicodelnorte.cl/", "tipo": "otro",
                    "hecho": "El sitio oficial se titula «Centro Oncologico del Norte – Centro Oncologico de "
                             "Antofagasta»: los dos nombres son del mismo centro."}]},
    {"id": "cics-temuco", "nombre": "Centro de Investigación Clínica del Sur", "ciudad": "Temuco",
     "textos": ["Centro de Investigacion Clinica del Sur", "Centro Investigacion Clinica Del Sur",
                "Centro Investigacion Clinica del Sur", "Centro de Investigación Clínica del Sur"],
     "evidencia": [{"url": "https://www.portalchile.org/empresa/centro-de-investigacion-clinica-del-sur-limitada-76602780",
                    "tipo": "otro",
                    "hecho": "Registro comercial: Centro de Investigación Clínica del Sur Limitada, Temuco."}],
     "avisos": ["Dos directorios dan direcciones distintas en Temuco; no se ubicó en el mapa."]},
    {"id": "centro-cancer-uc", "nombre": "Centro de Cáncer Nuestra Señora de la Esperanza (UC CHRISTUS)",
     "ciudad": "Santiago", "deis": "200699",
     "textos": ["Centro de Cancer Nuestra Senora de la Esperanza ( Site 1063)",
                "Centro de Cancer Nuestra Senora de la Esperanza ( Site 0065)",
                "Centro de Cancer Pontificie Universidad Catolica de Chile"],
     "evidencia": [deis("200699", "Centro de Cáncer Red de Salud UC CHRISTUS", "Santiago"),
                   {"url": "https://www.ucchristus.cl/blog-salud-uc/articulos/2023/centro-de-c%C3%A1ncer-nuestra-se%C3%B1ora-de-la-esperanza-cumple-25-a%C3%B1os",
                    "tipo": "otro", "hecho": "UC CHRISTUS: el Centro de Cáncer Nuestra Señora de la Esperanza cumple 25 años."}]},
    {"id": "hosp-clinico-uc", "nombre": "Hospital Clínico UC CHRISTUS", "ciudad": "Santiago",
     "textos": ["Hospital Clinico Universidad Catolica de Chile", "Hospital Clínico de la Pontificia Univ. Católica de Chile"],
     "evidencia": [], "avisos": ["El DEIS no tiene un registro con este nombre; no se ubicó en el mapa."]},
    {"id": "clinica-uc-san-carlos", "nombre": "Clínica UC CHRISTUS San Carlos de Apoquindo", "ciudad": "Las Condes",
     "deis": "112261",
     "textos": ["Clinica UC San Carlos de Apoquindo", "Clínica UC San Carlos de Apoquindo",
                "Clínica UC San Carlos de Apoquindo ( Site 0043)", "Clínica UC San Carlos de Apoquindo ( Site 0211)",
                "Clínica UC San Carlos de Apoquindo ( Site 0305)",
                "Clínica UC San Carlos de Apoquindo-Hemato-Oncology ( Site 2402)"],
     "evidencia": [deis("112261", "Clínica San Carlos de Apoquindo Red de Salud UC CHRISTUS", "Las Condes")]},
    {"id": "uc-san-joaquin", "nombre": "Centro Médico San Joaquín UC CHRISTUS", "ciudad": "Macul", "deis": "112512",
     "textos": ["San Joaquín Medical Center, UCChristus Health Network"],
     "evidencia": [deis("112512", "Centro Médico San Joaquín Red de Salud UC CHRISTUS", "Macul")]},
    {"id": "clinica-davila-vespucio", "nombre": "Clínica Dávila Vespucio (ex Clínica Vespucio)", "ciudad": "La Florida",
     "deis": "114223",
     "textos": ["Clinica Vespucio", "Clínica Vespucio ( Site 0205)", "Clínica Vespucio-Hemato - Ocology ( Site 0607)"],
     "evidencia": [deis("114223", "Clínica Dávila Vespucio", "La Florida"),
                   {"url": "https://www.davila.cl/conoce-la-nueva-davila-vespucio/", "tipo": "otro",
                    "hecho": "Clínica Dávila presenta la «nueva Dávila Vespucio», el antiguo edificio de Clínica Vespucio."}]},
    {"id": "meds-la-dehesa", "nombre": "Clínica MEDS La Dehesa", "ciudad": "Lo Barnechea", "deis": "200234",
     "textos": ["Clínica MEDS La Dehesa ( Site 0509)"],
     "evidencia": [deis("200234", "Clínica MEDS La Dehesa", "Lo Barnechea")]},
    {"id": "hosp-roberto-del-rio", "nombre": "Hospital Clínico de Niños Dr. Roberto del Río", "ciudad": "Santiago",
     "deis": "109101",
     "textos": ["Hospital Roberto Del Rio", "Hospital Roberto del Rio", "Hospital Roberto del Rio-Universidad de Chile",
                "Department of Pediatrics Hematology and Oncology, Hospital Roberto del Rio"],
     "evidencia": [deis("109101", "Hospital Clínico de Niños Dr. Roberto del Río (Santiago, Independencia)", "Independencia")]},
    {"id": "hosp-tisne", "nombre": "Hospital Santiago Oriente Dr. Luis Tisné Brousse", "ciudad": "Santiago",
     "deis": "112101",
     "textos": ["Hospital Luis Tisne Brousse", "Hospital Santiago Oriente Dr. Luis Tisne Brousse"],
     "evidencia": [deis("112101", "Hospital Dr. Luis Tisné B. (Santiago, Peñalolén)", "Peñalolén")]},
    {"id": "hosp-dipreca", "nombre": "Hospital DIPRECA", "ciudad": "Santiago", "deis": "112248",
     "textos": ["Hospital DIPRECA", "Hospital Dirección de Previsión de Carabineros"],
     "evidencia": [deis("112248", "Hospital Dipreca Teniente Hernán Merino", "Las Condes")],
     "avisos": ["No es el Hospital de Carabineros (otra ficha): el de la Dirección de Previsión es DIPRECA."]},
    {"id": "hosp-fach", "nombre": "Hospital FACh", "ciudad": "Santiago", "deis": "112238",
     "textos": ["Hospital FACH"], "evidencia": [deis("112238", "Hospital FACH", "Las Condes")]},
    {"id": "hosp-naval-vina", "nombre": "Hospital Naval Almirante Nef", "ciudad": "Viña del Mar", "deis": "107217",
     "textos": ["Hospital Naval Almirante Nef"], "evidencia": [deis("107217", "Hospital Naval Almirante Neff", "Viña del Mar")]},
    {"id": "hosp-san-jose", "nombre": "Complejo Hospitalario San José", "ciudad": "Santiago", "deis": "109100",
     "textos": ["Hospital San Jose"],
     "evidencia": [deis("109100", "Complejo Hospitalario San José (Santiago, Independencia)", "Independencia")],
     "avisos": ["Hay varios Hospital San José en Chile; se eligió el de Santiago porque es la ciudad que declara la fuente."]},
    {"id": "hosp-san-pablo-coquimbo", "nombre": "Hospital San Pablo de Coquimbo", "ciudad": "Coquimbo", "deis": "105101",
     "textos": ["Hospital San Pablo"], "evidencia": [deis("105101", "Hospital San Pablo (Coquimbo)", "Coquimbo")]},
    {"id": "hosp-la-serena", "nombre": "Hospital San Juan de Dios de La Serena", "ciudad": "La Serena", "deis": "105100",
     "textos": ["Hospital Regional de La Serena ( Site 0907)"],
     "evidencia": [deis("105100", "Hospital San Juan de Dios (La Serena)", "La Serena")],
     "avisos": ["La fuente lo llama «Hospital Regional de La Serena»; el DEIS registra un solo hospital en la "
                "comuna, el San Juan de Dios."]},
    {"id": "hosp-coyhaique", "nombre": "Hospital Regional de Coyhaique", "ciudad": "Coyhaique", "deis": "125100",
     "textos": ["Hospital regional de Coyhaique"], "evidencia": [deis("125100", "Hospital Regional de Coyhaique", "Coyhaique")]},
    {"id": "hosp-hanga-roa", "nombre": "Hospital Hanga Roa", "ciudad": "Isla de Pascua", "deis": "112107",
     "textos": ["Hospital Hanga Roa"], "evidencia": [deis("112107", "Hospital Hanga Roa (Isla De Pascua)", "Isla de Pascua")]},
    {"id": "hosp-arica", "nombre": "Hospital Regional Dr. Juan Noé Crevani", "ciudad": "Arica", "deis": "101100",
     "textos": ["Hospital Base de Arica"],
     "evidencia": [deis("101100", "Hospital Regional Dr. Juan Noé Crevani (Arica)", "Arica")],
     "avisos": ["La fuente lo llama «Hospital Base de Arica»; es el único hospital público de la ciudad en el DEIS."]},
    {"id": "hosp-villarrica", "nombre": "Hospital de Villarrica", "ciudad": "Villarrica", "deis": "121121",
     "textos": ["Hospital de Villarrica"], "evidencia": [deis("121121", "Hospital de Villarrica", "Villarrica")]},
    {"id": "hosp-victoria", "nombre": "Hospital San José de Victoria", "ciudad": "Victoria", "deis": "129106",
     "textos": ["Hospital de Victoria"], "evidencia": [deis("129106", "Hospital San José de Victoria", "Victoria")]},
    {"id": "hosp-nueva-imperial", "nombre": "Hospital Intercultural de Nueva Imperial", "ciudad": "Nueva Imperial",
     "deis": "121114", "textos": ["Hospital Intercultural"],
     "evidencia": [deis("121114", "Hospital Intercultural de Nueva Imperial", "Nueva Imperial")]},
    {"id": "hosp-curanilahue", "nombre": "Hospital Provincial Dr. Rafael Avaria (Curanilahue)", "ciudad": "Curanilahue",
     "deis": "128109", "textos": ["Hospital de Curanilahue"],
     "evidencia": [deis("128109", "Hospital Provincial Dr. Rafael Avaría (Curanilahue)", "Curanilahue")]},
    {"id": "hosp-molina", "nombre": "Hospital Santa Rosa de Molina", "ciudad": "Molina", "deis": "116102",
     "textos": ["Hospital Santa Rosa de Molina"], "evidencia": [deis("116102", "Hospital de Molina", "Molina")],
     "avisos": ["El DEIS lo registra como «Hospital de Molina», el único hospital de la comuna."]},
    {"id": "cesfam-el-roble", "nombre": "CESFAM El Roble", "ciudad": "La Pintana", "deis": "114319",
     "textos": ["CESFAM El Roble"],
     "evidencia": [deis("114319", "Centro de Salud Familiar El Roble", "La Pintana")]},
    {"id": "cesfam-juan-pablo-ii", "nombre": "CESFAM Juan Pablo II", "ciudad": "Santiago",
     "textos": ["CESFAM Juan Pablo II"], "evidencia": [],
     "avisos": ["El DEIS tiene dos CESFAM con este nombre en la Región Metropolitana (La Pintana y San Bernardo); "
                "no se eligió ninguno."]},
    {"id": "health-care-chile", "nombre": "Health & Care SpA", "ciudad": "Santiago",
     "textos": ["Health & Care SPA", "Health & Care Spa", "Health and Care Chile ( Site 0202)",
                "Health and Care Chile ( Site 0901)"],
     "evidencia": [], "avisos": ["No se encontró una página pública del centro: existe solo por su nombre en la fuente."]},
    {"id": "rey-oreilly", "nombre": "Rey y O'Reilly Limitada", "ciudad": "Temuco",
     "textos": ["Rey y Oreilly Limitada ( Site 1048)"], "evidencia": [],
     "avisos": ["Razón social sin página pública encontrada: existe solo por su nombre en la fuente."]},
    {"id": "aren-bachero", "nombre": "Sociedad Médica Arén y Bachero Limitada", "ciudad": "Santiago",
     "textos": ["Sociedad Medica Aren y Bachero Limitada ( Site 0207)", "Sociedad Medica Aren y Bachero Limitada ( Site 0426)"],
     "evidencia": [], "avisos": ["Razón social sin página pública encontrada: existe solo por su nombre en la fuente."]},
    {"id": "ceos", "nombre": "Centro de Estudios Oncológicos de Santiago (CEOS)", "ciudad": "Santiago",
     "textos": ["Centro de Estudios Oncologicos Santiago", "Centro de Estudios Oncologicos de Santiago (CEOS) Oncologia"],
     "evidencia": []},
    {"id": "urumed", "nombre": "Servicios Médicos Urumed", "ciudad": "Rancagua",
     "textos": ["Servicios Medicos Urumed ( Site 0405)"],
     "evidencia": [{"url": "https://www.unensayoparami.org/es/sitios/servicios-medicos-urumed", "tipo": "otro",
                    "hecho": "Un Ensayo para Mí lista «Servicios Médicos Urumed» como sitio de ensayos en Rancagua, O'Higgins."}]},
    {"id": "cec-suecia", "nombre": "Centro de Estudios Clínicos Suecia", "ciudad": "Santiago",
     "textos": ["Centro De Estudios Clínicos Suecia SpA"],
     "evidencia": [{"url": "https://suecia-cec.cl/", "tipo": "otro",
                    "hecho": "Sitio oficial del Centro de Estudios Clínicos Suecia."}]},
    {"id": "ufro", "nombre": "Universidad de La Frontera", "ciudad": "Temuco",
     "textos": ["Universidad de La Frontera",
                "Department of Rehabilitation Sciences, Faculty of Medicine, Universidad de La Frontera. Temuco, Chile"],
     "evidencia": []},
    {"id": "ucn", "nombre": "Universidad Católica del Norte", "ciudad": "Coquimbo",
     "textos": ["Universidad Católica del Norte"], "evidencia": []},
    {"id": "ucmaule", "nombre": "Universidad Católica del Maule", "ciudad": "Talca",
     "textos": ["Catholic University of Maule"], "evidencia": [],
     "avisos": ["Es la universidad, no la Clínica Universidad Católica del Maule (otra ficha)."]},
    {"id": "conac", "nombre": "Corporación Nacional del Cáncer (CONAC)", "ciudad": "Santiago",
     "textos": ["Corporacion Nacional del Cancer"], "evidencia": []},
    {"id": "cormun-puente-alto", "nombre": "Corporación de Salud Municipal de Puente Alto", "ciudad": "Puente Alto",
     "textos": ["Corporación de Salud Municipal de Puente Alto"], "evidencia": []},
    {"id": "icer-lab", "nombre": "ICER-Lab", "ciudad": "Talcahuano", "textos": ["ICER-Lab"], "evidencia": []},
    {"id": "clinica-las-nieves", "nombre": "Clínica Las Nieves", "ciudad": "Santiago",
     "textos": ["Clinica Las Nieves"], "evidencia": []},
    {"id": "benef-osorno", "nombre": "Corporación de Beneficencia Osorno", "ciudad": "Osorno",
     "textos": ["Corporacion de Beneficencia Osorno"], "evidencia": []},
    {"id": "enroll", "nombre": "Enroll SpA", "ciudad": "Providencia", "textos": ["Enroll SpA"], "evidencia": []},
    {"id": "meditek", "nombre": "Meditek Ltda.", "ciudad": "Santiago", "textos": ["Meditek Ltda."], "evidencia": []},
    {"id": "dermacross", "nombre": "Clínica Dermacross", "ciudad": "Santiago",
     "textos": ["Clinica Dermacross S.A."], "evidencia": []},
    {"id": "dermovein", "nombre": "Clínica Dermovein", "ciudad": "Santiago",
     "textos": ["Clinica Dermovein S.A."], "evidencia": []},
    {"id": "ced-vina", "nombre": "Centro de Especialidades Dermatológicas", "ciudad": "Viña del Mar",
     "textos": ["Centro de Especialidades Dermatologicas"], "evidencia": []},
]


def url_busqueda(texto):
    return "https://clinicaltrials.gov/search?locStr=Chile&term=" + urllib.parse.quote_plus(texto)


def main():
    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]
    por_id = {e["id"]: e for e in ent}

    destino = {}
    for texto, (iid, motivo) in ALIAS_EXISTENTES.items():
        if iid not in por_id:
            raise SystemExit("ALIAS_EXISTENTES apunta a una institución que no existe: " + iid)
        destino[texto] = (iid, motivo)
    nuevas_creadas = []
    for n in NUEVAS:
        if n["id"] in por_id and por_id[n["id"]]["tipo"] != "institucion":
            raise SystemExit("id ocupado por otra entidad: " + n["id"])
        for t in n["textos"]:
            if t in destino:
                raise SystemExit("texto asignado dos veces: " + t)
            destino[t] = (n["id"], "institución nueva, ver su evidencia")

    ya = {(v["origen"], v["destino"]) for v in vin}
    usados = collections.defaultdict(list)
    ligados = collections.Counter()
    for e in ent:
        if e["tipo"] != "ensayo_clinico" or not e.get("sedes_pendientes_resolucion"):
            continue
        quedan = []
        for texto in e["sedes_pendientes_resolucion"]:
            if texto not in destino:
                quedan.append(texto)
                continue
            iid = destino[texto][0]
            usados[iid].append(texto)
            if (iid, e["id"]) not in ya:
                vin.append({"origen": iid, "destino": e["id"], "tipo": "sitio del ensayo", "alias_fuente": texto})
                ya.add((iid, e["id"]))
                ligados[e["id"]] += 1
        if quedan:
            e["sedes_pendientes_resolucion"] = quedan
        else:
            del e["sedes_pendientes_resolucion"]

    for n in NUEVAS:
        if n["id"] in por_id:
            continue
        textos = [t for t in n["textos"] if t in usados[n["id"]]] or n["textos"]
        hechos = [{"tipo": "afiliacion",
                   "hecho": "Figura como sede chilena de ensayos clínicos en ClinicalTrials.gov, escrita en la fuente "
                            "como \"%s\"." % textos[0],
                   "fuente_url": url_busqueda(textos[0]), "fecha": FECHA, "confianza": "pendiente"}]
        for ev in n["evidencia"]:
            hechos.append({"tipo": ev["tipo"], "hecho": ev["hecho"], "fuente_url": ev["url"], "fecha": FECHA,
                           "confianza": "pendiente"})
        ficha = {"id": n["id"], "nombre": n["nombre"], "tipo": "institucion", "ciudad": n["ciudad"],
                 "subtitulo": SUB_SITIO, "alias_en_la_fuente": n["textos"], "hechos": hechos}
        if n.get("avisos"):
            ficha["nota_identidad"] = " ".join(n["avisos"])
        ent.append(ficha)
        por_id[n["id"]] = ficha
        nuevas_creadas.append(n["id"])

    for texto, (iid, motivo) in ALIAS_EXISTENTES.items():
        if texto in usados[iid]:
            alias = por_id[iid].setdefault("alias_en_la_fuente", [])
            if texto not in alias:
                alias.append(texto)

    base["actualizado"] = datetime.date.today().isoformat()
    json.dump(base, open(MUESTRA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    os.makedirs(SALIDA, exist_ok=True)
    en_cola = collections.Counter(t for e in ent for t in e.get("sedes_pendientes_resolucion") or [])
    inst_link = {x for v in vin if v["tipo"] in ("sitio del ensayo", "investigador de sitio") for x in (v["origen"], v["destino"])}
    resumen = {
        "fecha": FECHA,
        "instituciones_nuevas": len(nuevas_creadas),
        "alias_a_instituciones_existentes": len(ALIAS_EXISTENTES),
        "vinculos_nuevos_sitio_del_ensayo": sum(ligados.values()),
        "ensayos_que_ganaron_institucion": len(ligados),
        "ensayos_sin_institucion_despues": sum(1 for e in ent if e["tipo"] == "ensayo_clinico" and e["id"] not in inst_link),
        "textos_que_siguen_en_cola": len(en_cola),
    }
    json.dump(resumen, open(os.path.join(SALIDA, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"alias_a_existentes": [{"texto": t, "institucion": i, "motivo": m} for t, (i, m) in ALIAS_EXISTENTES.items()],
               "nuevas": NUEVAS,
               "siguen_en_cola": [{"texto": t, "ensayos": c} for t, c in en_cola.most_common()]},
              open(os.path.join(SALIDA, "decisiones.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
