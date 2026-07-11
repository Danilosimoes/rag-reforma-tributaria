"""Estruturas de dados do domínio. Enxuto: o LangChain já cobre as
abstrações de Document, Embeddings, VectorStore e Retriever — não
duplicamos isso aqui, só o que é específico da resposta do agente.
"""

from dataclasses import dataclass


@dataclass
class Resposta:
    """Resposta final do agente, com as fontes usadas para gerá-la."""

    texto: str
    fontes: list[str]
