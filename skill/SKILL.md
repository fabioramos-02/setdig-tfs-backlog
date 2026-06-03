# /tfs — Inserir item no backlog TFS

Insere work item em `C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.xlsx`, regenera JSON + HTML.

## Quando invocar

Usuário usa `/tfs` + descrição de item, ou pede para adicionar épico/feature/PBI/task/bug ao backlog.

Exemplos:
- `/tfs Task: implementar cache no matomo_client.py`
- `/tfs PBI: como gestor quero ver ranking mensal de cartas de serviço`
- `/tfs Bug: timeout na API Matomo com period=year`
- `/tfs Feature: 2.4 Análise de Abandono`

---

## Estrutura atual do backlog

> Última atualização: 2026-06-03 — max csv_id = **134** → próximo = **135**

```
100  Epic    Negocio e Governanca
101    Feature  2.2 Levantamento e Descoberta
103      PBI      Dashboard Analítico Portal Único MS
104          Task   Visualizar top páginas mais acessadas por período
105          Task   Exibir palavras-chave mais buscadas no portal
106          Task   Mostrar jornada de navegação (Transitions) da carta principal
107          Task   Integrar dados GA4 para app MS Digital
108          Task   Filtrar e rankear Cartas de Serviço via regex nas URLs
127      PBI      Estudo de Uso do Filtro de Perfil (bench-carta)
128          Task   Elaborar apresentação gerencial da recomendação REMOVER
129          Task   Documentar limitação event tracking e propor instrumentação
130      PBI      Prototipagem Seção Categorias Portal MS
131          Task   Apresentar protótipo para validação com partes interessadas
132          Task   Registrar feedback e definir próximos passos
133      PBI      Levantamento Material Design System MS
134          Task   Publicar catálogo DS-MS no vault Obsidian e wiki TFS
102    Feature  2.3 Cartas de Servico
109      PBI      Cruzamento e Higienização de Cartas de Serviço (CGE-MS)
110          Task   Detectar colunas HTML/entities (--probe-schema)
111          Task   Snapshot completo das cartas ativas
112          Task   Detectar duplicatas exatas e similares
113          Task   Pontuação de qualidade + cadastro modelo sugerido
114          Task   Relatório HTML offline (KPIs, treemap, diff)
115    Feature  2.4 Migração EDS → XVia
116      PBI      Documentação governança módulo FormFlow
117          Task   Criar documentacao-tecnica.md do FormFlow
118          Task   Revisar gaps FormFlow v1 com equipe XVia
119      PBI      Validação e handoff docs com fornecedor XVia
120          Task   Consolidar lista de gaps por módulo (todos os 6)
121          Task   Agendar reunião de repasse técnico com equipe XVia
122    Feature  2.5 ABEPTIC 2026 — Avaliação IOSPD
123      PBI      Convalidação IOSPD 2026 — MS
124          Task   Finalizar evidências Dimensão 1.1 para defesa
125          Task   Revisar backlog_convalidacao_v3.csv e fechar gaps abertos
126          Task   Submeter relatório final IOSPD ao ABEP 2026
```

**Mapeamento pai rápido:**
- Nova Task/Bug para dashboard/Matomo/GA4/jornada → csv_id_pai = **103** (PBI Dashboard Analítico)
- Nova Task/Bug para cartas de serviço/CGE/qualidade → csv_id_pai = **109** (PBI Cruzamento Cartas)
- Novo PBI sobre levantamento/descoberta/analytics → csv_id_pai = **101** (Feature 2.2)
- Novo PBI sobre cartas/banco/CGE → csv_id_pai = **102** (Feature 2.3)
- Nova Feature → csv_id_pai = **100** (Epic Negocio e Governanca)

---

## Inferir tipo

1. Usuário declarou ("Task:", "Bug:", "PBI:", "Feature:", "Epic:") → usar esse
2. Palavras "bug", "erro", "falha", "corrigir", "fix" → **Bug**
3. "como usuário", "como gestor", "quero que", "para que" → **Product Backlog Item**
4. Arquivo/função/endpoint específico mencionado → **Task**
5. Entrega de valor, módulo novo, sem código específico → **Feature**
6. Tema amplo sem pai natural → **Epic**

---

## Como executar

### 1. Ler backlog atual

```python
import openpyxl
wb = openpyxl.load_workbook(r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.xlsx", data_only=True)
ws = wb["Backlog"]
rows = list(ws.iter_rows(min_row=2, values_only=True))
max_id = max(int(r[0]) for r in rows if r[0])
novo_id = max_id + 1
```

### 2. Montar linha com campos inferidos

| Campo | Valor |
|-------|-------|
| csv_id | max_id + 1 |
| tipo | inferido (ver regras acima) |
| titulo | extraído da descrição do usuário |
| descricao | contexto adicional ou vazio |
| projeto_ado | SETDIG |
| csv_id_pai | inferido pelo mapeamento acima; se ambíguo → listar opções |
| prioridade | 2 (padrão Alta); 1 se urgente; 4 se baixa |
| sprint | se mencionado; senão vazio |
| estimativa_horas | se mencionado; senão vazio |
| tags | se mencionado; senão vazio |
| ado_id | vazio |

### 3. Mostrar prévia antes de salvar

```
csv_id | tipo    | titulo                            | csv_id_pai
-------|---------|-----------------------------------|----------
115    | Task    | Implementar cache matomo_client   | 103
```

Perguntar: **"Inserir? (s/n)"**

### 4. Inserir na planilha

```python
ws.append([novo_id, tipo, titulo, descricao, "SETDIG",
           csv_id_pai, prioridade, sprint, estimativa_horas, tags, ""])
wb.save(r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.xlsx")
```

### 5. Regenerar HTML

```python
import subprocess
subprocess.run(["python",
    r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\xlsx_to_json.py"])
```

Confirmar: `[OK] Item csv_id=115 inserido. HTML atualizado.`

---

## Contexto técnico do projeto

**Repo app:** `C:\Users\Fabio\Documents\SETDIG\2026\projetos\matomo\matomo-analytics-dashboard`

| Arquivo | Responsabilidade |
|---------|-----------------|
| app.py | Interface Streamlit |
| api/matomo_client.py | Cliente Matomo API (idSite=298) |
| utils/data_processor.py | Regex cartas de serviço, filtros |
| config.py | Tokens, IDs |

**Fontes de dados:** Matomo (Portal Único) · GA4 (app MS Digital) · Banco CGE-MS (Cartas)

**App produção:** https://setdig-dados.streamlit.app/

---

## Regras

- Nunca salvar sem prévia + confirmação
- Nunca inventar csv_id_pai — se não souber, listar opções do backlog
- Tipos exatos: `Epic` | `Feature` | `Product Backlog Item` | `Task` | `Bug`
- Sempre rodar xlsx_to_json.py após salvar
- Se backlog.xlsx estiver aberto (PermissionError): avisar, não abortar silenciosamente
