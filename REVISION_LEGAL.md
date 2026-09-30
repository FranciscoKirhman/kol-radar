# Revisión de protección de datos — KOL Radar

Fecha: 2026-09-29. Hecha por Claude a pedido de Francisco, con el método y el orden que seguiría un
abogado de protección de datos: qué ley rige, quién responde, con qué base legal, qué hay que informar,
qué derechos hay que atender y dónde está el riesgo.

> **No es asesoría legal ni la reemplaza.** Quien la escribe no es abogado y no puede representarte.
> Las citas de la ley salen de reproducciones del texto y de comentarios de terceros (enlazados abajo),
> no del Diario Oficial. Sirve para llegar a la reunión con un abogado con el trabajo hecho y las
> preguntas correctas, no para saltársela.

---

## 1. Qué ley rige, y desde cuándo

| Período | Norma | Qué importa para KOL Radar |
|---|---|---|
| Hasta el 30-11-2026 | Ley 19.628, texto actual | El art. 4 no exige autorización para tratar datos de **fuentes accesibles al público** contenidos en listados de una categoría de personas que solo indican, entre otros, su **profesión o actividad**. Un listado de oncólogos con su afiliación y sus ensayos encaja razonablemente ahí. |
| Desde el 01-12-2026 | Ley 19.628 reformada por la **Ley 21.719** | Las fuentes de acceso público dejan de ser una base de licitud: su tratamiento "se someterá a las disposiciones de esta ley" (art. 2 letra i). Hace falta una base del art. 13; para KOL Radar, el **interés legítimo** (art. 13 letra d). |
| En trámite | Proyecto de ley que posterga la Ley 21.719 al **01-12-2027** | Ingresó al Senado el 01-09-2026 con suma urgencia; al 22-09-2026 seguía en primer trámite. **Mientras no se apruebe, la fecha es el 1 de diciembre de 2026.** Conviene planificar con esa fecha y tratar la postergación como holgura, no como plan. |

## 2. Qué datos se tratan

- **Son datos personales**: nombre de un profesional identificado, su afiliación, los ensayos en que
  figura, sus publicaciones y coautorías, y un puntaje calculado sobre él. Que la fuente sea pública
  no les quita ese carácter.
- **No son datos sensibles** en el sentido de la ley: no hay datos de salud de nadie (los ensayos se
  describen por su protocolo, no por sus pacientes), ni origen, ideología, vida sexual o biometría.
- **Hay elaboración de perfiles.** El sitio calcula para cada persona un puntaje y un tier
  ("Prioridad alta", "Prioridad media", "Monitorear") a partir de su actividad, y permite filtrar por
  él. La ley define la elaboración de perfiles como el tratamiento automatizado para evaluar o
  predecir, entre otros, el **rendimiento profesional** de una persona. El puntaje es eso. Es el punto
  más delicado de toda esta revisión (§5).
- **Hay compilación entre fuentes.** Cada dato suelto ya es público, pero la ficha que junta PubMed,
  ClinicalTrials.gov, la CIF, el ISP y sitios institucionales en un solo lugar no existía antes. La
  compilación es parte del valor del producto y también parte del impacto en la persona: se pondera
  en §4.

## 3. Quién es el responsable

La ley obliga a identificar al responsable, con domicilio, correo y medio de contacto, y a publicarlo
de forma permanente (art. 14 ter). Hoy nadie figura: `contacto.responsable` es `null` y
`PRIVACIDAD.md` tiene el nombre entre corchetes.

- Si el proyecto lo lleva Francisco a título personal, **el responsable es Francisco**, persona natural,
  y responde con su patrimonio. Un abogado puede evaluar si conviene una persona jurídica (una
  fundación, una SpA o la universidad, si se cede) para separar ese riesgo.
- GitHub (Pages y el repositorio) aloja los datos en servidores fuera de Chile. Eso lo convierte en un
  **encargado** o proveedor, y la ley pide informar las **transferencias internacionales** y el nivel
  de protección del país de destino (art. 14 ter letra h).

