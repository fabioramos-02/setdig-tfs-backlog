# /tfs — Inserir item no backlog TFS SETDIG

Insere um novo work item direto em `C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.json` (fonte da verdade) a partir de linguagem natural, respeitando a hierarquia oficial do TFS/Azure DevOps da SETDIG, regenera o viewer via `build.py` e publica no GitHub Pages com **commit semântico automático + push**.

**Repo:** `https://github.com/fabioramos-02/setdig-tfs-backlog` (público, branch `master`, GitHub Pages).
**Fonte da verdade:** `backlog.json` (NÃO o xlsx — o xlsx é legado/autoria em massa opcional).

## Quando invocar

Quando o usuário digitar `/tfs` seguido de uma descrição de item, ou pedir para adicionar épico/feature/PBI/task/bug ao backlog.

Exemplos:
- `/tfs Task: ajustar regex de Cartas de Serviço em data_processor.py`
- `/tfs PBI: como gestor quero ver cartas duplicadas entre órgãos diferentes`
- `/tfs Feature: nova integração GA4 com Looker Studio`

## Hierarquia oficial TFS SETDIG (placeholders ancorados no backlog)

```
Epic 100  Negócio e Governança
├── Feature 101  2.2 Levantamento e Descoberta
│   └── PBI 103  Dashboard Analítico Portal Único MS
│       └── Tasks 104..108
└── Feature 102  2.3 Cartas de Serviço
    └── PBI 109  Cruzamento e Higienização de Cartas (CGE-MS)
        └── Tasks 110..114
```

Outros Epics oficiais (não estão no xlsx ainda — incluir como placeholder se necessário):

- Epic 1: Infraestrutura e Plataforma Base
  - 1.1 Provisionamento de Ambientes
  - 1.2 DevSecOps e Pipeline
  - 1.3 Observabilidade e Monitoramento
  - 1.4 Segurança e LGPD
- Epic 2: Negócio e Governança (já presente — id 100)
  - 2.1 Governança do Programa
  - 2.2 Levantamento e Descoberta (id 101)
  - 2.3 Cartas de Serviço (id 102)
  - 2.4 Gestão da Mudança
- Epic 3: Desenvolvimento e Integrações
  - 3.1 Portal Único do Cidadão
  - 3.2 Autenticação e Identidade
  - 3.3 Gestão de Formulários
  - 3.4 Gestão de Fluxos
  - 3.5 APIs e Integrações
  - 3.6 Auditoria e Rastreabilidade
- Epic 4: Homologação e Migração
  - 4.1 Estratégia de Homologação
  - 4.2 Migração de Dados
  - 4.3 Homologação Integrada
  - 4.4 Shadow Operation
- Epic 5: Implantação e Go Live

## O que fazer

### 1. Ler o backlog atual

```python
import json
PATH = r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\backlog.json"
data = json.load(open(PATH, encoding="utf-8"))
items = data["items"]
```

Extrair: lista de itens existentes (`csv_id`, `tipo`, `titulo`, `csv_id_pai`) e `max(csv_id)`.

### 2. Inferir os campos

**tipo** — regras em ordem de prioridade:
1. Usuário declarou explicitamente ("Epic:", "Feature:", "PBI:", "Task:", "Bug:") → usar esse
2. Palavras "bug", "erro", "falha", "corrigir", "regressão" → Bug
3. "como usuário", "como gestor", "como analista", "como DBA", "quero", "para que" → Product Backlog Item
4. Arquivo específico mencionado (`app.py`, função, endpoint, módulo) → Task
5. Módulo ou entrega de valor ampla sem código específico → Feature
6. Tema de alto nível sem pai claro → Epic

**csv_id_pai** — inferir pelo conteúdo:

