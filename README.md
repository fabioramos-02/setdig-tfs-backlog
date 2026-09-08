# Relatório semanal — SGD

Página que mostra, semana a semana, o que eu finalizei, o que está em andamento, o que
está pendente e o que está bloqueado no backlog XVIA do TFS.

**Publicado em:** <https://fabioramos-02.github.io/setdig-tfs-backlog/>

O repositório guarda dois tipos de arquivo: o CSV bruto exportado da query do TFS (`dados/`) e o
resumo em prosa de cada semana (`relatorios/`). O `build.py` junta os dois e reescreve o
`index.html`. Nada é buscado em tempo de execução — o dado vive dentro da própria página.

## Fluxo da semana

```bash
# 1. exporte a query do TFS (ver abaixo) e salve como dados/AAAA-MM-DD.csv
# 2. escreva ou gere relatorios/AAAA-MM-DD.md
python build.py
git add . && git commit -m "chore: add the weekly report for AAAA-MM-DD"
git push origin master
```

A data do nome do arquivo é sempre a **sexta-feira** que fecha o recorte. O `build.py` deriva o
período da semana útil: da segunda até essa sexta.

O comando `/semana` no Claude Code faz os passos 2 e 3 e ainda grava a nota no vault do Obsidian.

## A query do TFS

Query `Segunda`, tipo **Tree of work items**, no projeto XVIA.

**Filtros — top level**

| Campo | Operador | Valor |
|---|---|---|
| Work Item Type | = | Epic |
| And State | <> | Removed |

**Filtros — linked work items**

| Campo | Operador | Valor |
|---|---|---|
| Work Item Type | In | Product Backlog Item, Task, Bug |
| And Area Path | Under | `XVIA\SGD` |
| And Changed Date | >= | `@Today - 7` |
| And Assigned To | = | @Me |

Filter options: `Match linked work items first`.

**Colunas:** `ID`, `Work Item Type`, `Title`, `State`, `Assigned To`, `Area Path`,
`Iteration Path`, `Tags`, `Changed Date`, `Closed Date`, `Created Date`.

Não inclua `Description` — é HTML e infla o CSV sem servir ao relatório.

Sem filtro de `State`: o recorte por estado é feito no relatório, não na query. Filtrar por `Done`
esconde justamente o que a reunião de segunda precisa ver.

## Como o estado vira número

| Bloco da página | Estados do TFS |
|---|---|
| Finalizado | `Done`, `Closed` |
| Em andamento | `In Progress`, `Committed` |
| Pendente | `To Do`, `New`, `Approved` |
| Bloqueado | qualquer estado + tag `bloqueio` |

`Removed` é descartado. PBI, Feature e Epic não viram linha: eles dão o agrupamento, e contá-los
como pendência infla o número sem dizer nada. O que aparece são Tasks e Bugs.

**Bloqueio é tag.** O processo Scrum deste TFS não tem campo de impedimento, então quem trava marca
a tag `bloqueio` no work item. Sem a tag, a coluna nasce zerada.

## Estrutura

```
dados/AAAA-MM-DD.csv        export bruto da query
relatorios/AAAA-MM-DD.md    resumo em prosa da semana (opcional)
build.py                    CSV + md -> index.html
index.html                  gerado; não editar o bloco entre os marcadores DATA
assets/ds-sis.css           Design System do Governo de MS
assets/css/relatorio.css    estilos da página
```

## Rodar local

```bash
pip install -r requirements.txt
python build.py
python -m http.server 8743
```

O `index.html` também abre por duplo clique, sem servidor.

## Publicação

GitHub Pages, modo *deploy from a branch*: raiz da branch `master`. Um `git push` republica em
cerca de um minuto. Não adicione workflow de Pages em `.github/` — os dois modos conflitam.
