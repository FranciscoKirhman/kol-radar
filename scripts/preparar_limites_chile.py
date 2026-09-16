#!/usr/bin/env python3
"""
Prepara los límites de regiones y comunas de Chile para dibujar el mapa por ciudad.

Fuente: geoBoundaries (gbOpen, CHL ADM1 y ADM3), que redistribuye datos de la Biblioteca del
Congreso Nacional de Chile (BCN) y OCHA ROLAC bajo licencia CC BY 3.0 IGO. Son geometría
administrativa pública, no datos sobre personas.

Los archivos originales pesan 19 MB. Para el navegador se simplifican (Douglas-Peucker), se
redondean a 3 decimales (~110 m, de sobra para una comuna) y se descartan las islas diminutas
que no se ven a ningún zoom útil. Cada comuna queda asignada a su región por el punto medio de
su contorno.

Salida: data/geo/chile-regiones-comunas.json

Uso:
    python3 scripts/preparar_limites_chile.py            # descarga de geoBoundaries
    python3 scripts/preparar_limites_chile.py adm1.geojson adm3.geojson   # desde archivos locales
"""
import collections, datetime, json, os, sys, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "data", "geo", "chile-regiones-comunas.json")
API = "https://www.geoboundaries.org/api/current/gbOpen/CHL/%s/"
FICHA = "https://www.geoboundaries.org/countryDownloads.html"
USER_AGENT = "kol-radar/1.0 (+https://github.com/FranciscoKirhman/kol-radar)"
TOL_REGION, TOL_COMUNA = 0.02, 0.004      # grados; 0.004 ≈ 400 m
AREA_MINIMA = 0.0004                        # grados²; islas más chicas que ~2 × 2 km se descartan


def descargar(nivel):
    meta = json.load(urllib.request.urlopen(urllib.request.Request(API % nivel, headers={"User-Agent": USER_AGENT}), timeout=60))
    url = meta["simplifiedGeometryGeoJSON"]
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=300)), url


def reparar(s):
    # Los nombres de regiones vienen con doble codificación ("RegiÃ³n"); los de comunas no.
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def dp(puntos, tol):
    """Douglas-Peucker iterativo sobre una lista de (lon, lat)."""
    if len(puntos) < 4:
        return puntos
    guardar = [False] * len(puntos)
    guardar[0] = guardar[-1] = True
    pila = [(0, len(puntos) - 1)]
    while pila:
        a, b = pila.pop()
        (x1, y1), (x2, y2) = puntos[a], puntos[b]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5 or 1e-12
        idx, dmax = -1, 0.0
        for i in range(a + 1, b):
            x0, y0 = puntos[i]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / L
            if d > dmax:
                idx, dmax = i, d
        if dmax > tol and idx != -1:
            guardar[idx] = True
            pila.append((a, idx)); pila.append((idx, b))
    return [p for p, g in zip(puntos, guardar) if g]


def dp_anillo(anillo, tol):
    """Douglas-Peucker sobre un anillo cerrado. Sin esto, con el primer punto igual al último
    la recta de referencia mide cero y el algoritmo borraba el anillo entero."""
    if len(anillo) > 1 and anillo[0] == anillo[-1]:
        anillo = anillo[:-1]
    if len(anillo) < 4:
        return anillo
    x0, y0 = anillo[0]
    m = max(range(len(anillo)), key=lambda i: (anillo[i][0] - x0) ** 2 + (anillo[i][1] - y0) ** 2)
    return dp(anillo[:m + 1], tol) + dp(anillo[m:] + [anillo[0]], tol)[1:-1]


def area(anillo):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]))) / 2


def anillos_de(geom, tol):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    salida = []
    for poly in polys:
        exterior = [tuple(p[:2]) for p in poly[0]]
        if area(exterior) < AREA_MINIMA:
            continue
        simple = dp_anillo(exterior, tol)
        if len(simple) >= 3:
            salida.append([round(v, 3) for p in simple for v in p])
    return salida


def dentro(x, y, plano):
    """Punto en polígono (anillo plano [x0,y0,x1,y1,...]) por cruce de rayos."""
    n, c = len(plano) // 2, False
    j = n - 1
    for i in range(n):
        xi, yi, xj, yj = plano[2 * i], plano[2 * i + 1], plano[2 * j], plano[2 * j + 1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
            c = not c
        j = i
    return c


def main():
    # La fuente que se publica es SIEMPRE la página de geoBoundaries, nunca la ruta del archivo que
    # se usó para correr el script: esa ruta no le sirve a nadie y, si viene de un directorio
    # temporal, filtra el disco de quien lo corrió al JSON que se publica.
    if len(sys.argv) == 3:
        adm1, adm3 = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
        recursos = ["copia local de " + os.path.basename(sys.argv[1]), "copia local de " + os.path.basename(sys.argv[2])]
    else:
        (adm1, u1), (adm3, u3) = descargar("ADM1"), descargar("ADM3")
        recursos = [u1, u3]
    regiones = []
    for f in adm1["features"]:
        regiones.append({"nombre": reparar(f["properties"]["shapeName"]), "anillos": anillos_de(f["geometry"], TOL_REGION),
                         "_fino": anillos_de(f["geometry"], TOL_COMUNA)})
    comunas, sin_region = [], 0
    for f in adm3["features"]:
        anillos = anillos_de(f["geometry"], TOL_COMUNA)
        if not anillos:
            continue
        mayor = max(anillos, key=len)
        xs, ys = mayor[0::2], mayor[1::2]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        # Por votación de vértices, no por el centro de la caja: en comunas costeras como Puerto
        # Montt o Talcahuano el centro cae en el mar y la comuna quedaba sin región.
        votos = collections.Counter()
        paso = max(1, len(xs) // 24)
        for x, y in zip(xs[::paso], ys[::paso]):
            for r in regiones:
                if any(dentro(x, y, a) for a in r["_fino"]):
                    votos[r["nombre"]] += 1
                    break
        region = votos.most_common(1)[0][0] if votos else None
        sin_region += region is None
        comunas.append({"nombre": reparar(f["properties"]["shapeName"]), "region": region,
                        "centro": [round(cx, 3), round(cy, 3)], "anillos": anillos})
    for r in regiones:
        del r["_fino"]
    salida = {
        "fuente": "geoBoundaries gbOpen (CHL ADM1, ADM3) — datos de la Biblioteca del Congreso Nacional de Chile (BCN) y OCHA ROLAC",
        "licencia": "CC BY 3.0 IGO",
        "fuente_url": FICHA,
        "recursos": recursos,
        "fecha": datetime.date.today().isoformat(),
        "nota": "Geometría simplificada para dibujo (tolerancia %.3f° comunas, %.2f° regiones; coordenadas a 3 decimales). "
                "Anillos planos [lon, lat, lon, lat, ...]. No sirve para medir superficies." % (TOL_COMUNA, TOL_REGION),
        "regiones": regiones,
        "comunas": comunas,
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump(salida, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("%d regiones, %d comunas (%d sin región), %d KB → %s" % (
        len(regiones), len(comunas), sin_region, os.path.getsize(SALIDA) // 1024, os.path.relpath(SALIDA, RAIZ)))


if __name__ == "__main__":
    main()
