// Prototipo — calcula UNA VEZ las posiciones del mapa de conexiones y las guarda en
// posiciones.json. Es la pieza que hace posible crecer: el navegador ya no simula fuerzas en
// cada filtro (hoy ~700ms por tecla con 400 nodos), solo dibuja posiciones ya resueltas. En
// producción esto correría en el mismo pipeline que genera perfiles-muestra.json.
//
// Mismo layout que web/index.html (anclas por institución en espiral de Vogel, repulsión con
// grilla, resortes en las aristas, empujón inicial fijo por id), con más iteraciones porque
// acá el costo no lo paga el usuario.
//
// Uso: node prototipos/conexiones/calcular-posiciones.mjs

import fs from "node:fs";

const RAIZ = new URL("../../", import.meta.url);
const datos = JSON.parse(fs.readFileSync(new URL("data/sample/perfiles-muestra.json", RAIZ), "utf8"));
const nodes = datos.entidades.map((e) => ({ id: e.id, tipo: e.tipo }));
const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
const edges = datos.vinculos.filter((v) => byId[v.origen] && byId[v.destino]);

function ruidoFijo(id, semilla) {
  let h = 2166136261 ^ semilla;
  for (let q = 0; q < id.length; q++) { h ^= id.charCodeAt(q); h = Math.imul(h, 16777619); }
  h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16;
  return (h >>> 0) / 4294967296 - 0.5;
}

const escala = Math.min(2.2, Math.max(1, Math.sqrt(nodes.length / 180)));
const W = Math.round(720 * escala);
const H = Math.round(W * 0.62);

const grado = {};
nodes.forEach((n) => { grado[n.id] = 0; });
edges.forEach((e) => { grado[e.origen]++; grado[e.destino]++; });

const insts = nodes.filter((n) => n.tipo === "institucion")
  .sort((a, b) => grado[b.id] - grado[a.id] || (a.id < b.id ? -1 : 1));
const anclas = {};
insts.forEach((inst, i) => {
  const t = (i + 0.5) / insts.length;
  const radio = Math.sqrt(t) * Math.min(W, H) * 0.42;
  const ang = i * 2.399963229728653;
  anclas[inst.id] = { x: W / 2 + Math.cos(ang) * radio, y: H / 2 + Math.sin(ang) * radio };
});

const anclaDe = {};
nodes.forEach((n) => {
  if (n.tipo === "institucion") { anclaDe[n.id] = n.id; return; }
  for (const e of edges) {
    const otro = e.origen === n.id ? e.destino : e.destino === n.id ? e.origen : null;
    if (otro && byId[otro].tipo === "institucion") { anclaDe[n.id] = otro; break; }
  }
});

nodes.forEach((n, i) => {
  const a = anclas[anclaDe[n.id]];
  const ang = (i / nodes.length) * Math.PI * 2;
  const jx = ruidoFijo(n.id, 1), jy = ruidoFijo(n.id, 2);
  n.x = a ? a.x + Math.cos(ang) * 26 + jx * 12 : W / 2 + Math.cos(ang) * 150 + jx * 20;
  n.y = a ? a.y + Math.sin(ang) * 26 + jy * 12 : H / 2 + Math.sin(ang) * 150 + jy * 20;
  n.vx = 0; n.vy = 0; n.i = i; n.ancla = anclaDe[n.id];
});

const CORTE = 110, COLS = Math.ceil(W / CORTE), FILAS = Math.ceil(H / CORTE);
const celdas = Array.from({ length: COLS * FILAS }, () => []);
const celda = (v, max) => Math.max(0, Math.min(max - 1, (v / CORTE) | 0));
const t0 = Date.now();

for (let iter = 0; iter < 300; iter++) {
  celdas.forEach((c) => { c.length = 0; });
  nodes.forEach((n) => celdas[celda(n.x, COLS) * FILAS + celda(n.y, FILAS)].push(n));
  for (const a of nodes) {
    const cx = celda(a.x, COLS), cy = celda(a.y, FILAS);
    for (let gx = Math.max(0, cx - 1); gx <= Math.min(COLS - 1, cx + 1); gx++) {
      for (let gy = Math.max(0, cy - 1); gy <= Math.min(FILAS - 1, cy + 1); gy++) {
        for (const b of celdas[gx * FILAS + gy]) {
          if (b.i <= a.i) continue;
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy || 0.01, d = Math.sqrt(d2);
          const f = (a.ancla !== undefined && a.ancla === b.ancla ? 420 : 1500) / d2;
          a.vx += (dx / d) * f; a.vy += (dy / d) * f; b.vx -= (dx / d) * f; b.vy -= (dy / d) * f;
        }
      }
    }
  }
  for (const e of edges) {
    const a = byId[e.origen], b = byId[e.destino];
    const dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 0.01;
    const f = (d - 70) * 0.02;
    a.vx += (dx / d) * f; a.vy += (dy / d) * f; b.vx -= (dx / d) * f; b.vy -= (dy / d) * f;
  }
  for (const n of nodes) {
    const a = anclas[n.ancla];
    if (a) { const k = n.tipo === "institucion" ? 0.08 : 0.03; n.vx += (a.x - n.x) * k; n.vy += (a.y - n.y) * k; }
    else { n.vx += (W / 2 - n.x) * 0.0015; n.vy += (H / 2 - n.y) * 0.0015; }
    n.x += n.vx * 0.15; n.y += n.vy * 0.15; n.vx *= 0.82; n.vy *= 0.82;
    n.x = Math.max(30, Math.min(W - 30, n.x)); n.y = Math.max(20, Math.min(H - 20, n.y));
  }
}

const r1 = (v) => Math.round(v * 10) / 10;
const salida = {
  generado: new Date().toISOString().slice(0, 10),
  nota: "Posiciones precalculadas para los prototipos de prototipos/conexiones. No son datos: solo geometría.",
  W, H,
  nodos: Object.fromEntries(nodes.map((n) => [n.id, [r1(n.x), r1(n.y)]])),
  ancla: Object.fromEntries(nodes.filter((n) => n.ancla).map((n) => [n.id, n.ancla])),
};
fs.writeFileSync(new URL("posiciones.json", import.meta.url), JSON.stringify(salida));
console.log(`${nodes.length} nodos, ${edges.length} aristas, ${W}x${H}, ${Date.now() - t0}ms`);
