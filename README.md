# Backlog TFS — SETDIG

Visualizador de work items estilo Azure DevOps + skill `/tfs` para Claude Code.
Publicado **gratuitamente no GitHub Pages** (estático, read-only, público).

🔗 **Online:** https://fabioramos-02.github.io/setdig-tfs-backlog/

## Arquitetura (modelo "git como banco de dados")

```
/tfs (Claude Code)            GitHub                    Público
  edita backlog.json  ──push──►  Pages serve  ──F5──►  só LÊ o viewer
  build.py injeta no HTML        index.html             status commitado
  commit semântico               + index.html  vence cache local
```

- **`backlog.json`** — fonte da verdade (49+ work items + `generated_at`).
- **`index.html`** — viewer self-contained (DATA injetado inline; abre com duplo-clique e no Pages, sem fetch/CORS).
- **`build.py`** — lê o JSON, carimba `generated_at` e injeta no HTML.
- **`index.html`** — entrada do GitHub Pages → redireciona pro viewer.
- Sem API, sem banco, sem servidor. Persistência = commit versionado.

## Estrutura

```
setdig-tfs-backlog/
├── backlog.json              # Fonte da verdade (editar aqui ou via /tfs)
├── build.py                  # gera assets/js/data.js + relatorios.html
├── index.html                # Viewer do backlog (Pages serve direto)
├── relatorios.html           # Hub de relatórios semanais (gerado)
├── requirements.txt          # Dependência: markdown
├── CLAUDE.md                 # Convenções do projeto
├── assets/
│   ├── ds-sis.css            # Design System MS (@design-system-ms/ds-sis)
│   ├── css/
│   │   ├── viewer.css        # Estilos do backlog viewer
│   │   └── relatorios.css    # Estilos da página de relatórios
│   └── js/
│       ├── data.js           # Gerado: window.BACKLOG_DATA = {...}
│       └── viewer.js         # Lógica do viewer (tree, detail, filtros, md)
├── relatorios/
│   └── [YYYY-MM-DD]-relatorio-semanal.md
└── docs/
    └── TFS.pdf               # Padrão TFS SETDIG v1 jul/2024
```

Arquitetura **self-contained**: nenhum fetch em runtime. `assets/js/data.js` é carregado como script comum (funciona em `file://` e no Pages); `build.py` reescreve seu blob entre marcadores `/*DATA_START*/.../*DATA_END*/`.

Skill `/tfs` (Claude Code) instalada globalmente em `~/.claude/skills/tfs/SKILL.md` — não versionada neste repo.

## Relatórios semanais

`/tfs semana [N]` gera um arquivo `relatorios/[YYYY-MM-DD]-relatorio-semanal.md` listando PBIs criados nos últimos N dias (default 7), agrupados por `[PROJETO]`, com resumo, status e referência ao local de trabalho. Após gerar, o `build.py` converte todos os relatórios em HTML inline (sem fetch) e publica em:

🔗 **Relatórios online:** https://fabioramos-02.github.io/setdig-tfs-backlog/relatorios.html

O `index.html` tem um botão "Relatórios" no header que leva para a página.

Skill `/tfs` (Claude Code) instalada globalmente em `~/.claude/skills/tfs/SKILL.md` — não versionada neste repo.

## Como usar

### Inserir item (recomendado: skill `/tfs`)

No Claude Code, na pasta do repo:

```
/tfs Task: ajustar regex de Cartas de Serviço em data_processor.py
/tfs PBI: [X-VIA] Ajustes nos documentos - 23-06-2026
/tfs status 117 = Finalizado
/tfs semana             # resumo dos PBIs dos últimos 7 dias (reunião de planejamento)
/tfs semana 14          # últimos 14 dias
```

A skill insere no `backlog.json`, roda `build.py` e faz **commit semântico + push** automático. O GitHub Pages redeploya sozinho (~1 min).

### Convenção de título PBI (obrigatória)

Todo PBI segue o formato:

```
[PROJETO] demanda - DD-MM-YYYY
```

Exemplo: `[X-VIA] Ajustes nos documentos - 23-06-2026`

Esse padrão alimenta o subcomando `/tfs semana`, que filtra PBIs por data parseada do próprio título e agrupa por `[PROJETO]` — usado para responder rápido "o que foi feito na semana passada" em reuniões de planejamento. Task/Feature/Epic/Bug mantêm título livre.

### Editar à mão

```bash
# 1. editar backlog.json (única fonte da verdade)
# 2. regenerar o viewer
python build.py
# 3. publicar
git add backlog.json assets/js/data.js && git commit -m "feat(backlog): ..." && git push
```

> O `backlog.xlsx` e o pipeline `xlsx_to_json.py` foram removidos em 2026-06-24. O JSON é a única fonte; `build.py` injeta inline no viewer.

### Visualizar local

Abrir `index.html` com duplo-clique (funciona offline, dados inline).

## Persistência de status

Status (`A fazer` / `Em progresso` / `Finalizado`) é campo no `backlog.json`.
Cada deploy carimba `generated_at`; ao dar F5 numa versão nova o viewer descarta
overrides locais antigos do `localStorage` — **o status commitado sempre vence**.

## Hierarquia de work items

```
Epic → Feature → Product Backlog Item → Task | Bug
```

## Projeto

Dashboard Analítico Portal Único MS — SETDIG/SGD
Fontes: Matomo (Portal, idSite=298) · Google Analytics GA4 (MS Digital) · Banco (Cartas de Serviço)
App em produção: https://setdig-dados.streamlit.app/
