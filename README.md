# KOL Radar — Chile

Radar científico de especialistas, centros y evidencia pública en Chile, pensado como
herramienta de apoyo para Medical Science Liaisons (MSL) y Medical Affairs.

**Demo en vivo**: <https://franciscokirhman.github.io/kol-radar/>

Este documento es el spec del proyecto (objetivo, alcance, fuentes, modelo de datos,
disclaimers) escrito antes de construir nada. Desde entonces se armó un prototipo de
Fase 3 con datos reales de muestra — ver "Estado actual" al final de este archivo.

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

- Aplica Ley 19.628 sobre protección de la vida privada (Chile). Un profesional de
  salud identificado por nombre es un dato personal, aunque la fuente sea pública.
  La base para tratar ese dato es que es información profesional de interés público
  (autoría científica, afiliación institucional publicada, participación en estudios
  o congresos) — nunca datos de salud propios del profesional ni de pacientes.
- Toda persona listada puede pedir corrección o exclusión de su ficha — **pero este
  canal todavía no existe**. El contacto de abajo sigue sin completarse, así que
  hoy esa promesa no es cumplible en la práctica. No compartir este proyecto más
  allá de una demo interna hasta llenar esto.
- **Contacto**: [completar — nombre y correo de contacto del responsable del proyecto]
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
| ClinicalTrials.gov (API v2) | Activa | Ensayos con sitio en Chile, investigador cuando esté publicado |
| Sitios de sociedades médicas | Activa (manual al inicio) | Directorios, directivas, programas de congresos |
| Hospitales / universidades | Activa (manual al inicio) | Afiliación institucional publicada |
| SciELO / Revista Médica de Chile | Activa | Producción científica local, coautoría |
| Instituto de Salud Pública (ISP) | **Futura, no en MVP** | No tiene registro público navegable de investigadores por patología; requiere revisión caso a caso por protocolo. Se evalúa más adelante. |

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
- `web/index.html` — la vista de producto (búsqueda, lista con señales, red de
  conexiones, detalle con evidencia). Esto es lo que probaría un MSL.
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

Prototipo de Fase 3 funcionando con datos reales de muestra (una especialidad,
cáncer de pulmón): [COMPETITORS.md](COMPETITORS.md) (panorama competitivo),
[DATA_SAMPLE.md](DATA_SAMPLE.md) + [data/sample/perfiles-muestra.json](data/sample/perfiles-muestra.json)
(77 entidades reales con fuentes verificadas), [COSTS.md](COSTS.md) (modelo de costos
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
