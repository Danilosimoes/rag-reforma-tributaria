"""Serviço de embeddings usado tanto na indexação quanto na busca."""

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import settings


def criar_embeddings() -> HuggingFaceEmbeddings:
    """Cria o modelo de embeddings configurado em settings.EMBEDDING_MODEL_NAME.

    normalize_embeddings=True deixa os vetores em norma unitária. O índice
    FAISS usado em vectorstore.py é IndexFlatL2 (distância euclidiana, o
    padrão do LangChain quando nenhuma distance_strategy é passada) — não
    produto interno. Mas para vetores normalizados, ordenar por distância
    L2 é matematicamente equivalente a ordenar por similaridade de cosseno,
    então o resultado da busca é o mesmo de um índice de cosseno/IP.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
