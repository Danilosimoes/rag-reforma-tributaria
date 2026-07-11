"""Construção, persistência e carregamento do índice FAISS."""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import settings
from src.rag.embeddings import criar_embeddings


def construir_e_salvar(chunks: list[Document]) -> None:
    """Cria o índice FAISS a partir dos chunks e persiste em DIR_FAISS_INDEX."""
    vectorstore = FAISS.from_documents(chunks, criar_embeddings())
    settings.DIR_FAISS_INDEX.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(settings.DIR_FAISS_INDEX))
    print(f"[vectorstore] {len(chunks)} vetores indexados em {settings.DIR_FAISS_INDEX}")


def carregar() -> FAISS:
    """Carrega o índice FAISS persistido em DIR_FAISS_INDEX.

    allow_dangerous_deserialization=True é obrigatório porque o FAISS salva
    o docstore como pickle, e o LangChain recusa desserializar pickle por
    padrão (risco de execução de código arbitrário vindo de um arquivo não
    confiável). Aqui é seguro: o índice é gerado pelo próprio projeto
    (scripts/ingest.py), nunca importado de terceiros.
    """
    if not settings.DIR_FAISS_INDEX.exists():
        raise RuntimeError(
            f"Índice FAISS não encontrado em {settings.DIR_FAISS_INDEX}. "
            "Rode 'python -m scripts.ingest' para criar o índice antes de usar o agente."
        )
    return FAISS.load_local(
        str(settings.DIR_FAISS_INDEX),
        criar_embeddings(),
        allow_dangerous_deserialization=True,
    )
