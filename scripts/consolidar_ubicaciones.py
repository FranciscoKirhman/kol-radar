#!/usr/bin/env python3
"""
Junta en un solo archivo la ubicación de cada institución, con la fuente de cada dato por separado.

La dirección y el punto del mapa no tienen por qué salir de la misma fuente, y mezclarlos sin
decirlo es la forma más fácil de publicar una dirección que nadie verificó. Por eso cada
institución lleva dos fuentes: la de la DIRECCIÓN (texto citable) y la de las COORDENADAS.

Dirección, en este orden:
  1. Respuesta revisada del colaborador IA (data/pending/tarea-chatgpt-*/respuesta_*_A.json): sitio
     oficial o Superintendencia de Salud, con cita textual. Solo resultados ubicada/confirmada/corregida.
     Entre rondas manda la última (ORDEN_RONDAS), y cada dirección que cambia se imprime.
  2. Registro de establecimientos del DEIS (Minsal, datos.gob.cl, CC0), por código de establecimiento.
  3. OpenStreetMap, el objeto que aceptó scripts/geolocalizar_instituciones_osm.py.
Coordenadas, en este orden:
  1. DEIS: el Ministerio publica latitud y longitud de cada establecimiento.
  2. OpenStreetMap: el mismo objeto de arriba.
  3. Nominatim sobre la dirección verificada, dentro de la comuna declarada: vale si devuelve ese
     número de calle (precision "direccion"), o si solo encuentra la calle y la calle entera mide
     menos de CALLE_MAX_METROS (precision "calle"). Ojo: OSM parte las calles en tramos, así que
     eso acota el TRAMO devuelto, no la calle entera; por eso el punto se publica como "calle" y no
     como dirección. Una avenida larga se descarta igual, que es lo que importaba.
  4. Si nada de eso sirve pero la comuna está verificada: el centro de la comuna, marcado con
     precision "comuna" para que el mapa lo dibuje distinto. No es una dirección.

Una institución con varias sedes guarda todas en otras_sedes, pero el mapa usa solo la principal:
la de la ciudad donde la muestra la ubica.

Los DEIS se asignan a mano por código (DEIS_CODIGOS), no por parecido de nombre: en el registro
hay 21 "Santa María" y 27 establecimientos con "Puerto Montt" en el nombre.

Nada de esto pasa a data/sample/: el mapa lo lee aparte y muestra cada dato como pendiente de
revisión. Las diferencias entre fuentes quedan en "avisos" para la revisión humana.

Uso:
    python3 scripts/consolidar_ubicaciones.py [--deis ruta/establecimientos.csv]
Sin --deis, descarga la versión vigente desde datos.gob.cl.
"""
import argparse, csv, datetime, difflib, glob, io, json, math, os, re, time, unicodedata, urllib.parse, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
GEO = os.path.join(RAIZ, "data", "geo", "chile-regiones-comunas.json")
OSM = os.path.join(RAIZ, "data", "pending", "geolocalizacion-osm-2026-09-15", "instituciones_ubicadas.json")
RESPUESTAS = os.path.join(RAIZ, "data", "pending", "tarea-chatgpt-*", "respuesta_*_A.json")
ORDEN_RONDAS = ["tarea-chatgpt-2026-09-15", "tarea-chatgpt-2026-09-15-ronda2"]
SALIDA = os.path.join(RAIZ, "data", "geo", "ubicaciones-instituciones.json")
HOY = datetime.date.today().isoformat()

DEIS_PAQUETE = "https://datos.gob.cl/api/3/action/package_show?id=establecimientos-de-salud-vigentes"
DEIS_FICHA = "https://datos.gob.cl/dataset/establecimientos-de-salud-vigentes"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "kol-radar/1.0 (+https://github.com/FranciscoKirhman/kol-radar)"

