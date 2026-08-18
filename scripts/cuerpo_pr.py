#!/usr/bin/env python3
"""Arma el cuerpo markdown del Pull Request de propuesta OpenAlex."""
import json, sys

ruta = sys.argv[1]
d = json.load(open(ruta, encoding="utf-8"))
r = d["resumen"]

print("Generado automáticamente por `scripts/enriquecer_openalex.py`.")
print()
print("**Esto es una propuesta, no un cambio aplicado.** No toca "
      "`data/sample/perfiles-muestra.json`. Nada entra a la muestra hasta que una persona lo apruebe.")
print()
print("## Resumen")
print()
print("| | |")
print("|---|---|")
for k, v in r.items():
    print("| %s | %s |" % (k.replace("_", " "), v))
print()

amb = [p for p in d["propuestas"] if p.get("match_ambiguo")]
afi = [p for p in d["propuestas"] if p.get("afiliacion_no_coincide")]
if amb:
    print("## Revisar con atención — coincidencia ambigua (%d)" % len(amb))
    print()
    for p in amb:
        alts = ", ".join("%s (%s)" % (a["nombre"], a["puntaje"]) for a in p["candidatos_alternativos"])
        print("- **%s** → `%s`. Alternativos: %s" % (p["nombre"], p["openalex_nombre"], alts or "—"))
    print()
if afi:
    print("## Revisar con atención — la afiliación no coincide (%d)" % len(afi))
    print()
    for p in afi:
        print("- **%s** → OpenAlex lo ubica en: %s" % (p["nombre"], ", ".join(p["instituciones"]) or "sin institución"))
    print()

print("## Cómo revisar")
print()
print("1. Abrí la pestaña **Files changed**.")
print("2. Por cada propuesta, mirá `razones_match`.")
print("3. Las dos secciones de arriba marcan lo que más riesgo tiene de ser otra persona.")
print("4. Si algo no cuadra, **cerrá el PR sin mergear** — no se pierde nada, el script se puede volver a correr.")
print("5. Si está bien, mergealo. La propuesta queda registrada, todavía como `\"confianza\": \"pendiente\"`.")
print()
print("## Lo que este PR NO hace")
print()
print("- No marca ningún hecho como `confirmado`.")
print("- No fusiona identidades automáticamente.")
print("- No modifica los datos que ve el sitio público.")
