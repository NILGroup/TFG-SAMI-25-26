#pip install langchain langchain-community langchain-ollama langchain-chroma pymupdf
import os.path

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.runnables.passthrough import RunnablePassthrough

RAG = None

def crear_RAG():
    global RAG
    #usar el modelo que quieras de Ollama, mirar cuales tienes instalado: ollama list, descargar nuevo ollama pull llama3.2
    model = OllamaLLM(model="llama3.2")

    # cargar el PDF
    loader = PyMuPDFLoader("./MemoriaSAMI.pdf")
    data_pdf = loader.load()

    # se divide el documento en chunks de tamaño 1000 y teniendo en común las últimas 300 palabras de uno con
    # las primeras del siguiente
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    docs = text_splitter.split_documents(data_pdf)


    #Se crea el modelo de embedings
    embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    if not os.path.exists("chroma_db"):
        vs = Chroma.from_documents(
            documents=docs,
            embedding=embed_model,
            persist_directory="chroma_db",
            collection_name="TFG_prueba"
        )

    vector_store = Chroma(embedding_function=embed_model,
                          persist_directory="chroma_db",
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
