"""
build.py — Gera o relatório semanal a partir dos CSVs exportados da query do TFS.

Entradas:
  - dados/AAAA-MM-DD.csv      export bruto da query "Tree of work items" do TFS
  - relatorios/AAAA-MM-DD.md  resumo em prosa da semana (opcional)

Saída:
  - index.html    dados injetados entre /*DATA_START*/.../*DATA_END*/

A página não faz fetch: o dado vive dentro do HTML. Isso mantém o arquivo abrindo
por duplo clique (file://) e no GitHub Pages sem CORS.

Uso:
    python build.py
"""
import csv
import datetime
import json
import pathlib
import re

import markdown

ROOT = pathlib.Path(__file__).parent
DADOS_DIR = ROOT / "dados"
RELATORIOS_DIR = ROOT / "relatorios"
INDEX_PATH = ROOT / "index.html"

MARK_RE = re.compile(r"/\*DATA_START\*/.*?/\*DATA_END\*/", re.DOTALL)
NOME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
LINE_SEP = chr(0x2028)
PARA_SEP = chr(0x2029)

# Estado do TFS -> bucket do relatório. A tag "bloqueio" tem precedência (ver bucket()).
BUCKETS = {
    "Done": "done",
    "Closed": "done",
    "In Progress": "prog",
    "Committed": "prog",
    "To Do": "todo",
    "New": "todo",
    "Approved": "todo",
}
TAG_BLOQUEIO = "bloqueio"
DESCARTAR = {"Removed"}
# Todo item do time nasce com este prefixo; repeti-lo em cada linha é só ruído.
PREFIXO_RE = re.compile(r"^\[SGD\]\s*-\s*")


def bucket(estado, tags):
    """Bucket do item. Bloqueio ganha de qualquer estado — é o que precisa de decisão."""
    if TAG_BLOQUEIO in tags:
        return "block"
    return BUCKETS.get(estado, "todo")


def limpar_responsavel(valor):
    """'Fabio Willian Lima Ramos <SEGOV\\framos>' -> 'Fabio Ramos'."""
    nome = valor.split("<")[0].strip()
    if not nome:
        return ""
    partes = nome.split()
    return partes[0] if len(partes) == 1 else partes[0] + " " + partes[-1]


def parse_data(valor):
    """Aceita os formatos que o TFS exporta. Devolve date ou None."""
    valor = (valor or "").strip()
    if not valor:
        return None
    valor = valor.split("T")[0].split(" ")[0]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(valor, fmt).date()
        except ValueError:
            continue
    return None


def colunas_titulo(cabecalho):
    """Colunas 'Title 1'...'Title N' da árvore, em ordem de profundidade."""
    cols = [c for c in cabecalho if c and re.fullmatch(r"Title \d+", c)]
    return sorted(cols, key=lambda c: int(c.split()[1]))


