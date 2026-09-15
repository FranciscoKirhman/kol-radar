# Prompt completo para ChatGPT (sin adjuntos)

Pegar en una misma conversación, en orden. Después de cada lote, escribir "seguí".

---

MENSAJE 1 DE 3 — reglas, formato y tareas A y D

Vas a completar datos faltantes de KOL Radar, un mapa de especialistas, instituciones y ensayos clínicos de oncología en Chile construido solo con evidencia pública verificable. Lo usan Medical Science Liaisons para preparar territorios. Todo lo que entregues lo revisa una persona y lo pasa un validador automático antes de entrar. Un "no encontrado" honesto vale más que un dato plausible sin fuente. No hay archivos adjuntos: todos los datos de entrada están en estos mensajes. Usá la búsqueda web; si no podés navegar, decilo y no respondas de memoria.

REGLAS QUE NO SE NEGOCIAN
1. Nunca inventes datos: ni direcciones, comunas, coordenadas, nombres, NCT ni fechas. Si no tenés la URL exacta de donde sale un dato, el dato no existe: marcá no_encontrada / no_resoluble y explicá qué buscaste.
2. Cada dato lleva su fuente: URL exacta de la página (no el dominio), una cita textual de máximo 25 palabras copiada de esa página, y la fecha de consulta (AAAA-MM-DD).
3. Coordenadas solo si la fuente las publica (un objeto de OpenStreetMap o el listado de establecimientos del DEIS del Minsal). Si solo tenés la dirección, lat y lon van en null. Nunca estimes coordenadas ni las copies de Google Maps.
4. Fuentes permitidas, en este orden: sitio oficial de la institución (contacto, sedes, "dónde estamos"); Superintendencia de Salud (supersalud.gob.cl) y DEIS del Minsal (deis.minsal.cl); Registro de Empresas y Sociedades (registrodeempresasysociedades.cl) para razones sociales; ClinicalTrials.gov, PubMed, SciELO; OpenStreetMap con la URL del objeto (openstreetmap.org/node|way|relation/<id>).
5. Fuentes prohibidas: LinkedIn; Google Maps (sirve para orientarse, nunca como fuente ni para coordenadas); acortadores de enlaces; Doctoralia y directorios con reseñas; ASCO, IASLC, WCLC.
6. Personas: nunca asumas que dos registros son la misma persona por el apellido; los homónimos son comunes en Chile. Solo cuenta un ORCID, o nombre completo más institución coincidentes en la misma fuente. Solo información profesional pública.
7. Instituciones con varias sedes: la dirección tiene que ser la de la sede en la ciudad indicada. Si la fuente solo muestra la casa matriz u oficina administrativa, decilo en notas y listá las otras sedes en otras_sedes.
8. Nada de conexiones sin evidencia. El objetivo es que no queden ensayos sueltos en el mapa, pero un vínculo inventado es peor que un nodo desconectado.

CÓMO ENTREGAR
- Un lote por respuesta, de máximo 40 ítems y de una sola tarea. Numerá los lotes: "lote": 1, 2, 3…
- Orden: primero A, después D; con el mensaje 2 la B, con el mensaje 3 la C.
- La respuesta es solo un bloque de código JSON, sin texto antes ni después. Lo que haya que explicar va en "notas" o en "pendientes_para_el_proximo_lote".
- Copiá id, texto_sede y nct idénticos a como aparecen en las listas.
- Al terminar un lote, esperá a que te escriba "seguí".

FORMATO EXACTO (omití las claves de las tareas que no vengan en el lote)
```json
{
  "lote": 1,
  "tareas_incluidas": ["A"],
  "A": [
    {
      "id": "bradford-hill",
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
      "fecha_consulta": "2026-09-15",
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
      "fecha_consulta": "2026-09-15",
      "notas": ""
    }
  ],
  "C": [
    {
      "nct": "NCT00034125",
      "resultado": "sedes_nombradas",
      "sedes": [
        { "texto_en_clinicaltrials": "…", "ciudad": "Santiago", "resultado": "institucion_existente", "id_institucion": "…", "institucion_nueva": null }
      ],
      "evidencia_url": "https://clinicaltrials.gov/study/NCT00034125",
      "fecha_consulta": "2026-09-15",
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
      "fecha_consulta": "2026-09-15",
      "notas": "Por qué es la misma persona"
    }
  ],
  "pendientes_para_el_proximo_lote": []
}
```
Cuando corresponda, "institucion_nueva" lleva los mismos campos de ubicación de la tarea A: nombre_oficial, direccion, comuna, ciudad, region, lat, lon, fuente_url, fuente_tipo, cita_textual, fecha_consulta.

