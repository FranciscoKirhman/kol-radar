# Decisiones pendientes — para Francisco

Cuatro decisiones que bloquean trabajo y que **no me corresponde tomar por mi cuenta**: dos
involucran publicar información de contacto o datos de profesionales reales, una implica registrar
una cuenta a tu nombre, y una define el alcance del producto. Cada una acá abajo tiene el
contexto, las opciones con su trade-off real, y los pasos concretos con links.

Ninguna de estas está a medio hacer en el código — están todas sin empezar, esperando tu decisión.

---

## Decisión 1 — Canal de corrección / privacidad

**Prioridad: la más alta de las cuatro.** Es la única que involucra un riesgo real hoy, no a futuro.

### El problema concreto

El sitio es público y lista **médicos chilenos reales con nombre y apellido**, con un puntaje al
lado. El propio `README.md` promete que cualquier persona listada puede pedir corrección o
exclusión de su ficha — y hoy esa promesa **no es cumplible**, porque no existe ningún canal. El
footer del sitio lo dice honestamente ("el canal de contacto para eso todavía no está definido"),
pero eso es una mitigación, no una solución.

Esto aplica la Ley 19.628 sobre protección de la vida privada (Chile): un profesional identificado
por nombre es un dato personal aunque la fuente sea pública.

- Texto de la ley: <https://www.bcn.cl/leychile/navegar?idNorma=141599>
- Agencia de protección de datos (contexto de la reforma 2024, Ley 21.719):
  <https://www.bcn.cl/leychile/navegar?idNorma=1206484>

### Opciones

| Opción | A favor | En contra |
|---|---|---|
| **A. Correo dedicado** (ej. `kolradar.contacto@gmail.com`) | Simple, privado, gratis, es lo que la gente espera | Vas a recibir spam; expone una dirección tuya en un sitio público |
| **B. Formulario de Google** | Respuestas privadas, no expone tu correo, gratis, queda registro ordenado | Depende de Google; la persona necesita confiar en un form externo |
| **C. GitHub Issues** | Cero setup, ya existe | **No sirve** — un issue es público: alguien pidiendo que borres su información tendría que hacerlo en público. Es exactamente lo contrario de lo que necesita |
| **D. Bajar el sitio a privado** hasta resolverlo | Elimina el riesgo por completo | Perdés la demo pública, que es el punto del proyecto |

**Mi recomendación: B (formulario de Google).** No expone un correo tuyo al scraping, las
respuestas quedan privadas y ordenadas, y es lo suficientemente formal para que se vea serio en
una entrevista. Si preferís algo más directo, A también es perfectamente defendible.

### Pasos para la opción B

1. Andá a <https://docs.google.com/forms> y creá un formulario en blanco.
2. Título sugerido: "KOL Radar — corrección o eliminación de información".
3. Campos sugeridos: nombre, correo de contacto, qué ficha (nombre del profesional), qué dato es
   incorrecto o qué querés que se elimine, y un campo libre.
4. En "Configuración" → activá "Recopilar direcciones de correo" si querés poder responder.
5. Botón "Enviar" → pestaña del ícono de link → "Acortar URL" → copiá el link.
6. Pasame el link y yo lo pongo en el footer del sitio y en `README.md`, reemplazando el texto
   actual que dice que el canal no existe.

### Pasos para la opción A

1. Creá la cuenta en <https://accounts.google.com/signup> (o un alias en el proveedor que uses).
2. Pasame la dirección y la pongo en el footer y en `README.md`.

**Importante:** no voy a inventar ni usar tu correo personal (`francisco.osorio@ug.uchile.cl`) para
esto sin que me lo digas explícitamente — publicar una dirección real en un sitio público sobre
médicos identificados es una decisión con consecuencias que siguen después de esta sesión.

---

## Decisión 2 — OpenAlex: ¿resolvemos el problema de la API key?

### El problema concreto

Investigué OpenAlex y es **la única fuente de las tres que probé** (contra Semantic Scholar y
Crossref) que resuelve dos cosas que hoy no tenemos:

1. **Desambiguación de identidad de autor** — probado en vivo con un KOL chileno real (Dr.
   Christian Caglevic, FALP): consolidó 111 trabajos y 9.668 citas en un solo perfil, con ORCID
   vinculado. Semantic Scholar dejó al mismo médico fragmentado en 12 IDs distintos.
2. **Publicaciones por año** (`counts_by_year`) — ya calculado, listo para el gráfico de tendencia
   que querías para detectar *rising stars*.

