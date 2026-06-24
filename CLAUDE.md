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

**URLs**           ← opcional (omitir se não houver)
- https://app.vercel.app
- https://fabioramos-02.github.io/projeto/

**Requisitos**
- ...

**Critérios de Aceitação**
- ...
```

Bloco **URLs** é opcional. Skill `/tfs` **sempre pergunta** ao criar PBI/Task ("Tem URLs de publicação?"). Quando presentes, viram links clicáveis no relatório semanal.

Resumo e Local são consumidos pelo `/tfs semana` para alimentar o relatório.

**Tasks filhas:** após criar um PBI, sempre oferecer geração automática de uma Task por item de Requisito (1:1). Sem isso o PBI fica sem rastreio de execução.

## Design System e arquitetura de assets

Tudo consome `assets/ds-sis.css` (cópia do `@design-system-ms/ds-sis`). Sem hardcode de cor — usar tokens (`--color-primary-500`, `--color-neutral-*`, etc.). Atualizar lib: `cd /tmp && npm pack @design-system-ms/ds-sis@<v>` → copiar `dist/css/ds-sis.css` para `assets/`.

Layout do `assets/`:
- `assets/ds-sis.css` — biblioteca DS-MS (tokens + componentes)
- `assets/css/viewer.css` — estilos específicos do backlog viewer
- `assets/css/relatorios.css` — estilos específicos dos relatórios
- `assets/js/data.js` — gerado, contém `window.BACKLOG_DATA`
- `assets/js/viewer.js` — lógica do viewer (lê `window.BACKLOG_DATA`)

`backlog_viewer.html` é shell (~57 linhas) — sem `<style>` ou `<script>` inline. Tudo via `<link>` e `<script src>`. Funciona em `file://` (duplo-clique local) e no GitHub Pages.

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

1. `python build.py` → reescreve `assets/js/data.js` (DATA injetado entre marcadores) e regera `relatorios.html`; carimba `generated_at`.
2. `git add backlog.json assets/js/data.js relatorios.html relatorios/`.
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
