#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registro de exclusiones: personas que pidieron no aparecer en KOL Radar.

El problema que resuelve: si alguien pide que se retire su ficha y se borra a mano, la próxima
recolección de ClinicalTrials.gov o PubMed la vuelve a traer. Este registro es la lista que todos
los scripts respetan: ninguno escribe la muestra sin pasar por `guardar_muestra`, que quita a las
personas excluidas antes de guardar.

Dónde vive (decisión de Francisco, 2026-09-29)
----------------------------------------------
FUERA del repositorio, que es público: una lista de "médicos que pidieron salir" en el repo
publicaría justamente lo que esas personas pidieron no publicar.

  registro  ~/.config/kol-radar/exclusiones.json  (o la ruta en KOL_EXCLUSIONES)
  clave     ~/.config/kol-radar/clave-exclusiones  (o el valor en KOL_CLAVE_EXCLUSIONES)

Los dos se crean con `python3 scripts/exclusiones.py iniciar`. Hay que guardar copia de ambos en
un lugar seguro (un gestor de contraseñas), y si el proyecto se cede, entregarlos con él.

Aun fuera del repo, el registro no guarda nombres sino HUELLAS: un hash BLAKE2b con clave de cada
id, ORCID y forma del nombre. Si el archivo se filtra (una copia de respaldo, un envío por error),
sin la clave no se puede saber a quién corresponde cada huella ni probar nombres hasta dar con ella.

Falla cerrado: si el registro no existe, si tiene solicitudes y falta la clave, o si la clave no es
la que lo armó, los scripts se detienen en vez de seguir como si no hubiera nadie excluido. Un clon
nuevo del repositorio no puede integrar datos hasta que alguien corra `iniciar` (o copie el registro
y la clave de quien lo tiene): es a propósito.

Qué cuenta como coincidencia
----------------------------
  exacta   mismo id de ficha, mismo ORCID, o el mismo nombre completo (sin tildes, mayúsculas,
           puntuación ni orden). La persona se quita sin preguntar.
  posible  comparte nombre y un apellido con una persona excluida ("Ana Pérez" contra una
           exclusión de "Ana Pérez Soto"). No se crea ni se liga automáticamente:
           queda para revisión humana. Puede ser un homónimo; el costo de equivocarse en esta
           dirección es solo que una ficha espera, y es el que se prefiere.

