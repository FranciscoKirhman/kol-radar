# Entrega de la expansión mundial (borrador para revisión)

Fecha: 2026-10-07. Rama: `expansion-global`. `main` no se modificó.

## Qué quedó implementado

- T0 (`bc59081`): `noindex` en las páginas públicas mientras no se complete la revisión de privacidad; la corrección C3 incluye `web/privacidad.html`.
- T1 (`67d2123`): configuración y barrera de publicación de personas por país de afiliación. Solo Chile tiene aprobación; el verificador incluye un caso negativo.
- T2 (`4200d43`): parametrización inicial de los recolectores por país. **Incompleta:** la paridad de la muestra Chile no pasó por deriva de la fuente CTGov y no se comprobó el recorrido completo de Argentina.
- T3 (`8b08d80`): taxonomía de 15 áreas y nueva carga de ensayos Chile. La cobertura de publicaciones por área sigue incompleta.
- T4 (`1470010`): identificadores ROR, ORCID y OpenAlex cuando están respaldados; sin fusión automática de personas.
- T5 (`14d03fb`): índice y fragmentos publicados; la web conserva la carga de Chile por fragmento.
- T6 (`efee22f`): mapa mundial, índice de 222 países o territorios y primera página de estudios y sedes textuales por país en la **misma** `web/index.html`. Selector de país, mapa, búsqueda, filtros, fichas con fuente y red de ensayos/sedes. En países parciales, el botón consulta más páginas directamente a ClinicalTrials.gov. `web/mundo.html` queda como redirección para enlaces previos. Se retiró el aviso visible de beta.
- C1 (`bef4f82`): los nombres de médicos en sedes privadas de países sin aprobación se ocultan, sin quitar ensayo, ciudad ni fuente. La regla de Python y la carga en vivo de JavaScript son equivalentes; también se eliminan los datos de contacto de textos de sede.
- C2 (`4eab8e9`): selector de las 15 áreas de Chile, «Todas» y «Sin clasificar». Cada fragmento se carga al elegirlo; «Todas» reúne entidades por ID y vínculos sin repetir. El filtro muestra área → enfermedad.

## Corrección C3: condiciones y fármacos de Chile

Se revisaron las condiciones declaradas por ClinicalTrials.gov contra los descriptores MeSH de NLM. Se agregaron nodos y variantes verificadas a `data/config/areas.json`. La asignación lee únicamente `condiciones_fuente`, nunca el título. De los 436 ensayos nuevos que estaban en «Sin clasificar», 417 obtuvieron área; quedan 19. Estos últimos declaran principalmente resultados o conceptos inespecíficos (por ejemplo, sensibilidad a la insulina, calidad de vida, preferencias del paciente), procedimientos (hemodiálisis), o temas fuera de las 15 áreas (obstetricia, educación clínica y odontología). No se les asignó un diagnóstico por conjetura.

La integración de intervenciones consultó los 1.551 ensayos de Chile en ClinicalTrials.gov. Se preservaron las 361 fichas de fármacos anteriores y se incorporaron 613 nuevas (974 en total), 123 hechos en fichas anteriores y 1.253 vínculos ensayo → fármaco. Tres fichas nuevas que representaban «without / with or without» como si fuera un principio activo se corrigieron con sus fuentes en `data/pending/CL/farmacos-ctgov-2026-10-07/correcciones.json`. La clasificación NCIt terminó para las 613 fichas nuevas sin fallos de API: 190 permanecen «Sin clasificar» porque no se encontró clase sustentada; una consulta sin respuesta no se transforma en esa categoría. Los fármacos y sus vínculos se incluyen en los fragmentos de todas las áreas con ensayos que los sustentan. Se comprobó que todas las entidades, hechos y vínculos anteriores siguen presentes.

## Alcance real de los datos

El facet de ClinicalTrials.gov tenía 226 etiquetas con ensayos; 222 se asociaron a ISO2. Cuatro etiquetas históricas o ambiguas quedaron sin asignar. Hay detalle guardado de 14.166 pares país–ensayo y 29.023 pares ensayo–sede; 105 países están completos con la primera página y 117 son parciales. Las sedes son cadenas declaradas por la fuente, no instituciones canónicas ni puntos geográficos. El mapa ubica países; no inventa coordenadas para centros.

Chile conserva sus personas, fármacos, patentes y mapa detallado. Fuera de Chile solo se publican ensayos y sedes textuales. El pedido de paridad total con Chile **no está completo**: personas requieren aprobación de Francisco por país en `data/config/paises.json`; faltan fuentes y revisión para fármacos, publicaciones, patentes y ADM1 genérico de todos los países. El mapa utiliza textos de estado/provincia cuando CTGov los declara, sin inferirlos de la ciudad.

## Comprobación reproducible

```sh
python3 -m http.server 8182
# abrir http://localhost:8182/web/index.html?pais=FR#mapa
python3 scripts/verificar_mapa_mundial.py
python3 scripts/test_sede_mundo_paridad.py
python3 scripts/test_areas_cl.py
python3 scripts/test_componentes_farmacos.py
python3 scripts/verificar_paises.py
python3 scripts/test_verificar_paises.py
python3 scripts/test_puntaje_paridad.py
```

El navegador local mostró Francia y Chile en la interfaz original, a 375 px y 1280 px, sin desborde horizontal ni errores de consola. Francia pasó de 100 a 200 ensayos con detalle al consultar la API; una ficha de sede abrió su NCT y fuente. En Chile se comprobó «Sin clasificar» y «Todas»: esta última reunió 1.551 ensayos y 83 profesionales sin duplicar ID. JS pasó el control de sintaxis y sigue sin `let`, `const` ni flechas. Gzip nivel 9 de la carga inicial (índice más Oncología) tras C3: **271.159 bytes**; no es una medición de transferencia HTTP. La cifra anterior a C3 era 439.858 bytes para Chile y 192.125 para Francia. Un muestreo de 30 registros mundiales contrastado con el endpoint de estudio de CTGov coincidió 30/30 en NCT, país y sede textual. Ver `PRUEBAS_MAPA_MUNDIAL.md`.

## Pendientes que no se marcan como terminados

- T2: recuperar la paridad Chile y verificar el recorrido completo de otro país.
- T6: ADM1 de geoBoundaries para cada país, traducción completa ES/EN y paridad de capas no personales.
- T7: normalización del puntaje por cohorte país × área.
- T8: servicio y proceso de opt-out automatizado. No hay despliegue ni secretos creados.
- T9: revisión integral de `COLABORACION_IA.md`, `PUBLICAR.md`, `COSTS.md` y `COMPETITORS.md`.
- Revisión legal local antes de aprobar personas fuera de Chile. Revisar también el aviso de privacidad y definir responsable/canal privado.
- La revisión adversarial independiente A6 de todos los criterios originales aún no se ha completado; el PR permanece en borrador.

## Decisiones de Francisco

1. Aprobar, si corresponde y tras revisión jurídica, `estado_aprobado` de cada país antes de publicar perfiles de personas. Ningún otro país queda activado por este PR.
2. Priorizar los siguientes países y capas de datos para llevarlos al nivel de Chile.
3. Definir el responsable y canal privado de solicitudes; desplegar el opt-out solo tras revisión de T8.

Este PR es un borrador de trabajo. No se fusionó ni publicó el sitio en `main`.
