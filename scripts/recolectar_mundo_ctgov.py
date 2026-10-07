#!/usr/bin/env python3
"""Publica conteos mundiales y fragmentos de sedes sin datos de investigadores.

Sin argumentos actualiza solo el índice. Para guardar detalle de países concretos:
python3 scripts/recolectar_mundo_ctgov.py --paises FR,DE,BR --max-paginas 1
La API devuelve hasta 100 estudios por página; repetir con más páginas amplía
el detalle sin cambiar los conteos oficiales. Nunca guarda la respuesta cruda.
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import areas
import paises

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "publicado" / "mundo"
STATS = "https://clinicaltrials.gov/api/v2/stats/field/values?fields=LocationCountry"
API = "https://clinicaltrials.gov/api/v2/studies"
EARTH = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
ALIASES = {
    "United States": "US", "Turkey (Türkiye)": "TR", "Hong Kong": "HK", "Norway": "NO",
    "Singapore": "SG", "North Korea": "KP", "The Bahamas": "BS",
    "Martinique": "MQ", "Reunion": "RE", "Côte d’Ivoire": "CI", "Guadeloupe": "GP",
    "Monaco": "MC", "The Gambia": "GM", "Palestinian Territories": "PS", "Bahrain": "BH",
    "Malta": "MT", "Mauritius": "MU", "French Guiana": "GF", "Burma": "MM", "Guam": "GU",
    "Antigua and Barbuda": "AG", "Macau": "MO", "Barbados": "BB", "Liechtenstein": "LI",
    "Andorra": "AD", "American Samoa": "AS", "Faroe Islands": "FO", "French Polynesia": "PF",
    "Mayotte": "YT", "Grenada": "GD", "Jersey": "JE", "Saint Kitts and Nevis": "KN",
    "Comoros": "KM", "Niue": "NU", "Holy See": "VA", "Northern Mariana Islands": "MP",
    "Saint Lucia": "LC", "Samoa": "WS", "San Marino": "SM", "Bermuda": "BM",
    "Cayman Islands": "KY", "Dominica": "DM", "Saint Vincent and the Grenadines": "VC",
    "United States Minor Outlying Islands": "UM", "Aland Islands": "AX", "Anguilla": "AI",
    "Aruba": "AW", "Bonaire, Saint Eustatius and Saba ": "BQ", "Cabo Verde": "CV",
    "Christmas Island": "CX", "Curacao": "CW", "Gibraltar": "GI", "Kiribati": "KI",
    "Maldives": "MV", "Micronesia": "FM", "Montserrat": "MS", "Saint Martin": "MF",
    "Seychelles": "SC",
}
MARKERS = (
    "hospital", "medical center", "medical centre", "university",
    "institute", "research", "cancer center", "cancer centre", "health system",
    "healthcare", "health care", "medical group", "health center", "health centre",
    "foundation", "trust", "hospice", "polyclinic", "dispensary",
    "universitätsklinikum", "krankenhaus", "klinik", "klinikum",
    "centre hospitalier", "centro medico", "centro médico", "hospital universitario",
    "hospital universitário", "instituto", "centro hospitalar",
)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "KOL-Radar/1.0 (public trial map)",
                                                   "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def clean(value):
    return re.sub(r"\s+", " ", value).strip() if isinstance(value, str) else None


# Honoríficos y práctica privada son señales explícitas. No se infiere identidad
# de un apellido sin título (p. ej. Mayo Clinic); ese caso requiere revisión.
HONORIFIC = r"(?:^|[^a-z])(?:drs?|dra|dras|doctor|doctora|docteur|doctores|prof|professor|professeur|dott|dottore|doctoresse)(?:[.]|\b)"
PRIVATE_PRACTICE = r"\b(?:private healthcare|private practice|private office|consultorio|cabinet|praxis)\b|['’]s\s+(?:clinic|practice|office)\b"
STRONG_INSTITUTION = r"\b(?:hospital|hospitals|hospitalario|hospitalier|h[oô]pital|university|universidad|universidade|universit[aä]t|universitas|krankenhaus|klinikum|spitalul|ospedale|foundation|fundaci[oó]n|funda[cç][aã]o|institute|instituto|medical cent(?:er|re)|centro m[eé]dico)\b"
EMAIL = r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+"
PHONE_LABEL = r"\b(?:tel(?:ephone|efono|éfono)?|phone|fax|mobile|m[oó]vil|whatsapp)(?:\s*/\s*(?:tel|fax))?\s*[:.]?\s*\+?\d[\d ()./-]{5,}\d(?:\s*(?:ext[.]?|x)\s*\d+)?"
PHONE = r"\+?\d[\d ()./-]{5,}\d(?:\s*(?:ext[.]?|x)\s*\d+)?"
PERSON_SUFFIX = r"[,;|/_]\s*(?=(?:drs?|dra|doctor|doctora|docteur|prof|dott)[.\s])|\s+-\s+(?=(?:drs?|dra|doctor|doctora|docteur|prof|dott)[.\s])"


def institution_label_allowed(value):
    """Reconoce texto institucional; no constituye verificación de identidad."""
    value = (clean(value) or "").lower()
    if not value or "investigative site" in value or value in ("research site", "study site"):
        return False
    return any(marker in value for marker in MARKERS)


def sanitize_facility(value, persons_allowed=False):
    """Quita contactos; omite nombres médicos en países no aprobados.

    Conserva epónimos con marcador institucional fuerte. Un honorífico en una
    clínica privada no queda autorizado por contener «clinic» o «research».
    El original nunca se devuelve ni se guarda como nota de redacción.
    """
    original = clean(value)
    if not original:
        return {"facility_text": None, "site_text_redacted": False}
    text = re.sub(EMAIL, "", original, flags=re.I)
    text = re.sub(PHONE_LABEL, "", text, flags=re.I)
    # Sin etiqueta, exige al menos diez dígitos; evita borrar códigos de sede.
    text = re.sub(PHONE, lambda m: "" if len(re.findall(r"\d", m.group())) >= 10 else m.group(), text)
    text = re.sub(r"\b(?:e-?mail|correo(?: electr[oó]nico)?)\s*:?\s*(?=$|[,;|])", "", text, flags=re.I)
    text = re.sub(r"\(\s*\)", "", text)
    text = (clean(text) or "").strip(" ,;|/-") if text != original else original
    if not persons_allowed:
        # «Hospital X, Dr. Y» conserva Hospital X; «Hospital Dr. X» es epónimo.
        parts = re.split(PERSON_SUFFIX, text, maxsplit=1, flags=re.I)
        if (len(parts) > 1 and institution_label_allowed(parts[0]) and
                not re.search(STRONG_INSTITUTION, parts[1], re.I) and
                not (re.search(STRONG_INSTITUTION, parts[0], re.I) and " - " in text)):
            text = parts[0].strip(" ,;|/-_")
        strong = bool(re.search(STRONG_INSTITUTION, text, re.I))
        personal = bool(re.search(HONORIFIC, text, re.I) or
                        (re.search(PRIVATE_PRACTICE, text, re.I) and
                         not re.search(r"^st[.]?\s+", text, re.I)) or
                        re.search(r"\b(?:m[.]?d[.]?|ph[.]?d[.]?)\s*$", text, re.I))
        if not institution_label_allowed(text) or (personal and not strong):
            text = ""
    return {"facility_text": text or None,
            "site_text_redacted": text != original}


def discover():
    """Une el facet oficial con ISO2 usando nombres exactos y alias explícitos."""
    geo = fetch(EARTH)
    by_name = defaultdict(set)
    for feature in geo["features"]:
        prop = feature["properties"]
        iso = prop.get("ISO_A2_EH") or prop.get("ISO_A2")
        if not re.fullmatch(r"[A-Z]{2}", iso or ""):
            continue
        for field in ("ADMIN", "NAME", "FORMAL_EN"):
            label = prop.get(field)
            if label:
                by_name[label.casefold()].add(iso)
    map_names = {p["iso2"]: p["nombre"] for p in
                 json.loads((ROOT / "data/geo/mundo-paises.json").read_text(encoding="utf-8"))["paises"]}
    config = paises.configuracion()
    map_names.update({iso: row["nombre"] for iso, row in config.items()})
    aliases = {k.casefold(): v for k, v in ALIASES.items()}
    facet = fetch(STATS)
    values = next(x["topValues"] for x in facet if x.get("piece") == "LocationCountry")
    mapped, unmapped = [], []
    for item in values:
        label = item["value"]
        codes = by_name.get(label.casefold(), set())
        iso = aliases.get(label.casefold()) or (next(iter(codes)) if len(codes) == 1 else None)
        entry = {"etiqueta_ctgov": label, "ensayos": int(item["studiesCount"])}
        if not iso:
            unmapped.append(entry)
            continue
        entry["iso2"] = iso
        mapped.append(entry)
    return mapped, unmapped, map_names


def atomic_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n",
                    encoding="utf-8")
    temp.replace(path)


def publish_index(mapped, unmapped, names):
    today = dt.date.today().isoformat()
    atomic_json(DEST / "cobertura.json", {
        "actualizado": today,
        "fuente_ctgov": STATS,
        "fuente_geografia": EARTH,
        "metodo": "Nombre administrativo exacto, sin distinguir mayúsculas, o alias literal declarado. Los nombres ambiguos quedan sin ISO2.",
        "etiquetas_mapeadas": mapped,
        "etiquetas_sin_codigo_iso2": unmapped,
    })
    by_iso = defaultdict(list)
    for item in mapped:
        by_iso[item["iso2"]].append(item)
    rows = []
    for iso, labels in by_iso.items():
        total = sum(x["ensayos"] for x in labels)
        path = DEST / (iso + ".json")
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            records = data.get("registros", [])
            trials = {r["nct_id"] for r in records}
            centers = {(r["facility_text"], r.get("city"), r.get("state"))
                       for r in records if r.get("facility_text")}
            state = "completo" if data.get("recoleccion_completa") and len(trials) == total else "parcial"
        else:
            trials, centers, state = set(), set(), "resumen"
        rows.append({"iso2": iso, "nombre": names.get(iso, labels[0]["etiqueta_ctgov"]),
                     "nombre_ctgov": labels[0]["etiqueta_ctgov"], "ensayos": total,
                     "ensayos_fuente": total, "ensayos_detalle": len(trials),
                     "centros": len(centers), "ruta": "../data/publicado/mundo/" + iso + ".json",
                     "estado": state})
    rows.sort(key=lambda x: (-x["ensayos"], x["iso2"]))
    atomic_json(DEST / "indice.json", {"actualizado": today, "paises": rows})
    return by_iso


def site_rows(study, iso, label, today):
    ps = study.get("protocolSection") or {}
    ident = ps.get("identificationModule") or {}
    nct = clean(ident.get("nctId"))
    if not nct or not re.fullmatch(r"NCT\d{8}", nct):
        return []
    conditions = [clean(x) for x in ((ps.get("conditionsModule") or {}).get("conditions") or [])]
    conditions = list(dict.fromkeys(x for x in conditions if x))
    area_ids = sorted({area["id"] for area, _ in areas.desde_condiciones(conditions)})
    title = clean(ident.get("briefTitle")) or clean(ident.get("officialTitle"))
    status = clean((ps.get("statusModule") or {}).get("overallStatus"))
    out = []
    for loc in (ps.get("contactsLocationsModule") or {}).get("locations") or []:
        if clean(loc.get("country")) != clean(label):
            continue
        safe_site = sanitize_facility(loc.get("facility"), iso == "CL")
        out.append({"country_iso2": iso, "country_name": label, "area_ids": area_ids,
                    **safe_site,
                    "city": clean(loc.get("city")), "state": clean(loc.get("state")),
                    "nct_id": nct, "title": title, "conditions": conditions,
                    "status": status, "source_url": "https://clinicaltrials.gov/study/" + nct,
                    "source_date": today, "confidence": "pendiente", "review_status": "pending"})
    return out


def collect(iso, labels, max_pages):
    if len(labels) != 1:
        print(iso, "tiene múltiples etiquetas; se deja en resumen", file=sys.stderr)
        return
    label = labels[0]["etiqueta_ctgov"]
    total = labels[0]["ensayos"]
    token = None
    records = []
    seen = set()
    complete = False
    today = dt.date.today().isoformat()
    for page in range(max_pages):
        params = {"format": "json", "pageSize": 100,
                  "filter.advanced": "AREA[LocationCountry]" + label}
        if token:
            params["pageToken"] = token
        result = fetch(API + "?" + urllib.parse.urlencode(params))
        for study in result.get("studies", []):
            for row in site_rows(study, iso, label, today):
                key = (row["nct_id"], row["facility_text"], row["city"], row["state"])
                if key not in seen:
                    seen.add(key)
                    records.append(row)
        token = result.get("nextPageToken")
        if not token:
            complete = True
            break
    atomic_json(DEST / (iso + ".json"), {"pais": iso, "registros": records,
                                            "recoleccion_completa": complete,
                                            "paginas_consultadas": page + 1})
    print(iso, "ensayos", len({r["nct_id"] for r in records}), "de", total,
          "sedes", len(records), "completo" if complete else "parcial", flush=True)


def sanitize_published():
    """Migra archivos locales sin red ni eliminación de ensayos o ubicaciones."""
    changed_files = changed_rows = 0
    for path in sorted(DEST.glob("[A-Z][A-Z].json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for row in data.get("registros", []):
            safe = sanitize_facility(row.get("facility_text"), row["country_iso2"] == "CL")
            if safe["facility_text"] != row.get("facility_text"):
                row.update(safe)
                changed = True
                changed_rows += 1
        if changed:
            atomic_json(path, data)
            changed_files += 1
    index_path = DEST / "indice.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for country in index["paises"]:
        path = DEST / (country["iso2"] + ".json")
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8")).get("registros", [])
        country["centros"] = len({(r["facility_text"], r.get("city"), r.get("state"))
                                 for r in rows if r.get("facility_text")})
    atomic_json(index_path, index)
    print("Saneamiento local: %d registros en %d archivos; ensayos, ubicación y fuente conservados." %
          (changed_rows, changed_files))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sanear-publicado", action="store_true", help="sanea los fragmentos locales y recuenta sedes, sin red")
    ap.add_argument("--paises", help="ISO2 separados por coma; sin este argumento solo actualiza el índice")
    ap.add_argument("--todos", action="store_true", help="carga hasta --max-paginas en todos los países del facet")
    ap.add_argument("--max-paginas", type=int, default=1, help="hasta 100 estudios por página y país")
    args = ap.parse_args()
    if args.sanear_publicado:
        if args.todos or args.paises:
            ap.error("--sanear-publicado no se combina con recolección")
        sanitize_published()
        return
    if args.todos and args.paises:
        ap.error("usá --todos o --paises, no ambos")
    if not 1 <= args.max_paginas <= 1000:
        ap.error("--max-paginas debe estar entre 1 y 1000")
    mapped, unmapped, names = discover()
    by_iso = publish_index(mapped, unmapped, names)
    if not args.paises and not args.todos:
        print(len(by_iso), "países/territorios con conteo oficial;", len(unmapped),
              "etiquetas sin ISO2", flush=True)
        return
    requested = list(by_iso) if args.todos else [x.strip().upper() for x in args.paises.split(",") if x.strip()]
    unknown = sorted(set(requested) - set(by_iso))
    if unknown:
        ap.error("ISO2 sin etiqueta en el facet: " + ",".join(unknown))
    for iso in requested:
        if args.todos and (DEST / (iso + ".json")).exists():
            continue
        try:
            collect(iso, by_iso[iso], args.max_paginas)
        except Exception as error:
            print(iso, "sin detalle por", type(error).__name__, str(error)[:160], file=sys.stderr, flush=True)
        publish_index(mapped, unmapped, names)


if __name__ == "__main__":
    main()
