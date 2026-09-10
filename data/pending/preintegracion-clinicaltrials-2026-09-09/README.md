# Preintegración — ClinicalTrials.gov, 2026-09-09

**Nada de esto está integrado.** `data/sample/perfiles-muestra.json` no fue modificado. Este
directorio es el artefacto auditable que permite decidir, con evidencia, si la recolección entra
a la muestra pública y en qué forma.

## Cómo se recolectó

API v2 de ClinicalTrials.gov, misma sintaxis Essie ya usada en el proyecto, una consulta por área:

    AREA[LocationCountry]Chile AND AREA[ConditionSearch]"<condición en inglés>"

19 áreas oncológicas. Fecha de consulta: 2026-09-09. De ahí salieron 579 ensayos con
al menos una ubicación declarada en Chile; **314** pasan el umbral de admisión.

## Umbral de admisión de un ensayo (acumulativo)

1. Identidad estable por NCT y URL exacta de ClinicalTrials.gov.
2. La API declara al menos una ubicación con país Chile.
3. Se conserva la **condición declarada por la fuente**, no una interpretación clínica propia.
4. Al menos una sede chilena con nombre institucional específico, resoluble a una institución
   canónica mediante un alias documentado.
5. Se conserva el texto original de la sede, el estado del ensayo y la fecha de recuperación.

Los marcadores del patrocinador —`Research Site`, `Novartis Investigative Site`, `Site CL56001`—
**no crean instituciones ni vínculos**. Las sedes que no calzan con ningún alias documentado
quedan en cola de resolución: son trabajo pendiente, no evidencia negativa.

Este umbral admite un ensayo y su vínculo con una institución. **No autoriza crear una persona.**

## Qué hay acá

| Archivo | Contenido | KB |
|---|---|---|
| `ensayos_candidatos.json` | 314 ensayos: NCT, URL exacta, condición e intervenciones declaradas por la fuente, y cada sede chilena con su texto original y el alias aplicado | 559 |
| `instituciones_candidatas.json` | 47 instituciones canónicas (33 nuevas) con todos los alias textuales observados | 47 |
| `sedes_sin_resolver.json` | 253 sedes en cola de resolución | 24 |
| `placeholders_excluidos.json` | 645 sedes descartadas por ser marcadores del patrocinador | 14 |
| `personas_candidatas.json` | 129 contactos clasificados, **ninguno aprobado** | 70 |
| `simulacion.json` | Qué pasaría al integrar, medido corriendo el JavaScript real | 1 |
| `resumen.json` | Conteos | 1 |

## Personas: clasificadas, ninguna creada ni fusionada

| Clasificación | N | Qué significa |
|---|---|---|
| `no_persona_utilizable` | 60 | `Study Coordinator`, `Principal Investigator` sin nombre, contacto corporativo, código de sitio |
| `posible_coincidencia` | 48 | Abreviación, segundo apellido ausente, orden distinto o institución insuficiente. Queda en cola |
| `reutilizacion_propuesta` | 16 | Nombre completo idéntico **y** sede que apunta a una institución ya en la muestra |
| `persona_nueva_propuesta` | 5 | La fuente la nombra y le declara rol individual en una sede chilena resoluble |

Cada fila trae `decision_humana`, `revisor` y `fecha_decision` vacíos. **Ninguna ficha se creó,
se reutilizó ni se fusionó.** Un título `MD` es lo que declara esa fuente, no resuelve identidad.

Caso de referencia: `Christian Caglevic Medina, MD` frente a la ficha existente
`Christian Caglevic` queda como **`posible_coincidencia`**, con la URL del ensayo y la ficha
compatible listadas, para que lo decida una persona.

## Qué pasaría al integrar (medido, no estimado)

Se corrió el `computePriority` real extraído de `web/index.html` sobre el dataset simulado.

| | Hoy | A: solo ensayos e instituciones | B: si además se aprobaran las personas |
|---|---|---|---|
| Entidades | 173 | **446** | 451 |
| Vínculos | 349 | **1067** | 1088 |
| Personas con puntaje distinto | — | **0** | 7 |
| Tiers | {'alta': 12, 'media': 48, 'monitorear': 10} | **{'alta': 12, 'media': 48, 'monitorear': 10}** | {'alta': 13, 'media': 52, 'monitorear': 10} |
| Personas sobre el tope de 5 ensayos | 0 | 0 | **1** |

Los dos resultados que importan:

- **El escenario A no le cambia el puntaje a nadie.** Ensayos e instituciones no entran en
  ninguna dimensión del puntaje de una persona, y sin personas aprobadas no se crean vínculos
  nuevos hacia ellas. Los tiers quedan idénticos. El riesgo para el modelo de puntaje es cero;
  lo que cambia es el tamaño del grafo, que se multiplica por 2,6 en entidades y por 3 en vínculos.
- **El escenario B es el primero en ejercer un tope por dimensión.** Una persona pasaría a tener
  más de cinco ensayos únicos. Ahí es exactamente donde el `slice(0, cap)` viejo habría
  seleccionado por orden alfabético de URL en vez de por aporte. La corrección de `dimensionPts`
  no era teórica: es la condición para que esta expansión sea correcta.

## Límites

- Ningún hecho fue corroborado contra la fuente por una persona. Todo entra como `pendiente`.
- Que una URL tenga forma válida no prueba su contenido, disponibilidad ni que respalde el hecho.
- La resolución de sedes usa alias textuales. Un alias mal escrito uniría dos centros distintos;
  por eso cada alias observado queda listado en `instituciones_candidatas.json` para revisión.
- Las 253 sedes sin resolver incluyen centros chilenos reales. Descartarlas
  no significa que no existan.
- Esto no constituye cobertura completa de oncología en Chile, ni validación con un MSL.
