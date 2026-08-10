# Panorama competitivo

Investigación de referencia (agosto 2026) sobre plataformas existentes de mapeo de
KOL, para no reinventar lo obvio y para ubicar dónde hay un hueco real que este
proyecto puede ocupar.

## Los jugadores grandes

| Plataforma | Qué hace bien | Dato clave |
|---|---|---|
| **IQVIA OneKey / Expert Ecosystem** | Perfiles unificados multi-fuente, IA para detectar "rising stars" y "digital opinion leaders", métrica propia *Share of Scientific Voice (SoSV)* | El SoSV es un score propietario — no se ve cómo se calcula |
| **Veeva Link** | El más completo en amplitud de datos: publicaciones, ensayos, congresos, asociaciones, guías clínicas, grants, **pagos de la industria**, redes sociales, noticias. Mapas de red interactivos por fuerza de conexión. Integrado con Vault CRM | +250.000 fuentes públicas indexadas |
| **H1 (HCP Universe)** | Combina datos científicos con datos de claims (volumen de pacientes), notificaciones en tiempo real, integración con Veeva CRM | 10M+ HCPs, 10B+ claims, cobertura EE.UU./Europa |
| **Komodo Health** | El más agresivo en usar datos de mundo real (claims de 325M de pacientes) para encontrar KOLs "escondidos" en la comunidad, no solo en centros académicos grandes | Enfoque en patrones de referidos y volumen clínico real, no solo publicaciones |
| **Definitive Healthcare / SteepRock / MSLInsight** | Más orientados a CRM de interacción y datos de infraestructura de salud que a mapeo/perfilado en sí | Complementan, no compiten directo |

## Features "estándar" que cualquier jugador serio tiene

1. Perfil unificado: publicaciones + ensayos clínicos + congresos + afiliación institucional + guías clínicas autoría.
2. Visualización de red (coautoría, afiliaciones compartidas).
3. Detección de "rising stars" por tendencia de actividad, no solo volumen histórico total.
4. Filtro geográfico / por territorio.
5. Integración con CRM para cerrar el loop identificación → interacción.
6. App móvil y APIs.

## Lo que SÍ podemos copiar (razonable para un MVP)

- **El esquema de perfil**: publicaciones, ensayos, congresos, afiliación — ya está en nuestro modelo de datos.
- **Visualización de red por coautoría/afiliación** — ya está en el plan (Fase 3).
- **Detección de tendencia ("rising star")**: no necesita datos de claims, solo mirar la pendiente de publicaciones/ensayos en el tiempo. Barato de implementar con PubMed + ClinicalTrials.gov.
- **Patrón de UX**: buscador → mapa/red → perfil individual → evidencia. Es el flujo que ya usan todos, funciona.

## Lo que NO podemos copiar a este tamaño (y está bien no intentarlo)

- **Datos de claims / volumen de pacientes** (Komodo, H1): requieren datos licenciados de aseguradoras o Fonasa/Isapres, que no son públicos ni estructurados así en Chile. No es un problema de esfuerzo, es un problema de acceso a datos que no existe hoy.
- **Datos de pagos de la industria** (Veeva Link): en EE.UU. existe el Sunshine Act con registro público de pagos a médicos. **Chile no tiene un equivalente público** — así que esta columna simplemente no se puede llenar con fuentes públicas, y no hay que fingir que sí.
- **Cobertura global de 10M+ HCPs**: no es la pelea. Cubrir bien un país acotado por especialidad es más creíble que cubrir mal el mundo entero.

## Dónde está el hueco real (la diferenciación)

1. **Transparencia de la fuente, no un score opaco.** Ninguno de los grandes muestra *por qué* alguien tiene tal puntaje — el SoSV de IQVIA y los scores de H1/Komodo son cajas negras. Nuestro modelo (hecho + fuente + fecha + confianza, con link directo) es lo contrario, y en un mercado regulado eso es un argumento de venta real, no solo un detalle técnico.
2. **Chile como foco, no como una fila más en una base global.** Los jugadores grandes cubren Chile de forma superficial dentro de un producto global de precio enterprise (contratos de seis cifras). Nadie está optimizando específicamente para instituciones, sociedades médicas y congresos chilenos.
3. **Accesible para equipos pequeños.** Estas plataformas están pensadas para farmacéuticas grandes. Un laboratorio local, una filial pequeña o un equipo de Medical Affairs de 1-2 personas no tiene ese presupuesto — ahí hay espacio para algo más liviano.
4. **Canal de corrección visible.** Ser explícitos en que un profesional puede pedir corregir o quitar su ficha (lo que ya está en el spec) es higiene que los grandes no siempre exponen con claridad al usuario final.

## Conclusión para el diseño

No compitas en amplitud de datos (ahí pierdes seguro). Compite en **trazabilidad** y
**foco local** — que es exactamente lo que ya definimos en `README.md`. La única
adición que vale la pena incorporar del research: una señal simple de "tendencia" en
el perfil (¿su actividad científica está creciendo o estancada en los últimos 24
meses?), calculable solo con PubMed + ClinicalTrials.gov, sin necesitar datos de
claims.
