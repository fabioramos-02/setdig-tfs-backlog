"""
build.py — Regenera o viewer a partir do backlog.json (fonte da verdade).

Fluxo: backlog.json -> carimba generated_at -> injeta DATA inline no
backlog_viewer.html. Sem dependencia de openpyxl/xlsx.

Uso:
    python build.py

O backlog_viewer.html continua sendo um arquivo unico (abre com duplo-clique
e publica no GitHub Pages sem fetch/CORS). O carimbo generated_at faz o status
COMMITADO vencer overrides antigos do localStorage apos cada deploy.
"""
import json
import re
import datetime
import pathlib

ROOT = pathlib.Path(__file__).parent
JSON_PATH = ROOT / "backlog.json"
HTML_PATH = ROOT / "backlog_viewer.html"


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    # Carimbo de versao: cada build = nova versao publicada.
    data["generated_at"] = datetime.datetime.now().isoformat(timespec="seconds")

    # Persiste o carimbo de volta na fonte da verdade.
    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Injeta o blob DATA inline (linha unica) no HTML.
    blob = json.dumps(data, ensure_ascii=False)
    html = HTML_PATH.read_text(encoding="utf-8")
    new_html, n = re.subn(r"const DATA = .*;", "const DATA = " + blob + ";", html, count=1)
    if n != 1:
        raise SystemExit("[ERRO] linha 'const DATA = ...;' nao encontrada no HTML")
    HTML_PATH.write_text(new_html, encoding="utf-8")

    print(f"[OK] build: {len(data['items'])} items | versao {data['generated_at']}")


if __name__ == "__main__":
    main()
