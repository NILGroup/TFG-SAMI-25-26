import os
import csv
import re
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

CSV_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Scrapping", "resultados_scrapping.csv"))
DB_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "Scrapping", "chroma_db"))
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"
COLLECTION = "TFG_prueba"

def limpiar_texto(texto: str) -> str:
    # Eliminar caracteres no imprimibles
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ¿¡.,;:()\-\n]', ' ', texto) 
    # Colapsar espacios y saltos de linea múltiples
    texto = re.sub(r' {2,}', ' ', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()
 

def crear_DB(csv_path : str = CSV_PATH):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV en: {csv_path}")

    csv.field_size_limit(10 * 1024 * 1024)  
    documents = []
    filas_omitidas = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texto_principal = limpiar_texto(row.get("texto_principal", ""))
            titulo = limpiar_texto(row.get("titulo", ""))
            h1 = limpiar_texto(row.get("h1", ""))
            h2s = limpiar_texto(row.get("h2s", ""))
            url = row.get("url", "").strip()

            if len(texto_principal) < 30:
                filas_omitidas += 1
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
                page_content="\n\n".join(partes),
                metadata={"url": url, "titulo":titulo, "h1":h1},
            ))
    
    if not documents:
        raise ValueError("No se encontraron documentos válidos en el CSV.")

    # se divide el documento en chunks de tamaño 1000 y teniendo en común las últimas 300 palabras de uno con
    # las primeras del siguiente
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3500, chunk_overlap=600)
    docs = text_splitter.split_documents(documents)

    for doc in docs:
        titulo = doc.metadata.get("titulo", "")
        h1 = doc.metadata.get("h1", "")
        if titulo or h1:
            doc.page_content = f"[Fuente: {titulo} | {h1}]\n\n" + doc.page_content

    os.makedirs(DB_PATH, exist_ok=True)

    embed_model = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    encode_kwargs={"normalize_embeddings": True}
    )

    Chroma.from_documents(
        documents=docs,
        embedding=embed_model,
        persist_directory=DB_PATH,
        collection_name=COLLECTION
    )
    print(f"Base de datos creada en: {DB_PATH}")

if __name__ == "__main__":
    print(f"CSV de entrada : {CSV_PATH}")
    print(f"Base de datos  : {DB_PATH}")
    crear_DB()