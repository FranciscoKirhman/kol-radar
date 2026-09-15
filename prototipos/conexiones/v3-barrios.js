/* Prototipo 3 — «Barrios».
 * Eje: DENSIDAD. De lejos, cada institución es una burbuja con su gente y sus ensayos adentro, y
 * las líneas entre burbujas suman las conexiones entre barrios. Al acercarse (o al tocar una)
 * la burbuja se abre en sus fichas. Es la agregación por zoom de flowmap.gl aplicada al grafo,
 * con la apertura de nodos de force-graph. Conserva el cromo del sitio actual (barra de chips).
 * Escala porque lo dibujado depende de cuántos barrios hay, no de cuántas fichas. */
(function () {
  "use strict";
  var KR = window.KR;

  function montar(stage) {
    var el = KR.el;
    var h0 = KR.hash.leer();
    var filtros = KR.hash.aFiltros(h0);
    var grafo = KR.datos.grafo, prueba = false;
    var C = KR.colores(), limpiezas = [];
    var visibles, visE, barrios, listaBarrios, grupoDe, pares;
    var abiertos = {}, prog = {}, animando = false;
    var sel = null, profundidad = h0.d === "2" ? 2 : 1, hover = null, aristaHover = null, resaltadoLista = null;
    var tiempos = [];

    // ---------------------------------------------------------------- estructura
    var raiz = el("div", "variante v3");
    var top = el("header", "kr-top");
    var marca = el("div", "kr-marca");
    marca.appendChild(el("span", "kr-marca-nombre", "KOL Radar"));
    marca.appendChild(el("span", "kr-marca-tag", "oncología · Chile"));
    top.appendChild(marca);
    var bw = el("div", "kr-buscar v3-buscar");
    var input = el("input"); input.type = "search"; input.placeholder = "Buscar por nombre, institución o ensayo…";
    input.setAttribute("aria-label", "Buscar en el mapa");
    bw.appendChild(input); top.appendChild(bw);
    top.appendChild(el("span", "kr-top-sep"));
    var compartir = KR.botonCompartir(function () {
      return { filtros: filtros, ficha: sel ? grafo.byId[sel] : null, extra: { d: profundidad === 2 ? "2" : null } };
    });
    limpiezas.push(compartir.destruir);
    top.appendChild(compartir.el);
    raiz.appendChild(top);
    var barraFiltros = el("div", "v3-filtros");
    raiz.appendChild(barraFiltros);
    raiz.appendChild(KR.lineaBeta());
    var mapa = el("section", "v3-mapa");
    var canvas = el("canvas", "kr-canvas");
    canvas.setAttribute("aria-label", "Mapa por barrios institucionales. Usá la búsqueda para ubicar una ficha.");
    mapa.appendChild(canvas);
    var tooltip = el("div", "kr-tooltip"); tooltip.hidden = true; mapa.appendChild(tooltip);
    var barraFoco = el("div", "v1-foco v3-foco"); barraFoco.hidden = true; mapa.appendChild(barraFoco);
    var acciones = el("div", "v3-acciones"); mapa.appendChild(acciones);
    var leyenda = el("div", "kr-leyenda v1-leyenda"); mapa.appendChild(leyenda);
    var drawer = el("aside", "kr-drawer"); drawer.setAttribute("inert", "");
    var drawerCerrar = el("button", "kr-drawer-cerrar", "✕"); drawerCerrar.type = "button"; drawerCerrar.setAttribute("aria-label", "Cerrar");
    var drawerCuerpo = el("div", "kr-drawer-cuerpo");
    drawer.appendChild(drawerCerrar); drawer.appendChild(drawerCuerpo); mapa.appendChild(drawer);
    raiz.appendChild(mapa);
    stage.appendChild(raiz);

    // ---------------------------------------------------------------- modelo de barrios
    function recalcular() {
      visibles = {};
      grafo.nodos.forEach(function (n) { if (KR.pasa(n, filtros)) visibles[n.id] = true; });
      visE = grafo.vinculos.filter(function (v) { return visibles[v.origen] && visibles[v.destino]; });
      barrios = {}; grupoDe = {};
      grafo.nodos.forEach(function (n) {
        if (!visibles[n.id]) return;
        var key = n.tipo === "institucion" ? n.id : (n._ancla && grafo.byId[n._ancla] ? n._ancla : "@sin");
        var b = barrios[key];
        if (!b) {
          var inst = key === "@sin" ? null : grafo.byId[key];
          b = barrios[key] = { id: key, inst: inst, nombre: inst ? KR.etiquetaCorta(inst) : "Sin institución ligada", miembros: [], internas: [],
            cuenta: { persona: 0, institucion: 0, ensayo_clinico: 0 }, x: inst ? inst._x : 0, y: inst ? inst._y : 0 };
        }
        b.miembros.push(n); b.cuenta[n.tipo]++; grupoDe[n.id] = key;
      });
      listaBarrios = Object.keys(barrios).map(function (k) { return barrios[k]; });
      listaBarrios.forEach(function (b) {
        if (!b.inst) {
          var sx = 0, sy = 0;
          b.miembros.forEach(function (n) { sx += n._x; sy += n._y; });
          b.x = sx / b.miembros.length; b.y = sy / b.miembros.length;
        }
        var ds = b.miembros.map(function (n) { return Math.hypot(n._x - b.x, n._y - b.y); }).sort(function (a, c) { return a - c; });
        b.radioMundo = Math.max(24, ds[Math.floor(ds.length * 0.85)] || 24);
        b.rBurbuja = 7 + Math.sqrt(b.miembros.length) * 3.2;
        if (prog[b.id] === undefined) prog[b.id] = 0;
      });
      listaBarrios.sort(function (a, c) { return c.miembros.length - a.miembros.length; });
      pares = {};
      visE.forEach(function (v) {
        var ga = grupoDe[v.origen], gb = grupoDe[v.destino];
        if (ga === gb) { barrios[ga].internas.push(v); return; }
        var k = ga < gb ? ga + "|" + gb : gb + "|" + ga;
        (pares[k] = pares[k] || { a: barrios[ga < gb ? ga : gb], b: barrios[ga < gb ? gb : ga], vinculos: [] }).vinculos.push(v);
      });
      pares = Object.keys(pares).map(function (k) { return pares[k]; });
    }

    function focoActual() {
      if (hover && hover.tipo === "nodo") return KR.vecindario(grafo, hover.id, 1, function (n) { return visibles[n.id]; });
      if (sel && visibles[sel]) return KR.vecindario(grafo, sel, profundidad, function (n) { return visibles[n.id]; });
      return null;
    }
    // Un barrio está abierto si el usuario lo abrió, si contiene lo que está en foco, o si de tan
    // cerca que se ve ya no tiene sentido mostrarlo como burbuja (zoom semántico).
    function debeAbrirse(b, lz) {
      if (abiertos[b.id] === false) return false;
      if (abiertos[b.id]) return true;
      if (b.miembros.length < 2) return false;
      var foco = sel ? focoSel : null;
      if (foco && b.miembros.some(function (n) { return foco[n.id] !== undefined; })) return true;
      // "Sin institución ligada" no es un barrio de verdad (sus fichas están repartidas por todo el
      // lienzo): solo se abre si el usuario lo pide.
      if (b.id === "@sin") return false;
      var s = lz.aPantalla(b.x, b.y);
      var enVista = s[0] > -200 && s[0] < lz.w + 200 && s[1] > -200 && s[1] < lz.h + 200;
      return enVista && lz.cam.k >= 1.5 && b.radioMundo * lz.cam.k > 120;
    }
    var focoSel = null;

    function avanzarAnimacion(dt, lz) {
      var sigue = false;
      listaBarrios.forEach(function (b) {
        var meta = debeAbrirse(b, lz) ? 1 : 0;
        if (KR.reducirMovimiento()) { prog[b.id] = meta; return; }
        if (prog[b.id] !== meta) {
          var paso = dt / 240;
          prog[b.id] = meta > prog[b.id] ? Math.min(meta, prog[b.id] + paso) : Math.max(meta, prog[b.id] - paso * 1.4);
          if (prog[b.id] !== meta) sigue = true;
        }
      });
      return sigue;
    }

    function posDe(n, lz) {
      var b = barrios[grupoDe[n.id]], t = KR.easeOut(prog[b.id]);
      return lz.aPantalla(b.x + (n._x - b.x) * t, b.y + (n._y - b.y) * t);
    }
    function radioNodo(n, k) {
      var base = n.tipo === "institucion" ? 5.5 : n.tipo === "persona" ? 4.2 : 2.6;
      return Math.max(1.6, Math.min(20, (base + Math.min(n._grado, 30) * 0.14) * Math.max(0.5, Math.min(2.4, Math.sqrt(k)))));
    }
    function radioBurbuja(b, k) { return Math.max(5, Math.min(70, b.rBurbuja * Math.max(0.35, Math.min(1.6, Math.sqrt(k))))); }

    // ---------------------------------------------------------------- dibujo
    var ultimo = null;
    function dibujar(ctx, lz) {
      var ahora = performance.now(), dt = ultimo ? Math.min(64, ahora - ultimo) : 16;
      ultimo = ahora;
      focoSel = sel && visibles[sel] ? KR.vecindario(grafo, sel, profundidad, function (n) { return visibles[n.id]; }) : null;
      animando = avanzarAnimacion(dt, lz);
      var k = lz.cam.k, foco = focoActual();
      var hb = hover && hover.tipo === "barrio" ? hover.id : null;
      var byId = grafo.byId;
      ctx.lineCap = "round";

      // 1) Conexiones entre barrios: sumadas si los dos están cerrados, una por una si alguno se abrió.
      var sumadas = [];
      ctx.beginPath();
      pares.forEach(function (par) {
        var ta = prog[par.a.id], tb = prog[par.b.id];
        if (ta === 0 && tb === 0) { sumadas.push(par); return; }
        par.vinculos.forEach(function (v) {
          if (foco && (foco[v.origen] === undefined || foco[v.destino] === undefined)) return;
          var p = posDe(byId[v.origen], lz), q = posDe(byId[v.destino], lz);
          ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]);
        });
      });
      listaBarrios.forEach(function (b) {
        if (!prog[b.id]) return;
        b.internas.forEach(function (v) {
          if (foco && (foco[v.origen] === undefined || foco[v.destino] === undefined)) return;
          var p = posDe(byId[v.origen], lz), q = posDe(byId[v.destino], lz);
          ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]);
        });
      });
      ctx.strokeStyle = foco ? C.texto2 : C.tenue; ctx.globalAlpha = foco ? 0.45 : 0.22; ctx.lineWidth = 1; ctx.stroke();

      sumadas.forEach(function (par) {
        var enFoco = !hb || par.a.id === hb || par.b.id === hb;
        if (hb && !enFoco) return;
        if (foco) {
          var toca = par.vinculos.some(function (v) { return foco[v.origen] !== undefined && foco[v.destino] !== undefined; });
          if (!toca) return;
        }
        var p = lz.aPantalla(par.a.x, par.a.y), q = lz.aPantalla(par.b.x, par.b.y);
        ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]);
        var ancho = 0.8 + Math.log2(1 + par.vinculos.length) * 1.3;
        ctx.lineWidth = ancho;
        ctx.strokeStyle = hb || aristaHover === par ? C.acento : C.tenue;
        ctx.globalAlpha = hb || aristaHover === par ? 0.9 : 0.3;
        ctx.stroke();
      });
      if (aristaHover && aristaHover.vinculo) {
        var av = aristaHover.vinculo, pa = posDe(byId[av.origen], lz), pb = posDe(byId[av.destino], lz);
        ctx.beginPath(); ctx.moveTo(pa[0], pa[1]); ctx.lineTo(pb[0], pb[1]);
        ctx.strokeStyle = C.acento; ctx.globalAlpha = 1; ctx.lineWidth = 3; ctx.stroke();
      }

      // 2) Burbujas cerradas: tamaño por fichas, anillo con la mezcla de tipos.
      listaBarrios.forEach(function (b) {
        var alfa = 1 - KR.easeOut(prog[b.id]);
        if (alfa <= 0.01) return;
        var s = lz.aPantalla(b.x, b.y), r = radioBurbuja(b, k);
        if (s[0] < -r || s[1] < -r || s[0] > lz.w + r || s[1] > lz.h + r) return;
        var atenuar = (hb && hb !== b.id && !pares.some(function (par) { return (par.a.id === hb && par.b.id === b.id) || (par.b.id === hb && par.a.id === b.id); })) ||
          (foco && !b.miembros.some(function (n) { return foco[n.id] !== undefined; }));
        ctx.globalAlpha = alfa * (atenuar ? 0.2 : 1);
        ctx.beginPath(); ctx.arc(s[0], s[1], r, 0, Math.PI * 2);
        ctx.fillStyle = C.s2; ctx.fill();
        var total = b.miembros.length, ang = -Math.PI / 2;
        KR.TIPOS.forEach(function (t) {
          if (!b.cuenta[t]) return;
          var a1 = ang + (b.cuenta[t] / total) * Math.PI * 2;
          ctx.beginPath(); ctx.arc(s[0], s[1], r, ang, a1);
          ctx.strokeStyle = C[t]; ctx.lineWidth = Math.max(2, Math.min(5, r * 0.18)); ctx.stroke();
          ang = a1;
        });
        if (hb === b.id) { ctx.beginPath(); ctx.arc(s[0], s[1], r + 4, 0, Math.PI * 2); ctx.strokeStyle = C.texto; ctx.lineWidth = 1.5; ctx.stroke(); }
      });

      // 3) Barrios abiertos: contorno punteado y sus fichas saliendo desde el centro.
      KR.TIPOS.forEach(function (t) {
        [true, false].forEach(function (dim) {
          ctx.beginPath();
          var hay = false, alfaMax = 0;
          listaBarrios.forEach(function (b) {
            var tt = KR.easeOut(prog[b.id]);
            if (tt <= 0.01) return;
            alfaMax = Math.max(alfaMax, tt);
            b.miembros.forEach(function (n) {
              if (n.tipo !== t) return;
              var dentro = !foco || foco[n.id] !== undefined;
              if (dentro === dim) return;
              var s = posDe(n, lz);
              if (s[0] < -20 || s[1] < -20 || s[0] > lz.w + 20 || s[1] > lz.h + 20) return;
              KR.trazarForma(ctx, t, s[0], s[1], radioNodo(n, k) * (0.4 + 0.6 * tt));
              hay = true;
            });
          });
          if (!hay) return;
          ctx.fillStyle = C[t]; ctx.globalAlpha = alfaMax * (dim ? 0.12 : 1); ctx.fill();
        });
      });
      listaBarrios.forEach(function (b) {
        var tt = KR.easeOut(prog[b.id]);
        if (tt <= 0.05 || b.miembros.length < 2) return;
        // El contorno solo marca los barrios que se abrieron a propósito o que tienen lo que está
        // en foco. Los que abre el zoom no lo llevan: con 40 abiertos, 40 círculos eran ruido.
        if (!abiertos[b.id] && !(focoSel && b.miembros.some(function (n) { return focoSel[n.id] !== undefined; }))) return;
        var s = lz.aPantalla(b.x, b.y), r = b.radioMundo * k * tt + 14;
        ctx.beginPath(); ctx.arc(s[0], s[1], r, 0, Math.PI * 2);
        ctx.setLineDash([4, 5]); ctx.strokeStyle = C.borde; ctx.globalAlpha = tt; ctx.lineWidth = 1.2; ctx.stroke(); ctx.setLineDash([]);
      });
      ctx.globalAlpha = 1;
      var sl = KR.shortlist.lista();
      sl.forEach(function (id) {
        var n = byId[id]; if (!n || !visibles[id] || prog[grupoDe[id]] < 0.5) return;
        var s = posDe(n, lz); ctx.beginPath(); ctx.arc(s[0], s[1], radioNodo(n, k) + 3.5, 0, Math.PI * 2);
        ctx.strokeStyle = C.acento; ctx.lineWidth = 2; ctx.stroke();
      });
      [sel, hover && hover.tipo === "nodo" ? hover.id : null, resaltadoLista].forEach(function (id, i) {
        if (!id || !visibles[id] || prog[grupoDe[id]] < 0.5) return;
        var n = byId[id], s = posDe(n, lz);
        KR.dibujarForma(ctx, n.tipo, s[0], s[1], radioNodo(n, k) + (i === 0 ? 2.5 : 1.5));
        ctx.strokeStyle = C.texto; ctx.lineWidth = i === 0 ? 2.5 : 1.5; ctx.stroke();
      });

      // 4) Etiquetas por nivel de detalle: barrios cerrados primero, fichas de barrios abiertos después.
      ctx.font = KR.FUENTE_CANVAS;
      var cands = [], maxEt = Math.floor((lz.w * lz.h) / 7500);
      if (sel && visibles[sel] && prog[grupoDe[sel]] > 0.5) {
        var ns = byId[sel], ps = posDe(ns, lz);
        cands.push({ sx: ps[0], sy: ps[1], r: radioNodo(ns, k), texto: KR.etiquetaCorta(ns), n: ns, ancho: ns._tw, fuerte: true });
      }
      listaBarrios.forEach(function (b) {
        if (prog[b.id] > 0.5) return;
        if (foco && !b.miembros.some(function (n) { return foco[n.id] !== undefined; })) return;
        var s = lz.aPantalla(b.x, b.y);
        b._txt = b._txt || (b.nombre + " · " + KR.miles(b.miembros.length));
        cands.push({ sx: s[0], sy: s[1], r: radioBurbuja(b, k), texto: b._txt, ancho: b._tw, n: b, fuerte: hb === b.id });
      });
      listaBarrios.forEach(function (b) {
        if (prog[b.id] < 0.5) return;
        var ordenados = b._ordenados || (b._ordenados = b.miembros.slice().sort(function (x, y) {
          var p = { persona: 0, institucion: 1, ensayo_clinico: 2 };
          return p[x.tipo] - p[y.tipo] || y._grado - x._grado;
        }));
        ordenados.forEach(function (n) {
          if (foco && foco[n.id] === undefined) return;
          if (n.tipo === "ensayo_clinico" && k < 1.8 && !foco) return;
          var s = posDe(n, lz);
          cands.push({ sx: s[0], sy: s[1], r: radioNodo(n, k), texto: n._txt || (n._txt = KR.etiquetaCorta(n)), ancho: n._tw, n: n, fuerte: !!foco });
        });
      });
      var puestas = KR.colocarEtiquetas(ctx, cands, lz.w, lz.h, maxEt);
      ctx.textBaseline = "middle"; ctx.lineJoin = "round";
      puestas.forEach(function (pu) {
        ctx.lineWidth = 3; ctx.strokeStyle = C.s0; ctx.globalAlpha = 0.9; ctx.strokeText(pu.c.texto, pu.x, pu.y);
        ctx.globalAlpha = 1; ctx.fillStyle = pu.c.fuerte ? C.texto : C.texto2; ctx.fillText(pu.c.texto, pu.x, pu.y);
      });
      if (animando) lz.dibujar();
      else ultimo = null;
    }

    var lz = KR.lienzo(canvas, {
      minK: 0.04, maxK: 14, alDibujar: dibujar,
      alMedir: function (ms) { tiempos.push(ms); if (tiempos.length > 30) tiempos.shift(); pintarResumen(); },
      alMover: function (sx, sy) { apuntar(sx, sy); },
      alSalir: function () { estable.poner(null); aristaHover = null; tooltip.hidden = true; lz.dibujar(); },
      alClick: function (sx, sy) { tocar(sx, sy); },
      alCamara: function () { lz.dibujar(); }
    });
    limpiezas.push(lz.destruir);
    var estable = KR.hoverEstable(function (clave) {
      hover = clave ? (clave.indexOf("b:") === 0 ? { tipo: "barrio", id: clave.slice(2) } : { tipo: "nodo", id: clave.slice(2) }) : null;
      lz.dibujar();
    });

    // ---------------------------------------------------------------- puntería
    function queHay(sx, sy) {
      var k = lz.cam.k, mejor = null, d0 = Infinity;
      listaBarrios.forEach(function (b) {
        if (prog[b.id] > 0.5) {
          b.miembros.forEach(function (n) {
            var s = posDe(n, lz), d = Math.hypot(s[0] - sx, s[1] - sy);
            if (d < Math.max(6, radioNodo(n, k) + 3) && d < d0) { d0 = d; mejor = { tipo: "nodo", n: n }; }
          });
        } else {
          var s = lz.aPantalla(b.x, b.y), d = Math.hypot(s[0] - sx, s[1] - sy);
          if (d < radioBurbuja(b, k) + 3 && d < d0) { d0 = d; mejor = { tipo: "barrio", b: b }; }
        }
      });
      if (mejor) return mejor;
      var dMejor = 5;
      pares.forEach(function (par) {
        if (prog[par.a.id] || prog[par.b.id]) {
          par.vinculos.forEach(function (v) {
            var p = posDe(grafo.byId[v.origen], lz), q = posDe(grafo.byId[v.destino], lz), dd = distSeg(sx, sy, p, q);
            if (dd < dMejor) { dMejor = dd; mejor = { tipo: "vinculo", v: v }; }
          });
          return;
        }
        var p = lz.aPantalla(par.a.x, par.a.y), q = lz.aPantalla(par.b.x, par.b.y), dd = distSeg(sx, sy, p, q);
        if (dd < dMejor) { dMejor = dd; mejor = { tipo: "par", par: par }; }
      });
      return mejor;
    }
    function distSeg(sx, sy, p, q) {
      var dx = q[0] - p[0], dy = q[1] - p[1], L = dx * dx + dy * dy || 1;
      var t = Math.max(0, Math.min(1, ((sx - p[0]) * dx + (sy - p[1]) * dy) / L));
      return Math.hypot(sx - (p[0] + t * dx), sy - (p[1] + t * dy));
    }
    function mostrarTooltip(sx, sy, titulo, sub, extra) {
      tooltip.innerHTML = "";
      tooltip.appendChild(el("div", "kr-tooltip-tit", titulo));
      if (sub) tooltip.appendChild(el("div", "kr-tooltip-sub", sub));
      if (extra) tooltip.appendChild(extra);
      tooltip.hidden = false;
      tooltip.style.transform = "translate(" + Math.max(8, Math.min(sx + 14, lz.w - tooltip.offsetWidth - 8)) + "px," + Math.max(8, Math.min(sy + 14, lz.h - tooltip.offsetHeight - 8)) + "px)";
    }
    function resumenCuenta(c) {
      return KR.TIPOS.filter(function (t) { return c[t]; }).map(function (t) {
        return c[t] + " " + (c[t] === 1 ? KR.TIPO_LABEL[t] : KR.TIPO_PLURAL[t]).toLowerCase();
      }).join(", ");
    }
    function apuntar(sx, sy) {
      var q = queHay(sx, sy);
      aristaHover = null;
      if (!q) { estable.poner(null); tooltip.hidden = true; canvas.style.cursor = ""; lz.dibujar(); return; }
      canvas.style.cursor = "pointer";
      if (q.tipo === "nodo") {
        estable.poner("n:" + q.n.id);
        mostrarTooltip(sx, sy, q.n.nombre, KR.TIPO_LABEL[q.n.tipo] + " · " + grafo.adj[q.n.id].length + " conexiones");
      } else if (q.tipo === "barrio") {
        estable.poner("b:" + q.b.id);
        var vecinos = pares.filter(function (p) { return p.a === q.b || p.b === q.b; }).length;
        mostrarTooltip(sx, sy, q.b.nombre, resumenCuenta(q.b.cuenta) + " · conectado con " + KR.plural(vecinos, "barrio", "barrios") + " · click para abrir");
      } else {
        estable.poner(null);
        aristaHover = q.tipo === "par" ? q.par : { vinculo: q.v };
        if (q.tipo === "par") {
          mostrarTooltip(sx, sy, q.par.a.nombre + " ↔ " + q.par.b.nombre, KR.plural(q.par.vinculos.length, "conexión", "conexiones") + " · click para ver cuáles y su fuente");
        } else {
          var ex = el("div", "kr-tooltip-ev"); ex.appendChild(KR.insigniaEvidencia(KR.evidencia(q.v)));
          mostrarTooltip(sx, sy, grafo.byId[q.v.origen].nombre + " ↔ " + grafo.byId[q.v.destino].nombre, q.v.tipo, ex);
        }
      }
      lz.dibujar();
    }
    function tocar(sx, sy) {
      var q = queHay(sx, sy);
      if (!q) { seleccionar(null); return; }
      if (q.tipo === "nodo") seleccionar(q.n.id, false);
      else if (q.tipo === "barrio") abrirBarrio(q.b, true);
      else if (q.tipo === "par") abrirPar(q.par);
      else abrirPar({ a: barrios[grupoDe[q.v.origen]], b: barrios[grupoDe[q.v.destino]], vinculos: [q.v] });
    }

    // ---------------------------------------------------------------- hoja lateral
    function abrirDrawer(contenido) {
      if (drawerCuerpo.firstChild && drawerCuerpo.firstChild._destruir) drawerCuerpo.firstChild._destruir();
      drawerCuerpo.innerHTML = ""; drawerCuerpo.appendChild(contenido); drawerCuerpo.scrollTop = 0;
      drawer.classList.add("abierto"); drawer.removeAttribute("inert");
    }
    function cerrarDrawer() { drawer.classList.remove("abierto"); drawer.setAttribute("inert", ""); }
    drawerCerrar.addEventListener("click", function () { seleccionar(null); });

    function seleccionar(id, volar) {
      sel = id;
      if (!id) { cerrarDrawer(); pintarFoco(); lz.dibujar(); return; }
      var n = grafo.byId[id];
      abiertos[grupoDe[id]] = true;
      abrirDrawer(KR.ficha(n, {
        alNavegar: function (otro) { seleccionar(otro, true); },
        alResaltar: function (otro) { resaltadoLista = otro; lz.dibujar(); }
      }));
      pintarFoco();
      if (volar) volarA(n._x, n._y, 2);
      lz.dibujar();
    }
    function volarA(x, y, kMin) {
      var b = lz.base(), k = Math.max(b.k, kMin);
      var d = Math.hypot(x - lz.cam.cx, y - lz.cam.cy) * lz.cam.k;
      lz.animarA({ cx: x + Math.min(200, lz.w * 0.18) / k, cy: y, k: k }, Math.min(520, 280 + d * 0.25), false, KR.easeInOut);
    }
    function abrirBarrio(b, volar) {
      abiertos[b.id] = true;
      sel = null;
      var art = el("article", "kr-ficha");
      var cab = el("header", "kr-ficha-cab");
      cab.appendChild(el("span", "kr-ficha-tipo", "Barrio institucional"));
      cab.appendChild(el("h2", "kr-ficha-nombre", b.inst ? b.inst.nombre : b.nombre));
      cab.appendChild(el("p", "kr-ficha-sub", resumenCuenta(b.cuenta) + " agrupadas por su primera institución conectada."));
      art.appendChild(cab);
      var acc = el("div", "kr-ficha-acciones");
      if (b.inst) {
        var vf = el("button", "kr-btn", "Ver ficha de la institución"); vf.type = "button";
        vf.addEventListener("click", function () { seleccionar(b.inst.id, false); });
        acc.appendChild(vf);
      }
      var cerrar = el("button", "kr-btn", "Cerrar barrio en el mapa"); cerrar.type = "button";
      cerrar.addEventListener("click", function () { abiertos[b.id] = false; cerrarDrawer(); lz.dibujar(); });
      acc.appendChild(cerrar);
      art.appendChild(acc);
      var conexiones = pares.filter(function (p) { return p.a === b || p.b === b; })
        .sort(function (x, y) { return y.vinculos.length - x.vinculos.length; });
      art.appendChild(el("h3", "kr-ficha-sec", "Conectado con " + KR.plural(conexiones.length, "barrio", "barrios")));
      var ulp = el("ul", "kr-con-lista");
      conexiones.slice(0, 12).forEach(function (p) {
        var otro = p.a === b ? p.b : p.a;
        var li = el("li", "kr-con"), fila = el("div", "kr-con-fila");
        var bt = el("button", "kr-con-nombre", otro.nombre); bt.type = "button";
        bt.addEventListener("click", function () { abrirPar(p); });
        fila.appendChild(bt); fila.appendChild(el("span", "kr-con-tipo", p.vinculos.length + " conexiones"));
        li.appendChild(fila); ulp.appendChild(li);
      });
      art.appendChild(ulp);
      KR.TIPOS.forEach(function (t) {
        var ms = b.miembros.filter(function (n) { return n.tipo === t; });
        if (!ms.length) return;
        art.appendChild(el("h3", "kr-ficha-sec", KR.TIPO_PLURAL[t] + " · " + ms.length));
        var ul = el("ul", "kr-con-lista");
        ms.slice(0, 30).forEach(function (n) {
          var li = el("li", "kr-con"), bt = el("button", "kr-con-nombre", n.nombre); bt.type = "button";
          bt.addEventListener("click", function () { seleccionar(n.id, true); });
          bt.addEventListener("mouseenter", function () { resaltadoLista = n.id; lz.dibujar(); });
          bt.addEventListener("mouseleave", function () { resaltadoLista = null; lz.dibujar(); });
          li.appendChild(bt); ul.appendChild(li);
        });
        if (ms.length > 30) ul.appendChild(el("li", "kr-nota", "+" + (ms.length - 30) + " más"));
        art.appendChild(ul);
      });
      abrirDrawer(art);
      pintarFoco();
      if (volar) {
        var caja = { x0: b.x - b.radioMundo, x1: b.x + b.radioMundo, y0: b.y - b.radioMundo, y1: b.y + b.radioMundo };
        var dest = lz.encuadre(caja, 60); dest.k = Math.min(Math.max(dest.k, lz.cam.k), 5);
        dest.cx += Math.min(200, lz.w * 0.18) / dest.k;
        lz.animarA(dest, 420, false, KR.easeInOut);
      }
      lz.dibujar();
    }
    function abrirPar(par) {
      var art = el("article", "kr-ficha");
      var cab = el("header", "kr-ficha-cab");
      cab.appendChild(el("span", "kr-ficha-tipo", "Entre dos barrios"));
      cab.appendChild(el("h2", "kr-ficha-nombre kr-ficha-nombre-chico", par.a.nombre + " ↔ " + par.b.nombre));
      var porTipo = {};
      par.vinculos.forEach(function (v) { porTipo[v.tipo] = (porTipo[v.tipo] || 0) + 1; });
      cab.appendChild(el("p", "kr-ficha-sub", par.vinculos.length + " conexiones: " + Object.keys(porTipo).map(function (t) { return porTipo[t] + " " + t; }).join(", ")));
      art.appendChild(cab);
      art.appendChild(el("h3", "kr-ficha-sec", "Cada conexión y su fuente"));
      var ul = el("ul", "kr-con-lista");
      par.vinculos.slice(0, 40).forEach(function (v) {
        var ev = KR.evidencia(v), li = el("li", "kr-con"), fila = el("div", "kr-con-fila");
        var a = grafo.byId[v.origen], bb = grafo.byId[v.destino];
        var bt = el("button", "kr-con-nombre", KR.etiquetaCorta(a) + " ↔ " + KR.etiquetaCorta(bb)); bt.type = "button";
        bt.addEventListener("click", function () { seleccionar(a.tipo === "persona" ? a.id : bb.id, true); });
        bt.addEventListener("mouseenter", function () { aristaHover = { vinculo: v }; lz.dibujar(); });
        bt.addEventListener("mouseleave", function () { aristaHover = null; lz.dibujar(); });
        fila.appendChild(bt); fila.appendChild(el("span", "kr-con-tipo", v.tipo));
        var exp = el("button", "kr-con-ev"); exp.type = "button"; exp.appendChild(KR.insigniaEvidencia(ev));
        var det = null;
        exp.addEventListener("click", function () { if (!det) { det = KR.detalleEvidencia(ev); li.appendChild(det); } else det.hidden = !det.hidden; });
        fila.appendChild(exp); li.appendChild(fila); ul.appendChild(li);
      });
      if (par.vinculos.length > 40) ul.appendChild(el("li", "kr-nota", "+" + (par.vinculos.length - 40) + " más"));
      art.appendChild(ul);
      sel = null; abrirDrawer(art); pintarFoco(); lz.dibujar();
    }

    function pintarFoco() {
      barraFoco.innerHTML = "";
      if (!sel) { barraFoco.hidden = true; return; }
      barraFoco.hidden = false;
      var t = el("span"); t.appendChild(document.createTextNode("Red de ")); t.appendChild(el("strong", "", KR.etiquetaCorta(grafo.byId[sel])));
      barraFoco.appendChild(t);
      var seg = el("div", "kr-seg");
      [1, 2].forEach(function (d) {
        var b = el("button", "kr-seg-btn", d === 1 ? "Directas" : "A 2 saltos"); b.type = "button";
        b.setAttribute("aria-pressed", String(profundidad === d));
        b.addEventListener("click", function () { profundidad = d; pintarFoco(); lz.dibujar(); KR.hash.escribir(filtros, { d: d === 2 ? "2" : null }); });
        seg.appendChild(b);
      });
      barraFoco.appendChild(seg);
      var x = el("button", "kr-btn kr-btn-chico", "Ver todo"); x.type = "button";
      x.addEventListener("click", function () { seleccionar(null); abiertos = {}; restablecer(false); });
      barraFoco.appendChild(x);
    }

    // ---------------------------------------------------------------- barra de filtros
    var pops = [];
    function pintarFiltros() {
      // Si un desplegable estaba abierto (se está tildando áreas), se reabre tras repintar.
      var abierto = -1;
      pops.forEach(function (p, i) { if (!p.el.hidden) abierto = i; p.destruir(); }); pops = [];
      barraFiltros.innerHTML = "";
      var c = KR.conteos(grafo, filtros, KR.datos.grafo.nodos);
      KR.TIPOS.forEach(function (t) {
        var b = el("button", "v3-chip"); b.type = "button";
        b.setAttribute("aria-pressed", String(filtros.tipos[t]));
        b.appendChild(KR.formaSVG(t, 9));
        b.appendChild(document.createTextNode(KR.TIPO_PLURAL[t]));
        b.appendChild(el("span", "v3-chip-num", c.tipos[t].visibles === c.tipos[t].total ? KR.miles(c.tipos[t].total) : KR.miles(c.tipos[t].visibles) + "/" + KR.miles(c.tipos[t].total)));
        b.addEventListener("click", function () { filtros.tipos[t] = !filtros.tipos[t]; cambio(); });
        barraFiltros.appendChild(b);
      });
      barraFiltros.appendChild(el("span", "v3-sep"));
      function chipPop(texto, activo, contenido) {
        var b = el("button", "v3-chip" + (activo ? " activo" : ""), texto + " ▾"); b.type = "button";
        barraFiltros.appendChild(b);
        pops.push(KR.popover(b, contenido, { alinear: "izquierda" }));
      }
      var cuerpoAreas = el("div");
      cuerpoAreas.appendChild(el("p", "kr-compartir-titulo", "Áreas"));
      cuerpoAreas.appendChild(KR.faceta({
        filas: c.areas.map(function (a) {
          return { clave: a.area, nombre: a.area.charAt(0).toUpperCase() + a.area.slice(1), total: a.total, visibles: a.visibles, activa: !filtros.areas.length || filtros.areas.indexOf(a.area) !== -1 };
        }),
        alCambiar: function (area, on) {
          if (!filtros.areas.length) filtros.areas = c.areas.map(function (x) { return x.area; });
          if (on && filtros.areas.indexOf(area) === -1) filtros.areas.push(area);
          if (!on) filtros.areas = filtros.areas.filter(function (x) { return x !== area; });
          if (filtros.areas.length === c.areas.length) filtros.areas = [];
          cambio();
        }
      }));
      cuerpoAreas.firstChild.nextSibling.classList.add("v3-faceta-scroll");
      chipPop(filtros.areas.length ? "Áreas: " + filtros.areas.length : "Áreas", filtros.areas.length > 0, cuerpoAreas);
      var cuerpoAnios = el("div");
      cuerpoAnios.appendChild(el("p", "kr-compartir-titulo", "Año del hecho más reciente"));
      cuerpoAnios.appendChild(KR.histograma({ barras: c.barras, rango: filtros.anios, sinFecha: c.sinFecha, alCambiar: function (r) { filtros.anios = r; cambio(); } }));
      chipPop(filtros.anios ? "Años: " + filtros.anios.join("–") : "Años", !!filtros.anios, cuerpoAnios);
      var cuerpoSL = el("div");
      cuerpoSL.appendChild(el("p", "kr-compartir-titulo", "Qué comparte tu shortlist"));
      cuerpoSL.appendChild(KR.panelEnComun({
        ejemplo: true,
        alNavegar: function (id) { seleccionar(id, true); },
        alMostrar: function (ids) { seleccionar(ids[0], true); profundidad = 2; pintarFoco(); }
      }));
      chipPop("Shortlist (" + KR.shortlist.lista().length + ")", KR.shortlist.lista().length > 0, cuerpoSL);
      if (KR.hayFiltros(filtros)) {
        var q = el("button", "v3-limpiar", "Quitar filtros"); q.type = "button";
        q.addEventListener("click", function () { filtros = KR.filtrosVacios(); cambio(); });
        barraFiltros.appendChild(q);
      }
      resumen = el("span", "v3-resumen");
      barraFiltros.appendChild(resumen);
      pintarResumen();
      if (abierto !== -1 && pops[abierto]) pops[abierto].abrir();
    }
    var resumen = null;
    function pintarResumen() {
      if (!resumen) return;
      var abiertosN = listaBarrios.filter(function (b) { return prog[b.id] > 0.5; }).length;
      var prom = tiempos.length ? tiempos.reduce(function (a, b) { return a + b; }, 0) / tiempos.length : 0;
      resumen.textContent = KR.miles(Object.keys(visibles).length) + " fichas en " + listaBarrios.length + " barrios · " + abiertosN + " abiertos" +
        (prom ? " · " + prom.toFixed(1).replace(".", ",") + " ms" : "");
    }

    function pintarLeyenda() {
      leyenda.innerHTML = "";
      var burb = el("span"); burb.appendChild(el("i", "v3-ley-burbuja")); burb.appendChild(document.createTextNode("Barrio: tamaño = fichas, anillo = mezcla de tipos"));
      leyenda.appendChild(burb);
      leyenda.appendChild(el("span", "", "Línea gruesa = más conexiones entre barrios"));
      KR.TIPOS.forEach(function (t) { var s = el("span"); s.appendChild(KR.formaSVG(t, 9)); s.appendChild(document.createTextNode(KR.TIPO_LABEL[t])); leyenda.appendChild(s); });
      var lab = el("label", "kr-check v3-prueba");
      var cb = el("input"); cb.type = "checkbox"; cb.checked = prueba;
      lab.appendChild(cb); lab.appendChild(el("span", "", "Prueba de carga ×10 (sintética)"));
      cb.addEventListener("change", function () {
        prueba = cb.checked; grafo = prueba ? KR.pruebaDeCarga(10) : KR.datos.grafo;
        abiertos = {}; prog = {}; seleccionar(null); recalcular(); pintarFiltros(); restablecer(false);
      });
      leyenda.appendChild(lab);
    }

    function pintarAcciones() {
      acciones.innerHTML = "";
      var cerrarTodos = el("button", "kr-btn kr-btn-chico", "Cerrar barrios"); cerrarTodos.type = "button";
      cerrarTodos.addEventListener("click", function () {
        listaBarrios.forEach(function (b) { abiertos[b.id] = false; });
        seleccionar(null); lz.dibujar();
        setTimeout(function () { abiertos = {}; }, 400);
      });
      acciones.appendChild(cerrarTodos);
    }

    function cambio() {
      recalcular();
      if (sel && !visibles[sel]) seleccionar(null);
      pintarFiltros();
      KR.hash.escribir(filtros, { d: sel && profundidad === 2 ? "2" : null });
      lz.dibujar();
    }
    function restablecer(inmediato) { lz.animarA(lz.encuadre(grafo.caja, 50), 380, inmediato, KR.easeInOut); }

    KR.autocompletar(input, {
      etiqueta: function (n) { return KR.pasa(n, filtros) ? "" : "oculto por filtros"; },
      alElegir: function (n) {
        if (!KR.pasa(n, filtros)) { filtros = KR.filtrosVacios(); cambio(); }
        seleccionar(n.id, true); input.blur();
      }
    });
    mapa.appendChild(KR.botonesZoom(lz, function (inm) { abiertos = {}; restablecer(inm); }));
    function tecla(ev) {
      if (ev.key === "Escape" && !/^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName) && drawer.classList.contains("abierto")) seleccionar(null);
    }
    document.addEventListener("keydown", tecla);
    limpiezas.push(function () { document.removeEventListener("keydown", tecla); pops.forEach(function (p) { p.destruir(); }); });
    limpiezas.push(KR.shortlist.escuchar(function () { pintarFiltros(); lz.dibujar(); }));
    limpiezas.push(KR.alCambiarTema(function () { C = KR.colores(); lz.dibujar(); }));

    recalcular(); pintarFiltros(); pintarLeyenda(); pintarAcciones();
    requestAnimationFrame(function () {
      restablecer(true);
      if (h0.f && grafo.byId[h0.f]) seleccionar(h0.f, true);
      if (canvas.animate) canvas.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 300, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
    });
    return function () { limpiezas.forEach(function (fn) { fn(); }); };
  }

  window.VARIANTES = window.VARIANTES || [];
  window.VARIANTES[2] = { nombre: "Barrios", montar: montar };
})();
