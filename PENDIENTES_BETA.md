# Pendientes de la beta

La lista vigente de lo que falta, con quién lo tiene que hacer. Al final, lo que ya se resolvió y
cuándo, para que la próxima iteración no lo busque de cero. Actualizado el 2026-09-30.

## Lo que falta

### Decisiones de Francisco (bloquean publicar más allá de una demo)
1. **Publicar la rama `pendientes-beta-2026-09-28`** en `main`: el push lo hace una persona.
2. **El tier público por persona** ("Prioridad alta / media / Monitorear"). Según `REVISION_LEGAL.md`
   es elaboración de perfiles: sacarlo de la vista pública, reemplazarlo por conteos descriptivos, o
   mantenerlo con una evaluación de impacto y publicando su lógica. Antes del 1 de diciembre de 2026.
3. **Responsable legal y domicilio** para `PRIVACIDAD.md`, idealmente con un abogado. Con eso el
   aviso se publica como página del sitio.
4. **Indexación en buscadores** (T1 de la auditoría): decidir cuando 2 y 3 estén resueltos.

### Tareas externas
5. **Tercera ronda para ChatGPT** (`data/pending/tarea-chatgpt-2026-09-29-ronda3/`): 16 instituciones
   sin dirección, 16 textos de sede y 109 ensayos sin institución. Las respuestas se validan con
   `scripts/validar_respuesta_chatgpt.py` y se integran.
6. **OpenAlex**: crear la cuenta y guardar la API key como secret `OPENALEX_API_KEY` cuando se quiera
   usar (desambiguación de autores por ORCID y publicaciones por año). No hace falta ningún correo.
7. **Respaldar** el registro de exclusiones y su clave (`~/.config/kol-radar/`) en un gestor de
   contraseñas. No es urgente mientras el registro esté vacío.

### Revisión humana (sin fecha)
8. **Fichas de personas** (Etapa 3): 1 de 3.194 hechos revisado. Empezar por las 8 que entraron desde
   el ISP sin revisión de identidad, las ligaduras de nombre parcial (evidencia encontrada en la
   bandeja del ISP) y las 2 fusiones del 2026-09-29.
9. **Validación con 3–5 MSL** (Etapa 6). Recién después tiene sentido recalibrar el puntaje.

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

## Cifras al 2026-09-30

| | |
|---|---|
| Fichas | 1.133: 83 personas, 110 instituciones, 579 ensayos, 361 fármacos |
| Ensayos sin ninguna institución | 109 (eran 262 el 2026-09-10) |
| Instituciones ubicadas en el mapa | 94 de 110 |
| Hechos revisados por una persona | 1 de 3.194 |

## Lo resuelto

**2026-09-30**
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
