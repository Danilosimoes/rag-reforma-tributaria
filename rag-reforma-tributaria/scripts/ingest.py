"""Script de ingestão: carrega documentos locais + web, divide em chunks e
constrói o índice FAISS oficial em settings.DIR_FAISS_INDEX.

Só orquestra — toda a lógica de carregamento vive em src/ingestion/loaders.py
e a de indexação em src/rag/vectorstore.py.

Rode como módulo, a partir da raiz do projeto:
    python -m scripts.ingest
"""

from src.config import settings
from src.ingestion.loaders import carregar_tudo
from src.rag.vectorstore import construir_e_salvar


def main() -> None:
    chunks = carregar_tudo()

    urls_esperadas = set(settings.URLS_OFICIAIS_PARA_INDEXAR)
    urls_indexadas = {
        chunk.metadata["fonte"]
        for chunk in chunks
        if chunk.metadata.get("fonte") in urls_esperadas
    }
    urls_faltando = urls_esperadas - urls_indexadas

    settings.DIR_FAISS_INDEX.mkdir(parents=True, exist_ok=True)
    construir_e_salvar(chunks)

    print("\n" + "=" * 70)
    print("RESUMO DA INDEXAÇÃO")
    print("=" * 70)
    print(f"Total de chunks indexados: {len(chunks)}")
    print(f"Índice salvo em: {settings.DIR_FAISS_INDEX}")
    print("\nFontes web configuradas:")
    for url in settings.URLS_OFICIAIS_PARA_INDEXAR:
        status = "OK" if url in urls_indexadas else "FALHOU"
        print(f"  [{status}] {url}")

    if urls_faltando:
        print(
            "\n⚠️  AVISO: índice PARCIAL — as URLs marcadas como FALHOU acima "
            "não entraram. Rode 'python -m scripts.ingest' novamente para "
            "tentar reindexá-las."
        )
    else:
        print("\nTodas as fontes web configuradas foram indexadas com sucesso.")
    print("=" * 70)


if __name__ == "__main__":
    main()
