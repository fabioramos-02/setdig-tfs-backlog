# setdig-tfs-backlog — instruções do projeto

Repositório de **relatório semanal** individual (work items do Fabio). Guarda o CSV exportado da query do TFS, o resumo
em prosa de cada semana, e publica uma página única no GitHub Pages.

**Este repo não escreve no TFS.** Quem lança demanda é `../lancar-demandas-xvia`. Aqui só entra
o que já aconteceu, na forma de CSV exportado. Não misture os dois fluxos.

## O que o repo tem

| Caminho | O que é |
|---|---|
| `dados/AAAA-MM-DD.csv` | export bruto da query do TFS. Nunca editar à mão. |
| `relatorios/AAAA-MM-DD.md` | resumo em prosa da semana. Escrito ou gerado. |
| `build.py` | junta os dois e reescreve `index.html`. |
| `index.html` | **gerado** entre `/*DATA_START*/` e `/*DATA_END*/`. O resto do arquivo é template — pode editar. |

A data no nome é sempre a **sexta-feira** que fecha o recorte. O período exibido vai da segunda
àquela sexta. CSV e md de uma mesma semana têm o mesmo nome.

## Depois de mexer em dados/ ou relatorios/

```bash
python build.py
```

Sem isso a página não muda. O `build.py` aborta se os marcadores sumirem do `index.html`.

## Regras do relatório

- **Sem `Description` na query.** É HTML, infla o CSV e nada na página usa.
- **Sem filtro de `State` na query.** O recorte por estado é feito aqui, no `build.py`. Query que
  filtra `Done` esconde o pendente e o bloqueado — que é o que a reunião de segunda precisa ver.
- **PBI, Feature e Epic não viram linha.** Eles dão o agrupamento. Contar PBI como pendência infla
  o número sem dizer nada. O que aparece são Tasks e Bugs.
- **Bloqueio é a tag `bloqueio`** no work item. Não existe campo de impedimento no processo Scrum
  deste TFS. Sem a tag, a coluna nasce zerada.
- **O prefixo `[SGD] - ` é removido na exibição.** Todo item do time tem; repetir em cada linha é
  ruído.

## O resumo em prosa

Duas a seis linhas, no passado, dizendo o que andou. Estrutura que funciona:

```markdown
# Semana de DD/MM a DD/MM

Uma ou duas frases sobre o que andou de fato.

## Prioridades da semana (DD/MM a DD/MM)
1. **Frente** — o que fazer nesta semana. #id #id
2. ...

## Reuniões da semana
- **DD/MM — Assunto**, com quem. O que saiu dela. #id

## Destaques
- **Frente** — o que entregou, com número ou nome concreto.

## Aguardando terceiros
- **Quem** — o que está esperando, com número do chamado.

## Urgente do nosso time
O que trava outra coisa, e o que trava.
```

Não repita a lista de tasks: ela já está na página, logo abaixo. O resumo diz o que os números não
dizem.

## A página

Visual do MS Design System: tokens `--ds-*` embutidos no `<style>` do `index.html`, sem CSS
externo. A lista numerada logo abaixo de `## Prioridades...` vira cards numerados, e todo `#id` do
resumo vira link do TFS. Os dois efeitos vêm do JS da página, e o autor só escreve markdown.

Uma tela, uma rolagem: números, bloqueios em destaque, resumo, entregas por frente. Sem árvore,
sem painel de detalhe, sem filtro.

Grupo com item em aberto nasce aberto; grupo 100% finalizado nasce fechado. Dentro do grupo, mais
de cinco finalizados ficam recolhidos — lista longa de `Done` é scroll sem informação.

Os dados são embutidos no HTML, sem `fetch`. Isso mantém a página abrindo por duplo clique
(`file://`) e no Pages sem CORS. Se for adicionar dado novo, siga o mesmo caminho.

## Publicação

GitHub Pages, *deploy from a branch*: raiz de `master`. `git push origin master` republica.
**Não criar `.github/workflows` de Pages** — conflita com o modo legacy configurado no servidor.

## O que este repo não faz

- Não consulta a API do TFS. O export do CSV é manual, pela UI.
- Não edita work item, não muda estado, não comenta.
- Não guarda backlog paralelo. Isso era o propósito antigo e foi descontinuado em 04/09/2026.
