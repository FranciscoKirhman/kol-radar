# Modelo de costos — pipeline de agentes

Estimación de costo en tokens de API para el pipeline de automatización
(Recolector/Extractor/Resolutor/Revisor descrito en `README.md`), y
recomendación de arquitectura para trackear el gasto real.

Este documento pasó por una revisión adversarial de dos agentes
independientes (uno verificando el realismo de las estimaciones de tokens,
otro verificando qué le faltaba al modelo). Las cifras de abajo ya incorporan
sus correcciones — la primera versión subestimaba/sobreestimaba varias cosas.

## Pricing vigente (agosto 2026, USD por millón de tokens)

| Modelo | Input | Output |
|---|---|---|
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Claude Sonnet 5 | $3.00 ($2.00 hasta 2026-08-31) | $15.00 ($10.00 hasta 2026-08-31) |

Message Batches API: **50% de descuento** en todo el uso de tokens, a cambio
de procesamiento asíncrono (resultados en minutos-horas, máximo 24h). Este
pipeline no es conversacional — encaja naturalmente en Batches y se
recomienda usarla desde el día uno.

## Qué necesita LLM y qué no

- **Recolector**: código plano, sin LLM. PubMed E-utilities y
  ClinicalTrials.gov API v2 son APIs públicas gratuitas. Costo: $0, pero
  requiere una API key gratuita de NCBI para pasar de 3 a 10 solicitudes/s
  (a escala nacional, sin ella la recolección puede tardar días solo por
  rate limiting — no afecta el presupuesto en dólares, sí el cronograma).
- **Extractor**: Haiku 4.5. Tarea de extracción estructurada, no requiere
  juicio complejo.
- **Resolutor de identidad**: código primero, Sonnet 5 solo para casos
  ambiguos. Un match exacto por ORCID o por nombre+institución normalizados
  se resuelve gratis en código — Sonnet 5 se reserva para cuando no hay
  coincidencia determinista (nombres comunes, sin ORCID).
- **Revisor**: Sonnet 5. Juicio de calidad/vigencia, mayor riesgo si se
  equivoca.

## Costo por llamada

| Llamada | Input | Output | Costo |
|---|---|---|---|
| Extractor — abstract PubMed + metadata | ~700 tokens | ~150 tokens | $0.0015 |
| Extractor — página institucional scrapeada | ~2.000 tokens (alta varianza, 300-6.000+) | ~150 tokens | $0.0028 |
| Resolutor — caso ambiguo (Sonnet 5) | ~1.800 tokens | ~150 tokens | $0.0077 |
| Revisor — pasada completa (Sonnet 5) | ~1.800 tokens | ~250 tokens (200 sin hallazgos, hasta 350 con hallazgos) | $0.0092 |

El input de 700 tokens del Extractor para PubMed corrige una sobreestimación
de la primera versión de este modelo (tenía 2.500, ~4-5x más de lo real: un
abstract biomédico típico son 150-300 palabras). El caso de página
institucional se separó porque su varianza es mucho mayor y no debería
compartir cifra con el abstract.

## Costo por perfil (creación inicial)

- ~3 llamadas de Extractor (mezcla PubMed/institucional): ~$0.006
- ~1 comparación de Resolutor en promedio (la mitad de los candidatos
  resuelven gratis por ORCID/nombre exacto, la otra mitad necesita Sonnet 5): ~$0.004
- 1 pasada de Revisor: ~$0.009
- Subtotal: ~$0.019/perfil
- +20% de margen por reintentos (usando `output_config.format` con schema
  estricto en el Extractor, que reduce casi a cero el JSON mal formado, así
  que el margen baja del 30% inicial al 20%): **~$0.023/perfil**

**Con Batches API (recomendado): ~$0.012/perfil.**

## Estimación a escala (creación inicial, precio estándar sin Batches)

