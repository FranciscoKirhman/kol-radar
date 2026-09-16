# Tarea para ChatGPT — segunda ronda (sin adjuntos)

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
{
  "lote": 1,
  "tareas_incluidas": ["A"],
  "A": [
    {
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
      "otras_sedes": [{ "direccion": "…", "comuna": "…", "fuente_url": "https://…" }],
      "motivo_si_no_encontrada": "",
      "notas": ""
    }
  ],
  "B": [
    {
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
    }
  ],
  "D": [
    {
      "id": "myriam-campbell-bull",
      "resultado": "afiliacion_encontrada",
      "institucion": { "id_institucion": null, "nombre_oficial": "…", "ciudad": "…" },
      "tipo_vinculo": "afiliación",
      "fuente_url": "https://pubmed.ncbi.nlm.nih.gov/…",
      "cita_textual": "…",
      "fecha_de_la_fuente": "2021-05",
      "fecha_consulta": "2026-09-16",
      "notas": "Por qué es la misma persona"
    }
  ],
  "pendientes_para_el_proximo_lote": []
}
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

TAREA A · Instituciones pendientes (24)
Tres tipos de ítem:
- ubicar: no tenemos dirección. Encontrala en la ciudad indicada. La pista dice qué ya se probó.
- verificar: tenemos una dirección, pero dos fuentes no coinciden o no está claro que sea la misma institución. Resolvé lo que dice el motivo: confirmada si la dirección actual es correcta, corregida si es otra (con la nueva dirección y su fuente), no_encontrada si no hay evidencia suficiente. Explicá en notas qué te llevó a decidir.
- sede_medicina: universidades. Queremos la dirección de su Facultad o Escuela de Medicina en esa ciudad, desde el sitio oficial.
Formato: id | nombre | ciudad | tarea | motivo | dirección actual | fuente que tenemos
sochradioterapia | Sociedad Chilena de Radioterapia | Santiago | ubicar | Su página de contacto solo tiene un formulario. Probá el domicilio de la persona jurídica en el Registro de Empresas y Sociedades, o estatutos y actas publicados por la sociedad. | fuente que tenemos: https://pubmed.ncbi.nlm.nih.gov/39760579/
sim | Sociedad de Investigaciones Médicas (SIM) | Temuco | ubicar | Una patente municipal de Temuco confirma la sociedad pero no da dirección. Probá el Registro de Empresas y Sociedades o resoluciones municipales que publiquen el domicilio. | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Sociedad+de+Investigaciones+Medicas+Ltda+(SIM)
ciec | Centro Internacional de Estudios Clínicos (CIEC) | Santiago | ubicar | No se encontró sitio oficial. Probá el registro de prestadores de la Superintendencia de Salud y el Registro de Empresas y Sociedades. | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Centro+Internacional+de+Estudios+Clínicos+(CIEC)
crchile | Clinical Research Chile SpA | Valdivia | ubicar | Su sitio publica dos números distintos: Beauchef 683 y Beauchef 638 (Valdivia). El registro DEIS del Minsal tiene la 'Clínica Ramis' en Beauchef 683. Confirmá con otra fuente cuál es y si funciona dentro de esa clínica. | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Clinical+Research+Chile+SpA
itop | Instituto de Terapias Oncológicas Providencia | Providencia | ubicar | No se encontró sitio oficial. Probá la Superintendencia de Salud, el Registro de Empresas y Sociedades y publicaciones del instituto que den su dirección. | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Instituto+de+Terapias+Oncologicas+Providencia
hosp-carabineros | Hospital de Carabineros | Santiago | verificar | El sitio oficial dice Antonio Varas 2500 y el DEIS, Simón Bolívar 2200 (Ñuñoa). ¿Es el mismo recinto con dos accesos, o una de las dos está desactualizada? | actual: Antonio Varas 2500, Ñuñoa (según sitio_oficial) | fuente que tenemos: https://www.scielo.cl/scielo.php?script=sci_arttext&pid=S0034-98872016000200009
clinica-santa-maria | Clínica Santa María | Santiago | verificar | El sitio oficial dice Av. Santa María 0500 y el DEIS, Santa María 410 (Providencia). Confirmá cuál es la del edificio principal. | actual: Avenida Santa María 0500, Providencia (según openstreetmap) | fuente que tenemos: https://pubmed.ncbi.nlm.nih.gov/38320664/
hosp-puerto-montt | Hospital Puerto Montt | Puerto Montt | verificar | El Servicio de Salud dice Los Aromos 65 y el DEIS, Los Aromos 63. Confirmá el número. | actual: Calle Los Aromos 65, sector Cayenel, Puerto Montt (según sitio_oficial) | fuente que tenemos: https://www.scielo.cl/scielo.php?script=sci_arttext&pid=S0034-98872015000600009
inmunocel | Inmunocel | Santiago | verificar | Su sitio dice Av. Presidente Kennedy 5488, Vitacura, pero OpenStreetMap pone ese número en otra comuna. Confirmá la comuna con la Superintendencia de Salud u otra fuente oficial. | actual: Avenida Presidente Kennedy 5488, Torre Norte, oficinas 702-703, Vitacura (según sitio_oficial) | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Inmunocel
soc-cirujanos | Sociedad de Cirujanos de Chile | Santiago | verificar | En la muestra es 'Sociedad de Cirujanos de Chile'; la dirección vino del sitio de la 'Sociedad Chilena de Cirugía'. ¿Es la misma organización con otro nombre? Si no, buscá la dirección de la Sociedad de Cirujanos de Chile. | actual: Román Díaz 205, oficina 401, Providencia (según sitio_oficial) | fuente que tenemos: https://pubmed.ncbi.nlm.nih.gov/39760579/
centro-precision | Centro de Oncología de Precisión | Santiago | verificar | La dirección vino del Centro de Oncología de Precisión de la Universidad Mayor. Confirmá que es el mismo centro de la muestra (mirá la fuente que tenemos). | actual: Badajoz 130, Edificio Menor, Las Condes (según sitio_oficial) | fuente que tenemos: https://clinicaltrials.gov/study/NCT06890598
icos | Instituto Clínico Oncológico del Sur (ICOS) | Temuco | verificar | La dirección vino de Oncosur, que atiende 'en Clínica ICOS'. Confirmá con una fuente del propio ICOS (Instituto Clínico Oncológico del Sur) que esa es su sede. | actual: Lago Puyehue 01745, Temuco (según sitio_oficial) | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Instituto+Clinico+Oncologico+del+Sur
cic-vina | Centro de Investigaciones Clínicas Viña del Mar | Viña del Mar | verificar | El mapa lo ubica en el Hospital Clínico Viña del Mar (Limache 1741) porque ClinicalTrials.gov nombra esa sede. Buscá la dirección propia del centro de investigación; si funciona dentro del hospital, confirmalo con una fuente. | actual: Limache 1741, Viña del Mar (según openstreetmap) | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Centro+de+Investigaciones+Clínicas+Viña+del+Mar
redsalud | Clínica RedSalud | Santiago | verificar | ClinicalTrials.gov nombra 'Clinica Redsalud Vitacura'. Confirmá con el sitio oficial de RedSalud la dirección de esa clínica (hoy: Av. Tabancura 1185, según OpenStreetMap). | actual: Avenida Tabancura 1185, Vitacura (según openstreetmap) | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Clinica+Redsalud+Vitacura
bradford-hill | Bradford Hill Clinical Research Center | Santiago | verificar | El sitio oficial dice Palestina (ex Manzano) 343, Recoleta; el DEIS tiene un 'Laboratorio Clínico Bradford Hill' en Manzano 377. ¿Son dos recintos de la misma institución? ¿Cuál es el del centro de investigación? | actual: Palestina (ex Manzano) 343, 5.º piso, Recoleta (según sitio_oficial) | fuente que tenemos: https://pubmed.ncbi.nlm.nih.gov/41946650/
oncocentro | Oncocentro APYS | Viña del Mar | verificar | En la muestra es 'Oncocentro APYS'; la dirección vino de 'Oncocentro'. Confirmá que APYS es la misma institución. | actual: Avenida La Marina 1702, Viña del Mar (según sitio_oficial) | fuente que tenemos: https://clinicaltrials.gov/search?locStr=Chile&term=Oncocentro+Apys
uchile | Universidad de Chile | Santiago | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Santiago en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Avenida Libertador Bernardo O'Higgins 1058, Casa Central, Santiago (según sitio_oficial)
puc | Pontificia Universidad Católica de Chile | Santiago | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Santiago en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Avenida Libertador Bernardo O'Higgins 360, Santiago (según openstreetmap)
uandes | Universidad de los Andes | Santiago | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Santiago en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Avenida Monseñor Álvaro del Portillo 12455, Las Condes (según openstreetmap)
uautonoma | Universidad Autónoma de Chile | Talca | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Talca en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Avenida Canal de la Luz, Talca (según openstreetmap)
udec | Universidad de Concepción | Concepción | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Concepción en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Víctor Lamas 1290, Concepción (según openstreetmap)
utarapaca | Universidad de Tarapacá | Arica | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Arica en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: 18 de Septiembre 2222, Arica (según openstreetmap)
unab | Universidad Andrés Bello | Santiago | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Santiago en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Sazié 2212, Santiago (según openstreetmap)
uach | Universidad Austral de Chile | Valdivia | sede_medicina | Buscá la dirección de la Facultad o Escuela de Medicina en Valdivia en el sitio oficial. Si es otra, resultado corregida y la dirección actual va a otras_sedes; si es la misma, confirmada. | actual: Campus Isla Teja, sin número, Valdivia (según openstreetmap)

