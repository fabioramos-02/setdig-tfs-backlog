const DATA = window.BACKLOG_DATA;

// ── Bowtie SVG icons (ADO style) ──────────────────────────────────────────
const ICONS = {
  "Epic": {
    bg: "#FF7B00", fg: "#FFF3E0",
    svg: `<svg viewBox="0 0 10 10" fill="white" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 3.2L2.5 6 5 2.2 7.5 6 9 3.2V8H1z"/>
      <circle cx="1" cy="2.6" r="0.6"/>
      <circle cx="5" cy="1.6" r="0.6"/>
      <circle cx="9" cy="2.6" r="0.6"/>
    </svg>`
  },
  "Feature": {
    bg: "#773B93", fg: "#EDE7F6",
    svg: `<svg viewBox="0 0 10 10" fill="white" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 1.2h4v3a2 2 0 0 1-4 0V1.2z"/>
      <rect x="4.3" y="5.6" width="1.4" height="1.6"/>
      <rect x="2.8" y="7.6" width="4.4" height="1.2" rx="0.2"/>
      <path d="M2 2.4H1v1.4a1.2 1.2 0 0 0 1.2 1.2H3" fill="none" stroke="white" stroke-width="0.7"/>
      <path d="M8 2.4h1v1.4a1.2 1.2 0 0 1-1.2 1.2H7" fill="none" stroke="white" stroke-width="0.7"/>
    </svg>`
  },
  "Product Backlog Item": {
    bg: "#009CCC", fg: "#E1F5FE",
    svg: `<svg viewBox="0 0 10 10" fill="none" stroke="white" stroke-width="0.9" xmlns="http://www.w3.org/2000/svg">
      <rect x="1.2" y="1.5" width="7.6" height="7" rx="0.6" fill="white" fill-opacity="0.15"/>
      <line x1="2.4" y1="3.4" x2="7.6" y2="3.4"/>
      <line x1="2.4" y1="5"   x2="7.6" y2="5"/>
      <line x1="2.4" y1="6.6" x2="5.6" y2="6.6"/>
    </svg>`
  },
  "Task": {
    bg: "#F2CB1D", fg: "#FFF8E1",
    svg: `<svg viewBox="0 0 10 10" fill="none" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="8" height="8" rx="1" fill="white" fill-opacity="0.15" stroke="white" stroke-width="0.9"/>
      <polyline points="3,5 4.3,6.5 7,3.5"/>
    </svg>`
  },
  "Bug": {
    bg: "#CC293D", fg: "#FDECEA",
    svg: `<svg viewBox="0 0 10 10" fill="white" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="5" cy="5.5" rx="2.5" ry="3"/>
      <path d="M3.5 2.5 Q5 1 6.5 2.5" stroke="white" stroke-width="1" fill="none"/>
      <line x1="1" y1="4" x2="3" y2="4.5" stroke="white" stroke-width="1"/>
      <line x1="9" y1="4" x2="7" y2="4.5" stroke="white" stroke-width="1"/>
      <line x1="1" y1="6.5" x2="2.5" y2="6.5" stroke="white" stroke-width="1"/>
      <line x1="9" y1="6.5" x2="7.5" y2="6.5" stroke="white" stroke-width="1"/>
    </svg>`
  },
};
const LABEL = {
  "Epic": "Epic", "Feature": "Feature",
  "Product Backlog Item": "Product Backlog Item",
  "Task": "Task", "Bug": "Bug",
};
const INDENT_PX = 20;

const map = {};
DATA.items.forEach(it => { map[it.csv_id] = { ...it, children: [], parent: null }; });
const roots = [];
DATA.items.forEach(it => {
  const n = map[it.csv_id];
  if (it.csv_id_pai && map[it.csv_id_pai]) {
    map[it.csv_id_pai].children.push(n);
    n.parent = map[it.csv_id_pai];
  } else roots.push(n);
});

document.getElementById("hdr-count").textContent =
  `${DATA.items.length} items`;

