# Muestra de datos — oncología en Chile

Ejercicio de traer datos **reales** (no sintéticos) de las fuentes ya
documentadas en `README.md`, para descubrir qué campos son confiables antes de
diseñar la página de perfil. Esto se hizo con una muestra de prueba, no la
validación manual de 30 fichas que el Roadmap de `README.md` define como Fase
2 (esa etapa formal sigue sin hacerse). Los datos completos están en
[`data/sample/perfiles-muestra.json`](data/sample/perfiles-muestra.json) — 173
entidades reales (70 personas, 28 instituciones, 75 ensayos clínicos) y 349
vínculos entre ellas, cada hecho en el formato hecho/fuente/fecha/confianza
del modelo de datos, con un campo `tipo` adicional y (según el caso) `fase`
del ensayo o `revista` de la publicación.

Metodología: 4 agentes en paralelo, cada uno restringido a una sola fuente y
obligado a citar la URL exacta de donde sacó cada dato — sin inventar
autores, afiliaciones ni fechas. Fuentes que sí aportaron datos a esta
muestra: PubMed (E-utilities), ClinicalTrials.gov (API v2), SciELO Chile, e
Instituto Nacional del Tórax. SER Chile se intentó como quinta fuente, pero
sus páginas de directivas/congresos devolvieron HTTP 404 al momento de
recolectar — no hay ningún hecho de esta muestra citando serchile.cl (ver
`campos_faltantes_o_dificiles` en el JSON).

**Primera fusión de identidad (2026-08-18):** `claudio-silva-f` (como PubMed indexa el nombre) y
`claudio-silva-fuente-alba` (como firma en SciELO) eran dos fichas de la misma persona. Se
unificaron en una sola, con el id del nombre completo. Es la primera vez que se fusionan dos
personas en esta muestra, y no se hizo automáticamente: la regla del proyecto es que ninguna fusión
de identidad ocurre sin aprobación humana explícita, porque juntar a dos médicos distintos es un
error grave y difícil de deshacer.

