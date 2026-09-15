/* Prototipo 5 — «Chile → ciudad».
 * Pedido tras la primera ronda: el mapa de Chile de «Territorio» para entrar, y al tocar una ciudad
 * o región, el «Explorador» sobre el mapa real de esa región, acercándose por comunas.
 *
 * Qué resuelve del desorden del Explorador:
 *   - Las instituciones no flotan en un layout de fuerzas: están en su dirección (OpenStreetMap,
 *     pendiente de revisión). Las que no tienen dirección verificada van a una bandeja aparte,
 *     nunca a un punto inventado.
 *   - Las personas orbitan su institución y los ensayos se resumen en un número hasta que se elige
 *     la institución: de lejos no hay 579 triángulos.
 *   - Las conexiones se dibujan solo para lo seleccionado o bajo el puntero.
 * Chile se ve acostado (norte a la izquierda); al entrar a una región la cámara gira a norte arriba,
 * que es como se reconoce un mapa de ciudad. */
(function () {
  "use strict";
  var KR = window.KR;
  var K = Math.cos(33.45 * Math.PI / 180);   // escala de longitud a la latitud de Santiago
  var OSM_DIR = "../../data/pending/geolocalizacion-osm-2026-09-15/";

  function json(r) { if (!r.ok) throw new Error(r.url + " → " + r.status); return r.json(); }
  function cargarGeo() {
    if (KR._geoCiudad) return Promise.resolve(KR._geoCiudad);
    return Promise.all([fetch("../../data/geo/chile-regiones-comunas.json").then(json), fetch(OSM_DIR + "instituciones_ubicadas.json").then(json)])
      .then(function (r) { KR._geoCiudad = { limites: r[0], ubicadas: r[1] }; return KR._geoCiudad; });
  }
  function slug(s) { return KR.norm(s).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  function corto(region) { return region.replace(/^Región (de la |de los |del |de )?/, "").replace("Metropolitana de Santiago", "Metropolitana"); }
  function dentro(x, y, plano) {
    var n = plano.length / 2, c = false, j = n - 1;
    for (var i = 0; i < n; i++) {
      var xi = plano[2 * i], yi = plano[2 * i + 1], xj = plano[2 * j], yj = plano[2 * j + 1];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-12) + xi) c = !c;
      j = i;
    }
    return c;
  }
  function aMundo(lon, lat) { return [lon * K, -lat]; }
  function cajaDe(planos) {
    var c = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
    planos.forEach(function (p) {
      for (var i = 0; i < p.length; i += 2) {
        if (p[i] < c.x0) c.x0 = p[i]; if (p[i] > c.x1) c.x1 = p[i];
        if (p[i + 1] < c.y0) c.y0 = p[i + 1]; if (p[i + 1] > c.y1) c.y1 = p[i + 1];
      }
    });
    return c;
  }
  function ciudadDe(n) {
    var raw = (n.ciudad || "").trim();
    var dentroParen = /\(([^)+0-9][^)]*)\)/.exec(raw);
    var base = raw.split(" (")[0].split(",")[0].trim();
    var alias = { "port montt": "Puerto Montt", "renaca": "Viña del Mar", "reñaca": "Viña del Mar", "jardin del mar": "Viña del Mar" };
    return { comuna: dentroParen ? dentroParen[1].trim() : null, ciudad: alias[KR.norm(base)] || base };
  }

  function montar(stage) {
    var el = KR.el, g = KR.datos.grafo;
    var h0 = KR.hash.leer();
    var filtros = KR.hash.aFiltros(h0);
    var C = KR.colores(), limpiezas = [], vivo = true;
    var nivel = "pais", regionSel = null, comunaSel = null, sel = null, hover = null, profundidad = h0.d === "2" ? 2 : 1;
    var regiones = [], porRegion = {}, comunas = [], comunaPorNombre = {}, ubic = {}, lugares = {}, listaLugares = [], flujos = [];
    var visibles = {}, verTodasAreas = false, marcas = [], tiempos = [];

    // ---------------------------------------------------------------- estructura
    var raiz = el("div", "variante v1 v5");
    var top = el("header", "kr-top");
    var marca = el("div", "kr-marca");
    marca.appendChild(el("span", "kr-marca-nombre", "KOL Radar"));
    marca.appendChild(el("span", "kr-marca-tag", "oncología · Chile"));
    top.appendChild(marca);
    top.appendChild(el("span", "kr-top-sep"));
    var compartir = KR.botonCompartir(function () {
      return { filtros: filtros, ficha: sel ? g.byId[sel] : null,
        extra: { r: regionSel ? slug(regionSel) : null, c: comunaSel ? slug(comunaSel) : null, d: profundidad === 2 ? "2" : null } };
    });
    limpiezas.push(compartir.destruir);
    top.appendChild(compartir.el);
    raiz.appendChild(top);
    raiz.appendChild(KR.lineaBeta());
    var main = el("div", "v1-main");
    var panel = el("aside", "v1-panel");
    var buscarWrap = el("div", "kr-buscar");
    var input = el("input"); input.type = "search"; input.placeholder = "Buscar persona, institución o ensayo…";
    input.setAttribute("aria-label", "Buscar");
    buscarWrap.appendChild(input); panel.appendChild(buscarWrap);
    var panelCuerpo = el("div", "v1-panel-cuerpo"); panel.appendChild(panelCuerpo);
    main.appendChild(panel);
    var mapa = el("section", "v1-mapa v5-mapa");
    var canvas = el("canvas", "kr-canvas");
    canvas.setAttribute("aria-label", "Mapa de Chile. Elegí una región en el mapa o en el panel para ver sus instituciones sobre el mapa de sus comunas.");
    mapa.appendChild(canvas);
    var migas = el("nav", "v5-migas"); migas.setAttribute("aria-label", "Dónde estás"); mapa.appendChild(migas);
    var tooltip = el("div", "kr-tooltip"); tooltip.hidden = true; mapa.appendChild(tooltip);
    var barraFoco = el("div", "v1-foco"); barraFoco.hidden = true; mapa.appendChild(barraFoco);
    var bandeja = el("details", "v5-bandeja"); bandeja.hidden = true; mapa.appendChild(bandeja);
    var leyenda = el("div", "kr-leyenda v1-leyenda"); mapa.appendChild(leyenda);
    var drawer = el("aside", "kr-drawer"); drawer.setAttribute("inert", "");
    var drawerCerrar = el("button", "kr-drawer-cerrar", "✕"); drawerCerrar.type = "button"; drawerCerrar.setAttribute("aria-label", "Cerrar ficha");
    var drawerCuerpo = el("div", "kr-drawer-cuerpo");
    drawer.appendChild(drawerCerrar); drawer.appendChild(drawerCuerpo); mapa.appendChild(drawer);
    main.appendChild(mapa); raiz.appendChild(main);
    stage.appendChild(raiz);
    panelCuerpo.appendChild(el("p", "kr-nota", "Cargando límites comunales y ubicaciones…"));

    // ---------------------------------------------------------------- modelo
    function preparar(geo) {
      // Isla de Pascua y Juan Fernández quedan fuera: a esta escala alejan el encuadre 3.000 km.
      function continental(plano) { return plano[0] > -76.5 && plano[1] > -56.5; }
      regiones = geo.limites.regiones.map(function (r) {
        var planos = r.anillos.filter(continental);
        var mundo = planos.map(function (p) { var o = []; for (var i = 0; i < p.length; i += 2) { var w = aMundo(p[i], p[i + 1]); o.push(w[0], w[1]); } return o; });
        return { nombre: r.nombre, crudos: planos, anillos: mundo, caja: cajaDe(mundo), comunas: [] };
      });
      regiones.forEach(function (r) { porRegion[r.nombre] = r; });
      comunas = geo.limites.comunas.map(function (c) {
        var planos = c.anillos.filter(continental);
        var mundo = planos.map(function (p) { var o = []; for (var i = 0; i < p.length; i += 2) { var w = aMundo(p[i], p[i + 1]); o.push(w[0], w[1]); } return o; });
        var co = { nombre: c.nombre, region: c.region, crudos: planos, anillos: mundo, caja: cajaDe(mundo), centro: aMundo(c.centro[0], c.centro[1]), inst: 0 };
        if (porRegion[c.region] && planos.length) porRegion[c.region].comunas.push(co);
        (comunaPorNombre[KR.norm(c.nombre)] = comunaPorNombre[KR.norm(c.nombre)] || []).push(co);
        return co;
      }).filter(function (c) { return c.crudos.length; });
      geo.ubicadas.forEach(function (u) { ubic[u.id] = u; });

      function comunaEn(lon, lat) {
        for (var i = 0; i < comunas.length; i++) {
          var c = comunas[i], w = aMundo(lon, lat);
          if (w[0] < c.caja.x0 || w[0] > c.caja.x1 || w[1] < c.caja.y0 || w[1] > c.caja.y1) continue;
          if (c.crudos.some(function (p) { return dentro(lon, lat, p); })) return c;
        }
        return null;
      }
      function comunaDeCiudad(n) {
        var cd = ciudadDe(n);
        var cand = (cd.comuna && comunaPorNombre[KR.norm(cd.comuna)]) || comunaPorNombre[KR.norm(cd.ciudad)];
        return cand ? cand[0] : null;
      }
      g.nodos.forEach(function (n) { n._v5 = { x: null, y: null, comuna: null, region: null, inst: null, regiones: [] }; });
      g.nodos.forEach(function (n) {
        if (n.tipo !== "institucion") return;
        var u = ubic[n.id], v = n._v5;
        if (u) {
          var w = aMundo(u.lon, u.lat); v.x = w[0]; v.y = w[1];
          v.comuna = comunaEn(u.lon, u.lat);
          if (v.comuna) v.comuna.inst++;
          v.osm = u;
        }
        var cc = v.comuna || comunaDeCiudad(n);
        v.region = cc ? cc.region : null;
      });
      g.nodos.forEach(function (n) {
        var v = n._v5;
        if (n.tipo === "persona") {
          var afil = null, cualquiera = null;
          g.adj[n.id].forEach(function (a) {
            var o = g.byId[a.otro];
            if (o.tipo !== "institucion") return;
            if (!cualquiera) cualquiera = o;
            if (!afil && /afiliaci/.test(a.v.tipo)) afil = o;
          });
          v.inst = afil || cualquiera;
          var cc = comunaDeCiudad(n);
          v.region = v.inst ? v.inst._v5.region : cc ? cc.region : null;
          v.regiones = v.region ? [v.region] : [];
        } else if (n.tipo === "ensayo_clinico") {
          var rs = [];
          g.adj[n.id].forEach(function (a) {
            var o = g.byId[a.otro];
            if (o.tipo === "institucion" && o._v5.region && rs.indexOf(o._v5.region) === -1) rs.push(o._v5.region);
          });
          if (!rs.length) { var c2 = comunaDeCiudad(n); if (c2) rs.push(c2.region); }
          v.regiones = rs; v.region = rs[0] || null;
        } else {
          v.regiones = v.region ? [v.region] : [];
        }
      });
      calcularLugares();
    }

    // Ciudades del nivel país: las mismas de «Territorio» (centroides que declara la fuente).
    function calcularLugares() {
      var geoC = KR.datos.geo.ciudades;
      lugares = {};
      g.nodos.forEach(function (n) {
        if (!visibles[n.id]) return;
        var cs = [];
        if (n.tipo === "ensayo_clinico") {
          g.adj[n.id].forEach(function (a) {
            var o = g.byId[a.otro];
            if (o.tipo === "institucion") { var c = nombreCiudad(o); if (c && cs.indexOf(c) === -1) cs.push(c); }
          });
        }
        if (!cs.length) { var p = nombreCiudad(n); if (p) cs.push(p); }
        cs.forEach(function (c) {
          var L = lugares[c];
          if (!L) {
            var gc = geoC[c] || geoC[{ "Puerto Montt": "Port Montt" }[c]];
            var w = aMundo(gc.lon, gc.lat), cm = comunaPorNombre[KR.norm(c)];
            L = lugares[c] = { nombre: c, x: w[0], y: w[1], ids: [], cuenta: { persona: 0, institucion: 0, ensayo_clinico: 0 }, region: cm ? cm[0].region : null };
          }
          L.ids.push(n.id); L.cuenta[n.tipo]++;
        });
      });
      listaLugares = Object.keys(lugares).map(function (k) { return lugares[k]; }).sort(function (a, b) { return b.ids.length - a.ids.length; });
      var pares = {};
      g.nodos.forEach(function (n) {
        if (n.tipo !== "ensayo_clinico" || !visibles[n.id]) return;
        var cs = [];
        g.adj[n.id].forEach(function (a) {
          var o = g.byId[a.otro];
          if (o.tipo === "institucion" && visibles[o.id]) { var c = nombreCiudad(o); if (c && cs.indexOf(c) === -1) cs.push(c); }
        });
        for (var i = 0; i < cs.length; i++) for (var j = i + 1; j < cs.length; j++) {
          var k = cs[i] < cs[j] ? cs[i] + "|" + cs[j] : cs[j] + "|" + cs[i];
          (pares[k] = pares[k] || { a: lugares[cs[i]], b: lugares[cs[j]], n: 0 }).n++;
        }
      });
      flujos = Object.keys(pares).map(function (k) { return pares[k]; }).sort(function (a, b) { return b.n - a.n; });
    }
    function nombreCiudad(n) {
      var geoC = KR.datos.geo.ciudades, cd = ciudadDe(n), base = cd.ciudad;
      var rm = ["providencia", "recoleta", "las condes", "independencia", "nunoa", "vitacura", "maipu", "puente alto", "la florida", "macul", "huechuraba", "quilicura", "lo barnechea", "la reina", "san miguel", "penalolen", "estacion central"];
      if (rm.indexOf(KR.norm(base)) !== -1) base = "Santiago";
      return geoC[base] || geoC[{ "Puerto Montt": "Port Montt" }[base]] ? base : null;
    }

    function recalcular() {
      visibles = {};
      g.nodos.forEach(function (n) { if (KR.pasa(n, filtros)) visibles[n.id] = true; });
      calcularLugares();
    }
    function enAlcance(n) { return !regionSel || n._v5.regiones.indexOf(regionSel) !== -1 || n._v5.region === regionSel; }

    function focoActual() {
      var id = hover && hover.tipo === "ficha" ? hover.id : sel;
      if (!id) return null;
      return KR.vecindario(g, id, profundidad, function (n) { return visibles[n.id]; });
    }

    // ---------------------------------------------------------------- dibujo
    function trazarPlanos(ctx, lz, planos) {
      planos.forEach(function (p) {
        for (var i = 0; i < p.length; i += 2) {
          var s = lz.aPantalla(p[i], p[i + 1]);
          if (i) ctx.lineTo(s[0], s[1]); else ctx.moveTo(s[0], s[1]);
        }
        ctx.closePath();
      });
    }
    function vistaMundo(lz) {
      var esquinas = [lz.aMundo(0, 0), lz.aMundo(lz.w, 0), lz.aMundo(0, lz.h), lz.aMundo(lz.w, lz.h)];
      return { x0: Math.min.apply(null, esquinas.map(function (e) { return e[0]; })), x1: Math.max.apply(null, esquinas.map(function (e) { return e[0]; })),
        y0: Math.min.apply(null, esquinas.map(function (e) { return e[1]; })), y1: Math.max.apply(null, esquinas.map(function (e) { return e[1]; })) };
    }
    function cruza(a, b) { return !(a.x1 < b.x0 || a.x0 > b.x1 || a.y1 < b.y0 || a.y0 > b.y1); }

    function dibujar(ctx, lz) {
      if (!regiones.length) return;
      marcas = [];
      var vista = vistaMundo(lz), foco = focoActual();
      var fichasPorRegion = {}, maxF = 1;
      g.nodos.forEach(function (n) {
        if (!visibles[n.id]) return;
        (n._v5.regiones.length ? n._v5.regiones : n._v5.region ? [n._v5.region] : []).forEach(function (r) { fichasPorRegion[r] = (fichasPorRegion[r] || 0) + 1; });
      });
      Object.keys(fichasPorRegion).forEach(function (k) { maxF = Math.max(maxF, fichasPorRegion[k]); });

      // Regiones. En el país, sombreadas por cantidad de fichas; dentro de una región, solo contexto.
      regiones.forEach(function (r) {
        if (!cruza(r.caja, vista)) return;
        ctx.beginPath(); trazarPlanos(ctx, lz, r.anillos);
        if (nivel === "pais") {
          var t = Math.sqrt((fichasPorRegion[r.nombre] || 0) / maxF);
          ctx.fillStyle = C.s2; ctx.globalAlpha = 1; ctx.fill();
          ctx.fillStyle = C.acento; ctx.globalAlpha = 0.06 + t * 0.34; ctx.fill();
        } else {
          ctx.fillStyle = r.nombre === regionSel ? C.s0 : C.s2; ctx.globalAlpha = r.nombre === regionSel ? 1 : 0.6; ctx.fill();
        }
        var hv = hover && hover.tipo === "region" && hover.id === r.nombre;
        ctx.globalAlpha = 1; ctx.strokeStyle = hv ? C.texto : C.borde; ctx.lineWidth = hv ? 2 : 1; ctx.stroke();
      });

      if (nivel === "pais") { dibujarPais(ctx, lz, foco); return; }

      var reg = porRegion[regionSel];
      reg.comunas.forEach(function (c) {
        if (!cruza(c.caja, vista)) return;
        ctx.beginPath(); trazarPlanos(ctx, lz, c.anillos);
        var hv = hover && hover.tipo === "comuna" && hover.id === c;
        if (c.nombre === comunaSel || hv) { ctx.fillStyle = C.s1; ctx.globalAlpha = 1; ctx.fill(); }
        ctx.strokeStyle = C.borde; ctx.globalAlpha = 0.9; ctx.lineWidth = c.nombre === comunaSel ? 1.8 : 0.8; ctx.stroke();
      });
      ctx.globalAlpha = 1;
      dibujarRegion(ctx, lz, reg, foco, vista);
    }

    function dibujarPais(ctx, lz, foco) {
      var maxN = listaLugares.length ? listaLugares[0].ids.length : 1;
      flujos.slice(0, 40).forEach(function (f) {
        var a = lz.aPantalla(f.a.x, f.a.y), b = lz.aPantalla(f.b.x, f.b.y);
        var mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1];
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(mx - dy * 0.16, my + dx * 0.16, b[0], b[1]);
        ctx.strokeStyle = C.tenue; ctx.globalAlpha = 0.45; ctx.lineWidth = Math.min(8, 1 + Math.sqrt(f.n) * 0.9); ctx.stroke();
      });
      ctx.globalAlpha = 1;
      var cands = [];
      listaLugares.forEach(function (L) {
        var s = lz.aPantalla(L.x, L.y), r = Math.max(4, Math.min(34, 3 + Math.sqrt(L.ids.length) * 2.2));
        var tenue = foco && !L.ids.some(function (id) { return foco[id] !== undefined; });
        ctx.globalAlpha = tenue ? 0.25 : 1;
        ctx.beginPath(); ctx.arc(s[0], s[1], r, 0, Math.PI * 2); ctx.fillStyle = C.s0; ctx.fill();
        var ang = -Math.PI / 2;
        KR.TIPOS.forEach(function (t) {
          if (!L.cuenta[t]) return;
          var a1 = ang + (L.cuenta[t] / L.ids.length) * Math.PI * 2;
          ctx.beginPath(); ctx.arc(s[0], s[1], r - 1.5, ang, a1); ctx.strokeStyle = C[t]; ctx.lineWidth = Math.max(2.5, r * 0.28); ctx.stroke();
          ang = a1;
        });
        if (hover && hover.tipo === "lugar" && hover.id === L) { ctx.beginPath(); ctx.arc(s[0], s[1], r + 4, 0, Math.PI * 2); ctx.strokeStyle = C.texto; ctx.lineWidth = 2; ctx.stroke(); }
        marcas.push({ tipo: "lugar", L: L, sx: s[0], sy: s[1], r: r + 3 });
        cands.push({ sx: s[0], sy: s[1], r: r, texto: L.nombre + " · " + KR.miles(L.ids.length), fuerte: false });
      });
      ctx.globalAlpha = 1;
      etiquetas(ctx, lz, cands, 30);
    }

    // Posición en pantalla de cada ficha dentro de la región. Institución: su dirección. Persona:
    // en órbita alrededor de su institución. Ensayo: en abanico, solo si su institución está abierta.
    function dibujarRegion(ctx, lz, reg, foco, vista) {
      var k = lz.cam.k;
      var insts = g.nodos.filter(function (n) { return n.tipo === "institucion" && n._v5.region === regionSel && n._v5.x !== null; });
      var instVis = insts.filter(function (n) { return visibles[n.id]; });
      var pos = {};
      var escalaPin = Math.max(0.7, Math.min(1.6, Math.log(k / 40 + 1)));
      instVis.forEach(function (n) {
        var s = lz.aPantalla(n._v5.x, n._v5.y);
        var ens = 0, pers = [];
        g.adj[n.id].forEach(function (a) {
          var o = g.byId[a.otro];
          if (!visibles[o.id]) return;
          if (o.tipo === "ensayo_clinico") ens++;
          if (o.tipo === "persona" && o._v5.inst === n) pers.push(o);
        });
        n._v5.s = s; n._v5.r = (5 + Math.min(12, Math.sqrt(n._grado) * 0.9)) * escalaPin; n._v5.nEns = ens; n._v5.pers = pers;
        pos[n.id] = s;
      });
      // Apertura: la institución elegida, la que tiene lo elegido, o las que de tan cerca tienen espacio.
      var abiertas = {};
      instVis.forEach(function (n) {
        var cerca = instVis.every(function (m) { return m === n || Math.hypot(m._v5.s[0] - n._v5.s[0], m._v5.s[1] - n._v5.s[1]) > 170; });
        if (sel === n.id || (sel && g.byId[sel] && g.byId[sel].tipo !== "institucion" && g.adj[sel].some(function (a) { return a.otro === n.id; }) && g.byId[sel].tipo === "ensayo_clinico") || (cerca && n._v5.nEns <= 60 && k > 900)) abiertas[n.id] = true;
      });
      instVis.forEach(function (n) {
        var v = n._v5;
        v.pers.forEach(function (p, i) {
          var porAnillo = 10, anillo = Math.floor(i / porAnillo), enAnillo = Math.min(porAnillo, v.pers.length - anillo * porAnillo);
          var ang = -Math.PI / 2 + ((i % porAnillo) / enAnillo) * Math.PI * 2;
          var rad = v.r + 10 + anillo * 8;
          pos[p.id] = [v.s[0] + Math.cos(ang) * rad, v.s[1] + Math.sin(ang) * rad];
        });
        if (abiertas[n.id]) {
          var ens = g.adj[n.id].map(function (a) { return g.byId[a.otro]; })
            .filter(function (o) { return o.tipo === "ensayo_clinico" && visibles[o.id]; })
            .sort(function (a, b) { return (b._anio || 0) - (a._anio || 0); });
          var lim = Math.min(ens.length, 48), radE = v.r + 34 + Math.ceil(v.pers.length / 10) * 8;
          ens.slice(0, lim).forEach(function (e, i) {
            if (pos[e.id]) return;
            var ang = -Math.PI / 2 + (i / lim) * Math.PI * 2, rr = radE + (i % 2) * 12;
            pos[e.id] = [v.s[0] + Math.cos(ang) * rr, v.s[1] + Math.sin(ang) * rr];
          });
          v.resto = ens.length - lim;
        } else v.resto = 0;
      });

      // Conexiones: solo para lo seleccionado o bajo el puntero.
      var centro = hover && hover.tipo === "ficha" ? hover.id : sel;
      if (centro && pos[centro]) {
        var pc = pos[centro];
        var nodoC = g.byId[centro];
        var hacia = {};
        g.adj[centro].forEach(function (a) {
          var o = g.byId[a.otro];
          if (!visibles[o.id]) return;
          if (pos[o.id]) { hacia[o.id] = (hacia[o.id] || 0) + 1; return; }
          // Un ensayo cerrado se dibuja como su institución: la línea va al pin.
          if (o.tipo === "ensayo_clinico") {
            g.adj[o.id].forEach(function (b) { var ins = g.byId[b.otro]; if (ins.tipo === "institucion" && ins.id !== centro && pos[ins.id]) hacia[ins.id] = (hacia[ins.id] || 0) + 1; });
          }
        });
        Object.keys(hacia).forEach(function (id) {
          var p = pos[id], dx = p[0] - pc[0], dy = p[1] - pc[1], L = Math.hypot(dx, dy) || 1;
          ctx.beginPath(); ctx.moveTo(pc[0], pc[1]);
          ctx.quadraticCurveTo((pc[0] + p[0]) / 2 - dy * 0.12, (pc[1] + p[1]) / 2 + dx * 0.12, p[0], p[1]);
          ctx.strokeStyle = C[nodoC.tipo]; ctx.globalAlpha = 0.75; ctx.lineWidth = Math.min(6, 1.2 + Math.log2(hacia[id]) * 1.1); ctx.stroke();
        });
        ctx.globalAlpha = 1;
      }

      var cands = [];
      function tenue(id) { return !!(foco && foco[id] === undefined); }
      // Ensayos abiertos
      KR.TIPOS.forEach(function (t) {
        [true, false].forEach(function (dim) {
          ctx.beginPath(); var hay = false;
          Object.keys(pos).forEach(function (id) {
            var n = g.byId[id];
            if (n.tipo !== t || tenue(id) !== dim) return;
            var p = pos[id], r = t === "institucion" ? n._v5.r : t === "persona" ? 3.4 * escalaPin : 3 * escalaPin;
            KR.trazarForma(ctx, t, p[0], p[1], r); hay = true;
            marcas.push({ tipo: "ficha", id: id, sx: p[0], sy: p[1], r: Math.max(r + 2, 6) });
          });
          if (!hay) return;
          ctx.fillStyle = C[t]; ctx.globalAlpha = dim ? 0.18 : 1; ctx.fill();
          if (t === "institucion") { ctx.strokeStyle = C.s0; ctx.lineWidth = 1.5; ctx.stroke(); }
        });
      });
      ctx.globalAlpha = 1;
      // Número de ensayos de cada institución cerrada.
      ctx.font = '600 10px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
      ctx.textBaseline = "middle";
      instVis.forEach(function (n) {
        var v = n._v5;
        if (tenue(n.id)) return;
        var txt = abiertas[n.id] ? (v.resto ? "+" + v.resto : "") : v.nEns ? "▲ " + v.nEns : "";
        if (!txt) return;
        var tw = ctx.measureText(txt).width, x = v.s[0] + v.r + 3, y = v.s[1] + v.r + 2;
        ctx.fillStyle = C.s0; ctx.globalAlpha = 0.9;
        ctx.beginPath(); ctx.rect(x - 3, y - 7, tw + 6, 14); ctx.fill();
        ctx.globalAlpha = 1; ctx.fillStyle = C.ensayo_clinico; ctx.fillText(txt, x, y);
      });
      // Anillos: seleccionado y shortlist.
      KR.shortlist.lista().forEach(function (id) {
        if (!pos[id]) return;
        var n = g.byId[id], r = (n.tipo === "institucion" ? n._v5.r : 3.4 * escalaPin) + 4;
        ctx.beginPath(); ctx.arc(pos[id][0], pos[id][1], r, 0, Math.PI * 2); ctx.strokeStyle = C.acento; ctx.lineWidth = 2; ctx.stroke();
      });
      if (sel && pos[sel]) {
        var ns = g.byId[sel], rs = (ns.tipo === "institucion" ? ns._v5.r : 4 * escalaPin) + 3;
        KR.dibujarForma(ctx, ns.tipo, pos[sel][0], pos[sel][1], rs); ctx.strokeStyle = C.texto; ctx.lineWidth = 2.5; ctx.stroke();
      }

      // Etiquetas: lo seleccionado, instituciones, comunas con instituciones, y de cerca, personas.
      ctx.font = KR.FUENTE_CANVAS;
      if (sel && pos[sel]) cands.push({ sx: pos[sel][0], sy: pos[sel][1], r: 8, texto: KR.etiquetaCorta(g.byId[sel]), n: g.byId[sel], fuerte: true });
      // En foco, los ensayos del abanico se nombran recién de muy cerca: de a 40 alrededor de un
      // pin, sus títulos tapaban la institución que se acababa de elegir.
      if (foco) Object.keys(foco).forEach(function (id) {
        var nf = g.byId[id];
        if (!pos[id] || id === sel || (nf.tipo === "ensayo_clinico" && k < 6000)) return;
        cands.push({ sx: pos[id][0], sy: pos[id][1], r: 6, texto: KR.etiquetaCorta(nf), n: nf, fuerte: true });
      });
      instVis.slice().sort(function (a, b) { return b._grado - a._grado; }).forEach(function (n) {
        if (tenue(n.id)) return;
        cands.push({ sx: n._v5.s[0], sy: n._v5.s[1], r: n._v5.r, texto: KR.etiquetaCorta(n), n: n, fuerte: false });
      });
      if (k > 2200) Object.keys(pos).forEach(function (id) { var n = g.byId[id]; if (n.tipo === "persona" && !tenue(id)) cands.push({ sx: pos[id][0], sy: pos[id][1], r: 4, texto: n.nombre, n: n, fuerte: false }); });
      etiquetas(ctx, lz, cands, 60);
      // Nombres de comuna en gris, debajo de todo lo demás en prioridad.
      ctx.font = '600 9.5px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
      var ocupadas = cands.length;
      reg.comunas.forEach(function (c) {
        if (!cruza(c.caja, vista)) return;
        var s = lz.aPantalla(c.centro[0], c.centro[1]);
        var ancho = (c.caja.x1 - c.caja.x0) * k;
        if (ancho < 70 && c.nombre !== comunaSel) return;
        ctx.globalAlpha = 0.55; ctx.fillStyle = C.tenue; ctx.textAlign = "center";
        ctx.fillText(c.nombre.toUpperCase(), s[0], s[1]);
        ctx.textAlign = "start";
      });
      ctx.globalAlpha = 1;
      pintarBandeja(reg);
      pintarLeyendaDin(instVis.length, ocupadas);
    }

    function etiquetas(ctx, lz, cands, max) {
      var puestas = KR.colocarEtiquetas(ctx, cands, lz.w, lz.h, max);
      ctx.textBaseline = "middle"; ctx.lineJoin = "round";
      puestas.forEach(function (pu) {
        ctx.lineWidth = 3; ctx.strokeStyle = C.s0; ctx.globalAlpha = 0.95; ctx.strokeText(pu.c.texto, pu.x, pu.y);
        ctx.globalAlpha = 1; ctx.fillStyle = pu.c.fuerte ? C.texto : C.texto2; ctx.fillText(pu.c.texto, pu.x, pu.y);
      });
    }

    var lz = KR.lienzo(canvas, {
      minK: 3, maxK: 60000, alDibujar: function (ctx, l) { var t0 = performance.now(); dibujar(ctx, l); tiempos.push(performance.now() - t0); if (tiempos.length > 20) tiempos.shift(); },
      alMover: function (sx, sy) { apuntar(sx, sy); },
      alSalir: function () { hover = null; tooltip.hidden = true; lz.dibujar(); },
      alClick: function (sx, sy) { tocar(sx, sy); }
    });
    limpiezas.push(lz.destruir);

    // ---------------------------------------------------------------- puntería
    function queHay(sx, sy) {
      for (var i = marcas.length - 1; i >= 0; i--) {
        var m = marcas[i];
        if (Math.hypot(m.sx - sx, m.sy - sy) <= m.r) return m;
      }
      var w = lz.aMundo(sx, sy), lat = -w[1], lon = w[0] / K;
      if (nivel === "region") {
        var reg = porRegion[regionSel];
        for (var j = 0; j < reg.comunas.length; j++) {
          var c = reg.comunas[j];
          if (w[0] < c.caja.x0 || w[0] > c.caja.x1 || w[1] < c.caja.y0 || w[1] > c.caja.y1) continue;
          if (c.crudos.some(function (p) { return dentro(lon, lat, p); })) return { tipo: "comuna", id: c };
        }
      }
      for (var r = 0; r < regiones.length; r++) {
        var R = regiones[r];
        if (w[0] < R.caja.x0 || w[0] > R.caja.x1 || w[1] < R.caja.y0 || w[1] > R.caja.y1) continue;
        if (R.crudos.some(function (p) { return dentro(lon, lat, p); })) return { tipo: "region", id: R.nombre };
      }
      return null;
    }
    function mostrarTooltip(sx, sy, titulo, sub, nota) {
      tooltip.innerHTML = "";
      tooltip.appendChild(el("div", "kr-tooltip-tit", titulo));
      if (sub) tooltip.appendChild(el("div", "kr-tooltip-sub", sub));
      if (nota) tooltip.appendChild(el("div", "kr-tooltip-ev", nota));
      tooltip.hidden = false;
      tooltip.style.transform = "translate(" + Math.max(8, Math.min(sx + 14, lz.w - tooltip.offsetWidth - 8)) + "px," + Math.max(8, Math.min(sy + 14, lz.h - tooltip.offsetHeight - 8)) + "px)";
    }
    function apuntar(sx, sy) {
      var q = queHay(sx, sy);
      hover = q ? (q.tipo === "ficha" ? { tipo: "ficha", id: q.id } : q.tipo === "lugar" ? { tipo: "lugar", id: q.L } : q) : null;
      canvas.style.cursor = q ? "pointer" : "";
      if (!q) { tooltip.hidden = true; lz.dibujar(); return; }
      if (q.tipo === "ficha") {
        var n = g.byId[q.id], v = n._v5;
        if (n.tipo === "institucion") {
          mostrarTooltip(sx, sy, n.nombre, (v.comuna ? v.comuna.nombre + " · " : "") + KR.plural(v.pers.length, "persona", "personas") + " · " + KR.plural(v.nEns, "ensayo", "ensayos"),
            "Ubicación: OpenStreetMap, pendiente de revisión");
        } else mostrarTooltip(sx, sy, n.nombre, KR.TIPO_LABEL[n.tipo] + (n.subtitulo ? " · " + n.subtitulo : ""));
      } else if (q.tipo === "lugar") {
        mostrarTooltip(sx, sy, q.L.nombre, KR.miles(q.L.ids.length) + " fichas · click para entrar a " + (q.L.region ? corto(q.L.region) : "la región"));
      } else if (q.tipo === "region") {
        var cuantas = g.nodos.filter(function (n) { return visibles[n.id] && (n._v5.region === q.id || n._v5.regiones.indexOf(q.id) !== -1); }).length;
        mostrarTooltip(sx, sy, q.id, KR.miles(cuantas) + " fichas" + (nivel === "pais" || q.id !== regionSel ? " · click para entrar" : ""));
      } else if (q.tipo === "comuna") {
        mostrarTooltip(sx, sy, q.id.nombre, KR.plural(q.id.inst, "institución con dirección", "instituciones con dirección") + " · click para acercar");
      }
      lz.dibujar();
    }
    function tocar(sx, sy) {
      var q = queHay(sx, sy);
      if (!q) { if (sel) seleccionar(null); return; }
      if (q.tipo === "ficha") { seleccionar(q.id, false); return; }
      if (q.tipo === "lugar") { if (q.L.region) entrarRegion(q.L.region, false, q.L); return; }
      if (q.tipo === "region") { if (nivel === "pais" || q.id !== regionSel) entrarRegion(q.id); else if (sel) seleccionar(null); return; }
      if (q.tipo === "comuna") {
        if (sel) { seleccionar(null); return; }
        comunaSel = comunaSel === q.id.nombre ? null : q.id.nombre;
        if (comunaSel) lz.animarA(lz.encuadre(q.id.caja, 50, 0), 520, false, KR.easeInOut); else encuadrarRegion(false);
        pintarMigas(); escribirHash(); lz.dibujar();
      }
    }

    // ---------------------------------------------------------------- navegación
    function rotPais() { return lz.w / Math.max(1, lz.h) > 1.15 ? -Math.PI / 2 : 0; }
    function cajaPais() {
      var c = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
      listaLugares.concat(Object.keys(lugares).map(function (k) { return lugares[k]; })).forEach(function (L) {
        c.x0 = Math.min(c.x0, L.x); c.x1 = Math.max(c.x1, L.x); c.y0 = Math.min(c.y0, L.y); c.y1 = Math.max(c.y1, L.y);
      });
      if (!isFinite(c.x0)) return regiones.reduce(function (a, r) { return { x0: Math.min(a.x0, r.caja.x0), x1: Math.max(a.x1, r.caja.x1), y0: Math.min(a.y0, r.caja.y0), y1: Math.max(a.y1, r.caja.y1) }; }, { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity });
      return { x0: c.x0 - 1.4, x1: c.x1 + 1.4, y0: c.y0 - 1.4, y1: c.y1 + 1.4 };
    }
    function irPais(inmediato) {
      nivel = "pais"; regionSel = null; comunaSel = null;
      if (sel) seleccionar(null);
      lz.animarA(lz.encuadre(cajaPais(), 40, rotPais()), 760, inmediato, KR.easeInOut);
      pintarMigas(); pintarPanel(); bandeja.hidden = true; escribirHash(); lz.dibujar();
    }
    function cajaRegion(region) {
      var pts = g.nodos.filter(function (n) { return n.tipo === "institucion" && n._v5.region === region && n._v5.x !== null; });
      if (pts.length >= 2) {
        var c = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
        pts.forEach(function (n) { c.x0 = Math.min(c.x0, n._v5.x); c.x1 = Math.max(c.x1, n._v5.x); c.y0 = Math.min(c.y0, n._v5.y); c.y1 = Math.max(c.y1, n._v5.y); });
        var mx = Math.max(0.06, (c.x1 - c.x0) * 0.25), my = Math.max(0.06, (c.y1 - c.y0) * 0.25);
        return { x0: c.x0 - mx, x1: c.x1 + mx, y0: c.y0 - my, y1: c.y1 + my };
      }
      if (pts.length === 1) return { x0: pts[0]._v5.x - 0.08, x1: pts[0]._v5.x + 0.08, y0: pts[0]._v5.y - 0.08, y1: pts[0]._v5.y + 0.08 };
      return porRegion[region].caja;
    }
    function encuadrarRegion(inmediato) {
      var dest = lz.encuadre(cajaRegion(regionSel), 60, 0);
      if (drawer.classList.contains("abierto")) dest.cx += (Math.min(200, lz.w * 0.18)) / dest.k;
      lz.animarA(dest, 760, inmediato, KR.easeInOut);
    }
    function entrarRegion(region, inmediato) {
      if (!porRegion[region]) return;
      var cambia = region !== regionSel;
      nivel = "region"; regionSel = region; comunaSel = null;
      if (cambia && sel && g.byId[sel]._v5.regiones.indexOf(region) === -1 && g.byId[sel]._v5.region !== region) seleccionar(null);
      encuadrarRegion(inmediato);
      pintarMigas(); pintarPanel(); escribirHash(); lz.dibujar();
    }

    function pintarMigas() {
      migas.innerHTML = "";
      var b0 = el("button", "v5-miga" + (nivel === "pais" ? " actual" : ""), "Chile"); b0.type = "button";
      b0.addEventListener("click", function () { irPais(false); });
      migas.appendChild(b0);
      if (regionSel) {
        migas.appendChild(el("span", "v5-miga-sep", "›"));
        var b1 = el("button", "v5-miga" + (comunaSel ? "" : " actual"), corto(regionSel)); b1.type = "button";
        b1.addEventListener("click", function () { comunaSel = null; encuadrarRegion(false); pintarMigas(); escribirHash(); lz.dibujar(); });
        migas.appendChild(b1);
      }
      if (comunaSel) {
        migas.appendChild(el("span", "v5-miga-sep", "›"));
        migas.appendChild(el("span", "v5-miga actual", comunaSel));
      }
    }

    // ---------------------------------------------------------------- ficha
    function abrirDrawer(c) {
      if (drawerCuerpo.firstChild && drawerCuerpo.firstChild._destruir) drawerCuerpo.firstChild._destruir();
      drawerCuerpo.innerHTML = ""; drawerCuerpo.appendChild(c); drawerCuerpo.scrollTop = 0;
      drawer.classList.add("abierto"); drawer.removeAttribute("inert");
    }
    function cerrarDrawer() { drawer.classList.remove("abierto"); drawer.setAttribute("inert", ""); }
    drawerCerrar.addEventListener("click", function () { seleccionar(null); });

    function bloqueUbicacion(n) {
      var box = el("div", "v5-ubicacion");
      box.appendChild(el("p", "kr-ficha-sec", "Ubicación"));
      var v = n._v5;
      if (v.osm) {
        box.appendChild(el("p", "v5-ubic-dir", v.osm.direccion_osm));
        var p = el("p", "kr-nota");
        var a = el("a", "", "Objeto en OpenStreetMap ↗"); a.href = v.osm.fuente_url; a.target = "_blank"; a.rel = "noopener noreferrer";
        p.appendChild(a);
        p.appendChild(document.createTextNode(" · consultado " + v.osm.fecha + " · pendiente de revisión" + (v.osm.match_ambiguo ? " · hay otra sede con el mismo nombre" : "")));
        box.appendChild(p);
      } else {
        box.appendChild(el("p", "kr-aviso", "Sin dirección verificada. No se ubica en el mapa hasta tener una fuente: está en la tarea de data/pending/tarea-chatgpt-2026-09-15/."));
      }
      return box;
    }
    function seleccionar(id, volar) {
      sel = id;
      if (!id) { cerrarDrawer(); pintarFoco(); lz.dibujar(); escribirHash(); return; }
      var n = g.byId[id];
      var f = KR.ficha(n, {
        alNavegar: function (otro) { irAFicha(otro); },
        alResaltar: function (otro) { hover = otro ? { tipo: "ficha", id: otro } : null; lz.dibujar(); }
      });
      if (n.tipo === "institucion") {
        var acc = f.querySelector(".kr-ficha-acciones");
        acc.parentNode.insertBefore(bloqueUbicacion(n), acc.nextSibling);
      }
      abrirDrawer(f);
      pintarFoco(); escribirHash();
      if (volar) volarAFicha(n);
      lz.dibujar();
    }
    function puntoDe(n) {
      var v = n._v5;
      if (n.tipo === "institucion") return v.x !== null ? [v.x, v.y] : null;
      if (n.tipo === "persona") return v.inst && v.inst._v5.x !== null ? [v.inst._v5.x, v.inst._v5.y] : null;
      var pts = g.adj[n.id].map(function (a) { return g.byId[a.otro]; }).filter(function (o) { return o.tipo === "institucion" && o._v5.x !== null && o._v5.region === regionSel; });
      return pts.length ? [pts[0]._v5.x, pts[0]._v5.y] : null;
    }
    function irAFicha(id) {
      var n = g.byId[id];
      if (!KR.pasa(n, filtros)) { filtros = KR.filtrosVacios(); recalcular(); }
      var region = n._v5.region;
      if (region && (nivel === "pais" || regionSel !== region)) { nivel = "region"; regionSel = region; comunaSel = null; pintarMigas(); pintarPanel(); }
      seleccionar(id, true);
    }
    function volarAFicha(n) {
      var p = puntoDe(n);
      if (!p || nivel !== "region") { if (nivel === "region") encuadrarRegion(false); return; }
      var k = Math.max(lz.base().k, 2600);
      lz.animarA({ cx: p[0] + Math.min(200, lz.w * 0.18) / k, cy: p[1], k: k, rot: 0 }, 700, false, KR.easeInOut);
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
        b.addEventListener("click", function () { profundidad = d; pintarFoco(); escribirHash(); lz.dibujar(); });
        seg.appendChild(b);
      });
      barraFoco.appendChild(seg);
      var foco = focoActual() || {}, fuera = {};
      Object.keys(foco).forEach(function (id) {
        var r = g.byId[id]._v5.region;
        if (r && r !== regionSel) fuera[r] = (fuera[r] || 0) + 1;
      });
      var otras = Object.keys(fuera);
      if (otras.length) {
        var nota = el("span", "kr-nota v5-fuera");
        nota.appendChild(document.createTextNode("También en: "));
        otras.sort(function (a, b) { return fuera[b] - fuera[a]; }).slice(0, 3).forEach(function (r, i) {
          var b = el("button", "v5-miga", corto(r) + " (" + fuera[r] + ")"); b.type = "button";
          b.addEventListener("click", function () { entrarRegion(r); });
          if (i) nota.appendChild(document.createTextNode(" · "));
          nota.appendChild(b);
        });
        barraFoco.appendChild(nota);
      }
      var x = el("button", "kr-btn kr-btn-chico", "Cerrar"); x.type = "button";
      x.addEventListener("click", function () { seleccionar(null); });
      barraFoco.appendChild(x);
    }

    // Instituciones sin dirección verificada: fuera del mapa, en una bandeja, nunca en un punto inventado.
    var bandejaFirma = "";
    function pintarBandeja(reg) {
      var sinDir = g.nodos.filter(function (n) { return n.tipo === "institucion" && n._v5.region === regionSel && n._v5.x === null && visibles[n.id]; });
      var sueltos = g.nodos.filter(function (n) {
        return n.tipo === "ensayo_clinico" && visibles[n.id] && n._v5.region === regionSel && !g.adj[n.id].some(function (a) { return g.byId[a.otro].tipo === "institucion"; });
      }).length;
      var firma = regionSel + "|" + sinDir.map(function (n) { return n.id; }).join(",") + "|" + sueltos + "|" + sel;
      if (firma === bandejaFirma) return;
      bandejaFirma = firma;
      bandeja.innerHTML = "";
      if (!sinDir.length && !sueltos) { bandeja.hidden = true; return; }
      bandeja.hidden = false;
      // Plegada mientras hay algo elegido: abierta tapaba la barra de foco.
      bandeja.open = !sel;
      var tit = el("summary", "v5-bandeja-tit", "Sin dirección verificada en " + corto(regionSel) + " · " + sinDir.length);
      bandeja.appendChild(tit);
      var fila = el("div", "v5-bandeja-fila");
      sinDir.sort(function (a, b) { return b._grado - a._grado; }).forEach(function (n) {
        var b = el("button", "v5-chip" + (sel === n.id ? " activo" : "")); b.type = "button";
        b.appendChild(KR.formaSVG("institucion", 8));
        b.appendChild(document.createTextNode(KR.etiquetaCorta(n)));
        b.appendChild(el("span", "v5-chip-num", KR.miles(g.adj[n.id].length)));
        b.addEventListener("click", function () { seleccionar(n.id, false); });
        fila.appendChild(b);
      });
      if (sueltos) fila.appendChild(el("span", "kr-nota v5-sueltos", KR.plural(sueltos, "ensayo sin sede ligada", "ensayos sin sede ligada")));
      bandeja.appendChild(fila);
    }

    // ---------------------------------------------------------------- panel
    function seccion(t, extra) {
      var s = el("section", "v1-sec");
      var h = el("h3", "v1-sec-tit", t); if (extra) h.appendChild(extra);
      s.appendChild(h); panelCuerpo.appendChild(s); return s;
    }
    function pintarPanel() {
      panelCuerpo.innerHTML = "";
      var universo = g.nodos.filter(enAlcance);
      var c = KR.conteos(g, filtros, universo);
      var s0 = seccion(regionSel ? corto(regionSel) : "Chile");
      var p = el("p", "v1-resumen");
      p.appendChild(el("strong", "", KR.miles(c.visibles)));
      if (regionSel) {
        var conDir = g.nodos.filter(function (n) { return n.tipo === "institucion" && n._v5.region === regionSel && n._v5.x !== null; }).length;
        var total = g.nodos.filter(function (n) { return n.tipo === "institucion" && n._v5.region === regionSel; }).length;
        p.appendChild(document.createTextNode(" fichas · " + conDir + " de " + total + " instituciones con dirección"));
      } else p.appendChild(document.createTextNode(" fichas en " + listaLugares.length + " ciudades"));
      s0.appendChild(p);
      if (KR.hayFiltros(filtros)) {
        var q = el("button", "kr-btn kr-btn-chico", "Quitar filtros"); q.type = "button";
        q.addEventListener("click", function () { filtros = KR.filtrosVacios(); cambio(); });
        s0.appendChild(q);
      }
      if (nivel === "pais") {
        var sR = seccion("Regiones");
        var cuenta = {};
        // Mismo criterio que al entrar: un ensayo con sedes en dos regiones cuenta en las dos.
        g.nodos.forEach(function (n) {
          if (!visibles[n.id]) return;
          var rs = n._v5.regiones.length ? n._v5.regiones : n._v5.region ? [n._v5.region] : [];
          rs.forEach(function (r) { cuenta[r] = (cuenta[r] || 0) + 1; });
        });
        var ul = el("ul", "v5-regiones");
        Object.keys(cuenta).sort(function (a, b) { return cuenta[b] - cuenta[a]; }).forEach(function (r) {
          var li = el("li"), b = el("button", "v5-region-btn"); b.type = "button";
          b.appendChild(el("span", "", corto(r))); b.appendChild(el("span", "kr-faceta-num", KR.miles(cuenta[r])));
          b.addEventListener("click", function () { entrarRegion(r); });
          b.addEventListener("mouseenter", function () { hover = { tipo: "region", id: r }; lz.dibujar(); });
          b.addEventListener("mouseleave", function () { hover = null; lz.dibujar(); });
          li.appendChild(b); ul.appendChild(li);
        });
        sR.appendChild(ul);
      }
      var s1 = seccion("Tipo");
      s1.appendChild(KR.faceta({
        filas: KR.TIPOS.map(function (t) { return { clave: t, nombre: KR.TIPO_PLURAL[t], forma: t, color: "var(--" + KR.TIPO_VAR[t] + ")", total: c.tipos[t].total, visibles: c.tipos[t].visibles, activa: filtros.tipos[t] }; }),
        alCambiar: function (t, on) { filtros.tipos[t] = on; cambio(); }
      }));
      var s2 = seccion("Área");
      var areas = verTodasAreas ? c.areas : c.areas.slice(0, 5);
      s2.appendChild(KR.faceta({
        filas: areas.map(function (a) { return { clave: a.area, nombre: a.area.charAt(0).toUpperCase() + a.area.slice(1), total: a.total, visibles: a.visibles, activa: !filtros.areas.length || filtros.areas.indexOf(a.area) !== -1 }; }),
        alCambiar: function (area, on) {
          var todas = KR.conteos(g, KR.filtrosVacios()).areas.map(function (x) { return x.area; });
          if (!filtros.areas.length) filtros.areas = todas.slice();
          if (on && filtros.areas.indexOf(area) === -1) filtros.areas.push(area);
          if (!on) filtros.areas = filtros.areas.filter(function (x) { return x !== area; });
          if (filtros.areas.length === todas.length) filtros.areas = [];
          cambio();
        }
      }));
      if (c.areas.length > 5) {
        var mas = el("button", "kr-btn kr-btn-chico", verTodasAreas ? "Ver menos" : "Ver las " + c.areas.length + " áreas"); mas.type = "button";
        mas.addEventListener("click", function () { verTodasAreas = !verTodasAreas; pintarPanel(); });
        s2.appendChild(mas);
      }
      var s3 = seccion("Año del hecho más reciente");
      s3.appendChild(KR.histograma({ barras: c.barras, rango: filtros.anios, sinFecha: c.sinFecha, alCambiar: function (r) { filtros.anios = r; cambio(); } }));
      var s4 = seccion("Qué comparte tu shortlist");
      s4.appendChild(KR.panelEnComun({ ejemplo: true, alNavegar: irAFicha, alMostrar: function (ids) { profundidad = 1; irAFicha(ids[0]); } }));
      var s5 = seccion("De dónde sale cada ubicación");
      var geoRes = KR._geoCiudad ? KR._geoCiudad.ubicadas.length : 0;
      s5.appendChild(el("p", "kr-nota", geoRes + " de " + g.nodos.filter(function (n) { return n.tipo === "institucion"; }).length +
        " instituciones ubicadas con OpenStreetMap, pendientes de revisión. Las demás van a la bandeja «Sin dirección verificada», no a un punto inventado."));
      s5.appendChild(el("p", "kr-nota", "Límites comunales: geoBoundaries, datos de la BCN (CC BY 3.0 IGO). Mapa base © colaboradores de OpenStreetMap."));
    }

    var leyDin = null;
    function pintarLeyenda() {
      leyenda.innerHTML = "";
      var i1 = el("span"); i1.appendChild(KR.formaSVG("institucion", 10)); i1.appendChild(document.createTextNode("Institución en su dirección")); leyenda.appendChild(i1);
      var i2 = el("span"); i2.appendChild(KR.formaSVG("persona", 10)); i2.appendChild(document.createTextNode("Persona, junto a su institución")); leyenda.appendChild(i2);
      var i3 = el("span"); i3.appendChild(KR.formaSVG("ensayo_clinico", 10)); i3.appendChild(document.createTextNode("▲ N: ensayos; tocá la institución para verlos")); leyenda.appendChild(i3);
      leyDin = el("span", "kr-medidor"); leyenda.appendChild(leyDin);
    }
    function pintarLeyendaDin(nInst) {
      if (!leyDin) return;
      var prom = tiempos.length ? tiempos.reduce(function (a, b) { return a + b; }, 0) / tiempos.length : 0;
      leyDin.textContent = KR.plural(nInst, "institución en pantalla", "instituciones en pantalla") + " · " + prom.toFixed(1).replace(".", ",") + " ms";
    }

    function escribirHash() {
      KR.hash.escribir(filtros, { r: regionSel ? slug(regionSel) : null, c: comunaSel ? slug(comunaSel) : null, d: sel && profundidad === 2 ? "2" : null });
    }
    function cambio() {
      recalcular();
      if (sel && !visibles[sel]) seleccionar(null);
      bandejaFirma = "";
      pintarPanel(); escribirHash(); lz.dibujar();
    }

    KR.autocompletar(input, {
      etiqueta: function (n) { return KR.pasa(n, filtros) ? "" : "oculto por filtros"; },
      alElegir: function (n) { irAFicha(n.id); input.blur(); }
    });
    mapa.appendChild(KR.botonesZoom(lz, function (inm) { if (nivel === "region") { comunaSel = null; pintarMigas(); encuadrarRegion(inm); } else irPais(inm); }));
    function tecla(ev) {
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) return;
      if (ev.key === "Escape") { if (sel) seleccionar(null); else if (comunaSel) { comunaSel = null; encuadrarRegion(false); pintarMigas(); } else if (nivel === "region") irPais(false); }
    }
    document.addEventListener("keydown", tecla);
    limpiezas.push(function () { document.removeEventListener("keydown", tecla); vivo = false; });
    limpiezas.push(KR.shortlist.escuchar(function () { pintarPanel(); lz.dibujar(); }));
    limpiezas.push(KR.alCambiarTema(function () { C = KR.colores(); lz.dibujar(); }));

    cargarGeo().then(function (geo) {
      if (!vivo) return;
      preparar(geo);
      recalcular();
      pintarLeyenda();
      var regionHash = h0.r ? regiones.filter(function (r) { return slug(r.nombre) === h0.r; })[0] : null;
      requestAnimationFrame(function () {
        if (!vivo) return;
        if (regionHash) {
          nivel = "region"; regionSel = regionHash.nombre;
          var ch = h0.c ? porRegion[regionSel].comunas.filter(function (c) { return slug(c.nombre) === h0.c; })[0] : null;
          if (ch) { comunaSel = ch.nombre; lz.animarA(lz.encuadre(ch.caja, 50, 0), 0, true); } else encuadrarRegion(true);
          pintarMigas(); pintarPanel();
        } else irPais(true);
        if (h0.f && g.byId[h0.f]) irAFicha(h0.f);
        if (canvas.animate) canvas.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
      });
    }, function (err) {
      panelCuerpo.innerHTML = "";
      panelCuerpo.appendChild(el("p", "kr-aviso", "No se pudieron cargar los límites o las ubicaciones (" + err.message + ")."));
    });

    return function () { limpiezas.forEach(function (fn) { fn(); }); };
  }

  window.VARIANTES = window.VARIANTES || [];
  window.VARIANTES[4] = { nombre: "Chile → ciudad", montar: montar };
})();
