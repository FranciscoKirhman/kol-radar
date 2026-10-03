#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma el calendario de vencimientos de patentes de los fármacos de la muestra.

Tres fuentes oficiales, que dicen cosas distintas y no se mezclan:

  EE.UU. · FDA Orange Book (dominio público). Para cada medicamento aprobado por NDA (moléculas
      pequeñas), las patentes que el titular declaró y las exclusividades regulatorias, cada una
      con su fecha de vencimiento. Se liga por el principio activo (sin la sal: "OSIMERTINIB
      MESYLATE" → osimertinib), por producto: el paclitaxel genérico no tiene protección, pero
      ABRAXANE (paclitaxel unido a albúmina) sí, y mezclarlos daría una fecha falsa.
  EE.UU. · FDA Purple Book, lista de patentes (dominio público). Para los biológicos, solo las
      patentes que el titular informó a un fabricante de biosimilares: cubre pocos productos.
  Chile · INAPI, registros de patentes 2009–hoy (datos.gob.cl, CC0). Patentes chilenas vigentes
      cuyo TÍTULO nombra el fármaco. Es parcial a propósito: la patente del compuesto se presenta
      antes de que el fármaco tenga nombre, así que su título casi nunca lo nombra. El tipo
      (formulación, combinación, uso…) se deduce del título y así se rotula.

Lo que no se usa: Pat-INFORMED (OMPI) prohíbe las consultas automatizadas y la copia; el sitio
solo enlaza a su buscador. No se guardan inventores (personas): solo titulares.

Una patente que vence no significa que entren genéricos: puede quedar otra patente, una
exclusividad, un litigio o, en Chile, la protección de datos de prueba. La interfaz lo dice.

Uso:  python3 scripts/patentes.py [--cache DIR]
Sin --cache, descarga en ~/.cache/kol-radar/patentes (se reusa lo bajado el mismo día).
"""
import argparse
import collections
import csv
import datetime
import html
import io
import json
import os
import re
import sys
import unicodedata
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
SALIDA = os.path.join(RAIZ, "data", "patentes", "vencimientos.json")
HOY = datetime.date.today()
AGENTE = "kol-radar/1.0 (+https://franciscokirhman.github.io/kol-radar/)"

OB_PAGINA = "https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files"
OB_ZIP = "https://www.fda.gov/media/76860/download?attachment"
OB_PRODUCTO = "https://www.accessdata.fda.gov/scripts/cder/ob/patent_info.cfm?Product_No=%s&Appl_No=%s&Appl_type=N"
PB_PATENTES = "https://purplebooksearch.fda.gov/patent-list"
PB_DESCARGAS = "https://purplebooksearch.fda.gov/downloads"
MESES_EN = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
INAPI_PAQUETE = "https://datos.gob.cl/api/3/action/package_show?id=registros-de-patentes"
INAPI_FICHA = "https://datos.gob.cl/dataset/registros-de-patentes"

# Sales, hidratos y contraiones que el Orange Book agrega al principio activo.
SALES = (r"\b(MESYLATE|MESILATE|DIMESYLATE|HYDROCHLORIDE|DIHYDROCHLORIDE|MALEATE|TOSYLATE|DITOSYLATE|"
         r"SODIUM|POTASSIUM|CITRATE|ACETATE|PHOSPHATE|SULFATE|BESYLATE|FUMARATE|SUCCINATE|TARTRATE|"
         r"BITARTRATE|HYDROBROMIDE|MONOHYDRATE|HYDRATE|ANHYDROUS|CALCIUM|MAGNESIUM|S-MALATE|L-MALATE|"
         r"MALATE|ESYLATE|CAMSYLATE|LACTATE|TRIHYDRATE|HEMIHYDRATE|SESQUIHYDRATE|DISODIUM|MEGLUMINE|"
         r"TROMETHAMINE|CHLORIDE|DIMETHYL SULFOXIDE|HEMIFUMARATE|ETHANOLATE|SOLVATE|BENZOATE)\b")

# Significado de los códigos de exclusividad del Orange Book (los de prefijo llevan número).
EXCLUSIVIDAD = [
    ("NCE", "Nueva entidad química", "5 años desde la aprobación; mientras dure, la FDA no recibe solicitudes de genéricos"),
    ("ODE", "Medicamento huérfano", "7 años, solo para la indicación huérfana"),
    ("PED", "Extensión pediátrica", "6 meses que se suman a las otras protecciones"),
    ("I-", "Nueva indicación", "3 años, solo para esa indicación"),
    ("NP", "Nuevo producto", "3 años"),
    ("D-", "Nueva dosis o esquema", "3 años"),
    ("M-", "Otra exclusividad", "3 años"),
    ("NPP", "Nueva población de pacientes", "3 años"),
    ("NDF", "Nueva forma farmacéutica", "3 años"),
    ("NR", "Nueva vía de administración", "3 años"),
    ("NS", "Nueva concentración", "3 años"),
    ("NC", "Nueva combinación", "3 años"),
    ("GAIN", "Antibiótico calificado (GAIN)", "5 años adicionales"),
]

# Nombres de la muestra que no son un fármaco con nombre propio: en un título describen una clase.
NO_BUSCAR_EN_TITULOS = {"taxane", "bcg", "n-acetylcysteine", "peg-asparaginase"}

# Tipo de patente chilena según su título, en este orden: la combinación primero, porque una
# patente de "X en combinación con cisplatino" no protege el cisplatino.
TIPO_TITULO = [
    ("combinacion", r"COMBINACI[OÓ]N|EN COMBINACI|ASOCIACI[OÓ]N|JUNTO CON|CO-ADMINISTRA|COADMINISTRA"),
    ("proceso", r"^(PROCESO|PROCEDIMIENTO|M[EÉ]TODO PARA (PREPARAR|PRODUCIR|OBTENER|LA PREPARACI|LA S[IÍ]NTESIS|FABRICAR))"),
    ("forma_solida", r"CRISTAL|POLIMORF|^SALES? |^FORMAS? |SOLVATO|AMORF|CO-CRISTAL"),
    ("formulacion", r"^(COMPOSICI|FORMULACI|FORMA FARMAC|FORMA DE DOSIFICACI|COMPRIMIDO|TABLETA|C[AÁ]PSULA|"
                    r"SOLUCI[OÓ]N|SUSPENSI[OÓ]N|EMULSI[OÓ]N|LIOFILIZ|POLVO|PREPARACI[OÓ]N FARMAC|NANOPART|PARCHE|IMPLANTE)"),
    ("uso", r"^(USO|EMPLEO|M[EÉ]TODO PARA (TRATAR|EL TRATAMIENTO)|M[EÉ]TODO DE TRATAMIENTO)"),
    ("compuesto", r"^(COMPUESTO|DERIVADO|ANTICUERPO|PROTE[IÍ]NA|P[EÉ]PTIDO|MOL[EÉ]CULA)"),
]


# ---------------------------------------------------------------- descargas
def bajar(url, destino):
    if os.path.exists(destino) and datetime.date.fromtimestamp(os.path.getmtime(destino)) == HOY:
        return destino
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=180) as r, open(destino + ".tmp", "wb") as f:
        f.write(r.read())
    os.replace(destino + ".tmp", destino)
    return destino


def leer_xlsx(ruta):
    """Filas de la primera hoja de un .xlsx como dicts por encabezado. Solo biblioteca estándar."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    z = zipfile.ZipFile(ruta)
    comunes = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(ns + "si"):
            comunes.append("".join(t.text or "" for t in si.iter(ns + "t")))
    encabezado = None
    for fila in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(ns + "row"):
        celdas = {}
        for c in fila.iter(ns + "c"):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v = c.find(ns + "v")
            if c.get("t") == "s" and v is not None:
                celdas[col] = comunes[int(v.text)]
            elif c.get("t") == "inlineStr":
                celdas[col] = "".join(t.text or "" for t in c.iter(ns + "t"))
            else:
                celdas[col] = v.text if v is not None else None
        if encabezado is None:
            encabezado = celdas
        else:
            yield {encabezado[k]: v for k, v in celdas.items() if k in encabezado}


def fecha_excel(x):
    try:
        return datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(x)))
    except (TypeError, ValueError):
        return None


