#!/usr/bin/env python3
"""
Propone la ubicación de cada institución de la muestra desde OpenStreetMap (Nominatim).

Hoy la muestra solo sabe la CIUDAD de cada institución, y ClinicalTrials.gov ubica todo en el
centroide de esa ciudad: 36 de las 40 instituciones del área de Santiago comparten un mismo
punto. Para dibujarlas sobre un mapa de la ciudad hace falta su ubicación real, y esa ubicación
tiene que venir de una fuente citable, no de lo que uno sepa de memoria.

NUNCA escribe sobre data/sample/perfiles-muestra.json. Escribe una PROPUESTA en
data/pending/geolocalizacion-osm-<fecha>/ para revisión humana, con la URL exacta del objeto de
OpenStreetMap como fuente de cada punto y confianza "pendiente".

Criterio de aceptación (acumulativo), para no aceptar la farmacia que se llama parecido:
  1. La búsqueda se acota a una caja alrededor de la ciudad declarada por la muestra.
  2. El objeto es de una categoría de salud, educación u oficina (no un helipuerto ni una calle).
  3. Coinciden las palabras DISTINTIVAS del nombre, no las genéricas. Contar "hospital",
     "clínico" y "universidad" como coincidencia llevó al Hospital Clínico de la U. de Chile a un
     hospital veterinario de otra universidad en la primera corrida.
  4. Se prueban el nombre y todos los alias de la fuente, y gana el que calza más palabras
     distintivas: "Clínica RedSalud" a secas caía en la sede Providencia; la fuente dice Vitacura.
Lo que no pasa queda en sin_ubicar.json: trabajo pendiente, no evidencia de nada.

Datos de OpenStreetMap © colaboradores de OpenStreetMap, licencia ODbL.
Política de uso de Nominatim: una consulta por segundo, User-Agent identificable.

Uso:
    python3 scripts/geolocalizar_instituciones_osm.py
"""
import datetime, json, math, os, time, unicodedata, urllib.parse, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
HOY = datetime.date.today().isoformat()
SALIDA_DIR = os.path.join(RAIZ, "data", "pending", "geolocalizacion-osm-" + HOY)
API = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "kol-radar/1.0 (+https://github.com/FranciscoKirhman/kol-radar)"

COMUNAS_RM = {"providencia", "recoleta", "las condes", "independencia", "nunoa", "vitacura", "maipu",
              "puente alto", "la florida", "macul", "huechuraba", "quilicura", "lo barnechea", "la reina",
              "san miguel", "penalolen", "estacion central"}
# Radio de búsqueda en grados alrededor del centroide de la ciudad. Santiago es un área
# metropolitana de ~40 km; el resto, ciudades de ~15 km.
RADIO = {"Santiago": 0.32}
RADIO_DEFECTO = 0.16
VACIAS = {"de", "del", "la", "las", "los", "el", "y", "en", "e", "at", "spa", "ltda", "limitada", "sa", "s"}
GENERICAS = {"hospital", "clinica", "clinico", "clinical", "centro", "universidad", "university", "instituto", "sede",
             "investigacion", "investigaciones", "research", "estudios", "sociedad", "nacional", "regional", "dr", "doctor",
             "oncologia", "oncologico", "oncology", "servicio", "complejo", "asistencial", "medicos", "medicas", "care"}
CATEGORIAS = {
    "amenity": {"hospital", "clinic", "doctors", "university", "college", "research_institute", "social_facility"},
    "healthcare": None,          # cualquier valor
    "office": None,
    "building": {"hospital", "university", "office", "commercial", "yes"},
    "landuse": {"education"},
}


