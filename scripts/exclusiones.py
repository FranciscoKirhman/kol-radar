#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registro de exclusiones: personas que pidieron no aparecer en KOL Radar.

El problema que resuelve: si alguien pide que se retire su ficha y se borra a mano, la próxima
recolección de ClinicalTrials.gov o PubMed la vuelve a traer. Este registro es la lista que todos
los scripts respetan: ninguno escribe la muestra sin pasar por `guardar_muestra`, que quita a las
personas excluidas antes de guardar.

Por qué el registro no guarda nombres
-------------------------------------
El repositorio es público. Una lista en texto plano de "médicos que pidieron salir" publicaría
justamente lo que esas personas pidieron no publicar. Por eso `data/exclusiones.json` guarda solo
HUELLAS: un hash BLAKE2b con clave de cada id, ORCID y forma del nombre. Sin la clave no se puede
saber a quién corresponde una huella, ni probar nombres de a uno hasta dar con ella (eso es lo que
permitiría un hash sin clave, porque la lista de oncólogos chilenos es corta).

La clave vive fuera del repositorio:
  - variable de entorno KOL_CLAVE_EXCLUSIONES, o
  - archivo ~/.config/kol-radar/clave-exclusiones (se crea solo con la primera exclusión).
En GitHub Actions va como secret del repositorio con ese mismo nombre.

Falla cerrado: si el registro tiene entradas y no hay clave, o la clave no es la que generó el
registro, los scripts se detienen en vez de seguir como si no hubiera nadie excluido.

Qué cuenta como coincidencia
----------------------------
  exacta   mismo id de ficha, mismo ORCID, o el mismo nombre completo (sin tildes, mayúsculas,
           puntuación ni orden). La persona se quita sin preguntar.
  posible  comparte nombre y un apellido con una persona excluida ("Christian Caglevic" contra
           una exclusión de "Christian Caglevic Medina"). No se crea ni se liga automáticamente:
           queda para revisión humana. Puede ser un homónimo; el costo de equivocarse en esta
           dirección es solo que una ficha espera, y es el que se prefiere.

Uso
---
  python3 scripts/exclusiones.py retirar ID --tipo supresion --fecha-solicitud 2026-10-02
      Quita la ficha y sus vínculos de la muestra, registra la exclusión y lista los archivos del
      repositorio que todavía la nombran (bandejas de revisión, documentos) para limpiarlos a mano.
      --tipo bloqueo guarda una copia de la ficha FUERA del repositorio para poder restaurarla.
  python3 scripts/exclusiones.py registrar --nombre "Nombre Apellido" [--orcid ...] --tipo oposicion ...
      Para quien pide no ser incorporado y todavía no tiene ficha.
  python3 scripts/exclusiones.py verificar
      Revisa que ninguna persona excluida aparezca en la muestra: ni como ficha, ni por ORCID, ni
      nombrada en el texto de otra ficha. Sale con error si encuentra algo. Lo corre CI.
  python3 scripts/exclusiones.py estado
      Cuántas solicitudes hay, de qué tipo y cuántos días quedan de plazo para cada una.

El proceso completo —plazos, qué responder, quién decide— está en PROCESO_SOLICITUDES.md.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import secrets
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# KOL_EXCLUSIONES permite tener el registro fuera del repositorio si se prefiere (ver
# PROCESO_SOLICITUDES.md, "Dónde vive el registro"). Por defecto va en el repo, sin nombres.
REGISTRO = os.environ.get("KOL_EXCLUSIONES") or os.path.join(RAIZ, "data", "exclusiones.json")
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
CLAVE_ENV = "KOL_CLAVE_EXCLUSIONES"
CLAVE_ARCHIVO = os.path.join(os.path.expanduser("~"), ".config", "kol-radar", "clave-exclusiones")
RETIRADOS = os.path.join(os.path.expanduser("~"), ".config", "kol-radar", "retirados")
TIPOS = ("supresion", "oposicion", "bloqueo")
# Art. 11 de la Ley 19.628 reformada por la Ley 21.719: 30 días corridos, prorrogables una vez.
# Ver PROCESO_SOLICITUDES.md; no es asesoría legal.
PLAZO_DIAS = 30

