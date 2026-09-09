# Cómo trabajar en KOL Radar si sos una IA

Este archivo es el traspaso para un colaborador que no estuvo en las conversaciones previas
—ChatGPT, Gemini, o cualquier otro— y que va a opinar o proponer cambios sobre este proyecto.
Está escrito para que lo leas entero antes de proponer nada.

**Link para leerlo tú mismo:**
<https://raw.githubusercontent.com/FranciscoKirhman/kol-radar/main/COLABORACION_IA.md>

---

## 1. Qué es esto

KOL Radar mapea especialistas médicos (KOLs) activos en Chile a partir de **evidencia pública
verificable**, para que un Medical Science Liaison pueda responder en minutos una pregunta que
hoy le toma horas de búsqueda manual:

> ¿Quién está activo en esta área clínica en Chile, y con qué evidencia se sostiene esa conclusión?

Lo construye Francisco Kirhman, Ingeniero en Biotecnología Molecular. Es un prototipo público
en GitHub Pages: <https://franciscokirhman.github.io/kol-radar/>

No es un CRM, no es un ranking comercial, y no reemplaza el criterio humano. Cada afirmación
sobre una persona lleva su URL de origen y se puede auditar haciendo click.

---

## 2. La regla que importa más que todas las demás

**Nunca inventes datos.** Ni un nombre, ni una afiliación, ni un PMID, ni un NCT, ni una fecha.

Este es el modo de falla número uno cuando una IA colabora acá, y es fácil caer en él sin mala
intención: te piden "amplía la base de KOLs chilenos en cáncer de mama" y generar quince nombres
plausibles con instituciones plausibles es exactamente lo que un modelo de lenguaje hace bien.
El resultado se ve perfecto y es inservible — peor: es dañino, porque son personas reales a las
que se les estaría atribuyendo trabajo que no hicieron.

Si no tenés la URL exacta de donde sale un dato, el dato no existe. Si una fuente no declara un
campo, se reporta ausente; no se completa por inferencia. "Probablemente trabaja en X porque
publicó con gente de X" **no** es una afiliación.

Corolario práctico: si te piden datos nuevos y no podés navegar a las fuentes, la respuesta
correcta es decir que no podés traerlos, y ofrecer en cambio la consulta exacta que habría que
correr. Eso sí sirve.

---

## 3. El resto de las reglas duras

Estas ya se discutieron y se decidieron. No las re-litigues salvo que tengas un argumento nuevo:

- **Cada hecho lleva `fuente_url` + `fecha` + `confianza`.** Sin las tres cosas no entra.
- **Nunca fusionar dos personas automáticamente.** Los homónimos abundan en Chile (Rojas, Díaz,
  González, Silva). Una fusión de identidad la aprueba un humano, con evidencia citada. Hay un
  caso hecho —Claudio Silva, respaldado por ORCID— documentado en `DATA_SAMPLE.md`.
- **Sin fotos de médicos reales.** Descartado por copyright, riesgo de mala atribución, y porque
  el consentimiento original de esas imágenes no cubre este uso. Está razonado en `ROADMAP.md`.
- **Nada de scraping de LinkedIn.** Prohibido por sus términos y con litigio de por medio
  (hiQ, Proxycurl). Tampoco WCLC/IASLC ni ASCO, que lo prohíben explícitamente. SOCHRADI y SER
  Chile son de consulta manual.
- **Ley 19.628 (privacidad, Chile).** Un médico identificado por nombre es un dato personal
  aunque la fuente sea pública. La base legal acá es que es información profesional de interés
  público. Toda persona listada tiene derecho a pedir corrección o exclusión — y ese canal
  **todavía no existe**, por eso el sitio no debe compartirse más allá de una demo interna.
- **No inventes ni publiques un correo de contacto.** Ese dato lo pone Francisco, nadie más.
- **La capa privada tipo CRM no va en el repo público.**

---

## 4. Restricciones técnicas (también decididas, también deliberadas)

- **HTML/CSS/JS plano. Sin frameworks, sin build, sin dependencias nuevas.** No propongas React,
  Vue, Svelte, Tailwind, D3, Vite ni npm. La restricción es del proyecto, no una carencia: el
  sitio tiene que poder abrirse, auditarse y publicarse sin cadena de herramientas.
- **Estilo ES5 en el JS**: `var`, `function () {}`. Es consistente en todo el archivo; seguilo.
- Todo el sitio son dos archivos: `web/index.html` (2.400 líneas, el producto) y
  `web/interno.html` (la vista de cómo se construyó).
