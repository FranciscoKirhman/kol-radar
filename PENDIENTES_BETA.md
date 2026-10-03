# Pendientes de la beta

La lista vigente de lo que falta, con quién lo tiene que hacer. Al final, lo que ya se resolvió y
cuándo, para que la próxima iteración no lo busque de cero. Actualizado el 2026-10-03.

## Lo que falta

### Decisiones de Francisco (bloquean publicar más allá de una demo)
1. **Publicar la rama `pendientes-beta-2026-09-28`** en `main` cada vez que avance: el push lo hace
   una persona (`PUBLICAR.md`).
2. ~~El tier público por persona~~: decidido el 2026-09-30, **se mantiene con garantías**
   (explicación en cada ficha, oposición al indicador, evaluación de impacto en `EVALUACION_IMPACTO.md`).
3. ~~Responsable y domicilio~~: Francisco Kirhman, Bello Horizonte 979, Las Condes. Aviso publicado
   en `web/privacidad.html` y enlazado desde el pie (2026-09-30). Falta que lo revise un abogado.
4. ~~Indexación en buscadores~~: decidido el 2026-09-30, **se indexa** (sin `noindex`). El sitio tiene
   descripción, datos estructurados de Dataset y `sitemap.xml`; falta dar de alta la propiedad en
   Google Search Console y enviar el sitemap (lo hace Francisco con su cuenta).

### Tareas externas
5. **Tercera ronda para ChatGPT** (`data/pending/tarea-chatgpt-2026-09-29-ronda3/`): 10 ensayos con sede
   integrados. Faltan 8 instituciones de la A, los 16 textos de sede de la B y 37 ensayos de la segunda
   parte de la C (los de otros patrocinadores que Bristol-Myers Squibb).
6. **OpenAlex**: la API key está como secret y el workflow corre (2026-09-30). Falta revisar su
   propuesta, el PR #2 (28 coincidencias, 5 ambiguas, 21 con otra afiliación), y cerrar el PR #1, del
   2026-08-18, que quedó viejo.
7. **Respaldar** el registro de exclusiones y su clave (`~/.config/kol-radar/`): no hace falta todavía
   (decisión del 2026-09-30), el registro está vacío.

### Patentes (pestaña nueva, 2026-10-03)
8. **Patentes chilenas del compuesto**: el INAPI solo deja buscarlas por el título, y la del compuesto
   casi nunca nombra el fármaco. Para encontrarlas hace falta ligar cada patente de EE.UU. con su
   familia (sus equivalentes chilenas) en la base de la Oficina Europea de Patentes (EPO OPS, gratis con
   registro: lo crea Francisco y la clave va como secret). Con eso, Chile tendría la misma fecha clave
   que EE.UU.
9. **Biológicos sin datos en EE.UU.** (pembrolizumab, nivolumab y la mayoría de los anticuerpos): el
   Purple Book solo publica patentes cuando un biosimilar las pide, y no hay otra fuente abierta que
   las liste. Se pueden buscar a mano, o con EPO OPS por titular y fecha, con revisión de una persona.
10. **Revisar el primer PR mensual** del workflow "Actualizar patentes" (día 20 de cada mes).

### Revisión humana (sin fecha)
11. **Fichas de personas** (Etapa 3): 1 de 3.204 hechos revisado. Empezar por las 8 que entraron desde
   el ISP sin revisión de identidad, las ligaduras de nombre parcial (evidencia encontrada en la
   bandeja del ISP) y las 2 fusiones del 2026-09-29.
12. **Validación con 3–5 MSL** (Etapa 6). Recién después tiene sentido recalibrar el puntaje.

### Deliberadamente sin tocar
- **Modelo de puntaje**: pesos, umbrales, tope de red y heurística de guías, hasta validar con MSL.
  Diagnóstico ya hecho: la red aporta más de la mitad del puntaje a la mayoría; cinco perfiles
  llegan a "Prioridad alta" con un solo hecho de guía o consenso; esa clasificación se deriva del
  texto; los topes por dimensión no se ejercen.
- **Nombres tal como los escribe la fuente**: solo se normaliza la caja de las mayúsculas.
- **Área de un ensayo** por la condición que declara la fuente (ante empate, el área con menos
  ensayos): heurística, no clasificación clínica.
