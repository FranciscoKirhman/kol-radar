# Identificadores: auditoría del 2026-10-07

Se consultó la [API oficial de ROR](https://ror.readme.io/docs/rest-api) para las 110 instituciones. Solo se agregó un ID cuando una etiqueta completa de un registro activo coincidió exactamente con el nombre normalizado de la institución y su país fue CL. El [registro ROR](https://ror.org/registry/) publica estos datos bajo CC0. De 110 instituciones, 27 (24,5 %) tienen `ror_id`; 83 quedan sin ID. No se eligió ningún candidato por cercanía de nombre.

En las 83 personas, solo dos fichas ya tenían un hecho con URL ORCID propia. Las respuestas públicas de ORCID para [Francisco Aguayo](https://pub.orcid.org/v3.0/0000-0002-9619-7535/person) y [Claudio Silva Fuente-Alba](https://pub.orcid.org/v3.0/0000-0003-2472-1833/person) confirmaron sus nombres o variantes: 2/83 (2,4 %) quedaron con `orcid`. La consulta de OpenAlex por ese ORCID devolvió un solo autor para Francisco Aguayo: 1/83 (1,2 %) tiene `openalex_id`. Para Claudio Silva Fuente-Alba devolvió dos perfiles con el mismo ORCID; ninguno se escogió. Las correspondencias no aplicadas están en `data/pending/CL/identificadores-2026-10-07.json`.

Cada identificador agregado tiene un hecho nuevo con URL exacta, fecha y confianza `pendiente`. No se agregó ninguna persona ni se ejecutó una fusión. `scripts/fusionar_personas.py` ahora conserva el registro histórico, pero su comando no modifica datos. La coincidencia por nombre de la preintegración sigue siendo una propuesta; para países distintos de CL no usa el índice chileno por nombre/apellido. Los normalizadores conservan letras no latinas, y se comparó que las 83 personas chilenas mantienen la misma tokenización anterior.

```sh
python3 scripts/enriquecer_identificadores.py
python3 scripts/verificar_paises.py
python3 scripts/fusionar_personas.py  # informa 0 fusiones; no escribe
python3 scripts/test_puntaje_paridad.py
```

La API es cambiante; repetir el enriquecimiento puede devolver otros resultados y requiere revisar el diff antes de publicar. La página de ROR u ORCID no prueba por sí sola una afiliación actual ni la identidad de un homónimo.
