# Geolocalización de instituciones — OpenStreetMap, 2026-09-15

**Nada de esto está integrado.** Es una propuesta de ubicación para las 61 instituciones de la
muestra, pendiente de revisión humana.

## Por qué

La muestra solo sabe la ciudad de cada institución, y ClinicalTrials.gov ubica todo en el centroide
de esa ciudad: 36 de las 40 instituciones del área de Santiago comparten un mismo punto. Para
ordenarlas sobre el mapa de la ciudad hace falta su ubicación real, con fuente.

## Cómo se obtuvo

`scripts/geolocalizar_instituciones_osm.py` consulta Nominatim (OpenStreetMap) con el nombre y los
alias de cada institución. Un resultado se acepta solo si cumple las cuatro condiciones:

1. Está dentro de una caja alrededor de la ciudad declarada por la muestra.
2. Es un objeto de salud, educación u oficina: se descartaron estacionamientos, helipuertos y
   estaciones de metro que se llamaban igual (en la primera corrida, "Hospital de Carabineros" era
   un estacionamiento y "Universidad de Chile" una estación de metro).
3. Coinciden las palabras distintivas del nombre, no las genéricas ("hospital", "clínico").
4. Entre el nombre y los alias, gana el que calza más palabras distintivas: "Clínica RedSalud" a
   secas caía en la sede Providencia; la fuente dice Vitacura.

## Resultado

| | |
|---|---|
| Ubicadas | 31 |
| Con otra sede del mismo nombre a más de 500 m (`match_ambiguo`) | 6 |
| Sin ubicar | 30 |

Cada ubicación trae `fuente_url` (el objeto exacto de OpenStreetMap), `fecha`, `confianza:
"pendiente"`, la consulta que la encontró y, si hay, las alternativas. Lo que no pasó el criterio
está en `sin_ubicar.json` con las consultas probadas: trabajo pendiente, no evidencia de nada. Las
30 sin ubicar y las 6 ambiguas están en la tarea de `../tarea-chatgpt-2026-09-15/`.

## Cómo se revisa

Abrir `fuente_url` de cada una y confirmar que el objeto es la sede correcta. Las universidades con
varios campus quedan en el campus que devolvió OpenStreetMap: revisar si es el que corresponde.

Datos © colaboradores de OpenStreetMap, licencia ODbL.