def ler_csv(caminho):
    """CSV da árvore -> (itens, frentes). A frente é o título de nível 2 (Feature)
    herdado das linhas acima do item."""
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f))
    if not linhas:
        return [], []

    titulo_cols = colunas_titulo(linhas[0].keys())
    tem_titulo_simples = "Title" in linhas[0]
    hoje = datetime.date.today()

    itens = []
    frentes = {}
    contexto = {}  # profundidade -> título, para herdar a frente nas linhas seguintes

    for linha in linhas:
        estado = (linha.get("State") or "").strip()
        if estado in DESCARTAR:
            continue

        tipo = (linha.get("Work Item Type") or "").strip()

        # O item da linha é o título mais profundo preenchido. O export do TFS
        # preenche só a coluna do próprio nível e deixa os pais nas linhas de cima;
        # um CSV que repita a linhagem inteira na mesma linha também funciona aqui.
        preenchidas = []
        for i, col in enumerate(titulo_cols):
            valor = (linha.get(col) or "").strip()
            if valor:
                preenchidas.append((i, valor))

        titulo = ""
        if preenchidas:
            nivel, titulo = preenchidas[-1]
            for i, valor in preenchidas:
                contexto[i] = valor
            for mais_fundo in [k for k in contexto if k > nivel]:
                del contexto[mais_fundo]
        elif tem_titulo_simples:
            titulo = (linha.get("Title") or "").strip()

        # Epic, Feature e PBI dão o contexto; só Task e Bug viram linha do relatório.
        # PBI é guarda-chuva: contar ele como pendência infla o número sem dizer nada.
        if tipo in ("Epic", "Feature", "Product Backlog Item") or not titulo:
            continue

        frente = PREFIXO_RE.sub("", contexto.get(1) or contexto.get(0) or "Sem frente")
        tags = [t.strip().lower() for t in (linha.get("Tags") or "").split(";") if t.strip()]
        changed = parse_data(linha.get("Changed Date"))

        item = {
            "id": (linha.get("ID") or "").strip(),
            "tipo": tipo,
            "titulo": PREFIXO_RE.sub("", titulo),
            "estado": estado,
            "bucket": bucket(estado, tags),
            "responsavel": limpar_responsavel(linha.get("Assigned To") or ""),
            "dias": (hoje - changed).days if changed else None,
        }
        itens.append(item)
        frentes.setdefault(frente, []).append(item)

    ordem = {"block": 0, "prog": 1, "todo": 2, "done": 3}
    for lista in frentes.values():
        lista.sort(key=lambda i: (ordem.get(i["bucket"], 9), i["titulo"]))

    # Frente com pendência sobe; frente 100% finalizada desce.
    frentes_ord = sorted(
        ({"nome": nome, "itens": lista} for nome, lista in frentes.items()),
        key=lambda f: (all(i["bucket"] == "done" for i in f["itens"]), f["nome"]),
    )
    return itens, frentes_ord


def periodo(fim):
    """'2026-09-04' -> '29/08 a 04/09' (os 7 dias que terminam na data do arquivo)."""
    d = datetime.datetime.strptime(fim, "%Y-%m-%d").date()
    ini = d - datetime.timedelta(days=6)
    return "{:%d/%m} a {:%d/%m}".format(ini, d)


def ler_resumo(chave):
    md = RELATORIOS_DIR / (chave + ".md")
    if not md.exists():
        return ""
    return markdown.markdown(
        md.read_text(encoding="utf-8"), extensions=["extra", "sane_lists"]
    )


def montar():
    if not DADOS_DIR.exists():
        return []
    arquivos = sorted(
        (p for p in DADOS_DIR.iterdir() if NOME_RE.match(p.name)),
        key=lambda p: p.name,
        reverse=True,
    )
    semanas = []
    for caminho in arquivos:
        chave = caminho.stem
        itens, frentes = ler_csv(caminho)
        stats = {"done": 0, "prog": 0, "todo": 0, "block": 0}
        for i in itens:
            stats[i["bucket"]] = stats.get(i["bucket"], 0) + 1
        semanas.append({
            "arquivo": chave,
            "periodo": periodo(chave),
            "stats": stats,
            "bloqueios": [
                {"id": i["id"], "titulo": i["titulo"], "dias": i["dias"]}
                for i in itens if i["bucket"] == "block"
            ],
            "resumo_html": ler_resumo(chave),
            "frentes": frentes,
        })
        print("[OK] {}: {} itens | {}".format(
            chave, len(itens), " ".join("{}={}".format(k, v) for k, v in stats.items())))
    return semanas


def injetar(semanas):
    dados = {
        "generated_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "semanas": semanas,
    }
    blob = json.dumps(dados, ensure_ascii=False)
    blob = blob.replace(LINE_SEP, "\\u2028").replace(PARA_SEP, "\\u2029")

    src = INDEX_PATH.read_text(encoding="utf-8")
    novo, n = MARK_RE.subn(lambda _m: "/*DATA_START*/" + blob + "/*DATA_END*/", src, count=1)
    if n != 1:
        raise SystemExit(
            "[ERRO] marcadores /*DATA_START*/.../*DATA_END*/ nao encontrados em index.html"
        )
    INDEX_PATH.write_text(novo, encoding="utf-8")


def main():
    semanas = montar()
    injetar(semanas)
    if not semanas:
        print("[AVISO] nenhum CSV em dados/ — a pagina foi gerada vazia.")
    print("[OK] index.html gerado com {} semana(s).".format(len(semanas)))


if __name__ == "__main__":
    main()
