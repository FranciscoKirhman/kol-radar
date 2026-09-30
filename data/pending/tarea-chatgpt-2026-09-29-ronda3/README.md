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