TAREA D · Personas sin institución (2)
Buscá la afiliación profesional publicada de cada persona, partiendo de la fuente indicada. Solo PubMed, SciELO, ClinicalTrials.gov o el sitio oficial de la institución. En notas, explicá por qué es la misma persona.
Formato: id | nombre | institución según nuestra muestra | fuente que ya tenemos
myriam-campbell-bull | Myriam Campbell Bull | Hospital Roberto Del Rio | https://clinicaltrials.gov/study/NCT01281735
mauricio-olivera | Mauricio Olivera | Hospital Santa Rosa de Molina | https://clinicaltrials.gov/study/NCT01774266

Empezá con el lote 1 de la tarea A.

---

MENSAJE 2 DE 2 — tarea B (mismas reglas y formato del mensaje 1)

TAREA B · Resolver sedes de ensayos (141)
Cada fila es un texto de sede tal como lo escribe ClinicalTrials.gov que no calzó con ninguna institución conocida. Ya sacamos los que son marcadores del patrocinador a simple vista. Abrí al menos una de las fichas de ClinicalTrials.gov de esa fila (https://clinicaltrials.gov/study/<NCT>), revisá la sección Locations en Chile y decidí:
- institucion_existente: es una de la lista E (por nombre, alias o razón social). Hace falta evidencia de que ese texto corresponde a esa institución, por ejemplo la razón social en su sitio oficial o en el Registro de Empresas y Sociedades.
- institucion_nueva: es una institución real que no está en la lista E. Entregá nombre oficial, dirección, comuna, ciudad, fuente y cita.
- marcador_patrocinador: no nombra una institución ("Research Site", "Site CL001", "Local Institution").
- no_resoluble: nombra algo, pero no hay evidencia suficiente para decir qué es.
Si el texto de la sede es el nombre de una persona (por ejemplo "Karol Ramírez"), marcá no_resoluble y no la busques: esta tarea no crea ni investiga personas.
En nct_verificados poné solo los NCT donde viste ese texto en la ficha.

Formato de la lista B: texto_sede (copialo idéntico) | hasta 3 NCT donde aparece | ciudades de esos ensayos según nuestra muestra
Instituto Oncologico | NCT00542308 NCT00574873 NCT00910910 | Reñaca / Santiago / Temuco
Health & Care SPA | NCT02366143 NCT02367794 NCT02657434 | Santiago
Instituto Oncologico Ltda. | NCT00849667 NCT01663727 NCT02003924 | Santiago
Rey y Oreilly Limitada ( Site 1048) | NCT03834493 NCT03834506 NCT03834519 | Santiago
CIDO SpA-Oncology ( Site 0302) | NCT06136650 NCT06353386 | Santiago
Centro Oncologico del Norte | NCT02889874 NCT05352672 | Antofagasta
Centro de Cancer Nuestra Senora de la Esperanza ( Site 1063) | NCT03635567 NCT04634877 | Santiago
Centro de Investigacion Clinica del Sur | NCT03395197 NCT06629779 | Araucania / La Serena
Clinica IRAM | NCT02885376 NCT05592938 | Santiago / Vitacura
Clinica UC San Carlos de Apoquindo | NCT05608291 NCT05730036 | Santiago
Clinica Vespucio | NCT03371017 NCT05415215 | Recoleta / Santiago
Faculty of Medicine, University of Chile | NCT06152367 NCT06556004 | Santiago
Instituto Oncologico Clinica Renaca | NCT00967616 NCT01989676 | Santiago
Instituto Oncologico, Clinica Renaca | NCT01903733 NCT01989676 | Reñaca / Santiago
Universidad de Concepción | NCT02788214 NCT03188406 | Concepción
ACEREY Centro de Investigación Clínica Oncológica | NCT04987203 | Santiago
Alejandra Martínez | NCT04948983 | Santiago
Barbara Burgos Mansilla | NCT06148077 | Temuco
CESFAM El Roble | NCT02376023 | Santiago
CESFAM Juan Pablo II | NCT02376023 | Santiago
CIDO SpA ( Site 0212) | NCT06997497 | Port Montt
CIDO SpA ( Site 1509) | NCT06305767 | Recoleta, Santiago
CIDO SpA-Oncology ( Site 0508) | NCT05226598 | Antofagasta
CIDO SpA-Oncology ( Site 0608) | NCT05116189 | Port Montt
CIDO SpA-Oncology ( Site 0707) | NCT04738487 | Antofagasta
CIDO SpA-Oncology ( Site 0708) | NCT07216703 | La Serena
CIDO SpA-Oncology ( Site 2106) | NCT04626479 | Santiago
CIDO SpA-Oncology ( Site 2256) | NCT04305054 | La Serena
CIDO SpA-Oncology ( Site 4106) | NCT04626518 | Santiago
Catholic University of Maule | NCT04116281 | Talca
Centro De Estudios Clínicos Suecia SpA | NCT05111626 | La Serena
Centro Investigacion Clinica Del Sur | NCT03729245 | Osorno
Centro Investigacion Clinica del Sur | NCT00974311 | Santiago
Centro Oncologico Antofagasta | NCT01523587 | Antofagasta
Centro Oncologico Antofagasta ( Site 0206) | NCT03553836 | Antofagasta
Centro Oncologico Antofagasta ( Site 0386) | NCT03829319 | Antofagasta
Centro Oncologico Antofagasta ( Site 0914) | NCT03142334 | Antofagasta
Centro Oncologico Antofagasta ( Site 2804) | NCT03740165 | Antofagasta
Centro Oncológico Antofagasta | NCT01566721 | Antofagasta
Centro Oncológico del Norte | NCT03104699 | Antofagasta
Centro de Cancer Nuestra Senora de la Esperanza ( Site 0065) | NCT04246177 | Santiago
Centro de Cancer Pontificie Universidad Catolica de Chile | NCT02425891 | Santiago
Centro de Especialidades Dermatologicas | NCT01241591 | Santiago
Centro de Estudios Clinicos In | NCT04987203 | Santiago
Centro de Estudios Oncologicos Santiago | NCT00022516 | Santiago
Centro de Estudios Oncologicos de Santiago (CEOS) Oncologia | NCT01663727 | Santiago
Centro de Investigacion y Desarrollo Oncologico | NCT06054555 | Estacion Central
Centro de Investigacion y desarrollo Oncologico SpA - CIDO SpA ( Site 0380) | NCT03829319 | Antofagasta
Centro de Investigacion y desarrollo Oncologico SpA - CIDO SpA ( Site 2808) | NCT03740165 | Antofagasta
Centro de Investigaciones ( Site 0511) | NCT06717347 | Concepción
Centro de Investigaciones Clinicas | NCT02003924 | Santiago
Centro de Investigaciones Clinicas de la Universidad Catolica | NCT07022483 | Concepción
Centro de Investigación Clínica del Sur | NCT04736199 | Providencia
Centro de Investigación Oncológica del Norte ( Site 0504) | NCT05226598 | Antofagasta
Centro de investigacion y desarrollo oncolgico Spa | NCT06252649 | Providencia
Cilnica Santa Maria | NCT00083304 | Providencia
Clinica CIDO | NCT05052801 | Santiago
Clinica Dermacross S.A. | NCT01163253 | Santiago
Clinica Dermovein S.A. | NCT01241591 | Santiago
Clinica Las Nieves | NCT00002823 | Santiago
Clinica Renaca | NCT00094653 | Independencia
Clinica Renaca - Gocchi | NCT00005062 | Santiago
Clínica MEDS La Dehesa ( Site 0509) | NCT07431827 | Las Condes
Clínica UC San Carlos de Apoquindo | NCT07076121 | Santiago
Clínica UC San Carlos de Apoquindo ( Site 0043) | NCT06428409 | Providencia
Clínica UC San Carlos de Apoquindo ( Site 0211) | NCT06997497 | Port Montt
Clínica UC San Carlos de Apoquindo ( Site 0305) | NCT05665595 | Antofagasta
Clínica UC San Carlos de Apoquindo-Hemato-Oncology ( Site 2402) | NCT05933577 | Santiago
Clínica Vespucio ( Site 0205) | NCT05064059 | La Serena
Clínica Vespucio-Hemato - Ocology ( Site 0607) | NCT05116189 | Port Montt
Corporacion Nacional del Cancer | NCT00078832 | Santiago
Corporacion de Beneficencia Osorno | NCT03729245 | Osorno
Corporación de Salud Municipal de Puente Alto | NCT03920098 | Santiago
Daniel Munoz | NCT03400709 | Santiago
Department of Pediatrics Hematology and Oncology, Hospital Roberto del Rio | NCT00411541 | Santiago
Department of Rehabilitation Sciences, Faculty of Medicine, Universidad de La Frontera. Temuco, Chile | NCT05690295 | Temuco
Department of Surgery, Clinical Hospital, University of Chile | NCT00935779 | Santiago
Departmento de Hemato-Oncologia | NCT00080340 | Santiago
Enroll SpA | NCT06252649 | Providencia
Facultad de medicina UC | NCT07131735 | Santiago
Fresenius Kabi Chile Therapia iv | NCT01989676 | Santiago
Fresenius Kabi Chile, Therapia i.v. | NCT02364999 | Santiago
Fundación Arturo Pérez López | NCT05215340 | Santiago
Health & Care Spa | NCT03296163 | Santiago
Health and Care Chile ( Site 0202) | NCT03066778 | Santiago
Health and Care Chile ( Site 0901) | NCT03142334 | Antofagasta
Hosp Regional de Concepcion | NCT03220230 | Arica
Hospital Amaral Carvalho | NCT02312258 | Santiago
Hospital Base de Arica | NCT03220230 | Arica
Hospital Base de Puerto Montt | NCT03220230 | Arica
Hospital Clinico Universidad Catolica de Chile | NCT00722137 | Santiago
Hospital Clínico de la Pontificia Univ. Católica de Chile | NCT04736199 | Providencia
Hospital DIPRECA | NCT00715637 | Santiago
Hospital Dirección de Previsión de Carabineros | NCT00949650 | Los Condes
Hospital FACH | NCT00080340 | Santiago
Hospital Hanga Roa | NCT02788214 | Concepción
Hospital Intercultural | NCT03188406 | Concepción
Hospital Luis Tisne Brousse | NCT02889874 | Antofagasta
Hospital Naval Almirante Nef | NCT01989676 | Santiago
Hospital Regional de La Serena ( Site 0907) | NCT03142334 | Antofagasta
Hospital Roberto Del Rio | NCT01281735 | Santiago
Hospital Roberto del Rio | NCT02303821 | Santiago
Hospital Roberto del Rio-Universidad de Chile | NCT03007147 | Santiago
Hospital Salvador | NCT06556004 | Santiago
Hospital San Jose | NCT00974311 | Santiago
Hospital San Pablo | NCT07593066 | Coquimbo
Hospital Santa Maria | NCT00715637 | Santiago
Hospital Santa Rosa de Molina | NCT01774266 | Molina
Hospital Santiago Oriente Dr. Luis Tisne Brousse | NCT00553410 | Peñalolén
Hospital de Curanilahue | NCT03188406 | Concepción
Hospital de Puerto Montt | NCT03188406 | Concepción
Hospital de Referencia de Salud Cordillera Unidad de Patología Mamaria | NCT02594371 | Santiago
Hospital de Victoria | NCT03188406 | Concepción
Hospital de Villarrica | NCT03188406 | Concepción
Hospital regional de Coyhaique | NCT07593066 | Coquimbo
ICER-Lab | NCT06766903 | Talcahuano
INTOP | NCT01358877 | Providencia
IRAM | NCT02594371 | Santiago
IRAM - Chile | NCT00553410 | Peñalolén
IRAM - Instituto de Radio Medicina | NCT02576574 | Santiago
Instituto Clinico Oncologico | NCT04604132 | Santiago
Instituto Nacional de Cancer | NCT00465491 | Santiago
Instituto de Radiomedicine | NCT00864331 | Santiago
Instituto de Salud Publica | NCT02326857 | Santiago
Instituto de Terapias Oncologicas | NCT00849667 | Santiago
Instituto de Tereplas Oncologicas Providencia INTOP | NCT01512199 | Providencia
Iram Cancer Research ( Site 0198) | NCT04221945 | Santiago
Iram Cancer Research ( Site 0909) | NCT03142334 | Antofagasta
Iram Cancer Research ( Site 2809) | NCT03740165 | Antofagasta
Karol Ramírez | NCT04821609 | Puente Alto
Medical Research Limited Society | NCT03433313 | Temuco
Meditek Ltda. | NCT04987203 | Santiago
Pontifica Universidad Catolica De Chile | NCT07291076 | Santiago
San Joaquín Medical Center, UCChristus Health Network | NCT07593066 | Coquimbo
Servicio de Oncologia-Hospital Clinico Unversidad de Chile | NCT00057720 | Independencia
Servicios Medicos Urumed ( Site 0405) | NCT04736706 | La Serena
Sociedad Medica Aren y Bachero Limitada ( Site 0207) | NCT03553836 | Antofagasta
Sociedad Medica Aren y Bachero Limitada ( Site 0426) | NCT03820986 | Santiago
UROMED | NCT04736199 | Providencia
Universidad Católica del Norte | NCT03220230 | Arica
Universidad de La Frontera | NCT06148077 | Temuco

LISTA E · Instituciones que ya existen (para institucion_existente)
Formato: id | nombre | ciudad
bradford-hill | Bradford Hill Clinical Research Center | Santiago
falp | Fundación Arturo López Pérez (FALP) | Santiago (Providencia)
torax | Instituto Nacional del Tórax | Santiago
james-lind | James Lind Centro de Investigación del Cáncer | Temuco
hosp-concepcion | Hospital Clínico Regional de Concepción | Concepción
hosp-puerto-montt | Hospital Puerto Montt | Puerto Montt
puc | Pontificia Universidad Católica de Chile | Santiago
k2-oncology | K2 Oncology | Santiago (Providencia)
centro-precision | Centro de Oncología de Precisión | Santiago
clinica-alemana | Clínica Alemana Santiago | Santiago
clinica-las-condes | Clínica Las Condes | Santiago
orlandi | Orlandi Oncología | Santiago
clinica-santa-maria | Clínica Santa María | Santiago
uandes | Universidad de los Andes | Santiago
ser-chile | Sociedad Chilena de Enfermedades Respiratorias | Santiago
sochradi | Sociedad Chilena de Radiología | Santiago
sochradioterapia | Sociedad Chilena de Radioterapia | Santiago
soc-cirujanos | Sociedad de Cirujanos de Chile | Santiago
uautonoma | Universidad Autónoma de Chile | Talca
uchile | Universidad de Chile | Santiago
uss | Universidad San Sebastián | Concepción
udec | Universidad de Concepción | Concepción
utarapaca | Universidad de Tarapacá | Arica
unab | Universidad Andrés Bello | Santiago
uach | Universidad Austral de Chile | Valdivia
hosp-uchile | Hospital Clínico Universidad de Chile | Santiago
hosp-carabineros | Hospital de Carabineros | Santiago
isp | Instituto de Salud Pública de Chile | Santiago
oncocentro | Oncocentro APYS | Viña del Mar
cic-vina | Centro de Investigaciones Clínicas Viña del Mar | Viña del Mar
saga | Centro de Estudios Clínicos SAGA | Santiago
oncovida | Oncovida | Santiago
inc | Instituto Nacional del Cáncer | Santiago
ic-la-serena | IC La Serena Research | La Serena
icos | Instituto Clínico Oncológico del Sur (ICOS) | Temuco
biocenter | Biocenter | Concepción
redsalud | Clínica RedSalud | Santiago
ucm | Clínica Universidad Católica del Maule | Talca
inmunocel | Inmunocel | Santiago
sim | Sociedad de Investigaciones Médicas (SIM) | Temuco
cecim | CeCim Biocinetic | Santiago
ciec | Centro Internacional de Estudios Clínicos (CIEC) | Santiago
clinica-puerto-montt | Clínica Puerto Montt | Port Montt
iceg | Icegclinic | Santiago
hosp-calvo-mackenna | Hospital Luis Calvo Mackenna | Santiago
hosp-van-buren | Hospital Carlos Van Buren | Valparaíso
hosp-san-borja | Hospital Clínico San Borja Arriarán | Santiago
hosp-sotero | Hospital Sótero del Río | Santiago
iram | Instituto de Radiomedicina (IRAM) | Santiago
hosp-militar | Hospital Militar de Santiago | Santiago
crchile | Clinical Research Chile SpA | Valdivia
hosp-salvador | Hospital del Salvador | Santiago
hosp-rancagua | Hospital Regional de Rancagua | Rancagua
itop | Instituto de Terapias Oncológicas Providencia | Providencia
clinica-davila | Clínica Dávila | Recoleta
hosp-barros-luco | Hospital Barros Luco Trudeau | Santiago
hosp-valdivia | Hospital Base de Valdivia | Valdivia
hosp-temuco | Hospital Hernán Henríquez Aravena | Temuco
hosp-fricke | Hospital Gustavo Fricke | Viña del Mar
hosp-talca | Hospital Regional de Talca | Talca
hosp-sjd | Hospital San Juan de Dios | Santiago

Seguí con los lotes de la tarea B, de a 40.