La evidencia que la sostiene es directa, no inferida: el registro ORCID
[0000-0003-2472-1833](https://orcid.org/0000-0003-2472-1833) lista *"Claudio Silva F."* y *"Claudio
Silva Fuente-Alba"* entre las variantes del mismo nombre, y declara empleo en Radiología, Clínica
Alemana. Esa cita quedó guardada como un hecho más de la ficha, con su URL y su fecha, así que
cualquiera puede auditar la fusión sin creernos. La ficha además explica en `nota_identidad` que fue
unificada y por qué.

Efectos secundarios que hubo que resolver a mano: la persona quedaba con dos afiliaciones primarias
(Clínica Alemana por SciELO, Sociedad Chilena de Radiología por PubMed). Se dejó a Clínica Alemana
como `afiliación` — es el empleador y lo respalda ORCID — y a la sociedad científica como
`afiliación secundaria`, como pide el charter §3. El `subtitulo` decía "Departamento de Imágenes",
que es un departamento y no una organización: el mismo error de ingesta ya documentado más abajo.
Ahora dice "Clínica Alemana", citando ORCID.

Esto dejó la pregunta abierta de cuántos duplicados más hay. Un escaneo por apellido compartido
encontró otros dos pares con exactamente la misma huella — una ficha con el apellido materno
abreviado a inicial (formato SciELO) y otra con el apellido completo: `francisco-aguayo` /
`francisco-aguayo-g` y `juan-carlos-diaz-p` / `juan-carlos-diaz-patino`. **No se fusionaron**: son
plausibles, no probados, y siguen esperando la misma confirmación humana.

**Más de una enfermedad (2026-08-18):** la muestra dejó de estar clavada a cáncer de pulmón
— el gap #1 del `PRODUCT_CHARTER.md` §14 ("fixed demo scope"). Se sumaron ensayos con sitio real
en Chile de **cáncer de mama** (22 entidades) y **cáncer gástrico**
(5), traídos de ClinicalTrials.gov con la misma consulta Essie ya
verificada y conectados solo a instituciones que ya conocíamos. Se descartaron 20 ensayos cuyos
sitios chilenos no corresponden a ninguna institución de la muestra: entrarían como nodos sueltos.
Cada entidad lleva ahora un campo `area`, y la interfaz filtra por él.

Eso además arregló la capa de **temas**, que no tenía sentido: en un conjunto de una sola
enfermedad, "NSCLC" tocaba al 21% de las personas y "Tamizaje" al 20% — eran el tema del dataset
entero, no un rasgo de nadie, y como nodos del grafo se volvían hubs que no distinguían nada. Ahora
se descarta todo tema que cubra más del 18% del conjunto visible, y el umbral se relaja al filtrar
por área porque ahí el conjunto ya está acotado. Quedan los que sí discriminan: EGFR, ALK, PD-L1,
inmunoterapia, terapia dirigida, quimioterapia, radioterapia.

**Instituciones y coautoría (2026-08-18):** dos huecos que se notaban en el grafo, ambos
resueltos sin recolectar nada nuevo — solo usando mejor lo ya citado:

- **25 personas no tenían ninguna institución.** La causa era propia: al integrarlas tomé como
  `subtitulo` el primer fragmento del texto de afiliación, que suele ser el departamento
  ("Department of Thoracic Surgery") y no la organización ("Clínica Santa María"). Se releyó el
  texto completo de afiliación de cada una y se crearon las 18 instituciones
  reales que faltaban (universidades, clínicas, el ISP, y cuatro sociedades científicas). Hoy
  ninguna persona queda sin institución, y quien tiene más de una afiliación declarada recibe
  vínculos de tipo `afiliación` y `afiliación secundaria`, como pide el charter §3.
- **Solo existía 1 vínculo persona↔persona en toda la muestra.** Al apagar las otras capas del
  grafo quedaban 71 puntos sueltos y una sola línea. Se derivaron 112 vínculos de `coautoría`
  nuevos con una regla estricta: dos personas quedan conectadas **solo si citan exactamente la
  misma fuente** (mismo PMID o mismo artículo de SciELO) en sus propios hechos. No se infiere
  coautoría por apellido, institución ni tema — se conectan dos hechos que ya estaban citados.
  24 personas siguen sin coautores en la muestra, que es la respuesta honesta: su evidencia
  actual no las conecta con nadie más de este conjunto.

**Integración de candidatos pendientes (2026-08-18):** se revisaron los 64 candidatos que la
recolección de agosto había encontrado pero dejado sin integrar. Resultado: **53 personas nuevas**
(18 → 71), con 76 hechos y 28 vínculos a instituciones ya conocidas.

Criterios aplicados, en este orden:

1. **Alcance del charter** — `PRODUCT_CHARTER.md` limita el primer caso de uso a médicos, así
   que se excluyeron 11 candidatos cuya afiliación declarada dice estudiante de medicina, interno,
   alumno, residente o enfermería. No es un juicio sobre su relevancia: es el alcance declarado.
2. **Verificación contra la fuente, no contra el código de estado.** Las URLs de PubMed devuelven
   HTTP 203 (caché) y las de SciELO 403 (bloqueo ya documentado), así que el status no prueba nada.
   Se consultó la API de PubMed (esummary) para los 38 PMIDs citados y se comprobó que el autor
   afirmado **figure realmente en la lista de autores** del paper: 46 de 46 hechos confirmados.
   En el camino se corrigió un error propio de verificación — el chequeo inicial buscaba solo el
   segundo token del nombre como apellido y marcaba como no encontrados a "Osvaldo Arén Frontera"
   (PubMed lo indexa `Frontera OA`) y "María Paz Saavedra" (`Saavedra MP`); ambos eran correctos.
3. **Sin fusionar homónimos** — 4 personas conservan la advertencia de identidad que traía la
   recolección, ahora en un campo `nota_identidad` que la ficha muestra explícitamente.

**Refresco de ensayos (2026-08-18):** se volvió a consultar ClinicalTrials.gov en vivo para
los 49 ensayos de la muestra y se agregó a cada uno su **estado de reclutamiento** verificado
(27 reclutando, 21 activos sin reclutar), incluyendo cuántos de sus sitios chilenos están
reclutando hoy — dato de alto valor para un MSL que antes no capturábamos pese a estar
disponible en la misma API que ya usábamos.

Ese refresco detectó además un caso que justifica por sí solo tener cadencia de actualización:
**NCT07227597 eliminó todos sus sitios en Chile** (actualización del 2026-08-17; hoy solo tiene
sitios en China, Israel y Corea del Sur). Como el alcance de esta muestra es Chile, el ensayo se
quitó junto con sus 3 vínculos a Bradford Hill, FALP y PUC — eran afirmaciones que la fuente ya
no respalda. Se documenta acá en vez de borrarlo en silencio.

**Ronda de expansión (2026-08-15):** una segunda recolección, con el mismo
principio de citar URL exacta y no inventar, amplió la muestra de 23 a 77
entidades: 44 ensayos clínicos nuevos de ClinicalTrials.gov con sitio real en
alguna institución ya conocida (verificados uno por uno contra la API en
vivo antes de integrarlos, no solo confiados a lo que devolvió el agente),
9 personas nuevas (Christian Caglevic y Héctor Galindo, ambos investigadores
principales confirmados en el ensayo ALKAZAR/NCT06765109; 6 miembros del
equipo médico de FALP y 1 de Clínica Alemana desde sus directorios públicos),
1 institución nueva (Clínica Alemana), y 13 hechos nuevos sobre entidades ya
existentes. Quedó **pendiente, deliberadamente no integrado todavía**: 21
personas candidatas de PubMed y 43 de SciELO que la recolección encontró
pero no se revisaron una por una — su volumen no permitía la misma revisión
individual que sí se le dio a este lote. Quedan como trabajo futuro, no
descartadas.

## Lo que encontró (perfiles reales)

- **Carlos Rojas** y **Mauricio Burotto** — investigadores del Bradford Hill
  Clinical Research Center (Santiago), coautores en varios ensayos y
  publicaciones sobre NSCLC, uno de ellos con ORCID visible.
- **Fundación Arturo López Pérez (FALP)** — aparece como afiliación en
  publicaciones y como sitio activo en 4 ensayos clínicos distintos
  (WU-KONG1, REZILIENT3, BE6A LUNG-02, SUNRAY-02), con el nombre escrito de 4
  formas distintas entre fuentes.
- **Instituto Nacional del Tórax** — directorio público con nombres, cargos y
  formación de su plana directiva (Dra. Begoña Yarza, Dra. Claudia Sepúlveda),
  pero sin ninguna fecha de actualización visible en la página.
- **NCT06890598 (SUNRAY-02)** — el único de 8 ensayos muestreados que expone
  el nombre real del investigador principal por cada sitio en Chile.
- Cuatro médicos identificados vía SciELO Chile (Roberto González L., Andrés
  Rojas G., Fernando Saldías P., entre otros), todos con afiliación
  institucional citada literalmente del artículo.

## Lo que esto le enseña al modelo de datos

**Confiable en el 100% de los casos:** nombre de la entidad, URL de la fuente,
y una descripción del hecho. Eso es lo mínimo que la página puede prometer
mostrar siempre.

**Débil o inconsistente — y hay que diseñar para eso, no ignorarlo:**

1. **El investigador principal casi nunca aparece a nivel de sitio en
   ClinicalTrials.gov.** En 7 de 8 ensayos, el único contacto público es
   personal corporativo del patrocinador (ej. "GSK Clinical Trial, MD"), no
   alguien en Chile. Cuando SÍ aparece (SUNRAY-02), es la excepción, no la
   regla. **Implicación de diseño:** un ensayo clínico debe poder existir en
   la red sin una persona vinculada — el nodo principal ahí es el centro, no
   el investigador.
2. **Los nombres de institución no están normalizados.** La misma FALP
   aparece como "FALP", "Fundación Arturo López Pérez" y "Arturo López Pérez
   Oncology Foundation Institute" en fuentes distintas — y a veces en el mismo
   ensayo. Sin un diccionario de sinónimos, el sistema fragmentaría una
   institución en cuatro nodos separados.
3. **ORCID aparece en menos del 20% de los autores.** No se puede depender de
   él como identificador único; el modelo tiene que tolerar coincidencias
   "por nombre + institución" marcadas explícitamente como no confirmadas
   (ver el caso Carlos Rojas vs. Andrés Rojas G. — mismo apellido, personas
   distintas, sin ninguna relación).
4. **Las páginas institucionales (ej. torax.cl) no tienen fecha de
   revisión.** Ninguna. Hay que asumir que ese campo va a estar vacío la
   mayoría de las veces para este tipo de fuente, y mostrarlo como tal en vez
   de inferir una fecha falsa. (serchile.cl no entra en esta observación —
   sus páginas devolvieron HTTP 404 al recolectar, nunca se pudieron leer;
   ver Metodología arriba.)
5. **SciELO bloquea fetch directo (HTTP 403)** — hace falta navegador
   embebido para leerlo, no una llamada HTTP simple. Relevante para el
   presupuesto de ingeniería de la Fase 4.

## Recomendaciones concretas para la página de perfil

Ver el campo `recomendaciones_pagina` en
[`data/sample/perfiles-muestra.json`](data/sample/perfiles-muestra.json) para
el detalle completo. Resumen:

- Mostrar siempre: nombre, tipo, al menos una fuente. Todo lo demás es
  opcional y debe declararse como tal en la interfaz, no ocultarse en
  silencio.
- La afiliación se muestra como texto citado literal, nunca forzada a campos
  separados de institución/ciudad/país.
- Fecha con precisión variable (día/mes/año/desconocida) — nunca inventar un
  día 00 para rellenar un formato.
- Un ensayo clínico sin investigador nombrado muestra el centro como entidad
  principal; el campo de persona queda vacío, no relleno con el contacto
  corporativo del patrocinador.
- Cada hecho lleva su propio indicador de confianza y fuente — la revisión
  humana aprueba o rechaza hecho por hecho, no perfil completo.
- Ninguna fusión automática de dos personas solo por apellido compartido; el
  vínculo por nombre+institución sin ORCID se marca visiblemente como no
  confirmado.
