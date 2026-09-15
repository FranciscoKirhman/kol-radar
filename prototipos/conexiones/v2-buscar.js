/* Prototipo 2 — «Buscar primero».
 * Eje: MODELO DE INTERACCIÓN. No hay mapa completo: se parte de una ficha y se dibuja solo su
 * vecindario (1 o 2 saltos), como el grafo local de Quartz o "click to expand" de force-graph.
 * La escala no depende del total: con 700 o con 70.000 fichas se dibuja lo mismo. Los grupos
 * grandes se resumen en un nodo "+N" que se abre al tocarlo. SVG, porque lo dibujado es poco. */
(function () {
  "use strict";
  var KR = window.KR;
  var NS = "http://www.w3.org/2000/svg";
  var LIM1 = 18, LIM2 = 5;

  function montar(stage) {
    var el = KR.el, g = KR.datos.grafo;
    var h0 = KR.hash.leer();
    var filtros = KR.hash.aFiltros(h0);
    var profundidad = h0.d === "2" ? 2 : 1;
    var modo = "inicio", centro = null, rastro = [], abiertos = {}, areaInicio = null, tabInicio = "persona";
    var limpiezas = [];
    var posAnterior = {}, animRaf = null;
    var vb = { x: -400, y: -300, w: 800, h: 600 }, vbAnim = null;
    var hoverId = null, resaltadoArista = null;
    var layoutActual = null;

    var raiz = el("div", "variante v2");
    var top = el("header", "kr-top");
    var marca = el("div", "kr-marca");
    marca.appendChild(el("span", "kr-marca-nombre", "KOL Radar"));
    marca.appendChild(el("span", "kr-marca-tag", "oncología · Chile"));
    top.appendChild(marca);
    var buscarTop = el("div", "kr-buscar v2-buscar-top");
    var inputTop = el("input"); inputTop.type = "search"; inputTop.placeholder = "Buscar otra ficha…";
    inputTop.setAttribute("aria-label", "Buscar ficha");
    buscarTop.appendChild(inputTop);
    top.appendChild(buscarTop);
    top.appendChild(el("span", "kr-top-sep"));
    var compartir = KR.botonCompartir(function () {
      return { filtros: filtros, ficha: centro && centro !== "@shortlist" ? g.byId[centro] : null, extra: { d: profundidad === 2 ? "2" : null } };
    });
    limpiezas.push(compartir.destruir);
    top.appendChild(compartir.el);
    raiz.appendChild(top);
    raiz.appendChild(KR.lineaBeta());
    var cuerpo = el("div", "v2-cuerpo");
    raiz.appendChild(cuerpo);
    stage.appendChild(raiz);

    // ================================================================ INICIO
    function pintarInicio(enfocar) {
      modo = "inicio"; centro = null; rastro = [];
      buscarTop.hidden = true;
      cuerpo.innerHTML = "";
      var ini = el("div", "v2-inicio");
      var col = el("div", "v2-inicio-col");
      col.appendChild(el("h1", "v2-titulo", "¿Por quién o por qué querés empezar?"));
      col.appendChild(el("p", "v2-bajada", "Buscá una persona, institución o ensayo y mirá su red directa, con la fuente de cada conexión."));
      var b = el("div", "kr-buscar v2-buscar-grande");
      var inp = el("input"); inp.type = "search"; inp.placeholder = "Ej.: Burotto, FALP, pembrolizumab, NCT0689…";
      inp.setAttribute("aria-label", "Buscar ficha");
      b.appendChild(inp);
      col.appendChild(b);
      KR.autocompletar(inp, { max: 8, alElegir: function (n) { explorar(n.id, true); } });

      var c = KR.conteos(g, KR.filtrosVacios());
      col.appendChild(el("p", "v2-sec", "O recorré por área"));
      var chips = el("div", "v2-chips");
      c.areas.slice(0, 12).forEach(function (a) {
        var ch = el("button", "v2-chip"); ch.type = "button";
        ch.setAttribute("aria-pressed", String(areaInicio === a.area));
        ch.appendChild(document.createTextNode(a.area.replace(/^cáncer (de )?/, "").replace(/^./, function (x) { return x.toUpperCase(); })));
        ch.appendChild(el("span", "v2-chip-num", KR.miles(a.total)));
        ch.addEventListener("click", function () { areaInicio = areaInicio === a.area ? null : a.area; pintarInicio(); });
        chips.appendChild(ch);
      });
      col.appendChild(chips);

      var pool = g.nodos.filter(function (n) { return !areaInicio || n._area === areaInicio; });
      var tabs = el("div", "kr-seg v2-tabs"); tabs.setAttribute("role", "tablist");
      KR.TIPOS.forEach(function (t) {
        var cuantos = pool.filter(function (n) { return n.tipo === t; }).length;
        var tb = el("button", "kr-seg-btn", KR.TIPO_PLURAL[t] + " " + KR.miles(cuantos)); tb.type = "button";
        tb.setAttribute("aria-pressed", String(tabInicio === t));
        tb.addEventListener("click", function () { tabInicio = t; pintarInicio(); });
        tabs.appendChild(tb);
      });
      col.appendChild(tabs);
      var lista = el("ul", "v2-lista-inicio");
      var items = pool.filter(function (n) { return n.tipo === tabInicio; })
        .sort(function (x, y) { return x.nombre.localeCompare(y.nombre, "es"); });
      items.slice(0, 80).forEach(function (n) {
        var li = el("li");
        var bt = el("button", "v2-item"); bt.type = "button";
        bt.appendChild(KR.formaSVG(n.tipo, 10));
        var tx = el("span", "v2-item-txt");
        tx.appendChild(el("span", "v2-item-nombre", n.nombre));
        if (n.subtitulo) tx.appendChild(el("span", "v2-item-sub", n.subtitulo));
        bt.appendChild(tx);
        bt.appendChild(el("span", "v2-item-num", g.adj[n.id].length + " con."));
        bt.addEventListener("click", function () { explorar(n.id, true); });
        li.appendChild(bt); lista.appendChild(li);
      });
      if (items.length > 80) lista.appendChild(el("li", "kr-nota", "+" + (items.length - 80) + " más — usá la búsqueda"));
      col.appendChild(lista);
      ini.appendChild(col);

      var lado = el("aside", "v2-inicio-lado");
      lado.appendChild(el("p", "v2-sec", "Tu shortlist"));
      lado.appendChild(KR.panelEnComun({
        ejemplo: true,
        alNavegar: function (id) { explorar(id, true); },
        alMostrar: function () { explorarShortlist(); }
      }));
      var nota = el("div", "v2-escala");
      nota.appendChild(el("strong", "", "Por qué esta vista escala"));
      nota.appendChild(el("p", "", "No se dibuja el mapa entero: solo el vecindario de lo que elijas. Los grupos grandes se " +
        "resumen en un nodo «+N» que se abre al tocarlo. Con " + KR.miles(g.nodos.length) + " fichas o con 70.000, se dibuja lo mismo."));
      lado.appendChild(nota);
      ini.appendChild(lado);
      cuerpo.appendChild(ini);
      KR.hash.escribir(filtros, {});
      if (!KR.reducirMovimiento() && ini.animate) {
        ini.animate([{ opacity: 0, transform: "translateY(6px)" }, { opacity: 1, transform: "none" }], { duration: 260, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
      }
      if (enfocar) requestAnimationFrame(function () { inp.focus(); });
    }

    // ================================================================ EXPLORAR
    var lista, lienzoWrap, svg, gAristas, gNodos, fichaCol, migas, controles, contador, tooltip;

    function armarExplorar() {
      cuerpo.innerHTML = "";
      buscarTop.hidden = false;
      var ex = el("div", "v2-explorar");
      lista = el("aside", "v2-lista");
      var centroCol = el("section", "v2-centro");
      migas = el("nav", "v2-migas"); migas.setAttribute("aria-label", "Recorrido");
      controles = el("div", "v2-controles");
      centroCol.appendChild(migas);
      centroCol.appendChild(controles);
      lienzoWrap = el("div", "v2-lienzo");
      svg = document.createElementNS(NS, "svg");
      svg.setAttribute("class", "v2-svg");
      gAristas = document.createElementNS(NS, "g");
      gNodos = document.createElementNS(NS, "g");
      svg.appendChild(gAristas); svg.appendChild(gNodos);
      lienzoWrap.appendChild(svg);
      contador = el("div", "v2-contador");
      lienzoWrap.appendChild(contador);
      tooltip = el("div", "kr-tooltip"); tooltip.hidden = true;
      lienzoWrap.appendChild(tooltip);
      var zoom = el("div", "kr-zoom");
      [["+", "Acercar", 0.7], ["−", "Alejar", 1.4], ["⟲", "Encuadrar", 0]].forEach(function (d) {
        var bt = el("button", "kr-zoom-btn", d[0]); bt.type = "button"; bt.setAttribute("aria-label", d[1]); bt.title = d[1];
        bt.addEventListener("click", function (ev) {
          if (d[2]) zoomVB(d[2], vbBase().x + vbBase().w / 2, vbBase().y + vbBase().h / 2, ev.detail === 0);
          else encuadrar(ev.detail === 0);
        });
        zoom.appendChild(bt);
      });
      lienzoWrap.appendChild(zoom);
      centroCol.appendChild(lienzoWrap);
      fichaCol = el("aside", "v2-ficha");
      ex.appendChild(lista); ex.appendChild(centroCol); ex.appendChild(fichaCol);
      cuerpo.appendChild(ex);
      conectarCamara();
      posAnterior = {};
    }
    var roActual = null;
    function observarTamano() {
      if (roActual) roActual.disconnect();
      roActual = new ResizeObserver(function () { encuadrar(true); });
      roActual.observe(lienzoWrap);
    }

    function explorar(id, nuevo) {
      if (modo !== "explorar") { armarExplorar(); modo = "explorar"; }
      if (nuevo) {
        var i = rastro.indexOf(id);
        if (i !== -1) rastro = rastro.slice(0, i + 1); else rastro.push(id);
      }
      if (centro !== id) abiertos = {};
      centro = id;
      inputTop.value = "";
      pintarExplorar(true);
    }
    function explorarShortlist() {
      if (modo !== "explorar") { armarExplorar(); modo = "explorar"; }
      centro = "@shortlist";
      if (rastro[rastro.length - 1] !== "@shortlist") rastro.push("@shortlist");
      pintarExplorar(true);
    }

    // ---------------------------------------------------------------- layout radial
    function pasaVecino(n) { return KR.pasa(n, filtros); }

    function layoutEgo() {
      var c = g.byId[centro];
      var dist = KR.vecindario(g, centro, profundidad, function (n) { return n.id === centro || pasaVecino(n); });
      var nodos = [], pos = {}, agregados = [];
      pos[centro] = { x: 0, y: 0, nivel: 0 };
      nodos.push({ id: centro, n: c, x: 0, y: 0, nivel: 0 });
      var anillo1 = g.adj[centro].map(function (a) { return a.otro; })
        .filter(function (id, i, arr) { return arr.indexOf(id) === i && dist[id] === 1; });
      var orden = { persona: 0, institucion: 1, ensayo_clinico: 2 };
      function reciente(a, b) { return (g.byId[b]._anio || 0) - (g.byId[a]._anio || 0) || g.byId[a].nombre.localeCompare(g.byId[b].nombre, "es"); }
      var grupos = KR.TIPOS.map(function (t) {
        var ids = anillo1.filter(function (id) { return g.byId[id].tipo === t; }).sort(reciente);
        var lim = abiertos["1:" + t] ? 120 : LIM1;
        var visibles = ids.length > lim ? ids.slice(0, lim - 1) : ids;
        return { tipo: t, ids: ids, visibles: visibles, resto: ids.length - visibles.length };
      }).filter(function (gr) { return gr.ids.length; });
      var slots = [];
      grupos.forEach(function (gr) {
        gr.visibles.forEach(function (id) { slots.push({ id: id }); });
        if (gr.resto > 0) slots.push({ agregado: "1:" + gr.tipo, tipo: gr.tipo, cuenta: gr.resto });
        slots.push({ hueco: true }); slots.push({ hueco: true });
      });
      if (slots.length) { slots.pop(); slots.pop(); }
      var total1 = slots.length || 1;
      var R1 = Math.max(160, (total1 * 20) / (2 * Math.PI));
      slots.forEach(function (s, i) {
        var ang = -Math.PI / 2 + (i / total1) * Math.PI * 2;
        s.ang = ang;
        if (s.hueco) return;
        var x = Math.cos(ang) * R1, y = Math.sin(ang) * R1;
        if (s.agregado) { agregados.push({ clave: s.agregado, tipo: s.tipo, cuenta: s.cuenta, x: x, y: y, padre: centro, nivel: 1, ang: ang }); return; }
        pos[s.id] = { x: x, y: y, nivel: 1, ang: ang };
        nodos.push({ id: s.id, n: g.byId[s.id], x: x, y: y, nivel: 1, ang: ang });
      });
      if (profundidad === 2) {
        var R2 = R1 + 170, asignado = {};
        var paso1 = (Math.PI * 2) / total1;
        slots.forEach(function (s) {
          if (!s.id) return;
          var hijos = g.adj[s.id].map(function (a) { return a.otro; })
            .filter(function (id, i, arr) { return arr.indexOf(id) === i && dist[id] === 2 && !asignado[id]; })
            .sort(function (a, b) { return orden[g.byId[a].tipo] - orden[g.byId[b].tipo] || reciente(a, b); });
          if (!hijos.length) return;
          hijos.forEach(function (id) { asignado[id] = true; });
          var lim = abiertos["2:" + s.id] ? 40 : LIM2;
          var vis = hijos.length > lim ? hijos.slice(0, lim - 1) : hijos;
          var cant = vis.length + (hijos.length > vis.length ? 1 : 0);
          var abanico = Math.min(paso1 * 0.9 * Math.max(1, cant / 2), Math.PI / 3);
          vis.concat(hijos.length > vis.length ? ["+"] : []).forEach(function (id, j) {
            var ang = s.ang + (cant === 1 ? 0 : (j / (cant - 1) - 0.5) * abanico);
            var rr = R2 + (j % 2) * 34;
            var x = Math.cos(ang) * rr, y = Math.sin(ang) * rr;
            if (id === "+") { agregados.push({ clave: "2:" + s.id, cuenta: hijos.length - vis.length, x: x, y: y, padre: s.id, nivel: 2, ang: ang }); return; }
            pos[id] = { x: x, y: y, nivel: 2, ang: ang, padre: s.id };
            nodos.push({ id: id, n: g.byId[id], x: x, y: y, nivel: 2, ang: ang, padre: s.id });
          });
        });
      }
      var aristas = [];
      var puestos = {};
      nodos.forEach(function (x) { puestos[x.id] = true; });
      g.vinculos.forEach(function (v) {
        if (puestos[v.origen] && puestos[v.destino]) {
          var na = pos[v.origen].nivel, nb = pos[v.destino].nivel;
          if (Math.abs(na - nb) === 1 || (na === nb && na > 0)) aristas.push(v);
        }
      });
      agregados.forEach(function (a) { aristas.push({ agregado: a.clave, origen: a.padre }); });
      var totalVecindario = Object.keys(dist).length - 1;
      return { nodos: nodos, pos: pos, agregados: agregados, aristas: aristas, dist: dist, total: totalVecindario, R: profundidad === 2 ? R1 + 230 : R1 + 60 };
    }

    function layoutShortlist() {
      var ids = KR.shortlist.lista(), r = KR.enComun(ids);
      var nodos = [], pos = {}, R = Math.max(170, ids.length * 60);
      ids.forEach(function (id, i) {
        var ang = -Math.PI / 2 + (i / ids.length) * Math.PI * 2;
        var x = Math.cos(ang) * R, y = Math.sin(ang) * R;
        pos[id] = { x: x, y: y, nivel: 0 };
        nodos.push({ id: id, n: g.byId[id], x: x, y: y, nivel: 0 });
      });
      var comp = r.compartidos.filter(function (c) { return pasaVecino(c.n); }).slice(0, 60);
      comp.forEach(function (c, i) {
        var sx = 0, sy = 0;
        c.quienes.forEach(function (id) { sx += pos[id].x; sy += pos[id].y; });
        var ang = i * 2.39996, jit = 18 + (i % 7) * 11;
        var x = sx / c.quienes.length * 0.45 + Math.cos(ang) * jit, y = sy / c.quienes.length * 0.45 + Math.sin(ang) * jit;
        pos[c.n.id] = { x: x, y: y, nivel: 1 };
        nodos.push({ id: c.n.id, n: c.n, x: x, y: y, nivel: 1 });
      });
      var aristas = g.vinculos.filter(function (v) { return pos[v.origen] && pos[v.destino] && (pos[v.origen].nivel !== pos[v.destino].nivel || pos[v.origen].nivel === 0); });
      return { nodos: nodos, pos: pos, agregados: [], aristas: aristas, dist: {}, total: comp.length + ids.length, R: R + 80, shortlist: true, extra: r.compartidos.length - comp.length };
    }

    // ---------------------------------------------------------------- pintar
    function pintarExplorar(animar) {
      if (centro === "@shortlist" && KR.shortlist.lista().length < 2) { pintarInicio(); return; }
      limpiezasVista.forEach(function (fn) { fn(); });
      limpiezasVista = [];
      var L = centro === "@shortlist" ? layoutShortlist() : layoutEgo();
      layoutActual = L;
      pintarMigas(); pintarControles(L); pintarLista(L); pintarFicha();
      dibujarGrafo(L, animar);
      encuadrar(!animar, L);
      KR.hash.escribir(filtros, { d: profundidad === 2 ? "2" : null });
    }

    function pintarMigas() {
      migas.innerHTML = "";
      var ini = el("button", "v2-miga", "Inicio"); ini.type = "button";
      ini.addEventListener("click", pintarInicio);
      migas.appendChild(ini);
      rastro.forEach(function (id, i) {
        migas.appendChild(el("span", "v2-miga-sep", "›"));
        var nombre = id === "@shortlist" ? "Tu shortlist" : KR.etiquetaCorta(g.byId[id]);
        var b = el("button", "v2-miga" + (i === rastro.length - 1 ? " actual" : ""), nombre); b.type = "button";
        if (i === rastro.length - 1) b.setAttribute("aria-current", "page");
        b.addEventListener("click", function () { if (id === "@shortlist") explorarShortlist(); else explorar(id, true); });
        migas.appendChild(b);
      });
    }

    function pintarControles(L) {
      controles.innerHTML = "";
      if (!L.shortlist) {
        var seg = el("div", "kr-seg"); seg.setAttribute("role", "group"); seg.setAttribute("aria-label", "Distancia");
        [1, 2].forEach(function (d) {
          var b = el("button", "kr-seg-btn", d === 1 ? "Conexiones directas" : "A 2 saltos"); b.type = "button";
          b.setAttribute("aria-pressed", String(profundidad === d));
          b.addEventListener("click", function () { profundidad = d; abiertos = {}; pintarExplorar(true); });
          seg.appendChild(b);
        });
        controles.appendChild(seg);
      }
      var univ = L.shortlist ? L.nodos.map(function (x) { return x.n; })
        : Object.keys(KR.vecindario(g, centro, profundidad)).map(function (id) { return g.byId[id]; });
      var c = KR.conteos(g, filtros, univ);
      KR.TIPOS.forEach(function (t) {
        var b = el("button", "v2-tipo"); b.type = "button";
        b.setAttribute("aria-pressed", String(filtros.tipos[t]));
        b.appendChild(KR.formaSVG(t, 9));
        b.appendChild(document.createTextNode(KR.TIPO_PLURAL[t]));
        b.appendChild(el("span", "v2-chip-num", KR.miles(c.tipos[t].total)));
        b.addEventListener("click", function () { filtros.tipos[t] = !filtros.tipos[t]; pintarExplorar(true); });
        controles.appendChild(b);
      });
      var anios = el("button", "v2-tipo", filtros.anios ? "Años " + filtros.anios.join("–") : "Años"); anios.type = "button";
      var contHist = el("div");
      contHist.appendChild(el("p", "kr-compartir-titulo", "Año del hecho más reciente"));
      contHist.appendChild(el("p", "kr-nota", "Dentro de este vecindario."));
      contHist.appendChild(KR.histograma({ barras: c.barras, rango: filtros.anios, sinFecha: c.sinFecha,
        alCambiar: function (r) { filtros.anios = r; pop.cerrar(); pintarExplorar(true); } }));
      var pop = KR.popover(anios, contHist, { alinear: "izquierda" });
      limpiezasVista.push(pop.destruir);
      controles.appendChild(anios);
    }
    var limpiezasVista = [];

    function pintarLista(L) {
      lista.innerHTML = "";
      var titulo = el("div", "v2-lista-cab");
      titulo.appendChild(el("strong", "", L.shortlist ? "Lo que comparten" : profundidad === 2 ? "A 1 y 2 saltos" : "Conexiones directas"));
      titulo.appendChild(el("span", "kr-nota", KR.miles(L.total) + " fichas"));
      lista.appendChild(titulo);
      var porTipo = {};
      L.nodos.forEach(function (x) { if (x.nivel > 0 || L.shortlist) (porTipo[x.n.tipo] = porTipo[x.n.tipo] || []).push(x); });
      KR.TIPOS.forEach(function (t) {
        var arr = porTipo[t];
        if (!arr) return;
        lista.appendChild(el("p", "v2-lista-grupo", KR.TIPO_PLURAL[t] + " · " + arr.length));
        var ul = el("ul", "v2-lista-ul");
        arr.forEach(function (x) {
          var li = el("li");
          var b = el("button", "v2-fila"); b.type = "button"; b.dataset.id = x.id;
          b.appendChild(KR.formaSVG(t, 9));
          b.appendChild(el("span", "v2-fila-nombre", x.n.nombre));
          if (x.nivel === 2) b.appendChild(el("span", "v2-fila-nivel", "2°"));
          b.addEventListener("mouseenter", function () { resaltar(x.id); });
          b.addEventListener("mouseleave", function () { resaltar(null); });
          b.addEventListener("focus", function () { resaltar(x.id); });
          b.addEventListener("blur", function () { resaltar(null); });
          b.addEventListener("click", function () { explorar(x.id, true); });
          li.appendChild(b); ul.appendChild(li);
        });
        lista.appendChild(ul);
      });
      L.agregados.forEach(function (a) {
        var b = el("button", "kr-btn kr-btn-chico v2-lista-mas", "+" + a.cuenta + " " + (a.tipo ? KR.TIPO_PLURAL[a.tipo].toLowerCase() : "más") + " sin mostrar"); b.type = "button";
        b.addEventListener("click", function () { abiertos[a.clave] = true; pintarExplorar(true); });
        lista.appendChild(b);
      });
    }

    function pintarFicha() {
      if (fichaCol.firstChild && fichaCol.firstChild._destruir) fichaCol.firstChild._destruir();
      fichaCol.innerHTML = "";
      if (centro === "@shortlist") {
        fichaCol.appendChild(el("h2", "kr-ficha-nombre", "Tu shortlist"));
        fichaCol.appendChild(KR.panelEnComun({ alNavegar: function (id) { explorar(id, true); } }));
        return;
      }
      var f = KR.ficha(g.byId[centro], {
        alNavegar: function (id) { explorar(id, true); },
        alResaltar: function (id, v) { resaltadoArista = v || null; resaltar(id); }
      });
      fichaCol.appendChild(f);
      fichaCol.scrollTop = 0;
    }

    function formaNodo(tipo, r) {
      var s;
      if (tipo === "persona") s = KR.svg("circle", { r: r });
      else if (tipo === "institucion") s = KR.svg("rect", { x: -r * 0.9, y: -r * 0.9, width: r * 1.8, height: r * 1.8, rx: 1.5 });
      else s = KR.svg("polygon", { points: "0," + (-r * 1.15) + " " + r + "," + (r * 0.8) + " " + (-r) + "," + (r * 0.8) });
      s.setAttribute("fill", "var(--" + KR.TIPO_VAR[tipo] + ")");
      s.setAttribute("class", "v2-forma");
      return s;
    }

    function dibujarGrafo(L, animar) {
      gAristas.innerHTML = ""; gNodos.innerHTML = "";
      var anim = animar && !KR.reducirMovimiento();
      var desde = {};
      L.nodos.forEach(function (x) {
        var prev = posAnterior[x.id];
        // Lo que ya estaba en pantalla viaja a su lugar nuevo; lo nuevo aparece desde su padre.
        desde[x.id] = prev ? { x: prev.x, y: prev.y, nuevo: false }
          : { x: (L.pos[x.padre] || L.pos[centro] || { x: 0 }).x || 0, y: (L.pos[x.padre] || L.pos[centro] || { y: 0 }).y || 0, nuevo: true };
      });
      var elems = {};
      L.aristas.forEach(function (v) {
        var ln = KR.svg("line", { "class": "v2-arista" + (v.agregado ? " agregada" : "") });
        ln._v = v;
        gAristas.appendChild(ln);
      });
      L.nodos.forEach(function (x) {
        var n = x.n, r = x.nivel === 0 ? 11 : n.tipo === "ensayo_clinico" ? 5.5 : 7;
        var gr = KR.svg("g", { "class": "v2-nodo nivel-" + x.nivel + (KR.shortlist.tiene(x.id) ? " en-sl" : ""), tabindex: "0", role: "button" });
        gr.setAttribute("aria-label", n.nombre + ", " + KR.TIPO_LABEL[n.tipo]);
        gr.dataset.id = x.id;
        if (KR.shortlist.tiene(x.id)) gr.appendChild(KR.svg("circle", { r: r + 4.5, "class": "v2-anillo" }));
        gr.appendChild(formaNodo(n.tipo, r));
        var t = KR.svg("text", { "class": "v2-etiqueta", dy: "0.35em" });
        // Etiquetas a lo largo del radio, como un árbol radial: horizontales se pisaban arriba y
        // abajo del anillo apenas había más de una docena de vecinos. Del lado izquierdo se giran
        // 180° para que nunca queden de cabeza. El nombre completo va en el tooltip.
        var derecha = x.nivel === 0 || Math.cos(x.ang || 0) >= 0;
        if (x.nivel === 0) { t.setAttribute("y", r + 14); t.setAttribute("text-anchor", "middle"); t.setAttribute("dy", "0.7em"); }
        else {
          var grados = (x.ang || 0) * 180 / Math.PI + (derecha ? 0 : 180);
          t.setAttribute("x", derecha ? r + 5 : -(r + 5));
          t.setAttribute("text-anchor", derecha ? "start" : "end");
          t.setAttribute("transform", "rotate(" + grados.toFixed(1) + ")");
        }
        var corto = KR.etiquetaCorta(n);
        t.textContent = x.nivel === 0 ? n.nombre : corto.length > 30 ? corto.slice(0, 28).trim() + "…" : corto;
        gr.appendChild(t);
        gr.addEventListener("mouseenter", function (ev) { resaltar(x.id); mostrarTooltip(ev, n); });
        gr.addEventListener("mouseleave", function () { resaltar(null); tooltip.hidden = true; });
        gr.addEventListener("focus", function () { resaltar(x.id); });
        gr.addEventListener("blur", function () { resaltar(null); });
        function activar() { if (x.nivel === 0 && !L.shortlist) return; explorar(x.id, true); }
        gr.addEventListener("click", activar);
        gr.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); activar(); } });
        gNodos.appendChild(gr);
        elems[x.id] = { g: gr, x: x };
      });
      L.agregados.forEach(function (a) {
        var gr = KR.svg("g", { "class": "v2-agregado", tabindex: "0", role: "button" });
        var texto = "+" + KR.miles(a.cuenta) + (a.tipo ? " " + KR.TIPO_PLURAL[a.tipo].toLowerCase() : "");
        gr.setAttribute("aria-label", "Mostrar " + texto);
        var ancho = 14 + texto.length * 6.4;
        gr.appendChild(KR.svg("rect", { x: -ancho / 2, y: -11, width: ancho, height: 22, rx: 11 }));
        var t = KR.svg("text", { "text-anchor": "middle", dy: "0.35em" }); t.textContent = texto;
        gr.appendChild(t);
        function abrir() { abiertos[a.clave] = true; pintarExplorar(true); }
        gr.addEventListener("click", abrir);
        gr.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); abrir(); } });
        gNodos.appendChild(gr);
        elems["@" + a.clave] = { g: gr, x: a };
        desde["@" + a.clave] = { x: (L.pos[a.padre] || { x: 0 }).x, y: (L.pos[a.padre] || { y: 0 }).y, nuevo: true };
      });
      contador.textContent = "Dibujadas " + KR.miles(L.nodos.length + L.agregados.length) + " de " + KR.miles(g.nodos.length) + " fichas" +
        (L.agregados.length ? " · " + L.agregados.length + (L.agregados.length === 1 ? " grupo resumido" : " grupos resumidos") : "");
      // Los nombres del anillo exterior se esconden solo si son muchos; con pocos, se leen de una.
      svg.classList.toggle("muchos2", L.nodos.filter(function (x) { return x.nivel === 2; }).length > 24);

      function colocar(p) {
        Object.keys(elems).forEach(function (k) {
          var e = elems[k], d = desde[k], x = d.x + (e.x.x - d.x) * p, y = d.y + (e.x.y - d.y) * p;
          e.cx = x; e.cy = y;
          e.g.setAttribute("transform", "translate(" + x.toFixed(1) + "," + y.toFixed(1) + ")");
          if (d.nuevo) e.g.style.opacity = Math.min(1, p * 1.6);
        });
        Array.prototype.forEach.call(gAristas.childNodes, function (ln) {
          var v = ln._v, a = elems[v.origen], b = v.agregado ? elems["@" + v.agregado] : elems[v.destino];
          if (!a || !b) return;
          ln.setAttribute("x1", a.cx.toFixed(1)); ln.setAttribute("y1", a.cy.toFixed(1));
          ln.setAttribute("x2", b.cx.toFixed(1)); ln.setAttribute("y2", b.cy.toFixed(1));
          ln.style.opacity = desde[v.origen] && desde[v.origen].nuevo || (b && desde[v.agregado ? "@" + v.agregado : v.destino].nuevo) ? Math.min(1, p * 1.6) : "";
        });
      }
      if (animRaf) cancelAnimationFrame(animRaf);
      if (!anim) colocar(1);
      else {
        var t0 = null;
        colocar(0);
        var paso = function (t) {
          if (t0 === null) t0 = t;
          var p = Math.min(1, (t - t0) / 340);
          colocar(KR.easeInOut(p));
          if (p < 1) animRaf = requestAnimationFrame(paso); else animRaf = null;
        };
        animRaf = requestAnimationFrame(paso);
      }
      posAnterior = {};
      L.nodos.forEach(function (x) { posAnterior[x.id] = { x: x.x, y: x.y }; });
      pintarEtiquetasPorZoom();
    }

    function mostrarTooltip(ev, n) {
      var r = lienzoWrap.getBoundingClientRect();
      tooltip.innerHTML = "";
      tooltip.appendChild(el("div", "kr-tooltip-tit", n.nombre));
      tooltip.appendChild(el("div", "kr-tooltip-sub", KR.TIPO_LABEL[n.tipo] + " · " + g.adj[n.id].length + " conexiones · click para centrar"));
      tooltip.hidden = false;
      tooltip.style.transform = "translate(" + Math.min(ev.clientX - r.left + 14, r.width - 290) + "px," + (ev.clientY - r.top + 14) + "px)";
    }

    // Resaltar: como el demo de sigma.js, las aristas ajenas desaparecen y las propias se colorean.
    function resaltar(id) {
      hoverId = id;
      svg.classList.toggle("resaltando", !!id);
      Array.prototype.forEach.call(gAristas.childNodes, function (ln) {
        var v = ln._v;
        var on = id && (v.origen === id || v.destino === id);
        if (resaltadoArista && v === resaltadoArista) on = true;
        ln.classList.toggle("on", !!on);
        ln.style.stroke = on ? "var(--" + KR.TIPO_VAR[g.byId[id] ? g.byId[id].tipo : "persona"] + ")" : "";
      });
      Array.prototype.forEach.call(gNodos.childNodes, function (nd) {
        var nid = nd.dataset.id;
        var vec = id && nid && (nid === id || g.adj[id].some(function (a) { return a.otro === nid; }));
        nd.classList.toggle("on", !!vec);
      });
      Array.prototype.forEach.call(lista.querySelectorAll(".v2-fila"), function (b) { b.classList.toggle("on", b.dataset.id === id); });
      if (!id) resaltadoArista = null;
    }

    // ---------------------------------------------------------------- cámara (viewBox)
    function aplicarVB() { svg.setAttribute("viewBox", vb.x + " " + vb.y + " " + vb.w + " " + vb.h); pintarEtiquetasPorZoom(); }
    function vbBase() { return vbAnim ? vbAnim.meta : vb; }
    function animarVB(meta, dur, inmediato) {
      if (vbAnim) { cancelAnimationFrame(vbAnim.raf); vbAnim = null; }
      if (inmediato || KR.reducirMovimiento()) { vb = meta; aplicarVB(); return; }
      var d = { x: vb.x, y: vb.y, w: vb.w, h: vb.h }, t0 = null;
      vbAnim = { meta: meta };
      var paso = function (t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = KR.easeInOut(p);
        vb = { x: d.x + (meta.x - d.x) * e, y: d.y + (meta.y - d.y) * e, w: d.w + (meta.w - d.w) * e, h: d.h + (meta.h - d.h) * e };
        aplicarVB();
        if (p < 1) vbAnim.raf = requestAnimationFrame(paso); else vbAnim = null;
      };
      vbAnim.raf = requestAnimationFrame(paso);
    }
    function encuadrar(inmediato, L) {
      L = L || layoutActual;
      if (!L) return;
      var r = lienzoWrap.getBoundingClientRect();
      var ratio = r.width > 40 && r.height > 40 ? r.height / r.width : 0.75;
      var R = L.R + 185, w = R * 2, h = R * 2;   // margen para etiquetas radiales de ~30 caracteres
      if (h / w > ratio) w = h / ratio; else h = w * ratio;
      animarVB({ x: -w / 2, y: -h / 2, w: w, h: h }, 340, inmediato);
    }
    function zoomVB(f, cx, cy, inmediato) {
      var b = vbBase(), w = Math.max(160, Math.min(8000, b.w * f)), h = w * (b.h / b.w);
      animarVB({ x: cx - (cx - b.x) * (w / b.w), y: cy - (cy - b.y) * (h / b.h), w: w, h: h }, 240, inmediato);
    }
    // Etiquetas por zoom: a 2 saltos, las del anillo exterior aparecen recién al acercarse.
    function pintarEtiquetasPorZoom() {
      if (!svg || !layoutActual) return;
      var r = lienzoWrap.getBoundingClientRect();
      var escala = r.width / vb.w;
      svg.classList.toggle("cerca", escala > 0.9);
      svg.classList.toggle("lejos", escala < 0.45);
    }
    function conectarCamara() {
      var arr = null;
      svg.addEventListener("wheel", function (ev) {
        ev.preventDefault();
        if (vbAnim) { cancelAnimationFrame(vbAnim.raf); vbAnim = null; }
        var r = svg.getBoundingClientRect();
        var mx = vb.x + ((ev.clientX - r.left) / r.width) * vb.w, my = vb.y + ((ev.clientY - r.top) / r.height) * vb.h;
        var f = Math.exp(ev.deltaY * 0.0022), w = Math.max(160, Math.min(8000, vb.w * f)), h = w * (vb.h / vb.w);
        vb = { x: mx - (mx - vb.x) * (w / vb.w), y: my - (my - vb.y) * (h / vb.h), w: w, h: h };
        aplicarVB();
      }, { passive: false });
      svg.addEventListener("pointerdown", function (ev) {
        if (ev.target.closest(".v2-nodo, .v2-agregado")) return;
        if (vbAnim) { cancelAnimationFrame(vbAnim.raf); vbAnim = null; }
        arr = { x: ev.clientX, y: ev.clientY, vx: vb.x, vy: vb.y };
        svg.setPointerCapture(ev.pointerId);
        svg.classList.add("arrastrando");
      });
      svg.addEventListener("pointermove", function (ev) {
        if (!arr) return;
        var r = svg.getBoundingClientRect(), s = vb.w / r.width;
        vb = { x: arr.vx - (ev.clientX - arr.x) * s, y: arr.vy - (ev.clientY - arr.y) * s, w: vb.w, h: vb.h };
        aplicarVB();
      });
      ["pointerup", "pointercancel"].forEach(function (t) {
        svg.addEventListener(t, function () { arr = null; svg.classList.remove("arrastrando"); });
      });
      observarTamano();
    }
    limpiezas.push(function () { if (roActual) roActual.disconnect(); });

    KR.autocompletar(inputTop, { alElegir: function (n) { explorar(n.id, true); inputTop.blur(); } });

    function tecla(ev) {
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) return;
      if (ev.key === "Backspace" && modo === "explorar" && rastro.length > 1) {
        rastro.pop();
        var prev = rastro[rastro.length - 1];
        if (prev === "@shortlist") explorarShortlist(); else explorar(prev, false);
      }
    }
    document.addEventListener("keydown", tecla);
    limpiezas.push(function () { document.removeEventListener("keydown", tecla); });
    limpiezas.push(KR.shortlist.escuchar(function () {
      if (modo === "inicio") pintarInicio(); else pintarExplorar(false);
    }));

    if (h0.f && g.byId[h0.f]) explorar(h0.f, true); else pintarInicio(true);

    return function () {
      limpiezas.forEach(function (fn) { fn(); });
      limpiezasVista.forEach(function (fn) { fn(); });
      if (animRaf) cancelAnimationFrame(animRaf);
      if (vbAnim) cancelAnimationFrame(vbAnim.raf);
    };
  }

  window.VARIANTES = window.VARIANTES || [];
  window.VARIANTES[1] = { nombre: "Buscar primero", montar: montar };
})();
