/* Prototipo — núcleo compartido por las cuatro variantes de prototipos/conexiones.
 *
 * Todo lo que NO es una decisión de diseño vive acá, para que las variantes difieran solo en lo
 * que se está comparando (disposición, modelo de interacción, estrategia de escala):
 *   datos y grafo · búsqueda · filtros con conteos · evidencia de cada conexión · línea de
 *   tiempo · qué comparte la shortlist · estado en la URL · ficha · lienzo con cámara.
 *
 * Estilo ES5 como web/index.html, para que la variante elegida se pueda portar sin reescribir.
 * Nada de acá lo importa el sitio: es una superficie aislada de prototipo. */
(function () {
  "use strict";

  var KR = window.KR = {};

  KR.TIPOS = ["persona", "institucion", "ensayo_clinico"];
  KR.TIPO_LABEL = { persona: "Persona", institucion: "Institución", ensayo_clinico: "Ensayo clínico" };
  KR.TIPO_PLURAL = { persona: "Personas", institucion: "Instituciones", ensayo_clinico: "Ensayos" };
  KR.TIPO_VAR = { persona: "persona", institucion: "institucion", ensayo_clinico: "ensayo" };
  KR.HECHO_LABEL = { publicacion: "Publicación", ensayo_clinico: "Ensayo", afiliacion: "Afiliación" };
  KR.HECHO_VAR = { publicacion: "persona", ensayo_clinico: "ensayo", afiliacion: "institucion" };

  // ------------------------------------------------------------------ utilidades
  KR.norm = function (s) {
    return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  };
  KR.esUrlSegura = function (url) { return typeof url === "string" && /^https?:\/\//i.test(url); };
  KR.el = function (tag, clase, texto) {
    var e = document.createElement(tag);
    if (clase) e.className = clase;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    return e;
  };
  KR.svg = function (tag, attrs) {
    var e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) e.setAttribute(k, attrs[k]);
    return e;
  };
  KR.miles = function (n) { return Number(n).toLocaleString("es-CL"); };
  KR.plural = function (n, uno, varios) { return KR.miles(n) + " " + (n === 1 ? uno : varios); };
  KR.reducirMovimiento = function () {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  };
  // Las mismas curvas que los tokens de CSS (--ease-out / --ease-in-out), para animaciones en JS.
  KR.easeOut = function (t) { return 1 - Math.pow(1 - t, 5); };
  KR.easeInOut = function (t) { return t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2; };
  KR.fuenteNombre = function (url) {
    if (!url) return "";
    if (/pubmed/.test(url)) return "PubMed";
    if (/clinicaltrials\.gov/.test(url)) return "ClinicalTrials.gov";
    if (/scielo/.test(url)) return "SciELO";
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch (e) { return "fuente"; }
  };
  KR.colores = function () {
    var cs = getComputedStyle(document.documentElement);
    function v(n) { return cs.getPropertyValue("--" + n).trim(); }
    return {
      s0: v("surface-0"), s1: v("surface-1"), s2: v("surface-2"), borde: v("border"),
      texto: v("text-primary"), texto2: v("text-secondary"), tenue: v("text-muted"), acento: v("accent"),
      persona: v("persona"), institucion: v("institucion"), ensayo_clinico: v("ensayo"), esDark: v("color-scheme") === "dark"
    };
  };
  KR.alCambiarTema = function (fn) {
    if (!window.matchMedia) return function () {};
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", fn);
    return function () { mq.removeEventListener("change", fn); };
  };

  // ------------------------------------------------------------------ datos y grafo
  KR.cargar = function () {
    function json(r) { if (!r.ok) throw new Error(r.url + " → " + r.status); return r.json(); }
    return Promise.all([
      fetch("../../data/sample/perfiles-muestra.json").then(json),
      fetch("posiciones.json").then(json)
    ]).then(function (r) { KR.preparar(r[0], r[1]); return KR.datos; });
  };

  KR.preparar = function (bruto, pos) {
    var entidades = bruto.entidades.map(function (e) {
      var anios = (e.hechos || []).map(function (h) { var m = /^(\d{4})/.exec(h.fecha || ""); return m ? +m[1] : null; })
        .filter(function (a) { return a; });
      var p = pos.nodos[e.id] || [pos.W / 2, pos.H / 2];
      e._area = e.area || "cáncer de pulmón";
      e._anio = anios.length ? Math.max.apply(null, anios) : null;
      e._x = p[0]; e._y = p[1];
      e._ancla = pos.ancla[e.id] || null;
      e._busca = KR.norm(e.nombre);
      e._buscaExtra = KR.norm([e.subtitulo, e.ciudad].join(" "));
      return e;
    });
    var confianza = { pendiente: 0, confirmado: 0 };
    entidades.forEach(function (e) {
      (e.hechos || []).forEach(function (h) { if (confianza[h.confianza] !== undefined) confianza[h.confianza]++; });
    });
    KR.datos = {
      bruto: bruto,
      grafo: KR.grafo(entidades, bruto.vinculos),
      W: pos.W, H: pos.H,
      confianza: confianza,
      geo: bruto.geo
    };
  };

  // Un grafo es solo índices sobre nodos y vínculos. Las variantes nunca recorren el JSON crudo.
  KR.grafo = function (nodos, vinculos) {
    var byId = {}, adj = {};
    nodos.forEach(function (n) { byId[n.id] = n; adj[n.id] = []; });
    var vs = vinculos.filter(function (v) { return byId[v.origen] && byId[v.destino]; });
    vs.forEach(function (v) {
      adj[v.origen].push({ otro: v.destino, v: v });
      adj[v.destino].push({ otro: v.origen, v: v });
    });
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    nodos.forEach(function (n) {
      n._grado = adj[n.id].length;
      if (n._x < minX) minX = n._x; if (n._x > maxX) maxX = n._x;
      if (n._y < minY) minY = n._y; if (n._y > maxY) maxY = n._y;
    });
    return { nodos: nodos, vinculos: vs, byId: byId, adj: adj, caja: { x0: minX, y0: minY, x1: maxX, y1: maxY } };
  };

  // Vecindario hasta `saltos` de distancia. Devuelve { id: distancia }.
  KR.vecindario = function (grafo, id, saltos, pasa) {
    var dist = {}; dist[id] = 0;
    var frente = [id];
    for (var s = 1; s <= saltos; s++) {
      var nuevo = [];
      frente.forEach(function (x) {
        grafo.adj[x].forEach(function (a) {
          if (dist[a.otro] !== undefined) return;
          if (pasa && !pasa(grafo.byId[a.otro])) return;
          dist[a.otro] = s; nuevo.push(a.otro);
        });
      });
      frente = nuevo;
    }
    return dist;
  };

  // Prueba de carga: copias ANÓNIMAS del grafo real, en mosaico. Sirven para medir cuánto
  // aguanta el dibujo; no son datos y nunca llevan nombres, hechos ni fuentes.
  KR.pruebaDeCarga = function (copias) {
    var base = KR.datos.grafo, W = KR.datos.W, H = KR.datos.H, cols = Math.ceil(Math.sqrt(copias * 1.6));
    var nodos = base.nodos.slice(), vinculos = base.vinculos.slice(), cuenta = 0;
    for (var c = 1; c < copias; c++) {
      var ox = (c % cols) * W * 1.08, oy = Math.floor(c / cols) * H * 1.12;
      base.nodos.forEach(function (n) {
        cuenta++;
        nodos.push({
          id: "prueba-" + c + "-" + n.id, tipo: n.tipo, nombre: "Nodo de prueba " + cuenta,
          subtitulo: "Sintético — prueba de carga", hechos: [], _sintetico: true,
          _area: n._area, _anio: n._anio, _x: n._x + ox, _y: n._y + oy,
          _ancla: n._ancla ? "prueba-" + c + "-" + n._ancla : null, _busca: "", _buscaExtra: ""
        });
      });
      base.vinculos.forEach(function (v) {
        vinculos.push({ origen: "prueba-" + c + "-" + v.origen, destino: "prueba-" + c + "-" + v.destino, tipo: v.tipo, _sintetico: true });
      });
    }
    return KR.grafo(nodos, vinculos);
  };

  // ------------------------------------------------------------------ búsqueda
  // Ubica, no filtra: devuelve fichas para saltar a ellas. Primero los nombres que empiezan con
  // lo escrito, después los que tienen una palabra que empieza así, después el resto.
  KR.buscar = function (q, max) {
    var t = KR.norm(q).trim();
    if (t.length < 2) return [];
    var res = [];
    KR.datos.grafo.nodos.forEach(function (n) {
      var p;
      if (n._busca.indexOf(t) === 0) p = 0;
      else if (n._busca.indexOf(" " + t) !== -1 || n._busca.indexOf("(" + t) !== -1) p = 1;
      else if (n._busca.indexOf(t) !== -1) p = 2;
      else if (n._buscaExtra.indexOf(t) !== -1) p = 3;
      else return;
      res.push({ n: n, p: p });
    });
    var orden = { persona: 0, institucion: 1, ensayo_clinico: 2 };
    res.sort(function (a, b) {
      return a.p - b.p || orden[a.n.tipo] - orden[b.n.tipo] || a.n.nombre.localeCompare(b.n.nombre, "es");
    });
    return res.slice(0, max || 8).map(function (r) { return r.n; });
  };

  // ------------------------------------------------------------------ filtros y conteos
  KR.filtrosVacios = function () {
    return { tipos: { persona: true, institucion: true, ensayo_clinico: true }, areas: [], anios: null };
  };
  KR.pasa = function (n, f) {
    if (!f.tipos[n.tipo]) return false;
    if (f.areas.length && f.areas.indexOf(n._area) === -1) return false;
    if (f.anios && (n._anio === null || n._anio < f.anios[0] || n._anio > f.anios[1])) return false;
    return true;
  };
  // Conteos con dos números por valor, como los paneles del demo de sigma.js y los filtros de
  // Gephi Lite: cuántos hay en total y cuántos quedan visibles con los filtros activos.
  KR.conteos = function (grafo, f, universo) {
    var nodos = universo || grafo.nodos;
    var tipos = {}, areas = {}, anios = {}, visibles = 0, sinFecha = { total: 0, visibles: 0 };
    KR.TIPOS.forEach(function (t) { tipos[t] = { total: 0, visibles: 0 }; });
    nodos.forEach(function (n) {
      if (n._sintetico) return;
      var ok = KR.pasa(n, f);
      tipos[n.tipo].total++; if (ok) { tipos[n.tipo].visibles++; visibles++; }
      var a = areas[n._area] || (areas[n._area] = { area: n._area, total: 0, visibles: 0 });
      a.total++; if (ok) a.visibles++;
      if (n._anio === null) { sinFecha.total++; if (ok) sinFecha.visibles++; return; }
      var y = anios[n._anio] || (anios[n._anio] = { anio: n._anio, total: 0, visibles: 0 });
      y.total++; if (ok) y.visibles++;
    });
    var ys = Object.keys(anios).map(Number).sort(function (a, b) { return a - b; });
    var barras = [];
    if (ys.length) for (var y = ys[0]; y <= ys[ys.length - 1]; y++) barras.push(anios[y] || { anio: y, total: 0, visibles: 0 });
    return {
      total: nodos.filter(function (n) { return !n._sintetico; }).length, visibles: visibles, tipos: tipos,
      areas: Object.keys(areas).map(function (k) { return areas[k]; }).sort(function (a, b) { return b.total - a.total; }),
      barras: barras, sinFecha: sinFecha
    };
  };
  KR.hayFiltros = function (f) {
    return !f.tipos.persona || !f.tipos.institucion || !f.tipos.ensayo_clinico || f.areas.length > 0 || !!f.anios;
  };

  // ------------------------------------------------------------------ evidencia de un vínculo
  // Los vínculos del JSON no traen fuente propia. Se resuelve SOLO por coincidencia exacta, sin
  // inferir: (1) las dos fichas citan la misma URL; (2) un vínculo de sede se remite al registro
  // del ensayo, que es de donde sale la lista de sedes; (3) si no, se dice que falta.
  KR.evidencia = function (v) {
    var g = KR.datos.grafo, a = g.byId[v.origen], b = g.byId[v.destino];
    if (!a || !b || v._sintetico) return { nivel: "sin-fuente", etiqueta: "Vínculo sintético de prueba", items: [] };
    var urlsB = {};
    (b.hechos || []).forEach(function (h) { if (h.fuente_url) urlsB[h.fuente_url] = h; });
    var vistos = {}, items = [];
    (a.hechos || []).forEach(function (h) {
      if (h.fuente_url && urlsB[h.fuente_url] && !vistos[h.fuente_url]) {
        vistos[h.fuente_url] = true;
        items.push({ url: h.fuente_url, texto: h.hecho, fecha: h.fecha });
      }
    });
    if (items.length) return { nivel: "compartida", etiqueta: "Misma fuente en las dos fichas", items: items };
    if (v.tipo === "sitio del ensayo") {
      var ensayo = a.tipo === "ensayo_clinico" ? a : b;
      (ensayo.hechos || []).forEach(function (h) {
        if (h.fuente_url && !vistos[h.fuente_url]) { vistos[h.fuente_url] = true; items.push({ url: h.fuente_url, texto: h.hecho, fecha: h.fecha }); }
      });
      return {
        nivel: "registro",
        etiqueta: "Registro del ensayo" + (v.alias_fuente ? ", donde la sede figura como «" + v.alias_fuente + "»" : ""),
        items: items
      };
    }
    return { nivel: "sin-fuente", etiqueta: "Este vínculo no trae fuente propia en los datos", items: [] };
  };
  KR.evidenciaResumen = function () {
    var r = { compartida: 0, registro: 0, "sin-fuente": 0 };
    KR.datos.grafo.vinculos.forEach(function (v) { r[KR.evidencia(v).nivel]++; });
    return r;
  };

  // ------------------------------------------------------------------ qué comparte la shortlist
  // Como la herramienta "Interlocks" de Oligrapher: dadas varias fichas, lo que las conecta.
  KR.enComun = function (ids) {
    var g = KR.datos.grafo, quienes = {}, directos = [];
    ids.forEach(function (id) {
      if (!g.adj[id]) return;
      g.adj[id].forEach(function (a) {
        if (ids.indexOf(a.otro) !== -1) {
          if (id < a.otro) directos.push({ a: id, b: a.otro, v: a.v });
          return;
        }
        var q = quienes[a.otro] || (quienes[a.otro] = []);
        if (q.indexOf(id) === -1) q.push(id);
      });
    });
    var orden = { institucion: 0, persona: 1, ensayo_clinico: 2 };
    var compartidos = Object.keys(quienes).filter(function (k) { return quienes[k].length >= 2; })
      .map(function (k) { return { n: g.byId[k], quienes: quienes[k] }; })
      .sort(function (x, y) {
        return y.quienes.length - x.quienes.length || orden[x.n.tipo] - orden[y.n.tipo] ||
          x.n.nombre.localeCompare(y.n.nombre, "es");
      });
    return { compartidos: compartidos, directos: directos };
  };

  // ------------------------------------------------------------------ shortlist
  // Clave propia del prototipo: se inicializa con la shortlist del sitio pero nunca la modifica.
  var SL_KEY = "kol-radar-shortlist-prototipo", oyentesSL = [];
  function leerSL() {
    try {
      var s = localStorage.getItem(SL_KEY);
      if (s === null) s = localStorage.getItem("kol-radar-shortlist");
      return JSON.parse(s || "[]") || [];
    } catch (e) { return []; }
  }
  var shortlist = leerSL();
  KR.shortlist = {
    lista: function () { return shortlist.filter(function (id) { return KR.datos && KR.datos.grafo.byId[id]; }); },
    tiene: function (id) { return shortlist.indexOf(id) !== -1; },
    alternar: function (id) {
      if (KR.shortlist.tiene(id)) shortlist = shortlist.filter(function (x) { return x !== id; });
      else shortlist.push(id);
      try { localStorage.setItem(SL_KEY, JSON.stringify(shortlist)); } catch (e) { /* modo privado */ }
      oyentesSL.slice().forEach(function (fn) { fn(); });
    },
    escuchar: function (fn) {
      oyentesSL.push(fn);
      return function () { oyentesSL = oyentesSL.filter(function (x) { return x !== fn; }); };
    }
  };

  // ------------------------------------------------------------------ estado en la URL
  // Como Retina: la vista entera cabe en el enlace. Va en el hash para no chocar con ?v= del
  // selector de variantes. La ficha en foco (`f`) es un nombre de persona: solo entra al enlace
  // cuando el usuario lo pide explícitamente (ver KR.botonCompartir).
  KR.hash = {
    leer: function () {
      var o = {};
      location.hash.replace(/^#/, "").split("&").forEach(function (par) {
        if (!par) return;
        var i = par.indexOf("=");
        o[decodeURIComponent(par.slice(0, i))] = decodeURIComponent(par.slice(i + 1));
      });
      return o;
    },
    aFiltros: function (o) {
      var f = KR.filtrosVacios();
      if (o.t) { f.tipos = { persona: o.t.indexOf("p") !== -1, institucion: o.t.indexOf("i") !== -1, ensayo_clinico: o.t.indexOf("e") !== -1 }; }
      if (o.a) f.areas = o.a.split("|");
      if (o.y && /^\d{4}-\d{4}$/.test(o.y)) f.anios = o.y.split("-").map(Number);
      return f;
    },
    construir: function (f, extra) {
      var o = {};
      if (f) {
        var t = (f.tipos.persona ? "p" : "") + (f.tipos.institucion ? "i" : "") + (f.tipos.ensayo_clinico ? "e" : "");
        if (t !== "pie") o.t = t;
        if (f.areas.length) o.a = f.areas.join("|");
        if (f.anios) o.y = f.anios.join("-");
      }
      for (var k in extra) if (extra[k] !== null && extra[k] !== undefined && extra[k] !== "") o[k] = extra[k];
      return Object.keys(o).map(function (k) { return encodeURIComponent(k) + "=" + encodeURIComponent(o[k]); }).join("&");
    },
    escribir: function (f, extra) {
      var h = KR.hash.construir(f, extra);
      history.replaceState(null, "", location.pathname + location.search + (h ? "#" + h : ""));
    }
  };

  // ------------------------------------------------------------------ componentes compartidos
  KR.formaSVG = function (tipo, tam) {
    var s = KR.svg("svg", { width: tam, height: tam, viewBox: "0 0 10 10", "class": "kr-forma", "aria-hidden": "true" });
    var c = "var(--" + KR.TIPO_VAR[tipo] + ")";
    if (tipo === "persona") s.appendChild(KR.svg("circle", { cx: 5, cy: 5, r: 4.2, fill: c }));
    else if (tipo === "institucion") s.appendChild(KR.svg("rect", { x: 1, y: 1, width: 8, height: 8, rx: 1, fill: c }));
    else s.appendChild(KR.svg("polygon", { points: "5,0.8 9.4,9 0.6,9", fill: c }));
    return s;
  };

  KR.lineaBeta = function () {
    var c = KR.datos.confianza;
    var d = KR.el("details", "kr-beta");
    var s = KR.el("summary");
    s.appendChild(KR.el("strong", "", "Beta"));
    s.appendChild(document.createTextNode(" · fuentes públicas · " + KR.miles(c.pendiente) +
      " hechos sin revisión humana, " + c.confirmado + " confirmado"));
    var mas = KR.el("span", "kr-beta-mas", "Leer más");
    s.appendChild(mas);
    d.appendChild(s);
    var p = KR.el("p", "", "Todo sale de ClinicalTrials.gov, PubMed, SciELO y sitios institucionales, y cada dato " +
      "enlaza a la fuente exacta. Pueden faltar personas, sobrar duplicados y haber identidades sin confirmar. " +
      "No es una evaluación de desempeño profesional ni un listado comercial. ");
    var a = KR.el("a", "", "Reportar un error (reporte público) ↗");
    a.href = "https://github.com/FranciscoKirhman/kol-radar/issues/new"; a.target = "_blank"; a.rel = "noopener noreferrer";
    p.appendChild(a);
    d.appendChild(p);
    d.addEventListener("toggle", function () { mas.textContent = d.open ? "Cerrar" : "Leer más"; });
    return d;
  };

  // Autocompletado accesible (combobox). Sin animación al abrir: se usa con el teclado.
  KR.autocompletar = function (input, opts) {
    var lista = KR.el("ul", "kr-sugerencias");
    lista.setAttribute("role", "listbox");
    lista.id = "kr-sug-" + Math.random().toString(36).slice(2, 8);
    lista.hidden = true;
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-controls", lista.id);
    input.setAttribute("aria-expanded", "false");
    input.parentNode.appendChild(lista);
    var res = [], activo = -1;

    function cerrar() { lista.hidden = true; input.setAttribute("aria-expanded", "false"); activo = -1; }
    function marcar(i) {
      activo = i;
      Array.prototype.forEach.call(lista.children, function (li, j) { li.setAttribute("aria-selected", String(j === i)); });
      if (i >= 0 && lista.children[i]) input.setAttribute("aria-activedescendant", lista.children[i].id);
      else input.removeAttribute("aria-activedescendant");
    }
    function elegir(i) {
      var n = res[i];
      if (!n) return;
      input.value = n.nombre;
      cerrar();
      opts.alElegir(n);
    }
    function pintar() {
      res = KR.buscar(input.value, opts.max || 8);
      lista.innerHTML = "";
      if (!res.length) {
        if (input.value.trim().length >= 2) {
          var vacio = KR.el("li", "kr-sug-vacio", "Nada con ese nombre");
          lista.appendChild(vacio);
          lista.hidden = false;
        } else cerrar();
        return;
      }
      var t = KR.norm(input.value).trim();
      res.forEach(function (n, i) {
        var li = KR.el("li", "kr-sug");
        li.id = lista.id + "-" + i;
        li.setAttribute("role", "option");
        li.appendChild(KR.formaSVG(n.tipo, 10));
        var txt = KR.el("span", "kr-sug-txt");
        var nombre = KR.el("span", "kr-sug-nombre");
        var ini = n._busca.indexOf(t);
        if (ini !== -1 && n._busca.length === n.nombre.length) {
          nombre.appendChild(document.createTextNode(n.nombre.slice(0, ini)));
          nombre.appendChild(KR.el("mark", "", n.nombre.slice(ini, ini + t.length)));
          nombre.appendChild(document.createTextNode(n.nombre.slice(ini + t.length)));
        } else nombre.textContent = n.nombre;
        txt.appendChild(nombre);
        txt.appendChild(KR.el("span", "kr-sug-sub", KR.TIPO_LABEL[n.tipo] + (n.subtitulo ? " · " + n.subtitulo : "")));
        li.appendChild(txt);
        if (opts.etiqueta) { var et = opts.etiqueta(n); if (et) li.appendChild(KR.el("span", "kr-sug-tag", et)); }
        li.addEventListener("pointerdown", function (ev) { ev.preventDefault(); elegir(i); });
        li.addEventListener("pointermove", function () { if (activo !== i) marcar(i); });
        lista.appendChild(li);
      });
      lista.hidden = false;
      input.setAttribute("aria-expanded", "true");
      marcar(0);
    }
    input.addEventListener("input", pintar);
    input.addEventListener("focus", function () { if (input.value.trim().length >= 2) pintar(); });
    input.addEventListener("blur", function () { setTimeout(cerrar, 0); });
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown" && res.length) { ev.preventDefault(); if (lista.hidden) pintar(); else marcar(Math.min(res.length - 1, activo + 1)); }
      else if (ev.key === "ArrowUp" && res.length) { ev.preventDefault(); marcar(Math.max(0, activo - 1)); }
      else if (ev.key === "Enter") { ev.preventDefault(); if (!lista.hidden) elegir(activo < 0 ? 0 : activo); }
      else if (ev.key === "Escape") { if (!lista.hidden) { ev.stopPropagation(); cerrar(); } else if (input.value) { input.value = ""; } }
    });
    return { cerrar: cerrar };
  };

  // Barras de faceta al estilo del demo de sigma.js: la barra mide el total, el relleno lo visible.
  KR.faceta = function (opts) {
    var ul = KR.el("ul", "kr-faceta");
    var max = Math.max.apply(null, opts.filas.map(function (f) { return f.total; }).concat(1));
    opts.filas.forEach(function (fila) {
      var li = KR.el("li", "kr-faceta-fila" + (fila.activa ? "" : " apagada"));
      var lab = KR.el("label");
      var cb = KR.el("input"); cb.type = "checkbox"; cb.checked = fila.activa;
      cb.addEventListener("change", function () { opts.alCambiar(fila.clave, cb.checked); });
      lab.appendChild(cb);
      if (fila.forma) lab.appendChild(KR.formaSVG(fila.forma, 10));
      var cuerpo = KR.el("span", "kr-faceta-cuerpo");
      var linea = KR.el("span", "kr-faceta-linea");
      linea.appendChild(KR.el("span", "kr-faceta-nombre", fila.nombre));
      linea.appendChild(KR.el("span", "kr-faceta-num",
        fila.visibles === fila.total ? KR.miles(fila.total) : KR.miles(fila.visibles) + " / " + KR.miles(fila.total)));
      cuerpo.appendChild(linea);
      var barra = KR.el("span", "kr-faceta-barra");
      barra.style.width = Math.max(4, (100 * fila.total) / max) + "%";
      var relleno = KR.el("span", "kr-faceta-relleno");
      relleno.style.transform = "scaleX(" + (fila.total ? fila.visibles / fila.total : 0) + ")";
      if (fila.color) relleno.style.background = fila.color;
      barra.appendChild(relleno);
      cuerpo.appendChild(barra);
      lab.appendChild(cuerpo);
      li.appendChild(lab);
      ul.appendChild(li);
    });
    return ul;
  };

  // Histograma de años con selección por arrastre, como el filtro de rango de Gephi Lite:
  // barra fantasma = todas las fichas de ese año, barra sólida = las que quedan visibles.
  KR.histograma = function (opts) {
    var cont = KR.el("div", "kr-histo");
    var barras = opts.barras, n = barras.length;
    if (!n) return cont;
    var W = 260, H = 64, gap = 1, bw = (W - gap * (n - 1)) / n;
    var max = Math.max.apply(null, barras.map(function (b) { return b.total; }).concat(1));
    // Escala raíz: 2026 concentra la mitad de los hechos y aplastaría al resto de los años.
    function alto(v) { return v ? Math.max(2, Math.sqrt(v / max) * (H - 4)) : 0; }
    var svg = KR.svg("svg", { viewBox: "0 0 " + W + " " + (H + 14), "class": "kr-histo-svg", role: "img" });
    var rango = opts.rango ? opts.rango.slice() : null;
    var grupos = [];
    barras.forEach(function (b, i) {
      var x = i * (bw + gap);
      var g = KR.svg("g", {});
      g.appendChild(KR.svg("rect", { x: x, y: H - alto(b.total), width: bw, height: alto(b.total), "class": "kr-histo-total" }));
      g.appendChild(KR.svg("rect", { x: x, y: H - alto(b.visibles), width: bw, height: alto(b.visibles), "class": "kr-histo-vis" }));
      var t = KR.svg("title", {}); t.textContent = b.anio + ": " + b.visibles + " de " + b.total + " fichas";
      g.appendChild(t);
      svg.appendChild(g);
      grupos.push(g);
    });
    [barras[0].anio, barras[n - 1].anio].forEach(function (a, i) {
      var tx = KR.svg("text", { x: i ? W : 0, y: H + 11, "text-anchor": i ? "end" : "start", "class": "kr-histo-eje" });
      tx.textContent = a; svg.appendChild(tx);
    });
    cont.appendChild(svg);
    var pie = KR.el("div", "kr-histo-pie");
    var resumen = KR.el("span", "kr-histo-resumen");
    var todo = KR.el("button", "kr-btn kr-btn-chico", "Todos los años");
    todo.type = "button";
    pie.appendChild(resumen); pie.appendChild(todo);
    cont.appendChild(pie);

    function pintar() {
      grupos.forEach(function (g, i) {
        var dentro = !rango || (barras[i].anio >= rango[0] && barras[i].anio <= rango[1]);
        g.setAttribute("class", dentro ? "" : "fuera");
      });
      todo.hidden = !rango;
      resumen.textContent = rango
        ? (rango[0] === rango[1] ? "Solo " + rango[0] : rango[0] + "–" + rango[1])
        : "Arrastrá sobre las barras para elegir años";
    }
    function indice(ev) {
      var r = svg.getBoundingClientRect();
      var x = ((ev.clientX - r.left) / r.width) * W;
      return Math.max(0, Math.min(n - 1, Math.floor(x / (bw + gap))));
    }
    var desde = null;
    svg.addEventListener("pointerdown", function (ev) {
      desde = indice(ev); svg.setPointerCapture(ev.pointerId);
      rango = [barras[desde].anio, barras[desde].anio]; pintar();
    });
    svg.addEventListener("pointermove", function (ev) {
      if (desde === null) return;
      var i = indice(ev), a = Math.min(desde, i), b = Math.max(desde, i);
      rango = [barras[a].anio, barras[b].anio]; pintar();
    });
    svg.addEventListener("pointerup", function () {
      if (desde === null) return;
      desde = null; opts.alCambiar(rango);
    });
    todo.addEventListener("click", function () { rango = null; pintar(); opts.alCambiar(null); });
    svg.setAttribute("aria-label", "Años del hecho más reciente de cada ficha");
    pintar();
    if (opts.sinFecha && opts.sinFecha.total) {
      cont.appendChild(KR.el("p", "kr-nota", opts.sinFecha.total + " fichas sin fecha" + (rango ? " quedan fuera al elegir años." : ".")));
    }
    return cont;
  };

  // Popover anclado a un botón. Crece desde la esquina del botón (transform-origin).
  KR.popover = function (boton, contenido, opts) {
    opts = opts || {};
    var pop = KR.el("div", "kr-popover" + (opts.clase ? " " + opts.clase : ""));
    pop.setAttribute("role", "dialog");
    pop.hidden = true;
    pop.appendChild(contenido);
    document.body.appendChild(pop);
    function colocar() {
      var r = boton.getBoundingClientRect();
      var ancho = pop.offsetWidth || 300;
      var izq = opts.alinear === "izquierda" ? r.left : r.right - ancho;
      izq = Math.max(8, Math.min(window.innerWidth - ancho - 8, izq));
      var arriba = opts.arriba;
      pop.style.left = izq + "px";
      if (arriba) { pop.style.top = "auto"; pop.style.bottom = (window.innerHeight - r.top + 6) + "px"; }
      else { pop.style.bottom = "auto"; pop.style.top = (r.bottom + 6) + "px"; }
      pop.style.transformOrigin = (arriba ? "bottom " : "top ") + (opts.alinear === "izquierda" ? "left" : "right");
    }
    function abrir() { pop.hidden = false; colocar(); boton.setAttribute("aria-expanded", "true"); if (opts.alAbrir) opts.alAbrir(); }
    function cerrar() { if (pop.hidden) return; pop.hidden = true; boton.setAttribute("aria-expanded", "false"); }
    boton.setAttribute("aria-expanded", "false");
    boton.addEventListener("click", function () { if (pop.hidden) abrir(); else cerrar(); });
    function fuera(ev) { if (!pop.hidden && !pop.contains(ev.target) && !boton.contains(ev.target)) cerrar(); }
    function esc(ev) { if (ev.key === "Escape" && !pop.hidden) { cerrar(); boton.focus(); } }
    document.addEventListener("pointerdown", fuera);
    document.addEventListener("keydown", esc);
    return {
      cerrar: cerrar, abrir: abrir, el: pop,
      destruir: function () { document.removeEventListener("pointerdown", fuera); document.removeEventListener("keydown", esc); pop.remove(); }
    };
  };

  KR.botonCompartir = function (obtener) {
    var btn = KR.el("button", "kr-btn", "Compartir vista");
    btn.type = "button";
    var cuerpo = KR.el("div", "kr-compartir");
    cuerpo.appendChild(KR.el("p", "kr-compartir-titulo", "Enlace a esta vista"));
    cuerpo.appendChild(KR.el("p", "kr-nota", "Lleva los filtros, la vista y el encuadre. Quien lo abra ve lo mismo que vos."));
    var input = KR.el("input", "kr-compartir-url"); input.readOnly = true;
    var lab = KR.el("label", "kr-check");
    var cb = KR.el("input"); cb.type = "checkbox";
    var txt = KR.el("span");
    lab.appendChild(cb); lab.appendChild(txt);
    var copiar = KR.el("button", "kr-btn kr-btn-primario", "Copiar enlace"); copiar.type = "button";
    cuerpo.appendChild(input); cuerpo.appendChild(lab); cuerpo.appendChild(copiar);
    function actualizar() {
      var e = obtener();
      cb.disabled = !e.ficha;
      txt.textContent = e.ficha
        ? "Incluir la ficha abierta (" + e.ficha.nombre + ")" + (e.ficha.tipo === "persona" ? " — el enlace llevará el nombre de una persona" : "")
        : "No hay una ficha abierta";
      if (!e.ficha) cb.checked = false;
      var extra = e.extra || {};
      if (cb.checked && e.ficha) extra.f = e.ficha.id;
      input.value = location.origin + location.pathname + location.search + "#" + KR.hash.construir(e.filtros, extra);
    }
    cb.addEventListener("change", actualizar);
    var pop = KR.popover(btn, cuerpo, { alAbrir: function () { cb.checked = false; actualizar(); input.select(); } });
    copiar.addEventListener("click", function () {
      navigator.clipboard.writeText(input.value).then(function () {
        copiar.textContent = "Copiado ✓";
        setTimeout(function () { copiar.textContent = "Copiar enlace"; }, 1600);
      }, function () { input.select(); copiar.textContent = "Seleccionado: copiá con ⌘C"; });
    });
    return { el: btn, destruir: pop.destruir };
  };

  // Línea de tiempo de la ficha, al estilo de las líneas de tiempo de Aleph: un punto por hecho,
  // apilados por año, coloreados por tipo de hecho. Tocar un punto lleva al hecho en la lista.
  KR.lineaTiempo = function (n, alTocar) {
    var hechos = (n.hechos || []).map(function (h, i) {
      var m = /^(\d{4})/.exec(h.fecha || ""); return { h: h, i: i, anio: m ? +m[1] : null };
    });
    var fechados = hechos.filter(function (x) { return x.anio; });
    var cont = KR.el("div", "kr-tiempo");
    if (!fechados.length) { cont.appendChild(KR.el("p", "kr-nota", "Ningún hecho de esta ficha trae fecha.")); return cont; }
    var a0 = Math.min.apply(null, fechados.map(function (x) { return x.anio; }));
    var a1 = Math.max.apply(null, fechados.map(function (x) { return x.anio; }));
    if (a1 - a0 < 6) a0 = a1 - 6;
    var W = 300, R = 3.4, base = 44, porAnio = {};
    var maxPila = 1;
    fechados.forEach(function (x) { porAnio[x.anio] = (porAnio[x.anio] || 0) + 1; maxPila = Math.max(maxPila, porAnio[x.anio]); });
    var paso = Math.min(R * 2 + 1, (base - 6) / maxPila);
    var svg = KR.svg("svg", { viewBox: "0 0 " + W + " " + (base + 16), "class": "kr-tiempo-svg" });
    function xDe(a) { return 8 + ((a - a0) / Math.max(1, a1 - a0)) * (W - 16); }
    svg.appendChild(KR.svg("line", { x1: 4, x2: W - 4, y1: base + 1, y2: base + 1, "class": "kr-tiempo-eje" }));
    for (var a = a0; a <= a1; a++) {
      if ((a - a0) % Math.ceil((a1 - a0 + 1) / 7) !== 0 && a !== a1) continue;
      var t = KR.svg("text", { x: xDe(a), y: base + 13, "text-anchor": "middle", "class": "kr-tiempo-anio" });
      t.textContent = a; svg.appendChild(t);
    }
    var pila = {};
    fechados.forEach(function (x) {
      var k = pila[x.anio] = (pila[x.anio] || 0) + 1;
      var c = KR.svg("circle", {
        cx: xDe(x.anio), cy: base - 3 - (k - 1) * paso, r: Math.min(R, paso / 2),
        fill: "var(--" + (KR.HECHO_VAR[x.h.tipo] || "text-muted") + ")", "class": "kr-tiempo-punto", tabindex: "0"
      });
      var tt = KR.svg("title", {});
      tt.textContent = x.anio + " · " + (KR.HECHO_LABEL[x.h.tipo] || x.h.tipo) + " · " + (x.h.hecho || "").slice(0, 120);
      c.appendChild(tt);
      function ir() { if (alTocar) alTocar(x.i); }
      c.addEventListener("click", ir);
      c.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); ir(); } });
      svg.appendChild(c);
    });
    cont.appendChild(svg);
    var ley = KR.el("div", "kr-tiempo-ley");
    Object.keys(KR.HECHO_LABEL).forEach(function (tipo) {
      var cuantos = fechados.filter(function (x) { return x.h.tipo === tipo; }).length;
      if (!cuantos) return;
      var s = KR.el("span");
      var d = KR.el("i"); d.style.background = "var(--" + KR.HECHO_VAR[tipo] + ")";
      s.appendChild(d); s.appendChild(document.createTextNode(KR.HECHO_LABEL[tipo] + " " + cuantos));
      ley.appendChild(s);
    });
    var sinF = hechos.length - fechados.length;
    if (sinF) ley.appendChild(KR.el("span", "", sinF + " sin fecha"));
    cont.appendChild(ley);
    return cont;
  };

  KR.insigniaEvidencia = function (ev) {
    var txt = ev.nivel === "compartida" ? "Fuente compartida" : ev.nivel === "registro" ? "Registro del ensayo" : "Sin fuente propia";
    return KR.el("span", "kr-ev kr-ev-" + ev.nivel, txt);
  };

  KR.detalleEvidencia = function (ev) {
    var box = KR.el("div", "kr-ev-detalle");
    box.appendChild(KR.el("p", "kr-ev-etiqueta", ev.etiqueta));
    if (!ev.items.length && ev.nivel === "sin-fuente") {
      box.appendChild(KR.el("p", "kr-nota", "El pipeline registró el vínculo pero no la URL de donde salió. No se completa por inferencia."));
    }
    ev.items.slice(0, 3).forEach(function (it) {
      var p = KR.el("p", "kr-ev-item");
      p.appendChild(document.createTextNode((it.texto || "").slice(0, 160) + (it.texto && it.texto.length > 160 ? "… " : " ")));
      if (KR.esUrlSegura(it.url)) {
        var a = KR.el("a", "", KR.fuenteNombre(it.url) + (it.fecha ? " · " + it.fecha : "") + " ↗");
        a.href = it.url; a.target = "_blank"; a.rel = "noopener noreferrer";
        p.appendChild(a);
      }
      box.appendChild(p);
    });
    if (ev.items.length > 3) box.appendChild(KR.el("p", "kr-nota", "+" + (ev.items.length - 3) + " fuentes más"));
    return box;
  };

  // La ficha. Las variantes deciden dónde se muestra (panel, columna, hoja); el contenido es el mismo.
  KR.ficha = function (n, opts) {
    opts = opts || {};
    var g = KR.datos.grafo;
    var raiz = KR.el("article", "kr-ficha");
    var cab = KR.el("header", "kr-ficha-cab");
    var tag = KR.el("span", "kr-ficha-tipo");
    tag.appendChild(KR.formaSVG(n.tipo, 9));
    tag.appendChild(document.createTextNode(KR.TIPO_LABEL[n.tipo]));
    cab.appendChild(tag);
    cab.appendChild(KR.el("h2", "kr-ficha-nombre", n.nombre));
    var sub = [n.subtitulo, n.ciudad].filter(Boolean).join(" · ");
    if (sub) cab.appendChild(KR.el("p", "kr-ficha-sub", sub));
    raiz.appendChild(cab);

    if (n._sintetico) {
      raiz.appendChild(KR.el("p", "kr-aviso", "Nodo sintético de la prueba de carga. No representa a nadie: no tiene nombre, hechos ni fuentes."));
      return raiz;
    }

    var acciones = KR.el("div", "kr-ficha-acciones");
    var sl = KR.el("button", "kr-btn"); sl.type = "button";
    function pintarSL() {
      var on = KR.shortlist.tiene(n.id);
      sl.textContent = on ? "★ En tu shortlist" : "☆ Añadir a shortlist";
      sl.setAttribute("aria-pressed", String(on));
    }
    sl.addEventListener("click", function () { KR.shortlist.alternar(n.id); });
    var quitarSL = KR.shortlist.escuchar(pintarSL);
    pintarSL();
    acciones.appendChild(sl);
    (opts.acciones || []).forEach(function (b) { acciones.appendChild(b); });
    raiz.appendChild(acciones);

    var hechosLista;
    function irAHecho(i) {
      var li = hechosLista && hechosLista.children[i];
      if (!li) return;
      li.scrollIntoView({ block: "center", behavior: KR.reducirMovimiento() ? "auto" : "smooth" });
      li.classList.remove("kr-destello"); void li.offsetWidth; li.classList.add("kr-destello");
    }
    raiz.appendChild(KR.el("h3", "kr-ficha-sec", "Evidencia en el tiempo"));
    raiz.appendChild(KR.lineaTiempo(n, irAHecho));

    var rel = g.adj[n.id] || [];
    raiz.appendChild(KR.el("h3", "kr-ficha-sec", "Conexiones (" + rel.length + ")"));
    if (!rel.length) raiz.appendChild(KR.el("p", "kr-nota", "Sin conexiones registradas."));
    var porTipo = {};
    rel.forEach(function (a) { var t = g.byId[a.otro].tipo; (porTipo[t] = porTipo[t] || []).push(a); });
    KR.TIPOS.forEach(function (t) {
      var grupo = porTipo[t];
      if (!grupo) return;
      var bloque = KR.el("div", "kr-con-grupo");
      bloque.appendChild(KR.el("p", "kr-con-grupo-tit", KR.TIPO_PLURAL[t] + " · " + grupo.length));
      var ul = KR.el("ul", "kr-con-lista");
      var LIMITE = 6;
      grupo.forEach(function (a, i) {
        var otro = g.byId[a.otro];
        var ev = KR.evidencia(a.v);
        var li = KR.el("li", "kr-con");
        if (i >= LIMITE) li.hidden = true;
        var fila = KR.el("div", "kr-con-fila");
        var nom = KR.el("button", "kr-con-nombre", otro.nombre); nom.type = "button";
        nom.addEventListener("click", function () { if (opts.alNavegar) opts.alNavegar(otro.id); });
        if (opts.alResaltar) {
          nom.addEventListener("mouseenter", function () { opts.alResaltar(otro.id, a.v); });
          nom.addEventListener("mouseleave", function () { opts.alResaltar(null); });
        }
        fila.appendChild(nom);
        fila.appendChild(KR.el("span", "kr-con-tipo", a.v.tipo));
        var exp = KR.el("button", "kr-con-ev"); exp.type = "button";
        exp.appendChild(KR.insigniaEvidencia(ev));
        exp.setAttribute("aria-expanded", "false");
        fila.appendChild(exp);
        li.appendChild(fila);
        var det = null;
        exp.addEventListener("click", function () {
          if (!det) { det = KR.detalleEvidencia(ev); li.appendChild(det); }
          else det.hidden = !det.hidden;
          exp.setAttribute("aria-expanded", String(!det.hidden));
        });
        ul.appendChild(li);
      });
      bloque.appendChild(ul);
      if (grupo.length > LIMITE) {
        var ver = KR.el("button", "kr-btn kr-btn-chico", "Ver las " + grupo.length); ver.type = "button";
        ver.addEventListener("click", function () {
          Array.prototype.forEach.call(ul.children, function (li) { li.hidden = false; });
          ver.remove();
        });
        bloque.appendChild(ver);
      }
      raiz.appendChild(bloque);
    });

    raiz.appendChild(KR.el("h3", "kr-ficha-sec", "Hechos con fuente (" + (n.hechos || []).length + ")"));
    hechosLista = KR.el("ul", "kr-hechos");
    (n.hechos || []).forEach(function (h) {
      var li = KR.el("li", "kr-hecho");
      li.appendChild(KR.el("span", "kr-hecho-tag", KR.HECHO_LABEL[h.tipo] || h.tipo));
      li.appendChild(document.createTextNode(" " + (h.hecho || "")));
      var pie = KR.el("span", "kr-hecho-pie", (h.fecha || "sin fecha") + " · " + (h.confianza || "pendiente"));
      if (KR.esUrlSegura(h.fuente_url)) {
        var a = KR.el("a", "", KR.fuenteNombre(h.fuente_url) + " ↗");
        a.href = h.fuente_url; a.target = "_blank"; a.rel = "noopener noreferrer";
        pie.appendChild(document.createTextNode(" · ")); pie.appendChild(a);
      }
      li.appendChild(pie);
      hechosLista.appendChild(li);
    });
    raiz.appendChild(hechosLista);
    raiz.appendChild(KR.el("p", "kr-nota", "Confianza: pendiente de revisión humana. No es una evaluación de desempeño profesional."));
    raiz._destruir = quitarSL;
    return raiz;
  };

  // Panel "Qué comparten" (Interlocks de Oligrapher) para la shortlist.
  KR.panelEnComun = function (opts) {
    var cont = KR.el("div", "kr-comun");
    var ids = KR.shortlist.lista();
    if (ids.length < 2) {
      cont.appendChild(KR.el("p", "kr-nota", ids.length
        ? "Tenés 1 ficha en la shortlist. Con 2 o más, acá aparece lo que las conecta."
        : "Añadí 2 o más fichas a tu shortlist (☆ en cada ficha) para ver qué tienen en común."));
      if (opts.ejemplo) {
        var ej = KR.el("button", "kr-btn kr-btn-chico", "Probar con Carlos Rojas y Mauricio Burotto"); ej.type = "button";
        ej.addEventListener("click", function () {
          ["carlos-rojas", "mauricio-burotto"].forEach(function (id) { if (!KR.shortlist.tiene(id)) KR.shortlist.alternar(id); });
        });
        cont.appendChild(ej);
      }
      return cont;
    }
    var g = KR.datos.grafo, r = KR.enComun(ids);
    var chips = KR.el("div", "kr-comun-chips");
    ids.forEach(function (id) {
      var c = KR.el("button", "kr-chip-sl"); c.type = "button";
      c.appendChild(KR.formaSVG(g.byId[id].tipo, 8));
      c.appendChild(document.createTextNode(g.byId[id].nombre));
      var x = KR.el("span", "kr-chip-x", "×"); x.setAttribute("aria-label", "Quitar de la shortlist");
      c.appendChild(x);
      c.addEventListener("click", function (ev) {
        if (ev.target === x) KR.shortlist.alternar(id); else if (opts.alNavegar) opts.alNavegar(id);
      });
      chips.appendChild(c);
    });
    cont.appendChild(chips);
    var cuenta = {};
    r.compartidos.forEach(function (c) { cuenta[c.n.tipo] = (cuenta[c.n.tipo] || 0) + 1; });
    var partes = KR.TIPOS.filter(function (t) { return cuenta[t]; }).map(function (t) {
      return cuenta[t] + " " + (cuenta[t] === 1 ? KR.TIPO_LABEL[t] : KR.TIPO_PLURAL[t]).toLowerCase();
    });
    if (r.directos.length) partes.unshift(r.directos.length + " vínculo" + (r.directos.length === 1 ? "" : "s") + " directo" + (r.directos.length === 1 ? "" : "s"));
    cont.appendChild(KR.el("p", "kr-comun-resumen", partes.length ? "Comparten " + partes.join(", ") + "." : "No comparten ninguna conexión registrada."));
    if (opts.alMostrar && (r.compartidos.length || r.directos.length)) {
      var ver = KR.el("button", "kr-btn kr-btn-chico", "Resaltar en el mapa"); ver.type = "button";
      ver.addEventListener("click", function () { opts.alMostrar(ids, r); });
      cont.appendChild(ver);
    }
    var ul = KR.el("ul", "kr-comun-lista");
    r.compartidos.slice(0, 8).forEach(function (c) {
      var li = KR.el("li");
      var b = KR.el("button", "kr-con-nombre"); b.type = "button";
      b.appendChild(KR.formaSVG(c.n.tipo, 8));
      b.appendChild(document.createTextNode(" " + c.n.nombre));
      b.addEventListener("click", function () { if (opts.alNavegar) opts.alNavegar(c.n.id); });
      li.appendChild(b);
      li.appendChild(KR.el("span", "kr-nota", "conecta a " + c.quienes.map(function (id) { return g.byId[id].nombre.split(" ")[0]; }).join(", ")));
      ul.appendChild(li);
    });
    if (r.compartidos.length > 8) ul.appendChild(KR.el("li", "kr-nota", "+" + (r.compartidos.length - 8) + " más"));
    cont.appendChild(ul);
    return cont;
  };

  // ------------------------------------------------------------------ lienzo con cámara
  // Canvas 2D sin dependencias. La cámara es { cx, cy, k }: el punto del mundo en el centro de la
  // pantalla y la escala. Rueda y arrastre 1:1 (cortan cualquier animación); botones y saltos
  // animados e interrumpibles; con el teclado o movimiento reducido, inmediatos.
  KR.lienzo = function (canvas, opts) {
    var ctx = canvas.getContext("2d");
    // `rot` gira la cámara (radianes). Con 0 todo es idéntico a antes; el mapa por ciudad lo usa
    // para pasar de Chile acostado a una ciudad con el norte arriba.
    var cam = { cx: 0, cy: 0, k: 1, rot: 0 }, w = 0, h = 0, dpr = 1;
    var pendiente = false, anim = null, vivo = true;
    var minK = opts.minK || 0.05, maxK = opts.maxK || 12;
    var api = { cam: cam, ctx: ctx };

    function tam() {
      var r = canvas.getBoundingClientRect();
      dpr = Math.min(2, window.devicePixelRatio || 1);
      w = r.width; h = r.height;
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      api.w = w; api.h = h;
      api.dibujar();
    }
    api.aPantalla = function (x, y) {
      var dx = (x - cam.cx) * cam.k, dy = (y - cam.cy) * cam.k;
      if (!cam.rot) return [dx + w / 2, dy + h / 2];
      var c = Math.cos(cam.rot), s = Math.sin(cam.rot);
      return [dx * c - dy * s + w / 2, dx * s + dy * c + h / 2];
    };
    // Del punto de pantalla al del mundo, con una cámara dada (la actual si no se pasa).
    function aMundoCon(camara, sx, sy) {
      var dx = sx - w / 2, dy = sy - h / 2, r = camara.rot || 0;
      var c = Math.cos(r), s = Math.sin(r);
      return [(dx * c + dy * s) / camara.k + camara.cx, (-dx * s + dy * c) / camara.k + camara.cy];
    }
    api.aMundo = function (sx, sy) { return aMundoCon(cam, sx, sy); };
    // Centro de cámara que deja el punto del mundo `m` bajo el punto de pantalla `p` con escala k.
    function centrarEn(m, p, k, rot) {
      var dx = p[0] - w / 2, dy = p[1] - h / 2, c = Math.cos(rot || 0), s = Math.sin(rot || 0);
      return { cx: m[0] - (dx * c + dy * s) / k, cy: m[1] - (-dx * s + dy * c) / k };
    }
    api.dibujar = function () {
      if (pendiente || !vivo) return;
      pendiente = true;
      requestAnimationFrame(function () {
        pendiente = false;
        if (!vivo || !w) return;
        var t0 = performance.now();
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, w, h);
        opts.alDibujar(ctx, api);
        api.ms = performance.now() - t0;
        if (opts.alMedir) opts.alMedir(api.ms);
      });
    };
    api.cancelar = function () { if (anim) { cancelAnimationFrame(anim.raf); anim = null; } };
    api.animarA = function (meta, dur, inmediato, curva) {
      api.cancelar();
      meta.k = Math.max(minK, Math.min(maxK, meta.k));
      if (meta.rot === undefined) meta.rot = cam.rot;
      if (inmediato || KR.reducirMovimiento() || !dur) {
        cam.cx = meta.cx; cam.cy = meta.cy; cam.k = meta.k; cam.rot = meta.rot;
        api.dibujar(); if (opts.alCamara) opts.alCamara(true); return;
      }
      var desde = { cx: cam.cx, cy: cam.cy, k: cam.k, rot: cam.rot }, t0 = null, ease = curva || KR.easeOut;
      anim = { meta: meta };
      function paso(t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = ease(p);
        // La escala se interpola en logaritmo: un zoom de 1× a 8× se siente parejo, no de golpe al final.
        cam.k = Math.exp(Math.log(desde.k) + (Math.log(meta.k) - Math.log(desde.k)) * e);
        cam.cx = desde.cx + (meta.cx - desde.cx) * e;
        cam.cy = desde.cy + (meta.cy - desde.cy) * e;
        cam.rot = desde.rot + (meta.rot - desde.rot) * e;
        api.dibujar();
        if (opts.alCamara) opts.alCamara(p >= 1);
        if (p < 1) anim.raf = requestAnimationFrame(paso); else anim = null;
      }
      anim.raf = requestAnimationFrame(paso);
    };
    api.base = function () { return anim ? anim.meta : { cx: cam.cx, cy: cam.cy, k: cam.k, rot: cam.rot }; };
    api.encuadre = function (caja, pad, rot) {
      pad = pad === undefined ? 40 : pad;
      rot = rot === undefined ? cam.rot : rot;
      var bw = Math.max(1e-6, caja.x1 - caja.x0), bh = Math.max(1e-6, caja.y1 - caja.y0);
      // Girada 90°, el ancho del mundo ocupa el alto de la pantalla.
      var c = Math.abs(Math.cos(rot)), s = Math.abs(Math.sin(rot));
      var sw = bw * c + bh * s, sh = bw * s + bh * c;
      var k = Math.min((w - pad * 2) / sw, (h - pad * 2) / sh);
      return { cx: (caja.x0 + caja.x1) / 2, cy: (caja.y0 + caja.y1) / 2, k: Math.max(minK, Math.min(maxK, k)), rot: rot };
    };
    api.zoomEn = function (factor, sx, sy, dur, inmediato) {
      var b = api.base();
      var k = Math.max(minK, Math.min(maxK, b.k * factor));
      var m = aMundoCon(b, sx, sy), c = centrarEn(m, [sx, sy], k, b.rot);
      api.animarA({ cx: c.cx, cy: c.cy, k: k, rot: b.rot }, dur, inmediato);
    };

    // --- entrada: rueda, arrastre, pellizco, click, hover
    var punteros = {}, arrastre = null, pellizco = null;
    function pos(ev) { var r = canvas.getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top]; }
    function rueda(ev) {
      ev.preventDefault();
      var p = pos(ev), f = Math.exp(-ev.deltaY * (ev.ctrlKey ? 0.01 : 0.0022));
      api.cancelar();
      var k = Math.max(minK, Math.min(maxK, cam.k * f));
      var m = api.aMundo(p[0], p[1]), c = centrarEn(m, p, k, cam.rot);
      cam.k = k; cam.cx = c.cx; cam.cy = c.cy;
      api.dibujar(); if (opts.alCamara) opts.alCamara(false); programarAsentado();
    }
    var asentado = null;
    function programarAsentado() {
      clearTimeout(asentado);
      asentado = setTimeout(function () { if (opts.alCamara) opts.alCamara(true); }, 140);
    }
    function abajo(ev) {
      canvas.setPointerCapture(ev.pointerId);
      api.cancelar();
      punteros[ev.pointerId] = pos(ev);
      var ids = Object.keys(punteros);
      if (ids.length === 2) {
        var a = punteros[ids[0]], b = punteros[ids[1]];
        pellizco = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), k: cam.k };
        arrastre = null;
      } else {
        arrastre = { x: ev.clientX, y: ev.clientY, cx: cam.cx, cy: cam.cy, movio: false };
      }
    }
    function mover(ev) {
      var p = pos(ev);
      if (punteros[ev.pointerId]) punteros[ev.pointerId] = p;
      var ids = Object.keys(punteros);
      if (pellizco && ids.length === 2) {
        var a = punteros[ids[0]], b = punteros[ids[1]];
        var mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], m = api.aMundo(mid[0], mid[1]);
        cam.k = Math.max(minK, Math.min(maxK, pellizco.k * Math.hypot(a[0] - b[0], a[1] - b[1]) / pellizco.d));
        var cc = centrarEn(m, mid, cam.k, cam.rot); cam.cx = cc.cx; cam.cy = cc.cy;
        api.dibujar(); if (opts.alCamara) opts.alCamara(false);
        return;
      }
      if (arrastre) {
        var dx = ev.clientX - arrastre.x, dy = ev.clientY - arrastre.y;
        if (!arrastre.movio && Math.abs(dx) + Math.abs(dy) > 4) { arrastre.movio = true; canvas.classList.add("arrastrando"); }
        if (arrastre.movio) {
          var co = Math.cos(cam.rot), si = Math.sin(cam.rot);
          cam.cx = arrastre.cx - (dx * co + dy * si) / cam.k; cam.cy = arrastre.cy - (-dx * si + dy * co) / cam.k;
          api.dibujar(); if (opts.alCamara) opts.alCamara(false);
          return;
        }
      }
      if (!arrastre && opts.alMover) opts.alMover(p[0], p[1], ev);
    }
    function arriba(ev) {
      var fueClick = arrastre && !arrastre.movio && Object.keys(punteros).length === 1;
      delete punteros[ev.pointerId];
      if (Object.keys(punteros).length < 2) pellizco = null;
      if (arrastre && arrastre.movio && opts.alCamara) opts.alCamara(true);
      arrastre = null;
      canvas.classList.remove("arrastrando");
      if (fueClick && opts.alClick) { var p = pos(ev); opts.alClick(p[0], p[1], ev); }
    }
    function salir() { if (opts.alSalir) opts.alSalir(); }
    canvas.addEventListener("wheel", rueda, { passive: false });
    canvas.addEventListener("pointerdown", abajo);
    canvas.addEventListener("pointermove", mover);
    canvas.addEventListener("pointerup", arriba);
    canvas.addEventListener("pointercancel", arriba);
    canvas.addEventListener("pointerleave", salir);
    var ro = new ResizeObserver(tam);
    ro.observe(canvas);
    api.destruir = function () {
      vivo = false; api.cancelar(); ro.disconnect(); clearTimeout(asentado);
      canvas.removeEventListener("wheel", rueda);
    };
    return api;
  };

  // Botones + − ⟲ comunes. `detail === 0` es un click que vino del teclado: sin animación.
  KR.botonesZoom = function (lz, alRestablecer) {
    var cont = KR.el("div", "kr-zoom");
    [["+", "Acercar", 1.6], ["−", "Alejar", 1 / 1.6], ["⟲", "Encuadrar todo", 0]].forEach(function (d) {
      var b = KR.el("button", "kr-zoom-btn", d[0]); b.type = "button";
      b.setAttribute("aria-label", d[1]); b.title = d[1];
      b.addEventListener("click", function (ev) {
        if (d[2]) lz.zoomEn(d[2], lz.w / 2, lz.h / 2, 240, ev.detail === 0);
        else alRestablecer(ev.detail === 0);
      });
      cont.appendChild(b);
    });
    return cont;
  };

  // Etiquetas por nivel de detalle (idea del demo de sigma.js: se dibuja lo que cabe a ESTE zoom).
  // `candidatos` ya viene ordenado por prioridad. Devuelve las que entran sin pisarse.
  KR.colocarEtiquetas = function (ctx, candidatos, w, h, maxEtiquetas) {
    var CELDA = 64, grilla = {}, puestas = [];
    for (var i = 0; i < candidatos.length && puestas.length < maxEtiquetas; i++) {
      var c = candidatos[i];
      if (c.sx < -50 || c.sy < -20 || c.sx > w + 50 || c.sy > h + 20) continue;
      // El ancho se mide una vez por nodo y queda guardado: measureText en cada cuadro era la
      // mitad del costo de dibujar.
      var tw = c.ancho || (c.ancho = ctx.measureText(c.texto).width);
      if (c.n) c.n._tw = tw;
      var x0 = c.sx + c.r + 4, y0 = c.sy - 7, x1 = x0 + tw, y1 = c.sy + 7;
      var libre = true;
      var gx0 = Math.floor(x0 / CELDA), gx1 = Math.floor(x1 / CELDA), gy0 = Math.floor(y0 / CELDA), gy1 = Math.floor(y1 / CELDA);
      for (var gx = gx0; gx <= gx1 && libre; gx++) {
        for (var gy = gy0; gy <= gy1 && libre; gy++) {
          var lista = grilla[gx + ":" + gy];
          if (!lista) continue;
          for (var j = 0; j < lista.length; j++) {
            var o = lista[j];
            if (x0 < o[2] && x1 > o[0] && y0 < o[3] && y1 > o[1]) { libre = false; break; }
          }
        }
      }
      if (!libre) continue;
      var rect = [x0 - 2, y0 - 1, x1 + 2, y1 + 1];
      for (gx = gx0; gx <= gx1; gx++) for (gy = gy0; gy <= gy1; gy++) (grilla[gx + ":" + gy] = grilla[gx + ":" + gy] || []).push(rect);
      puestas.push({ c: c, x: x0, y: c.sy });
    }
    return puestas;
  };

  // Agrega la forma al trazo en curso sin abrir uno nuevo: así cientos de nodos del mismo tipo se
  // rellenan con UNA sola llamada a fill(), que es lo que permite dibujar miles por cuadro.
  KR.trazarForma = function (ctx, tipo, x, y, r) {
    if (tipo === "persona") { ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, Math.PI * 2); }
    else if (tipo === "institucion") ctx.rect(x - r * 0.9, y - r * 0.9, r * 1.8, r * 1.8);
    else { ctx.moveTo(x, y - r * 1.1); ctx.lineTo(x + r, y + r * 0.8); ctx.lineTo(x - r, y + r * 0.8); ctx.closePath(); }
  };
  KR.dibujarForma = function (ctx, tipo, x, y, r) { ctx.beginPath(); KR.trazarForma(ctx, tipo, x, y, r); };
  KR.etiquetaCorta = function (n) { return n.tipo === "ensayo_clinico" ? n.nombre.split(" (")[0] : n.nombre; };
  KR.FUENTE_CANVAS = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

  // Retardo al soltar el resaltado (como en web/index.html): pasar de un nodo al vecino no debe
  // reencender el mapa entero un instante.
  KR.hoverEstable = function (alCambiar, ms) {
    var actual = null, timer = null;
    return {
      poner: function (id) {
        clearTimeout(timer);
        if (id === actual) return;
        if (id === null) { timer = setTimeout(function () { actual = null; alCambiar(null); }, ms || 90); return; }
        actual = id; alCambiar(id);
      },
      valor: function () { return actual; },
      limpiar: function () { clearTimeout(timer); actual = null; }
    };
  };
})();
