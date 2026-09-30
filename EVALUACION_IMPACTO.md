# Evaluación de impacto — indicador de actividad por persona

Evaluación de impacto en protección de datos del **indicador de actividad** que KOL Radar muestra
junto a cada persona ("Prioridad alta", "Prioridad media", "Monitorear"). La Ley 19.628 reformada
por la Ley 21.719 la pide cuando hay elaboración de perfiles. Decisión de Francisco Kirhman
(responsable), 2026-09-30: **mantener el indicador, con garantías**. Documento para validar con un
abogado; el análisis general está en [`REVISION_LEGAL.md`](REVISION_LEGAL.md).

## 1. Qué es el tratamiento

| | |
|---|---|
| Qué se calcula | Un puntaje por persona y un nivel de tres valores, con las reglas de [`SCORING.md`](SCORING.md) |
| Con qué datos | Solo los hechos públicos de la propia ficha: ensayos clínicos (pesados por fase), publicaciones, guías y consensos, congresos, y la cantidad de conexiones en la red, cada uno pesado por su antigüedad |
| Quién lo ve | Cualquiera que visite el sitio |
| Para qué | Ordenar la investigación de quien prepara un territorio: dónde mirar primero. No decide nada |
| Quién decide con él | Nadie dentro de KOL Radar. El sitio no contacta, no excluye ni califica a nadie por su nivel |

## 2. Por qué es elaboración de perfiles

La ley la define como el tratamiento automatizado para evaluar o predecir, entre otros aspectos, el
rendimiento profesional de una persona. El indicador resume la actividad profesional pública de alguien
en un nivel. Aunque no mide calidad, un lector podría leerlo como una evaluación.

## 3. Necesidad y proporcionalidad

- **Útil para la finalidad**: sin un orden, un profesional de Medical Affairs tiene que leer cada ficha
  para saber dónde mirar. El indicador ahorra ese paso.
- **Datos mínimos**: no usa nada que no esté ya en la ficha con su fuente; nada privado, nada sensible.
- **Transparente**: el cálculo es público (`SCORING.md` y la pestaña "Cómo se calcula" del sitio), y la
  ficha muestra el desglose por componente.
- **Menos intrusivo que la alternativa**: no es un ranking numerado de personas ni compara a nadie
  con nadie en público; son tres niveles gruesos.

## 4. Riesgos para las personas

| Riesgo | Probabilidad | Gravedad | Por qué |
|---|---|---|---|
| Leer "Monitorear" como un juicio sobre la calidad de un médico | Media | Media | El rótulo es corto y la explicación está un clic más abajo |
| Nivel equivocado por un error de identidad (evidencia de un homónimo) | Media | Alta | Casi nada pasó por revisión humana; hay fichas ligadas por nombre |
| Nivel bajo por falta de fuentes, no por falta de actividad | Alta | Baja | Las fuentes cubren ensayos y publicaciones, no la práctica clínica |
| Uso por terceros para decidir sobre una persona | Baja | Media | La base es abierta (ODbL) y el sitio es público |

## 5. Medidas

| Medida | Estado |
|---|---|
| Cada ficha dice qué es y qué no es el indicador: "no evalúa la calidad profesional ni la idoneidad de nadie, y KOL Radar no toma decisiones sobre personas con él" | Hecho (2026-09-30) |
| El cálculo es público y cada ficha muestra el desglose | Hecho |
| Oposición al indicador sin salir del sitio: enlace en cada ficha a un correo con el asunto escrito; `scripts/exclusiones.py sin-indicador` la aplica y la mantiene en cada actualización | Hecho (2026-09-30) |
| Quien se opone no tiene nivel: no se muestra, no filtra, no ordena, no se exporta en la shortlist | Hecho (2026-09-30) |
| Los avisos del sitio ya no dicen "no es una evaluación de desempeño"; dicen que el nivel es un indicador automático de actividad | Hecho (2026-09-30) |
| La nota de identidad es visible cuando una ficha se armó sin revisión | Hecho |
| Revisión humana de las fichas con identidad dudosa | Pendiente (fase de expansión) |
| Validar con usuarios que el rótulo se entiende como se quiere | Pendiente (validación con MSL) |

## 6. Riesgo residual y conclusión

Con estas medidas, el riesgo residual es **moderado**, dominado por los errores de identidad, que no
dependen del indicador sino de la revisión pendiente. El indicador se mantiene. Se revisa esta
evaluación si cambia el cálculo, si el sitio pasa a ordenar o comparar personas de otra forma, si llega
una oposición que muestre un problema no previsto, o al terminar la revisión humana.

Aprobada por: Francisco Kirhman, responsable · 2026-09-30 · Revisada por abogado: [pendiente]
