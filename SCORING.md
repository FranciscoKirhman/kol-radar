# Especificación de puntaje v2

Implementa el diseño de puntaje descrito en [`PRODUCT_CHARTER.md`](PRODUCT_CHARTER.md) §5/§5A/§5B.
El charter deja los valores de puntos como "la siguiente decisión de diseño" — esto es esa
decisión, tomada con los principios que el charter ya fijó (categorías con tope, decaimiento por
recencia, confianza separada de prioridad, nunca premiar prestigio institucional o tamaño de red
por sí solos). Es v1 de esta especificación, no un número final e inmutable.

## Alcance: solo personas

El charter limita el primer caso de uso a médicos ("Limit the first use case to physicians").
El tier de prioridad y el puntaje **solo aplican a entidades `tipo: persona`**. Instituciones y
ensayos clínicos siguen mostrando su cantidad de hechos/conexiones como contexto, pero no llevan
badge de prioridad — mostrarles un tier sugeriría que "una institución es más prioritaria que
otra" para investigar, lo cual el charter no plantea.

## Las siete dimensiones — mapeadas a lo que el modelo de datos actual puede sostener

El charter define 7 dimensiones (§5B). Hoy el modelo de datos (`hecho.tipo`) solo distingue
`publicacion`, `ensayo_clinico`, `afiliacion` y `congreso` — no separa guías/consenso, docencia, o
liderazgo en sociedades como tipos propios todavía. En vez de inventar una separación que los
datos no sostienen, esta v1 muestra **6 filas visibles**, siendo honesta sobre cuáles hoy están
vacías por falta de fuente, no por diseño:

| Fila mostrada | Dimensión(es) del charter | Fuente en el modelo actual |
|---|---|---|
| Ensayos clínicos | A (rol en ensayo) | `hecho.tipo === "ensayo_clinico"` |
| Publicaciones | A (publicaciones) | `hecho.tipo === "publicacion"` |
| Guías y consensos | A (guías) | subconjunto de `publicacion` cuyo texto declara explícitamente ser guía/consenso/recomendación (ver heurística abajo) |
| Congresos y docencia | B + E (fusionadas — incorrecto separarlas hasta tener fuente propia para cada una) | `hecho.tipo === "congreso"` — **hoy siempre 0**, gap ya documentado en README |
| Sociedades y liderazgo | B/F | sin fuente hoy — **siempre 0**, mostrado igual (el charter pide visibilidad incluso cuando está vacío) |
| Red y afiliaciones | C/G | `connectionCount(id)` — con tope explícito para que el tamaño de red no domine |

## Reglas por dimensión

**Ensayos clínicos** — 2 pts por ensayo distinto; ×2 si la fase es III/IV (mismo peso que v1,
porque sigue siendo el único dato de "importancia" que una fuente real declara). Tope de la
dimensión: 5 ensayos contados (los siguientes se siguen mostrando como evidencia, no suman más).
Tope de puntos de la dimensión: 20.

**Publicaciones** — 2 pts por publicación. No se pesa por revista (seguimos sin inventar un dato
de impacto que la fuente no declara — mismo principio de v1). Tope: 5 publicaciones contadas, 10
puntos.

**Guías y consensos** — heurística: un hecho `publicacion` cuyo texto contiene explícitamente
"guía", "consenso", "guideline", "consensus" o "recomendaciones de" (no se infiere de otra forma).
4 pts por guía detectada, tope 2 guías = 8 puntos. Es una re-clasificación de un hecho que ya está
citado con su fuente — no agrega ningún dato nuevo, solo le da el peso más alto que el charter
pide para esta señal.

**Congresos y docencia** — 1 pt por hecho `congreso`, tope 5 = 5 puntos. Hoy será 0 para todos:
gap de fuente ya reconocido en README/ROADMAP, no un error de este cálculo.

**Sociedades y liderazgo** — sin campo propio en el modelo de datos todavía. Se muestra la fila
con 0 y una nota explícita ("sin fuente identificada todavía"), nunca oculta.

**Red y afiliaciones** — 1 pt por conexión, tope 5 puntos (evita que un nodo muy conectado dentro
de una sola institución (ej. FALP) domine el puntaje de sus médicos solo por tamaño de red).

**Total máximo teórico hoy:** 20 + 10 + 8 + 5 + 0 + 5 = 48 puntos, antes de recencia.

## Recencia — decaimiento por hecho, no por entidad

Cada hecho se pesa según su propia fecha antes de sumarse a su dimensión (charter §5B):

| Antigüedad | Multiplicador |
|---|---|
| < 1 año | ×1.0 |
| 1–3 años | ×0.7 |
| 3–5 años | ×0.4 |
| > 5 años | ×0 para el puntaje — el hecho se sigue mostrando en la ficha como evidencia histórica, nunca se oculta ni se borra |
| Sin fecha en la fuente | ×0.4 (tratado como incertidumbre media, ni se premia ni se penaliza al máximo) |

## Confianza — separada de la prioridad, no combinada

El charter pide mostrar "evidence confidence" aparte del puntaje, nunca mezclada. Se deriva del
campo `confianza` que ya existe por hecho:

- **Alta**: todos (o casi todos) los hechos de la entidad están `confirmado`.
- **Pendiente de revisión**: el caso de hoy para el 100% de la muestra — ningún hecho ha pasado
  revisión humana todavía (ver README, "Auditoría 2026-08-10" y Fase 2 del Roadmap, que sigue sin
  hacerse formalmente). No es un defecto del cálculo: es honesto sobre el estado real del dataset.
- **Media**: mezcla de `confirmado` y `probable`/`pendiente` (no aplica todavía, pero el mecanismo
  ya queda construido para cuando la revisión humana empiece a diferenciar).

## Tier de prioridad — interpretación, no el número crudo

El charter pide que el usuario vea un tier (Alta/Media/Monitorear), no solo un número (§5, tabla
de prioridad). Umbrales v1, recalibrados el 2026-08-16 contra el **rango real logrado en la
muestra actual** (1–11 puntos, 18 personas), no el máximo teórico de 48 — con el primer umbral
(≥12) nadie en el dataset alcanzaba nunca "Prioridad alta", lo cual se veía roto más que
riguroso. Van a necesitar recalibrarse de nuevo a medida que la muestra crezca y el rango real
de puntajes se mueva:

| Tier | Puntaje (post-recencia) |
|---|---|
| **Alta** | ≥ 8 |
| **Media** | 3–7 |
| **Monitorear** | 1–2 |

Una persona con **0 puntos no debería aparecer** como candidato priorizable — pero el charter dice
explícitamente que una sola señal ya alcanza para entrar al mapa (§5, "How the ranked output is
used"); en la práctica, toda persona en esta muestra tiene al menos un hecho, así que el tier
"Monitorear" es el piso real, no un caso vacío.

## Qué NO cambia

- Sigue sin ser un ranking de "a quién contactar primero" — el charter es explícito en que la
  decisión de contacto sigue siendo del MSL (§5, "The ranking supports where to invest research
  time... remains a deliberate MSL and compliance-governed decision").
- Sigue siendo transparente: cada componente del puntaje se puede desglosar hasta el hecho y su
  fuente, igual que v1.
- No se pesa por prestigio institucional, tamaño de red sin tope, ni reputación no verificable —
  exactamente lo que el charter prohíbe en §5B, principio 5.
