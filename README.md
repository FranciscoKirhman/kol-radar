# KOL Radar — Chile

Radar científico de especialistas, centros y evidencia pública en Chile, pensado como
herramienta de apoyo para Medical Science Liaisons (MSL) y Medical Affairs.

Este documento es el spec inicial del proyecto (Fase 1: planificación). No hay código
todavía — el objetivo de este commit es dejar por escrito qué hace la herramienta, qué
no hace, de dónde saca la información y bajo qué límites opera, antes de construir nada.

## Objetivo

Responder una pregunta concreta en minutos en vez de horas de investigación manual:

> ¿Qué especialistas y centros están activos en un área clínica específica en Chile,
> y con qué evidencia pública se sostiene esa conclusión?

El área clínica es un parámetro de búsqueda, no algo fijo en el código — la herramienta
debe servir para cualquier especialidad, no solo para una patología de ejemplo.

## Usuario inicial y trabajo a resolver

- **Usuario**: MSL o Medical Advisor preparando un territorio, un congreso o una
  conversación científica.
- **Trabajo**: pasar de buscar a mano en PubMed, ClinicalTrials.gov y sitios de
  sociedades médicas, a tener un mapa verificable y con evidencia enlazada.
- **No es** un CRM, no reemplaza revisión humana, no genera un ranking de "a quién
  contactar primero" ni un puntaje de valor comercial.

## Qué NO hace (explícito, no implícito)

- No infiere ni publica datos que no estén ya públicos.
- No guarda datos personales sensibles ni información de contacto privada.
- No calcula un score único ni oculto de "importancia" — muestra señales, no un
  ranking opaco.
- No registra interacciones con profesionales de salud (eso es trabajo de un CRM,
  fuera de alcance).
- No decide nada de forma autónoma: toda incorporación de un dato nuevo pasa por
  revisión humana antes de marcarse como confirmado.

## Marco legal y ético

- Aplica Ley 19.628 sobre protección de la vida privada (Chile). Un profesional de
  salud identificado por nombre es un dato personal, aunque la fuente sea pública.
  La base para tratar ese dato es que es información profesional de interés público
  (autoría científica, afiliación institucional publicada, participación en estudios
  o congresos) — nunca datos de salud propios del profesional ni de pacientes.
- Toda persona listada puede pedir corrección o exclusión de su ficha.
- **Contacto**: [completar — nombre y correo de contacto del responsable del proyecto]
- **Disclaimer visible en la app**: "La información de este sitio proviene de fuentes
  públicas (publicaciones científicas, registros de ensayos clínicos, sitios de
  sociedades médicas y centros de salud). No constituye una evaluación de desempeño
  profesional ni un listado comercial. Si eres un profesional listado aquí y quieres
  corregir o eliminar tu información, contáctanos en la dirección indicada arriba."

## Fuentes (Fase 1)

| Fuente | Estado | Qué se extrae |
|---|---|---|
| PubMed (E-utilities API) | Activa | Publicaciones, coautores, afiliación, fecha |
| ClinicalTrials.gov (API v2) | Activa | Ensayos con sitio en Chile, investigador cuando esté publicado |
| Sitios de sociedades médicas | Activa (manual al inicio) | Directorios, directivas, programas de congresos |
| Hospitales / universidades | Activa (manual al inicio) | Afiliación institucional publicada |
| SciELO / Revista Médica de Chile | Activa | Producción científica local, coautoría |
| Instituto de Salud Pública (ISP) | **Futura, no en MVP** | No tiene registro público navegable de investigadores por patología; requiere revisión caso a caso por protocolo. Se evalúa más adelante. |

Cualquier fuente nueva se agrega a esta tabla antes de integrarse — no se consume
ninguna fuente que no esté documentada acá.

## Modelo de datos mínimo

Cada afirmación sobre una persona guarda cuatro campos, sin excepción:

- **Hecho**: ej. "autor en publicación", "afiliado a este centro", "investigador en
  este ensayo", "ponente en este congreso".
- **Fuente**: URL específica (no un dominio genérico).
- **Fecha**: cuándo ocurrió el hecho y cuándo se revisó por última vez.
- **Confianza**: `confirmado` (revisado por una persona) | `probable` (extraído,
  pendiente de revisión) | `pendiente` (candidato sin validar).

Ningún dato se muestra como "confirmado" sin haber pasado por revisión humana.

## Relaciones de la red (v1)

Tipos de arista, deliberadamente pocos y literales al inicio:

- Médico → coautoría verificable → Médico
- Médico → investigador/centro del estudio → Ensayo clínico
- Médico → afiliación pública → Centro / universidad
- Médico → ponente o moderador → Congreso
- Médico → produce evidencia sobre → Tema clínico

Se llaman "conexiones científicas observables", no "influencia" — es más honesto y
evita sobre-interpretar una coautoría como una relación de poder.

## Arquitectura de agentes (para cuando se automatice — no en el primer commit de código)

| Agente | Hace | No decide |
|---|---|---|
| Recolector | Consulta las fuentes activas y trae candidatos | Si dos personas son la misma |
| Extractor | Convierte una fuente en hechos estructurados (hecho/fuente/fecha) | La importancia de un profesional |
| Resolutor de identidad | Propone coincidencias por nombre, afiliación, ORCID, tema | Unir perfiles automáticamente sin revisión |
| Revisor | Marca datos desactualizados, contradicciones, evidencia débil | Publicar sin paso por revisión humana |

Toda incorporación automática entra a una bandeja de revisión. Una persona acepta,
corrige o rechaza antes de que el dato pase a `confirmado`.

## Roadmap

1. **Fase 1 (este commit)** — spec: qué hace, qué no hace, fuentes, modelo de datos,
   disclaimers.
2. **Fase 2** — 30 fichas armadas a mano en una especialidad de prueba, para validar
   que el modelo de datos y las fuentes tienen sentido antes de automatizar nada.
3. **Fase 3** — red navegable simple (mapa + perfil por persona + botón "ver
   evidencia" en cada afirmación).
4. **Fase 4** — automatizar solo PubMed y ClinicalTrials.gov con los cuatro agentes;
   todo lo demás sigue siendo carga manual revisada.
5. **Fase 5** — matriz de señales (no score único) para priorizar sin caja negra.
6. **Fase 6** — validación con 5 entrevistas a usuarios reales de Medical Affairs.

## Estado actual

En planificación. Sin código todavía.