// ── Status (localStorage overrides) ───────────────────────────────────────
const STATUSES = ["A fazer", "Em progresso", "Finalizado"];
const ST_CLS = { "A fazer": "todo", "Em progresso": "prog", "Finalizado": "done" };
const ST_VAR = { "A fazer": "var(--s-todo)", "Em progresso": "var(--s-prog)", "Finalizado": "var(--s-done)" };
const LS_KEY = "tfs-backlog-status";
const VER_KEY = "tfs-backlog-version";

// Versionamento: cada deploy carimba DATA.generated_at. Se a versao publicada
// mudou, o status COMMITADO (backlog.json) e a verdade — descarta os overrides
// locais antigos para que F5 nunca mostre status mascarado por cache velho.
const DATA_VER = DATA.generated_at || "";
if (localStorage.getItem(VER_KEY) !== DATA_VER) {
  localStorage.removeItem(LS_KEY);
  localStorage.setItem(VER_KEY, DATA_VER);
}

let overrides = {};
try { overrides = JSON.parse(localStorage.getItem(LS_KEY) || "{}"); } catch (e) { overrides = {}; }
// poda overrides redundantes (já sincronizados no xlsx) ou inválidos
Object.keys(overrides).forEach(id => {
  if (!map[id] || !STATUSES.includes(overrides[id]) ||
      overrides[id] === (map[id].status || "A fazer")) delete overrides[id];
});
localStorage.setItem(LS_KEY, JSON.stringify(overrides));

function effStatus(n) { return overrides[n.csv_id] || n.status || "A fazer"; }

function descendants(n) {
  let out = [];
  n.children.forEach(c => { out.push(c); out = out.concat(descendants(c)); });
  return out;
}

function refreshNode(n) {
  const st = effStatus(n);
  if (n.dotEl) n.dotEl.style.background = ST_VAR[st];
  if (n.rowEl) n.rowEl.classList.toggle("st-done", st === "Finalizado");
  if (n.progEl) {
    const ds = descendants(n);
    const done = ds.filter(d => effStatus(d) === "Finalizado").length;
    n.progEl.textContent = `${done}/${ds.length}`;
  }
}

function updateHeader() {
  const c = { "A fazer": 0, "Em progresso": 0, "Finalizado": 0 };
  DATA.items.forEach(it => c[effStatus(map[it.csv_id])]++);
  document.getElementById("cnt-todo").textContent = c["A fazer"];
  document.getElementById("cnt-prog").textContent = c["Em progresso"];
  document.getElementById("cnt-done").textContent = c["Finalizado"];
  const total = DATA.items.length;
  const pct = total ? Math.round(100 * c["Finalizado"] / total) : 0;
  document.getElementById("hdr-fill").style.width = pct + "%";
  document.getElementById("hdr-pct").textContent = pct + "%";
}

let currentSeg = null;
function syncSeg(n) {
  if (!currentSeg || currentSeg.node !== n) return;
  const st = effStatus(n);
  currentSeg.seg.querySelectorAll("button").forEach((b, i) => {
    b.classList.toggle("active", STATUSES[i] === st);
  });
}

function setStatus(n, st) {
  const base = n.status || "A fazer";
  if (st === base) delete overrides[n.csv_id];
  else overrides[n.csv_id] = st;
  localStorage.setItem(LS_KEY, JSON.stringify(overrides));
  let p = n;
  while (p) { refreshNode(p); p = p.parent; }
  updateHeader();
  applyFilter();
  syncSeg(n);
}

// ── Filtro por status ─────────────────────────────────────────────────────
let filter = "Todos";

function nodeMatches(n) {
  if (filter === "Todos") return true;
  if (effStatus(n) === filter) return true;
  return n.children.some(nodeMatches);
}

function applyFilter() {
  Object.values(map).forEach(n => {
    const show = nodeMatches(n);
    if (n.wrapEl) n.wrapEl.style.display = show ? "" : "none";
    if (filter !== "Todos" && show && n.children.length && n.children.some(nodeMatches)) {
      n.childrenEl.classList.add("open");
      n.toggleEl.classList.add("open");
    }
  });
}

