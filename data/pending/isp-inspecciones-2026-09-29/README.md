# Cruce con la planilla de inspecciones del ISP — 2026-09-28 / 2026-09-29

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

## Investigadores: entraron todos (decisión de Francisco, 2026-09-29)

La planilla nombra 17 celdas de investigador principal para estos ensayos; una nombra a dos personas
(James Lind, 2024), así que son 18 nombres. Francisco decidió que entren todos **antes de revisar su
identidad**. `investigadores_candidatos.json` registra qué se hizo con cada uno.

| Qué | Cuántos | Cómo se ve en la ficha |
|---|---|---|
| Fichas nuevas | 8 | `nota_identidad`: salió de la planilla del ISP, entró antes de la revisión de identidad, sin ORCID ni segunda fuente |
| Nombres ligados a una ficha existente | 10 nombres → 6 fichas | Por la tabla `MISMA_PERSONA` del script: mismo nombre y apellido, o con un apellido más, y un centro que no lo contradice. La ficha lo declara en su `nota_identidad`, y cada hecho dice cómo escribe el nombre la planilla |

Cada persona recibe un hecho con la URL de la planilla y dos vínculos "investigador de sitio": con el
ensayo y con el centro. No "afiliación": la planilla dice dónde fue investigador principal un año,
no dónde trabaja hoy.

**Para la revisión humana que sigue pendiente**: las ligaduras de nombre parcial son las que más
conviene mirar primero. El 2026-09-30 se buscó evidencia para las tres (no se agregó nada a los datos):

| Ligadura | Evidencia encontrada |
|---|---|
| «Mauricio Burotto Pichun» (Bradford Hill, 2023) → Mauricio Burotto | La página oficial de Bradford Hill lista a «Dr. Mauricio Burotto» como «Director Médico»: <https://www.bradfordhill.org/nosotros>. Un solo Mauricio Burotto en el mismo centro. |
| «Osvaldo Arén» (CIEC, 2018) → Osvaldo Arén Frontera | Prensa Médica lo presenta como director del Centro de Investigación Clínica Bradford Hill: <https://prensamedica.org/entrevista-a-dr-osvaldo-aren-director-del-centro-de-investigacion-clinica-bradford-hill/>. CIEC funciona en el mismo edificio (Manzano/Palestina 343, Recoleta). |
| «Eduardo Yáñez Ruiz» (James Lind, 2024) → Eduardo Yañez (SIM Temuco) | La prensa lo describe como oncólogo de Temuco, exjefe de oncología del Hospital Regional y director de James Lind, junto a su hijo Patricio Yáñez. Mismo nombre, misma ciudad y especialidad. |

Si alguna no es la misma persona, se corrige en `MISMA_PERSONA` y se vuelve a correr el script.

**Aviso para esa revisión**: la cobertura de prensa sobre James Lind (T13 y BioBioChile, 2025–2026)
informa que Eduardo y Patricio Yáñez están siendo investigados por la inclusión de pacientes en ensayos.
Nada de eso entra a KOL Radar —no es evidencia de actividad profesional y rige la presunción de
inocencia—, pero conviene tenerlo presente al revisar esas dos fichas y ante cualquier solicitud de
rectificación o retiro.

## Qué NO entró

**Resultado, motivo, tipo y fecha de la inspección.** Son una evaluación regulatoria del centro y del
investigador, no evidencia de actividad clínica. No están en ningún archivo de este repositorio.

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
