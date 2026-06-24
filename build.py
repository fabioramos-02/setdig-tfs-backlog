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


RELATORIOS_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Relatórios semanais — Backlog TFS SETDIG</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --brand: #244061;
    --bg: #F5F7FA;
    --surface: #fff;
    --border: #E1E5EA;
    --text: #1B1F23;
    --text-sub: #5B6470;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 14px;
    background: var(--bg);
    color: var(--text);
  }}
  header {{
    background: var(--brand);
    color: #fff;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 10;
  }}
  header h1 {{ font-size: 16px; font-weight: 700; margin: 0; }}
  header a {{ color: #fff; text-decoration: none; font-size: 13px; opacity: .85; }}
  header a:hover {{ opacity: 1; text-decoration: underline; }}
  .layout {{ display: grid; grid-template-columns: 280px 1fr; }}
  aside {{
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 20px;
    position: sticky;
    top: 48px;
    align-self: start;
    max-height: calc(100vh - 48px);
    overflow-y: auto;
  }}
  aside h2 {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: var(--text-sub);
    margin: 0 0 12px;
  }}
  aside ul {{ list-style: none; padding: 0; margin: 0; }}
  aside li {{ margin-bottom: 4px; }}
  aside a {{
    color: var(--brand);
    text-decoration: none;
    font-weight: 500;
    display: block;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 13px;
  }}
  aside a:hover {{ background: #EEF3FD; }}
  main {{ padding: 32px 48px; max-width: 900px; }}
  .relatorio {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px 32px;
    margin-bottom: 24px;
  }}
  .relatorio h1 {{
    font-size: 20px;
    color: var(--brand);
    border-bottom: 2px solid var(--brand);
    padding-bottom: 8px;
    margin-top: 0;
  }}
  .relatorio h2 {{
    font-size: 15px;
    color: var(--brand);
    margin-top: 24px;
    margin-bottom: 8px;
  }}
  .relatorio ul {{ padding-left: 20px; }}
  .relatorio li {{ margin-bottom: 6px; line-height: 1.55; }}
  .relatorio code {{
    background: #F0F2F5;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 12px;
  }}
  .relatorio em {{ color: var(--text-sub); }}
  .empty {{
    text-align: center;
    color: var(--text-sub);
    padding: 80px 20px;
    font-size: 15px;
  }}
</style>
</head>
<body>
<header>
  <h1>Relatórios semanais — SETDIG</h1>
  <a href="backlog_viewer.html">← voltar ao backlog</a>
  <span style="margin-left:auto; font-size:12px; opacity:.7;">{count} relatório(s) · gerado em {generated_at}</span>
</header>
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
