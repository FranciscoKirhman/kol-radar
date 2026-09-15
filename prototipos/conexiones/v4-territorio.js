/* Prototipo 4 — «Territorio».
 * Eje: ESPACIO. El mapa de Chile del sitio pasa a ser la vista principal: cada ciudad es un
 * punto con sus fichas y las líneas suman las conexiones entre ciudades (ensayos con sedes en
 * ambas, coautorías, afiliaciones). Al alejarse, las ciudades cercanas se funden y sus líneas se
 * suman, como el clustering por zoom de flowmap.gl. Horizontal por defecto en pantallas anchas:
 * Chile vertical deja dos tercios del monitor vacíos. Escala porque las marcas son lugares, no
 * fichas: 10 veces más fichas agrandan los puntos, no los multiplican. */
(function () {
  "use strict";
  var KR = window.KR;

  var COMUNAS_RM = ["providencia", "recoleta", "las condes", "independencia", "ñuñoa", "nunoa", "vitacura", "maipú", "maipu",
    "puente alto", "la florida", "macul", "huechuraba", "quilicura", "lo barnechea", "la reina", "san miguel", "peñalolén",
    "penalolen", "estación central", "estacion central"];
  function ciudadDe(n) {
    var c = (n.ciudad || "").split(" (")[0].trim(), l = c.toLowerCase();
    if (COMUNAS_RM.indexOf(l) !== -1) return "Santiago";
    if (l === "port montt") return "Puerto Montt";
    if (l === "reñaca" || l === "renaca") return "Viña del Mar";
    return c;
  }

  function montar(stage) {
    var el = KR.el, g = KR.datos.grafo, geo = KR.datos.geo, K = geo.proyeccion.k_lon;
    var h0 = KR.hash.leer();
    var filtros = KR.hash.aFiltros(h0);
    var orientacion = h0.o === "v" ? "v" : h0.o === "h" ? "h" : null;
    var C = KR.colores(), limpiezas = [];
    var visibles, lugares, listaLugares, sinLugar, flujos, clusters = [], clusterDe = {};
    var sel = null, lugarSel = null, flujoSel = null, profundidad = h0.d === "2" ? 2 : 1;
    var hover = null, verTodasAreas = false, vista = "resumen", pila = [];
    var poligonos = geo.contorno.map(function (d) {
      var pts = [], re = /[ML]\s*(-?[\d.]+)[ ,](-?[\d.]+)/g, m;
      while ((m = re.exec(d))) pts.push([+m[1], +m[2]]);
      return pts;
    });

    // ---------------------------------------------------------------- estructura
    var raiz = el("div", "variante v4");
    var top = el("header", "kr-top");
    var marca = el("div", "kr-marca");
    marca.appendChild(el("span", "kr-marca-nombre", "KOL Radar"));
    marca.appendChild(el("span", "kr-marca-tag", "oncología · Chile"));
    top.appendChild(marca);
    var bw = el("div", "kr-buscar v3-buscar");
    var input = el("input"); input.type = "search"; input.placeholder = "Buscar persona, institución o ensayo…";
    input.setAttribute("aria-label", "Buscar");
    bw.appendChild(input); top.appendChild(bw);
    top.appendChild(el("span", "kr-top-sep"));
    var compartir = KR.botonCompartir(function () {
      return { filtros: filtros, ficha: sel ? g.byId[sel] : null, extra: { o: orientacion, d: profundidad === 2 ? "2" : null } };
    });
    limpiezas.push(compartir.destruir);
    top.appendChild(compartir.el);
    raiz.appendChild(top);
    raiz.appendChild(KR.lineaBeta());
    var main = el("div", "v4-main");
    var mapa = el("section", "v4-mapa");
    var canvas = el("canvas", "kr-canvas");
    canvas.setAttribute("aria-label", "Mapa de Chile con las fichas por ciudad y las conexiones entre ciudades. El panel de la derecha lista los lugares.");
    mapa.appendChild(canvas);
    var tooltip = el("div", "kr-tooltip"); tooltip.hidden = true; mapa.appendChild(tooltip);
    var barraFoco = el("div", "v1-foco"); barraFoco.hidden = true; mapa.appendChild(barraFoco);
    var orient = el("div", "kr-seg v4-orient"); mapa.appendChild(orient);
    var leyenda = el("div", "kr-leyenda v1-leyenda v4-leyenda"); mapa.appendChild(leyenda);
    var panel = el("aside", "v4-panel");
    var panelCab = el("div", "v4-panel-cab");
    var panelCuerpo = el("div", "v4-panel-cuerpo");
    panel.appendChild(panelCab); panel.appendChild(panelCuerpo);
    main.appendChild(mapa); main.appendChild(panel);
    raiz.appendChild(main);
    stage.appendChild(raiz);

    // ---------------------------------------------------------------- geografía
    function mundo(x, y) { return orientacion === "h" ? [y, -x] : [x, y]; }
    function coordCiudad(nombre) {
      var c = geo.ciudades[nombre];
      return c ? mundo(c.lon * K, -c.lat) : null;
    }
    var cajaPais = null;
    function calcularCaja() {
      cajaPais = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
      poligonos.forEach(function (pts) {
        pts.forEach(function (p) {
          var w = mundo(p[0], p[1]);
          cajaPais.x0 = Math.min(cajaPais.x0, w[0]); cajaPais.x1 = Math.max(cajaPais.x1, w[0]);
          cajaPais.y0 = Math.min(cajaPais.y0, w[1]); cajaPais.y1 = Math.max(cajaPais.y1, w[1]);
        });
      });
    }

    // ---------------------------------------------------------------- lugares y flujos
    function ciudadesDe(n) {
      if (n.tipo === "ensayo_clinico") {
        var cs = [];
        g.adj[n.id].forEach(function (a) {
          var o = g.byId[a.otro];
          if (o.tipo !== "institucion") return;
          var c = ciudadDe(o);
          if (geo.ciudades[c] && cs.indexOf(c) === -1) cs.push(c);
        });
        if (cs.length) return cs;
      }
      var propia = ciudadDe(n);
      return geo.ciudades[propia] ? [propia] : [];
    }
    function recalcular() {
      visibles = {};
      g.nodos.forEach(function (n) { if (KR.pasa(n, filtros)) visibles[n.id] = true; });
      lugares = {}; sinLugar = [];
      g.nodos.forEach(function (n) {
        if (!visibles[n.id]) return;
        var cs = ciudadesDe(n);
        n._ciudades = cs;
        if (!cs.length) { sinLugar.push(n); return; }
        cs.forEach(function (c) {
          var L = lugares[c];
          if (!L) { var p = coordCiudad(c); L = lugares[c] = { nombre: c, x: p[0], y: p[1], entidades: [], cuenta: { persona: 0, institucion: 0, ensayo_clinico: 0 } }; }
          L.entidades.push(n); L.cuenta[n.tipo]++;
        });
      });
      listaLugares = Object.keys(lugares).map(function (k) { return lugares[k]; }).sort(function (a, b) { return b.entidades.length - a.entidades.length; });
      flujos = {};
      function agregar(c1, c2, item) {
        if (c1 === c2) return;
        var k = c1 < c2 ? c1 + "|" + c2 : c2 + "|" + c1;
        (flujos[k] = flujos[k] || { a: c1 < c2 ? c1 : c2, b: c1 < c2 ? c2 : c1, items: [] }).items.push(item);
      }
      // Un ensayo con sedes en dos ciudades las conecta a través de sus dos instituciones.
      g.nodos.forEach(function (n) {
        if (n.tipo !== "ensayo_clinico" || !visibles[n.id]) return;
        var porCiudad = {};
        g.adj[n.id].forEach(function (a) {
          var o = g.byId[a.otro];
          if (o.tipo !== "institucion" || !visibles[o.id]) return;
          var c = ciudadDe(o);
          if (geo.ciudades[c] && !porCiudad[c]) porCiudad[c] = { inst: o, v: a.v };
        });
        var cs = Object.keys(porCiudad);
        for (var i = 0; i < cs.length; i++) for (var j = i + 1; j < cs.length; j++) {
          agregar(cs[i], cs[j], { tipo: "ensayo con sedes en ambas", via: n, a: porCiudad[cs[i]].inst, b: porCiudad[cs[j]].inst, va: porCiudad[cs[i]].v, vb: porCiudad[cs[j]].v });
        }
      });
      g.vinculos.forEach(function (v) {
        var a = g.byId[v.origen], b = g.byId[v.destino];
        if (!visibles[a.id] || !visibles[b.id] || a.tipo === "ensayo_clinico" || b.tipo === "ensayo_clinico") return;
        var ca = ciudadDe(a), cb = ciudadDe(b);
        if (!geo.ciudades[ca] || !geo.ciudades[cb]) return;
        agregar(ca, cb, { tipo: v.tipo, v: v, a: a, b: b });
      });
      flujos = Object.keys(flujos).map(function (k) { return flujos[k]; });
    }

    function radioLugar(total) { return Math.max(4, Math.min(46, 3 + Math.sqrt(total) * 2.3)); }

    // Agrupamiento por zoom (idea de flowmap.gl): de mayor a menor, cada ciudad se suma al primer
    // grupo cuyo círculo la tapa en pantalla. Se recalcula en cada cuadro: con 37 ciudades es nada.
    function agrupar(lz) {
      clusters = []; clusterDe = {};
      listaLugares.forEach(function (L) {
        var s = lz.aPantalla(L.x, L.y), r = radioLugar(L.entidades.length), dest = null;
        for (var i = 0; i < clusters.length; i++) {
          var c = clusters[i];
          if (Math.hypot(c.sx - s[0], c.sy - s[1]) < c.r + r * 0.6 + 4) { dest = c; break; }
        }
        if (!dest) {
          dest = { id: L.nombre, lider: L, x: L.x, y: L.y, sx: s[0], sy: s[1], miembros: [], total: 0, cuenta: { persona: 0, institucion: 0, ensayo_clinico: 0 }, ids: {} };
          clusters.push(dest);
        }
        dest.miembros.push(L);
        L.entidades.forEach(function (n) { if (!dest.ids[n.id]) { dest.ids[n.id] = true; dest.total++; dest.cuenta[n.tipo]++; } });
        dest.r = radioLugar(dest.total);
        clusterDe[L.nombre] = dest;
      });
    }
    function nombreCluster(c) { return c.lider.nombre + (c.miembros.length > 1 ? " +" + (c.miembros.length - 1) : ""); }

    function focoActual() {
      var id = hover && hover.tipo === "ficha" ? hover.id : sel;
      if (!id || !visibles[id]) return null;
      return KR.vecindario(g, id, profundidad, function (n) { return visibles[n.id]; });
    }
    function itemEnFoco(it, foco) {
      if (!foco) return true;
      if (it.via) return foco[it.via.id] !== undefined && (foco[it.a.id] !== undefined || foco[it.b.id] !== undefined);
      return foco[it.a.id] !== undefined && foco[it.b.id] !== undefined;
    }

    // ---------------------------------------------------------------- dibujo
    var flujosPantalla = [];
    function dibujar(ctx, lz) {
      if (!listaLugares || !cajaPais) return;
      agrupar(lz);
      var foco = focoActual();
      var hc = hover && hover.tipo === "lugar" ? clusterDe[hover.id] : null;
      var cs = lugarSel ? clusterDe[lugarSel] : null;

      ctx.lineJoin = "round";
      poligonos.forEach(function (pts) {
        ctx.beginPath();
        pts.forEach(function (p, i) { var w = mundo(p[0], p[1]), s = lz.aPantalla(w[0], w[1]); if (i) ctx.lineTo(s[0], s[1]); else ctx.moveTo(s[0], s[1]); });
        ctx.closePath();
        ctx.fillStyle = C.s2; ctx.globalAlpha = 1; ctx.fill();
        ctx.strokeStyle = C.borde; ctx.lineWidth = 1; ctx.stroke();
      });

      // Flujos sumados entre grupos visibles. Se dibujan los 50 más grandes: el resto se lista en el panel.
      var porPar = {};
      flujos.forEach(function (f) {
        var ca = clusterDe[f.a], cb = clusterDe[f.b];
        if (!ca || !cb || ca === cb) return;
        var items = foco ? f.items.filter(function (it) { return itemEnFoco(it, foco); }) : f.items;
        if (!items.length) return;
        var key = ca.id < cb.id ? ca.id + "|" + cb.id : cb.id + "|" + ca.id;
        var p = porPar[key] || (porPar[key] = { ca: ca, cb: cb, items: [], flujos: [] });
        p.items = p.items.concat(items); p.flujos.push(f);
      });
      var pares = Object.keys(porPar).map(function (kk) { return porPar[kk]; }).sort(function (a, b) { return b.items.length - a.items.length; });
      var dibujados = pares.slice(0, 50);
      flujosPantalla = [];
      dibujados.forEach(function (p) {
        var incide = hc ? p.ca === hc || p.cb === hc : cs ? p.ca === cs || p.cb === cs : true;
        if ((hc || cs) && !incide) return;
        var a = [p.ca.sx, p.ca.sy], b = [p.cb.sx, p.cb.sy];
        var mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1;
        var cx = mx - (dy / L) * L * 0.16, cy = my + (dx / L) * L * 0.16;
        var n = p.items.length;
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(cx, cy, b[0], b[1]);
        var activo = flujoSel && flujoSel === p.ca.id + "|" + p.cb.id || (hover && hover.tipo === "flujo" && hover.p === p);
        ctx.strokeStyle = activo || hc || cs ? C.acento : foco ? C.texto2 : C.tenue;
        ctx.globalAlpha = activo ? 1 : hc || cs || foco ? 0.75 : 0.35 + Math.min(0.4, n / 60);
        ctx.lineWidth = Math.min(10, 1 + Math.sqrt(n) * 1.1) + (activo ? 1.5 : 0);
        ctx.stroke();
        flujosPantalla.push({ p: p, a: a, b: b, c: [cx, cy] });
      });
      flujosOcultos = Math.max(0, pares.length - dibujados.length);

      clusters.forEach(function (c) {
        var atenuar = (foco && !c.miembros.some(function (L) { return L.entidades.some(function (n) { return foco[n.id] !== undefined; }); })) ||
          (hc && hc !== c && !pares.some(function (p) { return (p.ca === hc && p.cb === c) || (p.cb === hc && p.ca === c); }));
        ctx.globalAlpha = atenuar ? 0.25 : 1;
        ctx.beginPath(); ctx.arc(c.sx, c.sy, c.r, 0, Math.PI * 2);
        ctx.fillStyle = C.s0; ctx.fill();
        var ang = -Math.PI / 2;
        KR.TIPOS.forEach(function (t) {
          if (!c.cuenta[t]) return;
          var a1 = ang + (c.cuenta[t] / c.total) * Math.PI * 2;
          ctx.beginPath(); ctx.arc(c.sx, c.sy, c.r - 1.5, ang, a1);
          ctx.strokeStyle = C[t]; ctx.lineWidth = Math.max(2.5, Math.min(7, c.r * 0.3)); ctx.stroke();
          ang = a1;
        });
        if (c === hc || c === cs) { ctx.beginPath(); ctx.arc(c.sx, c.sy, c.r + 4, 0, Math.PI * 2); ctx.strokeStyle = C.texto; ctx.lineWidth = 2; ctx.stroke(); }
      });
      ctx.globalAlpha = 1;

      ctx.font = KR.FUENTE_CANVAS;
      var cands = clusters.map(function (c) {
        return { sx: c.sx, sy: c.sy, r: c.r, texto: nombreCluster(c) + " · " + KR.miles(c.total), n: null, fuerte: c === hc || c === cs };
      });
      var puestas = KR.colocarEtiquetas(ctx, cands, lz.w, lz.h, 40);
      ctx.textBaseline = "middle";
      puestas.forEach(function (pu) {
        ctx.lineWidth = 3; ctx.strokeStyle = C.s0; ctx.globalAlpha = 0.95; ctx.strokeText(pu.c.texto, pu.x, pu.y);
        ctx.globalAlpha = 1; ctx.fillStyle = pu.c.fuerte ? C.texto : C.texto2; ctx.fillText(pu.c.texto, pu.x, pu.y);
      });
      pintarLeyendaDinamica();
    }
    var flujosOcultos = 0;

    var lz = KR.lienzo(canvas, {
      minK: 3, maxK: 900, alDibujar: dibujar,
      alMover: function (sx, sy) { apuntar(sx, sy); },
      alSalir: function () { hover = null; tooltip.hidden = true; lz.dibujar(); },
      alClick: function (sx, sy) { tocar(sx, sy); }
    });
    limpiezas.push(lz.destruir);

    // ---------------------------------------------------------------- puntería
    function queHay(sx, sy) {
      for (var i = clusters.length - 1; i >= 0; i--) {
        var c = clusters[i];
        if (Math.hypot(c.sx - sx, c.sy - sy) < c.r + 3) return { tipo: "lugar", c: c };
      }
      var mejor = null, dMejor = 6;
      flujosPantalla.forEach(function (f) {
        for (var t = 0; t <= 1.0001; t += 1 / 16) {
          var x = (1 - t) * (1 - t) * f.a[0] + 2 * (1 - t) * t * f.c[0] + t * t * f.b[0];
          var y = (1 - t) * (1 - t) * f.a[1] + 2 * (1 - t) * t * f.c[1] + t * t * f.b[1];
          var d = Math.hypot(x - sx, y - sy);
          if (d < dMejor) { dMejor = d; mejor = { tipo: "flujo", p: f.p }; }
        }
      });
      return mejor;
    }
    var PLURAL = { "ensayo con sedes en ambas": "ensayos con sedes en ambas", "coautoría": "coautorías", "afiliación": "afiliaciones",
      "afiliación secundaria": "afiliaciones secundarias", "investigador de sitio": "investigadores de sitio" };
    function resumirItems(items) {
      var t = {};
      items.forEach(function (it) { t[it.tipo] = (t[it.tipo] || 0) + 1; });
      return Object.keys(t).sort(function (a, b) { return t[b] - t[a]; })
        .map(function (k) { return t[k] + " " + (t[k] === 1 ? k : PLURAL[k] || k); }).join(", ");
    }
    function mostrarTooltip(sx, sy, titulo, sub) {
      tooltip.innerHTML = "";
      tooltip.appendChild(el("div", "kr-tooltip-tit", titulo));
      if (sub) tooltip.appendChild(el("div", "kr-tooltip-sub", sub));
      tooltip.hidden = false;
      tooltip.style.transform = "translate(" + Math.max(8, Math.min(sx + 14, lz.w - tooltip.offsetWidth - 8)) + "px," + Math.max(8, Math.min(sy + 14, lz.h - tooltip.offsetHeight - 8)) + "px)";
    }
    function apuntar(sx, sy) {
      var q = queHay(sx, sy);
      var antes = hover;
      if (!q) { hover = null; tooltip.hidden = true; canvas.style.cursor = ""; if (antes) lz.dibujar(); return; }
      canvas.style.cursor = "pointer";
      if (q.tipo === "lugar") {
        hover = { tipo: "lugar", id: q.c.lider.nombre };
        var conex = flujos.filter(function (f) { return clusterDe[f.a] === q.c || clusterDe[f.b] === q.c; }).length;
        mostrarTooltip(sx, sy, q.c.miembros.map(function (L) { return L.nombre; }).join(", "),
          KR.miles(q.c.total) + " fichas: " + resumen(q.c.cuenta) + " · conectada con " + KR.plural(conex, "ciudad", "ciudades"));
      } else {
        hover = { tipo: "flujo", p: q.p };
        mostrarTooltip(sx, sy, nombreCluster(q.p.ca) + " ↔ " + nombreCluster(q.p.cb), q.p.items.length + " conexiones: " + resumirItems(q.p.items) + " · click para ver cada una");
      }
      lz.dibujar();
    }
    function resumen(c) {
      return KR.TIPOS.filter(function (t) { return c[t]; }).map(function (t) { return c[t] + " " + (c[t] === 1 ? KR.TIPO_LABEL[t] : KR.TIPO_PLURAL[t]).toLowerCase(); }).join(", ");
    }
    function tocar(sx, sy) {
      var q = queHay(sx, sy);
      if (!q) { if (lugarSel || flujoSel) { lugarSel = null; flujoSel = null; irA("resumen"); } return; }
      if (q.tipo === "lugar") {
        if (q.c.miembros.length > 1 && lz.cam.k < 400) {
          // Un grupo de ciudades se abre acercándose: es la única forma honesta de separarlas.
          var caja = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
          q.c.miembros.forEach(function (L) { caja.x0 = Math.min(caja.x0, L.x); caja.x1 = Math.max(caja.x1, L.x); caja.y0 = Math.min(caja.y0, L.y); caja.y1 = Math.max(caja.y1, L.y); });
          var dest = lz.encuadre(caja, 120); dest.k = Math.max(dest.k, lz.cam.k * 2.2);
          lz.animarA(dest, 420, false, KR.easeInOut);
        }
        abrirLugar(q.c.miembros.map(function (L) { return L.nombre; }));
      } else abrirFlujo(q.p);
    }

    // ---------------------------------------------------------------- panel
    function irA(v, datos, apilar) {
      if (apilar && vista !== v) pila.push({ vista: vista, datos: datosVista });
      if (!apilar) pila = [];
      vista = v; datosVista = datos;
      pintarPanel();
    }
    var datosVista = null;
    function volver() {
      var prev = pila.pop();
      if (!prev) { irA("resumen"); return; }
      vista = prev.vista; datosVista = prev.datos;
      if (vista !== "ficha") sel = null;
      if (vista === "resumen") { lugarSel = null; flujoSel = null; }
      pintarPanel(); pintarFoco(); lz.dibujar();
    }

    function abrirLugar(nombres) { lugarSel = nombres[0]; flujoSel = null; sel = null; irA("lugar", nombres, false); pintarFoco(); lz.dibujar(); }
    function abrirFlujo(p) { flujoSel = p.ca.id + "|" + p.cb.id; lugarSel = null; irA("flujo", p, !!pila.length || vista !== "resumen"); lz.dibujar(); }
    function abrirFicha(id, volar) {
      sel = id; lugarSel = null; flujoSel = null;
      irA("ficha", id, vista !== "resumen");
      pintarFoco();
      var n = g.byId[id];
      if (volar && n._ciudades && n._ciudades.length) {
        var caja = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
        n._ciudades.forEach(function (c) { var L = lugares[c]; caja.x0 = Math.min(caja.x0, L.x); caja.x1 = Math.max(caja.x1, L.x); caja.y0 = Math.min(caja.y0, L.y); caja.y1 = Math.max(caja.y1, L.y); });
        var pad = { x0: caja.x0 - 1.5, x1: caja.x1 + 1.5, y0: caja.y0 - 1.5, y1: caja.y1 + 1.5 };
        lz.animarA(lz.encuadre(pad, 60), 480, false, KR.easeInOut);
      }
      lz.dibujar();
    }

    function pintarPanel() {
      if (panelCuerpo.firstChild && panelCuerpo.firstChild._destruir) panelCuerpo.firstChild._destruir();
      panelCab.innerHTML = ""; panelCuerpo.innerHTML = "";
      if (vista !== "resumen") {
        var atras = el("button", "kr-btn kr-btn-chico", "← " + (pila.length ? "Volver" : "Todo el territorio")); atras.type = "button";
        atras.addEventListener("click", volver);
        panelCab.appendChild(atras);
      } else panelCab.appendChild(el("strong", "", "Territorio"));
      if (vista === "resumen") pintarResumen();
      else if (vista === "lugar") pintarLugar(datosVista);
      else if (vista === "flujo") pintarFlujo(datosVista);
      else if (vista === "ficha") {
        panelCuerpo.appendChild(KR.ficha(g.byId[datosVista], {
          alNavegar: function (id) { abrirFicha(id, true); },
          alResaltar: function (id) { hover = id ? { tipo: "ficha", id: id } : null; lz.dibujar(); }
        }));
      }
      panelCuerpo.scrollTop = 0;
    }
    function sec(t) { panelCuerpo.appendChild(el("h3", "kr-ficha-sec", t)); }

    function pintarResumen() {
      var c = KR.conteos(g, filtros);
      var p = el("p", "v4-resumen");
      p.appendChild(el("strong", "", KR.miles(Object.keys(visibles).length)));
      p.appendChild(document.createTextNode(" fichas en " + listaLugares.length + " ciudades · " + KR.miles(flujos.length) + " pares de ciudades conectados"));
      panelCuerpo.appendChild(p);
      if (sinLugar.length) panelCuerpo.appendChild(el("p", "kr-nota", KR.miles(sinLugar.length) + " fichas no traen una ciudad reconocible y no aparecen en el mapa (no se ubican por inferencia)."));
      if (KR.hayFiltros(filtros)) {
        var q = el("button", "kr-btn kr-btn-chico", "Quitar filtros"); q.type = "button";
        q.addEventListener("click", function () { filtros = KR.filtrosVacios(); cambio(); });
        panelCuerpo.appendChild(q);
      }
      sec("Tipo");
      panelCuerpo.appendChild(KR.faceta({
        filas: KR.TIPOS.map(function (t) { return { clave: t, nombre: KR.TIPO_PLURAL[t], forma: t, color: "var(--" + KR.TIPO_VAR[t] + ")", total: c.tipos[t].total, visibles: c.tipos[t].visibles, activa: filtros.tipos[t] }; }),
        alCambiar: function (t, on) { filtros.tipos[t] = on; cambio(); }
      }));
      sec("Año del hecho más reciente");
      panelCuerpo.appendChild(KR.histograma({ barras: c.barras, rango: filtros.anios, sinFecha: c.sinFecha, alCambiar: function (r) { filtros.anios = r; cambio(); } }));
      sec("Área");
      var areas = verTodasAreas ? c.areas : c.areas.slice(0, 5);
      panelCuerpo.appendChild(KR.faceta({
        filas: areas.map(function (a) { return { clave: a.area, nombre: a.area.charAt(0).toUpperCase() + a.area.slice(1), total: a.total, visibles: a.visibles, activa: !filtros.areas.length || filtros.areas.indexOf(a.area) !== -1 }; }),
        alCambiar: function (area, on) {
          if (!filtros.areas.length) filtros.areas = c.areas.map(function (x) { return x.area; });
          if (on && filtros.areas.indexOf(area) === -1) filtros.areas.push(area);
          if (!on) filtros.areas = filtros.areas.filter(function (x) { return x !== area; });
          if (filtros.areas.length === c.areas.length) filtros.areas = [];
          cambio();
        }
      }));
      var mas = el("button", "kr-btn kr-btn-chico", verTodasAreas ? "Ver menos" : "Ver las " + c.areas.length + " áreas"); mas.type = "button";
      mas.addEventListener("click", function () { verTodasAreas = !verTodasAreas; pintarPanel(); });
      panelCuerpo.appendChild(mas);
      sec("Ciudades");
      var ul = el("ul", "kr-con-lista");
      listaLugares.slice(0, 12).forEach(function (L) {
        var li = el("li", "kr-con"), fila = el("div", "kr-con-fila");
        var b = el("button", "kr-con-nombre", L.nombre); b.type = "button";
        b.addEventListener("click", function () { abrirLugar([L.nombre]); volarALugar(L); });
        b.addEventListener("mouseenter", function () { hover = { tipo: "lugar", id: L.nombre }; lz.dibujar(); });
        b.addEventListener("mouseleave", function () { hover = null; lz.dibujar(); });
        fila.appendChild(b); fila.appendChild(el("span", "kr-con-tipo", KR.miles(L.entidades.length) + " fichas"));
        li.appendChild(fila); ul.appendChild(li);
      });
      panelCuerpo.appendChild(ul);
      if (listaLugares.length > 12) panelCuerpo.appendChild(el("p", "kr-nota", "+" + (listaLugares.length - 12) + " ciudades más en el mapa."));
      sec("Qué comparte tu shortlist");
      panelCuerpo.appendChild(KR.panelEnComun({ ejemplo: true, alNavegar: function (id) { abrirFicha(id, true); }, alMostrar: function (ids) { abrirFicha(ids[0], true); } }));
    }
    function volarALugar(L) {
      var k = Math.max(lz.cam.k, 60);
      lz.animarA({ cx: L.x, cy: L.y, k: k }, 460, false, KR.easeInOut);
    }

    function pintarLugar(nombres) {
      var Ls = nombres.map(function (n) { return lugares[n]; }).filter(Boolean);
      if (!Ls.length) { irA("resumen"); return; }
      var ids = {}, ents = [];
      Ls.forEach(function (L) { L.entidades.forEach(function (n) { if (!ids[n.id]) { ids[n.id] = true; ents.push(n); } }); });
      var cab = el("header", "kr-ficha-cab");
      cab.appendChild(el("span", "kr-ficha-tipo", Ls.length > 1 ? "Ciudades agrupadas por cercanía" : "Ciudad"));
      cab.appendChild(el("h2", "kr-ficha-nombre", nombres.join(", ")));
      var cuenta = { persona: 0, institucion: 0, ensayo_clinico: 0 };
      ents.forEach(function (n) { cuenta[n.tipo]++; });
      cab.appendChild(el("p", "kr-ficha-sub", KR.miles(ents.length) + " fichas: " + resumen(cuenta)));
      panelCuerpo.appendChild(cab);
      panelCuerpo.appendChild(el("p", "kr-nota", "La ubicación es el centro de la ciudad que declara la fuente, no la dirección de cada centro."));
      var conex = flujos.filter(function (f) { return nombres.indexOf(f.a) !== -1 || nombres.indexOf(f.b) !== -1; })
        .filter(function (f) { return !(nombres.indexOf(f.a) !== -1 && nombres.indexOf(f.b) !== -1); })
        .sort(function (a, b) { return b.items.length - a.items.length; });
      sec("Conectada con " + KR.plural(conex.length, "ciudad", "ciudades"));
      var ul = el("ul", "kr-con-lista");
      conex.slice(0, 10).forEach(function (f) {
        var otra = nombres.indexOf(f.a) !== -1 ? f.b : f.a;
        var li = el("li", "kr-con"), fila = el("div", "kr-con-fila");
        var b = el("button", "kr-con-nombre", otra); b.type = "button";
        b.addEventListener("click", function () {
          var p = { ca: clusterDe[f.a] || { id: f.a }, cb: clusterDe[f.b] || { id: f.b }, items: f.items };
          abrirFlujo(p);
        });
        fila.appendChild(b); fila.appendChild(el("span", "kr-con-tipo", f.items.length + " · " + resumirItems(f.items)));
        li.appendChild(fila); ul.appendChild(li);
      });
      panelCuerpo.appendChild(ul);
      KR.TIPOS.forEach(function (t) {
        var ms = ents.filter(function (n) { return n.tipo === t; });
        if (!ms.length) return;
        sec(KR.TIPO_PLURAL[t] + " · " + ms.length);
        var ul2 = el("ul", "kr-con-lista");
        ms.slice(0, 25).forEach(function (n) {
          var li = el("li", "kr-con"), b = el("button", "kr-con-nombre", n.nombre); b.type = "button";
          b.addEventListener("click", function () { abrirFicha(n.id, false); });
          li.appendChild(b); ul2.appendChild(li);
        });
        if (ms.length > 25) ul2.appendChild(el("li", "kr-nota", "+" + (ms.length - 25) + " más"));
        panelCuerpo.appendChild(ul2);
      });
    }

    function pintarFlujo(p) {
      var cab = el("header", "kr-ficha-cab");
      cab.appendChild(el("span", "kr-ficha-tipo", "Entre ciudades"));
      cab.appendChild(el("h2", "kr-ficha-nombre kr-ficha-nombre-chico", (p.ca.lider ? nombreCluster(p.ca) : p.ca.id) + " ↔ " + (p.cb.lider ? nombreCluster(p.cb) : p.cb.id)));
      cab.appendChild(el("p", "kr-ficha-sub", p.items.length + " conexiones: " + resumirItems(p.items)));
      panelCuerpo.appendChild(cab);
      sec("Cada conexión y su fuente");
      var ul = el("ul", "kr-con-lista");
      p.items.slice(0, 40).forEach(function (it) {
        var li = el("li", "kr-con"), fila = el("div", "kr-con-fila");
        var titulo = it.via ? KR.etiquetaCorta(it.via) + " · " + KR.etiquetaCorta(it.a) + " y " + KR.etiquetaCorta(it.b)
          : KR.etiquetaCorta(it.a) + " ↔ " + KR.etiquetaCorta(it.b);
        var b = el("button", "kr-con-nombre", titulo); b.type = "button";
        b.addEventListener("click", function () { abrirFicha(it.via ? it.via.id : it.a.id, false); });
        fila.appendChild(b); fila.appendChild(el("span", "kr-con-tipo", it.tipo));
        var ev = KR.evidencia(it.via ? it.va : it.v);
        var exp = el("button", "kr-con-ev"); exp.type = "button"; exp.appendChild(KR.insigniaEvidencia(ev));
        var det = null;
        exp.addEventListener("click", function () { if (!det) { det = KR.detalleEvidencia(ev); li.appendChild(det); } else det.hidden = !det.hidden; });
        fila.appendChild(exp); li.appendChild(fila); ul.appendChild(li);
      });
      if (p.items.length > 40) ul.appendChild(el("li", "kr-nota", "+" + (p.items.length - 40) + " más"));
      panelCuerpo.appendChild(ul);
    }

    function pintarFoco() {
      barraFoco.innerHTML = "";
      if (!sel) { barraFoco.hidden = true; return; }
      barraFoco.hidden = false;
      var t = el("span"); t.appendChild(document.createTextNode("Red de ")); t.appendChild(el("strong", "", KR.etiquetaCorta(g.byId[sel])));
      barraFoco.appendChild(t);
      var seg = el("div", "kr-seg");
      [1, 2].forEach(function (d) {
        var b = el("button", "kr-seg-btn", d === 1 ? "Directas" : "A 2 saltos"); b.type = "button";
        b.setAttribute("aria-pressed", String(profundidad === d));
        b.addEventListener("click", function () { profundidad = d; pintarFoco(); lz.dibujar(); escribirHash(); });
        seg.appendChild(b);
      });
      barraFoco.appendChild(seg);
      var foco = focoActual() || {};
      var ciudades = {};
      Object.keys(foco).forEach(function (id) { (g.byId[id]._ciudades || []).forEach(function (c) { ciudades[c] = true; }); });
      var nc = Object.keys(ciudades).length;
      barraFoco.appendChild(el("span", "kr-nota", "en " + nc + (nc === 1 ? " ciudad" : " ciudades")));
      var x = el("button", "kr-btn kr-btn-chico", "Ver todo"); x.type = "button";
      x.addEventListener("click", function () { sel = null; irA("resumen"); pintarFoco(); restablecer(false); });
      barraFoco.appendChild(x);
    }

    function pintarOrientacion() {
      orient.innerHTML = "";
      [["h", "Horizontal"], ["v", "Vertical"]].forEach(function (o) {
        var b = el("button", "kr-seg-btn", o[1]); b.type = "button";
        b.setAttribute("aria-pressed", String(orientacion === o[0]));
        b.addEventListener("click", function () {
          if (orientacion === o[0]) return;
          orientacion = o[0]; calcularCaja(); recalcular(); pintarOrientacion(); pintarPanel(); restablecer(true); escribirHash();
        });
        orient.appendChild(b);
      });
      orient.appendChild(el("span", "v4-norte", orientacion === "h" ? "← Norte" : "↑ Norte"));
    }
    var leyendaDin = null;
    function pintarLeyenda() {
      leyenda.innerHTML = "";
      var c = el("span"); c.appendChild(el("i", "v3-ley-burbuja")); c.appendChild(document.createTextNode("Ciudad: tamaño = fichas, anillo = tipos"));
      leyenda.appendChild(c);
      leyenda.appendChild(el("span", "", "Línea = conexiones entre ciudades"));
      leyendaDin = el("span", "kr-medidor");
      leyenda.appendChild(leyendaDin);
    }
    function pintarLeyendaDinamica() {
      if (!leyendaDin) return;
      var agrupadas = clusters.filter(function (c) { return c.miembros.length > 1; }).length;
      leyendaDin.textContent = clusters.length + " puntos" + (agrupadas ? " (" + agrupadas + " agrupan ciudades cercanas)" : "") +
        (flujosOcultos ? " · " + flujosOcultos + " líneas menores sin dibujar" : "");
    }

    function escribirHash() { KR.hash.escribir(filtros, { o: orientacion, d: sel && profundidad === 2 ? "2" : null }); }
    function cambio() {
      recalcular();
      if (sel && !visibles[sel]) { sel = null; pintarFoco(); }
      if (vista === "resumen") pintarPanel();
      escribirHash(); lz.dibujar();
    }
    // Se encuadran las ciudades con fichas, no el país entero: el extremo sur no tiene datos hoy y
    // encuadrarlo dejaba la zona con actividad a la mitad del tamaño.
    function restablecer(inmediato) {
      var caja = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
      listaLugares.forEach(function (L) {
        caja.x0 = Math.min(caja.x0, L.x); caja.x1 = Math.max(caja.x1, L.x);
        caja.y0 = Math.min(caja.y0, L.y); caja.y1 = Math.max(caja.y1, L.y);
      });
      if (!isFinite(caja.x0)) caja = cajaPais;
      else { caja.x0 -= 1.6; caja.x1 += 1.6; caja.y0 -= 1.6; caja.y1 += 1.6; }
      lz.animarA(lz.encuadre(caja, 36), 420, inmediato, KR.easeInOut);
    }

    KR.autocompletar(input, {
      etiqueta: function (n) { return KR.pasa(n, filtros) ? "" : "oculto por filtros"; },
      alElegir: function (n) {
        if (!KR.pasa(n, filtros)) { filtros = KR.filtrosVacios(); cambio(); }
        abrirFicha(n.id, true); input.blur();
      }
    });
    mapa.appendChild(KR.botonesZoom(lz, restablecer));
    limpiezas.push(KR.shortlist.escuchar(function () { if (vista === "resumen") pintarPanel(); }));
    limpiezas.push(KR.alCambiarTema(function () { C = KR.colores(); lz.dibujar(); }));

    requestAnimationFrame(function () {
      if (!orientacion) {
        var r = mapa.getBoundingClientRect();
        orientacion = r.width / Math.max(1, r.height) > 1.15 ? "h" : "v";
      }
      calcularCaja(); recalcular(); pintarOrientacion(); pintarLeyenda(); pintarPanel();
      restablecer(true);
      if (h0.f && g.byId[h0.f]) abrirFicha(h0.f, true);
      if (canvas.animate) canvas.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
    });
    return function () { limpiezas.forEach(function (fn) { fn(); }); };
  }

  window.VARIANTES = window.VARIANTES || [];
  window.VARIANTES[3] = { nombre: "Territorio", montar: montar };
})();
