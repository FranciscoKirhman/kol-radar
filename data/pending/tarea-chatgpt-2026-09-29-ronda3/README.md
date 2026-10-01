# Tercera ronda para ChatGPT — 2026-09-29

Lo que no se pudo resolver con fuentes directas en la ronda del 2026-09-29:

| Tarea | Qué | Cuántos |
|---|---|---|
| A | Instituciones sin dirección citable | 16 |
| B | Textos de sede de ClinicalTrials.gov que no calzan con ninguna institución (sin los 35 marcadores obvios del patrocinador) | 16 |
| C | Ensayos sin ninguna sede identificada, después de la CIF, el ISP y el código postal | 109 |

## Cómo usarla

1. Abrí una conversación nueva de ChatGPT con búsqueda web activada.
2. Pegá el **mensaje 1** de `PROMPT.md` (todo lo que está entre las líneas `---`). Cuando responda con un
   lote en JSON, guardalo en esta carpeta como `respuesta_lote1_A.json` (la letra es la tarea del lote) y
   escribile "seguí". Repetí hasta que termine la tarea B.
3. Pegá el **mensaje 2** y después el **mensaje 3**, igual.
4. Validá todo junto:
   ```bash
   python3 scripts/validar_respuesta_chatgpt.py data/pending/tarea-chatgpt-2026-09-29-ronda3/respuesta_*.json
   ```
   Cada respuesta queda con su `.informe.md` al lado: errores (no se usan) y avisos (mirar con cuidado).
5. Pasame las respuestas validadas y las integro: las direcciones entran por
   `scripts/consolidar_ubicaciones.py` (esta ronda ya está en su orden), y las sedes, con su evidencia, a
   la muestra como `pendiente`.

`PROMPT.md` se regenera con `python3 scripts/preparar_tarea_chatgpt_ronda3.py` si cambian los datos.

## Resultado (2026-09-30)

| Tarea | Respondido | Integrado |
|---|---|---|
| A | Lote 1: 8 de 16 (`respuesta_lote1_A.json`, validado sin errores) | 2 direcciones, por `consolidar_ubicaciones.py`: `cesfam-juan-pablo-ii` (La Pintana) y `cormun-puente-alto` (su oficina de partes; el punto queda a nivel de comuna). Faltan los 8 de `pendientes_para_el_proximo_lote` |
| B | Nada todavía | — |
| C, primera parte | 55 de 55 (`crudo_C_primera_parte.tsv`, en su propio formato) | 3 ensayos, 8 sedes, por `scripts/integrar_sedes_documentos.py`. Verificadas abriendo cada documento |
| C, segunda parte | Primer intento, 54 de 54 (`crudo_C_segunda_parte_lote*.json`) | Nada: solo volvió a leer ClinicalTrials.gov, que ya sabíamos que enmascara la sede |
| C, segunda parte, repetida (2026-10-01) | 17 ensayos de Bristol-Myers Squibb (`respuesta_lote1_C.json`; las citas se guardan sin el nombre de los investigadores) | 7 ensayos, 14 sedes, por `scripts/integrar_sedes_documentos.py`. Faltan 37 ensayos de otros patrocinadores |

Revisión de las respuestas:
- **CESFAM Juan Pablo II**: la dirección es del sitio de UC CHRISTUS. Que sea el de La Pintana y no otro
  del mismo nombre lo sostiene el propio ensayo (NCT02376023): lo patrocina la Pontificia Universidad
  Católica, con el CESFAM El Roble —también de su red en La Pintana— como colaborador.
- **NCT00072462 (IBIS-II DCIS)**: el apéndice de la publicación nombra, además de los 4 centros, a sus
  investigadores. No se agregan personas desde esta fuente.
- **NCT00481247 y NCT01057810**: la ciudad y el código postal de cada centro del informe calzan con la
  sede enmascarada de ClinicalTrials.gov (Temuco 4810469, Viña del Mar 2540364).
- **Indicios no usados**: NCT00174655 (Clínica Las Condes) y NCT00806819 (Instituto Nacional del Cáncer)
  aparecen solo como afiliación de un autor, lo que no prueba que ahí se trataran pacientes.
- **Informes de Bristol-Myers Squibb** (repetición de la segunda parte): nombran el estudio por su código
  de protocolo, que es el `orgStudyId` de ClinicalTrials.gov (de ahí las 15 advertencias del validador,
  que busca el NCT). Cada centro se comparó con la sede enmascarada: el número de sede ("Local
  Institution - 0131"), o la ciudad y el código postal. Correcciones a la respuesta: el "Centro Oncológico
  Antofagasta" no es nuevo, es `centro-oncologico-norte` (misma dirección); y el "Centro Investigaciones
  Clinicas" de Av. Américo Vespucio 1314, Vitacura (CA209-066, sede 0085) **no se liga**: es el edificio
  del IRAM, pero ClinicalTrials.gov usa ese código postal para el IRAM y para el Centro de Investigaciones
  Clínicas Viña del Mar, y no se sabe cuál es.
- Los informes nombran a los investigadores de cada sede. No se agregan personas desde esta fuente sin
  una decisión explícita.