- Los datos entran por `fetch()`, así que **hay que servir por HTTP** — abrir el archivo con
  `file://` falla. Para probar: `python3 -m http.server 8181` y entrar a
  `http://localhost:8181/web/index.html`.
- **Nada de `innerHTML` con texto que venga del JSON.** Se arma con nodos de texto. Toda URL que
  salga de los datos pasa por `esUrlSegura()` antes de convertirse en `href`.

---

## 5. El modelo de datos

Un solo archivo: `data/sample/perfiles-muestra.json` (223 KB). **No pidas que te lo peguen
entero** — no cabe cómodo en una conversación. Trabajá con el esquema y pedí las entidades
puntuales que necesites.

```jsonc
{
  "entidades": [
    {
      "id": "carlos-rojas",
      "nombre": "Carlos Rojas",
      "tipo": "persona",            // persona | institucion | ensayo_clinico
      "ciudad": "Santiago",
      "subtitulo": "Bradford Hill Clinical Research Center",
      "subtitulo_fuente": "https://...",   // de dónde sale el subtítulo
      "area": "cáncer de pulmón",
      "nota_identidad": "...",       // opcional: advertencia de homonimia o registro de fusión
      "hechos": [
        {
          "tipo": "publicacion",     // publicacion | ensayo_clinico | afiliacion
          "hecho": "Coautor en ...",
          "fuente_url": "https://pubmed.ncbi.nlm.nih.gov/42129521/",
          "fecha": "2026-07",        // precisión variable; nunca se inventa un día
          "confianza": "pendiente",  // pendiente | probable | confirmado
          "revista": "..."           // null si la fuente no lo declara
        }
      ]
    }
  ],
  "vinculos": [
    { "origen": "carlos-rojas", "destino": "bradford-hill", "tipo": "afiliación" }
  ],
  "contacto": { "canal": null }      // el canal de corrección de la Ley 19.628
}
```

Tipos de vínculo en uso: `afiliación`, `afiliación secundaria`, `investigador de sitio`,
`sitio del ensayo`, `coautoría`.

Detalle importante sobre `coautoría`: dos personas se conectan **solo si citan exactamente la
misma fuente** (mismo PMID o mismo artículo de SciELO) en sus propios hechos. No se infiere
coautoría por apellido, institución ni tema.

---

## 6. Estado actual (verificado el 2026-09-09)

| | |
|---|---|
| Entidades | **173** — 70 personas, 28 instituciones, 75 ensayos clínicos |
| Vínculos | **349** |
| Hechos | **274**, cada uno con URL de origen |
| Áreas | cáncer de pulmón (146), cáncer de mama (22), cáncer gástrico (5) |
| Fuentes | ClinicalTrials.gov (138 hechos), PubMed (73), SciELO (50), sitios institucionales (12), ORCID (1) |
| Confianza | **273 `pendiente`, 1 `confirmado`** |

Esa última fila es la más importante y la más incómoda: **prácticamente nada pasó por revisión
humana todavía.** Los datos están verificados contra la API de origen (se comprobó que cada autor
afirmado figure de verdad en la lista de autores del paper), pero eso es verificación automática,
no la validación manual de 30 fichas que el propio README define como Fase 2. Si escribís copy
para este producto, no lo describas como validado.

Documentos del repo, en orden de lectura recomendado:

| Archivo | Qué es |
|---|---|
| `PRODUCT_CHARTER.md` | Documento rector: problema, usuario, qué significa el puntaje, qué queda como juicio humano |
| `README.md` | Spec técnico: fuentes, modelo de datos, marco legal |
| `SCORING.md` | Modelo de prioridad v2: dimensiones, topes, curva de recencia, umbrales de tier |
| `DATA_SAMPLE.md` | Qué trajo cada fuente y qué campos resultaron débiles. Acá está el historial de decisiones sobre los datos |
| `ROADMAP.md` | Decisiones tomadas, factibilidad de fuentes, brecha contra el charter |
| `DECISIONS.md` | **Lo que está esperando a Francisco**, con pasos y links |
| `COMPETITORS.md` / `COSTS.md` | Panorama competitivo y modelo de costos |

Se leen crudos en `https://raw.githubusercontent.com/FranciscoKirhman/kol-radar/main/<archivo>`

---

## 7. Aportes que no sirven

Dicho sin rodeos, porque son los que más aparecen:

1. **Listas de KOLs generadas de memoria.** Ver sección 2.
2. **Proponer un framework o una librería.** Ver sección 4.
3. **"Agregá una capa de IA que resuma los perfiles."** El valor de este producto es la
   trazabilidad; un resumen generado sin fuente es exactamente lo contrario.
