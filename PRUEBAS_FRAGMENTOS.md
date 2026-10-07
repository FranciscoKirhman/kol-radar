# Carga fragmentada: medición del 2026-10-07

`scripts/publicar_fragmentos.py --pais CL` validó la barrera legal y publicó `data/publicado/indice.json` más 16 fragmentos de Chile: 15 áreas de la taxonomía y una bandeja de ensayos sin clasificar. Los países sin aprobación legal no se publican mediante este comando. El índice informa rutas relativas, áreas y conteos. La web principal carga primero el índice y después solo el fragmento `CL/oncologia.json`; `web/interno.html` usa ese mismo fragmento para la vista oncológica.

| Recurso inicial | Bytes gzip, nivel 9 |
| --- | ---: |
| `web/index.html` | 119.233 |
| `data/publicado/indice.json` | 863 |
| `data/publicado/CL/oncologia.json` | 262.484 |
| Ubicaciones institucionales chilenas | 11.454 |
| Patentes | 32.356 |
| **Total estimado** | **426.390** |

La suma estimada es 426 KB comprimidos y queda bajo el objetivo de 500 KB. No incluye cabeceras HTTP ni caché. En una prueba local a 375 px, `document.documentElement.scrollWidth` fue 360 con `clientWidth` 360, y la consola no mostró errores. La interfaz conserva 83 personas, 110 instituciones, 361 fármacos y los 579 ensayos oncológicos previos; el fragmento contiene 587 ensayos después de la nueva recolección.

El fragmento oncológico tiene 1.141 entidades. Al quitar las 83 personas y sus vínculos, el gzip baja 14.138 bytes, aproximadamente 170 bytes por persona en esta muestra. A mezcla y compresión similares, los 73.610 bytes que restan hasta 500 KB admitirían alrededor de 430 personas adicionales; es una extrapolación de capacidad, no una promesa de rendimiento. Si una sola cohorte supera unas 500 personas nuevas o si crecen mucho los hechos por persona, habrá que fragmentar también por subárea, paginar fichas y medir de nuevo. Los 16 fragmentos juntos ocupan 405.337 bytes gzip; no se cargan juntos al inicio.

```sh
python3 scripts/publicar_fragmentos.py --pais CL
python3 scripts/verificar_paises.py
python3 -m http.server 8182
# Abrir http://localhost:8182/web/index.html a 375 px y en escritorio.
python3 scripts/test_puntaje_paridad.py
```

El JSON de muestra completo sigue disponible como fuente de revisión y reproducción local. El índice solo lista Chile mientras los otros países carezcan de aprobación para publicar personas.
