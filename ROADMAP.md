# Hoja de ruta — de "radar de evidencia" a herramienta de KOL mapping

Documento de planificación, no de implementación — nada de lo que describe acá está construido
todavía. Nace de tres auditorías independientes (la mía, ChatGPT y Gemini, cada una pensando como
un MSL que usa la página), las decisiones de producto que se tomaron sobre esos hallazgos, y una
investigación de factibilidad hecha antes de comprometerse a nada (5 hilos de investigación en
vivo — no solo documentación, sino consultas reales a las APIs candidatas). Se guarda en el repo
sin comitear todavía; el commit es una decisión aparte.

## Por qué existe este documento

Las tres auditorías coincidieron en algo más grande que cualquier bug puntual: la página hoy
contesta bien *"¿qué actividad pública encontré asociada a esta entidad?"*, pero un MSL necesita
que conteste *"¿quién es relevante para mi pregunta científica ahora mismo, y por qué?"*. Ese
cambio de pregunta es el hilo conductor de todo lo que sigue — no es una lista de features
sueltas, es una dirección de producto.

## 1. Decisiones de producto ya tomadas

Esto es lo que se decidió explícitamente después de leer el feedback de ChatGPT y Gemini — no son
propuestas abiertas, son la dirección confirmada.

### Búsqueda y filtros
- Buscar por tema/biomarcador, no solo por nombre/institución/ciudad — indexar el texto de cada
  `hecho`, no solo el nombre de la entidad.
- Filtros **jerárquicos**: tema grande → tema chico (ej. "Cirugía" antes que un biomarcador
  específico), no una lista plana mezclando escalas.
- Tags de expertise buscables con lógica **booleana AND/OR** sobre varios tags a la vez.

### Relevancia y puntaje
- Se mantiene el ranking único general (no se elimina, a diferencia de lo que sugería ChatGPT),
  pero se le suma un **puntaje por tema** cuando la búsqueda es específica — el ranking da
  contexto, no reemplaza al tema.
- "Por qué te muestro a esta persona" — mostrar explícitamente qué tags/criterios de la búsqueda
  cumplió, no solo el resultado.

### Perfil de persona
- Expertise tags derivados del texto ya existente en los `hechos` — no un campo nuevo que
  recolectar desde cero.
- Campo de rol/especialidad, solo cuando la fuente lo declare explícito (mismo principio que
  `revista`: null si no está, nunca inferido).
- Categoría por función (Trialist / Speaker / Academic / DOL), derivada del tipo de hecho
  dominante de cada persona.
- Afiliación **actual vs. histórica** — la más reciente se muestra como actual, el resto como
  histórico, para no repetir el error de mostrar una afiliación de 2014 con el mismo peso visual
  que una de 2026.
- Gráfico de tendencia temporal (publicaciones/ensayos por año) — la misma base sirve para "peso
  visual" y para detectar rising stars.
- Sección "lo que no sabemos" — vacíos de evidencia explícitos por ficha.
- Links externos a la persona (ej. búsqueda en PubMed), con foco especial cuando la confianza de
  identidad es baja, para que el usuario verifique manualmente.

### Confianza e identidad
- Separar **confianza de identidad** (¿es la misma persona?) de **estado de verificación**
  (¿lo revisó un humano?) — hoy `confianza` es un solo campo que mezcla ambas preguntas.
- Heurística: instituciones muy distintas entre publicaciones atribuidas a "la misma persona" →
  señal de posible error de identidad.
- Flag manual humano ("esto no parece ser de esta persona") sobre un hecho puntual.

### Instituciones
- Etiqueta público/privado por institución.
- Catalogar primero un registro base de instituciones de Chile, y **recién después** asociar
  personas a instituciones ya conocidas — en vez de descubrirlas ad-hoc desde publicaciones (ver
  §3 para la fuente concreta que resuelve esto).

