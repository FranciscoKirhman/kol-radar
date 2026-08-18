# Muestra de datos — cáncer de pulmón en Chile

Ejercicio de traer datos **reales** (no sintéticos) de las fuentes ya
documentadas en `README.md`, para descubrir qué campos son confiables antes de
diseñar la página de perfil. Esto se hizo con una muestra de prueba, no la
validación manual de 30 fichas que el Roadmap de `README.md` define como Fase
2 (esa etapa formal sigue sin hacerse). Los datos completos están en
[`data/sample/perfiles-muestra.json`](data/sample/perfiles-muestra.json) — 76
entidades reales (18 personas, 10 instituciones, 48 ensayos clínicos) y 119
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
