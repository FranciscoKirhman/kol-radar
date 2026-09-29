# Cómo se responde cuando alguien pide corregir o retirar su ficha

Procedimiento operativo para el canal de corrección (`contacto.canal` en la muestra, hoy
franckirhman@gmail.com). Cubre los derechos que la Ley 19.628, reformada por la **Ley 21.719**
(vigente desde el **1 de diciembre de 2026**), da a quien aparece en KOL Radar: acceso,
rectificación, supresión, oposición, bloqueo y portabilidad.

> **No es asesoría legal.** Los plazos de abajo salen de la lectura del art. 11 de la ley reformada
> en fuentes secundarias ([Alayia Trust](https://alayiatrust.com/blog/como-responder-derechos-arsop),
> [Todos los plazos de la Ley 21.719](https://alayiatrust.com/blog/plazos-ley-21719)). Confirmarlos con
> un abogado junto con el aviso de privacidad (`PUBLICAR.md`, paso 2).

## Plazos

| Qué | Plazo | Desde |
|---|---|---|
| Acusar recibo y responder cualquier solicitud | **30 días corridos** (no hábiles) | el día en que llega el correo |
| Prórroga | una sola vez, **30 días corridos más** | hay que avisarla **antes** de que venzan los primeros 30 |
| Bloqueo temporal (si lo pide, sola o junto con rectificación, supresión u oposición) | **2 días hábiles** | el día en que llega |
| Costo para quien pide | ninguno | |

Como el bloqueo es el plazo corto y cuesta un comando, la regla práctica es: **ante cualquier pedido
de retiro, bloquear primero y decidir después.**

## Paso a paso

### 1. Llega el correo
- Responder el mismo día con el acuse de recibo (plantilla A, abajo) y anotar la **fecha de
  ingreso**: de ahí corren los plazos.
- Identificar qué ficha es. El id está en la URL del perfil (`#ficha=<id>`).

### 2. ¿Es la persona? — decide el responsable
Retirar la ficha de alguien por pedido de un tercero también es un error. Lo mínimo razonable
suele ser que escriba desde un correo institucional que se pueda relacionar con la ficha, o que
responda desde el correo que ya figura en una fuente pública. **No pedir documentos de identidad
por correo.** El criterio exacto lo fija el responsable con su abogado; mientras tanto, si hay
duda, bloquear (paso 3) no le hace daño a nadie y da tiempo.

### 3. Bloqueo, dentro de 2 días hábiles
```bash
python3 scripts/exclusiones.py retirar <id> --tipo bloqueo --fecha-solicitud AAAA-MM-DD
```
Quita la ficha y sus vínculos de `data/sample/perfiles-muestra.json`, la registra en
`data/exclusiones.json` y guarda una copia **fuera del repositorio**
(`~/.config/kol-radar/retirados/`) para poder devolverla si la solicitud se resuelve a favor de
mantenerla. Después: commit y push a `main`; GitHub Pages publica en unos minutos.

### 4. Resolver
| Pide | Qué se hace |
|---|---|
| **Supresión** u **oposición** | `python3 scripts/exclusiones.py retirar <id> --tipo supresion` (u `oposicion`). Si ya estaba bloqueada, la ficha ya no está: registrar igual con `registrar --nombre ... --tipo supresion` para que quede el tipo definitivo. |
| Que **no lo incorporen** (todavía no tiene ficha) | `python3 scripts/exclusiones.py registrar --nombre "Nombre Apellido" [--nombre "otra forma"] [--orcid ...] --tipo oposicion --fecha-solicitud ...` |
| **Rectificación** | Corregir a mano el hecho en la muestra, con la fuente que lo respalda. Si la fuente dice otra cosa, se muestra lo que dice la fuente y se agrega una nota: KOL Radar no afirma nada que ninguna fuente diga. |
| **Acceso** | Enviarle su ficha: los hechos, con su fuente y fecha, tal como están en la muestra. |
| **Portabilidad** | Lo mismo, en JSON (el bloque de su entidad y sus vínculos). |

### 5. Limpiar lo que queda
`retirar` termina con dos listas:
- **Textos de otras fichas que todavía la nombran** (una coautoría, una nota de identidad). Hay que
  editarlos a mano; `python3 scripts/exclusiones.py verificar` falla hasta que no quede ninguno, y
  corre en cada push (`.github/workflows/verificar-exclusiones.yml`).
- **Archivos del repositorio que la nombran** fuera del sitio: bandejas de revisión en
  `data/pending/`, documentos. No se publican en la página, pero el repositorio es público.
  Editarlos o dejarlos es decisión del responsable.
- **El historial de git conserva todo lo borrado.** Purgarlo (`git filter-repo`) reescribe la
  historia de todo el repositorio y obliga a volver a clonar: se decide **caso a caso** y lo decide
  el responsable, no un script.

### 6. Responder y cerrar
Plantilla B o C. `python3 scripts/exclusiones.py estado` muestra cada solicitud con su fecha límite.

## Por qué la próxima recolección no la vuelve a traer
Todos los scripts que escriben la muestra (`integrar_beta.py`, `integrar_farmacos_ctgov.py`,
`clasificar_farmacos_ncit.py`, `resolver_sedes_web.py`, `integrar_estudiosclinicos_cl.py`) guardan a través de `exclusiones.guardar_muestra()`, que quita a las
personas excluidas antes de escribir. Los que crean personas o candidatos (`integrar_beta.py`,
`preintegracion_clinicaltrials.py`) además las saltan al crearlas:
una coincidencia exacta no se crea ni se lista en la bandeja de revisión, y una **posible** (mismo
nombre y apellido, otra forma del nombre) no se crea sola y queda marcada para que la revise una
persona.

## Dónde vive el registro — decide Francisco

El registro no puede ser una lista de nombres en el repositorio público: publicaría justo lo que
esas personas pidieron no publicar. Hay dos formas de evitarlo y el código admite las dos:

| | A. En el repo, sin nombres (lo que hay hoy) | B. Fuera del repo |
|---|---|---|
| Cómo | `data/exclusiones.json` guarda solo huellas BLAKE2b con clave; la clave está en `~/.config/kol-radar/clave-exclusiones` y como secret `KOL_CLAVE_EXCLUSIONES` | `KOL_EXCLUSIONES=/ruta/privada/exclusiones.json` en cada corrida |
| Qué se ve públicamente | cuántas solicitudes hay, su tipo y fechas; no quién | nada |
| CI puede verificar | sí, con el secret | no |
| Si el proyecto se cede | el registro va con el repo; hay que entregar la clave | hay que entregar el archivo y acordarse de hacerlo |
| Riesgo principal | perder la clave: los scripts se detienen (fallan cerrado) hasta recuperarla | una corrida sin la variable no ve el registro y puede volver a traer a alguien |

Con A, sin la clave no se puede saber a quién corresponde una huella ni probar nombres hasta dar con
ella. Los scripts se detienen si hay solicitudes y falta la clave, o si la clave no es la que armó
el registro.

## Plantillas

**A — Acuse de recibo**
> Hola, [nombre]. Recibimos tu solicitud del [fecha] sobre tu ficha en KOL Radar. Te respondemos a
> más tardar el [fecha + 30 días]. [Si pidió retiro:] Mientras tanto, tu ficha ya no se muestra en el
> sitio.

**B — Retiro hecho**
> Hola, [nombre]. Retiramos tu ficha de KOL Radar el [fecha] y registramos tu solicitud para que
> ninguna actualización futura de los datos la vuelva a incorporar. [Si corresponde:] Los datos
> siguen en las fuentes públicas de donde los tomamos (ClinicalTrials.gov, PubMed…): para
> corregirlos ahí hay que escribirles a ellas.

**C — Corrección hecha**
> Hola, [nombre]. Corregimos [qué] en tu ficha el [fecha]. Cada dato del sitio enlaza a la fuente de
> donde sale; si la fuente también está desactualizada, conviene pedir la corrección ahí, porque la
> próxima actualización vuelve a leerla.
