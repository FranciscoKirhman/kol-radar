# Tarea para ChatGPT — tercera ronda (sin adjuntos)

Pegar en una conversación NUEVA, un mensaje a la vez. Después de cada lote, escribir "seguí".
Guardar cada respuesta como `respuesta_loteN_A.json` (o `_B`, `_C`) en `{{CARPETA}}/` y correr:
`python3 scripts/validar_respuesta_chatgpt.py {{CARPETA}}/respuesta_*.json`

---

MENSAJE 1 DE 3 — reglas, formato y tareas A y B

Vas a completar datos faltantes de KOL Radar, un mapa de especialistas, instituciones y ensayos clínicos de oncología en Chile construido solo con evidencia pública verificable. Lo usan profesionales de Medical Affairs para preparar territorios. Todo lo que entregues lo revisa una persona y lo pasa un validador automático antes de entrar. Un "no encontrado" honesto vale más que un dato plausible sin fuente. No hay archivos adjuntos: todos los datos de entrada están en estos mensajes. Usá la búsqueda web; si no podés navegar, decilo y no respondas de memoria.

REGLAS QUE NO SE NEGOCIAN
1. Nunca inventes datos: ni direcciones, comunas, coordenadas, nombres, NCT ni fechas. Si no tenés la URL exacta de donde sale un dato, el dato no existe: marcá no_encontrada / no_resoluble y explicá qué buscaste.
2. Cada dato lleva su fuente: URL exacta de la página (no el dominio), una cita textual de máximo 25 palabras copiada de esa página, y la fecha de consulta (AAAA-MM-DD).
3. Coordenadas: lat y lon van siempre en null. Las calculamos nosotros desde la dirección.
4. Fuentes permitidas: sitio oficial de la institución; Superintendencia de Salud (supersalud.gob.cl) y DEIS del Minsal (deis.minsal.cl, datos.gob.cl); Registro de Empresas y Sociedades (registrodeempresasysociedades.cl); municipios y servicios de salud; ClinicalTrials.gov, PubMed, SciELO; el buscador de estudios clínicos de la CIF (estudiosclinicos.cl); el ISP (ispch.gob.cl); los buscadores de ensayos de los propios laboratorios; Un Ensayo para Mí (unensayoparami.org); OpenStreetMap con la URL del objeto.
5. Fuentes prohibidas: LinkedIn; Google Maps (sirve para orientarse, nunca como fuente); acortadores de enlaces; Doctoralia y directorios con reseñas; ASCO, IASLC, WCLC.
6. Personas: no busques información sobre personas. Si un texto de sede es el nombre de una persona, solo vale una fuente del MISMO ensayo que nombre la institución de esa sede.
7. Nada de conexiones sin evidencia. Un código postal compartido, un apellido o una cercanía NO prueban que dos cosas sean la misma. Un vínculo inventado es peor que un ensayo sin sede.

CÓMO ENTREGAR
- Un lote por respuesta, de máximo 30 ítems y de una sola tarea. Numerá los lotes: "lote": 1, 2, 3…
- Orden: A, después B; con los mensajes 2 y 3, la C.
- La respuesta es solo un bloque de código JSON, sin texto antes ni después. Lo que haya que explicar va en "notas".
- Copiá id, texto_sede y nct idénticos a como aparecen en las listas.
- Al terminar un lote, esperá a que te escriba "seguí".

FORMATO EXACTO (omití las claves de las tareas que no vengan en el lote)
```json
{
  "lote": 1,
  "tareas_incluidas": ["A"],
  "A": [
    {
      "id": "ceos",
      "tarea": "ubicar",
      "resultado": "ubicada",
      "nombre_oficial": "Nombre tal como lo publica la fuente",
      "direccion": "Calle y número, oficina si corresponde",
      "comuna": "Providencia",
      "ciudad": "Santiago",
      "region": "Región Metropolitana de Santiago",
      "lat": null,
      "lon": null,
      "fuente_url": "https://sitio-oficial.cl/contacto",
      "fuente_tipo": "sitio_oficial",
      "cita_textual": "Máximo 25 palabras copiadas de la fuente, con la dirección",
      "fecha_consulta": "2026-09-30",
      "otras_sedes": [],
      "motivo_si_no_encontrada": "",
      "notas": ""
    }
  ],
  "B": [
    {
      "texto_sede": "Hospital Santa Maria",
      "resultado": "institucion_existente",
      "id_institucion": "id de la lista E",
      "institucion_nueva": null,
      "nct_verificados": ["NCT00715637"],
      "ciudad_en_clinicaltrials": "Santiago",
      "evidencia_url": "https://clinicaltrials.gov/study/NCT00715637",
      "evidencia_institucion_url": "https://… página que prueba a qué institución corresponde el texto",
      "cita_textual": "…",
      "fecha_consulta": "2026-09-30",
      "notas": ""
    }
  ],
  "C": [
    {
      "nct": "NCT01234567",
      "resultado": "sede_encontrada",
      "sedes": [
        {
          "resultado": "institucion_existente",
          "id_institucion": "id de la lista E",
          "institucion_nueva": null,
          "ciudad": "Santiago",
          "evidencia_url": "https://… página que nombra ESTE estudio y ESTE centro",
          "cita_textual": "…",
          "fecha_consulta": "2026-09-30"
        }
      ],
      "motivo_si_no_encontrada": "",
      "notas": ""
    }
  ],
  "pendientes_para_el_proximo_lote": []
}
```
"institucion_nueva" lleva los campos de ubicación de la tarea A: nombre_oficial, direccion, comuna, ciudad, region, lat, lon, fuente_url, fuente_tipo, cita_textual, fecha_consulta.

