#pip install langchain langchain-huggingface langchain-chroma chromadb sentence-transformers
import os
import csv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CSV_PATH = os.path.normpath(os.path.join(BASE_DIR, "Data", "Scrapping", "resultados_preprocesados.csv"))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "Data", "Chroma", "chroma_db"))
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"
COLLECTION = "TFG_SAMI"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 82

def crear_DB(csv_path : str = CSV_PATH):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el CSV en: {csv_path}, ejecuta primero preprocesamiento.py")

    csv.field_size_limit(10 * 1024 * 1024)  
    documents = []
    filas_omitidas = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:

            if row.get("valido", "True").strip().lower() != "true":
                filas_omitidas += 1
                continue
            #Se extrae el texto principal, titulo, h1, h2s y url de cada fila del csv
            texto_principal = row.get("texto_principal", "").strip()
            titulo = row.get("titulo", "").strip()
            h1 = row.get("h1", "").strip()
            h2s = row.get("h2s", "").strip()
            url = row.get("url", "").strip()

            # TITULOS_GENERICOS = {
            #     "Facultad de Educación - Centro de Formación del Profesorado.",
            # }
            # if titulo and titulo not in TITULOS_GENERICOS:
            #     texto_principal = f"{titulo}. {texto_principal}"
            # elif h2s and len(h2s.split()) <= 5:
            #     texto_principal = f"{h2s}. {texto_principal}"

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
                metadata={"url": url, "titulo": titulo, "h1": h1},
            ))

    
    if not documents:
        raise ValueError("No se encontraron documentos válidos en el CSV.")

    print(f"Documentos cargados   : {len(documents)}")
    print(f"Documentos omitidos   : {filas_omitidas}")

    # Se divide el documento en chunks respetando el limite de tokens del modelo de embeddings
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    docs = text_splitter.split_documents(documents)

    for doc in docs:
        aux_titulo = doc.metadata.get("titulo", "")
        aux_h1 = doc.metadata.get("h1", "")
        if aux_titulo or aux_h1:
            doc.page_content = f"[Fuente: {aux_titulo} | {aux_h1} ]\n\n" + doc.page_content

    os.makedirs(DB_PATH, exist_ok=True)

    print(f"Generando embeddings con: {EMBED_MODEL}")
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
    
    # Debug con las constantes reales del script
    client = chromadb.PersistentClient(path=DB_PATH)
    print(client.list_collections())

    col = client.get_collection(COLLECTION)  # "TFG_SAMI"
    print(f"Documentos en la colección: {col.count()}")