#!/usr/bin/env python3
"""El comparador ausente no crea una ficha farmacológica."""
from integrar_farmacos_ctgov import componentes


def nombres(texto):
    return [nombre.strip() for nombre, _ in componentes(texto)]


assert nombres("Tofacitinib without methotrexate") == ["Tofacitinib"]
assert nombres("Azilsartan medoxomil with or without add-on chlorthalidone") == ["Azilsartan medoxomil"]
assert nombres("Pembrolizumab + Carboplatin") == ["Pembrolizumab", "Carboplatin"]
print("PASA: comparadores ausentes y combinaciones declaradas.")
