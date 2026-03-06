#pip install langchain langchain-community langchain-ollama langchain-chroma pymupdf beautifulsoup4

import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from crearBD import crear_DB

RAG = None

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
    retriever = vector_store.as_retriever(search_kwargs={'k': 2})

    prompt_template = ChatPromptTemplate.from_template("""Responde a la pregunta usando el contexto dado.

    Contexto:
    {context}

    Pregunta:
    {question}
    """)

    RAG = (
        {
            "question": lambda x: str(x),
            "context": retriever.invoke
        }
        | prompt_template
        | model
    )


def pregunta_a_RAG(pregunta: str):
    return RAG.invoke(pregunta)
