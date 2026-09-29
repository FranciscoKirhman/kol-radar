# Cruce con la planilla de inspecciones del ISP — 2026-09-28

Generado por `scripts/integrar_isp_inspecciones.py`.

**Fuente**: Instituto de Salud Pública de Chile, "Centros de investigación clínica inspeccionados
2016–2025" ([planilla](https://www.ispch.gob.cl/wp-content/uploads/2026/01/CENTROS-DE-INVESTIGACION-CLINICA-INSPECCIONADOS_-2016-2025.xls),
[página](https://www.ispch.gob.cl/anamed/establecimientos-farmaceuticos-y-cosmeticos/centros-de-investigacion-clinica/)),
versión del 29-01-2026. SHA-256 de la planilla usada en `resumen.json`.

## Qué entró a la muestra

- **8 vínculos "sitio del ensayo"** centro ↔ ensayo, cada uno con la URL de la planilla y el texto
  literal del centro. **4 ensayos** que no tenían ninguna institución ahora tienen una:
  NCT02853604 y NCT03662659 (FALP), NCT02869789 y NCT02967692 (CIEC). Ensayos sin institución: 212 → 208.
- **24 hechos** en los ensayos cruzados: "la planilla del ISP registra este estudio, con el código
  de protocolo X, en el centro Y, en una inspección de AAAA". 16 de ellos corroboran una sede que
  ClinicalTrials.gov o la CIF ya declaraban.

Poco, y es lo esperable: la planilla tiene 138 inspecciones de todas las áreas, no solo oncología.
El valor está en que son sedes que ninguna otra fuente nombraba.

## Qué NO entró

- **Resultado, motivo, tipo y fecha de la inspección.** Son una evaluación regulatoria del centro y
  del investigador, no evidencia de actividad clínica. No están en ningún archivo de este repositorio.
- **Ninguna persona.** Los 17 investigadores principales que la planilla nombra para estos
  ensayos están en `investigadores_candidatos.json`, con `decision_humana` vacío.

## Cómo revisar `investigadores_candidatos.json`

Cada candidato dice qué centro, qué ensayo y qué ficha existente podría ser la misma persona:

| Caso | Cuántos | Qué decidir |
|---|---|---|
| Con `fichas_existentes_compatibles` | 9 | Si es la misma persona (mismo nombre, mismo centro que ya figura en su ficha), el vínculo "investigador de sitio" con el ensayo es seguro de agregar. Con nombre abreviado o centro distinto, revisar como una fusión. |
| Sin ficha compatible | 8 | Crear ficha solo tras revisar la identidad: el ISP da nombre, centro y protocolo, nada más. |
| `puede_ser_mas_de_una_persona` | 1 | James Lind, 2024: la celda nombra a dos personas juntas. No se sabe cuál corresponde a cada protocolo. |

`posible_persona_excluida: true` marcaría a alguien que comparte nombre y apellido con una persona
que pidió salir (ver `PROCESO_SOLICITUDES.md`). Hoy no hay ninguno.

## Reglas del cruce

1. Protocolo normalizado (sin mayúsculas, espacios, guiones ni paréntesis) **igual** al
   `orgStudyId` o a un `secondaryId` de **un solo** ensayo. Códigos de menos de 5 caracteres no se
   usan. Los códigos de cada ensayo están en `codigos_ctgov.json`.
2. Centro → institución por la tabla `CENTROS` del script, con el motivo de cada alias.
3. Si el ensayo ya estaba ligado a esa institución, o a otra de su misma red (la Universidad
   Católica y sus centros), no se agrega otro vínculo: una sede no se cuenta dos veces.
4. Renglones sin centro ni investigador (la planilla deja vacías las celdas de una misma
   inspección con varios protocolos) heredan el centro del renglón de arriba, marcado en
   `cruces.json`, pero no el investigador.

`cruces.json` tiene los 24 renglones que calzaron y qué se decidió con cada uno.
