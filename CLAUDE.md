# setdig-tfs-backlog — Convenções do projeto

## Título de PBI (obrigatório)

Formato:

```
[PROJETO] demanda - DD-MM-YYYY
```

Exemplo: `[X-VIA] Ajustes nos documentos - 23-06-2026`

- `[PROJETO]`: sigla/nome curto em maiúsculo entre colchetes (livre — ex.: `X-VIA`, `DS-MS`, `SETDIG`, `NOTIFICA`).
- `demanda`: substantivo + contexto, sem verbo imperativo.
- `DD-MM-YYYY`: data informada pelo usuário no momento da criação. Não inferir de `currentDate`; se ausente, perguntar.

Task / Feature / Epic / Bug mantêm regra livre.

## Template de descrição PBI (5 seções obrigatórias)

```
**História do usuário**
Como <papel>, quero <ação>, para <benefício>.

**Resumo**
<uma frase do que foi/será feito — vai pro relatório semanal>

**Local**
<path absoluto do repo/pasta de trabalho — ex.: C:\...\Projetos\xvia. Use "—" se reunião sem repo.>

**Requisitos**
- ...

**Critérios de Aceitação**
- ...
```

Resumo e Local são consumidos pelo `/tfs semana` para alimentar o relatório.

## Status (`status` no JSON)

Valores: `A fazer` | `Em progresso` | `Finalizado` | `Impedido`.

Para marcar Impedido:
```
/tfs status 152 = Impedido motivo: aguardando aprovacao
```
A skill anexa `**Impedimento**\n<motivo>` à descrição. Ao mudar para outro status, o bloco é removido automaticamente.

## Relatórios semanais

- Pasta: `relatorios/` (raiz do repo).
- Nome: `[YYYY-MM-DD]-relatorio-semanal.md` (data = dia da geração).
- Geração: `/tfs semana [N]` (default N = 7 dias).
- Render: `build.py` converte todos `relatorios/*.md` para HTML inline → `relatorios.html` (self-contained, sem fetch).
- Publicação: `https://fabioramos-02.github.io/setdig-tfs-backlog/relatorios.html`.
- Acesso no viewer: botão "Relatórios" no header do `backlog_viewer.html`.

## Fluxo após editar `backlog.json`

1. `python build.py` → regenera `backlog_viewer.html` e `relatorios.html`, carimba `generated_at`.
2. `git add backlog.json backlog_viewer.html relatorios.html relatorios/`.
3. Commit semântico:
   - PBI/Task/Feature/Bug: `feat(backlog): adiciona <Tipo> <csv_id> — <titulo curto>`
   - Status: `fix(backlog): status <id> → <novo>`
   - Relatório: `feat(relatorio): semanal YYYY-MM-DD (N PBIs)`
4. `git push origin master` (Pages redeploya em ~1 min).

A skill `/tfs` automatiza tudo isso. Edição manual deve seguir o mesmo fluxo.

## Dependências

- Python 3.10+
- `markdown>=3.5` (PyPI) — usado pelo `build.py` para renderizar `relatorios/*.md` em HTML. Ver `requirements.txt`.

## Referências

- Skill global: `~/.claude/skills/tfs/SKILL.md`.
- Memória do projeto: `~/.claude/projects/.../memory/project_tfs_backlog.md`.
- Padrão TFS oficial: `docs/TFS.pdf` (v1 jul/2024).