def fecha_texto(s):
    for formato in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.datetime.strptime(s.strip(), formato).date()
        except ValueError:
            pass
    return None


def sin_acentos(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def base_ingrediente(s):
    return re.sub(r"\s+", " ", re.sub(SALES, "", s.upper())).strip()


# ---------------------------------------------------------------- Orange Book
def orange_book(cache, farmacos):
    z = zipfile.ZipFile(bajar(OB_ZIP, os.path.join(cache, "orange-book.zip")))
    def tabla(nombre):
        filas = list(csv.reader(io.TextIOWrapper(z.open(nombre), encoding="latin-1"), delimiter="~"))
        return [dict(zip(filas[0], f)) for f in filas[1:] if len(f) == len(filas[0])]
    productos, patentes, exclus = tabla("products.txt"), tabla("patent.txt"), tabla("exclusivity.txt")
    version = max(datetime.date(*z.getinfo(n).date_time[:3]) for n in ("products.txt", "patent.txt", "exclusivity.txt"))

    # Aplicación NDA → sus productos vigentes (Rx) y sus principios activos.
    apl = {}
    for p in productos:
        if p["Appl_Type"] != "N" or p["Type"] != "RX":
            continue
        a = apl.setdefault(p["Appl_No"], {"marcas": set(), "titular": p["Applicant_Full_Name"].strip(),
                                          "ingredientes": set(), "productos": set(), "aprobada": None})
        a["marcas"].add(p["Trade_Name"].strip())
        a["productos"].add(p["Product_No"])
        for ing in p["Ingredient"].split(";"):
            a["ingredientes"].add(base_ingrediente(ing))
        d = fecha_texto(p["Approval_Date"]) if p["Approval_Date"][:1].isalpha() and "Approved Prior" not in p["Approval_Date"] else None
        if d and (a["aprobada"] is None or d < a["aprobada"]):
            a["aprobada"] = d
    por_ingrediente = collections.defaultdict(set)
    for num, a in apl.items():
        for ing in a["ingredientes"]:
            por_ingrediente[ing].add(num)
    # Genéricos (ANDA) vigentes de un solo principio activo: cuántas solicitudes y la primera aprobación.
    genericos = collections.defaultdict(dict)
    for p in productos:
        if p["Appl_Type"] == "A" and p["Type"] == "RX" and ";" not in p["Ingredient"]:
            d = fecha_texto(p["Approval_Date"]) if p["Approval_Date"][:1].isalpha() and "Approved Prior" not in p["Approval_Date"] else None
            g = genericos[base_ingrediente(p["Ingredient"])]
            if p["Appl_No"] not in g or (d and (g[p["Appl_No"]] is None or d < g[p["Appl_No"]])):
                g[p["Appl_No"]] = d

    pat_por, exc_por = collections.defaultdict(list), collections.defaultdict(list)
    for r in patentes:
        if r["Appl_Type"] == "N" and r["Delist_Flag"] != "Y":
            pat_por[r["Appl_No"]].append(r)
    for r in exclus:
        if r["Appl_Type"] == "N":
            exc_por[r["Appl_No"]].append(r)

    salida, compet = {}, {}
    for f in farmacos:
        nombres = {base_ingrediente(x) for x in [f["nombre"]] + list(f.get("alias_en_la_fuente") or [])}
        nums = sorted(set().union(*[por_ingrediente.get(n, set()) for n in nombres]))
        productos_f = []
        for num in nums:
            a = apl[num]
            pats = {}
            for r in pat_por[num]:
                numero = r["Patent_No"].replace("*PED", "")
                vence = fecha_texto(r["Patent_Expire_Date_Text"])
                if not vence:
                    continue
                p = pats.setdefault(numero, {"numero": numero, "vence": vence, "sustancia": False, "formulacion": False,
                                             "usos": set(), "pediatrica": False, "producto": r["Product_No"]})
                if r["Patent_No"].endswith("*PED"):
                    p["pediatrica"] = True
                p["vence"] = max(p["vence"], vence)
                p["sustancia"] |= r["Drug_Substance_Flag"] == "Y"
                p["formulacion"] |= r["Drug_Product_Flag"] == "Y"
                if r["Patent_Use_Code"]:
                    p["usos"].add(r["Patent_Use_Code"])
            excs = {}
            for r in exc_por[num]:
                vence = fecha_texto(r["Exclusivity_Date"])
                if vence:
                    excs[r["Exclusivity_Code"]] = max(excs.get(r["Exclusivity_Code"], vence), vence)
            if not pats and not excs:
                continue
            producto_fuente = (sorted(p["producto"] for p in pats.values()) or sorted(a["productos"]))[0]
            productos_f.append({
                "aplicacion": "NDA " + num,
                "marcas": sorted(a["marcas"]),
                "titular": a["titular"],
                "aprobada": a["aprobada"].isoformat() if a["aprobada"] else None,
                "combinacion": sorted(i.lower() for i in a["ingredientes"]) if len(a["ingredientes"]) > 1 else None,
                "fuente_url": OB_PRODUCTO % (producto_fuente, num),
                "patentes": sorted(({
                    "numero": p["numero"], "vence": p["vence"].isoformat(),
                    "tipo": "sustancia" if p["sustancia"] and not p["formulacion"] else
                            "sustancia_formulacion" if p["sustancia"] else
                            "formulacion" if p["formulacion"] else "uso" if p["usos"] else "otra",
                    "usos": sorted(p["usos"]) or None, "pediatrica": p["pediatrica"] or None,
                } for p in pats.values()), key=lambda p: (p["vence"], p["numero"])),
                "exclusividades": sorted(({"codigo": c, "vence": d.isoformat()} for c, d in excs.items()),
                                         key=lambda e: (e["vence"], e["codigo"])),
            })
        gen = {}
        for n in nombres:
            gen.update(genericos.get(n, {}))
        if gen:
            fechas = sorted(d for d in gen.values() if d)
            compet[f["id"]] = {"genericos": len(gen), "primer_generico": fechas[0].isoformat() if fechas else None,
                               "fuente_url": OB_PAGINA}
        if productos_f:
            salida[f["id"]] = productos_f
    return salida, version, compet


# ---------------------------------------------------------------- Purple Book
def purple_book(cache, farmacos):
    pagina = open(bajar(PB_PATENTES, os.path.join(cache, "purple-book-patentes.html")), encoding="utf-8", errors="replace").read()
    por_nombre = collections.defaultdict(list)
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, flags=re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
        if len(tds) >= 6:
            por_nombre[re.sub(r"[^a-z]", "", tds[3].lower())].append(tds)
    salida = {}
    for f in farmacos:
        filas = por_nombre.get(re.sub(r"[^a-z]", "", re.sub(r"-[a-z]{4}\b", "", f["nombre"].lower())))
        if not filas:
            continue
        por_bla = collections.OrderedDict()
        for bla, titular, marca, _, numero, vence in (t[:6] for t in filas):
            d = fecha_texto(vence)
            b = por_bla.setdefault(bla, {"aplicacion": "BLA " + bla, "marcas": [marca], "titular": titular,
                                         "fuente_url": PB_PATENTES, "patentes": [], "exclusividades": []})
            if d:  # "Disclaimer filed on …": el titular renunció a esa patente
                b["patentes"].append({"numero": numero.replace(",", ""), "vence": d.isoformat(), "tipo": "biologico"})
        for b in por_bla.values():
            b["patentes"].sort(key=lambda p: (p["vence"], p["numero"]))
        salida[f["id"]] = [b for b in por_bla.values() if b["patentes"]]
    return salida


def biosimilares(cache, farmacos):
    """Biosimilares e intercambiables (351(k)) aprobados en EE.UU., por producto de referencia,
    desde la descarga mensual más reciente del Purple Book."""
    pagina = open(bajar(PB_DESCARGAS, os.path.join(cache, "purple-book-descargas.html")), encoding="utf-8", errors="replace").read()
    enlaces = re.findall(r'href="(https://[^"]*/PurpleBook/(\d{4})/purplebook-search-([A-Za-z]+)-data-download\.csv)"', pagina)
    url = max(enlaces, key=lambda e: (int(e[1]), MESES_EN.index(e[2].lower()) if e[2].lower() in MESES_EN else -1))[0]
    filas = list(csv.reader(io.open(bajar(url, os.path.join(cache, "purple-book.csv")), encoding="utf-8", errors="replace")))
    inicio = max(i for i, r in enumerate(filas) if r and r[0] == "N/R/U")
    cab = filas[inicio]
    por_ref = collections.defaultdict(dict)
    for r in filas[inicio + 1:]:
        d = dict(zip(cab, r))
        if not d.get("License Type", "").startswith("351(k)"):
            continue
        ref = re.sub(r"[^a-z]", "", re.sub(r"-[a-z]{4}\b", "", d.get("Ref. Product Proper Name", "").lower()))
        marca = d.get("Proprietary Name", "").strip()
        try:
            aprobado = datetime.datetime.strptime(d.get("Approval Date", "").strip(), "%d-%b-%y").date()
        except ValueError:
            aprobado = None
        b = por_ref[ref].setdefault(marca, {"marca": marca, "titular": d.get("Applicant", "").strip(), "aprobado": aprobado,
                                            "intercambiable": "Interchangeable" in d.get("License Type", "")})
        if aprobado and (b["aprobado"] is None or aprobado < b["aprobado"]):
            b["aprobado"] = aprobado
        b["intercambiable"] |= "Interchangeable" in d.get("License Type", "")
    salida = {}
    for f in farmacos:
        lista = por_ref.get(re.sub(r"[^a-z]", "", re.sub(r"-[a-z]{4}\b", "", f["nombre"].lower())))
        if lista:
            salida[f["id"]] = {"biosimilares": sorted(({**b, "aprobado": b["aprobado"].isoformat() if b["aprobado"] else None}
                                                       for b in lista.values()), key=lambda b: (b["aprobado"] or "9999", b["marca"])),
                               "fuente_url": PB_DESCARGAS}
    return salida


# ---------------------------------------------------------------- INAPI
def variantes_es(nombre):
    """Formas en que un título en español puede escribir una DCI: enzalutamide → enzalutamida."""
    n = sin_acentos(nombre).lower().strip()
    vs = {n}
    for a, b in ((r"ide$", "ida"), (r"ine$", "ina"), (r"one$", "ona"), (r"ate$", "ato"), (r"ane$", "ano"),
                 (r"ene$", "eno"), (r"ole$", "ol"), (r"in$", "ina"), (r"in$", "ino"), (r"ib$", "ib"),
                 (r"ph", "f"), (r"th", "t"), (r"y", "i"), (r"rubicin", "rrubicin"), (r"mycin", "micin")):
        vs |= {re.sub(a, b, v) for v in list(vs)}
    return {v for v in vs if len(v) >= 7}


def tipo_por_titulo(titulo):
    t = re.sub(r"^(UN|UNA|UNOS|UNAS|EL|LA|LOS|LAS)\s+", "", sin_acentos(titulo).upper().strip())
    for tipo, patron in TIPO_TITULO:
        if re.search(sin_acentos(patron), t):
            return tipo
    return "otra"


# INAPI escribe a las personas naturales como "APELLIDO APELLIDO, Nombre Nombre"; a las empresas, en
# mayúsculas y a menudo con una sola palabra ("SANOFI"). Una persona natural no se publica.
PERSONA = re.compile(r"^[A-ZÁÉÍÓÚÑÜ' .-]+, [A-ZÁÉÍÓÚÑ][a-záéíóúñü]+")
ORGANIZACION = re.compile(r"\b(INC|LTD|LIMITED|LLC|CORP\w*|COMPANY|GMBH|AG|PLC|S\.?A|S\.?P\.?A|B\.?V|N\.?V|"
                          r"UNIVERSI\w*|FOUNDATION|FUNDACI\w*|INSTITUT\w*|LABORATO\w*|PHARMA\w*)\b", re.I)


def titulares(texto):
    """Lista de titulares; las personas naturales quedan como None (el sitio dice "persona natural")."""
    salida = []
    for t in re.split(r"\.BR\.|;", texto or ""):
        t = re.sub(r"\(\w\w\)\s*", "", t).strip(" .;")
        if t:
            salida.append(None if PERSONA.match(t) and not ORGANIZACION.search(t) else t)
    return salida


def es_principal(titulo, variantes, tipo, otras):
    """¿El título trata de ESTE fármaco, o lo menciona al pasar? Principal: no es una combinación,
    lo nombra entre sus primeras 20 palabras y no nombra antes a otro fármaco de la muestra."""
    if tipo == "combinacion":
        return False
    palabras = re.sub(r"[^a-z0-9]+", " ", sin_acentos(titulo).lower()).split()
    pos = next((i for i, w in enumerate(palabras) if w in variantes), None)
    if pos is None or pos > 20:
        return False
    # "2'-desoxi-5-azacitidina" es la decitabina; "uso de un inhibidor de mdm2 y citarabina", otro fármaco.
    if set(palabras[max(0, pos - 2):pos]) & {"desoxi", "deoxi", "dihidro", "analogo", "analogos", "derivado", "derivados"}:
        return False
    if palabras[:1] == ["uso"] and pos > 6:
        return False
    return not any(w in otras for w in palabras[:pos])


def inapi(cache, farmacos):
    paquete = json.load(urllib.request.urlopen(urllib.request.Request(INAPI_PAQUETE, headers={"User-Agent": AGENTE}), timeout=60))
    registros = []
    for r in paquete["result"]["resources"]:
        ruta = bajar(r["url"], os.path.join(cache, r["name"]))
        for fila in leer_xlsx(ruta):
            fila["_fuente"] = r["url"]
            registros.append(fila)
    vigentes = [r for r in registros if r.get("Status") == "Registrada" and (fecha_excel(r.get("ExpirationDate")) or HOY) >= HOY
                and re.search(r"A61K|A61P|C07|C12N|C12P", r.get("IPC") or "")]
    titulos = [(" " + re.sub(r"[^a-z0-9]+", " ", sin_acentos(r.get("Title") or "").lower()) + " ", r) for r in vigentes]
    variantes = {f["id"]: variantes_es(f["nombre"]) for f in farmacos if f["nombre"].lower() not in NO_BUSCAR_EN_TITULOS}
    todas = set().union(*variantes.values())
    salida = {}
    for f in farmacos:
        if f["id"] not in variantes:
            continue
        vs = variantes[f["id"]]
        encontradas = []
        for t, r in titulos:
            if any(" " + v + " " in t for v in vs):
                tipo = tipo_por_titulo(r.get("Title") or "")
                encontradas.append({
                    "solicitud": r.get("ApplicationNumber"),
                    "registro": r.get("RegistrationNumber"),
                    "titulo": (r.get("Title") or "").strip(),
                    "titulares": titulares(r.get("Applicants")),
                    "presentada": (fecha_excel(r.get("FilingDate")) or HOY).isoformat(),
                    "vence": fecha_excel(r.get("ExpirationDate")).isoformat(),
                    "tipo": tipo,
                    "principal": es_principal(r.get("Title") or "", vs, tipo, todas - vs),
                    "fuente_url": r["_fuente"],
                })
        if encontradas:
            salida[f["id"]] = sorted(encontradas, key=lambda p: (p["vence"], p["solicitud"] or ""))
    version = max((r.get("last_modified") or r.get("created") or "")[:10] for r in paquete["result"]["resources"])
    return salida, version, len(registros), len(vigentes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/kol-radar/patentes"))
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    base = json.load(open(MUESTRA, encoding="utf-8"))
    farmacos = [e for e in base["entidades"] if e["tipo"] == "farmaco"]

    ob, ob_version, genericos = orange_book(a.cache, farmacos)
    pb = purple_book(a.cache, farmacos)
    bios = biosimilares(a.cache, farmacos)
    cl, cl_version, cl_total, cl_vigentes = inapi(a.cache, farmacos)

    por_farmaco = {}
    for fid in sorted(set(ob) | set(pb) | set(cl) | set(genericos) | set(bios)):
        d = {}
        if fid in ob or fid in pb:
            d["ee_uu"] = ob.get(fid, []) + pb.get(fid, [])
        if fid in genericos or fid in bios:
            d["ee_uu_competencia"] = {**genericos.get(fid, {}), **bios.get(fid, {})}
        if fid in cl:
            d["chile"] = cl[fid]
        por_farmaco[fid] = d

    salida = {
        "generado": HOY.isoformat(),
        "aviso": "Una patente que vence no significa que entren genéricos o biosimilares: puede quedar otra patente, "
                 "una exclusividad, un litigio o, en Chile, la protección de datos de prueba. No es asesoría legal.",
        "fuentes": {
            "orange_book": {"nombre": "FDA Orange Book — patentes y exclusividades", "url": OB_PAGINA,
                            "version": ob_version.isoformat(), "licencia": "Dominio público (gobierno de EE.UU.)"},
            "purple_book": {"nombre": "FDA Purple Book — lista de patentes de biológicos", "url": PB_PATENTES,
                            "version": HOY.isoformat(), "licencia": "Dominio público (gobierno de EE.UU.)"},
            "inapi": {"nombre": "INAPI — registros de patentes 2009 a hoy", "url": INAPI_FICHA,
                      "version": cl_version, "licencia": "CC0 (datos.gob.cl)"},
        },
        "exclusividades": [{"prefijo": p, "nombre": n, "alcance": d} for p, n, d in EXCLUSIVIDAD],
        "farmacos": por_farmaco,
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")

    proximos = []
    for fid, d in por_farmaco.items():
        for p in d.get("ee_uu", []):
            fechas = [x["vence"] for x in p["patentes"] + p["exclusividades"]]
            if max(fechas) >= HOY.isoformat():
                proximos.append((max(fechas), fid, p["marcas"][0]))
    print(json.dumps({
        "farmacos_en_la_muestra": len(farmacos),
        "con_patentes_o_exclusividades_ee_uu": sum(1 for d in por_farmaco.values() if "ee_uu" in d),
        "con_patentes_chilenas_que_los_nombran": len(cl),
        "registros_inapi_leidos": cl_total, "registros_inapi_farmaceuticos_vigentes": cl_vigentes,
        "protecciones_ee_uu_que_terminan_en_3_anos": sorted(x for x in proximos if x[0] <= (HOY + datetime.timedelta(days=3 * 365)).isoformat()),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
