# Licencia de los datos

La base de datos de KOL Radar —todo lo que está en `data/`, en particular
`data/sample/perfiles-muestra.json` y `data/geo/ubicaciones-instituciones.json`— se publica bajo
la **Open Database License (ODbL) 1.0**.

> This "KOL Radar — Chile" database is made available under the Open Database License:
> <https://opendatacommons.org/licenses/odbl/1-0/>. Any rights in individual contents of the
> database are licensed under the terms of their original sources, listed below.

El código del sitio y de los scripts tiene otra licencia (MIT): ver [`../LICENSE`](../LICENSE).

## Qué permite la ODbL, en corto

- **Usar, copiar, distribuir y adaptar** la base, también con fines comerciales.
- **Atribuir**: quien la use tiene que decir que viene de KOL Radar y de las fuentes de abajo.
- **Compartir igual**: si alguien publica una base *derivada* (esta base modificada o combinada),
  tiene que publicarla también bajo ODbL.
- **Mantener abierta**: no se puede redistribuir con restricciones técnicas que impidan reusarla
  sin ofrecer también una versión sin ellas.

Resumen oficial: <https://opendatacommons.org/licenses/odbl/summary/>

## Por qué ODbL y no otra

Las coordenadas de 27 instituciones (en esta versión) y parte de las direcciones vienen de **OpenStreetMap**, que se
licencia bajo ODbL con cláusula de "compartir igual": una base derivada de OpenStreetMap que se
publica tiene que usar la misma licencia. Elegir otra (por ejemplo CC BY-NC, "no comercial")
obligaría antes a sacar esos puntos de la base. Si en algún momento se quiere cambiar la licencia,
ese es el primer paso: regenerar `ubicaciones-instituciones.json` sin OpenStreetMap.

## Fuentes y sus términos

Cada hecho de la base lleva la URL exacta de donde salió. Las fuentes, con sus términos:

| Fuente | Qué aporta | Términos |
|---|---|---|
| ClinicalTrials.gov (NLM, EE. UU.) | Ensayos, sedes, intervenciones, patrocinador | Dominio público en EE. UU.; se pide citar la fuente — <https://clinicaltrials.gov/about-site/terms-conditions> |
| PubMed (NLM) | Autoría, afiliación, revista, fecha | Metadatos bibliográficos (hechos); los resúmenes no se reproducen |
| SciELO Chile | Autoría y afiliación en revistas chilenas | CC BY en la mayoría de las revistas |
| Buscador de estudios clínicos de la CIF (estudiosclinicos.cl) | Qué centros tienen abierto cada ensayo que hoy recluta | Solo se toma el hecho (ensayo ↔ centro) con su URL; no se reproducen textos ni contactos |
| DEIS, Minsal — Establecimientos de Salud (datos.gob.cl) | Dirección y coordenadas oficiales de hospitales y clínicas | CC0 |
| OpenStreetMap (Nominatim) | Coordenadas cuando el DEIS no tiene el establecimiento | ODbL — © colaboradores de OpenStreetMap |
| geoBoundaries (BCN Chile, OCHA ROLAC) | Límites de regiones y comunas (`data/geo/chile-regiones-comunas.json`) | CC BY 3.0 IGO |
| Sitios institucionales y de terceros | Evidencia puntual de una afiliación o de una sede | Solo el hecho con su URL |

## Datos personales: la licencia no alcanza

La base nombra a **profesionales de la salud**. Un nombre asociado a una afiliación o a un ensayo es
un **dato personal** aunque la fuente sea pública. La ODbL da permiso sobre los derechos de autor y
de base de datos; **no da ninguna base legal para tratar datos personales**. Quien reutilice esta
base se vuelve responsable de su propio tratamiento y tiene que cumplir la ley chilena:

- **Ley 19.628** sobre protección de la vida privada, y la **Ley 21.719**, que la reforma y entra
  en vigencia el **1 de diciembre de 2026**. La Ley 21.719 elimina la excepción amplia de las
  "fuentes de acceso público": que un dato sea público no basta, el tratamiento necesita una base
  de licitud (por ejemplo, interés legítimo) y respetar los derechos de las personas —acceso,
  rectificación, supresión, oposición, portabilidad y bloqueo—.
- **Usos incompatibles** con el origen profesional y científico de los datos —perfilamiento
  comercial de médicos, marketing directo, evaluación de desempeño, decisiones automatizadas sobre
  personas— probablemente no superen el test de interés legítimo. Este proyecto no los hace y no
  los respalda.
- Si una persona pide corregir o retirar su ficha de KOL Radar, **las copias derivadas deberían
  aplicar el mismo cambio**. El historial de correcciones de este repositorio es público.

Esto no es asesoría legal. Antes de usar la base en un contexto comercial o institucional, hay que
revisarlo con un abogado.