VALORES PERMITIDOS
- A.resultado: ubicada | no_encontrada
- B.resultado: institucion_existente | institucion_nueva | marcador_patrocinador | no_resoluble
- C.resultado: sede_encontrada | no_encontrada
- C.sedes[].resultado: institucion_existente | institucion_nueva
- fuente_tipo: sitio_oficial | superintendencia_salud | deis_minsal | openstreetmap | registro_empresas | otro

ANTES DE ENVIAR CADA LOTE, REVISÁ
- Cada URL abre la página exacta donde está el dato, y la cita está copiada de ahí.
- La comuna corresponde a la dirección, y la ciudad a la que pide la lista.
- En la tarea C, la página de evidencia nombra el estudio (NCT, código de protocolo o título) Y el centro.
- Lo que no pudiste verificar está como no_encontrada o no_resoluble, con el motivo.

TAREA A · Instituciones sin dirección ({{N_A}})
Encontrá la dirección de cada una en la ciudad indicada. La pista dice qué ya se probó y qué se sabe.
Formato: id | nombre | ciudad | pista
{{LISTA_A}}

TAREA B · Textos de sede sin resolver ({{N_B}})
Cada fila es un texto de sede tal como lo escribe ClinicalTrials.gov en Chile, que no calzó con ninguna institución conocida. Ya sacamos los marcadores obvios del patrocinador ("Site 122", "Exelixis Clinical Site #100"). Abrí la ficha del ensayo (https://clinicaltrials.gov/study/<NCT>), revisá Locations y decidí:
- institucion_existente: es una de la lista E. Hace falta evidencia de que ese texto corresponde a esa institución.
- institucion_nueva: es una institución real que no está en la lista E; entregá su ubicación con fuente.
- marcador_patrocinador: no nombra una institución ("Research Site", "Private Office").
- no_resoluble: nombra algo, pero no hay evidencia suficiente. Por ejemplo, "Hospital Amaral Carvalho" está en Brasil aunque la fuente lo declare en Chile.
Formato: texto_sede | apariciones | ciudad y código postal que declara ClinicalTrials.gov | NCT
{{LISTA_B}}

LISTA E · Instituciones que ya existen ({{N_E}}). Usá su id.
Formato: id | nombre | ciudad
{{LISTA_E}}

Empezá con el lote 1 de la tarea A.

---

MENSAJE 2 DE 3 — tarea C, primera parte (mismas reglas y formato del mensaje 1)

TAREA C · Ensayos sin ninguna sede identificada ({{N_C}} en total)
En estos ensayos ClinicalTrials.gov declara sitios en Chile pero oculta el nombre ("Research Site", "Novartis Investigative Site", "Local Institution"). Ya revisamos el buscador de la CIF, la planilla de inspecciones del ISP y el código postal de la sede. Buscá una fuente que nombre ESTE estudio (por NCT, código de protocolo o título exacto) y un centro chileno donde se hizo:
- el buscador de ensayos del laboratorio patrocinador (muchos listan los centros por país);
- la ficha del estudio en estudiosclinicos.cl o en Un Ensayo para Mí;
- sitios de centros de investigación chilenos que listen sus estudios;
- publicaciones del ensayo que listen centros o investigadores por país (a menudo en el apéndice o material suplementario), y comunicados de prensa;
- resoluciones del ISP o de comités de ética publicadas.
Un código postal, una ciudad o un investigador conocido NO bastan: la página tiene que nombrar el estudio y el centro. Si no hay, no_encontrada con lo que buscaste.
Formato: nct | patrocinador | código de protocolo | título | sedes enmascaradas en Chile (texto, ciudad, código postal)
{{LISTA_C1}}

Seguí en lotes de la tarea C hasta terminar esta parte.

---

MENSAJE 3 DE 3 — tarea C, segunda parte (mismas reglas y formato)

{{LISTA_C2}}

Seguí en lotes hasta terminar. Al final, mandá un último mensaje (no JSON) con cuántos ítems resolviste por tarea y cuáles fuentes te sirvieron más.
