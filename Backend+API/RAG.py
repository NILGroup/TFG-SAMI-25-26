# pip install langchain langchain-community langchain-ollama langchain-chroma pymupdf beautifulsoup4 sentence-transformers rank_bm25 fastembed
import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from crearBD import crear_DB, DB_PATH, COLLECTION, EMBED_MODEL

RAG = None
reranker = None
#usar el modelo que quieras de Ollama, mirar cuales tienes instalado: ollama list, descargar nuevo ollama pull llama3.2
model = OllamaLLM(model="llama3.2")

def generar_queries(pregunta: str):

    prompt_multiquery = f"""
    Genera 4 reformulaciones diferentes de la siguiente pregunta
    para buscar información en una base de conocimiento.

    Pregunta: {pregunta}

    Devuelve solo las preguntas, una por línea.
    """

    respuesta = model.invoke(prompt_multiquery)

    queries = [q.strip() for q in respuesta.split("\n") if q.strip()]

    return [pregunta] + queries

def crear_RAG():
    global RAG

    #Se crea el modelo de embedings
    embed_model = FastEmbedEmbeddings(model_name=EMBED_MODEL)

    if not os.path.exists(DB_PATH):
        crear_DB()                           

    vector_store = Chroma(embedding_function=embed_model,
                          persist_directory=DB_PATH,
                          collection_name=COLLECTION)
    # K es el número de chunks que se añaden al contexto
    retriever = vector_store.as_retriever(search_kwargs={'k': 10})

    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    docs = vector_store.get()

    bm25_retriever = BM25Retriever.from_texts(
        docs["documents"]
    )

    bm25_retriever.k = 10

    def retrieve_and_rerank(pregunta: str):
        # Recupera los k candidatos iniciales
        #docs = retriever.invoke(pregunta)

        #vector_docs = retriever.invoke(pregunta)
        #bm25_docs = bm25_retriever.invoke(pregunta)

        #docs = vector_docs + bm25_docs

        queries = generar_queries(pregunta)

        docs = []

        for q in queries:
            docs.extend(retriever.invoke(q))

        # Deduplicacion por contenido
        docs = list({doc.page_content: doc for doc in docs}.values())

        # Puntúa cada par (pregunta, chunk)
        pares = [[pregunta, doc.page_content] for doc in docs]
        puntuaciones = reranker.predict(pares)

        # Ordena por puntuación descendente y quédate con los top 3
        docs_ordenados = sorted(
            zip(puntuaciones, docs),
            key=lambda x: x[0],
            reverse=True
        )
        top_docs = [doc for _, doc in docs_ordenados[:3]]

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
