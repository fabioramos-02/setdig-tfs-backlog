# /tfs — Inserir item no backlog TFS

Insere um novo work item em `C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.xlsx` a partir de linguagem natural, depois regenera `backlog_viewer.html`.

## Quando invocar

Quando o usuário digitar `/tfs` seguido de uma descrição de item, ou pedir para adicionar épico/feature/PBI/task/bug ao backlog.

Exemplos:
- `/tfs Task: adicionar cache em matomo_client.py para evitar timeout`
- `/tfs PBI: como gestor quero ver comparativo mensal de cartas de serviço`
- `/tfs Epic: integração com dados do banco de cartas de serviço`

## O que fazer

### 1. Ler o backlog atual

```python
import openpyxl
wb = openpyxl.load_workbook(r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.xlsx", data_only=True)
ws = wb["Backlog"]
```

Extrair: lista de itens existentes (csv_id, tipo, titulo, csv_id_pai) e o max(csv_id).

### 2. Inferir os campos

**tipo** — regras em ordem de prioridade:
1. Usuário declarou explicitamente ("Epic:", "Task:", "Bug:", "PBI:") → usar esse
2. Palavras "bug", "erro", "falha", "corrigir" → Bug
3. "como usuário", "como gestor", "quero", "para que" → Product Backlog Item
4. Arquivo específico mencionado (`app.py`, função, endpoint) → Task
5. Módulo ou entrega de valor ampla sem código específico → Feature
6. Tema de alto nível sem pai claro → Epic

**csv_id_pai** — buscar no xlsx o item pai mais provável:
- Se tipo = Feature → buscar Epic com título mais relacionado
- Se tipo = PBI → buscar Feature mais relacionada
- Se tipo = Task ou Bug → buscar PBI mais relacionado
- Se ambíguo (> 1 candidato razoável) → **listar até 3 opções e pedir confirmação** antes de salvar

**csv_id** → max(csv_id existente) + 1

**titulo** → extrair da descrição do usuário, limpo e objetivo (sem verbos de instrução)

**descricao** → contexto adicional que o usuário forneceu, ou vazio

**projeto_ado** → "SETDIG" (padrão)

**prioridade** → 2 (padrão Alta), salvo se usuário mencionar urgência (→ 1) ou baixa prioridade (→ 4)

**sprint, estimativa_horas, tags** → preencher se mencionados; senão deixar vazio

### 3. Mostrar prévia antes de salvar

Exibir a linha que será inserida:

```
csv_id  | tipo    | titulo                        | csv_id_pai | sprint
--------|---------|-------------------------------|------------|-------
21      | Task    | Adicionar cache em matomo_... | 10         |
```

Perguntar: **"Inserir? (s/n)"**

### 4. Inserir na planilha

```python
ws.append([csv_id, tipo, titulo, descricao, "SETDIG", csv_id_pai, prioridade, sprint, estimativa_horas, tags, ""])
wb.save(r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.xlsx")
```

### 5. Regenerar HTML

```python
import subprocess
subprocess.run(["python", r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\xlsx_to_json.py"])
```

Confirmar: `[OK] Item inserido. HTML atualizado.`

## Contexto do projeto (para inferências)

**Repo principal:** `C:\Users\Fabio\Documents\SETDIG\2026\projetos\matomo\matomo-analytics-dashboard`

Arquivos-chave:
- `app.py` — interface Streamlit
- `api/matomo_client.py` — cliente Matomo API
- `utils/data_processor.py` — processamento e regex de cartas
- `config.py` — tokens e IDs

Fontes de dados do projeto:
- Portal Único → Matomo API (idSite=298)
- MS Digital → Google Analytics GA4
- Cartas de Serviço → banco de dados

Se o usuário mencionar algo relacionado a essas fontes ou arquivos, usar para enriquecer título e inferir pai.

## Regras

- Nunca salvar sem mostrar prévia e receber confirmação
- Nunca inventar csv_id_pai — se não souber, perguntar
- Manter tipos exatos: `Epic`, `Feature`, `Product Backlog Item`, `Task`, `Bug`
- Sempre rodar xlsx_to_json.py após salvar
