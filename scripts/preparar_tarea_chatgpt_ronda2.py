#!/usr/bin/env python3
"""
Segunda tarea para el colaborador IA: lo que quedó pendiente después de la primera ronda.

Qué cambió respecto de la primera (scripts/preparar_tarea_chatgpt.py):
  - La tarea C sale: scripts de ClinicalTrials.gov la resolvieron por API
    (data/pending/tarea-chatgpt-2026-09-15/C_revision_api_2026-09-15.json).
  - La tarea A ya no pide ubicar todo: pide lo que data/geo/ubicaciones-instituciones.json no pudo
    resolver o resolvió con dudas —instituciones sin dirección, fuentes que no coinciden, nombres
    que quizás no son la misma institución— y la sede de medicina de las universidades, que es la
    que importa en un mapa de especialistas y no la casa central.
  - La tarea B sale sin los textos que son marcadores del patrocinador a simple vista ("Site 122",
    "Exelixis Clinical Site #100"): se guardan en B_marcadores_descartados.csv con el patrón que los
    descartó, para que la revisión humana pueda discutirlo.
  - Una lección de la primera ronda: ChatGPT mandó dos versiones del mismo lote que se
    contradecían. El prompt ahora lo prohíbe explícitamente.

Escribe data/pending/tarea-chatgpt-2026-09-15-ronda2/ con los CSV que usa
scripts/validar_respuesta_chatgpt.py y PROMPT.md con todos los datos adentro (sin adjuntos).

Uso:
    python3 scripts/preparar_tarea_chatgpt_ronda2.py
"""
import csv, json, os, re, shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RONDA1 = os.path.join(RAIZ, "data", "pending", "tarea-chatgpt-2026-09-15")
SALIDA = os.path.join(RAIZ, "data", "pending", "tarea-chatgpt-2026-09-15-ronda2")
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
UBICACIONES = os.path.join(RAIZ, "data", "geo", "ubicaciones-instituciones.json")

MARCADOR = re.compile(r"investigat\w* site|research site|local institution|study site|clinical (study )?site|clincial|"
                      r"call cent|administrative office|^site\b|site reference|^chile$|^exelixis clinical|"
                      r"for additional information|^private office$|^research center$|^las condes$", re.I)

# Pistas por institución que no salen de los datos: lo que ya se probó y dónde conviene mirar.
PISTAS_UBICAR = {
    "sochradioterapia": "Su página de contacto solo tiene un formulario. Probá el domicilio de la persona jurídica en el Registro de Empresas y Sociedades, o estatutos y actas publicados por la sociedad.",
    "sim": "Una patente municipal de Temuco confirma la sociedad pero no da dirección. Probá el Registro de Empresas y Sociedades o resoluciones municipales que publiquen el domicilio.",
    "ciec": "No se encontró sitio oficial. Probá el registro de prestadores de la Superintendencia de Salud y el Registro de Empresas y Sociedades.",
    "crchile": "Su sitio publica dos números distintos: Beauchef 683 y Beauchef 638 (Valdivia). El registro DEIS del Minsal tiene la 'Clínica Ramis' en Beauchef 683. Confirmá con otra fuente cuál es y si funciona dentro de esa clínica.",
    "itop": "No se encontró sitio oficial. Probá la Superintendencia de Salud, el Registro de Empresas y Sociedades y publicaciones del instituto que den su dirección.",
}
VERIFICAR = {
    "hosp-carabineros": "El sitio oficial dice Antonio Varas 2500 y el DEIS, Simón Bolívar 2200 (Ñuñoa). ¿Es el mismo recinto con dos accesos, o una de las dos está desactualizada?",
    "clinica-santa-maria": "El sitio oficial dice Av. Santa María 0500 y el DEIS, Santa María 410 (Providencia). Confirmá cuál es la del edificio principal.",
    "hosp-puerto-montt": "El Servicio de Salud dice Los Aromos 65 y el DEIS, Los Aromos 63. Confirmá el número.",
    "inmunocel": "Su sitio dice Av. Presidente Kennedy 5488, Vitacura, pero OpenStreetMap pone ese número en otra comuna. Confirmá la comuna con la Superintendencia de Salud u otra fuente oficial.",
    "soc-cirujanos": "En la muestra es 'Sociedad de Cirujanos de Chile'; la dirección vino del sitio de la 'Sociedad Chilena de Cirugía'. ¿Es la misma organización con otro nombre? Si no, buscá la dirección de la Sociedad de Cirujanos de Chile.",
    "centro-precision": "La dirección vino del Centro de Oncología de Precisión de la Universidad Mayor. Confirmá que es el mismo centro de la muestra (mirá la fuente que tenemos).",
    "icos": "La dirección vino de Oncosur, que atiende 'en Clínica ICOS'. Confirmá con una fuente del propio ICOS (Instituto Clínico Oncológico del Sur) que esa es su sede.",
    "cic-vina": "El mapa lo ubica en el Hospital Clínico Viña del Mar (Limache 1741) porque ClinicalTrials.gov nombra esa sede. Buscá la dirección propia del centro de investigación; si funciona dentro del hospital, confirmalo con una fuente.",
    "redsalud": "ClinicalTrials.gov nombra 'Clinica Redsalud Vitacura'. Confirmá con el sitio oficial de RedSalud la dirección de esa clínica (hoy: Av. Tabancura 1185, según OpenStreetMap).",
    "bradford-hill": "El sitio oficial dice Palestina (ex Manzano) 343, Recoleta; el DEIS tiene un 'Laboratorio Clínico Bradford Hill' en Manzano 377. ¿Son dos recintos de la misma institución? ¿Cuál es el del centro de investigación?",
    "oncocentro": "En la muestra es 'Oncocentro APYS'; la dirección vino de 'Oncocentro'. Confirmá que APYS es la misma institución.",
}
# Para un mapa de especialistas importa dónde está medicina, no la casa central.
UNIVERSIDADES = ["uchile", "puc", "uandes", "uautonoma", "udec", "utarapaca", "unab", "uach"]


