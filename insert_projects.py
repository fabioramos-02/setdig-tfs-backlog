"""Insere work items dos projetos bench-carta, xvia, abep, prototipo, DS-MS."""
import openpyxl, os, subprocess, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, "backlog.xlsx")

NOVOS = [
    # csv_id, tipo, titulo, descricao, projeto_ado, csv_id_pai, prioridade, sprint, est_h, tags, ado_id
    (115, "Feature", "2.4 Migração EDS → XVia",
     "Documentação de governança para migração do ecossistema EDS (Control SSO, Admin, Atendimento, Integrador, FormFlow, CMS) para a plataforma XVia. Contrato de 180 dias de migração + 18 meses de operação. 36 serviços MS Digital a migrar + 10 novos autoatendimentos. 465.279+ usuários ativos.",
     "SETDIG", 100, 1, "", "", "xvia migracao-eds", ""),

    (116, "Product Backlog Item", "Documentação de governança módulo FormFlow",
     "Como PO, quero ter a documentação de governança do módulo FormFlow completa (visão funcional + documentacao-tecnica.md) para subsidiar o repasse à equipe XVia e reduzir risco operacional na transição. Módulos Control/Admin/Atendimento/Integrador/CMS já possuem doc oficial — FormFlow é o único pendente.",
     "SETDIG", 115, 1, "", 8, "xvia formflow documentacao", ""),

    (117, "Task", "Criar documentacao-tecnica.md do módulo FormFlow",
     "Ler Modulo FormFlow - v1.md e anexos em modulos/formflow/. Consultar manual EDS (https://manuais_ms.gitlab.io/forms/) via Playwright/Firecrawl. Preencher template modulos/TEMPLATE-MODULO.md com as 14+ seções técnicas (stack, fluxos, regras de negócio, integrações, gaps). Seguir padrão dos demais módulos oficiais.",
     "SETDIG", 116, 1, "", 6, "xvia formflow", ""),

    (118, "Task", "Revisar gaps Modulo FormFlow v1 com equipe XVia",
     "Identificar e documentar gaps na documentação atual do FormFlow (itens marcados como [a confirmar com EDS] ou 💡 [IA sugere]). Agendar validação com contato técnico EDS/XVia. Registrar veredito por gap no documento.",
     "SETDIG", 116, 1, "", 3, "xvia formflow gaps", ""),

    (119, "Product Backlog Item", "Validação e handoff dos documentos com fornecedor XVia",
     "Como PO, quero que todos os documentos de governança dos 6 módulos (Control, Admin, Atendimento, Integrador, FormFlow, CMS) sejam validados pelo novo fornecedor XVia antes do início formal da operação, garantindo entendimento compartilhado das regras de negócio.",
     "SETDIG", 115, 1, "", 12, "xvia handoff validacao", ""),

    (120, "Task", "Consolidar lista de gaps por módulo (todos os 6)",
     "Varrer os 6 documentos oficiais (modulos/*/Modulo *-v*.md) buscando ocorrências de '[a confirmar com EDS]', '💡 [IA sugere]' e seções incompletas. Gerar planilha de gaps: módulo | seção | gap | status | responsável.",
     "SETDIG", 119, 1, "", 4, "xvia gaps auditoria", ""),

    (121, "Task", "Agendar reunião de repasse técnico com equipe XVia",
     "Preparar pauta de repasse com base na lista de gaps (Task #120) e nos documentos oficiais. Contato técnico Integrador: miguel.alencar@extreme.digital. Incluir demo dos fluxos críticos: Control SSO (pré-requisito de todos), Integrador (webhook → API destino), FormFlow (formulários).",
     "SETDIG", 119, 1, "", 2, "xvia handoff reuniao", ""),

    (122, "Feature", "2.5 ABEPTIC 2026 — Avaliação IOSPD",
     "Participação do MS na avaliação do IOSPD (Índice de Oferta de Serviços Públicos Digitais) — ABEPTIC 2026. Envolve: convalidação das evidências por dimensão, defesa do relatório e submissão final. Referência: Relatório ABEP26.pdf + backlog_convalidacao_v3.csv em projetos/projeto-abep/.",
     "SETDIG", 100, 2, "", "", "abep iospd pesquisa", ""),

    (123, "Product Backlog Item", "Convalidação IOSPD 2026 — MS",
     "Como responsável técnico, quero ter todas as dimensões do IOSPD convalidadas com evidências suficientes (✅ ou ⚠️ documentado) para que o MS possa submeter o relatório final ao ABEP 2026 sem pendências críticas.",
     "SETDIG", 122, 2, "", 16, "abep iospd convalidacao", ""),

    (124, "Task", "Finalizar evidências Dimensão 1.1 para defesa",
     "Revisar Defesa_Dimensao_1.1.docx em projeto-abep/convalidacao/. Verificar qualificadores ⚠️ (parcial) e ❌ (não atendido) no RELATÓRIO DE CONVALIDAÇÃO - IOSPD 2026.csv. Buscar documentos complementares (decretos, portarias, PTD) para converter ⚠️ em ✅ onde possível.",
     "SETDIG", 123, 2, "", 4, "abep dimensao-1.1 evidencias", ""),

    (125, "Task", "Revisar backlog_convalidacao_v3.csv e fechar gaps abertos",
     "Abrir backlog_convalidacao_v3.csv, filtrar linhas com status ⚠️ e ❌. Para cada gap: identificar evidência faltante, buscar no site oficial do governo MS ou em decretos/portarias. Usar prompt avalia-pergunta.md para avaliação automatizada via Claude Code.",
     "SETDIG", 123, 2, "", 6, "abep convalidacao gaps", ""),

    (126, "Task", "Submeter relatório final IOSPD ao ABEP 2026",
     "Consolidar Relatorio_Convalidacao_MS.html com versão final aprovada. Verificar prazo de submissão ABEPTIC 2026. Exportar evidências no formato exigido. Submeter via canal oficial ABEP.",
     "SETDIG", 123, 2, "", 2, "abep submissao relatorio", ""),

    (127, "Product Backlog Item", "Estudo de Uso do Filtro de Perfil — bench-carta",
     "Estudo concluído (base 2025): recomendação REMOVER os filtros de Órgão e Perfil do Portal Único. Taxa de uso real do filtro estimada em ~0,091% dos visitantes da home — abaixo do limiar de 2%. Aba Servidor Público: 366 acessos/ano. PBI cobre comunicação e desdobramentos da recomendação.",
     "SETDIG", 101, 2, "", 6, "bench-carta filtro-perfil analytics", ""),

    (128, "Task", "Elaborar apresentação gerencial da recomendação REMOVER",
     "Preparar apresentação para a gestora (Duda/SGD) com base no relatório docs/estudo-uso-filtro-perfil.md. Incluir: funil de 3 etapas (home → serviço → filtro), KPIs em linguagem simples, comparativo proxy ingênuo (6,05%) vs taxa corrigida (0,091%), recomendação clara REMOVER com justificativa.",
     "SETDIG", 127, 2, "", 3, "bench-carta apresentacao gestao", ""),

    (129, "Task", "Documentar limitação de event tracking e propor instrumentação",
     "Registrar formalmente a limitação identificada na Fase 1: troca de aba no filtro de Perfil é DOM swap puro — invisível ao Matomo. Redigir proposta de event tracking (ex: dataLayer push ou Custom Dimension Matomo) para medição exata em versão futura. Salvar em docs/ do repo bench-carta.",
     "SETDIG", 127, 3, "", 2, "bench-carta event-tracking matomo", ""),

    (130, "Product Backlog Item", "Prototipagem Seção Categorias Portal MS",
     "Como PO, quero ter o protótipo da nova seção de categorias do Portal MS validado com as partes interessadas para decidir se avança para implementação. Protótipo React/Vite disponível em projetos/prototipo-categorias-ms/ com responsividade testada (desktop 1280, tablet 639/640, mobile 390).",
     "SETDIG", 101, 2, "", 5, "prototipo categorias portal-ms", ""),

    (131, "Task", "Apresentar protótipo de categorias para validação com partes interessadas",
     "Executar o protótipo localmente (npm run dev em prototipo-categorias-ms/). Agendar sessão de validação com SGD/SETDIG. Demonstrar variações responsivas (desktop, tablet, mobile) e o comportamento de expansão de categoria (verify-category-expanded.png). Coletar feedback estruturado.",
     "SETDIG", 130, 2, "", 2, "prototipo validacao apresentacao", ""),

    (132, "Task", "Registrar feedback e definir próximos passos do protótipo",
     "Após sessão de validação (Task #131): documentar feedback por stakeholder, classificar em: implementar como está / revisar design / descartar. Se aprovado: abrir issue no repositório do Portal Único para implementação. Registrar decisão no Diário de Decisões (skill /decisao).",
     "SETDIG", 130, 2, "", 2, "prototipo feedback decisao", ""),

    (133, "Product Backlog Item", "Levantamento Material Design System MS (DS-MS)",
     "Levantamento do material existente do Design System do Governo de MS (DS-MS). Artefatos coletados: tokens de cores e tipografia (colors_and_type.css), componentes (components.css), UI kits e assets visuais. Objetivo: ter referência centralizada para uso nos projetos SETDIG.",
     "SETDIG", 101, 3, "", 4, "ds-ms design-system", ""),

    (134, "Task", "Publicar catálogo DS-MS no vault Obsidian e wiki TFS",
     "Organizar artefatos de projetos/DS-MS Design System/ (colors_and_type.css, components.css, ui_kits/, assets/) em nota estruturada no vault Obsidian (10-conhecimento/setdig/ ou equivalente). Incluir: paleta de cores, tipografia, componentes disponíveis e link para o repositório.",
     "SETDIG", 133, 3, "", 3, "ds-ms obsidian catalogo", ""),
]

wb = openpyxl.load_workbook(XLSX)
ws = wb["Backlog"]

for row in NOVOS:
    ws.append(list(row))

tmp = XLSX + ".tmp"
wb.save(tmp)
try:
    shutil.move(tmp, XLSX)
    print(f"[OK] {len(NOVOS)} itens inseridos em backlog.xlsx")
except PermissionError:
    alt = os.path.join(BASE, "backlog_updated.xlsx")
    shutil.move(tmp, alt)
    print(f"[AVISO] xlsx bloqueado → salvo em backlog_updated.xlsx")
    print("        Feche o Excel, delete backlog.xlsx, renomeie backlog_updated.xlsx")
    import sys; sys.exit(0)

subprocess.run(["python", os.path.join(BASE, "xlsx_to_json.py")], check=True)
print("[OK] HTML e JSON regenerados.")
