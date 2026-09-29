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
Quita la ficha y sus vínculos de `data/sample/perfiles-muestra.json`, la registra en el registro de
exclusiones (fuera del repositorio, ver abajo) y guarda una copia **fuera del repositorio**
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
`retirar` termina con tres cosas:
- **Textos de otras fichas que todavía la nombran** (una coautoría, una nota de identidad). Hay que
  editarlos a mano; `python3 scripts/exclusiones.py verificar` falla hasta que no quede ninguno.
  **Correrlo antes de cada push a `main`.**
- **Archivos del repositorio que la nombran** fuera del sitio: bandejas de revisión en
  `data/pending/`, documentos. La purga del paso siguiente los limpia en toda la historia, incluida
  la versión actual.
- **El archivo de reemplazos para purgar el historial**, en `~/.config/kol-radar/purgas/`, con los
  comandos a correr.

### 5b. Purgar el historial de git — decisión 2026-09-29: se purga
Borrar la ficha de la muestra no la borra de GitHub: sigue en cada commit anterior, a un clic. Para
**supresión** y **oposición** se purga; para un **bloqueo** no (es temporal y puede revertirse).

Lo corre una persona, en este orden, siguiendo la
[guía de GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository),
que manda si algo cambió:

1. Publicar primero el retiro (commit y push de la muestra sin la ficha).
2. Instalar `git-filter-repo` (`brew install git-filter-repo`).
3. En un directorio **fuera** del proyecto:
   ```bash
   git clone --bare https://github.com/FranciscoKirhman/kol-radar.git kol-radar-purga
   ```
   ```bash
   cd kol-radar-purga && git filter-repo --sensitive-data-removal --replace-text ~/.config/kol-radar/purgas/<archivo>.txt
   ```
4. Comprobar que no quedó nada: `git log --all -p | grep -ciE '<apellido>'` tiene que dar 0.
5. `git push --force --mirror origin`.
6. Pedir a GitHub Support que borre las vistas en caché y las referencias de Pull Requests, con los
   commits que `filter-repo` informa como primeros cambiados.
7. **Volver a clonar** el proyecto en cada máquina y borrar ramas y worktrees viejos: tienen la
   historia anterior, y un push desde ahí la devuelve.
8. Borrar el archivo de reemplazos.

Qué reemplaza: cada forma completa del nombre (con o sin tildes, en cualquier caja, en orden normal
o "Apellido, Nombre", y como id: `ana-perez`) y el ORCID, por `[retirado]`. Las iniciales solas
("Pérez A") no, porque calzarían con otras personas. Qué no alcanza: los **forks** del repositorio
y las copias que alguien ya haya bajado; eso no se puede borrar desde acá.

### 6. Responder y cerrar
Plantilla B o C. `python3 scripts/exclusiones.py estado` muestra cada solicitud con su fecha límite.

## Por qué la próxima recolección no la vuelve a traer
Todos los scripts que escriben la muestra (`integrar_beta.py`, `integrar_farmacos_ctgov.py`,
`clasificar_farmacos_ncit.py`, `resolver_sedes_web.py`, `integrar_estudiosclinicos_cl.py`,
`integrar_isp_inspecciones.py`) guardan a través de `exclusiones.guardar_muestra()`, que quita a las
personas excluidas antes de escribir. Los que crean personas o candidatos (`integrar_beta.py`,
`preintegracion_clinicaltrials.py`, `integrar_isp_inspecciones.py`) además las saltan al crearlas:
una coincidencia exacta no se crea ni se lista en la bandeja de revisión, y una **posible** (mismo
nombre y apellido, otra forma del nombre) no se crea sola y queda marcada para que la revise una
persona.

## Dónde vive el registro — decisión 2026-09-29: fuera del repo

| | |
|---|---|
| Registro | `~/.config/kol-radar/exclusiones.json` (o la ruta en `KOL_EXCLUSIONES`) |
| Clave | `~/.config/kol-radar/clave-exclusiones` (o el valor en `KOL_CLAVE_EXCLUSIONES`) |
| Se crean con | `python3 scripts/exclusiones.py iniciar`, una vez por máquina |
| Respaldo | los dos, en un gestor de contraseñas. Si el proyecto se cede, se entregan con él |

Aun fuera del repo, el registro guarda **huellas** (BLAKE2b con la clave), no nombres: si el
archivo se filtra, sin la clave no se puede saber a quién corresponde cada una.

Falla cerrado: sin registro, sin clave o con otra clave, los scripts de integración se detienen.
Un clon nuevo del proyecto no puede integrar datos hasta tener el registro: es a propósito, porque
la alternativa es una corrida que no ve a nadie excluido y lo vuelve a publicar.

Como el registro no está en el repositorio, GitHub Actions no puede verificarlo: la verificación
es `python3 scripts/exclusiones.py verificar` antes de cada push a `main`. El único workflow que
corre en GitHub (OpenAlex) solo propone datos de personas que ya están en la muestra, así que no
puede traer de vuelta a nadie.

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
