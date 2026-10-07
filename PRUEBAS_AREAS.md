# Expansión de áreas terapéuticas: Chile, 2026-10-07

La taxonomía en `data/config/areas.json` tiene 15 áreas y 41 enfermedades. Sus identificadores y etiquetas MeSH se consultaron en el [servicio oficial de NLM](https://id.nlm.nih.gov/mesh/lookup). NLM permite reutilizar MeSH con atribución y mención de la versión consultada; esta copia se consultó el 2026-10-07 y puede quedar desactualizada. Las consultas a ClinicalTrials.gov recuperan candidatos: el área solo se asigna si una **condición declarada** coincide con el descriptor o término configurado. No se analizan títulos para asignar áreas.

Flujo reproducible, con la descarga cruda y los candidatos personales **fuera del repositorio**:

```sh
python3 scripts/descargar_ctgov.py --pais CL --todas-areas --salida /private/tmp/kol-radar-ctgov-cl-todas-2026-10-07.json
KOL_FECHA=2026-10-07 python3 scripts/preintegracion_clinicaltrials.py --pais CL --crudo /private/tmp/kol-radar-ctgov-cl-todas-2026-10-07.json --salida /private/tmp/kol-radar-pre-cl-todas-2026-10-07
KOL_FECHA=2026-10-07 python3 scripts/simular_preintegracion.py --pais CL --preintegracion /private/tmp/kol-radar-pre-cl-todas-2026-10-07 --crudo /private/tmp/kol-radar-ctgov-cl-todas-2026-10-07.json
KOL_FECHA=2026-10-07 python3 scripts/integrar_beta.py --pais CL --crudo /private/tmp/kol-radar-ctgov-cl-todas-2026-10-07.json --preintegracion /private/tmp/kol-radar-pre-cl-todas-2026-10-07 --muestra data/sample/perfiles-muestra.json --salida /private/tmp/kol-radar-integracion-cl-todas-2026-10-07.json
python3 scripts/verificar_paises.py
python3 scripts/test_puntaje_paridad.py
python3 scripts/auditar_fuentes_ctgov.py --cantidad 30
```

La muestra integrada pasa de 1.133 a 2.105 entidades: 83 personas (sin altas), 110 instituciones, 1.551 ensayos y 361 fármacos; de 3.374 a 3.811 vínculos. Se sumaron 972 ensayos y 437 vínculos de sede. Todos los hechos nuevos tienen URL de estudio, fecha y confianza `pendiente`. El muestreo determinista de 30 hechos nuevos cotejó título y sede chilena con la API oficial, y pasó 30/30 el 2026-10-07. Los candidatos de personas carecían de un país de afiliación comprobado y no se publicaron.

| Área | Ensayos con condición declarada compatible |
| --- | ---: |
| Oncología | 436 |
| Cardiología | 57 |
| Endocrinología/metabolismo | 85 |
| Neurología | 18 |
| Psiquiatría | 40 |
| Inmunología/reumatología | 122 |
| Infectología | 24 |
| Respiratorio | 128 |
| Gastroenterología/hepatología | 9 |
| Nefrología | 16 |
| Hematología no oncológica | 12 |
| Dermatología | 11 |
| Oftalmología | 5 |
| Enfermedades raras | 4 |
| Vacunas | 15 |

Los conteos por área pueden superponerse si un ensayo declara varias condiciones. 585 ensayos recuperados por las búsquedas no coincidieron de forma directa con la taxonomía y quedan explícitamente sin clasificar; varios usan sinónimos, siglas o condiciones más específicas. No se les asignó un área por el término de búsqueda. La preintegración completa queda privada porque contiene nombres de contactos sin país de afiliación comprobado. En `data/pending/CL/expansion-areas-2026-10-07/` solo se guardan resumen y simulación sin nombres.