function wiIcon(tipo, size = 16) {
  const ic = ICONS[tipo] || ICONS["Task"];
  const el = document.createElement("div");
  el.className = "wi-icon";
  el.style.cssText = `width:${size}px;height:${size}px;background:${ic.bg};border-radius:${size<=16?'3':'4'}px;display:flex;align-items:center;justify-content:center;flex-shrink:0`;
  el.innerHTML = ic.svg;
  return el;
}

function renderNode(node, depth) {
  const wrap = document.createElement("div");
  wrap.className = "node";

  const row = document.createElement("div");
  row.className = "node-row";
  row.style.paddingLeft = (8 + depth * INDENT_PX) + "px";
  row.dataset.id = node.csv_id;

  const toggle = document.createElement("span");
  toggle.className = "toggle" + (node.children.length ? "" : " leaf");
  toggle.innerHTML = '<svg width="10" height="10" viewBox="0 0 12 12" aria-hidden="true"><polygon points="2,4 10,4 6,9" fill="#545d64"/></svg>';

  const icon = wiIcon(node.tipo, 16);

  const title = document.createElement("span");
  title.className = "title-text";
  title.textContent = node.titulo;

  row.appendChild(toggle);
  row.appendChild(icon);
  row.appendChild(title);

  if (node.children.length) {
    const prog = document.createElement("span");
    prog.className = "node-prog";
    node.progEl = prog;
    row.appendChild(prog);
  }

  const dot = document.createElement("span");
  dot.className = "st-dot";
  row.appendChild(dot);

  node.rowEl = row;
  node.dotEl = dot;
  node.wrapEl = wrap;
  node.toggleEl = toggle;

  // children
  const childWrap = document.createElement("div");
  childWrap.className = "children-wrap";
  childWrap.style.setProperty("--guide-x", (16 + depth * INDENT_PX) + "px");

  const childrenDiv = document.createElement("div");
  childrenDiv.className = "children";
  node.children.forEach(c => childrenDiv.appendChild(renderNode(c, depth + 1)));
  childWrap.appendChild(childrenDiv);
  node.childrenEl = childrenDiv;

  row.addEventListener("click", e => {
    e.stopPropagation();
    if (node.children.length) {
      const open = childrenDiv.classList.toggle("open");
      toggle.classList.toggle("open", open);
    }
    document.querySelectorAll(".node-row.selected").forEach(r => r.classList.remove("selected"));
    row.classList.add("selected");
    renderDetail(node);
  });

  wrap.appendChild(row);
  wrap.appendChild(childWrap);
  return wrap;
}

function copy(text, btn) {
  (navigator.clipboard?.writeText(text) || Promise.reject())
    .then(() => flash(btn))
    .catch(() => {
      const ta = Object.assign(document.createElement("textarea"), { value: text });
      document.body.appendChild(ta); ta.select();
      document.execCommand("copy"); document.body.removeChild(ta);
      flash(btn);
    });
}
function flash(btn) {
  const t = btn.textContent;
  btn.textContent = "✓ Copiado"; btn.classList.add("ok");
  setTimeout(() => { btn.textContent = t; btn.classList.remove("ok"); }, 1400);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => (
    {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]
  ));
}

