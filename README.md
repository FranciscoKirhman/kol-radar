# KOL Radar — Chile y mapa mundial de ensayos

Radar científico de especialistas, centros y evidencia pública en Chile, pensado como
herramienta de apoyo para Medical Science Liaisons (MSL) y Medical Affairs.

**Demo en vivo**: <https://franciscokirhman.github.io/kol-radar/>

Este documento es el spec técnico del proyecto (alcance, fuentes, modelo de datos,
disclaimers) escrito antes de construir nada. Desde entonces se armó un prototipo de
Fase 3 con datos reales de muestra — ver "Estado actual" al final de este archivo.

## Documentos del proyecto

| Archivo | Qué contiene |
|---|---|
| [PRODUCT_CHARTER.md](PRODUCT_CHARTER.md) | **Documento rector**: el problema, el usuario, qué significa el puntaje, qué queda como juicio humano, y el método de trabajo por etapas |
| README.md (este) | Spec técnico: fuentes, modelo de datos, marco legal, cómo correr el prototipo |
| [SCORING.md](SCORING.md) | Especificación del modelo de prioridad v2: las dimensiones, sus topes, la curva de recencia y los umbrales de tier |
| [ROADMAP.md](ROADMAP.md) | Decisiones de producto tomadas, investigación de factibilidad de fuentes, y estado de la brecha contra el charter |
| [DECISIONS.md](DECISIONS.md) | **Decisiones abiertas que le tocan a Francisco**, con pasos y links — canal de corrección, OpenAlex, cadencia del pipeline, capa privada |
| [DATA_SAMPLE.md](DATA_SAMPLE.md) | Qué trajo cada fuente y qué campos resultaron confiables o débiles |
| [COMPETITORS.md](COMPETITORS.md) | Panorama competitivo |
| [COSTS.md](COSTS.md) | Modelo de costos del pipeline de automatización |
| [COLABORACION_IA.md](COLABORACION_IA.md) | **Traspaso para colaboradores IA** (ChatGPT, Gemini): reglas duras, modelo de datos, y en qué conviene que aporten |
| [PENDIENTES_BETA.md](PENDIENTES_BETA.md) | **Lo que la beta dejó sin resolver a propósito**, con la razón de cada caso |
| [PUBLICAR.md](PUBLICAR.md) | **Cómo publicarlo y cederlo**: qué bloquea la publicación, la Ley 21.719, pasos en orden |
| [PRIVACIDAD.md](PRIVACIDAD.md) | Borrador del aviso de privacidad, para completar y revisar con abogado |
| [LICENSE](LICENSE) · [data/LICENSE.md](data/LICENSE.md) | Licencias: código MIT, datos ODbL 1.0, y lo que la licencia no autoriza sobre datos personales |

## Mapa mundial