**Pregunta para el abogado:** ¿persona natural o jurídica como responsable? Y ¿GitHub como
encargado exige algo más que informarlo (cláusulas, términos del servicio)?

## 4. Base de licitud: interés legítimo

El art. 13 letra d) permite tratar datos "cuando el tratamiento sea necesario para la satisfacción de
intereses legítimos del responsable o de un tercero, siempre que con ello no se afecten los derechos y
libertades del titular". La doctrina chilena y comparada lo trata como la base que **exige más rendición
de cuentas**: hay que poder mostrar, por escrito, la evaluación en tres pasos. El borrador de esa
evaluación está en [`EVALUACION_INTERES_LEGITIMO.md`](EVALUACION_INTERES_LEGITIMO.md). Resumen:

| Paso | Conclusión |
|---|---|
| **Finalidad legítima** | Sí: dar a Medical Affairs y a la investigación clínica una vista trazable de quién está activo en oncología en Chile, con información científica y profesional de interés público. |
| **Necesidad** | Sí para nombre, afiliación, ensayos, publicaciones y coautorías: sin ellos el producto no existe. **No demostrada** para el puntaje público por persona: la finalidad se cumple mostrando la evidencia sin ordenarla en un ranking visible para cualquiera. |
| **Ponderación** | Favorable para los datos de actividad profesional (ya publicados por la propia persona o por registros regulatorios, en su rol profesional, sin datos sensibles, con fuente enlazada y derecho de oposición). **Desfavorable o dudosa** para el tier público y para las fichas con identidad no revisada, por el riesgo de atribuir a alguien trabajo ajeno. |

## 5. Hallazgos, de más a menos grave

### 5.1 El puntaje público por persona es elaboración de perfiles — **alto → mitigado**

> **Decisión del 2026-09-30: se mantiene, con garantías.** Evaluación de impacto en
> [`EVALUACION_IMPACTO.md`](EVALUACION_IMPACTO.md). Cada ficha explica qué es el indicador y qué no es,
> enlaza su cálculo y ofrece oponerse ("¿Es tu ficha? Pide que no se te calcule"); quien se opone
> queda sin nivel en todo el sitio (`scripts/exclusiones.py sin-indicador`). Los avisos ya no dicen
> "no es una evaluación de desempeño". Lo que sigue abajo es el análisis que llevó a esa decisión.

- El art. 8 bis da derecho a oponerse a decisiones basadas únicamente en tratamiento automatizado,
  incluida la elaboración de perfiles, que produzcan efectos jurídicos o **afecten significativamente**
  a la persona. Un rótulo público de "Monitorear" junto al nombre de un médico, calculado sin revisión
  humana, puede afectar su reputación profesional.
- Cuando hay elaboración de perfiles, la ley pide una **evaluación de impacto** (EIPD) y publicar
  **información sobre la lógica aplicada** (art. 14 ter letra l).
- `PRIVACIDAD.md` dice hoy que no hay "ninguna evaluación de desempeño". **Eso no es exacto mientras el
  tier se publique**, y un aviso inexacto es peor que uno incompleto.
- **Recomendación**: sacar el tier y el puntaje de la vista pública de personas (dejarlos para uso
  interno o detrás de una acción explícita del usuario, como "ordenar por actividad"), o reemplazar el
  rótulo evaluativo por conteos descriptivos ("12 ensayos, 4 publicaciones desde 2022"). Si se mantiene,
  hacer la EIPD y publicar la lógica (el `SCORING.md` ya la describe; falta enlazarla y decirlo en el
  aviso). Es una decisión de producto, no técnica: hay que tomarla antes del 1 de diciembre.

### 5.2 Identidades sin revisar — **alto**
- El principio de **calidad** exige datos exactos. Atribuirle a un médico el ensayo o el paper de un
  homónimo es el error más dañino que puede cometer este sitio.
