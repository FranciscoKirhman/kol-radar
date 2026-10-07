#!/usr/bin/env python3
"""Comprueba coherencia y límites de privacidad del mapa mundial publicado."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from recolectar_mundo_ctgov import institution_label_allowed

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data" / "publicado" / "mundo"
CLAVES = {
    "country_iso2", "country_name", "area_ids", "facility_text",
    "site_text_redacted", "city", "state", "nct_id", "title",
    "conditions", "status", "source_url", "source_date", "confidence",
    "review_status",
}


def verificar():
    indice = json.loads((DATOS / "indice.json").read_text(encoding="utf-8"))
    cobertura = json.loads((DATOS / "cobertura.json").read_text(encoding="utf-8"))
    fuente = defaultdict(int)
    etiquetas = defaultdict(set)
    for fila in cobertura.get("etiquetas_mapeadas", []):
        iso = fila["iso2"]
        fuente[iso] += fila["ensayos"]
        etiquetas[iso].add(fila["etiqueta_ctgov"])
    assert fuente, "Falta el inventario auditable de etiquetas y conteos de origen"
    vistos = set()
    detallados = 0
    for pais in indice["paises"]:
        iso = pais["iso2"]
        assert re.fullmatch(r"[A-Z]{2}", iso), (iso, "ISO2 inválido")
        assert iso not in vistos, (iso, "ISO2 duplicado")
        vistos.add(iso)
        assert pais["estado"] in {"resumen", "parcial", "completo", "no_recolectado"}
        total = pais["ensayos_fuente"]
        assert total == fuente.get(iso, 0), (iso, "conteo distinto del facet")
        assert pais["ensayos"] == total, (iso, "conteo mostrado distinto de fuente")
        if iso not in fuente:
            assert pais["estado"] == "no_recolectado", (iso, "cero inventado")
            continue
        assert total > 0, (iso, "facet sin estudios")
        if pais["estado"] == "resumen":
            assert pais["ensayos_detalle"] == pais["centros"] == 0, iso
            continue
        detallados += 1
        archivo = DATOS / (iso + ".json")
        assert archivo.is_file(), (iso, "sin fragmento")
        rows = json.loads(archivo.read_text(encoding="utf-8"))["registros"]
        ensayos = set()
        centros = set()
        for r in rows:
            assert set(r) <= CLAVES, (iso, "campo inesperado", set(r) - CLAVES)
            assert r["country_iso2"] == iso, (iso, "país incorrecto")
            assert r["country_name"] in etiquetas[iso], (iso, "etiqueta incorrecta")
            nct = r["nct_id"]
            assert re.fullmatch(r"NCT\d{8}", nct), (iso, nct)
            assert r["source_url"] == "https://clinicaltrials.gov/study/" + nct
            assert r["confidence"] == "pendiente"
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["source_date"])
            if iso != "CL" and r.get("facility_text"):
                assert institution_label_allowed(r["facility_text"]), (iso, nct, "sede no institucional")
            ensayos.add(nct)
            if r.get("facility_text"):
                centros.add((r["facility_text"], r.get("city"), r.get("state")))
        assert len(ensayos) == pais["ensayos_detalle"], (iso, "detalle de ensayos inconsistente")
        assert len(centros) == pais["centros"], (iso, "detalle de sedes inconsistente")
        assert len(ensayos) <= total, (iso, "más ensayos que la fuente")
        if pais["estado"] == "completo":
            assert len(ensayos) == total, (iso, "completo sin todos los ensayos")
    assert vistos >= set(fuente), "Faltan países del facet en el índice"
    print("OK: %d países/territorios con fuente, %d con detalle; sin cruces ni campos de contactos/investigadores." %
          (len(fuente), detallados))


if __name__ == "__main__":
    try:
        verificar()
    except (AssertionError, KeyError, ValueError) as error:
        print("ERROR:", error, file=sys.stderr)
        sys.exit(1)
