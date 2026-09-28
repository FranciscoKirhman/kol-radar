#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea las fichas de fármaco a partir de las intervenciones que declara ClinicalTrials.gov.

Un MSL busca por fármaco tanto como por persona: "¿quién trabaja con pembrolizumab en Chile?".
Hasta ahora el ensayo guardaba un resumen escrito a mano de su intervención, que no se podía
buscar ni conectar. Este script vuelve a la fuente, lee la lista estructurada de intervenciones
de cada ensayo y crea un fármaco por principio activo, unido a cada ensayo que lo evalúa.

Reglas, todas explícitas:

  1. Solo entran intervenciones de tipo DRUG, BIOLOGICAL, COMBINATION_PRODUCT o GENETIC. Las de
     tipo OTHER, PROCEDURE, RADIATION, DEVICE, etc. no son fármacos.
  2. No crean fármaco ni vínculo: placebos, cuidados de soporte, premedicaciones y clases
     genéricas ("chemotherapy", "LHRH agonist", "H1 receptor antagonist"). La lista está abajo,
     en EXCLUIR, y cada exclusión queda registrada en el artefacto de revisión con su motivo.
     La ficha del ensayo sigue mostrando la intervención completa: solo no se dibuja la arista.
  3. Una intervención compuesta se separa en sus componentes solo cuando la fuente los escribe
     unidos por "+", "/", " plus ", " and ", "(+)" o "formulated with". Un régimen con nombre
     propio (FOLFOX) no se expande: eso sería inferir su composición.
  4. Dos nombres se unen en un mismo fármaco solo por normalización tipográfica (mayúsculas,
     tildes, ®, sufijo de sal, sufijo de cuatro letras de la FDA) o porque la propia fuente los
     declara equivalentes en `otherNames`, y solo cuando esa equivalencia no es ambigua: si un
     código aparece asociado a dos principios activos distintos en la fuente, no se une a
     ninguno. Nada se une por parecido de nombre.
  5. Cada vínculo ensayo → fármaco guarda el nombre literal con que la fuente escribió la
     intervención. Cada hecho del fármaco apunta a la URL exacta del ensayo.
  6. Nada se marca como confirmado. Todo entra como `pendiente`.

Idempotente: borra los fármacos y vínculos de intervención de una corrida anterior antes de
volver a crearlos.

Uso:
    python3 scripts/integrar_farmacos_ctgov.py            # consulta la API
    KOL_CRUDO_CTGOV=ruta.json python3 scripts/...         # reutiliza una descarga previa
