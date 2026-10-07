# Pruebas de parametrización por país (7 de octubre de 2026)

La barrera usa el país de afiliación documentado de cada persona; el país de un sitio de ensayo no lo sustituye. Solo CL tiene aprobación en `data/config/paises.json`. Las bandejas nuevas de CL van en `data/pending/CL/`; las salidas de AR con contactos quedan fuera del repositorio. Los módulos CIF, ISP, DEIS/MINSAL, INAPI y código postal se rechazan para países que no los declaran.

## Comandos de recolección de prueba

Desde la raíz del repo, con el registro de exclusiones configurado:

```bash
python3 scripts/descargar_ctgov.py --pais CL --salida /tmp/kol-radar-ctgov-cl-2026-10-07.json
KOL_FECHA=2026-10-07 python3 scripts/preintegracion_clinicaltrials.py --pais CL --crudo /tmp/kol-radar-ctgov-cl-2026-10-07.json --salida /tmp/kol-radar-pre-cl-2026-10-07
cp data/sample/perfiles-muestra.json /tmp/kol-radar-base-cl-2026-10-07.json
KOL_FECHA=2026-10-07 python3 scripts/integrar_beta.py --pais CL --crudo /tmp/kol-radar-ctgov-cl-2026-10-07.json --preintegracion /tmp/kol-radar-pre-cl-2026-10-07 --muestra /tmp/kol-radar-base-cl-2026-10-07.json --salida /tmp/kol-radar-integrado-cl-2026-10-07.json
```

La API actual devolvió 585 NCT de CL. Frente a la muestra de `main`, la integración en una copia privada agregó 6 ensayos y 25 vínculos, sin personas ni instituciones nuevas. Las entidades/vínculos/hechos pasaron de 1.133/3.374/3.204 a 1.139/3.399/3.210. **No hay diff vacío con la fuente viva**; los ensayos publicados por ClinicalTrials.gov cambiaron desde la descarga de la que se construyó la muestra. No se dispone de esa descarga histórica cruda para demostrar reproducción exacta. Una prueba de compatibilidad sin ensayos nuevos, con crudo `{}` y la preintegración histórica, sí dejó idénticas las tres colecciones, pero no demuestra reproducción integral.

```bash
python3 scripts/descargar_ctgov.py --pais AR --salida /tmp/kol-radar-ctgov-ar-2026-10-07.json
KOL_FECHA=2026-10-07 python3 scripts/preintegracion_clinicaltrials.py --pais AR --crudo /tmp/kol-radar-ctgov-ar-2026-10-07.json --salida /tmp/kol-radar-pre-ar-2026-10-07
KOL_FECHA=2026-10-07 python3 scripts/integrar_beta.py --pais AR --crudo /tmp/kol-radar-ctgov-ar-2026-10-07.json --preintegracion /tmp/kol-radar-pre-ar-2026-10-07 --salida /tmp/kol-radar-integrado-ar-2026-10-07.json
```

AR produjo 976 NCT en crudo; la integración privada agregó 618 ensayos no presentes en la muestra y **0 personas**. La preintegración no resolvió ninguna sede a institución porque el catálogo de alias existente es exclusivamente chileno; 312 candidatos de contacto quedaron fuera del repo. La muestra pública no cambió. Tres intentos de escribir salidas AR dentro del repo (descarga, preintegración e integración) fueron rechazados antes de abrir el destino.

## Límite pendiente

Este avance parametriza las consultas y rutas, pero todavía no produce una colección argentina publicable con instituciones verificadas. Agregar alias nacionales o ROR exige fuentes y revisión; activarlo solo cambiando `estado_aprobado` habilita la barrera legal, no inventa relaciones ni demuestra afiliaciones.
