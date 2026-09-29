# Cómo publicar KOL Radar y cederlo para que otros lo usen

Estado al 2026-09-28. Este documento convierte la pregunta "¿cómo lo publicamos?" en una lista de
pasos concretos, en orden, con quién decide cada uno.

## Dónde estamos

| | Estado |
|---|---|
| Sitio | Funciona como sitio estático (sin servidor ni base de datos). Ya está en GitHub Pages: <https://franciscokirhman.github.io/kol-radar/> |
| Licencia del código | **MIT** — [`LICENSE`](LICENSE) |
| Licencia de los datos | **ODbL 1.0** — [`data/LICENSE.md`](data/LICENSE.md). Obligatoria mientras haya coordenadas de OpenStreetMap |
| Revisión humana de los datos | **No hecha.** 1 hecho confirmado de 2.986 |
| Canal para que un profesional corrija o retire su ficha | **Correo provisorio** (franckirhman@gmail.com), ya visible en el pie del sitio. Proceso y registro de exclusiones en [`PROCESO_SOLICITUDES.md`](PROCESO_SOLICITUDES.md) |
| Aviso de privacidad | Borrador en [`PRIVACIDAD.md`](PRIVACIDAD.md); falta identificar al responsable |
| Validación con MSL reales (Etapa 6 del charter) | **No hecha** |

## El plazo que manda: 1 de diciembre de 2026

Ese día entra en vigencia la **Ley 21.719**, que reforma la Ley 19.628 de datos personales. Para un
sitio que nombra médicos, cambia tres cosas:

1. **"Es público" deja de bastar.** La ley elimina la excepción amplia de fuentes de acceso público:
   tratar un dato publicado en PubMed o ClinicalTrials.gov necesita igual una base de licitud. La
   candidata natural es el **interés legítimo** (información profesional y científica, de interés
   público, sin fines comerciales sobre las personas). Hay que documentar esa evaluación.
2. **Derechos exigibles**: acceso, rectificación, supresión, oposición, portabilidad y bloqueo, con
   plazos de respuesta. Sin un canal que funcione, no hay cómo cumplirlos.
3. **Un responsable identificable**: una persona o institución con nombre y domicilio que conteste.
   La nueva Agencia de Protección de Datos Personales fiscaliza.

**Recomendación**: no difundir el sitio más allá de una demo interna hasta tener los pasos 1 y 2.
Esto no es asesoría legal; el paso 2 lo debería mirar un abogado.

## Pasos, en orden

### 1. Canal de corrección y retiro (decide: Francisco) — en curso
- ~~Crear un correo o formulario privado~~: hecho el 2026-09-28, `franckirhman@gmail.com` en
  `contacto.canal`. Más adelante conviene un correo dedicado del proyecto: uno personal publicado
  en un sitio recibe spam, y si el proyecto se cede, el correo tiene que poder pasar con él.
- ~~Definir cómo se responde~~: escrito en [`PROCESO_SOLICITUDES.md`](PROCESO_SOLICITUDES.md) —
  30 días corridos para responder (prorrogables una vez), 2 días hábiles para bloquear, qué comando
  corre cada caso y plantillas de respuesta. Falta que el responsable fije cómo se verifica que
  quien escribe es la persona de la ficha.
- ~~Registro de exclusiones~~: hecho, `scripts/exclusiones.py` + `data/exclusiones.json`. Todos los
  scripts que escriben la muestra lo aplican antes de guardar, y CI falla si alguien excluido
  reaparece. El registro guarda huellas con clave, no nombres. **Decide Francisco**: dejarlo así o
  llevarlo fuera del repo (las dos opciones, comparadas, en `PROCESO_SOLICITUDES.md`), y crear el
  secret `KOL_CLAVE_EXCLUSIONES` cuando llegue la primera solicitud.
- **Decide Francisco, caso a caso**: si se purga el historial de git cuando alguien pide salir.

