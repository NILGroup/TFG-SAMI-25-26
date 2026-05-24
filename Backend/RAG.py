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
#usar el modelo que quieras de Ollama, mirar cuales tienes instalado: ollama list, descargar nuevo ollama pull qwen3.5
model = OllamaLLM(model="ministral-3:8b")

def generar_queries(pregunta: str):
    logger.debug(f"Generando queries adicionales para: '{pregunta}'")
    t0 = time.time()

    prompt_multiquery = f"""
    Eres SAMI, el asistente virtual de la Facultad de Educación de la Universidad Complutense de Madrid, cuyas siglas significan Sistema Accesible para la Mejora de la 
    Inclusividad, diseñada para ayudar a los estudiantes del programa ACCEDE y al resto del alumnado a resolver dudas sobre la vida universitaria.
    Genera 3 reformulaciones diferentes de la siguiente pregunta para buscar información en una base de conocimiento.
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

    SYSTEM_PROMPT = """Eres SAMI, el asistente virtual de la Facultad de Educación de la Universidad Complutense de Madrid, cuyas siglas significan Sistema Accesible para la Mejora de la Inclusividad, diseñada para ayudar a los estudiantes del programa ACCEDE y al resto del alumnado a resolver dudas sobre la vida universitaria.
    
    COMPORTAMIENTO: 
    - Responde únicamente con la información contenida en el contexto proporcionado.
    - Si el contexto no contiene información suficiente para responder con seguridad, responde exactamente lo siguiente: "No tengo suficiente información para resolver tu duda. Te recomiendo consultar directamente en la Facultad de Educación o visitar educacion.ucm.es para más detalles."
    - Nunca inventes datos, fechas, nombres, teléfonos, correos electrónicos ni URLs.
    - Nunca hagas referencia a conocimientos generales fuera del contexto dado.
    
    ESTILO DE LA RESPUESTA:
    - Usa un tono cercano, amable, claro y directo.
    - Estructura la respuesta de forma lógica: primero lo importante.
    - Si la respuesta implica un procedimiento, al final de la respuesta indica que el usuario puede pedir un resumen paso a paso en el botón "Respuesta por pasos".
    - Si la respuesta es una información puntual, responde en uno o dos párrafos claros y concisos.
    - No añadas introducciones innecesarias ni frases de cortesía al inicio o al final de la respuesta.
    
    EJEMPLOS:
    ---
    Pregunta: ¿Dónde se encuentra la Facultad de Educación?
    Respuesta: La Facultad de Educación de la Universidad Complutense de Madrid se encuentra en el Campus de La Moncloa, entre las calles Rector Royo-Villanova y Camino de las Moreras.
    
    ---
    Pregunta: ¿Cómo puedo sacar un libro de la biblioteca?
    Respuesta: Para sacar un libro de la biblioteca de la Facultad de Educación, primero tienes que ser un alumno matriculado en la UCM. Luego, puedes acudir a la biblioteca con tu tarjeta de estudiante y escoger el libro que quieres sacar. En el mostrador de préstamos, el personal de la biblioteca te ayudará a registrar el préstamos del libro y te indicará la fecha de devolución. Recuerda que también puedes consultar el catálogo online de la biblioteca para ver la disponibilidad de los libros. Si quieres un resumen paso a paso del proceso, puedes pedirlo en el botón "Respuesta por pasos".
    ---"""

    USER_TEMPLATE = """
    
    Categoría:
    {categoria}

    Contexto:
    {context}

    Pregunta:
    {question}
    
    Respuesta:"""

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_TEMPLATE)
    ])

    RAG = (
        {
            "question": lambda x: x["pregunta"],
            "context": lambda x: retrieve_and_rerank(x["pregunta"]),  # ← extrae del dict
            "categoria": lambda x: x["categoria"],
        }
        | prompt_template
        | model
    )


def pregunta_a_RAG(pregunta: str, categoria: str):
    return RAG.invoke({"pregunta": pregunta, "categoria": categoria})