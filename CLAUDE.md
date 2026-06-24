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

**Motivo:** o subcomando `/tfs semana` parseia a data do próprio título para listar o que foi feito na semana, agrupado por `[PROJETO]`, e usar como roteiro de fala na reunião de planejamento.

Task / Feature / Epic / Bug mantêm regra livre (título objetivo, sem formato fixo).

## Fluxo após editar `backlog.json`

1. `python build.py` (injeta DATA no `backlog_viewer.html` e carimba `generated_at`)
2. `git add backlog.json backlog_viewer.html`
3. Commit semântico: `feat(backlog): adiciona PBI <csv_id> — <titulo curto>`
4. `git push` (GitHub Pages redeploya em ~1 min)

A skill `/tfs` automatiza tudo isso. Edição manual deve seguir o mesmo fluxo.

## Subcomando `/tfs semana [N]`

Read-only. Lista PBIs do tipo `Product Backlog Item` cujo título casa o regex
`^\[([^\]]+)\]\s+(.+?)\s+-\s+(\d{2}-\d{2}-\d{4})$` e cuja data está dentro
dos últimos N dias (default 7). PBIs legados pré-convenção são ignorados
silenciosamente.

## Referências

- Skill global: `~/.claude/skills/tfs/SKILL.md` (regras de inferência, hierarquia TFS, padrões de descrição por tipo).
- Memória do projeto: `~/.claude/projects/.../memory/project_tfs_backlog.md`.
