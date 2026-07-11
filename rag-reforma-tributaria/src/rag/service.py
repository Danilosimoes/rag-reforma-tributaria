"""RAGService: a única fronteira que src/app.py conhece. Encapsula toda a
chain LangChain (retriever + prompt + LLM) atrás de responder(pergunta).
LangChain é implementação interna — nunca vaza para fora desta classe.
"""

from langchain_anthropic import ChatAnthropic
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain

from src.config import settings
from src.models import Resposta
from src.prompt.templates import PROMPT_RAG
from src.rag import vectorstore


class RAGService:
    """Monta a chain RAG uma única vez (índice + retriever + LLM) e expõe
    responder(pergunta). Instanciar isto é caro (carrega o índice FAISS e
    o modelo de embeddings) — faça uma vez só, não a cada pergunta.
    """

    def __init__(self) -> None:
        # Log de inicialização: útil pra confirmar em produção (ex.: no
        # terminal do `streamlit run`) que o índice + modelo só carregam
        # uma vez, e não a cada pergunta.
        print("[RAGService] Inicializando (carregando índice FAISS e modelo)...")
        settings.validar_api_key()

        llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )
        retriever = vectorstore.carregar().as_retriever(
            search_kwargs={"k": settings.TOP_K}
        )
        combine_docs_chain = create_stuff_documents_chain(llm, PROMPT_RAG)
        self.chain = create_retrieval_chain(retriever, combine_docs_chain)
        print("[RAGService] Pronto.")

    def responder(self, pergunta: str) -> Resposta:
        resultado = self.chain.invoke({"input": pergunta})

        fontes: list[str] = []
        for doc in resultado["context"]:
            fonte = doc.metadata.get("fonte", "desconhecida")
            if fonte not in fontes:
                fontes.append(fonte)

        return Resposta(texto=resultado["answer"], fontes=fontes)
