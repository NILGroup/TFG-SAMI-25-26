# pip install langchain langchain-community langchain-ollama langchain-chroma pymupdf beautifulsoup4 sentence-transformers rank_bm25 langchain-huggingface transformers loguru
import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from loguru import logger
import time
import numpy as np
from Pipeline.crear_DB import crear_DB, DB_PATH, COLLECTION, EMBED_MODEL


logger.add("logs/rag.log", rotation="10 MB", retention="7 days", level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

RAG = None
reranker = None
#usar el modelo que quieras de Ollama, mirar cuales tienes instalado: ollama list, descargar nuevo ollama pull llama3.2
model = OllamaLLM(model="qwen3.5")

def get_all_documents_in_batches(collection, batch_size=5000):
    all_documents = []
    all_metadatas = []
    offset = 0
    while True:
        batch = collection.get(
            include=["documents", "metadatas"],
            limit=batch_size,
            offset=offset
        )
        if not batch["documents"]:
            break
        all_documents.extend(batch["documents"])
        all_metadatas.extend(batch["metadatas"])
        offset += batch_size
    return all_documents, all_metadatas

def crear_RAG():
    global RAG

    #Se crea el modelo de embedings
    embed_model = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )

    if not os.path.exists(DB_PATH):
        crear_DB()                           

    vector_store = Chroma(embedding_function=embed_model,
                          persist_directory=DB_PATH,
                          collection_name=COLLECTION)
    # K es el número de chunks que se añaden al contexto
    retriever = vector_store.as_retriever(search_kwargs={'k': 10})

    reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")

    all_docs, all_metas = get_all_documents_in_batches(vector_store._collection)
    bm25_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(all_docs, all_metas)
    ]
    bm25_retriever = BM25Retriever.from_documents(bm25_docs)

    bm25_retriever.k = 10

    def retrieve_and_rerank(pregunta: str):
        logger.debug(f"[Retrieve & Rerank] Pregunta recibida: '{pregunta}'")
        t_total = time.time()

        # Hybrid retrieval: vectorial + BM25
        t_retrieval = time.time()
        vector_docs = retriever.invoke(pregunta)
        bm25_docs = bm25_retriever.invoke(pregunta)
        docs = vector_docs + bm25_docs
        logger.debug(
            f"Docs recuperados — vectorial: {len(vector_docs)}, BM25: {len(bm25_docs)} "
            f"— {time.time() - t_retrieval:.2f}s"
        )

        # Deduplicacion por contenido
        docs_unicos = list({doc.page_content: doc for doc in docs}.values())
        logger.debug(f"Docs tras deduplicación: {len(docs_unicos)} (de {len(docs)} totales)")

        # Puntúa cada par (pregunta, chunk)
        t_rerank = time.time()
        pares = [[pregunta, doc.page_content] for doc in docs_unicos]
        
        puntuaciones = reranker.predict(pares)
        puntuaciones = np.array(puntuaciones).flatten().tolist()

        # Ordena por puntuación descendente y se queda con los top 5
        docs_ordenados = sorted(
            zip(puntuaciones, docs_unicos),
            key=lambda x: x[0],
            reverse=True
        )

        for i, (puntuacion, doc) in enumerate(docs_ordenados[:7]):
            logger.debug(
            f"--- Fragmento #{i+1} (score: {puntuacion:.4f}) ---\n"
            f"{doc.page_content}\n"
            f"{'='*60}"
        )

        # Loguea TODOS los fragmentos con su puntuación
        fragmentos_log = []
        for i, (puntuacion, doc) in enumerate(docs_ordenados):
            url = doc.metadata.get('url', 'desconocida')
            titulo = doc.metadata.get('titulo', '')
            texto_preview = doc.page_content.replace("\n", " ").strip()[:200]  # limitar a 200 chars
            fragmentos_log.append(
                f"   Fragmento #{i+1}\n"
                f"     URL:    {url}\n"
                f"     Titulo: {titulo}\n"
                f"     Texto:  {texto_preview}"
            )

        logger.debug(f"Todos los fragmentos ordenados ({len(docs_ordenados)}):\n" + "\n".join(fragmentos_log))

        top_docs = [doc for _, doc in docs_ordenados[:5]]
        logger.debug(f"Reranking completado en {time.time() - t_rerank:.2f}s")

        fragmentos_log = []
        for i, doc in enumerate(top_docs):
            url = doc.metadata.get('url', 'desconocida')
            titulo = doc.metadata.get('titulo', '')
            texto_preview = doc.page_content.replace("\n", " ").strip()
            fragmentos_log.append(
                f"   Fragmento #{i+1}\n"
                f"     URL:    {url}\n"
                f"     Titulo: {titulo}\n"
                f"     Texto:  {texto_preview}"
            )
 
        logger.debug("Top 5 fragmentos recuperados:\n" + "\n".join(fragmentos_log))
 
        logger.debug(f"Retrieve & Rerank completado en {time.time() - t_total:.2f}s total")
        return top_docs

    prompt_template = ChatPromptTemplate.from_template("""Responde a la pregunta usando el contexto dado.

    Contexto:
    {context}

    Pregunta:
    {question}
    """)

    RAG = (
        {
            "question": lambda x: str(x),
            "context": retrieve_and_rerank
        }
        | prompt_template
        | model
    )


def pregunta_a_RAG(pregunta: str):
    return RAG.invoke(pregunta)