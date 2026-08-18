# Bandeja de revisión

Propuestas generadas automáticamente que **todavía no entraron a la muestra**.

Nada acá se muestra en el sitio público. `web/index.html` lee únicamente
`data/sample/perfiles-muestra.json`; este directorio es la bandeja de revisión humana que
`README.md` promete y que `PRODUCT_CHARTER.md` §5B exige antes de que un dato pase a
`confirmado`.

## De dónde salen

`scripts/enriquecer_openalex.py`, disparado a demanda desde
[Actions → Enriquecer desde OpenAlex](../../actions/workflows/enriquecer-openalex.yml).
El workflow nunca escribe sobre `main`: abre un Pull Request con el archivo de propuesta.

## Cómo se revisa

En el diff del Pull Request. Cada propuesta trae por qué se propuso (`razones_match`) y dos
banderas que exigen atención extra:

- `match_ambiguo: true` — había otro candidato de OpenAlex casi igual de bueno.
- `afiliacion_no_coincide: true` — ninguna institución que OpenAlex conoce coincide con la
  afiliación de nuestra muestra. Puede ser una segunda afiliación legítima, o puede ser otra
  persona con el mismo nombre.

Cerrar el PR sin mergear no pierde nada: el script se vuelve a correr cuando se quiera.