- Hoy: 1 de 3.010 hechos revisado por una persona. Además, el 2026-09-29 entraron **8 fichas nuevas del
  ISP sin revisión de identidad** y se ligaron **10 nombres a 6 fichas** por coincidencia de nombre. Cada
  ficha lo dice, lo que mitiga pero no resuelve.
- **Recomendación**: priorizar la revisión humana de esas 14 fichas y de las fusiones pendientes antes
  del 1 de diciembre. Mientras tanto, mantener visible la nota de identidad (ya está).

### 5.3 Aviso de privacidad incompleto — **alto, fácil de resolver**
Lo que el art. 14 ter pide publicar de forma permanente, contra lo que tiene `PRIVACIDAD.md`:

| Exigencia (art. 14 ter) | Estado |
|---|---|
| a) Política de tratamiento y su fecha | Borrador, sin fecha |
| b) Identificación del responsable (y del encargado de prevención, si lo hay) | **Falta** |
| c) Domicilio, correo y medio de contacto | Correo sí; **domicilio falta** |
| d) Categorías de datos, destinatarios, finalidades, base legal | Parcial: faltan destinatarios (cualquiera, sitio abierto; reutilizadores bajo ODbL) |
| e) Medidas de seguridad | **Falta** |
| f) Derechos del titular | Sí |
| g) Derecho a reclamar ante la Agencia | **Falta** |
| h) Transferencias internacionales | **Falta** (GitHub, EE. UU.) |
| i) Plazo de conservación | Sí, genérico |
| j) Fuente de los datos | Sí |
| k) Revocar consentimiento | No aplica (la base no es el consentimiento): decirlo |
| l) Decisiones automatizadas y lógica aplicada | **Falta, y hoy dice lo contrario** (ver 5.1) |

Ya incorporé al borrador todo lo que no depende de una decisión tuya (ver `PRIVACIDAD.md`); quedan
entre corchetes el responsable, el domicilio y la decisión sobre el puntaje.

### 5.4 Indexación en buscadores — **medio**
- No es ilegal que el sitio esté en Google. Lo que cambia es el **alcance**: indexado, cualquiera que
  busque el nombre de un médico puede encontrar su ficha con un tier al lado, y el daño de un error de
  identidad (5.2) o de un rótulo (5.1) se multiplica. En la ponderación del interés legítimo, más
  alcance pesa en contra.
- Por eso la auditoría propuso `noindex` hasta tener responsable y aviso: no porque el sitio no deba
  encontrarse, sino para que lo primero que encuentre alguien sea una versión que ya cumple. Es tu
  decisión; si preferís indexar desde ya, lo que más reduce el riesgo es resolver 5.1 y 5.3 primero.

### 5.5 Reutilización bajo ODbL — **medio**
- La licencia abierta es compatible con el interés legítimo, pero cada tercero que reutilice la base
  pasa a ser responsable de su propio tratamiento. El aviso y `data/LICENSE.md` ya lo dicen.
- Falta: que la exclusión se propague. Quien bajó la base antes de un retiro sigue teniendo la ficha.
  **Recomendación**: publicar en el repositorio el número de versión y pedir en la licencia que los
  reutilizadores actualicen o respeten las supresiones. No se puede forzar, pero se puede pedir.

### 5.6 Derechos y procedimiento — **cumplido en lo operativo**
- Canal: correo publicado. Plazos: 30 días corridos, prorrogables una vez (art. 11); bloqueo en 2 días
  hábiles (art. 8 ter). Gratuidad: sí. Registro de exclusiones que las recolecciones respetan, y purga
  del historial en supresión u oposición. Todo en `PROCESO_SOLICITUDES.md`.
- **Verificación de identidad**: la hace Francisco caso a caso (decisión del 2026-09-29). Conviene dejar
  anotado en cada caso qué se pidió y por qué bastó, sin guardar documentos de identidad.