// Mini-renderer markdown — cobre o que usamos nas descricoes TFS.
function mdRender(s) {
  let t = escapeHtml(s).replace(/\r\n/g, "\n");
  // links [texto](url)
  t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  // URLs nuas
  t = t.replace(/(^|[\s])((?:https?:\/\/)[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
  // bold
  t = t.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
  // code inline
  t = t.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  // listas: agrupar linhas iniciadas por "- "
  const lines = t.split("\n");
  const out = [];
  let inList = false;
  let para = [];
  const flushPara = () => {
    if (para.length) { out.push("<p>" + para.join("<br>") + "</p>"); para = []; }
  };
  for (const ln of lines) {
    const li = ln.match(/^\s*-\s+(.+)$/);
    if (li) {
      flushPara();
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push("<li>" + li[1] + "</li>");
      continue;
    }
    if (inList) { out.push("</ul>"); inList = false; }
    if (ln.trim() === "") { flushPara(); continue; }
    para.push(ln);
  }
  if (inList) out.push("</ul>");
  flushPara();
  return out.join("");
}

function field(label, value, cls = "", asMarkdown = false) {
  const w = document.createElement("div"); w.className = "field";
  const top = document.createElement("div"); top.className = "field-top";
  const lbl = document.createElement("span"); lbl.className = "field-label"; lbl.textContent = label;
  const btn = document.createElement("button"); btn.className = "copy-btn"; btn.textContent = "Copiar";
  btn.addEventListener("click", () => copy(value || "", btn));
  top.appendChild(lbl); top.appendChild(btn);
  const val = document.createElement("div");
  val.className = "field-value" + (cls ? " "+cls : "") + (value ? "" : " empty-v");
  if (value && asMarkdown) {
    val.classList.add("md-v");
    val.innerHTML = mdRender(value);
  } else {
    val.textContent = value || "(sem preenchimento)";
  }
  w.appendChild(top); w.appendChild(val);
  return w;
}

function renderDetail(node) {
  const panel = document.getElementById("detail");
  panel.innerHTML = "";

  const ic = ICONS[node.tipo] || ICONS["Task"];

  // header bar
  const hdr = document.createElement("div"); hdr.className = "det-header";
  const bigIcon = wiIcon(node.tipo, 24); bigIcon.className = "det-wi-icon";
  bigIcon.style.cssText = `width:24px;height:24px;background:${ic.bg};border-radius:4px;display:flex;align-items:center;justify-content:center;flex-shrink:0`;
  const typeLabel = document.createElement("span"); typeLabel.className = "det-type-label";
  typeLabel.style.color = ic.bg; typeLabel.textContent = LABEL[node.tipo] || node.tipo;
  const sep = document.createElement("div"); sep.className = "det-sep";
  const idEl = document.createElement("span"); idEl.className = "det-id";
  idEl.textContent = node.ado_id ? `#${node.ado_id}` : `CSV-${node.csv_id}`;
  hdr.appendChild(bigIcon); hdr.appendChild(typeLabel);
  hdr.appendChild(sep); hdr.appendChild(idEl);

  // status segmented control
  const seg = document.createElement("div"); seg.className = "status-seg";
  STATUSES.forEach(st => {
    const b = document.createElement("button");
    b.classList.add(ST_CLS[st]);
    const d = document.createElement("span"); d.className = "dot";
    d.style.background = ST_VAR[st];
    b.appendChild(d);
    b.appendChild(document.createTextNode(st));
    b.addEventListener("click", () => setStatus(node, st));
    seg.appendChild(b);
  });
  hdr.appendChild(seg);
  currentSeg = { node, seg };
  syncSeg(node);

  panel.appendChild(hdr);

  // body
  const body = document.createElement("div"); body.className = "det-body";
  const titleEl = document.createElement("div"); titleEl.className = "det-title";
  titleEl.textContent = node.titulo;
  body.appendChild(titleEl);
  body.appendChild(field("Título", node.titulo, "title-v"));
  body.appendChild(field("Descrição", node.descricao, "", true));
  panel.appendChild(body);
}

const treeEl = document.getElementById("tree");
roots.forEach(r => treeEl.appendChild(renderNode(r, 0)));

// filter chips
const fb = document.getElementById("filterbar");
["Todos", ...STATUSES].forEach(f => {
  const b = document.createElement("button");
  b.className = "chip" + (f === filter ? " active" : "");
  if (f !== "Todos") {
    const d = document.createElement("span"); d.className = "dot";
    d.style.background = ST_VAR[f];
    b.appendChild(d);
  }
  b.appendChild(document.createTextNode(f));
  b.addEventListener("click", () => {
    filter = f;
    fb.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
    b.classList.add("active");
    applyFilter();
  });
  fb.appendChild(b);
});

Object.values(map).forEach(refreshNode);
updateHeader();

document.querySelectorAll(".node-row[data-id]").forEach(row => {
  const n = map[parseInt(row.dataset.id)];
  if (n?.tipo === "Epic" && n.children.length) row.click();
});