El mapa mundial está integrado en la [interfaz principal](web/index.html#mapa),
con la misma paleta, tipografía, búsqueda, filtros, fichas y grafo de Chile.
`web/mundo.html` redirige a esa vista para conservar enlaces existentes. El
selector del encabezado cambia de país en la misma interfaz. El índice
`data/publicado/mundo/indice.json` muestra, para cada país o
territorio que aparece en el [facet oficial de ClinicalTrials.gov](https://clinicaltrials.gov/api/v2/stats/field/values?fields=LocationCountry),
el número de ensayos con una ubicación declarada allí. La geometría viene de
[Natural Earth 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson):
ubica países, no centros. Los territorios que no tienen polígono a esa escala se
pueden elegir en la lista.

`data/publicado/mundo/<ISO2>.json` guarda pares ensayo–sede textual de las primeras
páginas consultadas; `ensayos_detalle` y `estado` indican con claridad cuánto se
guardó. Al elegir un país, el botón «Cargar más ensayos» puede seguir consultando páginas directamente a
[la API oficial](https://clinicaltrials.gov/data-api/api). Los estudios muestran
su NCT y enlace exacto; las sedes son cadenas declaradas por la fuente, todavía
sin validar como instituciones canónicas ni convertirlas en coordenadas. La
selección de área se basa en condiciones declaradas y los estudios sin área
clasificada siguen visibles al seleccionar “Todas las áreas”. Chile conserva
sus perfiles de personas, fármacos, patentes y mapa detallado; los demás países
solo publican ensayos y sedes textuales mientras no exista aprobación legal
para incluir personas y fuentes verificadas para las otras capas.

Para actualizar los recuentos y guardar hasta 100 estudios por país:

```sh
python3 scripts/recolectar_mundo_ctgov.py --todos --max-paginas 1
python3 scripts/verificar_mapa_mundial.py
```

Sin `--todos` ni `--paises`, el recolector actualiza solo el índice; con
`--paises FR,DE` y `--max-paginas 2` guarda detalle de esos dos países. Los
países sin aprobación legal no publican fichas de personas ni campos de
contacto o investigadores. La vista Chile y sus datos personales siguen bajo
la barrera de `data/config/paises.json`.

## Objetivo

Responder una pregunta concreta en minutos en vez de horas de investigación manual:

> ¿Qué especialistas y centros están activos en un área clínica específica en Chile,
> y con qué evidencia pública se sostiene esa conclusión?

El área clínica es un parámetro de búsqueda, no algo fijo en el código — la herramienta
debe servir para cualquier especialidad, no solo para una patología de ejemplo.

## Usuario inicial y trabajo a resolver

- **Usuario**: MSL o Medical Advisor preparando un territorio, un congreso o una
  conversación científica.
- **Trabajo**: pasar de buscar a mano en PubMed, ClinicalTrials.gov y sitios de
  sociedades médicas, a tener un mapa verificable y con evidencia enlazada.
- **No es** un CRM, no reemplaza revisión humana, no genera un ranking de "a quién
  contactar primero" ni un puntaje de valor comercial.

## Qué NO hace (explícito, no implícito)

- No infiere ni publica datos que no estén ya públicos.
- No guarda datos personales sensibles ni información de contacto privada.
- No calcula un score oculto de "importancia" — toda señal se muestra con su
  desglose de origen, nunca como un número sin explicación al lado.
  *(Nota del 2026-08-10, tras una auditoría: el prototipo de Fase 3 sí compone un
  "puntaje" visible sumando señales — publicaciones, ensayos pesados por fase,
  conexiones — porque se pidió explícitamente como diferenciador frente a
  competidores que sí ocultan su scoring. Cada componente queda siempre trazable a
  hechos concretos con fuente. Lo que el producto evita es usarlo como ranking por
  defecto: el orden inicial de la lista es cronológico, no por puntaje — ordenarla
  por puntaje es una acción que el usuario elige, no algo que la app decide por él.)*
- No registra interacciones con profesionales de salud (eso es trabajo de un CRM,
  fuera de alcance).
- No decide nada de forma autónoma: toda incorporación de un dato nuevo pasa por
  revisión humana antes de marcarse como confirmado.

## Marco legal y ético

- **Desde el 1 de diciembre de 2026 rige la Ley 21.719**, que reforma la 19.628: elimina la
  excepción amplia de "fuentes de acceso público" y exige una base de licitud (acá, interés
  legítimo) y un canal que responda los derechos de las personas listadas. Ver
  [PUBLICAR.md](PUBLICAR.md).
- Aplica Ley 19.628 sobre protección de la vida privada (Chile). Un profesional de
  salud identificado por nombre es un dato personal, aunque la fuente sea pública.
  La base para tratar ese dato es que es información profesional de interés público
  (autoría científica, afiliación institucional publicada, participación en estudios
  o congresos) — nunca datos de salud propios del profesional ni de pacientes.
- Toda persona listada puede pedir corrección o exclusión de su ficha. **Desde el 2026-09-28 hay
  un correo provisorio** (franckirhman@gmail.com) y el pie del sitio lo muestra. Falta el resto
  del proceso —plazo de respuesta, registro de exclusiones, responsable identificado—: ver
  [PUBLICAR.md](PUBLICAR.md) antes de difundir el sitio.
- **Contacto**: el canal no se escribe en este archivo ni en el HTML: vive en el
  campo `contacto.canal` de [`data/sample/perfiles-muestra.json`](data/sample/perfiles-muestra.json).
  Poné ahí una dirección de correo **o** la URL `https://` de un formulario y el pie de página del
  sitio se completa solo. Mientras siga en `null`, el sitio dice que el canal todavía no existe —
  que es la verdad. El campo se valida antes de usarse: una URL que no sea `http(s)` o un correo mal
  formado se ignoran y el aviso honesto se mantiene, para que un dato malo nunca borre la advertencia.
- **Disclaimer visible en la app** (implementado en el footer de `web/index.html`,
  visible siempre, no solo al abrir una ficha — versión actual, honesta sobre el
  contacto pendiente): "Información de fuentes públicas (...) — no es una evaluación
  de desempeño profesional ni un listado comercial. Datos de muestra, sin revisión
  humana todavía. ¿Eres un profesional listado acá y quieres corregir o eliminar tu
  información? El canal de contacto para eso todavía no está definido — este es un
  prototipo, no un producto en producción." Reemplazar por el texto original de
  abajo recién cuando el contacto esté completo:
  "La información de este sitio proviene de fuentes públicas (publicaciones
  científicas, registros de ensayos clínicos, sitios de sociedades médicas y centros
  de salud). No constituye una evaluación de desempeño profesional ni un listado
  comercial. Si eres un profesional listado aquí y quieres corregir o eliminar tu
  información, contáctanos en la dirección indicada arriba."

## Fuentes (Fase 1)

| Fuente | Estado | Qué se extrae |
|---|---|---|
| PubMed (E-utilities API) | Activa | Publicaciones, coautores, afiliación, fecha |
| ClinicalTrials.gov (API v2) | Activa | Ensayos con sitio en Chile, investigador cuando esté publicado, y la **lista estructurada de intervenciones**, de la que salen las fichas de fármaco (`scripts/integrar_farmacos_ctgov.py`) |
| NCI Thesaurus (API EVS del National Cancer Institute) | Activa (desde 2026-09-28) | Tipo de cada fármaco —inmunoterapia, terapia dirigida, quimioterapia, conjugado anticuerpo-fármaco…— desde la jerarquía del tesauro, con la URL del concepto. CC BY 4.0. Ver `scripts/clasificar_farmacos_ncit.py` |
| Buscador de estudios clínicos de la CIF (estudiosclinicos.cl) | Activa (desde 2026-09-28) | Para los ensayos que hoy reclutan, qué centros tienen abiertos en Chile — incluso cuando ClinicalTrials.gov oculta la sede como "Research Site". Solo el hecho ensayo ↔ centro con su URL; no se guardan contactos. `robots.txt` sin restricciones. Ver `scripts/recolectar_estudiosclinicos_cl.py` |
| Sitios de sociedades médicas | Activa (manual al inicio) | Directorios, directivas, programas de congresos |
| Hospitales / universidades | Activa (manual al inicio) | Afiliación institucional publicada |
| SciELO / Revista Médica de Chile | Activa | Producción científica local, coautoría |
| Instituto de Salud Pública (ISP) — planilla de centros de investigación clínica inspeccionados 2016–2025 | Activa (desde 2026-09-28) | El código de protocolo de cada inspección se cruza con el `orgStudyId` de ClinicalTrials.gov: si calza con exactamente un ensayo, el centro inspeccionado se liga como sede. **No se copian** fecha, tipo, resultado ni motivo de la inspección (son una evaluación regulatoria, no evidencia de actividad). Los investigadores principales que nombra entraron el 2026-09-29, **antes de la revisión de identidad** (decisión de Francisco): 8 fichas nuevas y 6 existentes ligadas por nombre, cada una con su nota de identidad. Detalle en `data/pending/isp-inspecciones-2026-09-29/`. Ver `scripts/integrar_isp_inspecciones.py` |
| FDA — Orange Book y Purple Book | Activa (desde 2026-10-03) | Para la pestaña **Patentes** y el perfil de cada fármaco: patentes y exclusividades de cada producto aprobado en EE.UU. con su vencimiento, patentes de biológicos informadas a biosimilares, y cuántos genéricos o biosimilares ya están aprobados. Dominio público. Ver `scripts/patentes.py` → `data/patentes/vencimientos.json` |
| INAPI — registros de patentes 2009 a hoy (datos.gob.cl) | Activa (desde 2026-10-03) | Patentes chilenas vigentes cuyo **título** nombra el fármaco, con su vencimiento; el tipo (formulación, combinación, uso…) se deduce del título. Parcial: la patente del compuesto casi nunca nombra el fármaco. Titulares sí, inventores no; un titular persona natural no se publica. CC0. Pat-INFORMED (OMPI) no se usa: sus términos prohíben las consultas automatizadas |
| OpenStreetMap (Nominatim) | Activa (ubicación de instituciones, pendiente de revisión) | Punto en el mapa de instituciones (no de personas) cuando el DEIS no lo tiene, con la URL del objeto como fuente. Licencia ODbL. Ver `scripts/geolocalizar_instituciones_osm.py` y `scripts/consolidar_ubicaciones.py` |
| DEIS (Minsal) — Establecimientos de Salud | Activa (ubicación de instituciones, pendiente de revisión) | Dirección y coordenadas oficiales de hospitales y clínicas, asignadas a mano por código de establecimiento. datos.gob.cl, licencia CC0. Consolidado con las demás fuentes en `data/geo/ubicaciones-instituciones.json` |
| geoBoundaries — límites de la BCN | Activa (solo geometría) | Límites de regiones y comunas para dibujar el mapa por ciudad. Datos de la Biblioteca del Congreso Nacional y OCHA ROLAC, licencia CC BY 3.0 IGO. Ver `data/geo/` y `scripts/preparar_limites_chile.py` |

Cualquier fuente nueva se agrega a esta tabla antes de integrarse — no se consume
ninguna fuente que no esté documentada acá.

## Modelo de datos mínimo

Cada afirmación sobre una persona guarda cuatro campos, sin excepción:

- **Hecho**: ej. "autor en publicación", "afiliado a este centro", "investigador en
  este ensayo", "ponente en este congreso".
- **Fuente**: URL específica (no un dominio genérico).
- **Fecha**: cuándo ocurrió el hecho y cuándo se revisó por última vez.
- **Confianza**: `confirmado` (revisado por una persona) | `probable` (extraído,
  pendiente de revisión) | `pendiente` (candidato sin validar).

Ningún dato se muestra como "confirmado" sin haber pasado por revisión humana.

## Relaciones de la red (v1)

Tipos de arista, deliberadamente pocos y literales al inicio:

- Médico → coautoría verificable → Médico
- Médico → investigador/centro del estudio → Ensayo clínico
- Médico → afiliación pública → Centro / universidad
- Médico → ponente o moderador → Congreso
- Médico → produce evidencia sobre → Tema clínico
- Ensayo clínico → intervención → Fármaco *(desde 2026-09-28)*

Se llaman "conexiones científicas observables", no "influencia" — es más honesto y
evita sobre-interpretar una coautoría como una relación de poder.

*(Nota del 2026-08-14: en la muestra de Fase 3, el campo `vinculos[].tipo` real usa
un vocabulario más específico que estos cinco — "afiliación", "afiliación
secundaria", "investigador de sitio", "sitio del ensayo" (ensayo sin PI nombrado,
el centro es la entidad principal) y "coautoría" cuando dos personas citan
independientemente la misma publicación como fuente. Los tipos "ponente o
moderador → Congreso" y "produce evidencia sobre → Tema clínico" están diseñados
pero todavía no tienen ningún vínculo en la muestra — la fuente de docencia/
congresos sigue sin capturarse de forma confiable, ver "Estado actual".)*

## Arquitectura de agentes (para cuando se automatice — no en el primer commit de código)

| Agente | Hace | No decide |
|---|---|---|
| Recolector | Consulta las fuentes activas y trae candidatos | Si dos personas son la misma |
| Extractor | Convierte una fuente en hechos estructurados (hecho/fuente/fecha) | La importancia de un profesional |
| Resolutor de identidad | Propone coincidencias por nombre, afiliación, ORCID, tema | Unir perfiles automáticamente sin revisión |
| Revisor | Marca datos desactualizados, contradicciones, evidencia débil | Publicar sin paso por revisión humana |

Toda incorporación automática entra a una bandeja de revisión. Una persona acepta,
corrige o rechaza antes de que el dato pase a `confirmado`.

## Cómo correr el prototipo (Fase 3)

`web/index.html` carga los datos con `fetch()`, así que necesita servirse por HTTP —
abrirlo con doble-click (`file://`) no funciona, el navegador bloquea esa llamada.

**Opción 1 — Python (ya viene instalado en macOS/Linux):**

```bash
cd kol-radar
python3 -m http.server 8000
```

Después abre <http://localhost:8000/web/index.html> en el navegador. Para parar el
servidor: `Ctrl+C` en la terminal donde corre.

**Opción 2 — Node, si no tienes Python o preferís npm:**

```bash
cd kol-radar
npx serve .
```

Te va a mostrar la URL exacta en la terminal (normalmente `http://localhost:3000`) —
agrégale `/web/index.html` al final.

**Si el puerto ya está ocupado** (`Address already in use`), cambia el número de puerto
(ej. `python3 -m http.server 8001`) y ajusta la URL igual.

**Qué vas a ver:**
- `web/index.html` — la vista de producto. Cuatro pestañas:
  - **Inicio**: buscador y cuatro entradas (fármacos, estudios, instituciones, profesionales).
  - **Perfil**: lo que se sabe de una ficha, en conclusiones y rankings — para un fármaco, en qué
    centros se estudia, quién patrocina, con qué se combina; para un centro, qué se investiga,
    quién trabaja ahí y con quién comparte estudios. Cada perfil tiene un enlace propio
    (`#ficha=<id>`) para compartir.
  - **Mapa**: Chile por región y, dentro de cada región, un círculo por centro con cuántos estudios
    tiene. Al elegir un centro: con quién comparte estudios (arcos) y quién trabaja ahí (panel).
  - **Fichas**: la lista filtrable, con la evidencia de cada hecho.
- `web/interno.html` — cómo se construyó (costos, arquitectura de agentes, pipeline).
  Enlazada desde "Detalles técnicos" en el header de `web/index.html` (no del
  `index.html` raíz, que solo redirige), no pensada para el usuario final —
  deliberadamente discreta para no competir con la vista de producto.

Si ves un mensaje de error en pantalla en vez de la lista, es casi siempre que abriste
el archivo sin servidor — revisa que la URL empiece con `http://localhost`, no `file://`.

## Roadmap

1. **Fase 1 (este commit)** — spec: qué hace, qué no hace, fuentes, modelo de datos,
   disclaimers.
2. **Fase 2** — 30 fichas armadas a mano en una especialidad de prueba, para validar
   que el modelo de datos y las fuentes tienen sentido antes de automatizar nada.
3. **Fase 3** — red navegable simple (mapa + perfil por persona + botón "ver
   evidencia" en cada afirmación).
4. **Fase 4** — automatizar solo PubMed y ClinicalTrials.gov con los cuatro agentes;
   todo lo demás sigue siendo carga manual revisada.
5. **Fase 5** — matriz de señales para priorizar sin caja negra. Parcialmente
   adelantada en el prototipo (puntaje visible + desglose por señal, orden por
   defecto cronológico no por puntaje); falta que el usuario pueda ajustar los
   pesos por su cuenta en vez de tenerlos fijos en el código.
6. **Fase 6** — validación con 5 entrevistas a usuarios reales de Medical Affairs.

## Estado actual

**Actualización 2026-09-28** — el prototipo pasó a buscar por las cuatro cosas que busca un MSL
(fármaco, estudio, profesional, institución) y a mostrar un perfil de cada una:

| | 2026-09-10 | 2026-09-28 | 2026-09-29 |
|---|---|---|---|
| Fichas | 717 | 1.146 (+380 fármacos, +49 instituciones) | 1.133 (361 fármacos, sin 19 duplicados; 83 personas) |
| Vínculos | 1.198 | 3.130 | 3.352 |
| Ensayos sin ninguna institución | 262 | 212 — el resto tiene la sede oculta en las dos fuentes | 109 — con el ISP y el código postal (inferido, marcado como tal) |
| Fichas sin ninguna conexión | 262 | 12 | — |
| Instituciones ubicadas en el mapa | 56 | 90 | 94 |

De dónde salió lo nuevo, sin inventar nada: los fármacos, de las intervenciones estructuradas de
ClinicalTrials.gov (uniendo nombres solo cuando la fuente declara la equivalencia), con su tipo
—inmunoterapia, terapia dirigida, quimioterapia…— según el NCI Thesaurus; las sedes, de
una tabla de alias revisada a mano contra el DEIS y sitios oficiales (`scripts/resolver_sedes_web.py`)
y del buscador de la CIF, que nombra los centros que ClinicalTrials.gov enmascara. Todo entra
`pendiente`. El detalle de cada decisión queda en `data/pending/`.

Antes de esa actualización:

Prototipo de Fase 3 funcionando con datos reales de muestra (una especialidad,
cáncer de pulmón): [COMPETITORS.md](COMPETITORS.md) (panorama competitivo),
[DATA_SAMPLE.md](DATA_SAMPLE.md) + [data/sample/perfiles-muestra.json](data/sample/perfiles-muestra.json)
(717 entidades reales con fuentes verificadas), [COSTS.md](COSTS.md) (modelo de costos
del pipeline de automatización, verificado adversarialmente), y `web/index.html`
(la página de producto — ver "Cómo correr el prototipo" arriba).

Sin automatizar todavía: Fase 2 (validación manual de 30 fichas) no se hizo formalmente
porque se saltó directo a construir con datos de muestra ya verificados; Fase 4
(automatización real vía los cuatro agentes) sigue sin implementar — el pipeline
descrito en `COSTS.md` es una estimación, no código corriendo.

**Auditoría 2026-08-10**: se corrió una auditoría adversarial (seguridad, integridad
de los datos, cumplimiento de las promesas de este README, consistencia entre
archivos) sobre todo el repo. 16 hallazgos confirmados, aplicados: orden por defecto
de la lista pasó de puntaje a cronológico, cada hecho ahora muestra su propia
confianza, se valida el esquema de las URLs antes de usarlas como link, se explicita
que un mismo hecho puede sumar puntos en dos entidades relacionadas,
`web/interno.html` dejó de tener datos hardcodeados desactualizados,
`DATA_SAMPLE.md` y este README quedaron con los números reales (23 entidades, no
10), y el disclaimer de privacidad quedó visible siempre en la app, no solo al
abrir una ficha. Pendiente real, no resuelto todavía: el canal de contacto para
pedir corrección/exclusión de una ficha (ver "Marco legal y ético" arriba).

## Licencia

- **Código** (`web/`, `scripts/`, `prototipos/`): [MIT](LICENSE). Se puede usar, modificar y
  redistribuir, también con fines comerciales, conservando el aviso de copyright.
- **Datos** (`data/`): [Open Database License 1.0](data/LICENSE.md). Se pueden reutilizar citando la
  fuente; una base derivada que se publique tiene que usar la misma licencia. Es la licencia que exige
  OpenStreetMap, del que salen parte de las ubicaciones.
- La licencia **no** autoriza a tratar datos personales de los profesionales listados fuera de la ley
  chilena: ver la sección final de [data/LICENSE.md](data/LICENSE.md).
- Para citar el proyecto: [CITATION.cff](CITATION.cff).
