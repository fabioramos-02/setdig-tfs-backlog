"""
build.py — Regenera o viewer e a página de relatórios a partir de:
  - backlog.json (fonte da verdade dos work items)
  - relatorios/*.md (relatórios semanais gerados por /tfs semana)

Fluxo:
  1. backlog.json -> carimba generated_at -> injeta blob DATA entre os marcadores
     /*DATA_START*/.../*DATA_END*/ no index.html
  2. relatorios/*.md -> renderiza inline em relatorios.html (self-contained)

Sem dependência de openpyxl/xlsx. Requer pip install markdown (ver requirements.txt).

Uso:
    python build.py
"""
import json
import re
import datetime
import pathlib

import markdown

ROOT = pathlib.Path(__file__).parent
JSON_PATH = ROOT / "backlog.json"
DATA_JS_PATH = ROOT / "assets" / "js" / "data.js"
RELATORIOS_DIR = ROOT / "relatorios"
RELATORIOS_HTML = ROOT / "relatorios.html"

MARK_RE = re.compile(r"/\*DATA_START\*/.*?/\*DATA_END\*/", re.DOTALL)
LINE_SEP = chr(0x2028)
PARA_SEP = chr(0x2029)

DATE_NAME_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2})\]-relatorio-semanal\.md$")


def build_viewer():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    data["generated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    blob = json.dumps(data, ensure_ascii=False)
    blob = blob.replace(LINE_SEP, "\\u2028").replace(PARA_SEP, "\\u2029")

    src = DATA_JS_PATH.read_text(encoding="utf-8")
    new_src, n = MARK_RE.subn(
        lambda _m: "/*DATA_START*/" + blob + "/*DATA_END*/", src, count=1
    )
    if n != 1:
        raise SystemExit(
            "[ERRO] marcadores /*DATA_START*/.../*DATA_END*/ nao encontrados em assets/js/data.js"
        )
    DATA_JS_PATH.write_text(new_src, encoding="utf-8")
    print(f"[OK] viewer: {len(data['items'])} items | versao {data['generated_at']}")


STATUS_TAG_MAP = {
    "Finalizado": ("done", "Finalizado"),
    "Em progresso": ("prog", "Em progresso"),
    "A fazer": ("todo", "A fazer"),
    "Impedido": ("block", "Impedido"),
}
STATUS_TAG_RE = re.compile(
    r"\s+—\s+(Finalizado|Em progresso|A fazer|Impedido)\s+—\s+"
)


def inject_status_tags(html):
    def repl(m):
        slug, label = STATUS_TAG_MAP[m.group(1)]
        return f' <span class="status-tag status-tag--{slug}">{label}</span> '
    return STATUS_TAG_RE.sub(repl, html)


RELATORIOS_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatórios semanais — Backlog TFS SETDIG</title>
<link rel="stylesheet" href="assets/ds-sis.css">
<link rel="stylesheet" href="assets/css/relatorios.css">
</head>
<body>
<div class="topbar">
  <a class="back-btn" href="index.html" aria-label="Voltar ao backlog">
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 12L6 8l4-4"/></svg>
    Backlog
  </a>
  <h1>Relatórios semanais — SETDIG</h1>
  <span class="meta">{count} relatório(s) · {generated_at}</span>
</div>
<div class="layout">
  <aside>
    <h2>Índice</h2>
    {nav}
  </aside>
  <main>
    {body}
  </main>
</div>
</body>
</html>
"""


def build_relatorios():
    RELATORIOS_DIR.mkdir(exist_ok=True)
    md_files = sorted(
        [p for p in RELATORIOS_DIR.glob("*.md") if DATE_NAME_RE.match(p.name)],
        key=lambda p: p.name,
        reverse=True,
    )
    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if not md_files:
        body = '<div class="empty">Nenhum relatório semanal gerado ainda.<br>Use <code>/tfs semana</code> para criar o primeiro.</div>'
        nav = "<p style='color:var(--text-sub); font-size:12px;'>vazio</p>"
        html = RELATORIOS_TEMPLATE.format(
            count=0, generated_at=generated_at, nav=nav, body=body
        )
        RELATORIOS_HTML.write_text(html, encoding="utf-8")
        print(f"[OK] relatorios: 0 arquivos | versao {generated_at}")
        return

    md_engine = markdown.Markdown(extensions=["extra", "sane_lists"])
    nav_items = []
    body_parts = []
    for p in md_files:
        anchor = p.stem
        m = DATE_NAME_RE.match(p.name)
        date_iso = m.group(1) if m else p.stem
        nav_items.append(f'<li><a href="#{anchor}">{date_iso}</a></li>')
        md_engine.reset()
        rendered = md_engine.convert(p.read_text(encoding="utf-8"))
        rendered = inject_status_tags(rendered)
        body_parts.append(
            f'<section class="relatorio" id="{anchor}">{rendered}</section>'
        )

    nav = "<ul>" + "".join(nav_items) + "</ul>"
    body = "\n".join(body_parts)
    html = RELATORIOS_TEMPLATE.format(
        count=len(md_files), generated_at=generated_at, nav=nav, body=body
    )
    RELATORIOS_HTML.write_text(html, encoding="utf-8")
    print(f"[OK] relatorios: {len(md_files)} arquivos | versao {generated_at}")


def main():
    build_viewer()
    build_relatorios()


if __name__ == "__main__":
    main()
