"""Lista configurável de URLs oficiais usadas na ingestão via web.

Mantida separada de settings.py (que a importa) por ser uma lista de dados
que tende a crescer e ser editada com frequência, sem mexer em config de
infraestrutura. Cada entrada é uma URL de página oficial (Planalto, gov.br)
sobre a Reforma Tributária, carregada por src/ingestion/loaders.py.
"""

URLS_OFICIAIS = [
    # LC 214/2025 — texto integral (institui IBS, CBS e IS). Documento central.
    "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm",
    # Ministério da Fazenda — página oficial da Reforma Tributária / regulamentação
    "https://www.gov.br/fazenda/pt-br/acesso-a-informacao/acoes-e-programas/reforma-tributaria",
    # (opcional) LC 227/2026 — altera a LC 214 (Comitê Gestor do IBS/CBS)
    "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp227.htm",
    # Decreto 12.955/2026 — REGULAMENTO da CBS (620 artigos): split payment, créditos,
    # documentos fiscais, alíquotas. Traz normas comuns ao IBS.
    "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/decreto/d12955.htm",
    # Receita Federal — Orientações 2026: novos modelos de documento fiscal (NF-ABI, NFAg,
    # DeRE) e quais DF-e passam a destacar IBS/CBS.
    "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/reforma-consumo/orientacoes-2026",
]