VALORES PERMITIDOS
- A.resultado: ubicada | confirmada | corregida | no_encontrada
- Resultado de una sede (B y cada sede de C): institucion_existente | institucion_nueva | marcador_patrocinador | no_resoluble
- C.resultado: sedes_nombradas | solo_marcadores | sin_sedes_en_chile
- D.resultado: afiliacion_encontrada | no_encontrada
- fuente_tipo: sitio_oficial | superintendencia_salud | deis_minsal | openstreetmap | registro_empresas | otro
- D.tipo_vinculo: afiliación | investigador de sitio

ANTES DE ENVIAR CADA LOTE, REVISÁ
- Cada URL abre la página exacta donde está el dato, y la cita está copiada de ahí.
- La comuna corresponde a la dirección, y la ciudad a la que pide la lista.
- No hay coordenadas que la fuente no publique.
- Ningún vínculo se apoya solo en que los nombres se parecen.
- Lo que no pudiste verificar está como no encontrado o no resoluble, con el motivo.

TAREA A · Ubicar o verificar instituciones (36)
- tarea = ubicar: encontrá la dirección de la sede en la ciudad indicada.
- tarea = verificar: trae un candidato de OpenStreetMap que tiene otra sede con el mismo nombre a más de 500 m. Confirmá que es la sede correcta (confirmada) o corregilo con la dirección correcta (corregida).
- Las sociedades científicas pueden no tener sede física: en ese caso no_encontrada, con el motivo.
Formato de la lista: id | nombre | ciudad | tarea [| candidato | motivo]
bradford-hill | Bradford Hill Clinical Research Center | Santiago | ubicar
james-lind | James Lind Centro de Investigación del Cáncer | Temuco | ubicar
hosp-concepcion | Hospital Clínico Regional de Concepción | Concepción | ubicar
hosp-puerto-montt | Hospital Puerto Montt | Puerto Montt | ubicar
k2-oncology | K2 Oncology | Santiago (Providencia) | ubicar
centro-precision | Centro de Oncología de Precisión | Santiago | ubicar
orlandi | Orlandi Oncología | Santiago | ubicar
ser-chile | Sociedad Chilena de Enfermedades Respiratorias | Santiago | ubicar
sochradi | Sociedad Chilena de Radiología | Santiago | ubicar
sochradioterapia | Sociedad Chilena de Radioterapia | Santiago | ubicar
soc-cirujanos | Sociedad de Cirujanos de Chile | Santiago | ubicar
uchile | Universidad de Chile | Santiago | ubicar
hosp-uchile | Hospital Clínico Universidad de Chile | Santiago | ubicar
hosp-carabineros | Hospital de Carabineros | Santiago | ubicar
oncocentro | Oncocentro APYS | Viña del Mar | ubicar
saga | Centro de Estudios Clínicos SAGA | Santiago | ubicar
oncovida | Oncovida | Santiago | ubicar
ic-la-serena | IC La Serena Research | La Serena | ubicar
icos | Instituto Clínico Oncológico del Sur (ICOS) | Temuco | ubicar
biocenter | Biocenter | Concepción | ubicar
inmunocel | Inmunocel | Santiago | ubicar
sim | Sociedad de Investigaciones Médicas (SIM) | Temuco | ubicar
cecim | CeCim Biocinetic | Santiago | ubicar
ciec | Centro Internacional de Estudios Clínicos (CIEC) | Santiago | ubicar
iceg | Icegclinic | Santiago | ubicar
hosp-sotero | Hospital Sótero del Río | Santiago | ubicar
iram | Instituto de Radiomedicina (IRAM) | Santiago | ubicar
crchile | Clinical Research Chile SpA | Valdivia | ubicar
itop | Instituto de Terapias Oncológicas Providencia | Providencia | ubicar
hosp-valdivia | Hospital Base de Valdivia | Valdivia | ubicar
clinica-alemana | Clínica Alemana Santiago | Santiago | verificar | candidato: https://www.openstreetmap.org/relation/13179277 | motivo: otra sede con el mismo nombre a más de 500 m
clinica-santa-maria | Clínica Santa María | Santiago | verificar | candidato: https://www.openstreetmap.org/way/37356304 | motivo: otra sede con el mismo nombre a más de 500 m
uss | Universidad San Sebastián | Concepción | verificar | candidato: https://www.openstreetmap.org/way/114254370 | motivo: otra sede con el mismo nombre a más de 500 m
unab | Universidad Andrés Bello | Santiago | verificar | candidato: https://www.openstreetmap.org/way/625289635 | motivo: otra sede con el mismo nombre a más de 500 m
uach | Universidad Austral de Chile | Valdivia | verificar | candidato: https://www.openstreetmap.org/way/136115984 | motivo: otra sede con el mismo nombre a más de 500 m
isp | Instituto de Salud Pública de Chile | Santiago | verificar | candidato: https://www.openstreetmap.org/way/152907976 | motivo: otra sede con el mismo nombre a más de 500 m