| Perfiles | Costo |
|---|---|
| 100 (piloto una especialidad) | ~$2.30 |
| 1.000 (cobertura amplia de una especialidad) | ~$23 |
| 10.000 (multi-especialidad, escala nacional) | ~$230 + ajuste por apellidos comunes (ver abajo) |

Con Batches API, la mitad de estas cifras.

**Advertencia sobre el Resolutor a escala**: el supuesto de "1 comparación
promedio" se degrada a medida que crece la base — con apellidos frecuentes en
Chile (González, Muñoz, Rodríguez) van a aparecer más candidatos plausibles
por nombre, y el Resolutor va a necesitar más comparaciones por perfil nuevo.
No proyectar la cifra de 10.000 perfiles como lineal sin validar contra una
muestra real de distribución de apellidos por especialidad.

## Mantenimiento — corregido

La primera versión de este modelo solo costeaba una pasada del Revisor sobre
hechos ya guardados (~$0.008/perfil/mes). Eso está mal: para una herramienta
que se llama "radar", el mantenimiento tiene que incluir volver a correr
Recolector+Extractor para detectar actividad nueva (publicaciones, ensayos),
no solo re-auditar lo que ya existe. Un ciclo de mantenimiento completo cuesta
aproximadamente lo mismo que la creación inicial:

| Perfiles | Costo por ciclo de actualización |
|---|---|
| 1.000 | ~$23 |
| 10.000 | ~$230 |

La cadencia (mensual, trimestral) es una decisión de producto, no técnica —
define el presupuesto operativo recurrente.

## Lo que este modelo no cuenta como "gratis" si se usa

- **Herramientas de búsqueda/fetch de Anthropic** (`web_search`, `web_fetch`):
  si se usan para páginas de sociedades médicas con JavaScript dinámico
  (donde un scraper propio falla), `web_search` cuesta $10 por 1.000
  búsquedas más los tokens del contenido recuperado, y `web_fetch` no cobra
  por llamada pero factura el contenido como tokens de entrada normales
  (~2.500 tokens por una página de 10KB). Esto ya está reflejado en la cifra
  de "página institucional scrapeada" de arriba, pero si se usan estas
  herramientas en vez de un scraper propio, sumar el costo de `web_search`
  aparte.
- **API pública de ORCID**: gratuita, pero es una integración no
  documentada en el spec original — el Resolutor depende de tener ORCID
  confiable, y ni PubMed ni ClinicalTrials.gov lo garantizan de forma
  consistente.
- **Mecanismo de recuperación de candidatos para el Resolutor**: el spec dice
  que compara "contra perfiles existentes" pero no dice cómo se eligen esos
  candidatos de una base de miles. Si termina necesitando embeddings o
  búsqueda semántica, eso es un costo de infraestructura adicional, no
  incluido aquí — la alternativa más barata es match determinista por ORCID o
  nombre normalizado, que debería bastar para el volumen de esta Fase 4.

## Trackear el gasto real (arquitectura)

Cada llamada a la API devuelve `usage.input_tokens`, `usage.output_tokens`,
`usage.cache_creation_input_tokens` y `usage.cache_read_input_tokens`. Loguear
esto en una tabla simple:

```
token_usage(
  timestamp, run_id, agent_role,        -- recolector/extractor/resolutor/revisor
  entity_id,                            -- qué perfil/hecho se estaba procesando
  model, input_tokens, output_tokens,
  cache_creation_tokens, cache_read_tokens,
  cost_usd                              -- calculado con una tabla de precios editable, no hardcodeado
)
```

Con eso, "costo por perfil", "costo por especialidad" y "gasto mensual" son
consultas SQL simples, no un sistema de observabilidad aparte. Antes de
correr un lote grande, usar `messages.count_tokens()` para estimar el costo
del lote sin gastarlo.

## Estado actual

Modelo verificado, sin implementar todavía — corresponde a la Fase 4
(automatizar PubMed + ClinicalTrials.gov) del roadmap en `README.md`.
