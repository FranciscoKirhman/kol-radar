#!/usr/bin/env python3
"""
Propone enriquecimiento desde OpenAlex para las personas de la muestra.

NUNCA escribe directo sobre data/sample/perfiles-muestra.json. Escribe una PROPUESTA en
data/pending/, que se revisa como diff en un Pull Request antes de entrar a main
(decisión 3.2 de DECISIONS.md). Ante contradicción con un dato existente, el dato viejo se
mantiene y el nuevo queda anotado como conflicto para que lo resuelva una persona
(decisión 3.3, opción A).

Uso:
    OPENALEX_API_KEY=... python3 scripts/enriquecer_openalex.py
    python3 scripts/enriquecer_openalex.py --dry-run     # sin key, pool "polite"
"""
import json, os, sys, time, urllib.parse, urllib.request, unicodedata, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
SALIDA_DIR = os.path.join(RAIZ, "data", "pending")
MAILTO = "kol-radar@example.org"   # pool "polite" de OpenAlex; se reemplaza por el contacto real
API = "https://api.openalex.org/authors"


def norm(s):
    s = (s or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kol-radar/1.0 (+%s)" % MAILTO})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def buscar_autor(nombre, api_key):
    params = {"search": nombre, "per-page": "10", "mailto": MAILTO}
    if api_key:
        params["api_key"] = api_key
    return get(API + "?" + urllib.parse.urlencode(params)).get("results", [])


def tokens(nombre):
    return [t for t in norm(nombre).replace("-", " ").replace(".", " ").split() if t]


def nombre_compatible(a, b):
    """Compuerta dura antes de puntuar nada.

    Sin esto el buscador de OpenAlex devuelve coincidencias por apellido con nombre de pila
    distinto ('Carlos Rojas' -> 'Carolina Rojas', 'Roberto Gonzalez' -> 'Giuseppe Roberto')
    y una puntuación alta por institución chilena las dejaba pasar. Exigimos que el nombre
    de pila coincida (o sea una inicial del otro) y que compartan al menos un apellido.
    """
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    pa, pb = ta[0], tb[0]
    pila_ok = (pa == pb
               or (len(pa) == 1 and pb.startswith(pa))
               or (len(pb) == 1 and pa.startswith(pb)))
    if not pila_ok:
        return False
    # apellidos: cualquier token posterior en común (ignorando iniciales sueltas)
    ap_a = {t for t in ta[1:] if len(t) > 1}
    ap_b = {t for t in tb[1:] if len(t) > 1}
    return bool(ap_a & ap_b)


# Palabras demasiado comunes en nombres de instituciones chilenas para probar identidad.
GENERICAS = {
    "instituto", "institute", "sociedad", "society", "chile", "chilena", "chileno",
    "universidad", "university", "hospital", "clinica", "centro", "center", "centre",
    "facultad", "faculty", "departamento", "department", "servicio", "unidad", "unit",
    "nacional", "national", "medicina", "medicine", "salud", "health", "ciencias",
    "escuela", "school", "laboratorio", "laboratory", "profesional", "regional",
    "santiago", "pontificia", "catolica", "catholic", "investigacion", "research",
}


def palabras_distintivas(texto):
    return {w for w in texto.replace(",", " ").replace(".", " ").split()
            if len(w) > 4 and w not in GENERICAS}


def evaluar(cand, persona):
    """Puntúa qué tan buena es la coincidencia. Solo señales verificables, sin adivinar."""
    razones, puntos = [], 0
    insts = cand.get("last_known_institutions") or []
    nombres_inst = [i.get("display_name", "") for i in insts]
    en_chile = any(i.get("country_code") == "CL" for i in insts)
    if not en_chile:
        # Compuerta dura, no un punto más: el alcance del proyecto es Chile. Sin esto, un
        # homónimo con ORCID en otro país (ej. un Carlos Rojas de la Universidad de Costa
        # Rica, 115 trabajos) alcanzaba el umbral y se proponía como si fuera el nuestro.
        return 0, ["descartado: sin institución conocida en Chile"]
    puntos += 3
    razones.append("institución conocida en Chile (%s)" % "; ".join(nombres_inst))
    if cand.get("orcid"):
        puntos += 3
        razones.append("ORCID publicado")

    # ¿la afiliación declarada en nuestra muestra aparece en OpenAlex?
    # Solo se comparan palabras DISTINTIVAS. Sin esto, "instituto", "sociedad", "chile" o
    # "universidad" -- presentes en casi todo nombre de institución chilena -- producían falsas
    # coincidencias que APAGABAN la advertencia: "Instituto Nacional del Tórax" matcheaba con
    # "Instituto Profesional Providencia" por la palabra "instituto".
    sub = norm(persona.get("subtitulo", ""))
    sub_dist = palabras_distintivas(sub)
    afil_ok = False
    for n in nombres_inst:
        nn = norm(n)
        if not sub:
            break
        if nn in sub or sub in nn:
            afil_ok = True
            break
        if sub_dist and (sub_dist & palabras_distintivas(nn)):
            afil_ok = True
            break
    if afil_ok:
        puntos += 2
        razones.append("coincide con la afiliación de nuestra muestra (%s)" % persona.get("subtitulo"))
    else:
        # No baja el puntaje (la afiliación puede haber cambiado o faltar en OpenAlex), pero
        # se dice explícito: es la señal que distingue a nuestro Andrés Rojas G. del Hospital
        # Puerto Montt de otro Andrés Rojas del Instituto Tecnológico del Salmón.
        razones.append("OJO: ninguna institución de OpenAlex coincide con la afiliación de "
                       "nuestra muestra (%s) — verificar que sea la misma persona"
                       % persona.get("subtitulo"))

    if norm(cand.get("display_name")) == norm(persona["nombre"]):
        puntos += 1
        razones.append("nombre idéntico")
    if (cand.get("works_count") or 0) >= 5:
        puntos += 1
        razones.append("%d trabajos indexados" % cand["works_count"])
    return puntos, razones


def main():
    api_key = os.environ.get("OPENALEX_API_KEY")
    dry = "--dry-run" in sys.argv
    if not api_key and not dry:
        print("ERROR: falta OPENALEX_API_KEY (o usá --dry-run)", file=sys.stderr)
        return 1
    if not api_key:
        print("· sin API key: usando el pool 'polite' de OpenAlex (más lento, sin garantías)")

    datos = json.load(open(MUESTRA, encoding="utf-8"))
    personas = [e for e in datos["entidades"] if e["tipo"] == "persona"]
    propuestas, sin_match, conflictos = [], [], []

    for i, p in enumerate(personas, 1):
        try:
            cands = buscar_autor(p["nombre"], api_key)
        except Exception as ex:
            print("  %d/%d %-34s ERROR %s" % (i, len(personas), p["nombre"], ex))
            continue

        evaluados = []
        for c in cands:
            if not nombre_compatible(p["nombre"], c.get("display_name", "")):
                continue
            pts, raz = evaluar(c, p)
            evaluados.append((pts, raz, c))
        evaluados.sort(key=lambda x: -x[0])

        # Umbral: institución chilena es obligatoria (compuerta en evaluar()), y encima
        # exigimos >=6, o sea al menos otra señal fuerte. Preferimos no traer dato antes
        # que traer el equivocado -- una propuesta errónea que se ve confiable es peor
        # que ninguna propuesta.
        evaluados = [e for e in evaluados if e[0] > 0]
        if not evaluados or evaluados[0][0] < 6:
            sin_match.append({"id": p["id"], "nombre": p["nombre"],
                              "motivo": "ninguna coincidencia superó el umbral de evidencia",
                              "candidatos_vistos": len(cands)})
            print("  %d/%d %-34s sin coincidencia confiable" % (i, len(personas), p["nombre"]))
            continue

        pts, raz, mejor = evaluados[0]
        segundo = evaluados[1][0] if len(evaluados) > 1 else 0
        ambiguo = segundo >= pts - 1 and segundo >= 5

        orcid_nuevo = (mejor.get("orcid") or "").replace("https://orcid.org/", "")
        texto_actual = " ".join(h.get("hecho", "") for h in p["hechos"])
        import re
        m = re.search(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", texto_actual)
        if m and orcid_nuevo and m.group(0) != orcid_nuevo:
            conflictos.append({
                "id": p["id"], "nombre": p["nombre"],
                "conflicto": "ORCID distinto al ya registrado",
                "en_muestra": m.group(0), "en_openalex": orcid_nuevo,
                "resolucion": "se mantiene el de la muestra; requiere revisión humana"
            })

        propuestas.append({
            "id": p["id"],
            "nombre": p["nombre"],
            "openalex_id": mejor.get("id"),
            "openalex_nombre": mejor.get("display_name"),
            "orcid": orcid_nuevo or None,
            "works_count": mejor.get("works_count"),
            "cited_by_count": mejor.get("cited_by_count"),
            "instituciones": [i.get("display_name") for i in (mejor.get("last_known_institutions") or [])],
            "publicaciones_por_ano": {str(c["year"]): c["works_count"]
                                      for c in (mejor.get("counts_by_year") or [])
                                      if c.get("works_count")},
            "puntaje_match": pts,
            "razones_match": raz,
            "match_ambiguo": ambiguo,
            "afiliacion_no_coincide": any(r.startswith("OJO:") for r in raz),
            "candidatos_alternativos": [
                {"id": c.get("id"), "nombre": c.get("display_name"),
                 "orcid": c.get("orcid"), "works": c.get("works_count"), "puntaje": pp}
                for pp, _, c in evaluados[1:4]
            ],
            "confianza": "pendiente",
            "fuente_url": mejor.get("id"),
        })
        print("  %d/%d %-34s → %s (match %d%s)" % (
            i, len(personas), p["nombre"], mejor.get("display_name"), pts,
            ", AMBIGUO" if ambiguo else ""))
        time.sleep(0.2)

    hoy = datetime.date.today().isoformat()
    salida = {
        "generado": hoy,
        "fuente": "OpenAlex API (https://api.openalex.org)",
        "estado": "PROPUESTA — no aplicado a la muestra",
        "como_revisar": ("Cada entrada es una coincidencia PROPUESTA entre una persona de la "
                         "muestra y un autor de OpenAlex. Revisá 'razones_match' y, si "
                         "'match_ambiguo' es true, revisá 'candidatos_alternativos' antes de "
                         "aceptar. Nada de esto entra a la muestra hasta que una persona lo "
                         "apruebe."),
        "resumen": {"personas_revisadas": len(personas),
                    "propuestas": len(propuestas),
                    "ambiguas": sum(1 for x in propuestas if x["match_ambiguo"]),
                    "afiliacion_no_coincide": sum(1 for x in propuestas if x["afiliacion_no_coincide"]),
                    "sin_coincidencia": len(sin_match),
                    "conflictos": len(conflictos)},
        "propuestas": propuestas,
        "sin_coincidencia": sin_match,
        "conflictos": conflictos,
    }
    os.makedirs(SALIDA_DIR, exist_ok=True)
    ruta = os.path.join(SALIDA_DIR, "openalex-%s.json" % hoy)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)
    print("\n%s" % json.dumps(salida["resumen"], ensure_ascii=False))
    print("Escrito: %s" % os.path.relpath(ruta, RAIZ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
