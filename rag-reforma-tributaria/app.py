"""Interface Streamlit do assistente contábil da Reforma Tributária.

Depende só de RAGService e Resposta — nenhuma referência a LangChain aqui,
mantendo a fronteira estabelecida em src/rag/service.py (DIP).

Rodar: streamlit run app.py
"""

import streamlit as st

from src.models import Resposta
from src.rag.service import RAGService

st.set_page_config(page_title="Assistente Contábil — Reforma Tributária")

st.title("Assistente Contábil — Reforma Tributária")
st.caption(
    "Tire dúvidas sobre IBS, CBS, Imposto Seletivo e o período de transição, "
    "com base em documentos oficiais."
)
st.info(
    "⚠️ Assistente informativo baseado em documentos oficiais da Reforma "
    "Tributária. Não substitui a orientação de um contador ou advogado "
    "tributarista habilitado. Confirme sempre com a legislação vigente e um "
    "profissional antes de tomar decisões."
)

PERGUNTA_MAX_CARACTERES = 2000


@st.cache_resource
def get_service() -> RAGService:
    """Instancia o RAGService uma única vez por sessão do servidor Streamlit.

    Sem o cache, o Streamlit reexecutaria este script inteiro a cada
    interação do usuário, recarregando o índice FAISS e o modelo de
    embeddings a cada pergunta.
    """
    return RAGService()


try:
    service = get_service()
except RuntimeError as erro:
    st.error(f"{erro}\n\nRode `python -m scripts.ingest` antes de iniciar o app.")
    st.stop()

pergunta = st.text_input("Sua pergunta:")
perguntar = st.button("Perguntar")

if perguntar:
    if not pergunta.strip():
        st.warning("Digite uma pergunta antes de clicar em Perguntar.")
    elif len(pergunta) > PERGUNTA_MAX_CARACTERES:
        st.warning(
            f"Pergunta muito longa (máximo de {PERGUNTA_MAX_CARACTERES} caracteres)."
        )
    else:
        with st.spinner("Consultando os documentos..."):
            try:
                resposta: Resposta = service.responder(pergunta)
            except Exception as erro:
                st.error(f"Erro ao consultar o modelo: {erro}")
            else:
                st.markdown(resposta.texto)
                st.subheader("Fontes")
                for fonte in resposta.fontes:
                    st.markdown(f"- {fonte}")
