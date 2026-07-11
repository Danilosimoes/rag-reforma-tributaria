"""Configurações centrais do projeto: paths, modelo, chunking, URLs.

Config sensível (API key) vem de variável de ambiente. As demais têm
defaults aqui, sobrescrevíveis via .env. Sem Pydantic — validação é
um `if not x: raise` simples, chamada só quando o valor é de fato
necessário (ex.: na hora de instanciar o LLM), não na importação do módulo.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.config.urls_oficiais import URLS_OFICIAIS

load_dotenv()

# --- Caminhos ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIR_DOCUMENTOS = BASE_DIR / "data" / "documentos"
DIR_FAISS_INDEX = BASE_DIR / "data" / "faiss_index"

# --- LLM (Anthropic) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "2048"))

# --- Embeddings ---
# Multilíngue e zero-config com HuggingFaceEmbeddings (sem prefixos
# query:/passage: exigidos pelo e5). MiniLM em vez do mpnet-base: ~470MB
# em vez de ~1GB, bem mais leve para rodar localmente (evita pico de RAM
# no carregamento), com qualidade de recuperação muito próxima para PT-BR.
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# --- Retriever ---
TOP_K = int(os.getenv("TOP_K", "4"))

# --- Ingestão web ---
WEB_REQUEST_TIMEOUT_SEGUNDOS = int(os.getenv("WEB_REQUEST_TIMEOUT_SEGUNDOS", "15"))
URLS_OFICIAIS_PARA_INDEXAR = URLS_OFICIAIS


def validar_api_key() -> None:
    """Levanta erro claro se a API key não estiver configurada.

    Chamado só na hora de instanciar o LLM (rag/service.py), não na
    importação deste módulo — scripts de ingestão não precisam da key.
    """
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY não configurada. Copie .env.example para .env "
            "e preencha sua chave da Anthropic."
        )
