"""
build.py — Regenera o viewer e a página de relatórios a partir de:
  - backlog.json (fonte da verdade dos work items)
  - relatorios/*.md (relatórios semanais gerados por /tfs semana)

Fluxo:
  1. backlog.json -> carimba generated_at -> injeta blob DATA entre os marcadores
     /*DATA_START*/.../*DATA_END*/ no backlog_viewer.html
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
HTML_PATH = ROOT / "backlog_viewer.html"
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

    html = HTML_PATH.read_text(encoding="utf-8")
    new_html, n = MARK_RE.subn(
        lambda _m: "/*DATA_START*/" + blob + "/*DATA_END*/", html, count=1
    )
    if n != 1:
        raise SystemExit(
            "[ERRO] marcadores /*DATA_START*/.../*DATA_END*/ nao encontrados no HTML"
        )
    HTML_PATH.write_text(new_html, encoding="utf-8")
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
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: var(--font-family-primary, 'IBM Plex Sans', system-ui, sans-serif);
    font-size: 14px;
    background: var(--color-neutral-100);
    color: var(--color-neutral-700);
    -webkit-font-smoothing: antialiased;
  }}
  .topbar {{
    background: var(--color-primary-500);
    color: #fff;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 10;
    box-shadow: 0 2px 4px rgba(0,0,0,0.10);
    min-height: 56px;
  }}
  .topbar h1 {{
    font-size: 16px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.01em;
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .back-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 600;
    color: #fff;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 4px;
    text-decoration: none;
    transition: background 120ms, border-color 120ms;
    flex: 0 0 auto;
  }}
  .back-btn:hover {{
    background: rgba(255,255,255,0.22);
    border-color: rgba(255,255,255,0.45);
  }}
  .back-btn svg {{ width: 14px; height: 14px; }}
  .meta {{ font-size: 12px; opacity: .85; flex: 0 0 auto; }}
  .layout {{ display: grid; grid-template-columns: 260px 1fr; }}
  aside {{
    background: #fff;
    border-right: 1px solid var(--color-neutral-200);
    padding: 24px 18px;
    position: sticky;
    top: 56px;
    align-self: start;
    max-height: calc(100vh - 56px);
    overflow-y: auto;
  }}
  aside h2 {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: var(--color-neutral-500);
    margin: 0 0 12px;
    font-weight: 600;
  }}
  aside ul {{ list-style: none; padding: 0; margin: 0; }}
  aside li {{ margin-bottom: 2px; }}
  aside a {{
    color: var(--color-primary-500);
    text-decoration: none;
    font-weight: 500;
    display: block;
    padding: 8px 10px;
    border-radius: 4px;
    font-size: 13px;
    transition: background 120ms;
  }}
  aside a:hover {{ background: var(--color-primary-100); }}
  main {{ padding: 28px 32px; max-width: 920px; }}
  .relatorio {{
    background: #fff;
    border: 1px solid var(--color-neutral-200);
    border-radius: 8px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }}
  .relatorio h1 {{
    font-size: 20px;
    color: var(--color-primary-700);
    border-bottom: 3px solid var(--color-primary-500);
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 12px;
    font-weight: 700;
    line-height: 1.3;
  }}
  .relatorio h2 {{
    font-size: 13px;
    color: var(--color-primary-500);
    background: var(--color-primary-100);
    margin-top: 24px;
    margin-bottom: 12px;
    padding: 6px 12px;
    border-radius: 4px;
    display: inline-block;
    font-weight: 600;
    letter-spacing: 0.01em;
  }}
  .relatorio p {{ margin: 8px 0; color: var(--color-neutral-500); font-size: 13px; }}
  .relatorio ul {{ padding-left: 20px; margin: 8px 0; }}
  .relatorio li {{ margin-bottom: 12px; line-height: 1.6; }}
  .relatorio strong {{ color: var(--color-neutral-800); }}
  .relatorio code {{
    background: var(--color-neutral-100);
    color: var(--color-neutral-700);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    word-break: break-all;
  }}
  .relatorio em {{
    color: var(--color-neutral-500);
    font-style: normal;
    font-size: 12.5px;
    display: inline-block;
    margin-right: 8px;
  }}
  /* status tags */
  .status-tag {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    line-height: 1.6;
    white-space: nowrap;
    vertical-align: middle;
  }}
  .status-tag--done {{
    background: var(--tag-success-background, #D0E8D6);
    color: var(--color-success-700, #08210f);
  }}
  .status-tag--prog {{
    background: var(--color-info-100, #cdebff);
    color: var(--color-info-700, #011f33);
  }}
  .status-tag--todo {{
    background: var(--color-neutral-100);
    color: var(--color-neutral-700);
    border: 1px solid var(--color-neutral-200);
  }}
  .status-tag--block {{
    background: var(--color-error-100, #f6d3d5);
    color: var(--color-error-700, #540f12);
  }}
  .empty {{
    text-align: center;
    color: var(--color-neutral-500);
    padding: 80px 20px;
    font-size: 15px;
  }}
  .empty code {{
    background: var(--color-neutral-100);
    padding: 2px 8px;
    border-radius: 3px;
    color: var(--color-primary-500);
    font-family: 'IBM Plex Mono', monospace;
  }}

  /* tablet */
  @media (max-width: 960px) {{
    .layout {{ grid-template-columns: 220px 1fr; }}
    main {{ padding: 24px 24px; }}
    .relatorio {{ padding: 20px 22px; }}
  }}

  /* mobile */
  @media (max-width: 720px) {{
    .topbar {{
      flex-wrap: wrap;
      padding: 10px 16px;
      gap: 10px;
    }}
    .topbar h1 {{ font-size: 14px; order: 2; flex-basis: 100%; }}
    .back-btn {{ order: 1; }}
    .meta {{ order: 3; margin-left: auto; }}
    .layout {{ grid-template-columns: 1fr; }}
    aside {{
      position: static;
      max-height: none;
      border-right: none;
      border-bottom: 1px solid var(--color-neutral-200);
      padding: 14px 16px;
    }}
    aside h2 {{ margin-bottom: 8px; }}
    aside ul {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }}
    aside li {{ margin: 0; }}
    aside a {{
      padding: 6px 10px;
      background: var(--color-neutral-100);
      font-size: 12px;
    }}
    main {{ padding: 16px; }}
    .relatorio {{ padding: 18px 16px; border-radius: 6px; }}
    .relatorio h1 {{ font-size: 18px; }}
    .relatorio h2 {{ font-size: 12px; padding: 5px 10px; }}
    .relatorio li {{ font-size: 13.5px; }}
    .relatorio em {{ display: block; margin: 4px 0 0; }}
    .relatorio code {{ font-size: 11.5px; }}
  }}

  @media (max-width: 420px) {{
    .meta {{ display: none; }}
    .topbar h1 {{ font-size: 13px; }}
  }}
</style>
</head>
<body>
<div class="topbar">
  <a class="back-btn" href="backlog_viewer.html" aria-label="Voltar ao backlog">
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
