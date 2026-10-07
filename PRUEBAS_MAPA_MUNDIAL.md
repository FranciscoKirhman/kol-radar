# Mapa mundial: alcance y verificación

Fecha de la carga: 2026-10-07. Fuente de los recuentos:
<https://clinicaltrials.gov/api/v2/stats/field/values?fields=LocationCountry>.
Fuente de cada ensayo: `https://clinicaltrials.gov/study/NCT########`, enlazada
desde el dato. Polígonos: [Natural Earth 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson),
con [condiciones de uso de dominio público](https://www.naturalearthdata.com/about/terms-of-use/).

## Cobertura publicada

- 226 etiquetas con estudios en el facet oficial. 222 se mapearon a ISO2 por
  nombre administrativo exacto o alias literal revisable en el recolector.
  Cuatro etiquetas históricas o ambiguas quedaron explícitas en
  `data/publicado/mundo/cobertura.json`: Serbia and Montenegro, Virgin Islands,
  Federal Republic of Yugoslavia y Netherlands Antilles. No se repartieron sus
  estudios entre países actuales por inferencia.
- 222 países o territorios con recuento y una primera página de detalle.
  En 105, la fuente terminó dentro de esa página y el detalle está completo;
  en 117, queda marcado como parcial y la web permite seguir cargando páginas.
- 14.166 pares país–ensayo con detalle, 29.023 pares ensayo–sede y 12.177
  etiquetas de sede distintas dentro de su país. No son instituciones
  canónicas ni un conteo de ensayos únicos mundiales: un NCT puede estar en
  varios países y una institución puede tener varias grafías.
- 175 polígonos en el mapa de Natural Earth 1:110m. Los países y territorios
  que no tienen polígono visible a esa escala aparecen en el selector.
- El detalle de cada país se descarga bajo demanda. Los JSON publicados de
  todos los países suman 15.178.197 bytes sin comprimir. La interfaz principal
  conserva la fragmentación previa para Chile y añade el índice mundial.
- Con gzip nivel 9, HTML + índice mundial + geometría + fragmento del país
  miden 439.858 bytes para Chile (incluye índice local) y 192.125 bytes para
  Francia (incluye taxonomía). Son tamaños de archivos, no una medición de
  transferencia HTTP ni del tiempo de descarga.

## Comprobaciones

```sh
python3 scripts/verificar_mapa_mundial.py
python3 scripts/verificar_paises.py
python3 scripts/test_verificar_paises.py
python3 scripts/test_puntaje_paridad.py
```

`verificar_mapa_mundial.py` comprueba que cada recuento coincide con el facet
guardado, que cada registro usa el ISO2 y la etiqueta de país correctos, que
cada URL tiene el NCT declarado, que no se guardaron campos de contacto o
investigadores, y que «completo» solo aparece cuando están todos los ensayos
de ese país. Un muestreo determinista de 30 países contrastó NCT, país y sede
textual contra `/api/v2/studies/<NCT>`: **30/30 coincidencias**. Es un control
de muestra, no validación de identidad institucional.

En el navegador se comprobó `web/index.html?pais=FR#mapa` y
`web/index.html?pais=CL#mapa` a 375 px, sin desborde horizontal ni errores
de consola. Francia mostró 43.051 ensayos registrados, 100 con detalle guardado;
el botón de consulta viva amplió el detalle a 200. Se abrió una sede francesa
con su NCT y fuente. Chile conservó sus datos y su mapa detallado junto al
mapa mundial. `web/mundo.html` redirige a la interfaz principal. El aviso
visible de beta se retiró. El mapa utiliza las variables de color, modo oscuro
y tipografía de la vista original.

## Límites deliberados

El recuento oficial no equivale a haber guardado todos los ensayos o centros
de los 117 países parciales. La primera página se guarda para que el mapa sea
rápido; las páginas restantes se consultan al pedirlas en la web. La API puede
no responder o cambiar después de esta fecha. No se deducen coordenadas de
centros a partir del país o la ciudad. El filtro de área deriva de condiciones
declaradas; las no clasificadas siguen visibles en «Todas las áreas».
