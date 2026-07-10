# Taxonomia do Backlog SETDIG — Dicionário de Dados

Vigente desde **10-07-2026**. Substitui a estrutura antiga (Epic único "Negócio e Governança").

## Objetivo

Dar à equipe (e à skill `/tfs`) uma regra objetiva de **onde lançar** Epic, Feature ou PBI, agora que o foco do PO se divide entre **Portal Atual (EDS)**, **Novo Portal (XVia)** e demandas transversais da **SGD**, além de **Premiações**.

## Os 4 Epics raiz

```
Epic  SGD              — demandas de gestão/governança sem vínculo a portal
Epic  Portal Atual     — sistema legado (EDS), em sustentação até migração completa
Epic  Novo Portal      — arquitetura nova (XVia), destino da migração
Epic  Premiações       — participação em prêmios/índices institucionais (ABEPTIC, IOSPD)
```

### Epic: SGD

**O que é:** hub de demandas estratégicas e de gestão que atendem à Superintendência de Governo Digital como um todo — não é "código" em nenhum portal.

**Regra de ouro:** se a entrega é um documento, relatório, decisão arquitetural, reunião ou demanda de gestão que **não mexe em repositório de portal**, entra aqui.

**Features:**
- **Levantamento e Descoberta** — dashboards de uso (Matomo/GA4), pesquisas, prototipagem, DS-MS, mapeamentos institucionais, demandas de outros times/plataformas (Responde-MS, Prosas) quando não são especificamente sobre o Portal Único.
- **Reunião** — alinhamentos de gestão (Duda, Glau, GTD e demais interlocutores) sem ata vinculada a um portal.

**Tags típicas:** `[SETDIG]`, `[DS-MS]`, `[CENSO]`, `[TEMPLATE-EMAIL]`, `[RESPONDE-MS]`, `[PROSAS]`.

**Exemplos reais:** Dashboard Analítico Portal Único MS (PBI 103); POC Storybook DS-MS (PBI 152); Alinhamento com a Duda (PBI 221).

### Epic: Portal Atual (EDS)

**O que é:** ambiente legado do Portal Único MS. Sustentação, correções e melhorias pontuais até a migração completa para o XVia.

**Regra de ouro:** se a alteração é feita no sistema que **será descontinuado**, o item mora aqui.

**Features (módulos, espelhados 1:1 no Novo Portal):**

| Módulo | Cobre |
|---|---|
| Cartas de Serviço | Higienização, duplicidade, cruzamento com CGE-MS |
| Control SSO | Autenticação e single sign-on |
| Admin | Administração, configuração, gestão de usuários |
| Integrador | Integrações com sistemas/órgãos externos |
| FormFlow | Construtor e gestão de formulários |
| CMS Notícias | Gestão de conteúdo e notícias publicadas |
| Reuniões | Agendamento/gestão de reuniões *do portal* (módulo — não confundir com Feature "Reunião" da SGD) |
| Portal | Núcleo (home, navegação, categorias) |
| Atendimento | Canais de atendimento ao cidadão |

**Tags típicas:** `[EDS]`, `[CARTAS]`, `[CARTAS-DE-SERVICO]`, `[LOGO-PERIODO-ELEITORAL]`.

**Exemplos reais:** Registro de bug no fluxo do FormFlow (PBI 213); Alteração da logo do Portal — período eleitoral (PBI 201).

### Epic: Novo Portal (XVia)

**O que é:** futuro do produto — nova arquitetura, entregue com o fornecedor XVia.

**Regra de ouro:** se o código/entrega vai rodar na **infraestrutura nova**, o item mora aqui.

**Features:** Migração EDS → XVia (documentação, handoff, validação) + os mesmos 8 módulos do Portal Atual, espelhados (Control SSO, Admin, Integrador, FormFlow, CMS Notícias, Reuniões, Portal, Atendimento).

**Tags típicas:** `[X-VIA]`.

**Exemplos reais:** Migração das APIs do MS Digital (PBI 179); Mapeamento Institucional XVia — Órgãos do Governo MS (PBI 135).

### Epic: Premiações

**O que é:** participação da SETDIG em prêmios e índices de avaliação institucional.

**Regra de ouro:** ABEPTIC, IOSPD, índices, apresentações a comitê.

**Feature:** Abeptic — Avaliação IOSPD 2026.

**Exemplos reais:** Convalidação IOSPD 2026 — MS (PBI 123); Apresentação Índice ABEP p/ Comitê (PBI 141).

## Fluxo de decisão — "onde lançar?"

1. **É reunião, documento, relatório ou decisão de gestão sem vínculo a portal?** → Epic SGD.
2. **É prêmio, índice ou avaliação institucional (ABEPTIC/IOSPD)?** → Epic Premiações.
3. **Envolve um módulo do Portal Único (SSO, Admin, Integrador, FormFlow, CMS, Reuniões, Portal, Atendimento)?**
   - Roda no ambiente **legado** (EDS)? → Epic Portal Atual, Feature do módulo.
   - Roda na infra **nova**, com o fornecedor XVia? → Epic Novo Portal, Feature do módulo.
4. **Ainda em dúvida?** → perguntar ao PO antes de lançar (nunca inventar `csv_id_pai`).

## Manutenção

Esta taxonomia espelha a estrutura real do TFS/Azure DevOps. Qualquer mudança na hierarquia do TFS deve ser replicada aqui e em [`~/.claude/skills/tfs/SKILL.md`](../../../../../.claude/skills/tfs/SKILL.md) (seção "Hierarquia oficial TFS SETDIG").
