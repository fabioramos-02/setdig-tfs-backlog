"""
build.py — Regenera o viewer a partir do backlog.json (fonte da verdade).

Fluxo: backlog.json -> carimba generated_at -> injeta o blob DATA entre os
marcadores /*DATA_START*/.../*DATA_END*/ no backlog_viewer.html.
Sem dependencia de openpyxl/xlsx.

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

MARK_RE = re.compile(r"/\*DATA_START\*/.*?/\*DATA_END\*/", re.DOTALL)
# U+2028/U+2029 sao validos em JSON mas quebram um literal JS — escapar.
LINE_SEP = chr(0x2028)
PARA_SEP = chr(0x2029)


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    # Carimbo de versao: cada build = nova versao publicada.
    data["generated_at"] = datetime.datetime.now().isoformat(timespec="seconds")

    # Persiste o carimbo de volta na fonte da verdade.
    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    blob = json.dumps(data, ensure_ascii=False)
    blob = blob.replace(LINE_SEP, "\\u2028").replace(PARA_SEP, "\\u2029")

    html = HTML_PATH.read_text(encoding="utf-8")
    # repl como FUNCAO: nao interpreta escapes (\n, \", \\) do blob JSON.
    # Marcadores tornam a injecao robusta a qualquer conteudo (";" em tags etc.).
    new_html, n = MARK_RE.subn(
        lambda _m: "/*DATA_START*/" + blob + "/*DATA_END*/", html, count=1
    )
    if n != 1:
        raise SystemExit(
            "[ERRO] marcadores /*DATA_START*/.../*DATA_END*/ nao encontrados no HTML"
        )
    HTML_PATH.write_text(new_html, encoding="utf-8")

    print(f"[OK] build: {len(data['items'])} items | versao {data['generated_at']}")


if __name__ == "__main__":
    main()
