# Evaluación de interés legítimo — BORRADOR

Documento que exige el uso del **interés legítimo** como base de licitud (art. 13 letra d de la Ley
19.628, reformada por la Ley 21.719): muestra por escrito por qué el tratamiento es legítimo,
necesario y proporcionado. Borrador del 2026-09-29, para validar con un abogado. El análisis
completo, con fuentes, está en [`REVISION_LEGAL.md`](REVISION_LEGAL.md).

**Responsable**: Francisco Kirhman. **Tratamiento**: KOL Radar, mapa público de profesionales
de la oncología activos en Chile, con evidencia pública trazable.

## 1. ¿Hay un interés legítimo?

**Sí.** Hay tres, y ninguno es comercial respecto de las personas nombradas:

- **De quienes usan el sitio** (terceros): profesionales de Medical Affairs, investigación clínica y
  sociedades científicas necesitan saber quién está activo en cada área de la oncología en Chile y con
  qué evidencia, para colaborar en investigación, educación médica y ensayos. Hoy eso toma horas de
  búsqueda manual por fuente.
- **Público**: la transparencia sobre la investigación clínica en Chile —qué ensayos corren, dónde y
  con quién— es de interés público; los registros de ensayos existen justamente para eso.
- **Del responsable**: desarrollar una herramienta de información científica abierta, con código MIT
  y datos ODbL.

El interés es **lícito, concreto y actual**: el producto funciona hoy, y la necesidad está descrita en
`PRODUCT_CHARTER.md`.

## 2. ¿Es necesario el tratamiento para ese interés?

| Dato | ¿Necesario? | Por qué |
|---|---|---|
| Nombre tal como lo publica la fuente | Sí | Sin nombre no hay a quién atribuir la evidencia. |
| Afiliación institucional | Sí | Es la pregunta central ("¿quién, dónde?"). |
| Ensayos donde figura, con su rol | Sí | Es la evidencia de actividad clínica. |
| Publicaciones y coautorías | Sí | Es la evidencia de actividad científica y de red. |
| Ciudad de la institución | Sí | Para planificar; es de la institución, no de la persona. |
| Datos de contacto personales, fotos, datos de salud, opiniones | **No se tratan** | No hacen falta para la finalidad. |
| Resultado de inspecciones del ISP | **No se trata** | Es una evaluación regulatoria, no evidencia de actividad. |
| **Tier público** ("Prioridad alta / media / Monitorear") | **Sí, con garantías** (decisión 2026-09-30) | Ordena la investigación de quien prepara un territorio. Es elaboración de perfiles: se sostiene con la evaluación de impacto (`EVALUACION_IMPACTO.md`), la explicación en cada ficha y la oposición al indicador. |

**Alternativas menos intrusivas consideradas**: publicar solo instituciones y ensayos, sin personas
(no responde la pregunta de la finalidad); pedir consentimiento a cada persona (inviable a esta
escala y no es la base elegida); mostrar conteos descriptivos en vez de un tier (viable, ver §4).

## 3. Ponderación: intereses del responsable y de terceros contra derechos de las personas

**A favor del tratamiento**
- Todo dato es **profesional** y fue publicado por la propia persona (autoría, rol declarado en un
  registro) o por un registro público o regulatorio (ClinicalTrials.gov, ISP), en su calidad profesional.
- Las personas nombradas pueden **esperar razonablemente** que su actividad científica y clínica
  publicada sea consultada por colegas y por la industria: ese es el propósito de publicarla.
- **Trazabilidad**: cada dato enlaza a su fuente; nada se afirma que la fuente no diga.
- **Garantías**: canal de corrección y retiro, plazos legales, bloqueo en 2 días hábiles, registro de
  exclusiones que las recolecciones respetan, purga del historial ante supresión, sin datos sensibles,
  sin fines comerciales sobre las personas.

**En contra del tratamiento**
- **Compilación**: juntar fuentes en una ficha crea una vista que no existía, más fácil de consultar
  que cada fuente por separado.
- **Elaboración de perfiles**: el tier por persona evalúa su actividad profesional de forma automatizada
  y lo muestra públicamente. Un rótulo como "Monitorear" puede afectar la reputación de alguien.
- **Errores de identidad**: con 1 de 3.010 hechos revisado por una persona, y 14 fichas del ISP ligadas o
  creadas sin revisión de identidad, existe el riesgo de atribuir a alguien trabajo ajeno.
- **Alcance**: un sitio indexado en buscadores multiplica tanto el beneficio como el daño de un error.

**Resultado**
- Para nombre, afiliación, ensayos, publicaciones y coautorías, con sus garantías: **el interés
  legítimo prevalece.**
- Para el **tier público por persona**: prevalece **con las garantías agregadas el 2026-09-30**:
  explicación en cada ficha, cálculo público, oposición al indicador sin salir del sitio y evaluación de
  impacto (`EVALUACION_IMPACTO.md`).
- Para las **fichas sin revisión de identidad**: prevalece de forma **condicionada** a que la nota de
  identidad sea visible (lo es) y a que la revisión se haga pronto.

## 4. Medidas que sostienen esta evaluación

| Medida | Estado |
|---|---|
| Fuente enlazada en cada dato | Hecho |
| Sin datos sensibles, contactos personales ni fotos | Hecho |
| Canal de corrección y retiro con plazos legales | Hecho (`PROCESO_SOLICITUDES.md`) |
| Registro de exclusiones respetado por toda recolección | Hecho |
| Purga del historial ante supresión | Procedimiento escrito |
| Nota visible en fichas con identidad no revisada | Hecho |
| Aviso de privacidad completo (art. 14 ter) | Hecho: publicado en `web/privacidad.html` (2026-09-30) |
| Decisión sobre el tier público | Hecho: se mantiene con garantías (2026-09-30) |
| Revisión humana de identidades | Pendiente |

## 5. Revisión

Esta evaluación se revisa cuando cambie la finalidad, cuando entre una fuente o categoría de dato
nueva, cuando cambie el puntaje, o una vez al año.

Aprobada por: Francisco Kirhman · Fecha: 2026-09-30 · Revisada por abogado: [pendiente]