### Vista de red (mapa completo)
- Se mantiene el grafo visual — la posición de Francisco coincide con Gemini ("un grafo visual
  real es oro"), no con ChatGPT (que prefería reemplazarlo por listas). Pero con:
  - Zoom y pan.
  - El grafo se **reconstruye según los filtros/búsqueda activos**, en vez de mostrar siempre las
    23 entidades completas sin importar qué se filtró antes de abrirlo.
  - Forma + color por tipo de entidad (no solo color), tamaño de nodo por grado de conexión, hover
    que resalta vecinos.
  - Avatar con iniciales o ícono en vez de un círculo anónimo — sin fabricar fotos reales que no
    existen como fuente.

### Roadmap futuro (documentado, explícitamente no ahora)
- Capa privada tipo CRM (notas del MSL, última interacción, engagement) — separada del repo
  público. Fuera de alcance de KOL Radar tal como está planteado hoy (ver §5, el propio README
  dice que esta herramienta "no registra interacciones con profesionales de salud").
- Canal de corrección/privacidad para profesionales listados — gap conocido desde antes de esta
  ronda de feedback, sigue pendiente.
- Mapa de Chile con conteo por territorio — Francisco pidió pensarlo con más calma antes de
  comprometerse: 17 de 23 entidades de la muestra hoy están en Santiago, así que el mapa por sí
  solo no resuelve el amontonamiento, solo le da sentido real a la posición.
- **Fotos de perfil.** Pedido explícitamente (14-ago-2026), queda deliberadamente pendiente, no
  descartado. La razón para no hacerlo todavía: una foto no es un hecho citable como el resto del
  modelo de datos — es una obra con derecho de autor propio (de la clínica/fotógrafo), el riesgo de
  atribuir la foto de la persona equivocada es mucho más grave que un dato de texto erróneo
  (la propia muestra ya documenta homónimos sin confirmar, ej. Carlos Rojas vs. Andrés Rojas G.),
  y que una clínica publique una foto en su propio sitio para su propia promoción no equivale a
  consentimiento para aparecer en una herramienta externa que además la acompaña de un puntaje —
  justo el tipo de uso fuera de propósito original que Ley 19.628 busca acotar, y lo que el README
  promete que esta herramienta no es ("no es una evaluación de desempeño profesional ni un listado
  comercial"). Alternativa ya decidida mientras tanto: avatar con iniciales/ícono por tipo, sin
  fabricar ni redistribuir una foto real (ver "Vista de red" en §1).

## 2. Correcciones a los hallazgos previos

- **"SONCHI" no existe.** La sociedad chilena de oncología médica activa es **SCOM** (Sociedad
  Chilena de Oncología Médica, scom.cl). Se usó el nombre equivocado en la ronda de feedback
  anterior — cualquier mención futura debe decir SCOM.

## 3. Investigación de factibilidad

Cinco hilos de investigación en paralelo, cada uno con consultas en vivo contra las APIs/sitios
candidatos (no solo lectura de documentación). Resumen accionable de cada uno — el detalle
completo con cada fuente citada queda en el journal de la sesión, no repetido acá.

### 3.1 Fuentes bibliométricas abiertas (para ampliar cobertura + resolver identidad + tendencia anual)

Se probaron **OpenAlex**, **Semantic Scholar** y **Crossref** en vivo contra un KOL chileno real
del dominio exacto del proyecto (Dr. Christian Caglevic, oncólogo torácico de FALP).

| Fuente | Desambiguación de autor | Publicaciones por año | Costo/fricción |
|---|---|---|---|
| **OpenAlex** | Sí — consolidó 111 trabajos y 9.668 citas del Dr. Caglevic en un solo perfil, con ORCID vinculado | Sí — campo `counts_by_year` ya calculado, serie 2012–2026 lista para graficar | **Desde el 13-feb-2026 exige API key** registrada y factura por créditos (~US$1 gratis/día, de sobra para el volumen del proyecto) |
| Semantic Scholar | No de forma confiable — el mismo KOL quedó fragmentado en 12 IDs, con la producción real (81 papers) archivada bajo "C. Caglevic" en vez del nombre completo buscable | No — solo totales de carrera, hay que agregar por año en el cliente | Gratis, sin key obligatoria |
| Crossref | No — son strings de nombre crudos, ORCID casi nunca presente | No | Gratis, sin key, solo pedir `mailto=` para el "polite pool" |

**Veredicto: OpenAlex es la única que resuelve ambos problemas de fábrica**, con evidencia empírica
contra un caso chileno real, y ya cubre las instituciones chilenas relevantes (Instituto Nacional
del Tórax, PUC, U. de Chile, FALP aparecen con perfiles poblados) y prácticamente todos los DOI de
SciELO.

**El hallazgo que cambia la arquitectura:** si KOL Radar sigue siendo un sitio estático sin
backend que hace `fetch()` directo desde el navegador, una API key de OpenAlex quedaría **expuesta
públicamente** en cada petición de red del sitio en GitHub Pages. Ni Semantic Scholar ni Crossref
tienen este problema. Esto no descarta OpenAlex — pero significa que consumirlo en vivo desde el
navegador no es la forma correcta; tendría que ser un paso intermedio (algo que corra fuera del
navegador y publique un JSON estático), lo cual de hecho encaja con el modelo de datos actual del
proyecto (hechos con fuente/fecha/confianza ya vienen de una recolección puntual, no de fetch en
vivo a fuentes de terceros).

### 3.2 Campos sin usar de ClinicalTrials.gov API v2

Confirmado en vivo (consultas reales a la API de producción, con ejemplos chilenos): hoy KOL Radar
solo guarda fase y a veces el PI. Existen, sin necesidad de ninguna dependencia nueva (es la misma
API que ya se usa):

- **Estado de reclutamiento** en dos niveles — por estudio completo (`overallStatus`) y por sitio
  individual (`LocationStatus`), que pueden diferir entre sí.
- **Patrocinador con clase** (`LeadSponsorClass`: INDUSTRY / NIH / OTHER / FED / ...) — distingue
  automáticamente ensayos industry-sponsored de académicos.
- **Lista completa de sitios chilenos** con contacto (`LocationContactName/Phone/EMail` — ojo,
  el campo correcto es `EMail` con mayúscula, `Email` da HTTP 400), aunque el contacto suele ser
  un coordinador de estudio, no el PI con nombre propio.
- **Intervención/droga estudiada** (`InterventionName`, `InterventionType`).
- **Fecha de última actualización** (`LastUpdatePostDate`) — ya es lo que hoy se muestra como
  "última actualización" en la ficha, confirmado que es el campo correcto.
- Se puede **filtrar por país + área terapéutica con precisión** usando sintaxis Essie
  (`AREA[LocationCountry]Chile AND AREA[ConditionSearch]"lung cancer"`), verificado con una
  consulta real que devolvió 3 ensayos reclutando activamente en Chile al 2026-08-14 — esto
  habilita descubrir ensayos nuevos de forma automatizada, no solo enriquecer los que ya se
  conocen.
- `referencesModule.references[].pmid` conecta un ensayo con su publicación en PubMed cuando
  existe — cruce barato entre las dos fuentes que ya se usan.

Sin rate limit oficial confirmado (la doc es una SPA que no se pudo leer directamente), consenso
de terceros ~50 req/min sin necesitar key — muy por encima del volumen de este proyecto.

### 3.3 Catálogo de instituciones de Chile

Confirmado en vivo: existe **"Establecimientos de Salud vigentes"** (DEIS/MINSAL), publicado en
datos.gob.cl, licencia CC0, con API REST tipo CKAN funcional (`datastore_search`, probado en vivo,
~5.717 registros). Trae:

- Nombre oficial, código único estable (`EstablecimientoCodigoVigente`), tipo de establecimiento,
  comuna/región, dirección, coordenadas.
- **Público/privado de forma explícita** (`TipoSistemaSaludGlosa`) — exactamente lo que se pedía —
  aunque hay tres campos relacionados no idénticos (`TipoSistemaSaludGlosa`,
  `DependenciaAdministrativa`, `TipoPertenenciaEstabGlosa`) que hay que reconciliar y documentar
  cuál se usa como fuente de verdad.
- Estado de funcionamiento (vigente/cerrado), útil para no catalogar instituciones que ya
  cerraron.
- Metadatos de actualización recientes (11–12 de agosto de 2026, dos días antes de esta
  investigación) — parece mantenido activamente, no abandonado.

**No trae especialidad médica declarada** — "esta institución trata cáncer de pulmón" sigue
teniendo que salir de las fuentes actuales (PubMed, ensayos, sitios institucionales), pero ahora
anclado a una institución ya conocida del catálogo en vez de descubrirla ad-hoc. La Superintendencia
de Salud (RNPI, prestadores acreditados) no sirve como catálogo base — son consultas uno-a-uno sin
descarga masiva, cobertura parcial.

### 3.4 Congresos, sociedades científicas y LinkedIn

**El hallazgo de mayor retorno de todo este documento:** la señal de "autoría de guía clínica"
(ASCO/ESMO/MINSAL) — que Gemini señaló como potencialmente más reveladora que cinco publicaciones
más — **ya es obtenible hoy mismo vía PubMed**, la fuente que el proyecto ya usa. No hace falta
ninguna infraestructura nueva, solo filtrar por tipo de publicación "Practice Guideline"/"Guideline"
combinado con cáncer de pulmón. Cero fricción legal, cero fuente nueva.

Para el resto de la señal de "liderazgo científico" (ponente/comité en congresos), el panorama es
desigual:

- **SCOM y SER Chile** (sociedades chilenas): programas en HTML plano, sin login, sin prohibición
  de scraping encontrada — técnicamente extraíble, pero bajo volumen (un congreso al año) y con
  URLs que no son 100% estables entre años → mejor como **consulta manual periódica**, igual que
  las demás fuentes institucionales chilenas de hoy, no como pipeline automatizado. **Nota real
  sobre SER Chile específicamente**: en la recolección de la muestra actual, las páginas de
  directivas/congresos de serchile.cl devolvieron HTTP 404 (ver DATA_SAMPLE.md, `campos_faltantes_o_dificiles`
  en el JSON) — no está claro si esas URLs cambiaron o si hay que buscar el patrón de URL vigente
  antes de asumir que "técnicamente extraíble" sigue siendo cierto hoy.
- **WCLC (IASLC) y ASCO**: sus Términos de Uso **prohíben explícitamente** scraping/automatización
  — IASLC incluso prohíbe literalmente usar su sitio para "entrenar, reentrenar, ajustar o mejorar
  cualquier modelo de IA", y ASCO ya bloquea el acceso automatizado en la práctica (HTTP 403
  observado). No construir nada automatizado contra estos dos sitios. Un dato puntual anotado a
  mano, citando fuente y fecha, sigue siendo aceptable — un scraper recurrente no.
- **ESMO** quedó sin verificar con certeza (varios fetches fallaron) — requiere chequeo manual en
  navegador antes de decidir su caso.

**LinkedIn: se descarta como fuente, con evidencia, no por precaución genérica.** El User Agreement
de LinkedIn prohíbe explícitamente scraping, sin excepción para proyectos pequeños o de
investigación. El caso que suele citarse como "precedente pro-scraping" (hiQ Labs v. LinkedIn) en
realidad terminó con el scraper condenado a pagar USD 500.000 y una prohibición judicial
permanente. Y en enero de 2025 — reciente, no histórico — LinkedIn demandó a Nubela/Proxycurl, una
API de "enriquecimiento de datos" del mismo tipo de modelo que se necesitaría acá; el propio
fundador demandado ahora recomienda públicamente una política de "cero datos de LinkedIn". No
existe tampoco una vía de API oficial realista para un proyecto sin afiliación comercial con
LinkedIn. **Se retira del roadmap.**

### 3.5 Patrones vanilla-JS (gráfico de tendencia, zoom/pan, búsqueda multi-tag)

Las tres capacidades son factibles sin ninguna librería nueva, con patrones estándar y bien
documentados — pero ninguna viene "gratis" en accesibilidad, hay que presupuestarla como trabajo
real:

- **Sparkline de tendencia anual**: `<svg viewBox>` dinámico + `<polyline>`/`<rect>`, mapeando
  índice→X y valor invertido→Y, con `vector-effect="non-scaling-stroke"` para que el trazo no varíe
  de grosor entre KOLs con distinta cantidad de años de datos. Necesita `<title>`/`aria-label` con
  el resumen textual desde el inicio (no es gratis con el SVG básico).
- **Zoom + pan sobre el grafo**: manipulación directa de los 4 números del atributo `viewBox` —
  zoom centrado en el cursor con la fórmula estándar de "fixed point", pan con Pointer Events
  (un solo set de handlers para mouse y touch), pinch con `Math.hypot()` sobre la distancia entre
  dos toques. Dos trampas documentadas: hay que dividir el delta de pan por el ratio
  `viewBox.width / anchoRenderizado`, y sin `{ passive:false }` + `touch-action:none` el navegador
  hace scroll/zoom nativo en vez de zoom del grafo. **Obligación real de accesibilidad**: WCAG
  2.5.1 exige una alternativa de un solo puntero (botones +/-) al gesto de pinch/rueda — no es
  opcional si se apunta a cumplir el estándar. Rendimiento de SVG puro se degrada recién sobre
  ~300–500 nodos — muy por encima de lo que tiene hoy una sola especialidad, así que no hace falta
  Canvas por ahora (sí sería tema si el proyecto escala a varias especialidades a la vez).
- **Multi-tag AND/OR**: `Array.every()` da AND, `Array.some()` da OR, sobre los tags de cada KOL —
  trivial en cliente, sin costo de rendimiento al volumen actual. **Nota de producto**: el
  convención de mercado (PatternFly, GitHub) es fijar OR-dentro-de-faceta / AND-entre-facetas sin
  dejarlo elegible al usuario — el toggle AND/OR manual que se pidió es una variante válida pero
  menos común que el default de la industria, vale la pena comunicarlo como decisión deliberada,
  no asumir que el usuario lo infiere solo. Los chips deben ser `<button aria-pressed="true/false">`,
  no un `<div>` con clase, y mantener mínimo 24px de alto (44px recomendado) de objetivo táctil.

## 4. Plan de implementación propuesto (orden sugerido, a discutir)

No es una decisión final — es un punto de partida para la conversación, ordenado por
esfuerzo/dependencias, no por importancia:

1. **Extender ClinicalTrials.gov** (§3.2) — mismo cliente HTTP que ya existe, cero fricción nueva,
   alto valor inmediato (estado de reclutamiento, patrocinador, sitios completos).
2. **Autoría de guías clínicas vía PubMed** (§3.4) — cero fuente nueva, cero fricción legal, señal
   de "thought leadership" de alto valor que hoy no se captura.
3. **Confianza de identidad vs. verificación** + heurística de instituciones dispares — es
   principalmente un cambio de modelo de datos y de UI sobre lo que ya existe.
4. **Expertise tags, filtros jerárquicos, búsqueda por tema** — se puede construir sobre el texto
   de los `hechos` ya recolectados, sin nueva fuente.
5. **Catálogo de instituciones de Chile** (§3.3) — importar el dataset DEIS una vez, definir la
   llave estable, y migrar las instituciones actuales para que apunten a ese catálogo.
6. **Vista de red**: zoom/pan + reconstrucción según filtros + forma/color/tamaño (§3.5) — encaja
   en el código ya existente del grafo, sin librería nueva.
7. **Gráfico de tendencia temporal / rising stars** — depende de resolver primero la decisión de
   OpenAlex (§3.1, el problema de la API key) o construirlo con datos de fecha que ya existen en
   los hechos actuales como primera versión más simple, sin esperar a OpenAlex.
8. **Sociedades chilenas (SCOM, SER Chile)** como fuente manual periódica — bajo volumen, no
   automatizar. Para SER Chile, verificar primero el patrón de URL vigente: las páginas de
   directivas/congresos devolvieron HTTP 404 en el último intento (§3.4).
9. **Geografía y capa privada** — quedan en el roadmap futuro (§1), no en este ciclo.

## 5. Preguntas abiertas para decidir juntos

- **OpenAlex**: ¿vale la pena resolver el problema de la API key (ej. moviendo la recolección a un
  paso que corre fuera del navegador y publica un JSON estático, en vez de fetch en vivo desde el
  cliente) para tener desambiguación de identidad + tendencia anual de fábrica? ¿O se prefiere una
  versión más simple primero, usando solo las fechas que ya existen en los hechos actuales?
- **Geografía**: Francisco pidió pensarlo con más calma — ¿mapa de Chile con conteo por territorio,
  como propuso ChatGPT, o alguna otra forma de darle sentido real a la posición sin prometer más de
  lo que el dato (mayoritariamente Santiago) puede sostener?
- **AND/OR en tags**: ¿se mantiene el toggle manual (decisión ya tomada) o, visto que es una
  variante poco común en el mercado, vale la pena validarlo con algún MSL real antes de construirlo?
- **Capa privada / CRM**: confirmado como roadmap futuro — ¿en qué momento se retoma la
  conversación de cómo se separaría del repo público?

---
*Generado a partir de: auditoría propia + auditorías externas de ChatGPT y Gemini (feedback del
usuario), decisiones de producto tomadas en conversación, e investigación de factibilidad de 5
hilos en paralelo con verificación en vivo contra APIs/sitios reales. No commiteado — pendiente de
decisión aparte.*