def escribir_csv(nombre, columnas, filas):
    with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)
    return len(filas)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    muestra = json.load(open(MUESTRA, encoding="utf-8"))
    by_id = {e["id"]: e for e in muestra["entidades"]}
    ub = json.load(open(UBICACIONES, encoding="utf-8"))

    def actual(iid):
        u = ub["instituciones"].get(iid)
        if not u:
            return ""
        p = u["principal"]
        return "%s, %s (según %s)" % (p["direccion"], p["comuna"], p["fuente_direccion"]["tipo"])

    def fuente_muestra(iid):
        for h in by_id[iid].get("hechos") or []:
            if h.get("fuente_url"):
                return h["fuente_url"]
        return ""

    filas_a = []
    for iid, pista in PISTAS_UBICAR.items():
        assert iid in ub["sin_ubicar"], iid
        filas_a.append({"id": iid, "nombre": by_id[iid]["nombre"], "ciudad_en_la_muestra": by_id[iid].get("ciudad") or "",
                        "tarea": "ubicar", "motivo": pista, "direccion_actual": "", "fuente_en_la_muestra": fuente_muestra(iid)})
    for iid, motivo in VERIFICAR.items():
        filas_a.append({"id": iid, "nombre": by_id[iid]["nombre"], "ciudad_en_la_muestra": by_id[iid].get("ciudad") or "",
                        "tarea": "verificar", "motivo": motivo, "direccion_actual": actual(iid), "fuente_en_la_muestra": fuente_muestra(iid)})
    for iid in UNIVERSIDADES:
        ciudad = (by_id[iid].get("ciudad") or "").split(" (")[0]
        filas_a.append({"id": iid, "nombre": by_id[iid]["nombre"], "ciudad_en_la_muestra": by_id[iid].get("ciudad") or "",
                        "tarea": "sede_medicina",
                        "motivo": "Buscá la dirección de la Facultad o Escuela de Medicina en %s en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada." % ciudad,
                        "direccion_actual": actual(iid), "fuente_en_la_muestra": ""})
    columnas_a = ["id", "nombre", "ciudad_en_la_muestra", "tarea", "motivo", "direccion_actual", "fuente_en_la_muestra"]
    n_a = escribir_csv("A_instituciones.csv", columnas_a, filas_a)

    b = list(csv.DictReader(open(os.path.join(RONDA1, "B_sedes_por_resolver.csv"), encoding="utf-8")))
    descartadas = [dict(r, patron=MARCADOR.search(r["texto_sede"]).group(0)) for r in b if MARCADOR.search(r["texto_sede"])]
    quedan = [r for r in b if not MARCADOR.search(r["texto_sede"])]
    escribir_csv("B_marcadores_descartados.csv", list(b[0].keys()) + ["patron"], descartadas)
    escribir_csv("B_sedes_por_resolver.csv", list(b[0].keys()), quedan)
    for nombre in ("D_personas_sin_institucion.csv", "instituciones_existentes.csv"):
        shutil.copy(os.path.join(RONDA1, nombre), os.path.join(SALIDA, nombre))
    d = list(csv.DictReader(open(os.path.join(SALIDA, "D_personas_sin_institucion.csv"), encoding="utf-8")))
    e = list(csv.DictReader(open(os.path.join(SALIDA, "instituciones_existentes.csv"), encoding="utf-8")))

    lineas_a = []
    for r in filas_a:
        extra = []
        if r["direccion_actual"]:
            extra.append("actual: " + r["direccion_actual"])
        if r["fuente_en_la_muestra"]:
            extra.append("fuente que tenemos: " + r["fuente_en_la_muestra"])
        lineas_a.append("%s | %s | %s | %s | %s%s" % (r["id"], r["nombre"], r["ciudad_en_la_muestra"], r["tarea"], r["motivo"],
                                                    (" | " + " | ".join(extra)) if extra else ""))
    lineas_d = ["%s | %s | %s | %s" % (r["id"], r["nombre"], r["subtitulo_en_la_muestra"], r["fuentes_en_la_muestra"]) for r in d]
    lineas_b = ["%s | %s | %s" % (r["texto_sede"], " ".join(r["ncts"].split()[:3]), " / ".join(r["ciudades_de_esos_ensayos"].split(" | ")))
                for r in quedan]
    lineas_e = ["%s | %s | %s" % (r["id"], r["nombre"], r["ciudad"]) for r in e]

    prompt = PROMPT.format(n_a=n_a, lista_a="\n".join(lineas_a), n_d=len(d), lista_d="\n".join(lineas_d),
                           n_b=len(quedan), lista_b="\n".join(lineas_b), lista_e="\n".join(lineas_e))
    open(os.path.join(SALIDA, "PROMPT.md"), "w", encoding="utf-8").write(prompt)
    resumen = {"A_instituciones": n_a, "A_ubicar": len(PISTAS_UBICAR), "A_verificar": len(VERIFICAR), "A_sede_medicina": len(UNIVERSIDADES),
               "B_sedes_por_resolver": len(quedan), "B_marcadores_descartados": len(descartadas), "D_personas_sin_institucion": len(d)}
    json.dump(resumen, open(os.path.join(SALIDA, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False))


PROMPT = '''# Tarea para ChatGPT — segunda ronda (sin adjuntos)

Pegar en una conversación NUEVA, en orden. Después de cada lote, escribir "seguí".
Guardar cada respuesta como `respuesta_loteN_A.json` (o `_B`, `_D`) en esta carpeta y correr:
`python3 scripts/validar_respuesta_chatgpt.py data/pending/tarea-chatgpt-2026-09-15-ronda2/respuesta_*.json`

---

MENSAJE 1 DE 2 — reglas, formato y tareas A y D

Vas a completar datos faltantes de KOL Radar, un mapa de especialistas, instituciones y ensayos clínicos de oncología en Chile construido solo con evidencia pública verificable. Lo usan Medical Science Liaisons para preparar territorios. Todo lo que entregues lo revisa una persona y lo pasa un validador automático antes de entrar. Un "no encontrado" honesto vale más que un dato plausible sin fuente. No hay archivos adjuntos: todos los datos de entrada están en estos mensajes. Usá la búsqueda web; si no podés navegar, decilo y no respondas de memoria.

REGLAS QUE NO SE NEGOCIAN
1. Nunca inventes datos: ni direcciones, comunas, coordenadas, nombres, NCT ni fechas. Si no tenés la URL exacta de donde sale un dato, el dato no existe: marcá no_encontrada / no_resoluble y explicá qué buscaste.
2. Cada dato lleva su fuente: URL exacta de la página (no el dominio), una cita textual de máximo 25 palabras copiada de esa página, y la fecha de consulta (AAAA-MM-DD).
3. Coordenadas: lat y lon van siempre en null. Las calculamos nosotros desde la dirección.
4. Fuentes permitidas, en este orden: sitio oficial de la institución (contacto, sedes, "dónde estamos"); Superintendencia de Salud (supersalud.gob.cl) y DEIS del Minsal (deis.minsal.cl, datos.gob.cl); Registro de Empresas y Sociedades (registrodeempresasysociedades.cl) para razones sociales y domicilios; ClinicalTrials.gov, PubMed, SciELO; OpenStreetMap con la URL del objeto (openstreetmap.org/node|way|relation/<id>).
5. Fuentes prohibidas: LinkedIn; Google Maps (sirve para orientarse, nunca como fuente); acortadores de enlaces; Doctoralia y directorios con reseñas; ASCO, IASLC, WCLC.
6. Personas: nunca asumas que dos registros son la misma persona por el apellido; los homónimos son comunes en Chile. Solo cuenta un ORCID, o nombre completo más institución coincidentes en la misma fuente. Solo información profesional pública.
7. Instituciones con varias sedes: la dirección tiene que ser la de la sede en la ciudad indicada. Las demás sedes van en otras_sedes, cada una con su fuente_url.
8. Nada de conexiones sin evidencia. Un vínculo inventado es peor que un nodo desconectado.

CÓMO ENTREGAR
- Un lote por respuesta, de máximo 40 ítems y de una sola tarea. Numerá los lotes: "lote": 1, 2, 3…
- Orden: primero A, después D; con el mensaje 2, la B. No hagas tareas que no estén en estos mensajes.
- Una sola versión de cada lote. Si después descubrís un error en un lote ya enviado, reenviá solo ese ítem corregido en el lote siguiente y explicá la corrección en "notas".
- La respuesta es solo un bloque de código JSON, sin texto antes ni después. Lo que haya que explicar va en "notas" o en "pendientes_para_el_proximo_lote".
- Copiá id y texto_sede idénticos a como aparecen en las listas.
- En "notas", cuando describas lo que dice una página, copiá el texto literal entre comillas; no lo resumas.
- Al terminar un lote, esperá a que te escriba "seguí".

FORMATO EXACTO (omití las claves de las tareas que no vengan en el lote)
```json
{{
  "lote": 1,
  "tareas_incluidas": ["A"],
  "A": [
    {{
      "id": "hosp-carabineros",
      "tarea": "verificar",
      "resultado": "confirmada",
      "nombre_oficial": "Nombre tal como lo publica la fuente",
      "direccion": "Calle y número, oficina si corresponde",
      "comuna": "Ñuñoa",
      "ciudad": "Santiago",
      "region": "Región Metropolitana de Santiago",
      "lat": null,
      "lon": null,
      "fuente_url": "https://sitio-oficial.cl/contacto",
      "fuente_tipo": "sitio_oficial",
      "cita_textual": "Máximo 25 palabras copiadas de la fuente, con la dirección",
      "fecha_consulta": "2026-09-16",
      "otras_sedes": [{{ "direccion": "…", "comuna": "…", "fuente_url": "https://…" }}],
      "motivo_si_no_encontrada": "",
      "notas": ""
    }}
  ],
  "B": [
    {{
      "texto_sede": "Instituto Oncologico Ltda.",
      "resultado": "institucion_existente",
      "id_institucion": "id de la lista E",
      "institucion_nueva": null,
      "nct_verificados": ["NCT00849667"],
      "ciudad_en_clinicaltrials": "Santiago",
      "evidencia_url": "https://clinicaltrials.gov/study/NCT00849667",
      "evidencia_institucion_url": "https://… página que prueba a qué institución corresponde el texto",
      "cita_textual": "…",
      "fecha_consulta": "2026-09-16",
      "notas": ""
    }}
  ],
  "D": [
    {{
      "id": "myriam-campbell-bull",
      "resultado": "afiliacion_encontrada",
      "institucion": {{ "id_institucion": null, "nombre_oficial": "…", "ciudad": "…" }},
      "tipo_vinculo": "afiliación",
      "fuente_url": "https://pubmed.ncbi.nlm.nih.gov/…",
      "cita_textual": "…",
      "fecha_de_la_fuente": "2021-05",
      "fecha_consulta": "2026-09-16",
      "notas": "Por qué es la misma persona"
    }}
  ],
  "pendientes_para_el_proximo_lote": []
}}
```
Cuando corresponda, "institucion_nueva" lleva los mismos campos de ubicación de la tarea A: nombre_oficial, direccion, comuna, ciudad, region, lat, lon, fuente_url, fuente_tipo, cita_textual, fecha_consulta.

VALORES PERMITIDOS
- A.resultado: ubicada | confirmada | corregida | no_encontrada
- B.resultado: institucion_existente | institucion_nueva | marcador_patrocinador | no_resoluble
- D.resultado: afiliacion_encontrada | no_encontrada
- fuente_tipo: sitio_oficial | superintendencia_salud | deis_minsal | openstreetmap | registro_empresas | otro
- D.tipo_vinculo: afiliación | investigador de sitio

ANTES DE ENVIAR CADA LOTE, REVISÁ
- Cada URL abre la página exacta donde está el dato, y la cita está copiada de ahí.
- La comuna corresponde a la dirección, y la ciudad a la que pide la lista.
- lat y lon están en null.
- Ningún vínculo ni identidad se apoya solo en que los nombres se parecen.
- Lo que no pudiste verificar está como no_encontrada o no_resoluble, con el motivo.

TAREA A · Instituciones pendientes ({n_a})
Tres tipos de ítem:
- ubicar: no tenemos dirección. Encontrala en la ciudad indicada. La pista dice qué ya se probó.
- verificar: tenemos una dirección, pero dos fuentes no coinciden o no está claro que sea la misma institución. Resolvé lo que dice el motivo: confirmada si la dirección actual es correcta, corregida si es otra (con la nueva dirección y su fuente), no_encontrada si no hay evidencia suficiente. Explicá en notas qué te llevó a decidir.
- sede_medicina: universidades. Queremos la dirección de su Facultad o Escuela de Medicina en esa ciudad, desde el sitio oficial.
Formato: id | nombre | ciudad | tarea | motivo | dirección actual | fuente que tenemos
{lista_a}

TAREA D · Personas sin institución ({n_d})
Buscá la afiliación profesional publicada de cada persona, partiendo de la fuente indicada. Solo PubMed, SciELO, ClinicalTrials.gov o el sitio oficial de la institución. En notas, explicá por qué es la misma persona.
Formato: id | nombre | institución según nuestra muestra | fuente que ya tenemos
{lista_d}

Empezá con el lote 1 de la tarea A.

---

MENSAJE 2 DE 2 — tarea B (mismas reglas y formato del mensaje 1)

TAREA B · Resolver sedes de ensayos ({n_b})
Cada fila es un texto de sede tal como lo escribe ClinicalTrials.gov que no calzó con ninguna institución conocida. Ya sacamos los que son marcadores del patrocinador a simple vista. Abrí al menos una de las fichas de ClinicalTrials.gov de esa fila (https://clinicaltrials.gov/study/<NCT>), revisá la sección Locations en Chile y decidí:
- institucion_existente: es una de la lista E (por nombre, alias o razón social). Hace falta evidencia de que ese texto corresponde a esa institución, por ejemplo la razón social en su sitio oficial o en el Registro de Empresas y Sociedades.
- institucion_nueva: es una institución real que no está en la lista E. Entregá nombre oficial, dirección, comuna, ciudad, fuente y cita.
- marcador_patrocinador: no nombra una institución ("Research Site", "Site CL001", "Local Institution").
- no_resoluble: nombra algo, pero no hay evidencia suficiente para decir qué es.
Si el texto de la sede es el nombre de una persona (por ejemplo "Karol Ramírez"), marcá no_resoluble y no la busques: esta tarea no crea ni investiga personas.
En nct_verificados poné solo los NCT donde viste ese texto en la ficha.

Formato de la lista B: texto_sede (copialo idéntico) | hasta 3 NCT donde aparece | ciudades de esos ensayos según nuestra muestra
{lista_b}

LISTA E · Instituciones que ya existen (para institucion_existente)
Formato: id | nombre | ciudad
{lista_e}

Seguí con los lotes de la tarea B, de a 40.
'''

if __name__ == "__main__":
    main()
