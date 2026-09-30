# Tarea para ChatGPT — tercera ronda (sin adjuntos)

Pegar en una conversación NUEVA, un mensaje a la vez. Después de cada lote, escribir "seguí".
Guardar cada respuesta como `respuesta_loteN_A.json` (o `_B`, `_C`) en `data/pending/tarea-chatgpt-2026-09-29-ronda3/` y correr:
`python3 scripts/validar_respuesta_chatgpt.py data/pending/tarea-chatgpt-2026-09-29-ronda3/respuesta_*.json`

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

TAREA A · Instituciones sin dirección (16)
Encontrá la dirección de cada una en la ciudad indicada. La pista dice qué ya se probó y qué se sabe.
Formato: id | nombre | ciudad | pista
aren-bachero | Sociedad Médica Arén y Bachero Limitada | Santiago | ClinicalTrials.gov declara el código postal 8420383, el mismo del edificio de Bradford Hill y CIEC. Confirmá con una fuente propia (sitio, Superintendencia, registro de empresas).
benef-osorno | Corporación de Beneficencia Osorno | Osorno | ClinicalTrials.gov la declara en Osorno con código postal 5311092. No está en el DEIS con ese nombre: puede ser la persona jurídica dueña de una clínica de Osorno. Buscá qué establecimiento opera y su dirección.
ced-vina | Centro de Especialidades Dermatológicas | Viña del Mar | ClinicalTrials.gov lo declara en Viña del Mar sin código postal útil.
ceos | Centro de Estudios Oncológicos de Santiago (CEOS) | Santiago | ClinicalTrials.gov escribe 'Centro de Estudios Oncologicos de Santiago (CEOS) Oncologia' con código postal 7500921, el de la Fundación Arturo López Pérez. ¿Funciona dentro de FALP?
cesfam-juan-pablo-ii | CESFAM Juan Pablo II | Santiago | Hay varios CESFAM Juan Pablo II (La Pintana —Red de Salud UC CHRISTUS—, San Bernardo, Padre Hurtado, entre otros). ClinicalTrials.gov lo ubica en 'Santiago' con código postal 8831695. Decidí cuál es con una fuente que lo diga (el registro del ensayo, la red de salud, el municipio); no por cercanía del código.
cics-temuco | Centro de Investigación Clínica del Sur | Temuco | ClinicalTrials.gov lo declara en Temuco con códigos postales 4781156 y 4810371.
clinica-las-nieves | Clínica Las Nieves | Santiago | ClinicalTrials.gov la declara en Santiago, sin código postal. No está en el DEIS con ese nombre.
cormun-puente-alto | Corporación de Salud Municipal de Puente Alto | Puente Alto | Es la corporación municipal de salud, no un establecimiento. ClinicalTrials.gov declara el código postal 8210269. Buscá su domicilio en su sitio oficial o en el del municipio.
crchile | Clinical Research Chile SpA | Valdivia | Su sitio publica dos números incompatibles en la misma calle: Beauchef 683 y Beauchef 638 (Valdivia). ClinicalTrials.gov declara el código postal 5110683. El DEIS tiene la 'Clínica Ramis' en Beauchef 683. Confirmá con otra fuente cuál es y si funciona dentro de esa clínica.
dermovein | Clínica Dermovein | Santiago | ClinicalTrials.gov declara 'Clinica Dermovein S.A.' en Santiago con código postal 7640881, que también usa Clínica Dermacross.
enroll | Enroll SpA | Providencia | ClinicalTrials.gov lo declara en Providencia con código postal 7500587.
health-care-chile | Health & Care SpA | Santiago | ClinicalTrials.gov escribe 'Health and Care Chile' con código postal 7500006 (Providencia), que también usa Orlandi Oncología.
icer-lab | ICER-Lab | Talcahuano | ClinicalTrials.gov lo declara en Talcahuano, sin código postal.
meditek | Meditek Ltda. | Santiago | ClinicalTrials.gov declara el código postal 8420383, el mismo del edificio de Bradford Hill y CIEC (Palestina, ex Manzano, 343, Recoleta). Confirmá si funciona ahí con una fuente propia.
rey-oreilly | Rey y O'Reilly Limitada | Temuco | ClinicalTrials.gov escribe 'Rey y Oreilly Limitada' en Temuco con código postal 4810148, el mismo que usa CIDO. ¿Es la razón social de CIDO u otro centro?
sochradioterapia | Sociedad Chilena de Radioterapia | Santiago | Su página de contacto (https://www.sochira.cl/contacto) solo tiene un formulario. Probá el domicilio de la persona jurídica en el Registro de Empresas y Sociedades o en estatutos publicados.

TAREA B · Textos de sede sin resolver (16)
Cada fila es un texto de sede tal como lo escribe ClinicalTrials.gov en Chile, que no calzó con ninguna institución conocida. Ya sacamos los marcadores obvios del patrocinador ("Site 122", "Exelixis Clinical Site #100"). Abrí la ficha del ensayo (https://clinicaltrials.gov/study/<NCT>), revisá Locations y decidí:
- institucion_existente: es una de la lista E. Hace falta evidencia de que ese texto corresponde a esa institución.
- institucion_nueva: es una institución real que no está en la lista E; entregá su ubicación con fuente.
- marcador_patrocinador: no nombra una institución ("Research Site", "Private Office").
- no_resoluble: nombra algo, pero no hay evidencia suficiente. Por ejemplo, "Hospital Amaral Carvalho" está en Brasil aunque la fuente lo declare en Chile.
Formato: texto_sede | apariciones | ciudad y código postal que declara ClinicalTrials.gov | NCT
Administrative office | 1 | Temuco 4810561 | NCT01989676
Alejandra Martínez | 1 | Santiago sANTIAGO | NCT04948983
Barbara Burgos Mansilla | 1 | Temuco | NCT06148077
Centro de Estudios Clinicos In | 1 | Santiago 8420383 | NCT04987203
Clincial Study Site | 1 | Viña del Mar | NCT03088540
Daniel Munoz | 1 | Santiago 7160166 | NCT03400709
Departmento de Hemato-Oncologia | 1 | Santiago | NCT00080340
Fresenius Kabi Chile Therapia iv | 1 | Santiago 7780050 | NCT01989676
Fresenius Kabi Chile, Therapia i.v. | 1 | Santiago 8940575 | NCT02364999
Hospital Amaral Carvalho | 1 | Temuco 4800827 | NCT02312258
Hospital Santa Maria | 1 | Santiago 7530204 | NCT00715637
Hospital de Referencia de Salud Cordillera Unidad de Patología Mamaria | 1 | Santiago | NCT02594371
Karol Ramírez | 1 | Puente Alto | NCT04821609
Las Condes | 1 | Santiago | NCT00081796
Private Office | 1 | Santiago RM 8360160 | NCT00920816
Research Center | 1 | Santiago | NCT00370383

LISTA E · Instituciones que ya existen (110). Usá su id.
Formato: id | nombre | ciudad
aren-bachero | Sociedad Médica Arén y Bachero Limitada | Santiago
benef-osorno | Corporación de Beneficencia Osorno | Osorno
biocenter | Biocenter | Concepción
bradford-hill | Bradford Hill Clinical Research Center | Santiago
cec-suecia | Centro de Estudios Clínicos Suecia | Santiago
cecim | CeCim Biocinetic | Santiago
ced-vina | Centro de Especialidades Dermatológicas | Viña del Mar
centro-cancer-uc | Centro de Cáncer Nuestra Señora de la Esperanza (UC CHRISTUS) | Santiago
centro-oncologico-norte | Centro Oncológico del Norte | Antofagasta
centro-precision | Centro de Oncología de Precisión | Santiago
ceos | Centro de Estudios Oncológicos de Santiago (CEOS) | Santiago
cesfam-el-roble | CESFAM El Roble | La Pintana
cesfam-juan-pablo-ii | CESFAM Juan Pablo II | Santiago
cic-vina | Centro de Investigaciones Clínicas Viña del Mar | Viña del Mar
cics-temuco | Centro de Investigación Clínica del Sur | Temuco
cido | CIDO — Centro de Investigación y Desarrollo Oncológico | Temuco
ciec | Centro Internacional de Estudios Clínicos (CIEC) | Santiago
clinica-alemana | Clínica Alemana Santiago | Santiago
clinica-alemana-temuco | Clínica Alemana de Temuco | Temuco
clinica-davila | Clínica Dávila | Recoleta
clinica-davila-vespucio | Clínica Dávila Vespucio (ex Clínica Vespucio) | La Florida
clinica-las-condes | Clínica Las Condes | Santiago
clinica-las-nieves | Clínica Las Nieves | Santiago
clinica-puerto-montt | Clínica Puerto Montt | Port Montt
clinica-santa-maria | Clínica Santa María | Santiago
clinica-uc-san-carlos | Clínica UC CHRISTUS San Carlos de Apoquindo | Las Condes
conac | Corporación Nacional del Cáncer (CONAC) | Santiago
cormun-puente-alto | Corporación de Salud Municipal de Puente Alto | Puente Alto
crchile | Clinical Research Chile SpA | Valdivia
dermacross | Clínica Dermacross | Santiago
dermovein | Clínica Dermovein | Santiago
enroll | Enroll SpA | Providencia
falp | Fundación Arturo López Pérez (FALP) | Santiago (Providencia)
health-care-chile | Health & Care SpA | Santiago
hosp-arica | Hospital Regional Dr. Juan Noé Crevani | Arica
hosp-barros-luco | Hospital Barros Luco Trudeau | Santiago
hosp-calvo-mackenna | Hospital Luis Calvo Mackenna | Santiago
hosp-carabineros | Hospital de Carabineros | Santiago
hosp-clinico-uc | Hospital Clínico UC CHRISTUS | Santiago
hosp-concepcion | Hospital Clínico Regional de Concepción | Concepción
hosp-coyhaique | Hospital Regional de Coyhaique | Coyhaique
hosp-curanilahue | Hospital Provincial Dr. Rafael Avaria (Curanilahue) | Curanilahue
hosp-dipreca | Hospital DIPRECA | Santiago
hosp-fach | Hospital FACh | Santiago
hosp-fricke | Hospital Gustavo Fricke | Viña del Mar
hosp-hanga-roa | Hospital Hanga Roa | Isla de Pascua
hosp-la-serena | Hospital San Juan de Dios de La Serena | La Serena
hosp-militar | Hospital Militar de Santiago | Santiago
hosp-molina | Hospital Santa Rosa de Molina | Molina
hosp-naval-vina | Hospital Naval Almirante Nef | Viña del Mar
hosp-nueva-imperial | Hospital Intercultural de Nueva Imperial | Nueva Imperial
hosp-puerto-montt | Hospital Puerto Montt | Puerto Montt
hosp-rancagua | Hospital Regional de Rancagua | Rancagua
hosp-roberto-del-rio | Hospital Clínico de Niños Dr. Roberto del Río | Santiago
hosp-salvador | Hospital del Salvador | Santiago
hosp-san-borja | Hospital Clínico San Borja Arriarán | Santiago
hosp-san-jose | Complejo Hospitalario San José | Santiago
hosp-san-pablo-coquimbo | Hospital San Pablo de Coquimbo | Coquimbo
hosp-sjd | Hospital San Juan de Dios | Santiago
hosp-sotero | Hospital Sótero del Río | Santiago
hosp-talca | Hospital Regional de Talca | Talca
hosp-temuco | Hospital Hernán Henríquez Aravena | Temuco
hosp-tisne | Hospital Santiago Oriente Dr. Luis Tisné Brousse | Santiago
hosp-uchile | Hospital Clínico Universidad de Chile | Santiago
hosp-valdivia | Hospital Base de Valdivia | Valdivia
hosp-van-buren | Hospital Carlos Van Buren | Valparaíso
hosp-victoria | Hospital San José de Victoria | Victoria
hosp-villarrica | Hospital de Villarrica | Villarrica
ic-la-serena | IC La Serena Research | La Serena
iceg | Icegclinic | Santiago
icer-lab | ICER-Lab | Talcahuano
icos | Instituto Clínico Oncológico del Sur (ICOS) | Temuco
inc | Instituto Nacional del Cáncer | Santiago
inmunocel | Inmunocel | Santiago
instituto-oncologico-vina | Instituto Oncológico — Clínica Bupa Reñaca | Viña del Mar
iram | Instituto de Radiomedicina (IRAM) | Santiago
isp | Instituto de Salud Pública de Chile | Santiago
itop | Instituto de Terapias Oncológicas Providencia | Providencia
james-lind | James Lind Centro de Investigación del Cáncer | Temuco
k2-oncology | K2 Oncology | Santiago (Providencia)
meditek | Meditek Ltda. | Santiago
meds-la-dehesa | Clínica MEDS La Dehesa | Lo Barnechea
oncocentro | Oncocentro APYS | Viña del Mar
oncovida | Oncovida | Santiago
orlandi | Orlandi Oncología | Santiago
puc | Pontificia Universidad Católica de Chile | Santiago
redsalud | Clínica RedSalud | Santiago
rey-oreilly | Rey y O'Reilly Limitada | Temuco
saga | Centro de Estudios Clínicos SAGA | Santiago
ser-chile | Sociedad Chilena de Enfermedades Respiratorias | Santiago
sim | Sociedad de Investigaciones Médicas (SIM) | Temuco
soc-cirujanos | Sociedad de Cirujanos de Chile | Santiago
sochradi | Sociedad Chilena de Radiología | Santiago
sochradioterapia | Sociedad Chilena de Radioterapia | Santiago
torax | Instituto Nacional del Tórax | Santiago
uach | Universidad Austral de Chile | Valdivia
uandes | Universidad de los Andes | Santiago
uautonoma | Universidad Autónoma de Chile | Talca
uc-san-joaquin | Centro Médico San Joaquín UC CHRISTUS | Macul
uchile | Universidad de Chile | Santiago
ucm | Clínica Universidad Católica del Maule | Talca
ucmaule | Universidad Católica del Maule | Talca
ucn | Universidad Católica del Norte | Coquimbo
udec | Universidad de Concepción | Concepción
ufro | Universidad de La Frontera | Temuco
unab | Universidad Andrés Bello | Santiago
uromed | Instituto de Especialidades Urológicas (UROMED) | Santiago
urumed | Servicios Médicos Urumed | Rancagua
uss | Universidad San Sebastián | Concepción
utarapaca | Universidad de Tarapacá | Arica

Empezá con el lote 1 de la tarea A.

---

MENSAJE 2 DE 3 — tarea C, primera parte (mismas reglas y formato del mensaje 1)

TAREA C · Ensayos sin ninguna sede identificada (109 en total)
En estos ensayos ClinicalTrials.gov declara sitios en Chile pero oculta el nombre ("Research Site", "Novartis Investigative Site", "Local Institution"). Ya revisamos el buscador de la CIF, la planilla de inspecciones del ISP y el código postal de la sede. Buscá una fuente que nombre ESTE estudio (por NCT, código de protocolo o título exacto) y un centro chileno donde se hizo:
- el buscador de ensayos del laboratorio patrocinador (muchos listan los centros por país);
- la ficha del estudio en estudiosclinicos.cl o en Un Ensayo para Mí;
- sitios de centros de investigación chilenos que listen sus estudios;
- publicaciones del ensayo que listen centros o investigadores por país (a menudo en el apéndice o material suplementario), y comunicados de prensa;
- resoluciones del ISP o de comités de ética publicadas.
Un código postal, una ciudad o un investigador conocido NO bastan: la página tiene que nombrar el estudio y el centro. Si no hay, no_encontrada con lo que buscaste.
Formato: nct | patrocinador | código de protocolo | título | sedes enmascaradas en Chile (texto, ciudad, código postal)
NCT00034125 | Eli Lilly and Company | 3883 | Phase 3 Study of LY353381 Vs Tamoxifen in Women With Locally Advanced or Metastatic Breast Cancer. | sin nombre (Las Condes) | sin nombre (Providencia)
NCT00034268 | Eli Lilly and Company | 6428 | A Phase 3 Trial of LY900003 Plus Gemcitabine and Cisplatin Versus Gemcitabine and Cisplatin in Patients With Advanced, Previously Untreated Non-Small Cell Lung  | sin nombre (Las Condes)
NCT00043927 | GlaxoSmithKline | 104864-A/389 | Extensive Small Cell Lung Cancer Treatment Using An Investigational Drug Plus Chemotherapy In Chemotherapy-Naive Adults | GSK Clinical Trials Call Center (Santiago)
NCT00056407 | GlaxoSmithKline | ARI40006 | "REDUCE" - A Clinical Research Study To Reduce The Incidence Of Prostate Cancer In Men Who Are At Increased Risk | GSK Investigational Site (Santiago) | GSK Investigational Site (Viña del Mar)
NCT00072462 | Queen Mary University of London | ISRCTN37546358 | Adjuvant Tamoxifen Compared With Anastrozole in Treating Postmenopausal Women With Ductal Carcinoma In Situ | Chile (Santiago)
NCT00073307 | Bayer | 11213 | Study of BAY43-9006 in Patients With Unresectable and/or Metastatic Renal Cell Cancer | sin nombre (Santiago)
NCT00081796 | Sanofi | EFC6089 | Breast Cancer Trial of RPR109881 Versus Capecitabine in Male or Female Patients With Advanced Breast Cancer | Las Condes (Santiago) | sin nombre (Santiago)
NCT00082433 | R-Pharm | CA163-048 | Epothilone (Ixabepilone) Plus Capecitabine Versus Capecitabine Alone in Patients With Advanced Breast Cancer | Local Institution (Santiago)
NCT00105443 | Bayer | 100554 | A Phase III Study of Sorafenib in Patients With Advanced Hepatocellular Carcinoma | sin nombre (Santiago Región Metropolitana) | sin nombre (Santiago) | sin nombre (Santiago, 833-0024)
NCT00113607 | Johnson & Johnson Pharmaceutical Research & Development, L.L.C. | CR003448 | An Efficacy and Safety Study for Yondelis (Trabectedin) in Patients With Advanced Relapsed Ovarian Cancer | sin nombre (Reneca) | sin nombre (Santiago)
NCT00117598 | Pfizer | 3066K1-305 | Study Evaluating Temsirolimus (CCI-779) In Mantle Cell Lymphoma (MCL) | Pfizer Investigational Site (Providencia)
NCT00124566 | Eisai Inc. | IROF-018 | Study of Irofulven in Patients With Hormone-refractory Prostate Cancer | sin nombre (Santiago)
NCT00130897 | Pfizer | A6181037 | Treatment Use Study With Sunitinib (SU011248) For Patients With Cytokine-Refractory Metastatic Renal Cell Carcinoma | Pfizer Investigational Site (Santiago)
NCT00148798 | Merck KGaA, Darmstadt, Germany | EMR 62202-046 | Study of Cisplatin/Vinorelbine +/- Cetuximab as First-line Treatment of Advanced Non Small Cell Lung Cancer (FLEX) | Research Site (Antofagasta) | Research Site (Santiago)
NCT00154102 | Merck KGaA, Darmstadt, Germany | EMR 62202-013 | Cetuximab Combined With Irinotecan in First-line Therapy for Metastatic Colorectal Cancer (CRYSTAL) | Research Site (Santiago-Las Condes) | Research Site (Santiago-Providencia)
NCT00171340 | Novartis Pharmaceuticals | CFEM345D2405 | Zoledronic Acid in the Prevention of Cancer Treatment Related Bone Loss in Postmenopausal Women Receiving Letrozole for Breast Cancer. | Novartis Investigative Site (Santiago)
NCT00174655 | Sanofi | RP56976_PR_315 | BIG 02/98 Docetaxel - Breast Cancer | Sanofi-Aventis (Providencia Santiago)
NCT00174837 | Sanofi | EFC5512 | TRACE: Tirapazamine-Radiation And Cisplatin Evaluation | Sanofi-Aventis Administrative Office (Santiago)
NCT00174863 | Sanofi | EFC5378 | Evaluation of SR 31747A Versus Placebo in Androgen-Independent Non Metastatic Prostate Cancer | Sanofi-Aventis Administrative Office (Santiago)
NCT00191620 | Eli Lilly and Company | 6952 | Study Comparing Short Infusion Vs. Fixed Dose of Cisplatin + Gemcitabine in Non Small Cell Lung Cancer. | For additional information regarding investigative sites for this trial, contact 1-877-CTLILLY (1-877-285-4559, 1-317-615-4559) Mon-Fri from 9 AM to 5 PM Eastern Time (UTC/ GMT - 5 hours, EST), or speak with your personal physician (Santiago)
NCT00305188 | Sanofi | EFC5505 | Evaluation of the Efficacy of Xaliproden (SR57746A) in Preventing the Neurotoxicity of Oxaliplatin / 5FU/LV Chemotherapy. | Sanofi-Aventis Administrative Office (Santiago)
NCT00324155 | Bristol-Myers Squibb | CA184-024 | Dacarbazine and Ipilimumab vs. Dacarbazine With Placebo in Untreated Unresectable Stage III or IV Melanoma | Local Institution (Santiago)
NCT00338286 | Janssen Research & Development, LLC | CR005143 | A Study of Epoetin Alfa Plus Standard Supportive Care Versus Standard Supportive Care Only in Anemic Patients With Metastatic Breast Cancer Receiving Standard C | sin nombre (Arica) | sin nombre (Santiago) | sin nombre (Temuco) | sin nombre (Valdivia) | sin nombre (Valparaíso)
NCT00373113 | Pfizer | A6181107 | A Clinical Trial Comparing Efficacy And Safety Of Sunitinib And Capecitabine | Pfizer Investigational Site (Temuco, 4810469)
NCT00417079 | Sanofi | EFC6193 | XRP6258 Plus Prednisone Compared to Mitoxantrone Plus Prednisone in Hormone Refractory Metastatic Prostate Cancer | sanofi-aventis Chile (Santiago)
NCT00417209 | Sanofi | EFC6596 | Larotaxel Compared To Continuous Administration of 5-FU in Advanced Pancreatic Cancer Patients Previously Treated With A Gemcitabine-Containing Regimen | Sanofi-Aventis Administrative Office (Santiago)
NCT00418236 | Wyeth is now a wholly owned subsidiary of Pfizer | 3068A1-400 | Effect of Bazedoxifene, Raloxifene, and Placebo on Breast Density | sin nombre (Santiago)
NCT00474786 | Pfizer | 3066K1-404 | Temsirolimus Versus Sorafenib As Second-Line Therapy In Patients With Advanced RCC Who Have Failed First-Line Sunitinib | Pfizer Investigational Site (Providencia)
NCT00481247 | Bristol-Myers Squibb | CA180-056 | A Phase III Study of Dasatinib vs Imatinib in Patients With Newly Diagnosed Chronic Phase Chronic Myeloid Leukemia | Local Institution (Santiago)
NCT00519285 | Sanofi | EFC6546 | Aflibercept in Combination With Docetaxel in Metastatic Androgen Independent Prostate Cancer | Sanofi-Aventis Administrative Office (Providencia Santiago)
NCT00532155 | Sanofi | EFC10261 | A Study of Aflibercept Versus Placebo in Patients With Second-Line Docetaxel for Locally Advanced or Metastatic Non-Small-Cell Lung Cancer | Sanofi-Aventis Administrative Office (Santiago)
NCT00556322 | Hoffmann-La Roche | BO18602 | A Study of Tarceva (Erlotinib) and Standard of Care Chemotherapy in Patients With Advanced, Recurrent, or Metastatic Non-Small Cell Lung Cancer (NSCLC) | sin nombre (Santiago, 0000)
NCT00556712 | Hoffmann-La Roche | BO18192 | A Study of Tarceva (Erlotinib) Following Platinum-Based Chemotherapy in Patients With Advanced, Recurrent, or Metastatic Non-Small Cell Lung Cancer (NSCLC) | sin nombre (Santiago, 0000)
NCT00574275 | Sanofi | EFC10547 | Aflibercept Compared to Placebo in Term of Efficacy in Patients Treated With Gemcitabine for Metastatic Pancreatic Cancer | Sanofi-Aventis Administrative Office (Santiago)
NCT00626548 | AstraZeneca | D4320C00015 | A Phase III Trial of ZD4054 (Zibotentan) (Endothelin A Antagonist) in Non-metastatic Hormone Resistant Prostate Cancer | Research Site (La Serena) | Research Site (Santiago) | Research Site (Temuco) | Research Site (Viña del Mar)
NCT00678535 | Merck KGaA, Darmstadt, Germany | EMR 200048-052 | Erbitux in Combination With Xeloda and Cisplatin in Advanced Esophago-gastric Cancer | Research site (Reñaca) | Research site (Santiago) | Research site (Temuco) | Research site (Valparaíso)
NCT00681122 | AstraZeneca | NIS-OEU-ARI-2007/1 | CARIATIDE (Compliance of ARomatase Inhibitors AssessmenT In Daily Practice Through Educational Approach) | Research Site (Santiago) | Research Site (Temuco)
NCT00692770 | Bayer | 12414 | Sorafenib as Adjuvant Treatment in the Prevention Of Recurrence of Hepatocellular Carcinoma (STORM) | sin nombre (Reñaca) | sin nombre (Santiago, 833-0024)
NCT00806819 | Boehringer Ingelheim | 1199.14 | Lume Lung 2 : BIBF 1120 Plus Pemetrexed Compared to Placebo Plus Pemetrexed in 2nd Line Nonsquamous NSCLC | Boehringer Ingelheim Investigational Site (Jardin Del Mar, Renaca) | Boehringer Ingelheim Investigational Site (Las Condes) | Boehringer Ingelheim Investigational Site (Santiago) | Boehringer Ingelheim Investigational Site (Temuco)
NCT00883909 | GlaxoSmithKline | 103094 | ARI103094-Follow-Up Study for REDUCE Study Subjects | GSK Investigational Site (Santiago)
NCT00949910 | Hoffmann-La Roche | MO18109 | An Expanded Access Program of Tarceva (Erlotinib) in Participants With Advanced Non-Small Cell Lung Cancer (NSCLC) | sin nombre (Santiago)
NCT01009593 | Abbott | M10-963 | Efficacy and Tolerability of ABT-869 Versus Sorafenib in Advanced Hepatocellular Carcinoma (HCC) | Site Reference ID/Investigator# 36964 (Viña del Mar) | Site Reference ID/Investigator# 36967 (Temuco, 01745)
NCT01030783 | AVEO Pharmaceuticals, Inc. | AV-951-09-301 | A Study to Compare Tivozanib (AV-951) to Sorafenib in Subjects With Advanced Renal Cell Carcinoma | Site 121 (La Reina, 7510009) | Site 122 (Santiago, 8320000) | Site 123 (Temuco, 4810469)
NCT01057810 | Bristol-Myers Squibb | CA184-095 | Phase 3 Study of Immunotherapy to Treat Advanced Prostate Cancer | Local Institution (Santiago) | Local Institution (Temuco, 4810469) | Local Institution (Viña del Mar, 2540364)
NCT01076010 | AVEO Pharmaceuticals, Inc. | AV-951-09-902 | An Extension Treatment Protocol for Subjects Who Have Participated in a Study of Tivozanib Versus Sorafenib in Kidney Carcinoma (Protocol AV-951-09-301). | Site 122 (Santiago, 8320000) | Site 123 (Temuco, 4810469)
NCT01170663 | Eli Lilly and Company | 13894 | A Study of Paclitaxel With or Without Ramucirumab (IMC-1211B) in Metastatic Gastric Adenocarcinoma | ImClone Investigational Site (Providencia) | ImClone Investigational Site (Viña del Mar)
NCT01193244 | Millennium Pharmaceuticals, Inc. | C21004 | Study Comparing Orteronel Plus Prednisone in Participants With Chemotherapy-Naive Metastatic Castration-Resistant Prostate Cancer | sin nombre (Las Condes) | sin nombre (Santiago) | sin nombre (Temuco) | sin nombre (Valparaíso)
NCT01204749 | Amgen | 20090508 | TRINOVA-1: A Study of AMG 386 or Placebo, in Combination With Weekly Paclitaxel Chemotherapy, as Treatment for Ovarian Cancer, Primary Peritoneal Cancer and Fal | Research Site (Temuco, 4810469) | Research Site (Valparaíso, 2363058)
NCT01234311 | Active Biotech AB | 10TASQ10 | A Study of Tasquinimod in Men With Metastatic Castrate Resistant Prostate Cancer | sin nombre (Santiago) | sin nombre (Temuco) | sin nombre (Viña del Mar)
NCT01412957 | Amgen | 20100007 | Comparison of Survival Benefit of Panitumumab With Supportive Care to Best Supportive Care Alone in Patients With Metastatic Colorectal Cancer | Research Site (Temuco, 4810469) | Research Site (Viña del Mar, 2520612)
NCT01437566 | Genentech, Inc. | GDC4950g | Study of GDC-0941 or GDC-0980 With Fulvestrant Versus Fulvestrant in Advanced or Metastatic Breast Cancer in Participants Resistant to Aromatase Inhibitor Thera | sin nombre (Santiago, 7630370) | sin nombre (Temuco, 4810469) | sin nombre (Valparaíso, 2341391) | sin nombre (Viña del Mar, 2540364)
NCT01456325 | Genentech, Inc. | OAM4971g | A Study of Onartuzumab (MetMAb) in Combination With Tarceva (Erlotinib) in Participants With Met Diagnostic-Positive Non-Small Cell Lung Cancer Who Have Receive | sin nombre (Santiago, 0) | sin nombre (Santiago, Providencia) | sin nombre (Temuco, 4810469)
NCT01482962 | Millennium Pharmaceuticals, Inc. | C14012 | Alisertib (MLN8237) or Investigator's Choice in Patients With Relapsed/Refractory Peripheral T-Cell Lymphoma | sin nombre (Concepción) | sin nombre (Santiago)
NCT01516736 | Sandoz | LA-EP06-302 | Phase III Study Comparing the Efficacy and Safety of LA-EP2006 and Peg-Filgrastim | Sandoz Investigational Site (Temuco, 4810469)
NCT01571284 | Sanofi | AFLIBC06097 | Safety and Quality of Life Study of Aflibercept in Patients With Metastatic Colorectal Cancer Previously Treated With an Oxaliplatin-Based Regimen | Investigational Site Number 152001 (Santiago) | Investigational Site Number 152003 (Santiago)

Seguí en lotes de la tarea C hasta terminar esta parte.

---

MENSAJE 3 DE 3 — tarea C, segunda parte (mismas reglas y formato)

NCT01642004 | Bristol-Myers Squibb | CA209-017 | Study of BMS-936558 (Nivolumab) Compared to Docetaxel in Previously Treated Advanced or Metastatic Squamous Cell Non-small Cell Lung Cancer (NSCLC) (CheckMate 0 | Local Institution - 0110 (Viña del Mar) | Local Institution - 0117 (Santiago, 7600448) | Local Institution - 0131 (Santiago, 8420383) | Local Institution - 0154 (Santiago, 7630370) | Local Institution - 0161 (Antofagasta, 240000)
NCT01646021 | Janssen Research & Development, LLC | CR100848 | Study of Ibrutinib (a Bruton's Tyrosine Kinase Inhibitor), Versus Temsirolimus in Patients With Relapsed or Refractory Mantle Cell Lymphoma Who Have Received at | sin nombre (Temuco)
NCT01673867 | Bristol-Myers Squibb | CA209-057 | Study of BMS-936558 (Nivolumab) Compared to Docetaxel in Previously Treated Metastatic Non-squamous NSCLC | Local Institution - 0012 (Viña del Mar) | Local Institution - 0058 (Santiago, 7600448) | Local Institution - 0077 (Santiago, 8420383) | Local Institution - 0134 (Santiago)
NCT01715285 | Janssen Research & Development, LLC | CR100900 | A Study of Abiraterone Acetate Plus Low-Dose Prednisone Plus Androgen Deprivation Therapy (ADT) Versus ADT Alone in Newly Diagnosed Participants With High-Risk, | sin nombre (Santiago)
NCT01721772 | Bristol-Myers Squibb | CA209-066 | Study of Nivolumab (BMS-936558) Compared With Dacarbazine in Untreated, Unresectable, or Metastatic Melanoma | Local Institution (Santiago) | Local Institution (Santiago, 7630370) | Local Institution (Viña del Mar)
NCT01724021 | Hoffmann-La Roche | MO28457 | A Study of Participant Preference With Subcutaneous Versus Intravenous MabThera/Rituxan in Participants With CD20+ Diffuse Large B-Cell Lymphoma or CD20+ Follic | sin nombre (Santiago, 8380000) | sin nombre (Santiago, 8420383) | sin nombre (Viña del Mar, 2520612)
NCT01865747 | Exelixis | XL184-308 | A Study of Cabozantinib (XL184) vs Everolimus in Subjects With Metastatic Renal Cell Carcinoma | sin nombre (Santiago)
NCT02119663 | Incyte Corporation | INCB 18424-363 | A Study of Ruxolitinib in Pancreatic Cancer Patients | sin nombre (Santiago) | sin nombre (Vitacura)
NCT02125461 | AstraZeneca | D4191C00001 | A Global Study to Assess the Effects of MEDI4736 Following Concurrent Chemoradiation in Patients With Stage III Unresectable Non-Small Cell Lung Cancer | Research Site (Santiago, 7500000) | Research Site (Santiago, 8420383) | Research Site (Viña del Mar)
NCT02162667 | Celltrion | CT-P6 3.2 | Efficacy and Safety Evaluating Study of CT-P6 in Her2 Positive Early Breast Cancer | sin nombre (Santiago, 6640166) | sin nombre (Temuco, 4810469)
NCT02231749 | Bristol-Myers Squibb | CA209-214 | Nivolumab Combined With Ipilimumab Versus Sunitinib in Previously Untreated Advanced or Metastatic Renal Cell Carcinoma (CheckMate 214) | Local Institution - 0101 (Santiago, 8420383) | Local Institution - 0102 (Santiago) | Local Institution - 0103 (Viña del Mar, 254 0364) | Local Institution - 0144 (Santiago)
NCT02279862 | Bristol-Myers Squibb | CA184-437 | Safety and Efficacy Study of Ipilimumab 3 mg/kg Versus Ipilimumab 10 mg/kg in Subjects With Metastatic Castration Resistant Prostate Cancer Who Are Chemotherapy | Local Institution (Recoleta) | Local Institution (Santiago) | Local Institution (Viña del Mar, 2540364)
NCT02300831 | AstraZeneca | D1532R00004 | LUMINIST: LUng Cancer Molecular Insights Non Interventional Study | Research Site (Santiago)
NCT02352948 | AstraZeneca | D4191C00004 | A Global Study to Assess the Effects of MEDI4736 (Durvalumab), Given as Monotherapy or in Combination With Tremelimumab Determined by PD-L1 Expression Versus St | Research Site (Santiago, 7500000) | Research Site (Santiago, 8420383) | Research Site (Temuco, 4810469)
NCT02367040 | Bayer | 17067 | Copanlisib and Rituximab in Relapsed Indolent B-cell Non-Hodgkin's Lymphoma (iNHL) | sin nombre (Temuco, 4800827)
NCT02369874 | AstraZeneca | D4193C00002 | Study of MEDI4736 Monotherapy and in Combination With Tremelimumab Versus Standard of Care Therapy in Patients With Head and Neck Cancer | Research Site (Temuco, 4810469)
NCT02437318 | Novartis Pharmaceuticals | CBYL719C2301 | Study Assessing the Efficacy and Safety of Alpelisib Plus Fulvestrant in Men and Postmenopausal Women With Advanced Breast Cancer Which Progressed on or After A | Novartis Investigative Site (Santiago, 8420383) | Novartis Investigative Site (Temuco, 4810469) | Novartis Investigative Site (Viña del Mar, 2520612)
NCT02472964 | Mylan Inc. | MYL-Her 3001 | Study of Efficacy and Safety of Myl1401O + Taxane vs Herceptin©+ Taxane for 1st Line, Met. Br. Ca. | Mylan Investigational Site (Santiago) | Mylan Investigational Site (Temuco)
NCT02481830 | Bristol-Myers Squibb | CA209-331 | Effectiveness Study of Nivolumab Compared to Chemotherapy in Patients With Relapsed Small-cell Lung Cancer | Local Institution - 0025 (Recoleta, 0)
NCT02559583 | Janssen-Cilag Ltd. | CR105066 | Observational Study in Participants With Chronic Lymphocytic Leukemia (CLL), Multiple Myeloma (MM) and Non-Hodgkin's Lymphoma (NHL) in Latin America | sin nombre (Santiago)
NCT02677896 | Astellas Pharma Global Development, Inc. | 9785-CL-0335 | A Study of Enzalutamide Plus Androgen Deprivation Therapy (ADT) Versus Placebo Plus ADT in Patients With Metastatic Hormone Sensitive Prostate Cancer (mHSPC) | Site CL56001 (Santiago) | Site CL56002 (Temuco) | Site CL56003 (Santiago) | Site CL56004 (Reñaca) | Site CL56005 (Viña del Mar) | Site CL56007 (Providencia)
NCT02752074 | Incyte Corporation | INCB 24360-301 (ECHO-301) | A Phase 3 Study of Pembrolizumab + Epacadostat or Placebo in Subjects With Unresectable or Metastatic Melanoma (Keynote-252 / ECHO-301) | sin nombre (Santiago) | sin nombre (Viña del Mar)
NCT02809053 | Archigen Biotech Limited | AGB002 | A Randomized, Double-blind, Multi-center, Multi-national Trial to Evaluate the Efficacy, Safety, and Immunogenicity of SAIT101 Versus Rituximab as a First-line  | Research site (Temuco, 4810469)
NCT02823574 | Bristol-Myers Squibb | CA209-714 | Study of Nivolumab in Combination With Ipilimumab Versus Nivolumab in Combination With Ipilimumab Placebo in Patients With Recurrent or Metastatic Squamous Cell | Local Institution - 0115 (Santiago)
NCT02872116 | Bristol-Myers Squibb | CA209-649 | Efficacy Study of Nivolumab Plus Ipilimumab or Nivolumab Plus Chemotherapy Against Chemotherapy in Stomach Cancer or Stomach/Esophagus Junction Cancer | Local Institution - 0031 (Santiago) | Local Institution - 0032 (Temuco, 4800827) | Local Institution - 0033 (Viña del Mar, 2540364) | Local Institution - 0057 (Santiago, 8320000) | Local Institution - 0058 (Independencia)
NCT02941926 | Novartis Pharmaceuticals | CLEE011A2404 | Study to Assess the Safety and Efficacy of Ribociclib (LEE011) in Combination With Letrozole for the Treatment of Men and Pre/Postmenopausal Women With HR+ HER2 | Novartis Investigative Site (Santiago, 8420383)
NCT03088540 | Regeneron Pharmaceuticals | R2810-ONC-1624 | Study of REGN 2810 Compared to Platinum-Based Chemotherapies in Participants With Metastatic Non-Small Cell Lung Cancer (NSCLC) | Clincial Study Site (Viña del Mar) | Clinical Study Site (Recoleta) | Clinical Study Site (Santiago) | Clinical Study Site (Temuco)
NCT03141177 | Bristol-Myers Squibb | CA209-9ER | A Study of Nivolumab Combined With Cabozantinib Compared to Sunitinib in Previously Untreated Advanced or Metastatic Renal Cell Carcinoma | Local Institution - 0045 (Santiago, 8420383)
NCT03200717 | Novartis Pharmaceuticals | CPZP034A2410 | Study of Efficacy, Safety, and Quality of Life of Pazopanib in Patients With Advanced and/or Metastatic Renal Cell Carcinoma After Prior Checkpoint Inhibitor Tr | Novartis Investigative Site (Santiago, 8420383) | Novartis Investigative Site (Temuco, 4810469)
NCT03338790 | Bristol-Myers Squibb | CA209-9KD | An Investigational Immunotherapy Study of Nivolumab in Combination With Rucaparib, Docetaxel, or Enzalutamide in Metastatic Castration-resistant Prostate Cancer | Local Institution - 0034 (Santiago, 8420383) | Local Institution - 0051 (Viña del Mar, 2540364)
NCT03377361 | Bristol-Myers Squibb | CA209-9N9 | An Investigational Immuno-therapy Study Of Nivolumab In Combination With Trametinib With Or Without Ipilimumab In Participants With Previously Treated Cancer of | Local Institution - 0117 (Santiago, 000000) | Local Institution - 0118 (Santiago, 8420383)
NCT03400709 | Hospital San Juan de Dios, Santiago | 123606 | Protective Role of N-acetylcisteine From Cisplatin-induced Ototoxicity in Patients With Head and Neck Cancer | Daniel Munoz (Santiago, 7160166)
NCT03470922 | Bristol-Myers Squibb | CA224-047 | A Study of Relatlimab Plus Nivolumab Versus Nivolumab Alone in Participants With Advanced Melanoma | Local Institution - 0001 (Santiago)
NCT03519256 | Bristol-Myers Squibb | CA209-9UT | A Study of Nivolumab or Nivolumab Plus Experimental Medication BMS-986205 With or Without Bacillus Calumette-Guerin (BCG) in BCG Unresponsive Bladder Cancer Tha | Local Institution - 0069 (Santiago) | Local Institution - 0154 (Santiago, 8420383)
NCT03626545 | Novartis Pharmaceuticals | CACZ885V2301 | Phase III Study Evaluating Efficacy and Safety of Canakinumab in Combination With Docetaxel in Adult Subjects With Non-small Cell Lung Cancers as a Second or Th | Novartis Investigative Site (Santiago, 7500006)
NCT03631199 | Novartis Pharmaceuticals | CACZ885U2301 | Study of Efficacy and Safety of Pembrolizumab Plus Platinum-based Doublet Chemotherapy With or Without Canakinumab in Previously Untreated Locally Advanced or M | Novartis Investigative Site (Santiago, 8420383) | Novartis Investigative Site (Temuco, 4810469)
NCT03635983 | Bristol-Myers Squibb | CA045-001 | A Study of NKTR-214 Combined With Nivolumab vs Nivolumab Alone in Participants With Previously Untreated Inoperable or Metastatic Melanoma | Local Institution - 0173 (Santiago, 8330024) | Local Institution - 0174 (Recoleta, 0)
NCT03704077 | Bristol-Myers Squibb | CA224-061 | An Investigational Immuno-therapy Study of Relatlimab Plus Nivolumab Compared to Various Standard-of-Care Therapies in Previously Treated Participants With Recu | Local Institution (Santiago) | Local Institution (Santiago, 8330024)
NCT03721289 | AstraZeneca | D133FR00143 | Evaluation in Real World of Molecular Testing and Treatment Patterns for EGFR Mutation in Lung Cancer Patients | Research Site (Santiago)
NCT03725475 | AstraZeneca | D133HR00004 | A Study to Reveal the Patient Characteristics and Treatment Patterns of Stage III Non-small-cell Lung Cancer Patients | Research Site (Santiago)
NCT03980314 | Bristol-Myers Squibb | CA209-8FC | A Study to Compare Nivolumab Drug Product Process D to Nivolumab Drug Product Process C in Participants With Stage IIIa/b/c/d or Stage IV Melanoma After Complet | Local Institution - 0022 (Santiago, 0) | Local Institution - 0023 (Santiago) | Local Institution - 0024 (Independencia) | Local Institution - 0045 (Santiago, 8420383)
NCT04078152 | AstraZeneca | D910FC00001 | Durvalumab Long-Term Safety and Efficacy Study | Research Site (Santiago, 7500000)
NCT04266301 | Novartis Pharmaceuticals | CMBG453B12301 | Study of Efficacy and Safety of MBG453 in Combination With Azacitidine in Subjects With Intermediate, High or Very High Risk Myelodysplastic Syndrome (MDS) as P | Novartis Investigative Site (Viña del Mar, 2540364)
NCT04821609 | Pontificia Universidad Catolica de Chile | SA20I0060 | Supervised Resistance TRaining amONG Women at Risk of Breast Cancer Related Lymphedema | Karol Ramírez (Puente Alto)
NCT04948983 | Pontificia Universidad Catolica de Chile | SA18i0002 | The Effect of a Patient Decision Aids for Breast Cancer Screening | Alejandra Martínez (Santiago, sANTIAGO)
NCT04964908 | AstraZeneca | D8220R00031 | Study to Understand Clinical Characteristics, Treatment Pathway in Chronic Lymphocytic Leukemia | Research Site (Providencia, 7500000)
NCT05091437 | AstraZeneca | D133FR00176 | DOuBLED - Doubling Outcomes by Lung Cancer Early Diagnosis | Research Site (Antofagasta) | Research Site (Concepción)
NCT05329766 | Arcus Biosciences, Inc. | ARC-21 | A Safety and Efficacy Study of Treatment Combinations With and Without Chemotherapy in Adult Participants With Advanced Upper Gastrointestinal Tract Malignancie | Research Site (Las Condes) | Research Site (Recoleta) | Research Site (Santiago) | Research Site (Talca)
NCT05568095 | Arcus Biosciences, Inc. | STAR-221 | A Clinical Trial of a New Combination Treatment, Domvanalimab and Zimberelimab, Plus Chemotherapy, for People With an Upper Gastrointestinal Tract Cancer That C | Research Site (La Florida) | Research Site (Port Montt) | Research Site (Providencia) | Research Site (Recoleta) | Research Site (Santiago) | Research Site (Talca)
NCT05669989 | Sanofi | LTS17704 | International Treatment-extension Study in Adult Participants With Multiple Myeloma and Who Have Derived Clinical Benefit From Isatuximab | Investigational Site Number : 1520001 (Temuco, 4780000)
NCT06587451 | Sandoz | CJPB898A12301 | Integrated Pharmacokinetics (PK)/Efficacy, Safety, and Immunogenicity Study to Demonstrate Similarity of JPB898, a Proposed Biosimilar to Nivolumab, to Opdivo®  | Sandoz Investigational Site (Santiago) | Sandoz Investigational Site 1 (Santiago)
NCT06901531 | Astellas Pharma Global Development, Inc. | 8951-CL-0305 | A Study of Zolbetuximab Together With Pembrolizumab and Chemotherapy in Adults With Gastric Cancer | Site CL56001 (Santiago) | Site CL56004 (Las Condes)
NCT06946797 | Bristol-Myers Squibb | CA209-1533 | A Study to Evaluate Two Dosing Regimens of Subcutaneous Nivolumab in Combination With Intravenous Ipilimumab and Chemotherapy in Participants With Previously Un | Local Institution - 0067 (Santiago, 8420383)
NCT07476326 | Biocon Biologics UK PLC | BIO-NIVOLU-103 | Pharmacokinetics, Safety, and Immunogenicity Comparison of Bmab1700 and Opdivo® as Adjuvant Monotherapy in Participants With Melanoma | Biocon Investigational Site (Providencia) | Biocon Investigational Site (Recoleta) | Biocon Investigational Site (Santiago) | Biocon Investigational Site 1 (Santiago)

Seguí en lotes hasta terminar. Al final, mandá un último mensaje (no JSON) con cuántos ítems resolviste por tarea y cuáles fuentes te sirvieron más.