### 2. Responsable y aviso de privacidad (decide: Francisco, con abogado) — bloqueante
- Completar en [`PRIVACIDAD.md`](PRIVACIDAD.md) quién es el responsable del tratamiento.
- Revisar la base de licitud (interés legítimo) y dejar escrita la evaluación.
- Publicarlo como página del sitio y enlazarlo desde el pie.

### 3. Revisión humana mínima (decide: Francisco) — muy recomendable
- La Etapa 3 del charter (revisar fichas a mano) sigue pendiente. Para publicar, al menos las
  **77 fichas de personas**: identidad (homónimos), afiliación, y que cada hecho diga lo que la
  fuente dice. Los ensayos, fármacos e instituciones salen de registros estructurados y tienen
  menos riesgo.
- Resolver las dos fusiones abiertas (`DECISIONS.md` §5) y los 7 candidatos de
  `data/pending/preintegracion-clinicaltrials-2026-09-09/personas_candidatas.json`.

### 4. Validación con 3–5 MSL (decide: Francisco) — antes de invertir más
- Mostrar el inicio y el perfil de un fármaco y de una institución. Preguntar qué decisión tomarían
  con eso y qué les faltó. Es la prueba que falta: nada acá está validado por un usuario real.

### 5. Publicar
- **Opción A — seguir en GitHub Pages** (recomendada al comienzo): gratis, cada cambio en `main` se
  publica solo. Se puede agregar un dominio propio en Settings → Pages.
- **Opción B — Netlify o Cloudflare Pages**: lo mismo, con vistas previas por rama. Útil si hay
  más de una persona editando.
- No hace falta servidor: todo es HTML estático y un JSON.

### 6. Ceder el proyecto para que otros lo usen
Tres niveles, de menos a más compromiso:

1. **Reutilización libre** (ya habilitada por las licencias): cualquiera puede clonar el repositorio,
   cambiar el área clínica y publicar su propia versión. La ODbL les exige atribuir y publicar sus
   datos derivados bajo la misma licencia; la ley de datos personales los hace responsables de su
   propio tratamiento.
2. **Versión citable**: conectar el repositorio con **Zenodo** para que cada versión publicada
   (GitHub Release) reciba un DOI. Ya está [`CITATION.cff`](CITATION.cff), que GitHub muestra como
   "Cite this repository".
3. **Transferir la custodia** a una institución (una sociedad científica, una universidad, una
   fundación): GitHub permite transferir el repositorio a una organización sin perder historial ni
   el sitio. Conviene que el nuevo custodio asuma también el canal de corrección y el rol de
   responsable de datos, y que quede escrito en el README.

## Cómo se actualizan los datos

Cada fuente tiene su script en `scripts/`, y todo lo que entra deja un artefacto en `data/pending/`
para revisión:

| Script | Qué hace |
|---|---|
| `integrar_beta.py` | Ensayos con sede en Chile desde ClinicalTrials.gov |
| `integrar_farmacos_ctgov.py` | Fármacos desde las intervenciones estructuradas de cada ensayo |
| `clasificar_farmacos_ncit.py` | Tipo de cada fármaco según el NCI Thesaurus. Se corre **después** del anterior, que recrea los fármacos |
| `resolver_sedes_web.py` | Liga textos de sede a instituciones, con evidencia buscada a mano |
| `recolectar_estudiosclinicos_cl.py` + `integrar_estudiosclinicos_cl.py` | Centros que la CIF nombra para ensayos que reclutan |
| `consolidar_ubicaciones.py` | Dirección y punto de cada institución (DEIS, sitios oficiales, OpenStreetMap) |
| `enriquecer_openalex.py` | Propuestas de afiliación desde OpenAlex (vía PR, nunca directo) |

Una cadencia razonable: mensual para ClinicalTrials.gov y la CIF (el estado de reclutamiento cambia),
trimestral para lo demás.