| Termos | Sugestão de pai |
|---|---|
| dashboard, matomo, GA4, portal, acessos, analytics, transitions, ranking de cartas | PBI 103 (Tasks) ou Feature 101 (PBIs) |
| cartas de serviço, cruzamento, duplicata, similaridade, CGE, higienização | PBI 109 (Tasks) ou Feature 102 (PBIs) |
| formulário, fluxo, API, autenticação, portal cidadão, identidade | Epic 3 → pedir confirmação sobre Feature 3.x |
| infraestrutura, pipeline, LGPD, observabilidade, DevSecOps | Epic 1 → pedir confirmação sobre Feature 1.x |
| homologação, migração, shadow operation | Epic 4 → pedir confirmação sobre Feature 4.x |
| governança, ritos, indicadores do programa | Feature 2.1 (placeholder — perguntar antes de criar) |
| gestão da mudança, comunicação, treinamento | Feature 2.4 (placeholder — perguntar antes de criar) |

Regras de ancoragem:
- Se tipo = Task → pai deve ser PBI
- Se tipo = PBI → pai deve ser Feature
- Se tipo = Feature → pai deve ser Epic
- Se tipo = Epic → sem pai (csv_id_pai = None)

Se ambíguo (> 1 candidato razoável) → **listar até 3 opções e pedir confirmação** antes de salvar. Nunca inventar.

**csv_id** → `max(csv_id existente) + 1` (a partir de 115).

**titulo** → extrair limpo e objetivo (sem verbos de instrução).

**descricao** → seguir padrão TFS conforme tipo (ver seção abaixo).

**projeto_ado** → "SETDIG" (padrão).

**prioridade** → 2 (padrão Alta), salvo se usuário mencionar urgência (→ 1) ou baixa prioridade (→ 4).

**sprint, estimativa_horas, tags** → preencher se mencionados; senão deixar vazio.

### 3. Padrão de descrição por tipo (TFS.pdf v1 jul/2024)

**Epic / Feature** — campo `descricao` deve conter:

```
**Descrição**
<visão do valor a ser entregue>

**Critérios de Aceitação**
- <critério 1>
- <critério 2>
- ...
```

**Product Backlog Item** — campo `descricao` deve conter:

```
**História do usuário**
Como <papel>, quero <ação>, para <benefício>.

**Requisitos**
- <requisito funcional 1>
- <requisito funcional 2>

**Critérios de Aceitação**
- <critério mensurável 1>
- <critério mensurável 2>
```

**Task** — campo `descricao` deve conter:

```
<breve descrição da atividade>

Subatividades:
- <passo 1>
- <passo 2>
```

(Subatividades só se houver decomposição natural.)

**Bug** — campo `descricao` deve conter:

```
**Sintoma**
<o que está errado, com evidência>

**Passos para reproduzir**
1. ...
2. ...

**Resultado esperado**
<o que deveria acontecer>
```

### 4. Mostrar prévia antes de salvar

```
csv_id  | tipo    | titulo                        | csv_id_pai | sprint
--------|---------|-------------------------------|------------|-------
115     | Task    | Ajustar regex de cartas em... | 108        | Sprint 2

Descrição:
<conteúdo proposto>
```

Perguntar: **"Inserir? (s/n)"**

### 5. Inserir no backlog.json