# id de la muestra → código DEIS. Revisado a mano contra nombre, tipo y comuna del registro.
DEIS_CODIGOS = {
    "falp": "112254",                 # Instituto Clínico Oncológico Fundación Arturo López Pérez
    "torax": "112103",                # Instituto Nacional de Enfermedades Respiratorias y Cirugía Torácica
    "clinica-alemana": "112200",      # Clínica Alemana, Vitacura (no las de Osorno, Valdivia o Temuco)
    "clinica-las-condes": "112212",
    "orlandi": "200905",
    "clinica-santa-maria": "112249",  # Providencia (no La Reina, La Dehesa ni Los Dominicos)
    "hosp-concepcion": "118100",      # Hospital Clínico Regional Dr. Guillermo Grant Benavente
    "hosp-puerto-montt": "124105",
    "hosp-uchile": "109200",
    "hosp-carabineros": "112240",
    "oncovida": "201799",
    "inc": "109103",
    "ic-la-serena": "202100",
    "ucm": "116276",                  # la clínica de 2 Sur, no el local del mall
    "clinica-puerto-montt": "124250",
    "hosp-calvo-mackenna": "112102",
    "hosp-van-buren": "106100",
    "hosp-san-borja": "111100",
    "hosp-sotero": "114101",
    "hosp-militar": "112530",
    "hosp-salvador": "112100",        # el de Santiago, no los de Peumo o Valparaíso
    "hosp-rancagua": "115100",        # Hospital Dr. Franco Ravera Zunino
    "clinica-davila": "109201",       # Recoleta, no Dávila Vespucio
    "hosp-barros-luco": "113100",
    "hosp-valdivia": "122100",
    "hosp-temuco": "121109",
    "hosp-fricke": "107100",
    "hosp-talca": "116105",           # Hospital Dr. César Garavagno Burotto = Hospital Regional de Talca
    "hosp-sjd": "110100",
}
# Diferencia entre dos fuentes de coordenadas que amerita revisión.
AVISO_METROS = 400
# Diagonal máxima de la calle para aceptar su centro cuando OSM no tiene el número.
CALLE_MAX_METROS = 600
PREFIJOS_CALLE = re.compile(r"^(avenida|avda\.?|av\.?|calle|paseo|pasaje)\s+", re.I)
# "Alcalde Délano 12205, piso 2" → calle y número para geocodificar.
RELLENO = re.compile(r"\((?:ex|antes)[^)]*\)|\bsector\b.*$|^calle\s+", re.I)


def norm(s):
    s = (s or "").lower().strip()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", "".join(c for c in unicodedata.normalize("NFD", s)
                                                      if unicodedata.category(c) != "Mn")).split())


