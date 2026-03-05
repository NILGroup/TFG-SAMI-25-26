import os
import json
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma



def crear_DB():
    # cargar las urls (si se ha usado antes con pdf hacer Remove-Item -Recurse -Force chroma_db para quitar la bd con el pdf)
    ruta_urls = os.path.join(os.path.dirname(os.path.abspath(__file__)), "urls_completas_educacion_ucm.txt")
    with open(ruta_urls, "r", encoding="utf-8") as f:
        datos = json.load(f)
        urls = [item["url"] for item in datos]
    web_loader = WebBaseLoader(urls)
    data_web = web_loader.load()


    # se divide el documento en chunks de tamaño 1000 y teniendo en común las últimas 300 palabras de uno con
    # las primeras del siguiente
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    docs = text_splitter.split_documents(data_web)

    embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    Chroma.from_documents(
        documents=docs,
        embedding=embed_model,
        persist_directory="chroma_db",
        collection_name="TFG_prueba"
    )
