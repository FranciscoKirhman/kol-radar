# Tarea para ChatGPT — 2026-09-15

**Nada de esto está integrado.** Es el paquete para que un colaborador IA complete, con fuentes, lo
que la muestra no resuelve. Las respuestas vuelven a esta carpeta y pasan por el validador y por
revisión humana antes de tocar `data/sample/perfiles-muestra.json`.

## Qué falta (medido sobre la muestra)

| Archivo | Filas | Qué se pide |
|---|---|---|
| `A_instituciones.csv` | 36 | 30 instituciones que OpenStreetMap no encontró, y 6 ubicaciones con advertencia (otra sede del mismo nombre a más de 500 m) |
| `B_sedes_por_resolver.csv` | 181 | Textos de sede de ClinicalTrials.gov que no calzaron con ninguna institución |
| `C_ensayos_sin_sede_nombrada.csv` | 226 | Ensayos sin ninguna conexión y sin sede nombrada en la muestra |
| `D_personas_sin_institucion.csv` | 2 | Personas sin institución ligada |
| `instituciones_existentes.csv` | 61 | Referencia para resolver sedes contra lo que ya existe |

Hoy **262 de 579 ensayos** no tienen ninguna conexión y se dibujan sueltos en el mapa; las tareas
B y C apuntan a eso. Las ubicaciones de la tarea A son las que permiten ordenar las instituciones
sobre el mapa de cada ciudad.

## Cómo se usa

1. En ChatGPT, con búsqueda web activada, adjuntar los cinco CSV y pegar `PROMPT.md` (desde la
   línea horizontal).
2. Pedir lote por lote ("Seguí con el lote 2"). Guardar cada respuesta como
   `respuesta_lote1.json`, `respuesta_lote2.json`, … en esta carpeta.
3. Validar:

       python3 scripts/validar_respuesta_chatgpt.py data/pending/tarea-chatgpt-2026-09-15/respuesta_lote*.json

   Cada archivo genera un `.informe.md` con los ítems válidos, los errores (coordenadas fuera de la
   comuna, comuna de otra región, fuente prohibida, NCT que no contiene la sede…) y las advertencias.
4. Los errores se le devuelven a ChatGPT para que los corrija. Lo válido se revisa a mano: el
   validador descarta lo roto, no confirma que lo demás sea verdad.

## Cómo se regenera

    python3 scripts/preparar_tarea_chatgpt.py

Se vuelve a correr después de integrar respuestas: los CSV salen solo con lo que sigue faltando.
