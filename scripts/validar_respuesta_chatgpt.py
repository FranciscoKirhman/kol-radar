#!/usr/bin/env python3
"""
Valida la respuesta de un colaborador IA a la tarea de data/pending/tarea-chatgpt-<fecha>/.

No acepta ni integra nada: separa lo que se puede revisar de lo que viene roto, para que la
revisión humana no pierda tiempo en direcciones mal ubicadas o fuentes que no sirven.

Errores (bloquean el ítem):
  - Campos obligatorios ausentes, valores fuera de los permitidos, IDs o NCT que no existen.
  - Fuente que no es https, o de un dominio prohibido (LinkedIn, acortadores, Google Maps).
  - Coordenadas fuera de Chile, fuera de la comuna declarada, o lejos de la ciudad de la muestra.
  - Comuna que no existe o que no pertenece a la región de la ciudad de la muestra.
  - Un NCT "verificado" que según la muestra no contiene esa sede.
Advertencias (se revisan con más cuidado):
  - Dos instituciones con la misma dirección, cita sin número de calle, ciudad distinta a la de
    la muestra, una persona ligada sin decir por qué es la misma persona.

Uso:
    python3 scripts/validar_respuesta_chatgpt.py data/pending/tarea-chatgpt-2026-09-15/respuesta_lote1.json [...]
Escribe <archivo>.informe.md al lado de cada respuesta. Sale con código 1 si hay errores.
"""
import collections, csv, glob, json, math, os, re, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
GEO = os.path.join(RAIZ, "data", "geo", "chile-regiones-comunas.json")
PROHIBIDOS = ("linkedin.com", "goo.gl", "bit.ly", "maps.app.goo.gl", "google.com/maps", "google.cl/maps", "maps.google",
              "doctoralia", "asco.org", "iaslc.org", "wclc")
RESULTADOS = {
    "A": {"ubicada", "confirmada", "corregida", "no_encontrada"},
    "B": {"institucion_existente", "institucion_nueva", "marcador_patrocinador", "no_resoluble"},
    "C": {"sedes_nombradas", "solo_marcadores", "sin_sedes_en_chile"},
    "D": {"afiliacion_encontrada", "no_encontrada"},
}
FUENTE_TIPOS = {"sitio_oficial", "superintendencia_salud", "deis_minsal", "openstreetmap", "registro_empresas", "otro"}
COMUNAS_RM_CIUDAD = {"santiago"}


def norm(s):
    s = (s or "").lower().strip()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


