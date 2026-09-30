# Sedes inferidas por código postal — 2026-09-29

Generado por `scripts/sedes_por_codigo_postal.py`. Muchos ensayos de la industria ocultan el nombre
de la sede en ClinicalTrials.gov ("Research Site", "Novartis Investigative Site"), pero publican su
ciudad y su código postal. Si ese código es el mismo que la fuente declara, en otros ensayos, para un
centro con nombre, la sede es muy probablemente ese centro.

**Es una inferencia, no una declaración de la fuente.** Cada vínculo lleva `"criterio":
"codigo_postal"` y la ficha del ensayo lo dice: "sede inferida por código postal (ClinicalTrials.gov no
la nombra)", con un hecho que cita los ensayos que la respaldan.

| | |
|---|---|
| Ensayos sin ninguna sede con nombre | 208 |
| Ensayos con al menos una sede inferida | 99 |
| Vínculos inferidos | 183 |
| Sedes que quedaron sin asignar por ambiguas | 159 (`ambiguas.json`) |
| Ensayos sin institución después | 109 |

Reglas: código postal de 7 dígitos que no termine en 0000 (los terminados en 0000 son genéricos de
ciudad); el centro aparece con ese código en al menos 2 registros con nombre y concentra al menos el
90% de ellos. Si dos centros comparten el código —Bradford Hill y CIEC en 8420383, que están en el
mismo edificio—, no se asigna.

Para revisar: `asignadas.json` tiene cada sede, el código, los centros que usan ese código y hasta
tres ensayos que lo respaldan. Si un código resulta ser de un edificio con varios centros, se agrega
una excepción al script y se vuelve a correr.
