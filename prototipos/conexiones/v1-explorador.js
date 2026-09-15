/* Prototipo 1 — «Explorador».
 * Eje: DISPOSICIÓN. El mapa ocupa toda la pantalla y los controles viven en un panel fijo al
 * costado, como Retina y el demo de sigma.js. Escala dibujando TODO en canvas con posiciones
 * precalculadas: filtrar oculta nodos, nunca recalcula el layout. */
(function () {
  "use strict";
  var KR = window.KR;

  function montar(stage) {
    var el = KR.el;
    var h0 = KR.hash.leer();
    var filtros = KR.hash.aFiltros(h0);
    var grafo = KR.datos.grafo, prueba = false;
    var sel = null, profundidad = h0.d === "2" ? 2 : 1, hover = null, aristaHover = null, resaltadoLista = null;
    var grupoResaltado = null, tituloGrupo = "", avisoFiltros = "";
    var verTodasAreas = false;
    var visN = null, visE = null, visibles = null, ordenEtiquetas = null, grilla = null;
    var C = KR.colores();
    var limpiezas = [];

    // ---------------------------------------------------------------- estructura
    var raiz = el("div", "variante v1");
    var top = el("header", "kr-top");
    var marca = el("div", "kr-marca");
    marca.appendChild(el("span", "kr-marca-nombre", "KOL Radar"));
    marca.appendChild(el("span", "kr-marca-tag", "oncología · Chile"));
    top.appendChild(marca);
    top.appendChild(el("span", "kr-top-sep"));
    var compartir = KR.botonCompartir(function () {
      return { filtros: filtros, ficha: sel ? grafo.byId[sel] : null, extra: { d: profundidad === 2 ? "2" : null } };
    });
    limpiezas.push(compartir.destruir);
    top.appendChild(compartir.el);
    raiz.appendChild(top);
    raiz.appendChild(KR.lineaBeta());

    var main = el("div", "v1-main");
    var panel = el("aside", "v1-panel");
    panel.setAttribute("aria-label", "Buscar y filtrar");
    var buscarWrap = el("div", "kr-buscar");
    var input = el("input"); input.type = "search"; input.placeholder = "Buscar persona, institución o ensayo…";
    input.setAttribute("aria-label", "Buscar en el mapa");
    buscarWrap.appendChild(input);
    panel.appendChild(buscarWrap);
    var panelCuerpo = el("div", "v1-panel-cuerpo");
    panel.appendChild(panelCuerpo);
    main.appendChild(panel);

    var mapa = el("section", "v1-mapa");
    var canvas = el("canvas", "kr-canvas");
    canvas.setAttribute("aria-label", "Mapa de conexiones. Usá la búsqueda del panel para ubicar una ficha.");
    mapa.appendChild(canvas);
    var tooltip = el("div", "kr-tooltip"); tooltip.hidden = true;
    mapa.appendChild(tooltip);
    var barraFoco = el("div", "v1-foco"); barraFoco.hidden = true;
    mapa.appendChild(barraFoco);
    var leyenda = el("div", "kr-leyenda v1-leyenda");
    mapa.appendChild(leyenda);
    var drawer = el("aside", "kr-drawer");
    drawer.setAttribute("inert", "");
    var drawerCerrar = el("button", "kr-drawer-cerrar", "✕"); drawerCerrar.type = "button";
    drawerCerrar.setAttribute("aria-label", "Cerrar ficha");
    var drawerCuerpo = el("div", "kr-drawer-cuerpo");
    drawer.appendChild(drawerCerrar); drawer.appendChild(drawerCuerpo);
    mapa.appendChild(drawer);
    main.appendChild(mapa);
    raiz.appendChild(main);
    stage.appendChild(raiz);

    // ---------------------------------------------------------------- visibilidad
    function recalcular() {
      visN = { persona: [], institucion: [], ensayo_clinico: [] };
      visibles = {};
      grafo.nodos.forEach(function (n) {
        if (KR.pasa(n, filtros)) { visN[n.tipo].push(n); visibles[n.id] = true; }
      });
      visE = grafo.vinculos.filter(function (v) { return visibles[v.origen] && visibles[v.destino]; });
      var prio = { persona: 0, institucion: 1, ensayo_clinico: 2 };
      ordenEtiquetas = [].concat(visN.persona, visN.institucion, visN.ensayo_clinico).sort(function (a, b) {
        return prio[a.tipo] - prio[b.tipo] || b._grado - a._grado;
      });
      // Grilla del mundo para encontrar el nodo bajo el puntero sin recorrer todos.
      grilla = {};
      var CEL = 40;
      ordenEtiquetas.forEach(function (n) {
        var key = Math.floor(n._x / CEL) + ":" + Math.floor(n._y / CEL);
        (grilla[key] = grilla[key] || []).push(n);
      });
      grilla._cel = CEL;
    }

    function focoActual() {
      if (hover) return KR.vecindario(grafo, hover, 1, function (n) { return visibles[n.id]; });
      if (grupoResaltado) return grupoResaltado;
      if (sel && visibles[sel]) return KR.vecindario(grafo, sel, profundidad, function (n) { return visibles[n.id]; });
      return null;
    }

    function radio(n, k) {
      var base = n.tipo === "institucion" ? 5.5 : n.tipo === "persona" ? 4.2 : 2.6;
      var r = (base + Math.min(n._grado, 30) * 0.16) * Math.max(0.45, Math.min(2.6, Math.sqrt(k)));
      return Math.max(1.4, Math.min(24, r));
    }

    // ---------------------------------------------------------------- dibujo
    function dibujar(ctx, lz) {
      var cam = lz.cam, k = cam.k, w = lz.w, h = lz.h;
      var m = 40 / k;
      var vx0 = cam.cx - w / 2 / k - m, vx1 = cam.cx + w / 2 / k + m, vy0 = cam.cy - h / 2 / k - m, vy1 = cam.cy + h / 2 / k + m;
      var foco = focoActual();
      var centro = hover || (grupoResaltado ? null : sel);
      var byId = grafo.byId, i, v, a, b, p, q;

      ctx.lineCap = "round";
      ctx.beginPath();
      for (i = 0; i < visE.length; i++) {
        v = visE[i]; a = byId[v.origen]; b = byId[v.destino];
        if ((a._x < vx0 && b._x < vx0) || (a._x > vx1 && b._x > vx1) || (a._y < vy0 && b._y < vy0) || (a._y > vy1 && b._y > vy1)) continue;
        if (foco && (foco[a.id] === undefined || foco[b.id] === undefined)) continue;
        if (centro && (a.id === centro || b.id === centro)) continue;
        p = lz.aPantalla(a._x, a._y); q = lz.aPantalla(b._x, b._y);
        ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]);
      }
      // Como el demo de sigma.js: con un nodo resaltado, las aristas ajenas no se atenúan, se van.
      ctx.strokeStyle = foco ? C.texto2 : C.tenue;
      ctx.globalAlpha = foco ? 0.4 : visE.length > 3000 ? 0.1 : 0.26;
      ctx.lineWidth = k < 0.5 ? 0.6 : 1;
      ctx.stroke();
      if (centro && visibles[centro]) {
        ctx.beginPath();
        var pc = lz.aPantalla(byId[centro]._x, byId[centro]._y);
        grafo.adj[centro].forEach(function (x) {
          if (!visibles[x.otro]) return;
          var po = lz.aPantalla(byId[x.otro]._x, byId[x.otro]._y);
          ctx.moveTo(pc[0], pc[1]); ctx.lineTo(po[0], po[1]);
        });
        ctx.strokeStyle = C[byId[centro].tipo]; ctx.globalAlpha = 0.85; ctx.lineWidth = 1.8;
        ctx.stroke();
      }
      var ah = aristaHover || (resaltadoLista && resaltadoLista.v);
      if (ah && visibles[ah.origen] && visibles[ah.destino]) {
        p = lz.aPantalla(byId[ah.origen]._x, byId[ah.origen]._y); q = lz.aPantalla(byId[ah.destino]._x, byId[ah.destino]._y);
        ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]);
        ctx.strokeStyle = C.acento; ctx.globalAlpha = 1; ctx.lineWidth = 3; ctx.stroke();
      }

      function pasada(atenuados) {
        KR.TIPOS.forEach(function (t) {
          var lista = visN[t], hay = false;
          ctx.beginPath();
          for (var j = 0; j < lista.length; j++) {
            var n = lista[j];
            if (n._x < vx0 || n._x > vx1 || n._y < vy0 || n._y > vy1) continue;
            var dentro = !foco || foco[n.id] !== undefined;
            if (dentro === atenuados) continue;
            var s = lz.aPantalla(n._x, n._y);
            KR.trazarForma(ctx, t, s[0], s[1], radio(n, k));
            hay = true;
          }
          if (!hay) return;
          ctx.fillStyle = C[t]; ctx.globalAlpha = atenuados ? 0.12 : 1; ctx.fill();
        });
      }
      pasada(true);
      pasada(false);

      ctx.globalAlpha = 1;
      var sl = KR.shortlist.lista();
      if (sl.length) {
        ctx.beginPath();
        sl.forEach(function (id) {
          var n = byId[id];
          if (!n || !visibles[id]) return;
          var s = lz.aPantalla(n._x, n._y), r = radio(n, k) + 3.5;
          ctx.moveTo(s[0] + r, s[1]); ctx.arc(s[0], s[1], r, 0, Math.PI * 2);
        });
        ctx.strokeStyle = C.acento; ctx.lineWidth = 2; ctx.stroke();
      }
      [sel, hover, resaltadoLista && resaltadoLista.id].forEach(function (id, idx) {
        if (!id || !visibles[id]) return;
        var n = byId[id], s = lz.aPantalla(n._x, n._y);
        KR.dibujarForma(ctx, n.tipo, s[0], s[1], radio(n, k) + (idx === 0 ? 2.5 : 1.5));
        ctx.strokeStyle = C.texto; ctx.lineWidth = idx === 0 ? 2.5 : 1.5; ctx.stroke();
      });

      // Etiquetas por nivel de detalle: a más zoom, más nombres. Primero el vecindario en foco.
      ctx.font = KR.FUENTE_CANVAS;
      var candidatos = [], maxEt = Math.floor((w * h) / 7000);
      function candidato(n, fuerte) {
        if (n._x < vx0 || n._x > vx1 || n._y < vy0 || n._y > vy1) return;
        if (!fuerte && n.tipo === "ensayo_clinico" && k < 1.6) return;
        if (!fuerte && foco && foco[n.id] === undefined) return;
        var s = lz.aPantalla(n._x, n._y);
        n._txt = n._txt || KR.etiquetaCorta(n);
        candidatos.push({ sx: s[0], sy: s[1], r: radio(n, k), texto: n._txt, ancho: n._tw, n: n, fuerte: fuerte });
      }
      [sel, hover].forEach(function (id) { if (id && visibles[id]) candidato(byId[id], true); });
      if (foco) Object.keys(foco).sort(function (x, y) { return foco[x] - foco[y] || byId[y]._grado - byId[x]._grado; })
        .forEach(function (id) { candidato(byId[id], true); });
      for (i = 0; i < ordenEtiquetas.length && candidatos.length < maxEt * 5; i++) candidato(ordenEtiquetas[i], false);
      var puestas = KR.colocarEtiquetas(ctx, candidatos, w, h, maxEt);
      ctx.textBaseline = "middle";
      ctx.lineJoin = "round";
      puestas.forEach(function (pu) {
        pu.c.n._tw = pu.c.ancho;
        ctx.lineWidth = 3; ctx.strokeStyle = C.s0; ctx.globalAlpha = 0.9;
        ctx.strokeText(pu.c.texto, pu.x, pu.y);
        ctx.globalAlpha = 1; ctx.fillStyle = pu.c.fuerte ? C.texto : C.texto2;
        ctx.fillText(pu.c.texto, pu.x, pu.y);
      });
      etiquetasDibujadas = puestas.length;
    }
    var etiquetasDibujadas = 0, tiempos = [];

    var lz = KR.lienzo(canvas, {
      minK: 0.04, maxK: 14,
      alDibujar: dibujar,
      alMedir: function (ms) { tiempos.push(ms); if (tiempos.length > 30) tiempos.shift(); pintarMedidor(); },
      alMover: function (sx, sy) { apuntar(sx, sy); },
      alSalir: function () { estable.poner(null); aristaHover = null; tooltip.hidden = true; lz.dibujar(); },
      alClick: function (sx, sy) { tocar(sx, sy); }
    });
    limpiezas.push(lz.destruir);

    var estable = KR.hoverEstable(function (id) { hover = id; lz.dibujar(); });

    function nodoEn(sx, sy) {
      var m = lz.aMundo(sx, sy), k = lz.cam.k, CEL = grilla._cel, mejor = null, dMejor = Infinity;
      var tol = 8 / k;
      var gx0 = Math.floor((m[0] - tol - 24 / k) / CEL), gx1 = Math.floor((m[0] + tol + 24 / k) / CEL);
      var gy0 = Math.floor((m[1] - tol - 24 / k) / CEL), gy1 = Math.floor((m[1] + tol + 24 / k) / CEL);
      if ((gx1 - gx0) * (gy1 - gy0) > 400) return null;
      for (var gx = gx0; gx <= gx1; gx++) for (var gy = gy0; gy <= gy1; gy++) {
        var lista = grilla[gx + ":" + gy]; if (!lista) continue;
        for (var i = 0; i < lista.length; i++) {
          var n = lista[i], r = radio(n, k) / k + tol * 0.4;
          var d = Math.hypot(n._x - m[0], n._y - m[1]);
          if (d < r && d < dMejor) { mejor = n; dMejor = d; }
        }
      }
      return mejor;
    }
    function aristaEn(sx, sy) {
      var byId = grafo.byId, mejor = null, dMejor = 5;
      var foco = focoActual();
      for (var i = 0; i < visE.length; i++) {
        var v = visE[i], a = byId[v.origen], b = byId[v.destino];
        if (foco && (foco[a.id] === undefined || foco[b.id] === undefined)) continue;
        var p = lz.aPantalla(a._x, a._y), q = lz.aPantalla(b._x, b._y);
        var dx = q[0] - p[0], dy = q[1] - p[1], L = dx * dx + dy * dy || 1;
        var t = Math.max(0, Math.min(1, ((sx - p[0]) * dx + (sy - p[1]) * dy) / L));
        var d = Math.hypot(sx - (p[0] + t * dx), sy - (p[1] + t * dy));
        if (d < dMejor) { dMejor = d; mejor = v; }
      }
      return mejor;
    }

    function mostrarTooltip(sx, sy, titulo, sub, extra) {
      tooltip.innerHTML = "";
      tooltip.appendChild(el("div", "kr-tooltip-tit", titulo));
      if (sub) tooltip.appendChild(el("div", "kr-tooltip-sub", sub));
      if (extra) tooltip.appendChild(extra);
      tooltip.hidden = false;
      var x = Math.min(sx + 14, lz.w - tooltip.offsetWidth - 8), y = Math.min(sy + 14, lz.h - tooltip.offsetHeight - 8);
      tooltip.style.transform = "translate(" + Math.max(8, x) + "px," + Math.max(8, y) + "px)";
    }

    function apuntar(sx, sy) {
      var n = nodoEn(sx, sy);
      if (n) {
        aristaHover = null;
        estable.poner(n.id);
        canvas.style.cursor = "pointer";
        mostrarTooltip(sx, sy, n.nombre, KR.TIPO_LABEL[n.tipo] + " · " + grafo.adj[n.id].length + " conexiones");
        return;
      }
      estable.poner(null);
      var v = grafo.vinculos.length <= 20000 ? aristaEn(sx, sy) : null;
      if (v !== aristaHover) { aristaHover = v; lz.dibujar(); }
      if (v) {
        canvas.style.cursor = "pointer";
        var ev = KR.evidencia(v);
        var extra = el("div", "kr-tooltip-ev"); extra.appendChild(KR.insigniaEvidencia(ev));
        extra.appendChild(el("span", "", " Click para ver la fuente"));
        mostrarTooltip(sx, sy, grafo.byId[v.origen].nombre + " ↔ " + grafo.byId[v.destino].nombre, v.tipo, extra);
      } else { canvas.style.cursor = ""; tooltip.hidden = true; }
    }

    function tocar(sx, sy) {
      var n = nodoEn(sx, sy);
      if (n) { seleccionar(n.id, false); return; }
      var v = aristaEn(sx, sy);
      if (v) { abrirArista(v); return; }
      grupoResaltado = null; seleccionar(null);
    }

    // ---------------------------------------------------------------- ficha / drawer
    function abrirDrawer(contenido) {
      if (drawerCuerpo.firstChild && drawerCuerpo.firstChild._destruir) drawerCuerpo.firstChild._destruir();
      drawerCuerpo.innerHTML = "";
      drawerCuerpo.appendChild(contenido);
      drawerCuerpo.scrollTop = 0;
      drawer.classList.add("abierto");
      drawer.removeAttribute("inert");
    }
    function cerrarDrawer() {
      drawer.classList.remove("abierto");
      drawer.setAttribute("inert", "");
    }
    drawerCerrar.addEventListener("click", function () { seleccionar(null); });

    function seleccionar(id, volar) {
      sel = id;
      grupoResaltado = null;
      if (!id) { cerrarDrawer(); pintarFoco(); lz.dibujar(); return; }
      var n = grafo.byId[id];
      abrirDrawer(KR.ficha(n, {
        alNavegar: function (otro) { seleccionar(otro, true); },
        alResaltar: function (otro, v) { resaltadoLista = otro ? { id: otro, v: v } : null; lz.dibujar(); }
      }));
      pintarFoco();
      if (volar) volarA(n);
      lz.dibujar();
    }
    function abrirArista(v) {
      var a = grafo.byId[v.origen], b = grafo.byId[v.destino], ev = KR.evidencia(v);
      var art = el("article", "kr-ficha");
      var cab = el("header", "kr-ficha-cab");
      cab.appendChild(el("span", "kr-ficha-tipo", "Conexión · " + v.tipo));
      cab.appendChild(el("h2", "kr-ficha-nombre kr-ficha-nombre-chico", a.nombre + " ↔ " + b.nombre));
      art.appendChild(cab);
      var acc = el("div", "kr-ficha-acciones");
      [a, b].forEach(function (n) {
        var bt = el("button", "kr-btn", "Abrir " + KR.etiquetaCorta(n)); bt.type = "button";
        bt.addEventListener("click", function () { seleccionar(n.id, true); });
        acc.appendChild(bt);
      });
      art.appendChild(acc);
      art.appendChild(el("h3", "kr-ficha-sec", "¿Por qué están conectados?"));
      art.appendChild(KR.insigniaEvidencia(ev));
      art.appendChild(KR.detalleEvidencia(ev));
      sel = null; tituloGrupo = ""; grupoResaltado = {}; grupoResaltado[a.id] = 0; grupoResaltado[b.id] = 1;
      abrirDrawer(art); pintarFoco(); lz.dibujar();
    }

    function volarA(n) {
      var b = lz.base(), k = Math.max(b.k, 1.8);
      var s = lz.aPantalla(n._x, n._y);
      var enVista = s[0] > 60 && s[0] < lz.w - 420 && s[1] > 60 && s[1] < lz.h - 60;
      if (enVista && lz.cam.k >= 1.2) return;
      // El drawer tapa la derecha: se centra el nodo en la parte visible del mapa.
      var desplaz = Math.min(200, lz.w * 0.18) / k;
      var d = Math.hypot(n._x - lz.cam.cx, n._y - lz.cam.cy) * lz.cam.k;
      lz.animarA({ cx: n._x + desplaz, cy: n._y, k: k }, Math.min(520, 280 + d * 0.25), false, KR.easeInOut);
    }
    function encuadrarFoco() {
      var foco = focoActual() || {};
      var ids = Object.keys(foco);
      if (!ids.length) return;
      var caja = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
      ids.forEach(function (id) {
        var n = grafo.byId[id];
        caja.x0 = Math.min(caja.x0, n._x); caja.x1 = Math.max(caja.x1, n._x);
        caja.y0 = Math.min(caja.y0, n._y); caja.y1 = Math.max(caja.y1, n._y);
      });
      var dest = lz.encuadre(caja, 70);
      dest.k = Math.min(dest.k, 4);
      dest.cx += Math.min(200, lz.w * 0.18) / dest.k;
      lz.animarA(dest, 420, false, KR.easeInOut);
    }

    // ---------------------------------------------------------------- barra de foco
    function pintarFoco() {
      barraFoco.innerHTML = "";
      if (!sel && !grupoResaltado && !avisoFiltros) { barraFoco.hidden = true; return; }
      barraFoco.hidden = false;
      if (avisoFiltros) { barraFoco.appendChild(el("span", "v1-foco-aviso", avisoFiltros)); }
      if (grupoResaltado && !sel) {
        barraFoco.appendChild(el("span", "", tituloGrupo || "Conexión seleccionada"));
      } else if (sel) {
        var n = grafo.byId[sel];
        var t = el("span"); t.appendChild(document.createTextNode("Red de ")); t.appendChild(el("strong", "", KR.etiquetaCorta(n)));
        barraFoco.appendChild(t);
        var seg = el("div", "kr-seg"); seg.setAttribute("role", "group"); seg.setAttribute("aria-label", "Distancia");
        [1, 2].forEach(function (d) {
          var b = el("button", "kr-seg-btn", d === 1 ? "Directas" : "A 2 saltos"); b.type = "button";
          b.setAttribute("aria-pressed", String(profundidad === d));
          b.addEventListener("click", function () { profundidad = d; pintarFoco(); lz.dibujar(); escribirHash(); });
          seg.appendChild(b);
        });
        barraFoco.appendChild(seg);
        var cuantos = Object.keys(KR.vecindario(grafo, sel, profundidad, function (x) { return visibles[x.id]; })).length - 1;
        barraFoco.appendChild(el("span", "kr-nota", KR.miles(cuantos) + " fichas"));
      }
      var enc = el("button", "kr-btn kr-btn-chico", "Encuadrar"); enc.type = "button";
      enc.addEventListener("click", encuadrarFoco);
      var x = el("button", "kr-btn kr-btn-chico", "Ver todo"); x.type = "button";
      x.addEventListener("click", function () { avisoFiltros = ""; seleccionar(null); restablecer(false); });
      if (sel || grupoResaltado) barraFoco.appendChild(enc);
      barraFoco.appendChild(x);
    }

    // ---------------------------------------------------------------- panel
    function seccion(titulo, extra) {
      var s = el("section", "v1-sec");
      var h = el("h3", "v1-sec-tit", titulo);
      if (extra) h.appendChild(extra);
      s.appendChild(h);
      panelCuerpo.appendChild(s);
      return s;
    }
    function pintarPanel() {
      panelCuerpo.innerHTML = "";
      var c = KR.conteos(grafo, filtros, KR.datos.grafo.nodos);

      var s0 = seccion("Lo que ves");
      var pct = c.total ? c.visibles / c.total : 1;
      var linea = el("p", "v1-resumen");
      linea.appendChild(el("strong", "", KR.miles(c.visibles)));
      linea.appendChild(document.createTextNode(c.visibles === c.total ? " fichas · " + KR.miles(visE.length) + " conexiones" :
        " de " + KR.miles(c.total) + " fichas (" + Math.round(pct * 100) + "%) · " + KR.miles(visE.length) + " conexiones"));
      s0.appendChild(linea);
      var barra = el("div", "kr-faceta-barra v1-resumen-barra");
      var rel = el("span", "kr-faceta-relleno"); rel.style.transform = "scaleX(" + pct + ")";
      barra.appendChild(rel); s0.appendChild(barra);
      if (KR.hayFiltros(filtros)) {
        var q = el("button", "kr-btn kr-btn-chico", "Quitar filtros"); q.type = "button";
        q.addEventListener("click", function () { filtros = KR.filtrosVacios(); cambioFiltros(); });
        s0.appendChild(q);
      }

      var s1 = seccion("Tipo");
      s1.appendChild(KR.faceta({
        filas: KR.TIPOS.map(function (t) {
          return { clave: t, nombre: KR.TIPO_PLURAL[t], forma: t, color: "var(--" + KR.TIPO_VAR[t] + ")", total: c.tipos[t].total, visibles: c.tipos[t].visibles, activa: filtros.tipos[t] };
        }),
        alCambiar: function (t, on) { filtros.tipos[t] = on; cambioFiltros(); }
      }));

      var s2 = seccion("Área", filtros.areas.length ? el("span", "v1-sec-num", filtros.areas.length + " elegidas") : null);
      var areas = verTodasAreas ? c.areas : c.areas.slice(0, 6);
      s2.appendChild(KR.faceta({
        filas: areas.map(function (a) {
          return { clave: a.area, nombre: a.area.charAt(0).toUpperCase() + a.area.slice(1), total: a.total, visibles: a.visibles,
            activa: !filtros.areas.length || filtros.areas.indexOf(a.area) !== -1 };
        }),
        alCambiar: function (area, on) {
          if (!filtros.areas.length) filtros.areas = c.areas.map(function (x) { return x.area; });
          if (on && filtros.areas.indexOf(area) === -1) filtros.areas.push(area);
          if (!on) filtros.areas = filtros.areas.filter(function (x) { return x !== area; });
          if (filtros.areas.length === c.areas.length) filtros.areas = [];
          cambioFiltros();
        }
      }));
      if (c.areas.length > 6) {
        var mas = el("button", "kr-btn kr-btn-chico", verTodasAreas ? "Ver menos" : "Ver las " + c.areas.length + " áreas"); mas.type = "button";
        mas.addEventListener("click", function () { verTodasAreas = !verTodasAreas; pintarPanel(); });
        s2.appendChild(mas);
      }

      var s3 = seccion("Año del hecho más reciente");
      s3.appendChild(KR.histograma({ barras: c.barras, rango: filtros.anios, sinFecha: c.sinFecha,
        alCambiar: function (r) { filtros.anios = r; cambioFiltros(); } }));

      var s4 = seccion("Qué comparte tu shortlist");
      s4.appendChild(KR.panelEnComun({
        ejemplo: true,
        alNavegar: function (id) { seleccionar(id, true); },
        alMostrar: function (ids, r) {
          sel = null; grupoResaltado = {};
          ids.forEach(function (id) { grupoResaltado[id] = 0; });
          r.compartidos.forEach(function (x) { grupoResaltado[x.n.id] = 1; });
          tituloGrupo = "Lo que comparte tu shortlist";
          cerrarDrawer(); pintarFoco(); encuadrarFoco(); lz.dibujar();
        }
      }));

      var ev = KR.evidenciaResumen();
      var s5 = seccion("De dónde sale cada conexión");
      var ul = el("ul", "v1-ev-lista");
      [["compartida", "misma fuente en las dos fichas"], ["registro", "remitidas al registro del ensayo"], ["sin-fuente", "sin fuente propia en los datos"]].forEach(function (x) {
        var li = el("li");
        li.appendChild(KR.insigniaEvidencia({ nivel: x[0] }));
        li.appendChild(el("span", "", " " + KR.miles(ev[x[0]]) + " " + x[1]));
        ul.appendChild(li);
      });
      s5.appendChild(ul);
      s5.appendChild(el("p", "kr-nota", "Pasá el mouse sobre una línea del mapa para ver la suya."));

      var s6 = seccion("Prueba de carga");
      var lab = el("label", "kr-check");
      var cb = el("input"); cb.type = "checkbox"; cb.checked = prueba;
      lab.appendChild(cb);
      lab.appendChild(el("span", "", "Dibujar 10 copias anónimas del mapa (" + KR.miles(KR.datos.grafo.nodos.length * 10) + " nodos)"));
      cb.addEventListener("change", function () {
        prueba = cb.checked;
        grafo = prueba ? KR.pruebaDeCarga(10) : KR.datos.grafo;
        seleccionar(null); recalcular(); pintarPanel(); restablecer(false);
      });
      s6.appendChild(lab);
      s6.appendChild(el("p", "kr-nota", "Nodos sintéticos sin nombre ni hechos, para medir cuánto aguanta el dibujo. No son datos."));
    }

    function pintarLeyenda() {
      leyenda.innerHTML = "";
      KR.TIPOS.forEach(function (t) {
        var s = el("span"); s.appendChild(KR.formaSVG(t, 10)); s.appendChild(document.createTextNode(KR.TIPO_LABEL[t])); leyenda.appendChild(s);
      });
      leyenda.appendChild(el("span", "", "Tamaño = conexiones"));
      var anillo = el("span"); anillo.appendChild(el("i", "kr-anillo")); anillo.appendChild(document.createTextNode("En tu shortlist"));
      leyenda.appendChild(anillo);
      medidor = el("span", "kr-medidor");
      leyenda.appendChild(medidor);
    }
    var medidor = null;
    function pintarMedidor() {
      if (!medidor || !tiempos.length) return;
      var prom = tiempos.reduce(function (a, b) { return a + b; }, 0) / tiempos.length;
      medidor.textContent = KR.miles(grafo.nodos.length) + " nodos · " + etiquetasDibujadas + " nombres · " + prom.toFixed(1).replace(".", ",") + " ms por cuadro";
    }

    // ---------------------------------------------------------------- flujo
    function escribirHash() { KR.hash.escribir(filtros, { d: sel && profundidad === 2 ? "2" : null }); }
    function cambioFiltros() {
      avisoFiltros = "";
      recalcular();
      if (sel && !visibles[sel]) seleccionar(null);
      pintarPanel(); pintarFoco(); escribirHash(); lz.dibujar();
    }
    function restablecer(inmediato) {
      var dest = lz.encuadre(grafo.caja, 50);
      lz.animarA(dest, 380, inmediato, KR.easeInOut);
    }

    KR.autocompletar(input, {
      etiqueta: function (n) { return KR.pasa(n, filtros) ? "" : "oculto por filtros"; },
      alElegir: function (n) {
        if (!KR.pasa(n, filtros)) {
          filtros = KR.filtrosVacios(); recalcular(); pintarPanel(); escribirHash();
          avisoFiltros = "Se quitaron los filtros para mostrar a " + KR.etiquetaCorta(n) + ".";
        }
        seleccionar(n.id, true);
        input.blur();
      }
    });

    var mapaZoom = KR.botonesZoom(lz, restablecer);
    mapa.appendChild(mapaZoom);

    function tecla(ev) {
      if (ev.key !== "Escape" || /^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) return;
      if (drawer.classList.contains("abierto") || sel || grupoResaltado) { avisoFiltros = ""; seleccionar(null); }
    }
    document.addEventListener("keydown", tecla);
    limpiezas.push(function () { document.removeEventListener("keydown", tecla); });
    limpiezas.push(KR.shortlist.escuchar(function () { pintarPanel(); lz.dibujar(); }));
    limpiezas.push(KR.alCambiarTema(function () { C = KR.colores(); lz.dibujar(); }));

    recalcular();
    pintarPanel();
    pintarLeyenda();
    requestAnimationFrame(function () {
      restablecer(true);
      if (h0.f && grafo.byId[h0.f]) seleccionar(h0.f, true);
      if (canvas.animate) canvas.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
    });

    return function () { limpiezas.forEach(function (fn) { fn(); }); };
  }

  window.VARIANTES = window.VARIANTES || [];
  window.VARIANTES[0] = { nombre: "Explorador", montar: montar };
})();