TRATAMIENTOS = {"dr", "dra", "prof", "profa", "md", "phd", "msc", "mg", "mgs"}
ORCID = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")


def tokens(nombre):
    """"Dr. Héctor  Galindo-Aranibar" → ["hector", "galindo", "aranibar"]."""
    s = unicodedata.normalize("NFD", nombre or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return [t for t in re.split(r"[^a-z0-9]+", s) if t and t not in TRATAMIENTOS]


def formas_nombre(nombre):
    """Las dos formas que se registran de un nombre: la completa y los pares nombre–apellido.

    La completa es la lista de palabras ordenada, así "Caglevic, Christian" y "Christian
    Caglevic" dan lo mismo. Los pares son todas las combinaciones de dos palabras de más de una
    letra, también ordenadas: las iniciales ("P.") no alcanzan para decir nada de nadie.
    """
    t = tokens(nombre)
    completa = " ".join(sorted(t)) if len(t) >= 2 else None
    largas = sorted(set(x for x in t if len(x) > 1))
    pares = ["%s|%s" % (largas[i], largas[j]) for i in range(len(largas)) for j in range(i + 1, len(largas))]
    return completa, pares


class SinClave(SystemExit):
    pass


def leer_clave(crear=False):
    clave = os.environ.get(CLAVE_ENV, "").strip()
    if not clave and os.path.exists(CLAVE_ARCHIVO):
        clave = open(CLAVE_ARCHIVO, encoding="utf-8").read().strip()
    if not clave and crear:
        clave = secrets.token_hex(32)
        os.makedirs(os.path.dirname(CLAVE_ARCHIVO), exist_ok=True)
        with open(CLAVE_ARCHIVO, "w", encoding="utf-8") as f:
            f.write(clave + "\n")
        os.chmod(CLAVE_ARCHIVO, 0o600)
        print("Se creó una clave nueva en %s.\n"
              "  Guardala también como secret del repositorio (Settings → Secrets → Actions →\n"
              "  New repository secret, nombre %s) y en un lugar seguro: sin ella nadie puede\n"
              "  volver a leer el registro, y si el proyecto se cede, la clave va con él."
              % (CLAVE_ARCHIVO, CLAVE_ENV), file=sys.stderr)
    return clave or None


def _huella(clave, texto):
    # BLAKE2b acepta una clave de hasta 64 bytes; una clave más larga se resume primero.
    k = clave.encode("utf-8")
    if len(k) > 64:
        k = hashlib.sha512(k).digest()
    return hashlib.blake2b(texto.encode("utf-8"), key=k, digest_size=16).hexdigest()


class Registro(object):
    def __init__(self, ruta=REGISTRO, clave=None, crear_clave=False):
        self.ruta = ruta
        self.datos = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else {"solicitudes": []}
        self.datos.setdefault("solicitudes", [])
        self.clave = clave or leer_clave(crear=crear_clave)
        huella = self.datos.get("huella_clave")
        if self.datos["solicitudes"]:
            if not self.clave:
                raise SinClave(
                    "%s tiene %d solicitud(es) y no hay clave para leerlo.\n"
                    "Definí %s o poné la clave en %s. No se sigue sin ella: seguir sería volver a\n"
                    "publicar a quien pidió salir." % (ruta, len(self.datos["solicitudes"]), CLAVE_ENV, CLAVE_ARCHIVO))
            if huella and huella != self._h("kol-radar/huella-de-la-clave"):
                raise SinClave("La clave disponible no es la que generó " + ruta + ". "
                               "Con otra clave ninguna huella coincide y el registro no protege a nadie.")
        self._indice()

    def _h(self, texto):
        return _huella(self.clave, texto)

    def _indice(self):
        self.exactas, self.pares = set(), set()
        for s in self.datos["solicitudes"]:
            h = s.get("huellas", {})
            for k in ("id", "orcid", "nombre"):
                self.exactas.update(h.get(k, []))
            self.pares.update(h.get("par", []))

    def vacio(self):
        return not self.datos["solicitudes"]

    # ------------------------------------------------------------------ consultas
    def estado_persona(self, nombre=None, id=None, orcid=None):
        """None, "exacta" o "posible". Ver el docstring del módulo."""
        if self.vacio():
            return None
        if id and self._h("id:" + id) in self.exactas:
            return "exacta"
        for o in ORCID.findall(orcid or ""):
            if self._h("orcid:" + o) in self.exactas:
                return "exacta"
        completa, pares = formas_nombre(nombre)
        if completa and self._h("nombre:" + completa) in self.exactas:
            return "exacta"
        if any(self._h("par:" + p) in self.pares for p in pares):
            return "posible"
        return None

    def estado_entidad(self, e):
        if e.get("tipo") != "persona":
            return None
        orcids = " ".join([e.get("orcid") or ""] + [h.get("fuente_url") or "" for h in e.get("hechos", [])
                                                    if "orcid.org" in (h.get("fuente_url") or "")])
        mejor = None
        for nombre in [e.get("nombre")] + list(e.get("alias_en_la_fuente") or []):
            r = self.estado_persona(nombre=nombre, id=e.get("id"), orcid=orcids)
            if r == "exacta":
                return r
            mejor = mejor or r
        return mejor

    # ------------------------------------------------------------------ escritura
    def huellas_de(self, nombres, ids=(), orcids=()):
        h = {"id": set(), "orcid": set(), "nombre": set(), "par": set()}
        for i in ids:
            h["id"].add(self._h("id:" + i))
        for o in orcids:
            for x in ORCID.findall(o or ""):
                h["orcid"].add(self._h("orcid:" + x))
        for n in nombres:
            completa, pares = formas_nombre(n)
            if completa:
                h["nombre"].add(self._h("nombre:" + completa))
            h["par"].update(self._h("par:" + p) for p in pares)
        return {k: sorted(v) for k, v in h.items()}

    def agregar(self, tipo, fecha_solicitud, huellas, nota=""):
        if not self.clave:
            raise SinClave("Hace falta una clave para registrar una exclusión.")
        self.datos["huella_clave"] = self._h("kol-radar/huella-de-la-clave")
        n = max([s.get("n", 0) for s in self.datos["solicitudes"]] + [0]) + 1
        self.datos["solicitudes"].append({
            "n": n, "tipo": tipo, "fecha_solicitud": fecha_solicitud,
            "fecha_aplicada": datetime.date.today().isoformat(),
            "nota": nota, "huellas": huellas})
        self._indice()
        return n

    def guardar(self):
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(self.datos, f, ensure_ascii=False, indent=1)
            f.write("\n")


# ---------------------------------------------------------------------- lo que usan los scripts
def aplicar(base, registro=None):
    """Quita de `base` las personas con coincidencia exacta, y sus vínculos. Devuelve sus ids.

    Las coincidencias posibles NO se quitan acá (sería borrar a un homónimo sin que nadie lo
    decida): se devuelven aparte para que el script que integra no cree ni ligue esas fichas.
    """
    registro = registro or Registro()
    if registro.vacio():
        return [], []
    quitar, posibles = set(), []
    for e in base["entidades"]:
        r = registro.estado_entidad(e)
        if r == "exacta":
            quitar.add(e["id"])
        elif r == "posible":
            posibles.append(e["id"])
    if quitar:
        base["entidades"] = [e for e in base["entidades"] if e["id"] not in quitar]
        base["vinculos"] = [v for v in base["vinculos"] if v["origen"] not in quitar and v["destino"] not in quitar]
    return sorted(quitar), posibles


def guardar_muestra(base, ruta=MUESTRA, registro=None):
    """La única forma en que un script escribe la muestra: primero aplica las exclusiones."""
    quitadas, _ = aplicar(base, registro)
    if quitadas:
        print("exclusiones: %d ficha(s) excluida(s) no se escriben." % len(quitadas), file=sys.stderr)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------- verificación
def _textos(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for t in _textos(v):
                yield t
    elif isinstance(obj, list):
        for v in obj:
            for t in _textos(v):
                yield t


def verificar(base, registro):
    """Lista de problemas: fichas excluidas presentes, o nombres excluidos en el texto de otras."""
    problemas, avisos = [], []
    for e in base["entidades"]:
        r = registro.estado_entidad(e)
        if r == "exacta":
            problemas.append("La ficha %s corresponde a una persona excluida." % e["id"])
        elif r == "posible":
            avisos.append("La ficha %s comparte nombre y apellido con una persona excluida: revisar "
                          "que sea otra persona." % e["id"])
        for t in _textos(e):
            for o in ORCID.findall(t):
                if registro.estado_persona(orcid=o) == "exacta":
                    problemas.append("La ficha %s cita el ORCID de una persona excluida." % e["id"])
        # Un nombre excluido puede quedar escrito en la ficha de OTRO (una coautoría, una nota de
        # identidad). Se buscan todas las ventanas de 2 a 5 palabras de cada texto.
        vistos = set()
        for t in _textos({k: v for k, v in e.items() if k != "id"}):
            p = tokens(t)
            for n in range(2, 6):
                for i in range(len(p) - n + 1):
                    forma = " ".join(sorted(p[i:i + n]))
                    if forma in vistos:
                        continue
                    vistos.add(forma)
                    if registro._h("nombre:" + forma) in registro.exactas:
                        problemas.append("El texto de la ficha %s nombra a una persona excluida." % e["id"])
    return sorted(set(problemas)), sorted(set(avisos))


# ---------------------------------------------------------------------- línea de comandos
def _menciones(nombres, ignorar):
    """Archivos de texto del repositorio que todavía nombran a la persona, para limpiar a mano."""
    patrones = [re.compile(r"\b" + r"\W+".join(re.escape(t) for t in n.split()) + r"\b", re.I)
                for n in nombres if len(n.split()) >= 2]
    hallados = []
    for base, dirs, archivos in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for a in archivos:
            ruta = os.path.join(base, a)
            if ruta in ignorar or not a.endswith((".json", ".md", ".html", ".js", ".mjs", ".py", ".csv", ".txt")):
                continue
            try:
                texto = open(ruta, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            n = sum(len(p.findall(texto)) for p in patrones)
            if n:
                hallados.append((os.path.relpath(ruta, RAIZ), n))
    return hallados


def _fecha(s):
    datetime.date.fromisoformat(s)
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="orden", required=True)
    r = sub.add_parser("retirar", help="quita una ficha de la muestra y registra la exclusión")
    r.add_argument("id")
    r.add_argument("--tipo", choices=TIPOS, required=True)
    r.add_argument("--fecha-solicitud", type=_fecha, required=True)
    r.add_argument("--nota", default="", help="sin nombres: el registro es público")
    g = sub.add_parser("registrar", help="registra a alguien que todavía no tiene ficha")
    g.add_argument("--nombre", action="append", required=True, help="repetible: cada forma del nombre")
    g.add_argument("--orcid", action="append", default=[])
    g.add_argument("--tipo", choices=TIPOS, required=True)
    g.add_argument("--fecha-solicitud", type=_fecha, required=True)
    g.add_argument("--nota", default="")
    sub.add_parser("verificar", help="falla si alguien excluido aparece en la muestra")
    sub.add_parser("estado", help="solicitudes registradas y plazos")
    a = ap.parse_args(argv)

    if a.orden == "estado":
        reg = json.load(open(REGISTRO, encoding="utf-8")) if os.path.exists(REGISTRO) else {}
        sol = reg.get("solicitudes", [])
        print("%d solicitud(es) registrada(s)." % len(sol))
        hoy = datetime.date.today()
        for s in sol:
            limite = datetime.date.fromisoformat(s["fecha_solicitud"]) + datetime.timedelta(days=PLAZO_DIAS)
            print("  #%d %-10s pedida %s, aplicada %s (plazo legal: %s)"
                  % (s["n"], s["tipo"], s["fecha_solicitud"], s.get("fecha_aplicada") or "—", limite))
        return 0

    if a.orden == "verificar":
        reg = Registro()
        if reg.vacio():
            print("Registro de exclusiones vacío: nada que verificar.")
            return 0
        base = json.load(open(MUESTRA, encoding="utf-8"))
        problemas, avisos = verificar(base, reg)
        for x in avisos:
            print("aviso: " + x)
        for x in problemas:
            print("ERROR: " + x)
        if problemas:
            print("%d problema(s). La muestra nombra a alguien que pidió salir." % len(problemas))
            return 1
        print("Ninguna de las %d persona(s) excluida(s) aparece en la muestra." % len(reg.datos["solicitudes"]))
        return 0

    reg = Registro(crear_clave=True)
    if a.orden == "registrar":
        n = reg.agregar(a.tipo, a.fecha_solicitud, reg.huellas_de(a.nombre, orcids=a.orcid), a.nota)
        reg.guardar()
        print("Registrada la solicitud #%d. Ninguna recolección futura va a crear esa ficha." % n)
        for ruta, k in _menciones(a.nombre, set()):
            print("  todavía la nombra: %s (%d vez/veces)" % (ruta, k))
        return 0

    base = json.load(open(MUESTRA, encoding="utf-8"))
    e = next((x for x in base["entidades"] if x["id"] == a.id), None)
    if not e:
        sys.exit("No hay ninguna ficha con id %r en la muestra." % a.id)
    if e["tipo"] != "persona":
        sys.exit("%s es %s, no una persona: el registro de exclusiones es para datos personales." % (a.id, e["tipo"]))
    nombres = [e["nombre"]] + list(e.get("alias_en_la_fuente") or [])
    orcids = [h.get("fuente_url") or "" for h in e.get("hechos", [])] + [e.get("orcid") or ""]
    if a.tipo == "bloqueo":
        # El bloqueo es temporal: la ficha se guarda fuera del repositorio para poder devolverla
        # si la solicitud se resuelve a favor de mantenerla. Supresión y oposición no guardan nada.
        os.makedirs(RETIRADOS, exist_ok=True)
        copia = os.path.join(RETIRADOS, "%s-%s.json" % (datetime.date.today().isoformat(), a.id))
        vin = [v for v in base["vinculos"] if a.id in (v["origen"], v["destino"])]
        json.dump({"entidad": e, "vinculos": vin}, open(copia, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.chmod(copia, 0o600)
        print("Copia para restaurar (fuera del repositorio): " + copia)
    n = reg.agregar(a.tipo, a.fecha_solicitud, reg.huellas_de(nombres, ids=[a.id], orcids=orcids), a.nota)
    reg.guardar()
    antes = len(base["vinculos"])
    quitadas, _ = aplicar(base, reg)
    base["actualizado"] = datetime.date.today().isoformat()
    guardar_muestra(base, registro=reg)
    print("Solicitud #%d: se retiró %s y %d vínculo(s)." % (n, ", ".join(quitadas), antes - len(base["vinculos"])))
    problemas, _ = verificar(base, reg)
    for x in problemas:
        print("  queda por limpiar a mano: " + x)
    menciones = _menciones(nombres, {MUESTRA})
    if menciones:
        print("Archivos del repositorio que todavía la nombran (no se publican en el sitio, pero el\n"
              "repositorio es público; ver PROCESO_SOLICITUDES.md):")
        for ruta, k in menciones:
            print("  %s (%d)" % (ruta, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