- **Sedes que no se pueden resolver**: 35 marcadores del patrocinador ("Site 122", "Exelixis Clinical
  Site #100") y 159 sedes enmascaradas con código postal ambiguo (`data/pending/sedes-codigo-postal-2026-09-29/ambiguas.json`).

## Cifras al 2026-10-01

| | |
|---|---|
| Fichas | 1.133: 83 personas, 110 instituciones, 579 ensayos, 361 fármacos |
| Ensayos sin ninguna institución | 99 (eran 262 el 2026-09-10) |
| Instituciones ubicadas en el mapa | 96 de 110 |
| Hechos revisados por una persona | 1 de 3.204 |

## Lo resuelto

**2026-10-03**
- Pestaña **Patentes**: cuenta regresiva al próximo vencimiento, vencimientos por año y lista con
  filtros; sección de patentes en el perfil de cada fármaco, con una cronología por producto; aviso en
  Inicio. Datos de `scripts/patentes.py`: 88 fármacos con patentes o exclusividades en EE.UU. (Orange
  Book y Purple Book), 72 con genéricos y 10 con biosimilares ya aprobados allá, y 49 con patentes
  chilenas que los nombran (INAPI).

**2026-10-01**
- Segunda parte de la tarea C, repetida: los informes de resultados de Bristol-Myers Squibb nombran 14
  sedes en 7 ensayos (106 → 99 ensayos sin institución). Un centro que nombran no se liga porque no se
  sabe cuál es.

**2026-09-30**
- Tercera ronda de ChatGPT, primera entrega: 8 sedes nuevas en 3 ensayos que ClinicalTrials.gov
  enmascaraba, tomadas de la publicación o del informe de resultados del estudio (109 → 106 ensayos sin
  institución), y 2 direcciones nuevas (94 → 96 instituciones en el mapa).
- OpenAlex funcionando con la API key como secret; primera propuesta en el PR #2.
- Un enlace `#ficha=` mal formado ya no muestra un error falso; los ids de fichas fusionadas siguen
  abriendo la ficha que quedó (T8).
- Evidencia buscada para las tres ligaduras de nombre parcial del ISP (Burotto, Arén, Yáñez), en la
  bandeja del ISP. No cambia los datos.

**2026-09-29**
- **Registro de exclusiones** fuera del repo, con huellas y clave; todos los scripts lo aplican; en
  supresión y oposición se purga el historial (`PROCESO_SOLICITUDES.md`).
- **Revisión legal** (`REVISION_LEGAL.md`), evaluación de interés legítimo y aviso de privacidad
  completado en lo que no depende de una decisión.
- **ISP**: 8 vínculos de sede, 4 ensayos ganan institución, 18 investigadores (8 fichas nuevas, 6
  existentes ligadas), antes de la revisión de identidad por decisión de Francisco.
- **Fusiones**: Aguayo y Díaz Patiño, con evidencia; los 7 candidatos de ClinicalTrials.gov ya estaban
  ligados; `uchile` y `hosp-uchile` separadas.
- **Sedes por código postal**: 99 ensayos ganan centro (inferencia marcada en la ficha).
- **Fármacos**: 380 → 361, cortes y sufijos unidos; "Soporte" separado de "Otros agentes"; una corrida
  sin red ya no borra clases (T5, T6).
- **CIF**: se descartan NCT repetidos o de otro laboratorio (T7). **OpenAlex**: una rama por corrida,
  sin correo obsoleto (T10). **`.gitignore`** (T9). **Documentación** con cifras calculadas (T11).
- **Reproducibilidad**: `normalizar.py` y `descargar_ctgov.py`; secuencia completa en `PUBLICAR.md` (T4).
- **Ubicaciones**: 90 → 94 instituciones con dirección citada.

**2026-09-28**
- **Mapa**: quadtree (Barnes-Hut); el tope sube de 400 a 2.500 nodos, la simulación converge (antes no
  convergía) y "Ecosistema completo" se agrupa por centro cuando hay más de 250 fichas.
- **Sedes**: de 181 textos en cola a 51; 49 instituciones y 31 alias nuevos, cada uno con su motivo.
- **Fármacos** desde las intervenciones de ClinicalTrials.gov, con tipo según el NCI Thesaurus.
- **Canal de corrección**: correo provisorio (franckirhman@gmail.com) en el pie del sitio.