TAREA D · Personas sin institución (2)
Buscá la afiliación profesional publicada de cada persona, partiendo de la fuente indicada. Solo PubMed, SciELO, ClinicalTrials.gov o el sitio oficial de la institución. En notas, explicá por qué es la misma persona.
Formato: id | nombre | institución según nuestra muestra | fuente que ya tenemos
myriam-campbell-bull | Myriam Campbell Bull | Hospital Roberto Del Rio | https://clinicaltrials.gov/study/NCT01281735
mauricio-olivera | Mauricio Olivera | Hospital Santa Rosa de Molina | https://clinicaltrials.gov/study/NCT01774266

Empezá con el lote 1 de la tarea A.

---

MENSAJE 2 DE 3 — tarea B (mismas reglas y formato del mensaje 1)

TAREA B · Resolver sedes de ensayos (181)
Cada fila es un texto de sede tal como lo escribe ClinicalTrials.gov que no calzó con ninguna institución conocida. Abrí al menos una de las fichas de ClinicalTrials.gov de esa fila (https://clinicaltrials.gov/study/<NCT>), revisá la sección Locations en Chile y decidí:
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
Site 122 | NCT01030783 NCT01076010 | La Reina / Santiago
Site 123 | NCT01030783 NCT01076010 | La Reina / Santiago
Universidad de Concepción | NCT02788214 NCT03188406 | Concepción
ACEREY Centro de Investigación Clínica Oncológica | NCT04987203 | Santiago
Administrative office | NCT01989676 | Santiago
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
Chile | NCT00072462 | Santiago
Cilnica Santa Maria | NCT00083304 | Providencia
Clincial Study Site | NCT03088540 | Recoleta
Clinica CIDO | NCT05052801 | Santiago
Clinica Dermacross S.A. | NCT01163253 | Santiago
Clinica Dermovein S.A. | NCT01241591 | Santiago
Clinica Las Nieves | NCT00002823 | Santiago
Clinica Renaca | NCT00094653 | Independencia
Clinica Renaca - Gocchi | NCT00005062 | Santiago
Clinical Study Site | NCT03088540 | Recoleta
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
Exelixis Clinical #263 | NCT04446117 | Providencia
Exelixis Clinical Site #100 | NCT03937219 | Santiago
Exelixis Clinical Site #106 | NCT05678673 | Providencia
Exelixis Clinical Site #107 | NCT05678673 | Providencia
Exelixis Clinical Site #108 | NCT05678673 | Providencia
Exelixis Clinical Site #109 | NCT05678673 | Providencia
Exelixis Clinical Site #113 | NCT04446117 | Providencia
Exelixis Clinical Site #119 | NCT04446117 | Providencia
Exelixis Clinical Site #139 | NCT04446117 | Providencia
Exelixis Clinical Site #142 | NCT04446117 | Providencia
Exelixis Clinical Site #148 | NCT04446117 | Providencia
Exelixis Clinical Site #247 | NCT04446117 | Providencia
Exelixis Clinical Site #53 | NCT05678673 | Providencia
Exelixis Clinical Site #85 | NCT03937219 | Santiago
Exelixis Clinical Site #90 | NCT04446117 | Providencia
Exelixis Clinical Site #91 | NCT03937219 | Santiago
Facultad de medicina UC | NCT07131735 | Santiago
For additional information regarding investigative sites for this trial, contact 1-877-CTLILLY (1-877-285-4559, 1-317-615-4559) Mon-Fri from 9 AM to 5 PM Eastern Time (UTC/ GMT - 5 hours, EST), or speak with your personal physician | NCT00191620 | Santiago
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
Las Condes | NCT00081796 | Santiago
Medical Research Limited Society | NCT03433313 | Temuco
Meditek Ltda. | NCT04987203 | Santiago
Pontifica Universidad Catolica De Chile | NCT07291076 | Santiago
Private Office | NCT00920816 | Providencia
Research Center | NCT00370383 | Santiago
SITE | NCT02853604 | Santiago
San Joaquín Medical Center, UCChristus Health Network | NCT07593066 | Coquimbo
Sandoz Investigational Site 1 | NCT06587451 | Santiago
Servicio de Oncologia-Hospital Clinico Unversidad de Chile | NCT00057720 | Independencia
Servicios Medicos Urumed ( Site 0405) | NCT04736706 | La Serena
Site 121 | NCT01030783 | La Reina
Site 25 | NCT06525220 | Antofagasta
Site 26 | NCT06525220 | Antofagasta
Site 29 | NCT06525220 | Antofagasta
Site 32 | NCT06525220 | Antofagasta
Site 34 | NCT06525220 | Antofagasta
Site 38 | NCT06525220 | Antofagasta
Site 40 | NCT06525220 | Antofagasta
Site Reference ID/Investigator# 36964 | NCT01009593 | Temuco
Site Reference ID/Investigator# 36967 | NCT01009593 | Temuco
Sociedad Medica Aren y Bachero Limitada ( Site 0207) | NCT03553836 | Antofagasta
Sociedad Medica Aren y Bachero Limitada ( Site 0426) | NCT03820986 | Santiago
Tanvex Investigational Site 4001 | NCT03556358 | Temuco
Tanvex Investigational Site 4002 | NCT03556358 | Temuco
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

---

MENSAJE 3 DE 3 — tarea C (mismas reglas y formato del mensaje 1; la lista E está en el mensaje 2)

TAREA C · Ensayos sin ninguna sede nombrada (226)
En nuestra muestra estos ensayos no tienen ninguna institución y quedan como nodos sueltos. Abrí https://clinicaltrials.gov/study/<NCT> y revisá sus ubicaciones en Chile:
- sedes_nombradas: hay sedes con nombre real. Resolvé cada una igual que en la tarea B, dentro de "sedes".
- solo_marcadores: solo aparecen marcadores del patrocinador.
- sin_sedes_en_chile: la ficha ya no declara ubicaciones en Chile.

Formato de la lista C: NCT | ciudad según nuestra muestra
NCT00034125 | Las Condes (+1 sitios)
NCT00034268 | Las Condes
NCT00043927 | Santiago
NCT00056407 | Santiago (+1 sitios)
NCT00073307 | Santiago
NCT00073528 | Santiago (+1 sitios)
NCT00075270 | Santiago (+2 sitios)
NCT00082433 | Santiago
NCT00089999 | Santiago (+2 sitios)
NCT00099437 | Antofagasta (+2 sitios)
NCT00105443 | Santiago (+2 sitios)
NCT00113607 | Reneca (+1 sitios)
NCT00117598 | Providencia
NCT00124566 | Santiago
NCT00130897 | Santiago
NCT00148798 | Antofagasta (+1 sitios)
NCT00154102 | Santiago-Las Condes (+1 sitios)
NCT00171340 | Santiago
NCT00174655 | Providencia Santiago
NCT00174837 | Santiago
NCT00174863 | Santiago
NCT00300885 | Santiago (+3 sitios)
NCT00305188 | Santiago
NCT00324155 | Santiago
NCT00334282 | Santiago (+2 sitios)
NCT00338247 | Santiago
NCT00338286 | Arica (+4 sitios)
NCT00373113 | Temuco
NCT00374322 | Santiago (+3 sitios)
NCT00387764 | Santiago (+1 sitios)
NCT00417079 | Santiago
NCT00417209 | Santiago
NCT00418236 | Santiago
NCT00428090 | Providencia / Santiago (+3 sitios)
NCT00457392 | Independencia (+2 sitios)
NCT00457691 | Santiago (+1 sitios)
NCT00474786 | Providencia
NCT00481247 | Santiago
NCT00490139 | Santiago (+7 sitios)
NCT00519285 | Providencia Santiago
NCT00532155 | Santiago
NCT00556322 | Santiago
NCT00556712 | Santiago
NCT00558103 | Santiago (+2 sitios)
NCT00560235 | Providencia
NCT00561470 | Santiago (+4 sitios)
NCT00574275 | Santiago
NCT00625664 | Santiago
NCT00626548 | La Serena (+3 sitios)
NCT00673049 | Independencia
NCT00678535 | Reñaca (+3 sitios)
NCT00680901 | Santiago (+3 sitios)
NCT00681122 | Santiago (+1 sitios)
NCT00692770 | Reñaca (+1 sitios)
NCT00806819 | Jardin Del Mar, Renaca (+3 sitios)
NCT00858364 | Reñaca (+4 sitios)
NCT00861614 | Santiago (+4 sitios)
NCT00863746 | Santiago (+1 sitios)
NCT00883909 | Santiago
NCT00901901 | Santiago (+1 sitios)
NCT00917384 | Concepción (+2 sitios)
NCT00949910 | Santiago
NCT01013740 | Santiago (+2 sitios)
NCT01057810 | Santiago (+2 sitios)
NCT01077154 | Santiago (+2 sitios)
NCT01170663 | Providencia (+1 sitios)
NCT01193244 | Las Condes (+3 sitios)
NCT01204749 | Temuco (+1 sitios)
NCT01234311 | Santiago (+2 sitios)
NCT01235962 | Santiago (+1 sitios)
NCT01244191 | Santiago (+3 sitios)
NCT01263886 | Santiago (+3 sitios)
NCT01285609 | Santiago (+2 sitios)
NCT01308580 | Santiago (+3 sitios)
NCT01412957 | Temuco (+1 sitios)
NCT01437566 | Santiago (+3 sitios)
NCT01450696 | Santiago (+2 sitios)
NCT01450761 | Santiago (+2 sitios)
NCT01456325 | Santiago (+2 sitios)
NCT01482962 | Concepción (+1 sitios)
NCT01500720 | Santiago (+1 sitios)
NCT01516736 | Temuco
NCT01571284 | Santiago (+1 sitios)
NCT01642004 | Antofagasta (+4 sitios)
NCT01646021 | Temuco
NCT01673867 | Santiago (+3 sitios)
NCT01715285 | Santiago
NCT01721772 | Santiago (+2 sitios)
NCT01724021 | Santiago (+2 sitios)
NCT01865747 | Santiago
NCT01901146 | Santiago (+1 sitios)
NCT01933932 | Santiago (+5 sitios)
NCT01977651 | Santiago (+3 sitios)
NCT02016534 | Santiago (+2 sitios)
NCT02023697 | Santiago
NCT02119663 | Santiago (+1 sitios)
NCT02125461 | Santiago (+2 sitios)
NCT02162667 | Santiago (+1 sitios)
NCT02231749 | Santiago (+3 sitios)
NCT02279862 | Recoleta (+2 sitios)
NCT02300831 | Santiago
NCT02352948 | Santiago (+2 sitios)
NCT02367040 | Temuco
NCT02369874 | Temuco
NCT02386800 | Santiago (+2 sitios)
NCT02437318 | Santiago (+2 sitios)
NCT02472964 | Santiago (+1 sitios)
NCT02475681 | Santiago (+1 sitios)
NCT02477826 | Santiago (+2 sitios)
NCT02481830 | Recoleta
NCT02542293 | Santiago (+6 sitios)
NCT02559583 | Santiago
NCT02588261 | Santiago (+2 sitios)
NCT02677896 | Providencia (+5 sitios)
NCT02752074 | Santiago (+1 sitios)
NCT02809053 | Temuco
NCT02823574 | Santiago
NCT02869789 | Santiago (+1 sitios)
NCT02872116 | Independencia (+4 sitios)
NCT02941926 | Santiago
NCT02960022 | IX Region (+5 sitios)
NCT02967692 | Santiago (+2 sitios)
NCT03056755 | Santiago (+2 sitios)
NCT03138512 | La Serena (+4 sitios)
NCT03141177 | Santiago
NCT03200717 | Santiago (+1 sitios)
NCT03215706 | Santiago (+2 sitios)
NCT03338790 | Santiago (+1 sitios)
NCT03377361 | Santiago (+1 sitios)
NCT03383458 | Santiago (+3 sitios)
NCT03447769 | Santiago (+1 sitios)
NCT03470922 | Santiago
NCT03504397 | Providencia (+3 sitios)
NCT03519256 | Santiago (+1 sitios)
NCT03626545 | Santiago
NCT03631199 | Santiago (+1 sitios)
NCT03635983 | Recoleta (+1 sitios)
NCT03661320 | Santiago (+3 sitios)
NCT03662659 | Rancagua (+3 sitios)
NCT03704077 | Santiago (+1 sitios)
NCT03721289 | Santiago
NCT03725475 | Santiago
NCT03732677 | Antofagasta (+5 sitios)
NCT03732820 | Santiago (+3 sitios)
NCT03778229 | Santiago (+2 sitios)
NCT03798626 | Santiago
NCT03800134 | Santiago (+3 sitios)
NCT03830866 | Antofagasta (+6 sitios)
NCT03873402 | Independencia (+4 sitios)
NCT03930953 | Recoleta (+4 sitios)
NCT03980314 | Independencia (+3 sitios)
NCT04008030 | Independencia (+2 sitios)
NCT04026412 | Santiago (+1 sitios)
NCT04035486 | Santiago (+3 sitios)
NCT04039607 | La Serena (+7 sitios)
NCT04078152 | Santiago
NCT04100018 | Providencia (+4 sitios)
NCT04109066 | Antofagasta (+5 sitios)
NCT04109391 | Temuco (+1 sitios)
NCT04149574 | La Serena (+2 sitios)
NCT04154956 | Santiago (+4 sitios)
NCT04266301 | Viña del Mar
NCT04351555 | Las Condes (+2 sitios)
NCT04475939 | Santiago (+2 sitios)
NCT04478266 | La Serena (+8 sitios)
NCT04493853 | Santiago (+4 sitios)
NCT04524689 | Santiago (+3 sitios)
NCT04567615 | Santiago (+2 sitios)
NCT04581824 | Santiago (+1 sitios)
NCT04613596 | Santiago (+2 sitios)
NCT04623775 | Santiago (+2 sitios)
NCT04659603 | Santiago (+2 sitios)
NCT04711252 | Concepción (+3 sitios)
NCT04742192 | Santiago (+1 sitios)
NCT04810078 | Santiago (+4 sitios)
NCT04884360 | Santiago (+4 sitios)
NCT04913220 | Antofagasta (+5 sitios)
NCT04914897 | Santaigo (+4 sitios)
NCT04915755 | Santiago (+2 sitios)
NCT04943900 | Santiago (+2 sitios)
NCT04960709 | Santiago (+1 sitios)
NCT04964908 | Providencia
NCT05002569 | Santiago (+2 sitios)
NCT05005273 | Santiago (+2 sitios)
NCT05043090 | Providencia (+3 sitios)
NCT05091437 | Antofagasta (+1 sitios)
NCT05104567 | Santiago
NCT05128773 | Santiago
NCT05179603 | Santiago (+3 sitios)
NCT05211895 | Las Condes (+6 sitios)
NCT05261399 | Santiago
NCT05328908 | Santiago (+1 sitios)
NCT05329766 | Las Condes (+3 sitios)
NCT05348577 | Santiago (+3 sitios)
NCT05405166 | Santiago (+5 sitios)
NCT05519085 | Santiago (+2 sitios)
NCT05568095 | La Florida (+5 sitios)
NCT05577715 | Independencia (+3 sitios)
NCT05613088 | Santiago (+2 sitios)
NCT05625399 | Port Montt (+8 sitios)
NCT05669989 | Temuco
NCT05774951 | Concepción (+8 sitios)
NCT05952557 | Concepción (+8 sitios)
NCT06090539 | Antofagasta (+2 sitios)
NCT06101134 | Concepción (+1 sitios)
NCT06120491 | Concepción (+7 sitios)
NCT06232707 | Santiago (+3 sitios)
NCT06356129 | Santiago (+5 sitios)
NCT06380751 | Providencia (+4 sitios)
NCT06425302 | Santiago (+1 sitios)
NCT06646276 | Santiago (+4 sitios)
NCT06764485 | Santiago (+3 sitios)
NCT06764875 | Port Montt (+6 sitios)
NCT06767462 | Santiago (+1 sitios)
NCT06868277 | Conception (+3 sitios)
NCT06901531 | Las Condes (+1 sitios)
NCT06911502 | Santiago (+2 sitios)
NCT06946797 | Santiago
NCT06952803 | Concepción (+2 sitios)
NCT07063745 | Antofagasta (+3 sitios)
NCT07100080 | Santiago (+2 sitios)
NCT07218809 | Port Montt (+8 sitios)
NCT07221149 | Santiago (+2 sitios)
NCT07221357 | Recoleta (+2 sitios)
NCT07476326 | Providencia (+3 sitios)
NCT07680764 | Santiago (+2 sitios)

Seguí con los lotes de la tarea C, de a 40.