"""
import collections
import datetime
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
FECHA = datetime.date.today().isoformat()
SALIDA = os.path.join(RAIZ, "data", "pending", "farmacos-ctgov-" + FECHA)
API = "https://clinicaltrials.gov/api/v2/studies"
TIPOS_FARMACO = {"DRUG", "BIOLOGICAL", "COMBINATION_PRODUCT", "GENETIC"}
TIPO_LEGIBLE = {"DRUG": "fármaco", "BIOLOGICAL": "biológico",
                "COMBINATION_PRODUCT": "producto combinado", "GENETIC": "terapia génica"}
VINCULO = "intervención"

# Motivo → patrón. Se evalúan sobre el nombre ya normalizado (minúsculas, sin tildes).
EXCLUIR = [
    # "palcebo" es una errata de la propia fuente, no un fármaco.
    ("placebo o vehículo", r"\bplacebo\b|\bpalcebo\b|\bvehicle\b|\bsaline\b|\bsham\b|\bmatching\b|^dextrose$|^water$"),
    ("cuidado de soporte o rescate", r"\bsupportive\b|\brescue\b|\bbest supportive\b|\busual care\b"
                                     r"|\bstandard of care\b|^soc$|\bpremedication"),
    ("clase o esquema genérico, no un principio activo",
     r"chemotherap|\bchemo\b|\btreatment\b|\btherapy\b|\bregimen\b|\bagonist\b"
     r"|\bantagonist\b|\binhibitors?\b|\bphysician'?s choice\b|\binvestigator'?s choice\b"
     r"|\bhormonal\b|\bendocrine\b|\bcorticosteroids?\b|\bsteroids?\b|\bantiemetics?\b"
     r"|\bmouthwash\b|\bor equivalent\b|\bdrug:|\bstandard\b"),
    ("premedicación o soporte habitual",
     r"^(dexamethasone|methylprednisolone|prednisone|prednisolone|predinsone|prenisolone|hydrocortisone|fludrocortisone"
     r"|folic acid|vitamin b12|b12|cyanocobalamin|acetaminophen|paracetamol|diphenhydramine"
     r"|ondansetron|granisetron|palonosetron|aprepitant|fosaprepitant|ranitidine|famotidine"
     r"|cetirizine|loratadine|chlorphenamine|clemastine|ibuprofen|allopurinol|mesna"
     r"|calcium|vitamin d|simethicone)$|transfusion"),
]
SALES = r" (acetate|sulfate|sulphate|hydrochloride|hcl|mesylate|maleate|dimaleate|citrate|tosylate" \
        r"|sodium|disodium|malate|besylate|succinate|tartrate|phosphate|bromide|fumarate|dihydrochloride)$"
SEPARADORES = r"\s*\(\+\)\s*|\s+formulated with\s+|\s*\+\s*|\s*/\s*|\s+plus\s+|\s+and\s+|\s+or\s+" \
              r"|\s+with\s+|\s*;\s*|,\s+"
# Equivalencias tipográficas universales (no dependen de la fuente): prefijos y abreviaturas INN.
TIPOGRAFICAS = {"5-fluorouracil": "fluorouracil", "5-fu": "fluorouracil", "5fu": "fluorouracil",
                "nab paclitaxel": "nab-paclitaxel", "albumin-bound paclitaxel": "nab-paclitaxel",
                "abraxane": "nab-paclitaxel"}


def sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def normalizar(t):
    """Clave de comparación: minúsculas, sin tildes, sin ®/™, sin dosis, vía, sufijo de sal ni
    sufijo FDA. Solo tipografía: no cambia un principio activo por otro."""
    t = sin_tildes(t).lower()
    for marca in ("\u00ae", "\u2122", "\u00a9", "^tm", "^", "\u00a0"):
        t = t.replace(marca, " " if marca == "\u00a0" else "")
    t = re.sub(r"\s+", " ", t).strip(" .,;:-")
    t = re.sub(r"\s+\d+(\.\d+)?\s*(mg|mcg|ug|g|iu|ui|ml)(/m2|/kg)?\b.*$", "", t)   # dosis
    t = re.sub(r"^(intrathecal|intravenous|subcutaneous|oral|iv|sc|combination product:) ", "", t)
    t = re.sub(r" (for subcutaneous (use|administration)|for intravenous use|iv|sc|po|dp|oral"
               r"|intravenous|subcutaneous|injection|tablets?|capsules?|in combination|-eu|-us)$", "", t)
    t = re.sub(r"-(eu|us)$", "", t)
    t = re.sub(r" regimen$", "", t)
    t = re.sub(r"^(fam|ado)-", "", t)
    t = re.sub(r"(\w{6,})-[a-z]{4}$", r"\1", t)          # govitecan-hziy → govitecan
    t = re.sub(r"(\w{6,})-[a-z]{4}(?= )", r"\1", t)
    t = re.sub(SALES, "", t)
    if re.fullmatch(r"[a-z]{1,5}[\s-]?\d[\d,.\-]*[a-z]?", t):   # BMS-936558 = BMS936558 = BMS 936558
        t = re.sub(r"[\s-]", "", t)
    t = re.sub(r"^(dexamethasone|acetaminophen).*equivalent.*$", r"\1", t)
    return TIPOGRAFICAS.get(t, t)


def parentesis(t):
    """Separa "Sorafenib (Nexavar, BAY43-9006)" en ("Sorafenib", ["Nexavar", "BAY43-9006"])."""
    dentro = re.findall(r"[\(\[]([^\)\]]*)[\)\]]", t)
    fuera = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]", "", t).strip()
    alias = []
    for d in dentro:
        for pieza in re.split(r"[,;]", d):
            pieza = pieza.strip()
            if pieza and pieza.lower() not in ("us", "eu", "+", "or equivalent"):
                alias.append(pieza)
    return fuera, alias


def componentes(nombre):
    """Parte una intervención compuesta. Devuelve [(texto_principal, [alias_de_paréntesis])]."""
    nombre = nombre.replace("(+)", " + ")
    nombre = re.sub(r",\s+(an?|the)\s.*$", "", nombre)      # "Atezolizumab, an engineered…"
    base, alias_global = parentesis(nombre)
    partes = [p for p in re.split(SEPARADORES, base, flags=re.I) if p and p.strip()]
    if len(partes) == 1:
        return [(partes[0], alias_global)]
    return [(p, []) for p in partes]   # alias entre paréntesis de un compuesto: ambiguos, se omiten


def parece_dci(clave):
    return bool(re.fullmatch(r"[a-z]{5,}( [a-z]{5,})*", clave))


# Terminaciones de denominación común internacional (OMS). Dos nombres que las tienen son dos
# principios activos distintos aunque la fuente los declare equivalentes: eso es un error de la
# fuente (hay un ensayo que da "Pembrolizumab" como otro nombre de adagrasib), no una sinonimia.
RAICES_DCI = r"(mab|tinib|rafenib|ciclib|parib|lisib|rasib|zomib|platin|taxel|rubicin|stine|lutamide" \
             r"|relix|relin|tecan|mustine|citabine|trexed|uracil|fosfamide|mide|dronate|zumab|ximab" \
             r"|cept|kin|leukin|tug|vedotin|deruxtecan|govitecan|tirumotecan|emtansine|strant|trozole" \
             r"|degib|metinib|alisib|lintinib|mig|limab)$"


def es_dci(clave):
    return bool(re.search(RAICES_DCI, clave.split()[-1] if clave.split() else clave))


RUIDO_ALIAS = r"^(sulfate|acetate|hydrochloride|mesylate|sodium|chile)$|\+|\b(adjuvant|neoadjuvant|generic|induction|maintenance|radiosensiti\w*|and|or|with|plus" \
              r"|for injection|injection concentrate|tablets?|capsules?|mg|m2|kg|dose|arm|cohort)\b|[\[\]]|\d\s*mg"


def alias_presentable(a):
    """Una marca, un código o una DCI. Descarta descripciones, dosis y nombres químicos."""
    a = a.replace("®", "").replace("™", "").replace("©", "").replace("^TM", "").replace("^", "").strip()
    if not a or len(a) > 32 or len(a.split()) > 3 or re.search(RUIDO_ALIAS, a, re.I):
        return None
    if a.count("-") > 2 or re.match(r"^[\d.\-]", a):
        return None
    return a


def motivo_exclusion(clave):
    for motivo, patron in EXCLUIR:
        if re.search(patron, clave):
            return motivo
    if len(clave) < 3 or not re.search(r"[a-z]", clave):
        return "texto demasiado corto para identificar un principio activo"
    return None


def descargar(ncts):
    out = {}
    for i in range(0, len(ncts), 100):
        lote = ncts[i:i + 100]
        url = API + "?filter.ids=" + ",".join(lote) + "&pageSize=100&format=json"
        r = json.load(urllib.request.urlopen(url, timeout=60))
        for s in r["studies"]:
            out[s["protocolSection"]["identificationModule"]["nctId"]] = s
        time.sleep(0.4)
    return out


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes(t).lower()).strip("-")


def main():
    base = json.load(open(MUESTRA, encoding="utf-8"))
    ent, vin = base["entidades"], base["vinculos"]

    # Corrida anterior fuera: la integración es reproducible desde la fuente.
    viejos = {e["id"] for e in ent if e["tipo"] == "farmaco"}
    ent[:] = [e for e in ent if e["tipo"] != "farmaco"]
    vin[:] = [v for v in vin if v["tipo"] != VINCULO and v["destino"] not in viejos]

    ensayos = {e["id"].upper(): e for e in ent if e["tipo"] == "ensayo_clinico"}
    ruta = os.environ.get("KOL_CRUDO_CTGOV")
    crudo = json.load(open(ruta, encoding="utf-8")) if ruta else descargar(sorted(ensayos))
    faltan = sorted(set(ensayos) - set(crudo))
    if faltan:
        sys.exit("La API no devolvió: " + ", ".join(faltan))

    # ------------------------------------------------ 1. menciones: (ensayo, clave, literal)
    menciones, excluidas = [], collections.defaultdict(lambda: {"motivo": None, "ensayos": set(), "literal": set()})
    grafo_alias = collections.defaultdict(set)     # clave principal ↔ clave de otro nombre
    literal_por_clave = collections.defaultdict(collections.Counter)
    alias_literal = collections.defaultdict(collections.Counter)
    for nct, s in crudo.items():
        for iv in s["protocolSection"].get("armsInterventionsModule", {}).get("interventions", []):
            if iv.get("type") not in TIPOS_FARMACO:
                continue
            otros = []
            for o in iv.get("otherNames") or []:
                otros += [p.strip() for p in re.split(r"[,;]", o) if p.strip()]
            partes = componentes(iv["name"])
            for texto, alias_par in partes:
                clave = normalizar(texto)
                motivo = motivo_exclusion(clave)
                if motivo:
                    x = excluidas[clave]
                    x["motivo"] = motivo
                    x["ensayos"].add(nct)
                    x["literal"].add(iv["name"])
                    continue
                menciones.append((nct, clave, iv["name"], iv["type"]))
                literal_por_clave[clave][texto.strip()] += 1
                # otherNames solo describen a la intervención si no es compuesta.
                for a in alias_par + (otros if len(partes) == 1 else []):
                    ca = normalizar(parentesis(a)[0] or a)
                    if ca and ca != clave and not motivo_exclusion(ca):
                        grafo_alias[clave].add(ca)
                        grafo_alias[ca].add(clave)
                        alias_literal[ca][a.replace("®", "").replace("™", "").strip()] += 1

    principales = collections.Counter(c for _, c, _, _ in menciones)

    # ------------------------------------------------ 2. uniones no ambiguas
    def vecinos_principales(c):
        return {v for v in grafo_alias[c] if v in principales}

    # a se une a b cuando TODAS las equivalencias que la fuente declara para a apuntan a b, y b
    # no es un nombre menos establecido que a. Así "Keytruda" y "MK-3475" se unen a
    # pembrolizumab, pero un código que la fuente asocia a dos principios activos no se une a
    # ninguno, y un error de la fuente en un solo ensayo no arrastra a un fármaco usado en setenta.
    def rango(k):
        return (not parece_dci(k), bool(re.search(r"\d", k)), -principales[k], k)

    padre = {c: c for c in principales}
    uniones = []
    for a in sorted(principales, key=rango, reverse=True):
        va = vecinos_principales(a)
        if len(va) != 1:
            continue
        b = next(iter(va))
        if rango(b) > rango(a) or (es_dci(a) and es_dci(b)):
            continue
        padre[a] = b
        uniones.append({"une": a, "en": b, "evidencia": "otherNames de ClinicalTrials.gov"})

    def raiz(c):
        vistos = set()
        while padre[c] != c and c not in vistos:
            vistos.add(c)
            c = padre[c]
        return c

    canon = {c: raiz(c) for c in principales}
    for u in uniones:
        u["en"] = canon[u["en"]]

    # Alias que no son nombre principal en ninguna parte (marcas y códigos): solo si apuntan a uno.
    alias_de = collections.defaultdict(set)
    for c in principales:
        alias_de[canon[c]].update(t for t, _ in literal_por_clave[c].most_common())
    for ca in grafo_alias:
        if ca in principales:
            continue
        destinos = {canon[v] for v in grafo_alias[ca] if v in principales}
        if len(destinos) == 1:
            alias_de[next(iter(destinos))].update(alias_literal[ca])

    # ------------------------------------------------ 3. fichas y vínculos
    por_farmaco = collections.defaultdict(dict)       # canon → {nct: [literales]}
    for nct, clave, literal, tipo in menciones:
        por_farmaco[canon[clave]].setdefault(nct, {"literal": set(), "tipo": tipo})["literal"].add(literal)

    def nombre_visible(c):
        cuenta = collections.Counter()
        for k, v in canon.items():
            if v == c:
                cuenta.update(literal_por_clave[k])
        mejor = max(cuenta.items(), key=lambda kv: (kv[1], kv[0] != kv[0].upper(), kv[0][:1].isupper()))[0]
        # Se muestra sin dosis ni vía: "Etanercept 50 mg" es etanercept. El literal queda en el hecho.
        mejor = re.sub(r"\s+\d+(\.\d+)?\s*(mg|mcg|ug|g|iu|ui|ml)(/m2|/kg)?\b.*$", "", mejor, flags=re.I)
        mejor = re.sub(r"-(EU|US)$|\s+(IV|SC)$", "", mejor).strip()
        return mejor[:1].upper() + mejor[1:] if mejor.islower() else mejor

    nuevos, nuevos_v = [], []
    usados = {e["id"] for e in ent}
    for c, ensayos_f in sorted(por_farmaco.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        fid = "farmaco-" + slug(c)
        while fid in usados:
            fid += "-2"
        usados.add(fid)
        nombre = nombre_visible(c)
        areas = collections.Counter(ensayos[n].get("area") for n in ensayos_f if ensayos[n].get("area"))
        patro = collections.Counter(ensayos[n].get("patrocinador") for n in ensayos_f if ensayos[n].get("patrocinador"))
        hechos = []
        for nct in sorted(ensayos_f, key=lambda n: ensayos[n]["nombre"]):
            e = ensayos[nct]
            lit = " · ".join(sorted(ensayos_f[nct]["literal"]))
            fase = next((h.get("fase") for h in e["hechos"] if h.get("fase")), None)
            partes = [TIPO_LEGIBLE[ensayos_f[nct]["tipo"]].capitalize() + " evaluado en " + e["nombre"]]
            if fase:
                partes.append(fase)
            if e.get("patrocinador"):
                partes.append("patrocina " + e["patrocinador"])
            hechos.append({
                "tipo": "ensayo_clinico",
                "hecho": ", ".join(partes) + ". La fuente escribe la intervención como “" + lit + "”.",
                "fase": fase,
                "fuente_url": "https://clinicaltrials.gov/study/" + nct,
                "fecha": FECHA,
                "confianza": "pendiente",
            })
            nuevos_v.append({"origen": e["id"], "destino": fid, "tipo": VINCULO, "texto_en_la_fuente": lit})
        n_ens = len(ensayos_f)
        otros = sorted({x for x in (alias_presentable(a) for a in alias_de[c]) if x
                        and normalizar(x) != normalizar(nombre)
                        and not any(k != c and difflib.SequenceMatcher(None, normalizar(x), k).ratio() > 0.85
                                    for k in por_farmaco)}, key=str.lower)
        # Una misma marca escrita en dos cajas cuenta una vez.
        vistos, dedup = set(), []
        for a in otros:
            if a.lower() not in vistos:
                vistos.add(a.lower())
                dedup.append(a)
        otros = dedup
        ficha = {
            "id": fid,
            "nombre": nombre,
            "tipo": "farmaco",
            "ciudad": None,
            "subtitulo": "Intervención en " + str(n_ens) + (" ensayo" if n_ens == 1 else " ensayos") +
                         " con sitio en Chile",
            "area": areas.most_common(1)[0][0] if areas else None,
            "areas": [a for a, _ in areas.most_common()],
            "patrocinadores": [p for p, _ in patro.most_common()],
            "hechos": hechos,
        }
        if otros:
            ficha["alias_en_la_fuente"] = otros[:10]
        nuevos.append(ficha)

    ent.extend(nuevos)
    vin.extend(nuevos_v)
    base["actualizado"] = FECHA
    json.dump(base, open(MUESTRA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # ------------------------------------------------ 4. artefacto de revisión
    os.makedirs(SALIDA, exist_ok=True)
    conectados = {v["origen"] for v in vin}
    aislados_antes = {e["id"] for e in ent if e["tipo"] == "ensayo_clinico"} - {
        x for v in vin if v["tipo"] != VINCULO for x in (v["origen"], v["destino"])}
    resumen = {
        "fecha": FECHA,
        "fuente": API,
        "ensayos_consultados": len(crudo),
        "farmacos_creados": len(nuevos),
        "vinculos_intervencion": len(nuevos_v),
        "farmacos_con_2_o_mas_ensayos": sum(1 for f in nuevos if len(f["hechos"]) > 1),
        "uniones_por_otherNames": len(uniones),
        "claves_excluidas": len(excluidas),
        "ensayos_sin_institucion_que_ahora_tienen_farmaco": len(aislados_antes & conectados),
        "ensayos_sin_institucion_total": len(aislados_antes),
    }
    json.dump(resumen, open(os.path.join(SALIDA, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"uniones": uniones,
               "excluidas": sorted(({"clave": k, "motivo": v["motivo"], "texto_en_la_fuente": sorted(v["literal"]),
                                     "ensayos": sorted(v["ensayos"])} for k, v in excluidas.items()),
                                   key=lambda x: (x["motivo"], x["clave"]))},
              open(os.path.join(SALIDA, "decisiones.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