def metros(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 12742000 * math.asin(math.sqrt(a))


def dentro(x, y, plano):
    n, c, j = len(plano) // 2, False, len(plano) // 2 - 1
    for i in range(n):
        xi, yi, xj, yj = plano[2 * i], plano[2 * i + 1], plano[2 * j], plano[2 * j + 1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
            c = not c
        j = i
    return c


def clave_respuesta(ruta):
    """Ordena las respuestas por ronda y por número de lote, no por texto de la ruta."""
    carpeta = os.path.basename(os.path.dirname(ruta))
    if carpeta not in ORDEN_RONDAS:
        raise SystemExit("ronda desconocida: %s. Agregala a ORDEN_RONDAS en el orden que corresponda." % carpeta)
    archivo = os.path.basename(ruta)
    lote = re.search(r"lote(\d+)", archivo)
    return (ORDEN_RONDAS.index(carpeta), int(lote.group(1)) if lote else 0, archivo)


def leer_deis(ruta):
    if ruta:
        texto, recurso = open(ruta, encoding="utf-8").read(), "archivo local " + os.path.basename(ruta)
    else:
        paquete = json.load(urllib.request.urlopen(DEIS_PAQUETE, timeout=60))["result"]
        csvs = [r for r in paquete["resources"] if (r.get("format") or r["url"]).lower().endswith("csv") or r["url"].endswith(".csv")]
        recurso = csvs[0]["url"]
        texto = urllib.request.urlopen(recurso, timeout=120).read().decode("utf-8")
    filas = {r["EstablecimientoCodigo"]: r for r in csv.DictReader(io.StringIO(texto), delimiter=";")}
    return filas, recurso


ultima = [0.0]


def consultar_nominatim(params):
    espera = 1.1 - (time.time() - ultima[0])
    if espera > 0:
        time.sleep(espera)
    params.update({"format": "jsonv2", "addressdetails": "1", "limit": "5", "accept-language": "es", "countrycodes": "cl"})
    req = urllib.request.Request(NOMINATIM + "?" + urllib.parse.urlencode(params), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    finally:
        ultima[0] = time.time()


def geocodificar(calle, numero, comuna):
    """Nominatim estructurado. Devuelve (resultado, precision) o (None, None).

    OSM suele escribir "General Holley" donde el sitio oficial dice "Avenida General Holley", así
    que se prueba también sin el prefijo."""
    variantes = [calle]
    sin_prefijo = PREFIJOS_CALLE.sub("", calle)
    if sin_prefijo != calle:
        variantes.append(sin_prefijo)
    calle_corta = None
    for v in variantes:
        res = consultar_nominatim({"street": numero + " " + v, "city": comuna, "country": "Chile"})
        for r in res:
            if norm((r.get("address") or {}).get("house_number")) == norm(numero):
                return r, "direccion"
        for r in res:
            via = norm(PREFIJOS_CALLE.sub("", (r.get("address") or {}).get("road") or ""))
            s0, n0, w0, e0 = [float(x) for x in r["boundingbox"]]
            if r.get("category") == "highway" and via == norm(sin_prefijo) and metros(s0, w0, n0, e0) <= CALLE_MAX_METROS:
                calle_corta = calle_corta or r
    return (calle_corta, "calle") if calle_corta else (None, None)


def calle_y_numero(direccion):
    base = RELLENO.sub("", (direccion or "").split(",")[0]).strip()
    m = re.match(r"^(.*?)\s+(?:n[°º]\s*|#\s*)?(\d+)(?:-?[a-z])?$", base, re.I)
    return (m.group(1).strip(), m.group(2)) if m else (None, None)


def direccion_osm_corta(u):
    partes = [p.strip() for p in u["direccion_osm"].split(",")]
    if partes and partes[0] == u["nombre_en_osm"]:
        partes = partes[1:]
    if len(partes) >= 2 and partes[0].isdigit():
        return partes[1] + " " + partes[0]
    return partes[0] if partes else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deis", help="CSV de establecimientos ya descargado")
    args = ap.parse_args()

    muestra = json.load(open(MUESTRA, encoding="utf-8"))
    insts = [e for e in muestra["entidades"] if e["tipo"] == "institucion"]
    limites = json.load(open(GEO, encoding="utf-8"))
    comunas = {}
    for c in limites["comunas"]:
        comunas.setdefault(norm(c["nombre"]), []).append(c)
    osm = {u["id"]: u for u in json.load(open(OSM, encoding="utf-8"))}
    deis, deis_recurso = leer_deis(args.deis)

    # Orden de precedencia entre rondas, a mano: la última corrige a las anteriores. No se puede
    # inferir del nombre de la carpeta —sorted() pone ".../tarea-...-ronda2/respuesta" ANTES que
    # ".../tarea-.../respuesta" porque "-" < "/", y "lote10" antes que "lote2"—, y además es una
    # decisión editorial: qué ronda manda lo decide quien revisa, no el sistema de archivos.
    respuestas = {}
    for ruta in sorted(glob.glob(RESPUESTAS), key=clave_respuesta):
        for it in json.load(open(ruta, encoding="utf-8")).get("A") or []:
            it["_archivo"] = os.path.relpath(ruta, RAIZ)
            previo = respuestas.get(it["id"])
            if previo and (previo.get("direccion") or "") != (it.get("direccion") or ""):
                print("cambia %-22s «%s» (%s) → «%s» (%s)" % (it["id"], previo.get("direccion"), previo["_archivo"],
                                                              it.get("direccion"), it["_archivo"]))
            respuestas[it["id"]] = it

    def comuna_de(nombre, lon=None, lat=None):
        cands = comunas.get(norm(nombre)) or []
        if lon is None:
            return cands[0] if cands else None
        for c in cands:
            if any(dentro(lon, lat, a) for a in c["anillos"]):
                return c
        return None

    def comuna_por_punto(lon, lat):
        for lista in comunas.values():
            for c in lista:
                if any(dentro(lon, lat, a) for a in c["anillos"]):
                    return c
        return None

    salida, sin_ubicar, resumen = {}, {}, {"direccion": {}, "coordenadas": {}}
    for inst in insts:
        iid, avisos = inst["id"], []
        r = respuestas.get(iid)
        r_ok = r if r and r.get("resultado") in ("ubicada", "confirmada", "corregida") and r.get("direccion") else None
        d = deis.get(DEIS_CODIGOS.get(iid, ""))
        u = osm.get(iid)
        # Si la revisión CORRIGIÓ la dirección, el punto del DEIS o de OSM es el de la dirección
        # vieja (en universidades, la casa central en vez de la facultad): se geocodifica la nueva.
        if r_ok and r_ok.get("resultado") == "corregida":
            d_coords, u = None, None
        else:
            d_coords = d

        # ---- dirección
        if r_ok:
            principal = {"direccion": r_ok["direccion"], "comuna": r_ok["comuna"], "ciudad": r_ok.get("ciudad"),
                         "region": r_ok.get("region"), "nombre_oficial": r_ok.get("nombre_oficial"),
                         "fuente_direccion": {"url": r_ok["fuente_url"], "tipo": r_ok["fuente_tipo"],
                                              "cita": r_ok.get("cita_textual"), "fecha": r_ok["fecha_consulta"],
                                              "via": "colaborador IA, " + r_ok["_archivo"]}}
            otras = r_ok.get("otras_sedes") or []
        elif d:
            principal = {"direccion": (d["NombreVia"] + " " + d["Numero"]).strip(), "comuna": d["ComunaGlosa"],
                         "ciudad": None, "region": None, "nombre_oficial": d["EstablecimientoGlosa"],
                         "fuente_direccion": {"url": DEIS_FICHA, "tipo": "deis_minsal", "cita": None, "fecha": HOY,
                                              "via": "código de establecimiento " + d["EstablecimientoCodigo"]}}
            otras = []
        elif u:
            # Nominatim a veces llama "Santiago" a la comuna de todo el Gran Santiago: manda el polígono.
            cpu = comuna_por_punto(u["lon"], u["lat"])
            principal = {"direccion": direccion_osm_corta(u), "comuna": cpu["nombre"] if cpu else u["comuna_osm"], "ciudad": None,
                         "region": u["region_osm"], "nombre_oficial": u["nombre_en_osm"],
                         "fuente_direccion": {"url": u["fuente_url"], "tipo": "openstreetmap", "cita": None,
                                              "fecha": u["fecha"], "via": "scripts/geolocalizar_instituciones_osm.py"}}
            otras = []
        else:
            sin_ubicar[iid] = {"nombre": inst["nombre"], "ciudad_en_la_muestra": inst.get("ciudad"),
                               "motivo": (r or {}).get("motivo_si_no_encontrada") or "sin dirección en ninguna fuente revisada",
                               "fuente_revisada": (r or {}).get("fuente_url")}
            continue

        # ---- coordenadas
        coords = None
        if d_coords and d_coords.get("Latitud") and d_coords.get("Longitud"):
            coords = {"lat": float(d["Latitud"]), "lon": float(d["Longitud"]), "precision": "establecimiento",
                      "fuente": {"url": DEIS_FICHA, "tipo": "deis_minsal", "fecha": HOY,
                                 "via": "código de establecimiento " + d["EstablecimientoCodigo"]}}
        if u:
            punto_osm = {"lat": u["lat"], "lon": u["lon"], "precision": "establecimiento",
                         "fuente": {"url": u["fuente_url"], "tipo": "openstreetmap", "fecha": u["fecha"],
                                    "via": "scripts/geolocalizar_instituciones_osm.py"}}
            if coords:
                dist = metros(coords["lat"], coords["lon"], u["lat"], u["lon"])
                if dist > AVISO_METROS:
                    avisos.append("DEIS y OpenStreetMap difieren en %d m" % dist)
            else:
                coords = punto_osm
            if u.get("match_ambiguo") and not (r_ok and r_ok.get("tarea") == "verificar"):
                avisos.append("OpenStreetMap tiene otra sede con el mismo nombre a más de 500 m")
        calle, numero = calle_y_numero(principal["direccion"])
        if not coords and calle:
            hit, precision = geocodificar(calle, numero, principal["comuna"])
            if hit:
                lat, lon = float(hit["lat"]), float(hit["lon"])
                if comuna_de(principal["comuna"], lon, lat):
                    coords = {"lat": lat, "lon": lon, "precision": precision,
                              "fuente": {"url": "https://www.openstreetmap.org/%s/%s" % (hit["osm_type"], hit["osm_id"]),
                                         "tipo": "openstreetmap", "fecha": HOY,
                                         "via": "Nominatim, búsqueda de «%s %s, %s»" % (calle, numero, principal["comuna"])}}
                else:
                    avisos.append("Nominatim ubicó «%s %s» fuera de la comuna %s; descartado" % (calle, numero, principal["comuna"]))
        if not coords:
            c = comuna_de(principal["comuna"])
            if c:
                coords = {"lat": c["centro"][1], "lon": c["centro"][0], "precision": "comuna",
                          "fuente": {"url": limites["fuente_url"], "tipo": "geoboundaries", "fecha": limites["fecha"],
                                     "via": "centro de la comuna " + c["nombre"] + "; la dirección no se pudo ubicar"}}
        if not coords:
            sin_ubicar[iid] = {"nombre": inst["nombre"], "ciudad_en_la_muestra": inst.get("ciudad"),
                               "motivo": "hay dirección pero ni la comuna se pudo ubicar", "direccion": principal["direccion"]}
            continue

        # ---- coherencia: el punto debe caer en la comuna de la dirección
        cp = comuna_por_punto(coords["lon"], coords["lat"])
        if cp and norm(cp["nombre"]) != norm(principal["comuna"]):
            avisos.append("el punto cae en %s y la dirección dice %s" % (cp["nombre"], principal["comuna"]))
        if cp and not principal.get("region"):
            principal["region"] = cp["region"]
        if r_ok and d:
            # El DEIS trae erratas ("Santos Dumond") y la oficina pegada a la calle ("Manuel Montt, oficina 101").
            calle_d = norm(PREFIJOS_CALLE.sub("", d["NombreVia"].split(",")[0]))
            calle_v = norm(PREFIJOS_CALLE.sub("", calle or ""))
            if calle_d and calle_v and difflib.SequenceMatcher(None, calle_d, calle_v).ratio() < 0.85:
                avisos.append("la dirección verificada (%s) no es la del DEIS (%s %s)" % (principal["direccion"], d["NombreVia"], d["Numero"]))
            elif numero and d["Numero"] and int(numero) != int(re.sub(r"\D", "", d["Numero"]) or 0):
                avisos.append("el número verificado (%s) no es el del DEIS (%s)" % (numero, d["Numero"]))

        principal.update(coords)
        principal["fuente_coordenadas"] = principal.pop("fuente")
        principal["confianza"] = "pendiente"
        salida[iid] = {"nombre": inst["nombre"], "principal": principal,
                       "otras_sedes": [{"direccion": o.get("direccion"), "comuna": o.get("comuna"), "fuente_url": o.get("fuente_url")}
                                       for o in otras],
                       "avisos": avisos}
        t = principal["fuente_direccion"]["tipo"]
        resumen["direccion"][t] = resumen["direccion"].get(t, 0) + 1
        k = principal["fuente_coordenadas"]["tipo"] + " · " + coords["precision"]
        resumen["coordenadas"][k] = resumen["coordenadas"].get(k, 0) + 1
        print("%-22s %-13s %-40s %s" % (iid, coords["precision"], principal["direccion"][:40], " | ".join(avisos)))

    doc = {
        "generado": HOY,
        "nota": "Propuesta pendiente de revisión humana. El mapa usa solo 'principal'; 'otras_sedes' se muestran en la ficha.",
        "fuentes": {
            "deis_minsal": {"nombre": "Establecimientos de Salud (DEIS, Minsal)", "url": DEIS_FICHA, "recurso": deis_recurso, "licencia": "CC0"},
            "openstreetmap": {"nombre": "OpenStreetMap", "url": "https://www.openstreetmap.org/copyright", "licencia": "ODbL, © colaboradores de OpenStreetMap"},
            "geoboundaries": {"nombre": limites["fuente"], "url": limites["fuente_url"], "licencia": limites["licencia"]},
        },
        "resumen": {"con_ubicacion": len(salida), "sin_ubicar": len(sin_ubicar), **resumen},
        "instituciones": salida,
        "sin_ubicar": sin_ubicar,
    }
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps(doc["resumen"], ensure_ascii=False, indent=1))
    print("sin ubicar:", ", ".join(sin_ubicar))


if __name__ == "__main__":
    main()
