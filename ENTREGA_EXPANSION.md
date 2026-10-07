# Entrega de la expansión mundial (borrador para revisión)

Fecha: 2026-10-07. Rama: `expansion-global`. `main` no se modificó.

## Qué quedó implementado

- T0 (`bc59081`): `noindex` en las tres páginas públicas mientras no se complete la revisión de privacidad.
- T1 (`67d2123`): configuración y barrera de publicación de personas por país de afiliación. Solo Chile tiene aprobación; el verificador incluye un caso negativo.
- T2 (`4200d43`): parametrización inicial de los recolectores por país. **Incompleta:** la paridad de la muestra Chile no pasó por deriva de la fuente CTGov y no se comprobó el recorrido completo de Argentina.
- T3 (`8b08d80`): taxonomía de 15 áreas y nueva carga de ensayos Chile. La cobertura de todas las enfermedades y publicaciones por área sigue incompleta.
- T4 (`1470010`): identificadores ROR, ORCID y OpenAlex cuando están respaldados; sin fusión automática de personas.
- T5 (`14d03fb`): índice y fragmentos publicados; la web conserva la carga de Chile por fragmento.
- T6 (`efee22f`): mapa mundial, índice de 222 países o territorios y primera página de estudios y sedes textuales por país en la **misma** `web/index.html`. Selector de país, mapa, búsqueda, filtros, fichas con fuente y red de ensayos/sedes. En países parciales, el botón consulta más páginas directamente a ClinicalTrials.gov. `web/mundo.html` queda como redirección para enlaces previos. Se retiró el aviso visible de beta.

## Alcance real de los datos

El facet de ClinicalTrials.gov tenía 226 etiquetas con ensayos; 222 se asociaron a ISO2. Cuatro etiquetas históricas o ambiguas quedaron sin asignar. Hay detalle guardado de 14.166 pares país–ensayo y 29.023 pares ensayo–sede; 105 países están completos con la primera página y 117 son parciales. Las sedes son cadenas declaradas por la fuente, no instituciones canónicas ni puntos geográficos. El mapa ubica países; no inventa coordenadas para centros.

Chile conserva sus personas, fármacos, patentes y mapa detallado. Fuera de Chile solo se publican ensayos y sedes textuales. El pedido de paridad total con Chile **no está completo**: personas requieren aprobación de Francisco por país en `data/config/paises.json`; faltan fuentes y revisión para fármacos, publicaciones, patentes y ADM1 genérico de todos los países. El mapa utiliza textos de estado/provincia cuando CTGov los declara, sin inferirlos de la ciudad.

## Comprobación reproducible

```sh
python3 -m http.server 8182
# abrir http://localhost:8182/web/index.html?pais=FR#mapa
python3 scripts/verificar_mapa_mundial.py
python3 scripts/verificar_paises.py
python3 scripts/test_verificar_paises.py
python3 scripts/test_puntaje_paridad.py
```

El navegador local mostró Francia y Chile en la interfaz original, a 375 px y 1280 px, sin desborde horizontal ni errores de consola. Francia pasó de 100 a 200 ensayos con detalle al consultar la API; una ficha de sede abrió su NCT y fuente. Chile mantuvo la carga inicial y el mapa propio. JS pasó el control de sintaxis y sigue sin `let`, `const` ni flechas. Gzip nivel 9 de los archivos de carga inicial: 439.858 bytes para Chile y 192.125 para Francia; no es una medición de transferencia HTTP. Un muestreo de 30 registros mundiales contrastado con el endpoint de estudio de CTGov coincidió 30/30 en NCT, país y sede textual. Ver `PRUEBAS_MAPA_MUNDIAL.md`.

## Pendientes que no se marcan como terminados

- T2: recuperar la paridad Chile y verificar el recorrido completo de otro país.
- T6: ADM1 de geoBoundaries para cada país, traducción completa ES/EN y paridad de capas no personales. La selección de áreas muestra las áreas presentes en la carga del país y permite AND/OR en los filtros existentes, pero aún no muestra la jerarquía completa área → enfermedad.
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
