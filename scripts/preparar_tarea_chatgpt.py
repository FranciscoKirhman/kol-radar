#!/usr/bin/env python3
"""
Arma el paquete de trabajo para un colaborador IA (ChatGPT) con lo que la muestra no resuelve.

Tres huecos, todos medidos sobre data/sample/perfiles-muestra.json:
  A. Instituciones sin ubicación, o con una ubicación de OpenStreetMap que hay que verificar.
  B. Sedes de ensayos que ClinicalTrials.gov nombra pero que no calzaron con ninguna institución:
     son la causa de que cientos de ensayos queden como nodos sueltos en el mapa.
  C. Ensayos sin ninguna conexión y sin sede nombrada (solo marcadores del patrocinador).
  D. Personas sin institución ligada.

No consulta nada en la red: solo cruza archivos del repo. Se vuelve a correr cuando se integren
respuestas, y el paquete sale más chico.

Salida: data/pending/tarea-chatgpt-<fecha>/  (PROMPT.md lo escribe a mano el equipo; este
script genera los CSV de entrada que el prompt referencia).

Uso:
    python3 scripts/preparar_tarea_chatgpt.py [carpeta-geolocalizacion-osm]
"""
import collections, csv, datetime, glob, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
HOY = datetime.date.today().isoformat()
SALIDA = os.path.join(RAIZ, "data", "pending", "tarea-chatgpt-" + HOY)


def escribir_csv(nombre, columnas, filas):
    ruta = os.path.join(SALIDA, nombre)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        w.writeheader()
        for fila in filas:
            w.writerow(fila)
    return len(filas)