El obstáculo: **desde el 13 de febrero de 2026 OpenAlex exige una API key**. Y como KOL Radar es un
sitio estático sin backend, si el navegador hace la llamada, la key queda **visible públicamente**
en las peticiones de red de cualquier visitante.

- Anuncio del cambio: <https://blog.openalex.org/openalex-api-new-features-and-usage-based-pricing/>
- Precios y cuotas: <https://help.openalex.org/hc/en-us/articles/24397762024087-Pricing>
- (El uso que necesitaríamos está muy por debajo del umbral gratis: ~US$1/día de crédito gratuito
  alcanza de sobra para una especialidad.)

### Opciones

| Opción | A favor | En contra |
|---|---|---|
| **A. GitHub Actions con la key como secret** | La key nunca llega al navegador; se puede correr automático (ej. semanal); encaja con el modelo actual (los datos ya se recolectan fuera del navegador y se publican como JSON) | Hay que configurar el workflow; agrega una pieza de infraestructura |
| **B. Correr la recolección a mano y comitear el JSON** | Cero infraestructura nueva; es literalmente lo que ya venimos haciendo | Manual, no se actualiza solo |
| **C. No usar OpenAlex** | Cero fricción | Perdemos la desambiguación de identidad y el gráfico de tendencia sale peor, calculado a mano desde las fechas que ya tenemos |

**Mi recomendación: A**, y B como paso intermedio si querés probar primero sin comprometerte a
armar el workflow. Ojo que A también es la base técnica de la Decisión 3, así que resolverlas
juntas ahorra trabajo.

### Pasos

1. Creá cuenta gratis en <https://openalex.org/> (el alta toma ~30 segundos).
2. Andá a <https://openalex.org/settings/api> y generá la API key.
3. **No me la mandes por chat.** Guardala directamente como secret del repo:
   → <https://github.com/FranciscoKirhman/kol-radar/settings/secrets/actions>
   → botón "New repository secret" → Name: `OPENALEX_API_KEY` → pegá el valor → "Add secret".
   (Docs de GitHub: <https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions>)
4. Avisame cuando esté y yo escribo el script de recolección + el workflow que la consume.

---

## Decisión 3 — Cadencia del pipeline con bandeja de revisión

Ya elegiste la opción 1 (automatizar la recolección, **mantener** la revisión humana antes de que
algo pase a `confirmado`) — eso respeta lo que el `README.md` promete y no lo voy a cambiar. Lo que
falta son tres sub-decisiones operativas:

### 3.1 ¿Cada cuánto corre?

| Opción | Cuándo tiene sentido |
|---|---|
| **Semanal** (recomendado) | ClinicalTrials.gov actualiza seguido; PubMed también. Semanal detecta cambios sin generar ruido |
| Mensual | Si preferís revisar lotes más grandes y menos seguido |
| Solo a demanda (botón manual) | Si querés control total y no te molesta correrlo vos |

### 3.2 ¿Dónde vive la bandeja de revisión?

| Opción | A favor | En contra |
|---|---|---|
| **Un archivo `data/pending/` en el repo + un PR automático** (recomendado) | Revisás en la interfaz de diff de GitHub, que ya está hecha para esto; queda historial completo; nada entra a `main` sin que aprobes el PR | Tenés que entender un poco de PRs |
| Una pestaña "Pendientes" en `interno.html` | Se revisa en la misma web | Sin backend no puede escribir tu aprobación en ninguna parte — sería solo de lectura |
| Un CSV que revisás aparte | Simple | Se desincroniza del repo fácil |

### 3.3 ¿Qué pasa si la fuente contradice un dato ya confirmado?

Esta es la que más me importa que decidas vos, porque puede sobrescribir trabajo de revisión
humana ya hecho:

- **A.** El dato nuevo entra a la bandeja y el viejo se mantiene visible hasta que revises.
  (Conservador, recomendado.)
- **B.** El dato nuevo reemplaza al viejo automáticamente y se marca como "cambió, revisar".
- **C.** Se muestran los dos con sus fechas y el conflicto queda visible en la ficha.

### Pasos

No hay nada que configurares por tu parte más allá de la Decisión 2 (el workflow de GitHub
Actions es la misma pieza). Solo decime: cadencia, dónde vive la bandeja, y qué hacer ante
contradicción. Con eso lo construyo.

---

## Decisión 4 — Capa privada tipo CRM

### El problema concreto

Tanto ChatGPT como Gemini pidieron cosas que **no deberían vivir en un repo público**: notas
internas del MSL ("prefiere visitas los martes"), última interacción, y — la más delicada, que
sugirió Gemini — si el médico es *speaker* de la competencia.