### 5.7 Seguridad y brechas — **bajo**
- El sitio es estático y público: no hay credenciales ni datos no publicados que filtrar, salvo el
  registro de exclusiones (fuera del repo, con huellas y clave). La obligación de notificar brechas a
  la Agencia existe igual; conviene tener escrito a quién se avisa.

### 5.8 Datos del ISP — **bien resuelto**
- De la planilla de inspecciones solo se usa centro, protocolo e investigador principal. No se copian
  resultados ni motivos de inspección, que sí serían una evaluación del profesional.

## 6. Sanciones, para dimensionar

La ley clasifica las infracciones en leves, graves y gravísimas (art. 34), con multas de hasta
**5.000, 10.000 y 20.000 UTM** respectivamente (art. 35), y porcentajes de los ingresos en caso de
reincidencia. Fiscaliza la Agencia de Protección de Datos Personales.

## 7. Lista para llegar al abogado

1. Responsable: persona natural o jurídica; domicilio para el aviso.
2. ¿Basta el interés legítimo tal como está en `EVALUACION_INTERES_LEGITIMO.md`?
3. El tier público por persona: ¿es "afectar significativamente"? ¿Se mantiene, se transforma o se saca?
4. ¿Hay deber de informar individualmente a cada persona cuya ficha se crea con datos de terceros, o
   basta el aviso publicado?
5. GitHub como encargado y transferencia internacional: ¿qué hay que informar o firmar?
6. Estado del proyecto de postergación al 2027.

## 8. Qué hacer antes del 1 de diciembre de 2026

| # | Qué | Quién |
|---|---|---|
| 1 | ~~Decidir qué pasa con el tier público (5.1)~~ — se mantiene con garantías (2026-09-30) | Francisco |
| 2 | ~~Responsable y domicilio en el aviso; publicarlo como página del sitio~~ — hecho (2026-09-30), falta revisión de abogado | Francisco + abogado |
| 3 | Revisar a mano las 14 fichas del ISP y las fusiones pendientes | Francisco |
| 4 | Validar la evaluación de interés legítimo | abogado |
| 5 | Decidir indexación con 1–3 resueltos | Francisco |

---

Fuentes consultadas:
[Texto de la Ley 21.719 (Informática Jurídica)](https://www.informatica-juridica.com/ley/ley-no-21-719-de-14-de-noviembre-de-2024/) ·
[BCN, Ley 21.719](https://www.bcn.cl/leychile/Navegar/imprimir?idNorma=1209272) ·
[Bases de licitud y deberes de información (Hackmetrix)](https://blog.hackmetrix.com/bases-de-licitud-ley-21719-chile/) ·
[El interés legítimo como nueva base de licitud (Repositorio U. de Chile)](https://repositorio.uchile.cl/bitstream/handle/2250/206588/El-interes-legitimo-como-nueva-base-de-licitud-para-el-tratamiento-de-datos-personales.pdf?sequence=1) ·
[Pablo Viollier sobre fuentes de acceso público (Actualidad Jurídica)](https://actualidadjuridica.doe.cl/pablo-viollier-sobre-fuentes-de-acceso-publico-que-un-dato-sea-publico-no-necesariamente-significa-que-se-puede-procesar-libremente/) ·
[Decisiones automatizadas y lógica aplicada (Hackmetrix)](https://blog.hackmetrix.com/mapear-algoritmos-ia-ley-21719/) ·
[Multas y sanciones (Prey)](https://preyproject.com/es/blog/multas-y-sanciones-ley-21719) ·
[Plazos para responder derechos (Alayia Trust)](https://alayiatrust.com/blog/como-responder-derechos-arsop) ·
[Proyecto de postergación (Carey)](https://www.carey.cl/gobierno-ingresa-proyecto-de-ley-que-posterga-en-un-ano-entrada-en-vigor-de-la-ley-sobre-proteccion-de-datos-personales) ·
[Postergación al 2027: qué dice el proyecto](https://protecciondatosweb.cl/postergacion-de-la-ley-21719-al-2027/)
