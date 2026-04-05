# pip install langchain langchain-community langchain-ollama langchain-chroma pymupdf beautifulsoup4 sentence-transformers rank_bm25 langchain-huggingface transformers loguru
import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from crearBD import crear_DB, DB_PATH, COLLECTION, EMBED_MODEL
from loguru import logger
import time
import numpy as np

logger.add("logs/rag.log", rotation="10 MB", retention="7 days", level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

RAG = None
reranker = None
#usar el modelo que quieras de Ollama, mirar cuales tienes instalado: ollama list, descargar nuevo ollama pull llama3.2
model = OllamaLLM(model="qwen3.5")

def generar_queries(pregunta: str):
    logger.debug(f"Generando queries adicionales para: '{pregunta}'")
    t0 = time.time()

    prompt_multiquery = f"""
    Genera 3 reformulaciones diferentes de la siguiente pregunta
    para buscar información en una base de conocimiento.
    Mantén los términos específicos como nombres de grados, facultades y universidades.

    Pregunta: {pregunta}

    Devuelve solo las preguntas en español, una por línea. No hagas ninguna linea introductoria.
    """

    respuesta = model.invoke(prompt_multiquery)

    queries = [q.strip() for q in respuesta.split("\n") if q.strip()]
    queries = [q for q in queries if q.endswith("?")]
    todas = [pregunta] + queries
 
    elapsed = time.time() - t0
    queries_formateadas = "\n".join(f"    [{i+1}] {q}" for i, q in enumerate(todas))
    logger.debug(
        f"Queries generadas en {elapsed:.2f}s ({len(todas)} en total):\n{queries_formateadas}"
    )
    return todas

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

    reranker = CrossEncoder("amberoad/bert-multilingual-passage-reranking-msmarco")

    #docs = vector_store.get()

    #bm25_retriever = BM25Retriever.from_texts(
    #    docs["documents"]
    #)

    #bm25_retriever.k = 10

    def retrieve_and_rerank(pregunta: str):
        # Recupera los k candidatos iniciales
        #docs = retriever.invoke(pregunta)

        #vector_docs = retriever.invoke(pregunta)
        #bm25_docs = bm25_retriever.invoke(pregunta)

        #docs = vector_docs + bm25_docs

        logger.debug(f"[Retrieve & Rerank] Pregunta recibida: '{pregunta}'")
        t_total = time.time()

        queries = generar_queries(pregunta)

        docs = []

        logger.debug(f"Lanzando {len(queries)} búsquedas vectoriales...")
        t_retrieval = time.time()
        for i, q in enumerate(queries):
            resultados = retriever.invoke(q)
            logger.debug(f"  Query [{i+1}/{len(queries)}]: '{q[:60]}' → {len(resultados)} docs recuperados")
            docs.extend(resultados)

        # Deduplicacion por contenido
        docs_unicos = list({doc.page_content: doc for doc in docs}.values())
        logger.debug(f"Docs tras deduplicación: {len(docs_unicos)} (de {len(docs)} totales) — {time.time() - t_retrieval:.2f}s")

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

        # Loguea TODOS los fragmentos con su puntuación
        fragmentos_log = []
        for i, (puntuacion, doc) in enumerate(docs_ordenados):  # <-- desempaquetar la tupla
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