def dentro(x, y, plano):
    n, c, j = len(plano) // 2, False, len(plano) // 2 - 1
    for i in range(n):
        xi, yi, xj, yj = plano[2 * i], plano[2 * i + 1], plano[2 * j], plano[2 * j + 1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
            c = not c
        j = i
    return c


class Informe:
    def __init__(self):
        self.errores, self.avisos, self.ok = [], [], collections.Counter()

    def error(self, tarea, clave, msg):
        self.errores.append((tarea, clave, msg))

    def aviso(self, tarea, clave, msg):
        self.avisos.append((tarea, clave, msg))


def main(rutas):
    if not rutas:
        print(__doc__); return 2
    muestra = json.load(open(MUESTRA, encoding="utf-8"))
    by_id = {e["id"]: e for e in muestra["entidades"]}
    ciudades_geo = muestra["geo"]["ciudades"]
    geo = json.load(open(GEO, encoding="utf-8"))
    comunas = {}
    for c in geo["comunas"]:
        comunas.setdefault(norm(c["nombre"]), []).append(c)
    carpeta = os.path.dirname(os.path.abspath(rutas[0]))

    def leer_csv(nombre):
        ruta = os.path.join(carpeta, nombre)
        return list(csv.DictReader(open(ruta, encoding="utf-8"))) if os.path.exists(ruta) else []

    csv_a = {r["id"]: r for r in leer_csv("A_instituciones.csv")}
    csv_b = {r["texto_sede"]: r for r in leer_csv("B_sedes_por_resolver.csv")}
    csv_c = {r["nct"]: r for r in leer_csv("C_ensayos_sin_sede_nombrada.csv")}
    csv_d = {r["id"]: r for r in leer_csv("D_personas_sin_institucion.csv")}
    instituciones = {e["id"] for e in muestra["entidades"] if e["tipo"] == "institucion"}
    sedes_por_nct = {e["id"].upper(): set(e.get("sedes_pendientes_resolucion") or []) for e in muestra["entidades"] if e["tipo"] == "ensayo_clinico"}

    def region_de_ciudad(ciudad):
        base = norm((ciudad or "").split(" (")[0])
        if base in COMUNAS_RM_CIUDAD:
            return "Región Metropolitana de Santiago"
        cand = comunas.get(base) or comunas.get(norm({"port montt": "Puerto Montt", "renaca": "Viña del Mar"}.get(base, "")))
        return cand[0]["region"] if cand else None

    def centro_ciudad(ciudad):
        c = (ciudad or "").split(" (")[0]
        g = ciudades_geo.get(c) or ciudades_geo.get({"Puerto Montt": "Port Montt"}.get(c, ""))
        return (g["lat"], g["lon"]) if g else None

    def revisar_url(inf, tarea, clave, url, campo="fuente_url", obligatoria=True):
        if not url:
            if obligatoria:
                inf.error(tarea, clave, "falta %s" % campo)
            return
        if not re.match(r"^https://", url):
            inf.error(tarea, clave, "%s no es https: %s" % (campo, url))
        if any(p in url.lower() for p in PROHIBIDOS):
            inf.error(tarea, clave, "%s usa una fuente prohibida o no citable: %s" % (campo, url))

    def revisar_lugar(inf, tarea, clave, item, ciudad_muestra):
        for campo in ("direccion", "comuna", "ciudad", "fuente_url", "cita_textual", "fecha_consulta"):
            if not item.get(campo):
                inf.error(tarea, clave, "falta %s" % campo)
        revisar_url(inf, tarea, clave, item.get("fuente_url"))
        if item.get("fuente_tipo") and item["fuente_tipo"] not in FUENTE_TIPOS:
            inf.error(tarea, clave, "fuente_tipo desconocido: %s" % item["fuente_tipo"])
        if item.get("fuente_tipo") == "openstreetmap" and not re.search(r"openstreetmap\.org/(node|way|relation)/\d+", item.get("fuente_url") or ""):
            inf.error(tarea, clave, "fuente OpenStreetMap sin URL de objeto (node/way/relation)")
        cand = comunas.get(norm(item.get("comuna")))
        esperada = region_de_ciudad(ciudad_muestra)
        if item.get("comuna") and not cand:
            inf.error(tarea, clave, "la comuna '%s' no existe en los límites oficiales" % item["comuna"])
        elif cand and esperada and all(c["region"] != esperada for c in cand):
            inf.error(tarea, clave, "la comuna '%s' es de %s, pero la muestra ubica la institución en %s" % (item["comuna"], cand[0]["region"], esperada))
        lat, lon = item.get("lat"), item.get("lon")
        if lat is not None or lon is not None:
            try:
                lat, lon = float(lat), float(lon)
            except (TypeError, ValueError):
                inf.error(tarea, clave, "lat/lon no numéricos"); return
            if not (-56.5 < lat < -17 and -76.5 < lon < -66):
                inf.error(tarea, clave, "coordenadas fuera de Chile continental: %s, %s" % (lat, lon))
            if cand and not any(dentro(lon, lat, a) for c in cand for a in c["anillos"]):
                inf.error(tarea, clave, "las coordenadas no caen dentro de la comuna declarada (%s)" % item["comuna"])
            cc = centro_ciudad(ciudad_muestra)
            if cc:
                limite = 45 if norm((ciudad_muestra or "").split(" (")[0]) == "santiago" else 25
                d = km(lat, lon, cc[0], cc[1])
                if d > limite:
                    inf.error(tarea, clave, "coordenadas a %.0f km del centro de %s (límite %d km)" % (d, ciudad_muestra, limite))
            if item.get("fuente_tipo") not in ("openstreetmap", "deis_minsal"):
                inf.aviso(tarea, clave, "trae coordenadas pero la fuente es '%s': confirmar que la fuente las publica" % item.get("fuente_tipo"))
        if item.get("cita_textual") and not re.search(r"\d", item["cita_textual"]):
            inf.aviso(tarea, clave, "la cita no tiene número de calle: confirmar que es una dirección y no solo la comuna")
        if item.get("cita_textual") and len(item["cita_textual"].split()) > 40:
            inf.aviso(tarea, clave, "cita de más de 40 palabras")

    codigo = 0
    for ruta in rutas:
        inf = Informe()
        try:
            resp = json.load(open(ruta, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            print("%s: no es JSON válido (%s)" % (ruta, err)); codigo = 1; continue
        direcciones = collections.defaultdict(list)

        for item in resp.get("A") or []:
            clave = item.get("id")
            fila = csv_a.get(clave)
            if not fila:
                inf.error("A", clave, "id que no está en A_instituciones.csv"); continue
            if item.get("resultado") not in RESULTADOS["A"]:
                inf.error("A", clave, "resultado inválido: %s" % item.get("resultado")); continue
            if item["resultado"] == "no_encontrada":
                if not item.get("motivo_si_no_encontrada"):
                    inf.error("A", clave, "no_encontrada sin motivo")
                else:
                    inf.ok["A"] += 1
                continue
            n = len(inf.errores)
            revisar_lugar(inf, "A", clave, item, fila["ciudad_en_la_muestra"])
            if item.get("direccion"):
                direcciones[norm(item["direccion"])].append(clave)
            if len(inf.errores) == n:
                inf.ok["A"] += 1
        for dirn, ids in direcciones.items():
            if len(ids) > 1:
                inf.aviso("A", ", ".join(ids), "misma dirección para varias instituciones")

        for item in resp.get("B") or []:
            clave = item.get("texto_sede")
            fila = csv_b.get(clave)
            n = len(inf.errores)
            if not fila:
                inf.error("B", clave, "texto_sede que no está en B_sedes_por_resolver.csv (debe copiarse idéntico)"); continue
            res = item.get("resultado")
            if res not in RESULTADOS["B"]:
                inf.error("B", clave, "resultado inválido: %s" % res); continue
            ncts = item.get("nct_verificados") or []
            if res in ("institucion_existente", "institucion_nueva"):
                if not ncts:
                    inf.error("B", clave, "falta nct_verificados")
                for nct in ncts:
                    if clave not in sedes_por_nct.get(str(nct).upper(), set()):
                        inf.error("B", clave, "según la muestra, %s no tiene la sede '%s'" % (nct, clave))
                if not re.search(r"clinicaltrials\.gov/study/NCT\d{8}", item.get("evidencia_url") or ""):
                    inf.error("B", clave, "evidencia_url debe ser la ficha exacta de ClinicalTrials.gov")
                revisar_url(inf, "B", clave, item.get("evidencia_institucion_url"), "evidencia_institucion_url")
                if not item.get("cita_textual"):
                    inf.error("B", clave, "falta cita_textual")
            if res == "institucion_existente":
                iid = item.get("id_institucion")
                if iid not in instituciones:
                    inf.error("B", clave, "id_institucion inexistente: %s" % iid)
                else:
                    ciudad_inst = norm((by_id[iid].get("ciudad") or "").split(" (")[0])
                    ciudad_ct = norm(item.get("ciudad_en_clinicaltrials"))
                    if ciudad_ct and ciudad_inst and ciudad_ct != ciudad_inst and region_de_ciudad(ciudad_ct) != region_de_ciudad(ciudad_inst):
                        inf.aviso("B", clave, "la sede está en %s y la institución %s en %s: ¿otra sede de la misma red?" % (item.get("ciudad_en_clinicaltrials"), iid, by_id[iid].get("ciudad")))
            if res == "institucion_nueva":
                nueva = item.get("institucion_nueva") or {}
                if not nueva.get("nombre_oficial"):
                    inf.error("B", clave, "institucion_nueva sin nombre_oficial")
                revisar_lugar(inf, "B", clave, nueva, item.get("ciudad_en_clinicaltrials") or fila["ciudades_de_esos_ensayos"].split(" | ")[0])
            if len(inf.errores) == n:
                inf.ok["B"] += 1

        for item in resp.get("C") or []:
            clave = item.get("nct")
            n = len(inf.errores)
            if clave not in csv_c:
                inf.error("C", clave, "nct que no está en C_ensayos_sin_sede_nombrada.csv"); continue
            if item.get("resultado") not in RESULTADOS["C"]:
                inf.error("C", clave, "resultado inválido: %s" % item.get("resultado")); continue
            if not re.search(r"clinicaltrials\.gov/study/%s" % re.escape(clave), item.get("evidencia_url") or "", re.I):
                inf.error("C", clave, "evidencia_url debe ser la ficha de ese mismo NCT")
            for sede in item.get("sedes") or []:
                if sede.get("resultado") not in RESULTADOS["B"]:
                    inf.error("C", clave, "sede con resultado inválido: %s" % sede.get("resultado"))
                if sede.get("resultado") == "institucion_existente" and sede.get("id_institucion") not in instituciones:
                    inf.error("C", clave, "id_institucion inexistente: %s" % sede.get("id_institucion"))
                if sede.get("resultado") == "institucion_nueva":
                    revisar_lugar(inf, "C", clave, sede.get("institucion_nueva") or {}, sede.get("ciudad"))
            if item["resultado"] == "sedes_nombradas" and not item.get("sedes"):
                inf.error("C", clave, "sedes_nombradas sin sedes")
            if len(inf.errores) == n:
                inf.ok["C"] += 1

        for item in resp.get("D") or []:
            clave = item.get("id")
            n = len(inf.errores)
            if clave not in csv_d:
                inf.error("D", clave, "id que no está en D_personas_sin_institucion.csv"); continue
            if item.get("resultado") not in RESULTADOS["D"]:
                inf.error("D", clave, "resultado inválido"); continue
            if item["resultado"] == "afiliacion_encontrada":
                revisar_url(inf, "D", clave, item.get("fuente_url"))
                if not item.get("cita_textual"):
                    inf.error("D", clave, "falta cita_textual")
                inst = item.get("institucion") or {}
                if inst.get("id_institucion") and inst["id_institucion"] not in instituciones:
                    inf.error("D", clave, "id_institucion inexistente: %s" % inst["id_institucion"])
                if not item.get("notas") or len(item["notas"].split()) < 5:
                    inf.aviso("D", clave, "no explica por qué es la misma persona (ORCID, nombre completo + institución)")
            if len(inf.errores) == n:
                inf.ok["D"] += 1

        lineas = ["# Validación de %s" % os.path.basename(ruta), "",
                  "| Tarea | Ítems válidos |", "|---|---|"] + ["| %s | %d |" % (t, inf.ok[t]) for t in "ABCD"] + [""]
        lineas += ["## Errores (%d)" % len(inf.errores), ""] + ["- **%s · %s** — %s" % e for e in inf.errores] + [""]
        lineas += ["## Advertencias (%d)" % len(inf.avisos), ""] + ["- **%s · %s** — %s" % a for a in inf.avisos]
        open(ruta + ".informe.md", "w", encoding="utf-8").write("\n".join(lineas) + "\n")
        print("%s: %s válidos · %d errores · %d advertencias → %s" % (
            os.path.basename(ruta), dict(inf.ok), len(inf.errores), len(inf.avisos), os.path.basename(ruta) + ".informe.md"))
        codigo = codigo or (1 if inf.errores else 0)
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