Uso
---
  python3 scripts/exclusiones.py iniciar
      Crea el registro vacío y la clave, si no existen. Una vez por máquina.
  python3 scripts/exclusiones.py retirar ID --tipo supresion --fecha-solicitud 2026-10-02
      Quita la ficha y sus vínculos de la muestra, registra la exclusión, lista los archivos del
      repositorio que todavía la nombran y prepara la purga del historial de git (ver abajo).
      --tipo bloqueo guarda una copia de la ficha FUERA del repositorio para poder restaurarla, y
      no prepara purga: un bloqueo es temporal.
  python3 scripts/exclusiones.py registrar --nombre "Nombre Apellido" [--orcid ...] --tipo oposicion ...
      Para quien pide no ser incorporado y todavía no tiene ficha.
  python3 scripts/exclusiones.py sin-indicador ID --fecha-solicitud 2026-10-02
      La persona sigue en KOL Radar pero sin el indicador de actividad (el nivel "Prioridad alta /
      media / Monitorear"): no se calcula, no se muestra, no filtra ni ordena. Oposición parcial.
  python3 scripts/exclusiones.py verificar
      Revisa que ninguna persona excluida aparezca en la muestra: ni como ficha, ni por ORCID, ni
      nombrada en el texto de otra ficha. Sale con error si encuentra algo. Correrlo antes de cada
      push a main.
  python3 scripts/exclusiones.py estado
      Cuántas solicitudes hay, de qué tipo y cuántos días quedan de plazo para cada una.

Purga del historial (decisión de Francisco, 2026-09-29: se purga)
-----------------------------------------------------------------
Borrar la ficha de la muestra no la borra de GitHub: sigue en cada commit anterior. Para supresión
y oposición, `retirar` y `registrar` escriben fuera del repo el archivo de reemplazos para
`git filter-repo --replace-text` (cada forma del nombre, su id y su ORCID → "[retirado]") y
muestran los comandos. No los ejecutan: reescribir la historia de un repo público y forzar el push
lo hace una persona, mirando lo que hace.

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
PRIVADO = os.path.join(os.path.expanduser("~"), ".config", "kol-radar")
REGISTRO = os.environ.get("KOL_EXCLUSIONES") or os.path.join(PRIVADO, "exclusiones.json")
MUESTRA = os.path.join(RAIZ, "data", "sample", "perfiles-muestra.json")
CLAVE_ENV = "KOL_CLAVE_EXCLUSIONES"
CLAVE_ARCHIVO = os.path.join(PRIVADO, "clave-exclusiones")
RETIRADOS = os.path.join(PRIVADO, "retirados")
PURGAS = os.path.join(PRIVADO, "purgas")
TIPOS = ("supresion", "oposicion", "bloqueo")
# Oposición solo al indicador de actividad (el nivel "Prioridad alta / media / Monitorear"): la
# persona sigue en KOL Radar, pero no se le calcula ni se le muestra. No se purga nada.
TIPO_INDICADOR = "oposicion_indicador"
# Art. 11 de la Ley 19.628 reformada por la Ley 21.719: 30 días corridos, prorrogables una vez.
# Ver PROCESO_SOLICITUDES.md; no es asesoría legal.
PLAZO_DIAS = 30

TRATAMIENTOS = {"dr", "dra", "prof", "profa", "md", "phd", "msc", "mg", "mgs"}
ORCID = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")


def tokens(nombre):
    """"Dra. Ana  Pérez-Soto" → ["ana", "perez", "soto"]."""
    s = unicodedata.normalize("NFD", nombre or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").casefold()
    # \w conserva letras y números de otros alfabetos. Para nombres latinos,
    # el resultado sigue siendo el mismo que el separador ASCII previo.
    return [t for t in re.split(r"[^\w]+|_+", s, flags=re.UNICODE)
            if t and t not in TRATAMIENTOS]


def formas_nombre(nombre):
    """Las dos formas que se registran de un nombre: la completa y los pares nombre–apellido.

    La completa es la lista de palabras ordenada, así "Pérez, Ana" y "Ana Pérez" dan
    lo mismo. Los pares son todas las combinaciones de dos palabras de más de una
    letra, también ordenadas: las iniciales ("P.") no alcanzan para decir nada de nadie.
    """
    t = tokens(nombre)
    completa = " ".join(sorted(t)) if len(t) >= 2 or (len(t) == 1 and
        len(t[0]) >= 2 and any(ord(c) > 127 for c in t[0])) else None
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
              "  Guardá una copia en un lugar seguro (un gestor de contraseñas): sin ella nadie puede\n"
              "  volver a leer el registro, y si el proyecto se cede, la clave va con él."
              % CLAVE_ARCHIVO, file=sys.stderr)
    return clave or None


def _huella(clave, texto):
    # BLAKE2b acepta una clave de hasta 64 bytes; una clave más larga se resume primero.
    k = clave.encode("utf-8")
    if len(k) > 64:
        k = hashlib.sha512(k).digest()
    return hashlib.blake2b(texto.encode("utf-8"), key=k, digest_size=16).hexdigest()


QUE_ES = ("Registro de personas que pidieron no aparecer en KOL Radar (supresión, oposición o bloqueo). "
          "Vive fuera del repositorio. No guarda nombres: solo huellas BLAKE2b con la clave de "
          "clave-exclusiones. Se modifica únicamente con scripts/exclusiones.py; todos los scripts que "
          "escriben la muestra lo aplican antes de guardar. Proceso en PROCESO_SOLICITUDES.md.")


def iniciar(ruta=REGISTRO):
    """Crea el registro vacío y la clave si no existen. No toca un registro que ya existe."""
    clave = leer_clave(crear=True)
    if os.path.exists(ruta):
        return False
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    datos = {"_que_es": QUE_ES, "huella_clave": _huella(clave, "kol-radar/huella-de-la-clave"), "solicitudes": []}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.chmod(ruta, 0o600)
    return True


class Registro(object):
    def __init__(self, ruta=REGISTRO, clave=None, crear_clave=False):
        self.ruta = ruta
        if not os.path.exists(ruta):
            # Sin registro no hay forma de saber si alguien pidió salir: se detiene, no se asume
            # que la lista está vacía.
            raise SinClave(
                "No encuentro el registro de exclusiones en %s.\n"
                "Si esta máquina ya lo tenía, copiá el registro y la clave desde su respaldo (o definí\n"
                "KOL_EXCLUSIONES y %s). Si es una instalación nueva del proyecto, crealo con:\n"
                "  python3 scripts/exclusiones.py iniciar" % (ruta, CLAVE_ENV))
        self.datos = json.load(open(ruta, encoding="utf-8"))
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
        self.exactas, self.pares, self.indicador = set(), set(), set()
        for s in self.datos["solicitudes"]:
            h = s.get("huellas", {})
            if s.get("tipo") == TIPO_INDICADOR:
                for k in ("id", "orcid", "nombre"):
                    self.indicador.update(h.get(k, []))
                continue
            for k in ("id", "orcid", "nombre"):
                self.exactas.update(h.get(k, []))
            self.pares.update(h.get("par", []))

    def sin_indicador(self, e):
        """True si la persona pidió que no se le calcule el indicador (coincidencia exacta)."""
        if e.get("tipo") != "persona" or not self.indicador:
            return False
        if self._h("id:" + e["id"]) in self.indicador:
            return True
        for nombre in [e.get("nombre")] + list(e.get("alias_en_la_fuente") or []):
            completa, _ = formas_nombre(nombre)
            if completa and self._h("nombre:" + completa) in self.indicador:
                return True
        return False

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
        os.chmod(self.ruta, 0o600)


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
    # La oposición al indicador se vuelve a marcar en cada escritura: si una integración recrea la
    # ficha, la marca no se pierde.
    for e in base["entidades"]:
        if registro.sin_indicador(e):
            e["sin_indicador"] = True
    return sorted(quitar), posibles


def guardar_muestra(base, ruta=MUESTRA, registro=None):
    """La única forma en que un script escribe la muestra: primero aplica las exclusiones."""
    import paises
    # La comprobación ocurre ANTES de abrir el archivo. Si falla, el JSON anterior queda intacto.
    destino = os.path.realpath(ruta)
    raiz = os.path.realpath(RAIZ) + os.sep
    if destino.startswith(raiz):
        errores = paises.comprobar_publicacion(base)
        if errores:
            raise ValueError("Publicación bloqueada por país: " + "; ".join(errores[:8]))
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


# Variantes con que una fuente puede escribir cada letra. La purga busca en bytes (UTF-8), así que
# cada variante va como alternativa completa y no dentro de una clase de caracteres.
VARIANTES = {"a": "aáàäâ", "e": "eéèëê", "i": "iíìïî", "o": "oóòöô", "u": "uúùüû", "n": "nñ", "c": "cç"}


def _patron_nombre(nombre):
    """"Ana Pérez" → regex que calza con Ana Perez, ANA PÉREZ, ana-perez (su id)."""
    partes = []
    for t in tokens(nombre):
        letras = []
        for ch in t:
            vs = VARIANTES.get(ch, ch)
            alts = sorted(set(vs + vs.upper()))
            letras.append(re.escape(alts[0]) if len(alts) == 1 else "(?:" + "|".join(re.escape(x) for x in alts) + ")")
        partes.append("".join(letras))
    return r"[\s._,-]+".join(partes)


def preparar_purga(n, nombres, orcids):
    """Escribe FUERA del repositorio el archivo para `git filter-repo --replace-text` y devuelve su ruta.

    Solo nombres completos (dos palabras o más), su id y su ORCID. Las iniciales ("Pérez A") no:
    calzarían también con otras personas y borrarían datos de quien no pidió nada.
    """
    lineas, vistos = [], set()
    for nombre in nombres:
        if len(tokens(nombre)) < 2:
            continue
        for orden in (tokens(nombre), tokens(nombre)[1:] + tokens(nombre)[:1]):
            pat = _patron_nombre(" ".join(orden))
            if pat not in vistos:
                vistos.add(pat)
                # Sin \\b: en bytes, una letra con tilde no es "letra", y "Ángela" no tendría borde.
                lineas.append("regex:(?i)(?<![A-Za-z0-9])" + pat + "(?![A-Za-z0-9])==>[retirado]")
    for o in orcids:
        for x in ORCID.findall(o or ""):
            if x not in vistos:
                vistos.add(x)
                lineas.append("literal:" + x + "==>[retirado]")
    os.makedirs(PURGAS, exist_ok=True)
    ruta = os.path.join(PURGAS, "%s-solicitud-%d.txt" % (datetime.date.today().isoformat(), n))
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    os.chmod(ruta, 0o600)
    return ruta


def _instrucciones_purga(ruta):
    return (
        "\nPurga del historial (decisión 2026-09-29). Lo corre una persona, mirando lo que hace; ver\n"
        "PROCESO_SOLICITUDES.md y la guía de GitHub, que manda sobre esto:\n"
        "  https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository\n"
        "  1. Publicar primero el retiro (commit + push de la muestra sin la ficha).\n"
        "  2. En un directorio fuera del proyecto:\n"
        "       git clone --bare https://github.com/FranciscoKirhman/kol-radar.git kol-radar-purga && cd kol-radar-purga\n"
        "       git filter-repo --sensitive-data-removal --replace-text %s\n"
        "  3. Comprobar que no quedó nada: git log --all -p | grep -ciE '<apellido>'   (tiene que dar 0)\n"
        "  4. git push --force --mirror origin\n"
        "  5. Pedir a GitHub Support que borre las vistas en caché y las referencias de PR, con los\n"
        "     commits que filter-repo informa como primeros cambiados.\n"
        "  6. Volver a clonar el proyecto en cada máquina y borrar ramas y worktrees viejos: tienen la\n"
        "     historia anterior y un push desde ahí la devuelve.\n"
        "  7. Borrar %s.\n" % (ruta, ruta))


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
    sub.add_parser("iniciar", help="crea el registro vacío y la clave, fuera del repositorio")
    si = sub.add_parser("sin-indicador", help="la persona sigue, pero sin indicador de actividad")
    si.add_argument("id")
    si.add_argument("--fecha-solicitud", type=_fecha, required=True)
    si.add_argument("--nota", default="", help="sin nombres: el registro guarda huellas")
    sub.add_parser("verificar", help="falla si alguien excluido aparece en la muestra")
    sub.add_parser("estado", help="solicitudes registradas y plazos")
    a = ap.parse_args(argv)

    if a.orden == "iniciar":
        creado = iniciar()
        print(("Registro creado en %s." if creado else "El registro ya existía en %s; no se tocó.") % REGISTRO)
        print("Clave en %s (o en %s). Guardá copia de los dos en un lugar seguro." % (CLAVE_ARCHIVO, CLAVE_ENV))
        return 0

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
        n = sum(1 for x in reg.datos["solicitudes"] if x.get("tipo") != TIPO_INDICADOR)
        print("Ninguna de las %d persona(s) excluida(s) aparece en la muestra." % n)
        return 0

    reg = Registro()
    if a.orden == "sin-indicador":
        base = json.load(open(MUESTRA, encoding="utf-8"))
        e = next((x for x in base["entidades"] if x["id"] == a.id), None)
        if not e or e["tipo"] != "persona":
            sys.exit("No hay ninguna persona con id %r en la muestra." % a.id)
        nombres = [e["nombre"]] + list(e.get("alias_en_la_fuente") or [])
        n = reg.agregar(TIPO_INDICADOR, a.fecha_solicitud, reg.huellas_de(nombres, ids=[a.id]), a.nota)
        reg.guardar()
        guardar_muestra(base, registro=reg)
        print("Solicitud #%d: %s sigue en KOL Radar, sin indicador de actividad." % (n, a.id))
        return 0
    if a.orden == "registrar":
        n = reg.agregar(a.tipo, a.fecha_solicitud, reg.huellas_de(a.nombre, orcids=a.orcid), a.nota)
        reg.guardar()
        print("Registrada la solicitud #%d. Ninguna recolección futura va a crear esa ficha." % n)
        menciones = _menciones(a.nombre, set())
        for ruta, k in menciones:
            print("  todavía la nombra: %s (%d vez/veces)" % (ruta, k))
        if menciones and a.tipo != "bloqueo":
            print(_instrucciones_purga(preparar_purga(n, a.nombre, a.orcid)))
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
    if a.tipo != "bloqueo":
        print(_instrucciones_purga(preparar_purga(n, nombres + [a.id], orcids)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