```python
items.append({
    "csv_id": csv_id,
    "tipo": tipo,
    "titulo": titulo,
    "descricao": descricao,
    "projeto_ado": "SETDIG",
    "csv_id_pai": csv_id_pai,
    "prioridade": prioridade,
    "sprint": sprint,
    "estimativa_horas": estimativa_horas,
    "tags": tags,
    "ado_id": "",
    "status": "A fazer",
})
json.dump(data, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

Status novo **sempre** `A fazer`. Manter os 12 campos do schema.

### 6. Regenerar viewer (build.py)

```python
import subprocess
subprocess.run(["python", r"C:\Users\Fabio\Documents\SETDIG\2026\tfs\build.py"], check=True)
```

`build.py` carimba `generated_at` (nova versão) e injeta o DATA inline no `backlog_viewer.html`. Não depende de openpyxl.

### 7. Commit semântico + push (automático)

Sem perguntar — após o build, publicar:

```bash
cd "C:/Users/Fabio/Documents/SETDIG/2026/tfs"
git add backlog.json backlog_viewer.html
git commit -m "feat(backlog): adiciona <Tipo> <csv_id> — <titulo curto>"
git push
```

Regras do commit:
- Tipo Conventional Commits sempre `feat(backlog):` para item novo (`fix(backlog):` se for correção de item existente).
- Mensagem em português, `<titulo curto>` ≤ 60 chars, sem assinatura de IA.
- 1 item = 1 commit. Vários itens na mesma chamada = 1 commit consolidado descrevendo o conjunto.
- GitHub Pages redeploya sozinho no push (~1 min). URL pública servida pelo `index.html` → `backlog_viewer.html`.

Confirmar: `[OK] Item <csv_id> inserido, buildado e publicado (push em master).`

## Contexto do projeto (para inferências)

**Repo de analytics:** `C:\Users\Fabio\Documents\SETDIG\2026\projetos\matomo\matomo-analytics-dashboard`

Arquivos-chave:
- `app.py` — interface Streamlit
- `api/matomo_client.py` — cliente Matomo API
- `api/ga4_client.py` — cliente GA4
- `utils/data_processor.py` — processamento e regex de cartas
- `config.py` — tokens e IDs

**Repo de cruzamento:** `C:\Users\Fabio\Documents\SETDIG\2026\projetos\cruzamento-carta`

Arquivos-chave:
- `src/cruzamento_carta/db.py` — conexão via .env
- `src/cruzamento_carta/html_clean.py` — strip HTML + entities
- `src/cruzamento_carta/queries.py` — SQL com JOIN gerenciamento_jornada
- `src/cruzamento_carta/similaridade.py` — score composto 8 campos
- `src/cruzamento_carta/clusters.py` — agrupamento + diff
- `src/cruzamento_carta/relatorio.py` — relatório HTML

Fontes de dados:
- Portal Único → Matomo API (idSite=298)
- MS Digital → Google Analytics GA4
- Cartas de Serviço → Postgres (via VPN)

Se o usuário mencionar algo relacionado a essas fontes ou arquivos, usar para enriquecer título e inferir pai.

## Regras

- Nunca salvar sem mostrar prévia e receber confirmação.
- Nunca inventar `csv_id_pai` — se não souber, listar até 3 opções e perguntar.
- Manter tipos exatos: `Epic`, `Feature`, `Product Backlog Item`, `Task`, `Bug`.
- Respeitar hierarquia TFS: Epic → Feature → PBI → Task. Sem Feature dentro de Feature.
- Descrição **sempre** segue o padrão TFS do tipo correspondente.
- Sempre rodar `python build.py` após editar o `backlog.json`, e em seguida commit + push (sem perguntar).
- Itens placeholder (100, 101, 102) ancoram itens reais do TFS — campo `ado_id` deve ser preenchido quando vinculado ao Azure DevOps.

## Status dos work items

Campo `status` no JSON: `A fazer` | `Em progresso` | `Finalizado`. Default de item novo = `A fazer`.

**Persistência (modelo "git como banco de dados"):**
- O status COMMITADO no `backlog.json` é a verdade pública. Para mudar o status oficial de um item: editar `status` no `backlog.json` → `python build.py` → commit + push.
- No viewer publicado (read-only, público), qualquer pessoa pode marcar status no painel de detalhe, mas isso fica só no `localStorage` dela.
- Cada deploy carimba `generated_at` novo. Ao dar F5 numa versão nova, o viewer **descarta os overrides locais antigos** (ver `VER_KEY` no HTML) — então o status commitado sempre vence cache velho. É exatamente o comportamento desejado: status oficial não se perde nem fica mascarado.

Para mudar status de um item existente via comando, basta pedir (ex.: `/tfs status 117 = Finalizado`) → editar JSON → build → commit `fix(backlog): status <id> → Finalizado` → push.
