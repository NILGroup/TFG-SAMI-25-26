#pip install langchain langchain-community langchain-ollama langchain-chroma pymupdf beautifulsoup4 sentence-transformers

import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from crearBD import crear_DB

RAG = None
reranker = None

def crear_RAG():
    global RAG
    #usar el modelo que quieras de Ollama, mirar cuales tienes instalado: ollama list, descargar nuevo ollama pull llama3.2
    model = OllamaLLM(model="llama3.2")

    #Se crea el modelo de embedings
    embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    DB_PATH = os.path.join(os.path.expanduser("~"), ".sami_db", "chroma_db")
                           
    if not os.path.exists(DB_PATH):
        crear_DB()

    vector_store = Chroma(embedding_function=embed_model,
                          persist_directory=DB_PATH,
                          collection_name="TFG_prueba")
    # K es el número de chunks que se añaden al contexto
    retriever = vector_store.as_retriever(search_kwargs={'k': 10})

    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def retrieve_and_rerank(pregunta: str):
        # 1. Recupera los k candidatos iniciales
        docs = retriever.invoke(pregunta)

        # 2. Puntúa cada par (pregunta, chunk)
        pares = [[pregunta, doc.page_content] for doc in docs]
        puntuaciones = reranker.predict(pares)

        # 3. Ordena por puntuación descendente y quédate con los top 3
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
