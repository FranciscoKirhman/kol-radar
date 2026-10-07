#!/usr/bin/env python3
"""Caso negativo: una persona de un país no aprobado debe impedir la publicación."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exclusiones

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")


def main():
    base = json.load(open(MUESTRA, encoding="utf-8"))
    base["entidades"].append({"id": "persona-sintetica-prueba", "tipo": "persona",
                              "nombre": "Persona Sintética de Prueba", "pais_afiliacion": "AR", "hechos": []})
    base["vinculos"].append({"origen": "persona-sintetica-prueba", "destino": "prueba",
                             "tipo": "afiliación", "pais_afiliacion": "AR",
                             "alias_fuente": "Persona Sintética de Prueba"})
    with tempfile.TemporaryDirectory(prefix="kol-pais-") as carpeta:
        ruta = os.path.join(carpeta, "muestra.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False)
        r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "verificar_paises.py"),
                            "--muestra", ruta], capture_output=True, text=True)
        if r.returncode == 0 or "persona-sintetica-prueba" not in r.stderr:
            raise AssertionError("El verificador no rechazó la persona de AR: " + r.stdout + r.stderr)
    # La función común de guardado tiene que bloquear ANTES de abrir el archivo público.
    class RegistroVacio:
        def vacio(self):
            return True
    destino = os.path.join(RAIZ, "data", "sample", "__prueba_pais.json")
    try:
        try:
            exclusiones.guardar_muestra(base, destino, RegistroVacio())
        except ValueError as exc:
            if "Publicación bloqueada por país" not in str(exc):
                raise
        else:
            raise AssertionError("guardar_muestra permitió escribir la persona de AR")
        if os.path.exists(destino):
            raise AssertionError("guardar_muestra abrió el destino público antes de rechazar")
    finally:
        if os.path.exists(destino):
            os.unlink(destino)
    print("PASA — la muestra negativa falla como corresponde.")


if __name__ == "__main__":
    main()
