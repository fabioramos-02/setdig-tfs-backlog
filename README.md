# Backlog TFS — SETDIG

Visualizador de work items estilo Azure DevOps + skill `/tfs` para Claude Code.
Publicado **gratuitamente no GitHub Pages** (estático, read-only, público).

🔗 **Online:** https://fabioramos-02.github.io/setdig-tfs-backlog/

## Arquitetura (modelo "git como banco de dados")

```
/tfs (Claude Code)            GitHub                    Público
  edita backlog.json  ──push──►  Pages serve  ──F5──►  só LÊ o viewer
  build.py injeta no HTML        index.html             status commitado
  commit semântico               + backlog_viewer.html  vence cache local
```

- **`backlog.json`** — fonte da verdade (49+ work items + `generated_at`).
- **`backlog_viewer.html`** — viewer self-contained (DATA injetado inline; abre com duplo-clique e no Pages, sem fetch/CORS).
- **`build.py`** — lê o JSON, carimba `generated_at` e injeta no HTML.
- **`index.html`** — entrada do GitHub Pages → redireciona pro viewer.
- Sem API, sem banco, sem servidor. Persistência = commit versionado.

## Estrutura

```
tfs/
├── backlog.json          # Fonte da verdade (editar aqui ou via /tfs)
├── build.py              # backlog.json → injeta DATA no viewer
├── backlog_viewer.html   # Viewer (gerado/injetado)
├── index.html            # Entrada do GitHub Pages
├── backlog.xlsx          # Legado (autoria em massa opcional)
├── xlsx_to_json.py       # Legado: xlsx → json
└── skill/SKILL.md        # Skill /tfs para Claude Code
```

## Como usar

### Inserir item (recomendado: skill `/tfs`)

No Claude Code, na pasta do repo:

```
/tfs Task: ajustar regex de Cartas de Serviço em data_processor.py
/tfs PBI: como gestor quero ver cartas duplicadas entre órgãos diferentes
/tfs status 117 = Finalizado
```

A skill insere no `backlog.json`, roda `build.py` e faz **commit semântico + push** automático. O GitHub Pages redeploya sozinho (~1 min).

### Editar à mão

```bash
# 1. editar backlog.json
# 2. regenerar o viewer
python build.py
# 3. publicar
git add backlog.json backlog_viewer.html && git commit -m "feat(backlog): ..." && git push
```

### Visualizar local

Abrir `backlog_viewer.html` com duplo-clique (funciona offline, dados inline).

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
