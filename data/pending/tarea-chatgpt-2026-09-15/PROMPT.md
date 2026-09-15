# Prompt para ChatGPT — completar ubicaciones y conexiones de KOL Radar

> Copiar desde la línea de abajo hasta el final. Adjuntar en la conversación los archivos
> `A_instituciones.csv`, `B_sedes_por_resolver.csv`, `C_ensayos_sin_sede_nombrada.csv`,
> `D_personas_sin_institucion.csv` e `instituciones_existentes.csv`. Hace falta la búsqueda web
> activada: sin navegar, la única respuesta correcta es "no puedo verificarlo".

---

Vas a completar datos faltantes de **KOL Radar**, un mapa de especialistas, instituciones y
ensayos clínicos de oncología en Chile construido **solo con evidencia pública verificable**. Lo
usan Medical Science Liaisons para preparar territorios. Cada dato que entregues va a revisarlo
una persona y lo va a pasar un validador automático antes de entrar. Una respuesta honesta de
"no encontrado" vale más que un dato plausible sin fuente.

## Reglas que no se negocian

1. **Nunca inventes datos.** Ni direcciones, ni comunas, ni coordenadas, ni nombres, ni NCT, ni
   fechas. Si no tenés la URL exacta de donde sale un dato, el dato no existe: marcá
   `no_encontrada` / `no_resoluble` y explicá qué buscaste.
2. **Cada dato lleva su fuente**: URL exacta de la página (no el dominio), una cita textual de
   máximo 25 palabras copiada de esa página y la fecha en que la consultaste.
3. **Coordenadas solo si la fuente las publica** (un objeto de OpenStreetMap o el listado de
   establecimientos del DEIS del Minsal). Si solo tenés la dirección, dejá `lat` y `lon` en `null`:
   nosotros la geocodificamos. Nunca estimes coordenadas ni las copies de Google Maps.
4. **Fuentes permitidas**, en este orden de preferencia:
   - sitio oficial de la institución (página de contacto, sedes o "dónde estamos");
   - Superintendencia de Salud (supersalud.gob.cl) y DEIS del Minsal (deis.minsal.cl);
   - Registro de Empresas y Sociedades (registrodeempresasysociedades.cl), para razones sociales;
   - ClinicalTrials.gov, PubMed, SciELO;
   - OpenStreetMap (con la URL del objeto: `openstreetmap.org/node|way|relation/<id>`).
5. **Fuentes prohibidas**: LinkedIn, Google Maps (se puede usar para orientarse, nunca como fuente
   ni para coordenadas), acortadores de enlaces, Doctoralia y directorios con reseñas, ASCO, IASLC
   y WCLC.
6. **Personas**: nunca asumas que dos registros son la misma persona por el apellido. Los homónimos
   son comunes en Chile (Rojas, González, Silva). Solo cuenta un ORCID, o nombre completo más
   institución coincidentes en la misma fuente. Solo información profesional pública.
7. **Instituciones con varias sedes**: la dirección tiene que ser la de la sede que corresponde a la
   ciudad declarada (en el CSV o en ClinicalTrials.gov). Si la fuente solo muestra la casa matriz o
   una oficina administrativa, decilo en `notas` y listá las otras sedes en `otras_sedes`.
8. **Nada de conexiones sin evidencia.** El objetivo es que no queden ensayos sueltos, pero un
   vínculo inventado es peor que un nodo desconectado.

## Las cuatro tareas

### A · Ubicar o verificar instituciones — `A_instituciones.csv`

- `tarea = ubicar`: encontrá la dirección de la sede en la ciudad indicada.
- `tarea = verificar`: el CSV trae un candidato de OpenStreetMap con una advertencia (otra sede con
  el mismo nombre, o un tipo de objeto dudoso). Confirmá que es la sede correcta (`confirmada`),
  o corregilo con la dirección correcta (`corregida`).
- Las sociedades científicas pueden no tener sede física: en ese caso, `no_encontrada` con el motivo.

### B · Resolver sedes de ensayos — `B_sedes_por_resolver.csv`

Cada fila es un texto de sede tal como lo escribe ClinicalTrials.gov ("Instituto Oncologico Ltda.",
"Rey y Oreilly Limitada ( Site 1048)") que no calzó con ninguna institución conocida. Abrí al menos
una de las fichas de ClinicalTrials.gov listadas y decidí:

- `institucion_existente`: es una de `instituciones_existentes.csv` (por nombre, alias o razón
  social). Hace falta evidencia de que ese texto corresponde a esa institución (por ejemplo, la
  razón social en su sitio oficial o en el Registro de Empresas y Sociedades).
- `institucion_nueva`: es una institución real que no está en la lista. Entregá nombre oficial,
  dirección, comuna, ciudad, fuente y cita.
