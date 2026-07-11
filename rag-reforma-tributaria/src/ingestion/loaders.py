"""Carrega documentos das duas fontes de conhecimento (locais e web) e
os divide em chunks prontos para indexação.

Fase de ingestão pura: não toca em embeddings nem em FAISS (isso é
responsabilidade de src/rag/vectorstore.py, na Fase 3).
"""

import time

from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings

# Nº de tentativas por URL antes de desistir dela (algumas páginas .gov.br
# têm timeout intermitente, não é sempre a mesma requisição que falha).
TENTATIVAS_POR_URL = 3
SEGUNDOS_ENTRE_TENTATIVAS = 2

# Páginas do Planalto são servidas em ISO-8859-1, não UTF-8 — sem forçar o
# encoding, o texto sai corrompido (ex.: "cÃ¡lculo" em vez de "cálculo").
ENCODING_PLANALTO = "ISO-8859-1"

# WebBaseLoader usa por padrão o header "DefaultLangchainUserAgent" (e a lib
# requests usa "python-requests/..."). O planalto.gov.br não devolve resposta
# nenhuma para esses user agents — a conexão TLS abre, mas a requisição fica
# pendurada até o timeout. Um user agent de navegador resolve.
HEADERS_NAVEGADOR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def carregar_documentos_locais() -> list[Document]:
    """Lê todos os PDFs e TXTs de settings.DIR_DOCUMENTOS."""
    pasta = settings.DIR_DOCUMENTOS
    if not pasta.exists():
        print(f"[loaders] Pasta {pasta} não existe — nenhum documento local carregado.")
        return []

    documentos: list[Document] = []

    for caminho in sorted(pasta.glob("*.pdf")):
        docs = PyPDFLoader(str(caminho)).load()
        for doc in docs:
            doc.metadata["fonte"] = caminho.name
        documentos.extend(docs)

    for caminho in sorted(pasta.glob("*.txt")):
        docs = TextLoader(str(caminho), encoding="utf-8").load()
        for doc in docs:
            doc.metadata["fonte"] = caminho.name
        documentos.extend(docs)

    if not documentos:
        print(f"[loaders] Nenhum PDF/TXT encontrado em {pasta}.")

    return documentos


def carregar_documentos_web() -> list[Document]:
    """Carrega cada URL de settings.URLS_OFICIAIS_PARA_INDEXAR.

    Cada URL é carregada isoladamente, com retry (páginas .gov.br têm
    timeout intermitente). Se mesmo assim falhar após todas as tentativas,
    avisamos bem visível e seguimos com as demais URLs — nunca derrubamos
    a ingestão inteira nem geramos um índice incompleto silenciosamente.
    """
    documentos: list[Document] = []

    for url in settings.URLS_OFICIAIS_PARA_INDEXAR:
        encoding = ENCODING_PLANALTO if "planalto.gov.br" in url else None
        docs: list[Document] | None = None
        ultimo_erro: Exception | None = None

        for tentativa in range(1, TENTATIVAS_POR_URL + 1):
            try:
                loader = WebBaseLoader(
                    web_path=url,
                    encoding=encoding,
                    header_template=HEADERS_NAVEGADOR,
                    requests_kwargs={"timeout": settings.WEB_REQUEST_TIMEOUT_SEGUNDOS},
                )
                docs = loader.load()
                break
            except Exception as erro:
                ultimo_erro = erro
                if tentativa < TENTATIVAS_POR_URL:
                    print(
                        f"[loaders] Tentativa {tentativa}/{TENTATIVAS_POR_URL} "
                        f"falhou para {url} ({erro}). Tentando de novo..."
                    )
                    time.sleep(SEGUNDOS_ENTRE_TENTATIVAS)

        if docs is None:
            print(
                f"[loaders] ⚠️  AVISO: falha ao carregar {url} após "
                f"{TENTATIVAS_POR_URL} tentativas ({ultimo_erro}). "
                "Essa fonte NÃO entrará no índice."
            )
            continue

        for doc in docs:
            doc.metadata["fonte"] = url
        documentos.extend(docs)

    return documentos


def dividir_em_chunks(documentos: list[Document]) -> list[Document]:
    """Divide documentos em chunks, preservando os metadados originais."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    return splitter.split_documents(documentos)


def carregar_tudo() -> list[Document]:
    """Carrega locais + web e retorna os chunks finais, prontos para indexar."""
    locais = carregar_documentos_locais()
    web = carregar_documentos_web()
    chunks = dividir_em_chunks(locais + web)

    print(
        f"[loaders] {len(locais)} docs locais, {len(web)} docs web, "
        f"{len(chunks)} chunks no total."
    )
    return chunks


if __name__ == "__main__":
    chunks = carregar_tudo()

    chunk_web = next(
        (c for c in chunks if "planalto.gov.br" in c.metadata.get("fonte", "")), None
    )
    if chunk_web:
        print("\n--- Trecho de um chunk web (Planalto, LC 214) ---")
        print(chunk_web.page_content[:500])
        print("\nmetadata['fonte']:", chunk_web.metadata["fonte"])

    chunk_local = next(
        (c for c in chunks if c.metadata.get("fonte", "").endswith((".pdf", ".txt"))),
        None,
    )
    if chunk_local:
        print("\n--- metadata de um chunk local ---")
        print("metadata['fonte']:", chunk_local.metadata["fonte"])
    else:
        print("\n[loaders] Nenhum documento local em data/documentos/ para testar.")