def norm(s):
    s = (s or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def palabras(s):
    t = norm(s)
    for ch in "()[]-.,;/#:'\"":
        t = t.replace(ch, " ")
    return [w for w in t.split() if w and w not in VACIAS and not w.isdigit()]


def distintivas(s):
    return set(w for w in palabras(s) if w not in GENERICAS)


def coincidencia(nombre_buscado, nombre_osm):
    """(palabras distintivas en común, proporción sobre el nombre más corto).

    Sobre el más corto porque OSM suele guardar el nombre corto ("FALP") y la fuente el largo
    ("Fundación Arturo López Pérez (FALP)"), o al revés."""
    a, b = distintivas(nombre_buscado), distintivas(nombre_osm)
    if not a or not b:
        return 0, 0.0
    comun = len(a & b)
    return comun, comun / min(len(a), len(b))


def nombres_de(r):
    """Todos los nombres del objeto: el principal, el oficial, el alternativo, el antiguo.

    El Hospital Clínico Regional de Concepción se llama "Guillermo Grant Benavente" en OSM; el
    nombre que usa la fuente vive en otra etiqueta."""
    nd = r.get("namedetails") or {}
    vistos, salida = set(), []
    for n in [r.get("name")] + [v for k, v in nd.items() if k.split(":")[0] in ("name", "official_name", "alt_name", "short_name", "old_name")]:
        for parte in (n or "").split(";"):
            parte = parte.strip()
            if parte and parte not in vistos:
                vistos.add(parte); salida.append(parte)
    return salida or [r.get("display_name", "").split(",")[0]]


def categoria_aceptable(r):
    permitidos = CATEGORIAS.get(r.get("category"), False)
    return permitidos is None or (permitidos and r.get("type") in permitidos)


def tipo_coherente(inst, r):
    """1 si el tipo de objeto de OSM calza con lo que la muestra dice que es la institución.

    "Universidad de Chile" y "Hospital Clínico Universidad de Chile" comparten la única palabra
    distintiva; sin esto la universidad podía terminar ubicada en su hospital."""
    texto = norm(inst["nombre"] + " " + (inst.get("subtitulo") or ""))
    t = r.get("type")
    if "hospital" in texto or "clinica" in norm(inst["nombre"]):
        return 1 if t in ("hospital", "clinic", "doctors") or r.get("category") == "healthcare" else 0
    if "universidad" in texto:
        return 1 if t in ("university", "college") else 0
    return 1   # "Centro oncológico", "Organismo público": no hay tipo contra el cual comparar


def limpiar_alias(alias):
    # "Oncovida ( Site 1405)" y "Sociedad Oncovida /ID# 231152" son marcadores del patrocinador.
    for corte in ("( Site", "(Site", "/ID#", "/Id#"):
        if corte in alias:
            alias = alias.split(corte)[0]
    return alias.strip(" ;-")


def ciudad_base(ciudad):
    c = (ciudad or "").split(" (")[0].strip()
    if norm(c) in COMUNAS_RM:
        return "Santiago"
    return c


def km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


ultima = [0.0]


def buscar(q, centro, radio):
    espera = 1.1 - (time.time() - ultima[0])
    if espera > 0:
        time.sleep(espera)
    lat, lon = centro
    params = {
        # 20 resultados y no 5: Nominatim ordena primero el estacionamiento, el helipuerto y la
        # estación de metro que se llaman igual, y el edificio real quedaba fuera de la lista.
        "q": q, "format": "jsonv2", "limit": "20", "addressdetails": "1", "namedetails": "1", "countrycodes": "cl",
        "accept-language": "es", "bounded": "1",
        "viewbox": "%f,%f,%f,%f" % (lon - radio, lat + radio, lon + radio, lat - radio),
    }
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    finally:
        ultima[0] = time.time()


def main():
    datos = json.load(open(MUESTRA, encoding="utf-8"))
    ciudades = datos["geo"]["ciudades"]
    ubicadas, sin_ubicar = [], []
    insts = [e for e in datos["entidades"] if e["tipo"] == "institucion"]
    for n, inst in enumerate(insts, 1):
        base = ciudad_base(inst.get("ciudad"))
        # La muestra escribe "Puerto Montt"; ClinicalTrials.gov, "Port Montt".
        geo = ciudades.get(base) or ciudades.get(inst.get("ciudad") or "") or ciudades.get({"Puerto Montt": "Port Montt"}.get(base, ""))
        if not geo:
            sin_ubicar.append({"id": inst["id"], "nombre": inst["nombre"], "ciudad_en_la_muestra": inst.get("ciudad"),
                               "motivo": "la ciudad declarada no tiene coordenadas en la muestra", "consultas_probadas": []})
            continue
        centro, radio = (geo["lat"], geo["lon"]), RADIO.get(base, RADIO_DEFECTO)
        consultas = [inst["nombre"].split(" (")[0], inst["nombre"]]
        for a in inst.get("alias_en_la_fuente") or []:
            a = limpiar_alias(a)
            if a and norm(a) not in {norm(c) for c in consultas}:
                consultas.append(a)
        consultas = consultas[:6]
        candidatos, probadas, vistos = [], [], set()
        for orden, q in enumerate(consultas):
            try:
                res = buscar(q, centro, radio)
            except Exception as err:  # red caída o límite: se anota y se sigue
                probadas.append({"consulta": q, "error": str(err)})
                continue
            aceptables = 0
            for r in res:
                if not categoria_aceptable(r):
                    continue
                mejor = max(((coincidencia(q, nm), nm) for nm in nombres_de(r)), key=lambda x: x[0])
                (comun, prop), _ = mejor
                nombre_osm = r.get("name") or mejor[1]
                if comun < 1 or prop < 0.67:
                    continue
                aceptables += 1
                clave = (r["osm_type"], r["osm_id"])
                if clave in vistos:
                    continue
                vistos.add(clave)
                candidatos.append((comun, tipo_coherente(inst, r), prop, -orden, r, nombre_osm, q))
            probadas.append({"consulta": q, "resultados": len(res), "aceptables": aceptables})
        candidatos.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)
        elegido = candidatos or None
        if not elegido:
            sin_ubicar.append({"id": inst["id"], "nombre": inst["nombre"], "ciudad_en_la_muestra": inst.get("ciudad"),
                               "motivo": "ningún objeto de OSM en la ciudad con un nombre suficientemente parecido",
                               "consultas_probadas": probadas})
            print("%2d/%d  —  %s" % (n, len(insts), inst["nombre"]))
            continue
        comun, coherente, prop, _, r, nombre_osm, q = elegido[0]
        sim = prop
        lat, lon = float(r["lat"]), float(r["lon"])
        dir_ = r.get("address", {})
        # Ambiguo: otro candidato igual de bueno a más de 500 m (otra sede, otro campus).
        otras = [c for c in elegido[1:] if c[0] == comun and c[1] == coherente and c[2] >= prop
                 and km(lat, lon, float(c[4]["lat"]), float(c[4]["lon"])) > 0.5]
        ubicadas.append({
            "id": inst["id"],
            "nombre": inst["nombre"],
            "ciudad_en_la_muestra": inst.get("ciudad"),
            "consulta": q,
            "nombre_en_osm": nombre_osm,
            "similitud_nombre": round(sim, 2),
            "categoria_osm": "%s=%s" % (r.get("category"), r.get("type")),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "comuna_osm": dir_.get("city") or dir_.get("town") or dir_.get("municipality") or dir_.get("suburb"),
            "region_osm": dir_.get("state"),
            "direccion_osm": r.get("display_name"),
            "fuente_url": "https://www.openstreetmap.org/%s/%s" % (r["osm_type"], r["osm_id"]),
            "fecha": HOY,
            "confianza": "pendiente",
            "match_ambiguo": bool(otras),
            "tipo_coherente": bool(coherente),
            "alternativas": [{"nombre_en_osm": c[5], "fuente_url": "https://www.openstreetmap.org/%s/%s" % (c[4]["osm_type"], c[4]["osm_id"]),
                              "direccion_osm": c[4].get("display_name")} for c in otras],
        })
        print("%2d/%d  ✓  %s  →  %s (%s)%s" % (n, len(insts), inst["nombre"], nombre_osm, ubicadas[-1]["comuna_osm"],
                                              "  [ambiguo]" if otras else ""))

    # Dos instituciones distintas en el mismo objeto de OSM es casi siempre un error de match.
    por_objeto = {}
    for u in ubicadas:
        por_objeto.setdefault(u["fuente_url"], []).append(u["id"])
    for u in ubicadas:
        otros = [i for i in por_objeto[u["fuente_url"]] if i != u["id"]]
        u["comparte_objeto_osm_con"] = otros

    os.makedirs(SALIDA_DIR, exist_ok=True)
    json.dump(ubicadas, open(os.path.join(SALIDA_DIR, "instituciones_ubicadas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sin_ubicar, open(os.path.join(SALIDA_DIR, "sin_ubicar.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    resumen = {
        "fecha": HOY, "fuente": "OpenStreetMap vía Nominatim (ODbL)", "instituciones": len(insts),
        "ubicadas": len(ubicadas), "ambiguas": sum(1 for u in ubicadas if u["match_ambiguo"]),
        "tipo_no_coherente": sum(1 for u in ubicadas if not u["tipo_coherente"]),
        "comparten_objeto": sum(1 for u in ubicadas if u["comparte_objeto_osm_con"]), "sin_ubicar": len(sin_ubicar),
    }
    json.dump(resumen, open(os.path.join(SALIDA_DIR, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
