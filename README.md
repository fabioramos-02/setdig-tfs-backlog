# Backlog TFS — SETDIG

Visualizador de work items estilo Azure DevOps + skill `/tfs` para Claude Code.

## Estrutura

```
tfs/
├── backlog.xlsx          # Planilha fonte (editar aqui)
├── backlog.json          # Gerado automaticamente
├── backlog_viewer.html   # Visualizador — abrir no browser
├── xlsx_to_json.py       # Converte xlsx → json + html
├── update_descriptions.py# Atualiza descrições na planilha
└── skill/
    └── SKILL.md          # Skill /tfs para Claude Code
```

## Como usar

### 1. Visualizar backlog

```bash
# Regenerar HTML após editar a planilha
python xlsx_to_json.py

# Abrir no browser
start backlog_viewer.html   # Windows
open backlog_viewer.html    # Mac
```

### 2. Skill `/tfs` no Claude Code

Copiar `skill/SKILL.md` para `~/.claude/skills/tfs/SKILL.md`:

```bash
# Windows
mkdir "%USERPROFILE%\.claude\skills\tfs"
copy skill\SKILL.md "%USERPROFILE%\.claude\skills\tfs\SKILL.md"

# Mac/Linux
mkdir -p ~/.claude/skills/tfs
cp skill/SKILL.md ~/.claude/skills/tfs/SKILL.md
```

Depois usar no Claude Code:

```
/tfs Task: adicionar cache em matomo_client.py para evitar timeout
/tfs PBI: como gestor quero ver comparativo mensal de cartas de serviço
/tfs Epic: integração com dados do banco de cartas de serviço
```

## Hierarquia de work items

```
Epic → Feature → Product Backlog Item → Task | Bug
```

## Projeto

Dashboard Analítico Portal Único MS — SETDIG/SGD  
Fontes: Matomo (Portal, idSite=298) · Google Analytics GA4 (MS Digital) · Banco (Cartas de Serviço)  
App em produção: https://setdig-dados.streamlit.app/

## Dependências

```bash
pip install openpyxl
```
