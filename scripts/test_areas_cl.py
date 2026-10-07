#!/usr/bin/env python3
"""Comprueba asignaciones por condición declarada, sin inferencia por título."""
import areas


def ids(condiciones):
    return {a["id"] for a, _ in areas.desde_condiciones(condiciones)}


def main():
    assert "cardiologia" in ids(["Severe Aortic Stenosis"])
    assert "nefrologia" in ids(["Primary IgA Nephropathy"])
    assert "endocrinologia-metabolismo" in ids(["Type II Diabetes"])
    assert "inmunologia-reumatologia" in ids(["RA"])
    assert "inmunologia-reumatologia" not in ids(["Radiation"])
    assert not ids(["Patient Satisfaction", "Quality of Life"])
    print("PASA: MeSH, variantes de CTGov, siglas exactas y condiciones inespecíficas.")


if __name__ == "__main__":
    main()