- `marcador_patrocinador`: no nombra una institución ("Research Site", "Site CL001", "Local
  Institution").
- `no_resoluble`: nombra algo, pero no encontrás evidencia suficiente para decir qué es.

En `nct_verificados` poné solo los NCT donde **viste** ese texto en la ficha de ClinicalTrials.gov.

### C · Ensayos sin ninguna sede nombrada — `C_ensayos_sin_sede_nombrada.csv`

Son ensayos que en nuestra muestra no tienen ninguna institución. Abrí la ficha y revisá la sección
de ubicaciones (Locations) en Chile:

- `sedes_nombradas`: hay sedes con nombre real → resolvé cada una igual que en la tarea B.
- `solo_marcadores`: solo aparecen marcadores del patrocinador.
- `sin_sedes_en_chile`: la ficha ya no declara ubicaciones en Chile.

### D · Personas sin institución — `D_personas_sin_institucion.csv`

Buscá la afiliación profesional publicada de cada persona, partiendo de la fuente que ya tenemos.
Solo PubMed, SciELO, ClinicalTrials.gov o el sitio oficial de la institución. En `notas` explicá
por qué es la misma persona.

## Cómo entregar

- **Un lote por respuesta, de máximo 40 ítems**, de una sola tarea. Numerá los lotes (`"lote": 1`,
  `2`, …). Empezá por la A, después la D, la B y la C.
- La respuesta es **solo un bloque de código JSON**, sin texto antes ni después. Si algo necesita
  explicación, va en `notas` o en `pendientes_para_el_proximo_lote`.
- Copiá `id`, `texto_sede` y `nct` **idénticos** a como vienen en el CSV.
- `fecha_consulta` en formato `AAAA-MM-DD`.

### Formato exacto

```json
{
  "lote": 1,
  "tareas_incluidas": ["A"],
  "A": [
    {
      "id": "bradford-hill",
      "tarea": "ubicar",
      "resultado": "ubicada",
      "nombre_oficial": "Nombre tal como lo publica la fuente",
      "direccion": "Calle y número, oficina si corresponde",
      "comuna": "Providencia",
      "ciudad": "Santiago",
      "region": "Región Metropolitana de Santiago",
      "lat": null,
      "lon": null,
      "fuente_url": "https://sitio-oficial.cl/contacto",
      "fuente_tipo": "sitio_oficial",
      "cita_textual": "Máximo 25 palabras copiadas de la fuente, con la dirección",
      "fecha_consulta": "2026-09-15",
      "otras_sedes": [
        { "direccion": "…", "comuna": "…", "fuente_url": "https://…" }
      ],
      "motivo_si_no_encontrada": "",
      "notas": ""
    }
  ],
  "B": [
    {
      "texto_sede": "Instituto Oncologico Ltda.",
      "resultado": "institucion_existente",
      "id_institucion": "id-de-instituciones_existentes.csv",
      "institucion_nueva": null,
      "nct_verificados": ["NCT00849667"],
      "ciudad_en_clinicaltrials": "Santiago",
      "evidencia_url": "https://clinicaltrials.gov/study/NCT00849667",
      "evidencia_institucion_url": "https://… (página que prueba a qué institución corresponde el texto)",
      "cita_textual": "…",
      "fecha_consulta": "2026-09-15",
      "notas": ""
    }
  ],
  "C": [
    {
      "nct": "NCT00034125",
      "resultado": "sedes_nombradas",
      "sedes": [
        {
          "texto_en_clinicaltrials": "…",
          "ciudad": "Santiago",
          "resultado": "institucion_existente",
          "id_institucion": "…",
          "institucion_nueva": null
        }
      ],
      "evidencia_url": "https://clinicaltrials.gov/study/NCT00034125",
      "fecha_consulta": "2026-09-15",
      "notas": ""
    }
  ],
  "D": [
    {
      "id": "myriam-campbell-bull",
      "resultado": "afiliacion_encontrada",
      "institucion": { "id_institucion": null, "nombre_oficial": "…", "ciudad": "…" },
      "tipo_vinculo": "afiliación",
      "fuente_url": "https://pubmed.ncbi.nlm.nih.gov/…",
      "cita_textual": "…",
      "fecha_de_la_fuente": "2021-05",
      "fecha_consulta": "2026-09-15",
      "notas": "Por qué es la misma persona"
    }
  ],
  "pendientes_para_el_proximo_lote": ["ids o textos que quedaron sin revisar"]
}
```

`institucion_nueva`, cuando corresponde, lleva los mismos campos de ubicación que la tarea A:
`nombre_oficial`, `direccion`, `comuna`, `ciudad`, `region`, `lat`, `lon`, `fuente_url`,
`fuente_tipo`, `cita_textual`, `fecha_consulta`.

Valores permitidos:

| Campo | Valores |
|---|---|
| A · `resultado` | `ubicada`, `confirmada`, `corregida`, `no_encontrada` |
| B y C · resultado de una sede | `institucion_existente`, `institucion_nueva`, `marcador_patrocinador`, `no_resoluble` |
| C · `resultado` | `sedes_nombradas`, `solo_marcadores`, `sin_sedes_en_chile` |
| D · `resultado` | `afiliacion_encontrada`, `no_encontrada` |
| `fuente_tipo` | `sitio_oficial`, `superintendencia_salud`, `deis_minsal`, `openstreetmap`, `registro_empresas`, `otro` |
| D · `tipo_vinculo` | `afiliación`, `investigador de sitio` |

## Antes de enviar cada lote, revisá

- [ ] Cada URL abre la página exacta donde está el dato, y la cita está copiada de ahí.
- [ ] La comuna corresponde a la dirección, y la ciudad a la que pide el CSV.
- [ ] No hay coordenadas que la fuente no publique.
- [ ] Ningún vínculo se apoya solo en que los nombres se parecen.
- [ ] Lo que no pudiste verificar está marcado como no encontrado o no resoluble, con el motivo.