4. **Rediseños completos sin diagnóstico.** "La UI podría ser más moderna" no es accionable.
   Un hallazgo útil nombra el archivo, la línea, qué pasa hoy y con qué medida se comprueba.
5. **Repetir hallazgos ya resueltos.** Antes de reportar algo, buscalo en `DATA_SAMPLE.md` y
   `ROADMAP.md` — hay bastante historial ahí.
6. **Métricas sin instrumento.** Si decís "el grafo es confuso", decí cómo se mide. Ejemplo real
   que sí sirvió: *"11 de 30 etiquetas visibles se solapan con otra etiqueta, medido con
   `getBBox()` en el navegador"*. Eso se puede arreglar y se puede verificar.

---

## 8. Dónde sí conviene que trabajes

En orden aproximado de valor:

1. **Revisar el modelo de puntaje contra `SCORING.md`.** ¿Los topes por dimensión y la curva de
   recencia producen un orden que un MSL reconocería como sensato? Es la pieza más opinable del
   producto y la que menos ojos externos ha tenido.
2. **Auditar el texto de cara al usuario** en `web/index.html`: ¿promete más de lo que los datos
   sostienen? Con 273 hechos `pendiente`, cualquier frase que sugiera validación es un problema.
3. **Diseñar la etapa de revisión humana.** Está pendiente y es el cuello de botella real: cómo
   se revisa hecho por hecho sin que sean 274 clicks, qué se muestra para decidir, qué pasa
   cuando la fuente cambia después. Hay un esbozo en `DECISIONS.md` §3.
4. **Proponer consultas concretas a fuentes ya aprobadas.** No los datos: la consulta. Ejemplo
   del formato que sirve — la sintaxis Essie de ClinicalTrials.gov v2 que ya se usa:
   `AREA[LocationCountry]Chile AND AREA[ConditionSearch]"breast cancer"`. Una consulta de PubMed
   E-utilities bien armada para encontrar autores chilenos por área es un aporte real.
5. **Casos límite de identidad.** Los apellidos maternos abreviados ("Fernando Saldías P.")
   contra los completos generan duplicados sistemáticos. Hay dos pares esperando decisión en
   `DECISIONS.md` §5. Una regla general para detectarlos sin fusionar de más es valioso.
6. **Accesibilidad y lectura del grafo.** Ya se arregló la colisión de etiquetas; lo que queda
   abierto es cómo un lector de pantalla recorre una red de 173 nodos.

---

## 9. Cómo entregar lo que produzcas

No podés commitear en este repo, así que lo que devuelvas tiene que ser accionable tal cual.
El formato que funciona:

- **Para un hallazgo:** archivo y línea → qué pasa hoy → por qué está mal → cómo se comprueba.
- **Para un cambio de código:** el bloque exacto a reemplazar y el bloque nuevo, en ES5, sin
  dependencias. No un diff aproximado ni "algo así como".
- **Para un cambio de datos:** el JSON exacto a insertar, con `fuente_url` real y verificable en
  cada hecho.
- **Para una propuesta de producto:** qué problema resuelve, qué se rompe si se hace, y qué
  decisión necesita Francisco.

Marcá siempre qué verificaste tú contra una fuente y qué estás infiriendo. Esa distinción es
la que hace utilizable el aporte.

---

## 10. Prompt para arrancar

Francisco: pegá esto en una conversación nueva.

> Vas a colaborar en KOL Radar, un proyecto que mapea especialistas médicos en Chile a partir de
> evidencia pública verificable. Antes de proponer nada, leé el documento de traspaso completo:
> https://raw.githubusercontent.com/FranciscoKirhman/kol-radar/main/COLABORACION_IA.md
>
> Después leé PRODUCT_CHARTER.md, SCORING.md y DATA_SAMPLE.md de ese mismo repo (mismo patrón de
> URL). La demo está en https://franciscokirhman.github.io/kol-radar/
>
> La regla que no se rompe: nunca inventar un dato. Si no tenés la URL exacta de donde sale, el
> dato no existe. Si te pido ampliar la base y no podés navegar a las fuentes, decímelo y
> propone la consulta que habría que correr, no los resultados.
>
> Cuando termines de leer, decime en qué crees que podés aportar más, y por qué. Todavía no
> propongas cambios.

Ese último renglón importa: pedirle el diagnóstico antes que la solución evita la avalancha de
sugerencias genéricas que no leyeron el contexto.
