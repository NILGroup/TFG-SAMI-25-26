import os
import csv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

CSV_PATH    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados_scrapping.csv")
DB_PATH = os.path.join(os.path.expanduser("~"), ".sami_db", "chroma_db")
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION = "TFG_prueba"

def crear_DB(csv_path : str = CSV_PATH):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV en: {csv_path}")

    documents = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texto_principal = row.get("texto_principal", "").strip()
            titulo = row.get("titulo", "").strip()
            h1 = row.get("h1", "").strip()
            h2s = row.get("h2s", "").strip()
            url = row.get("url", "").strip()

            if len(texto_principal) < 30:
                continue

            partes = []
            if titulo:
                partes.append(f"Titulo: {titulo}")
            if h1:
                partes.append(f"H1: {h1}")
            if h2s:
                partes.append(f"H2s: {h2s}")
            partes.append(texto_principal)

            documents.append(Document(
                page_conent="\n\n".join(partes),
                metadata={"url": url, "titulo":titulo, "h1":h1},
            ))
    
    if not documents:
        raise ValueError("No se encontraron documentos válidos en el CSV.")

    # se divide el documento en chunks de tamaño 1000 y teniendo en común las últimas 300 palabras de uno con
    # las primeras del siguiente
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    docs = text_splitter.split_documents(documents)

    os.makedirs(DB_PATH, exist_ok=True)
    embed_model = FastEmbedEmbeddings(model_name=EMBED_MODEL)

    Chroma.from_documents(
        documents=docs,
        embedding=embed_model,
        persist_directory=DB_PATH,
        collection_name=COLLECTION
    )