Ese último punto además choca de frente con lo que el `README.md` promete: "no genera un ranking de
valor comercial" y "no registra interacciones con profesionales de salud". Y el
`PRODUCT_CHARTER.md` (§9, "Non-goals") también lo excluye del primer alcance.

Ya lo confirmaste como roadmap futuro. Lo que falta decidir es **cuándo y cómo se separa**:

| Opción | A favor | En contra |
|---|---|---|
| **A. No hacerlo hasta tener un caso de uso real** (recomendado por ahora) | Cero riesgo; el proyecto se mantiene defendible como "inteligencia pública trazable" | No cubre el workflow completo de un MSL |
| B. Repo privado separado que consume el JSON público | Separación limpia; los datos privados nunca tocan el repo público | Dos repos que mantener |
| C. Capa local en el navegador (localStorage), nunca sube | Simple; ya existe el precedente — la shortlist funciona así hoy | Se pierde al cambiar de máquina; no sirve para un equipo |

**Nota:** la shortlist que acabo de construir ya usa el patrón C (vive solo en tu navegador, no se
envía a ningún servidor ni se comitea). Si querés, ese mismo patrón puede extenderse a notas
personales sin ningún riesgo de privacidad — es el paso más chico posible en esta dirección.

### Pasos

Nada por hacer hasta que decidas. Si querés el paso chico (notas privadas en localStorage), decime
y lo agrego; es media hora de trabajo y cero riesgo.

---

## Decisión 5 — Dos fusiones de identidad más, esperando tu OK

### El problema concreto

Confirmaste que Claudio Silva F. y Claudio Silva Fuente-Alba eran la misma persona, y ya están
unificados. Eso me hizo preguntarme cuántos duplicados más había, así que corrí una auditoría sobre
las 70 personas de la muestra con cuatro criterios distintos.

La causa es siempre la misma y es estructural, no un descuido: las revistas chilenas abrevian el
apellido materno a una inicial ("Fernando Saldías P.") y PubMed indexa por apellido + iniciales. La
misma persona entra dos veces si la recolección la encuentra por SciELO y por PubMed en rondas
distintas. Van a seguir apareciendo a medida que crezca la base.

**Yo no fusiono a nadie sin que me lo confirmes.** El costo de equivocarse no es simétrico: dejar un
duplicado es feo, pero atribuirle a un médico el trabajo de otro es un error grave, difícil de
detectar después y que le afecta a una persona real.

Aviso sobre el alcance de lo que sigue: la fase de verificación automática de esa auditoría **no
alcanzó a correr** — se agotó el límite mensual de gasto de la cuenta y los cuatro verificadores
murieron. Así que verifiqué a mano contra las fuentes, y abajo separo lo que comprobé yo de lo que no.

---

### 5.1 — Francisco Aguayo G. + Francisco Aguayo · **recomiendo fusionar**

| | `francisco-aguayo-g` | `francisco-aguayo` |
|---|---|---|
| Nombre | Francisco Aguayo G. | Francisco Aguayo |
| Institución | Instituto Nacional del Tórax | Universidad de Tarapacá |
| Subtítulo | Laboratorio de Biología Molecular | Laboratorio de Oncovirología |
| Evidencia | SciELO 2006, p16INK4a en cáncer escamoso de pulmón | PubMed 2022 y 2024 |

Lo que comprobé yo, consultando las APIs:

1. [ORCID 0000-0002-9619-7535](https://orcid.org/0000-0002-9619-7535) corresponde a **"Francisco
   Aguayo González"**, con nombre de firma "Francisco Aguayo", empleado en el **Departamento de
   Ciencias Biomédicas de la Universidad de Tarapacá** — la institución y el laboratorio de la ficha
   `francisco-aguayo`. O sea: la "G." es González.
2. Ese mismo ORCID **reclama como obra propia** el
   [PMID 18449464](https://pubmed.ncbi.nlm.nih.gov/18449464/) — *"High frequency of p16 promoter
   methylation in non-small cell lung carcinomas from Chile"*, Biol Res 2007 — donde firma como
   "Aguayo, Francisco R".
3. Los coautores de ese paper son **Darwins Castillo** y **Leda M. Guzmán**, que en nuestra propia
   base son coautores de `francisco-aguayo-g` en el paper de SciELO de 2006. Mismo grupo, mismo
   tema (metilación de p16 en cáncer de pulmón en Chile), mismos años.

Lo que **no** pude comprobar, y por eso esto no es tan sólido como el caso Silva: el ORCID de Aguayo
tiene el campo de variantes de nombre **vacío** — a diferencia del de Silva, no declara él mismo
"Aguayo G." como forma alternativa. Y el artículo exacto de SciELO de 2006 no figura entre sus obras
de ORCID (SciELO suele no sincronizar). El vínculo se apoya en coautores + tema + apellido, no en una
declaración del propio investigador.

**Si decís que sí**, la ficha resultante muestra 20 años de trayectoria — del Instituto Nacional del
Tórax en 2006 a la Universidad de Tarapacá en 2024 — en vez de dos personas sueltas. Es justo el tipo
de recorrido que a un MSL le sirve ver.

---

### 5.2 — Juan Carlos Díaz P. + Juan Carlos Díaz Patiño · **recomiendo fusionar**

| | `juan-carlos-diaz-p` | `juan-carlos-diaz-patino` |
|---|---|---|
| Nombre | Juan Carlos Díaz P. | Juan Carlos Díaz Patiño |
| Institución | Hospital Clínico U. de Chile | Clínica Alemana |
| Subtítulo | Departamento de Radiología | Departamento de Imágenes |
| Evidencia | Rev Med Chile 2016, TC de tórax en EPOC | Rev Med Chile 2018, neoplasia pulmonar quística |

Lo que comprobé yo: el programa de la Universidad de Chile
[*Estada de Perfeccionamiento en Imagenología de Tórax y Cardiovascular*](https://medichi.uchile.cl/estada-de-perfeccionamiento-en-imagenologia-de-torax-y-cardiovascular/)
lista textualmente entre sus docentes **"Dr. Juan Carlos Díaz Patiño — Prof. Asociado — Facultad de
Medicina U. de Chile"**. Es decir, el radiólogo de la U. de Chile se apellida **Díaz Patiño**, y su
subespecialidad declarada es imagenología de tórax: exactamente el tema de los dos papers. La doble
afiliación (universidad pública + clínica privada) es lo normal en Chile, no una contradicción.

No encontré ORCID para él, así que no hay una declaración propia que liste ambas formas del nombre.

**Cuidado con un vecino:** `orlando-diaz-p` **no** es la misma persona — es broncopulmonar de la PUC,
no radiólogo. Comparten apellido y probablemente familia; no los toqués.

---

### 5.3 — `uchile` + `hosp-uchile` · **es criterio tuyo, no un error de dato**

Esto es una institución, no una persona. Hay dos nodos para lo mismo, nacidos de una sola cadena de
afiliación ("Departamento de Radiología, Hospital Clínico Universidad de Chile") que la recolección
partió en dos. `hosp-uchile` no tiene ninguna otra persona ni ningún otro hecho colgando.

Pero el Hospital Clínico es jurídicamente una entidad distinta de la Universidad, así que separarlos
puede ser correcto a propósito. La pregunta de fondo es de producto: **¿el mapa modela organizaciones
jurídicas o lugares donde alguien trabaja?** Para un MSL que planifica visitas, creo que lo segundo
sirve más — pero es tu llamado, no mío.

### Pasos

Contestame `5.1 sí/no`, `5.2 sí/no`, `5.3 fusionar/separar`. Cada fusión que aprobés queda igual que
la de Silva: una sola ficha, con la URL de la evidencia citada como hecho y una `nota_identidad`
visible que dice que se unificó, quién lo aprobó y con qué respaldo. Nada se borra en silencio.

---

## Resumen de qué necesito de ti

| # | Decisión | Qué necesito | Bloquea |
|---|---|---|---|
| 1 | Canal de corrección | Un link de formulario **o** una dirección de correo | Poder compartir el sitio más allá de una demo interna |
| 2 | OpenAlex | Que crees la cuenta y guardes la key como secret del repo | Desambiguación de identidad + gráfico de tendencia/rising stars |
| 3 | Cadencia del pipeline | Tres respuestas cortas (cada cuánto, dónde, qué hacer ante conflicto) | Automatizar la recolección |
| 4 | Capa privada | Solo confirmar si querés el paso chico (notas locales) o nada por ahora | Nada urgente |
| 5 | Fusiones de identidad | `sí/no` a dos pares de fichas duplicadas, y un criterio para las instituciones | Que el mapa no muestre a la misma persona dos veces |

La #1 es la que yo movería primero. Las otras tres son mejoras; esa es una promesa incumplida en
un sitio público sobre personas reales.