def main():
    datos = json.load(open(MUESTRA, encoding="utf-8"))
    E, V = datos["entidades"], datos["vinculos"]
    by_id = {e["id"]: e for e in E}
    carpetas = sorted(glob.glob(os.path.join(RAIZ, "data", "pending", "geolocalizacion-osm-*")))
    osm_dir = sys.argv[1] if len(sys.argv) > 1 else (carpetas[-1] if carpetas else None)
    ubicadas = json.load(open(os.path.join(osm_dir, "instituciones_ubicadas.json"), encoding="utf-8")) if osm_dir else []
    sin_ubicar = json.load(open(os.path.join(osm_dir, "sin_ubicar.json"), encoding="utf-8")) if osm_dir else []
    os.makedirs(SALIDA, exist_ok=True)

    grado, con_inst = collections.Counter(), set()
    for v in V:
        grado[v["origen"]] += 1; grado[v["destino"]] += 1
        for a, b in ((v["origen"], v["destino"]), (v["destino"], v["origen"])):
            if by_id.get(b, {}).get("tipo") == "institucion":
                con_inst.add(a)

    # Referencia: las instituciones que ya existen, para que las sedes se resuelvan contra ellas.
    n_ref = escribir_csv("instituciones_existentes.csv", ["id", "nombre", "ciudad", "tipo_segun_muestra", "alias_en_la_fuente"], [
        {"id": e["id"], "nombre": e["nombre"], "ciudad": e.get("ciudad") or "", "tipo_segun_muestra": e.get("subtitulo") or "",
         "alias_en_la_fuente": " | ".join(sorted(set((a.split("( Site")[0].split("/ID#")[0]).strip() for a in (e.get("alias_en_la_fuente") or []))))[:400]}
        for e in E if e["tipo"] == "institucion"])

    # A. Instituciones: sin ubicar, y ubicadas con alguna bandera que exige mirarlas.
    filas_a = []
    for s in sin_ubicar:
        e = by_id[s["id"]]
        filas_a.append({"id": e["id"], "nombre": e["nombre"], "ciudad_en_la_muestra": e.get("ciudad") or "",
                        "tarea": "ubicar", "motivo": "OpenStreetMap no tiene un objeto con ese nombre en la ciudad",
                        "candidato_osm_url": "", "candidato_osm_direccion": ""})
    for u in ubicadas:
        banderas = []
        if u.get("match_ambiguo"): banderas.append("hay otra sede con el mismo nombre a más de 500 m")
        if not u.get("tipo_coherente", True): banderas.append("el tipo de objeto de OSM no calza con el tipo de institución")
        if u.get("comparte_objeto_osm_con"): banderas.append("otra institución quedó en el mismo punto")
        if banderas:
            filas_a.append({"id": u["id"], "nombre": u["nombre"], "ciudad_en_la_muestra": u["ciudad_en_la_muestra"] or "",
                            "tarea": "verificar", "motivo": "; ".join(banderas),
                            "candidato_osm_url": u["fuente_url"], "candidato_osm_direccion": u["direccion_osm"]})
    n_a = escribir_csv("A_instituciones.csv", ["id", "nombre", "ciudad_en_la_muestra", "tarea", "motivo", "candidato_osm_url", "candidato_osm_direccion"], filas_a)

    # B. Sedes nombradas por ClinicalTrials.gov que no calzaron con ninguna institución.
    por_texto = collections.OrderedDict()
    for e in E:
        if e["tipo"] != "ensayo_clinico":
            continue
        for texto in e.get("sedes_pendientes_resolucion") or []:
            r = por_texto.setdefault(texto, {"ncts": [], "ciudades": set()})
            nct = e["id"].upper()
            if nct not in r["ncts"]:
                r["ncts"].append(nct)
            if e.get("ciudad"):
                r["ciudades"].add(e["ciudad"].split(" (")[0])
    filas_b = [{"texto_sede": t, "apariciones": len(r["ncts"]), "ciudades_de_esos_ensayos": " | ".join(sorted(r["ciudades"])),
                "ncts": " ".join(r["ncts"][:6]),
                "urls_clinicaltrials": " ".join("https://clinicaltrials.gov/study/" + n for n in r["ncts"][:3])}
               for t, r in sorted(por_texto.items(), key=lambda kv: (-len(kv[1]["ncts"]), kv[0]))]
    n_b = escribir_csv("B_sedes_por_resolver.csv", ["texto_sede", "apariciones", "ciudades_de_esos_ensayos", "ncts", "urls_clinicaltrials"], filas_b)

    # C. Ensayos sueltos sin ninguna sede nombrada.
    filas_c = [{"nct": e["id"].upper(), "titulo": (e.get("titulo_fuente") or e["nombre"])[:160], "ciudad_en_la_muestra": e.get("ciudad") or "",
                "sitios_chile": e.get("sitios_chile") or "", "url_clinicaltrials": "https://clinicaltrials.gov/study/" + e["id"].upper()}
               for e in E if e["tipo"] == "ensayo_clinico" and grado[e["id"]] == 0 and not e.get("sedes_pendientes_resolucion")]
    n_c = escribir_csv("C_ensayos_sin_sede_nombrada.csv", ["nct", "titulo", "ciudad_en_la_muestra", "sitios_chile", "url_clinicaltrials"], filas_c)

    # D. Personas sin institución ligada.
    filas_d = [{"id": e["id"], "nombre": e["nombre"], "subtitulo_en_la_muestra": e.get("subtitulo") or "",
                "fuentes_en_la_muestra": " ".join(h.get("fuente_url") or "" for h in e.get("hechos", []))}
               for e in E if e["tipo"] == "persona" and e["id"] not in con_inst]
    n_d = escribir_csv("D_personas_sin_institucion.csv", ["id", "nombre", "subtitulo_en_la_muestra", "fuentes_en_la_muestra"], filas_d)

    resumen = {"fecha": HOY, "geolocalizacion_osm_usada": os.path.relpath(osm_dir, RAIZ) if osm_dir else None,
               "instituciones_existentes": n_ref, "A_instituciones": n_a, "B_sedes_por_resolver": n_b,
               "C_ensayos_sin_sede_nombrada": n_c, "D_personas_sin_institucion": n_d,
               "ensayos_sin_ninguna_conexion": sum(1 for e in E if e["tipo"] == "ensayo_clinico" and grado[e["id"]] == 0)}
    json.dump(resumen, open(os.path.join(SALIDA, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
