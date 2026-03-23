#pip install requests beautifulsoup4 pypdf
import json # libreria para leer el archivo obtenido en el crawling
import time # libreria para hacer pausas entre peticiones
import csv # libreria para guardar los resultados
import requests # libreria para hacer peticiones HTTP
from bs4 import BeautifulSoup # libreria para parsear el HTML de cada pagina
import pypdf # libreria para extraer texto de PDFs
import io # libreria para leer el PDF en memoria sin guardarlo en disco

FICHERO_URLS = "crawling_result.json"
FICHERO_URLS_PDFS = "crawling_pdfs.json"
FICHERO_SALIDA = "resultados_scrapping.csv"
PAUSA_SEGUNDOS = 1.5
MAX_URLS = 50 # Para probar funcionamiento de manera rapida, limitar a un numero (20 p.e.).

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

#Funcion para cargar las URLs desde el archivo JSON generado por el crawling
def cargar_urls(fichero):
    with open(fichero, "r", encoding = "utf-8") as f:
        datos = json.load(f)
    
    urls_unicas = list({item['url'] for item in datos})
    print(f"Total URLs únicas cargadas: {len(urls_unicas)}")
    return urls_unicas

def cargar_pdfs(fichero):
    try:
        with open(fichero, "r", encoding="utf-8") as f:
            datos = json.load(f)
        urls_unicas = list({item['url'] for item in datos})
        print(f"Total PDFs únicos cargados: {len(urls_unicas)}")
        return urls_unicas
    except FileNotFoundError:
        print("crawling_pdfs.json no encontrado, se omiten los PDFs.")
        return []
    
#Funcion para extraer el contenido de una pagina dada su URL
def extraer_contenido(url):
    try:
        respuesta = requests.get(url,headers= HEADERS,timeout=10)
        if respuesta.status_code != 200:
            print (f"Error: {respuesta.status_code} - {url}")
            return {
                "url": url,
                "estado": respuesta.status_code,
                "titulo": "",
                "contenido": "",
                "h1": "",
                "h2s": "",
                "texto_principal": ""
            }
        
        # A partir de aqui parseamos el HTML para extraer la informacion relevante
        soup = BeautifulSoup(respuesta.text, "html.parser")

        titulo = soup.find("title")
        titulo = titulo.get_text(strip=True) if titulo else ""

        meta_descripcion = soup.find("meta", attrs={"name": "description"})
        descripcion = meta_descripcion["content"].strip() if meta_descripcion and meta_descripcion.get("content") else ""

        h1 = soup.find("h1")
        h1 = h1.get_text(strip=True) if h1 else ""

        h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
        h2s_texto = " | ".join(h2s) #Se unen para guardar todos los h2 en una misma celda del CSV

        # Aqui extraemos el contenido principal de la pagina
        for tag in soup(["nav", "header", "footer","script","style"]):
            tag.decompose()# eliminamos elementos que no aportan informacion relevante
        
        contenedor = soup.find("main") or soup.find("div", class_="content") or soup.find("body")
        texto = contenedor.get_text(separator=" ", strip=True) if contenedor else ""

        print(f"Extraído: {url[:70]}")
        return {
            "url": url,
            "estado": 200,
            "titulo": titulo,
            "contenido": descripcion,
            "h1": h1,
            "h2s": h2s_texto,
            "texto_principal": texto
        }
    except requests.exceptions.Timeout:
        print(f"Timeout al acceder a: {url}")
        return {
            "url": url,
            "estado": "Timeout",
            "titulo": "",
            "contenido": "",
            "h1": "",
            "h2s": "",
            "texto_principal": ""
        }
    except requests.exceptions.ConnectionError:
        print(f"Error de conexión al acceder a: {url}")
        return {
            "url": url,
            "estado": "Connection Error",
            "titulo": "",
            "contenido": "",
            "h1": "",
            "h2s": "",
            "texto_principal": ""
        }
    except Exception as e:
        print(f"Error inesperado al acceder a: {url} - {str(e)}")
        return {
            "url": url,
            "estado": "Error inesperado",
            "titulo": "",
            "contenido": "",
            "h1": "",
            "h2s": "",
            "texto_principal": ""
        }
def extraer_contenido_pdf(url):
    try:
        respuesta = requests.get(url, headers=HEADERS, timeout=20)
        if respuesta.status_code != 200:
            print(f"Error: {respuesta.status_code} - {url}")
            return {
                "url": url,
                "estado": respuesta.status_code,
                "titulo": "",
                "contenido": "",
                "h1": "",
                "h2s": "",
                "texto_principal": ""
            }

        # Leer el PDF en memoria
        pdf = pypdf.PdfReader(io.BytesIO(respuesta.content))

        texto = " ".join(pagina.extract_text() or "" for pagina in pdf.pages)

        titulo = ""
        if pdf.metadata and pdf.metadata.title:
            titulo = pdf.metadata.title

        print(f"PDF Extraido: {url[:70]}")
        return {
            "url": url,
            "estado": 200,
            "titulo": titulo,
            "contenido": "PDF",
            "h1": "",
            "h2s": "",
            "texto_principal": texto
        }
    except Exception as e:
        print(f"Error inesperado al acceder al PDF: {url} - {str(e)}")
        return {
            "url": url,
            "estado": "Error inesperado",
            "titulo": "",
            "contenido": "",
            "h1": "",
            "h2s": "",
            "texto_principal": ""
        }

def guardar_resultados(resultados, fichero):
    columnas = ["url", "estado", "titulo", "contenido", "h1", "h2s", "texto_principal"]

    with open(fichero, "w", newline="", encoding="utf-8-sig")as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(resultados)

    print(f"Resultados guardados en: {fichero}")
        
if __name__ == "__main__":

    # Cargar URLs
    urls = cargar_urls(FICHERO_URLS)

    if MAX_URLS:
        urls = urls[:MAX_URLS]
        print(f"  → Modo prueba: procesando solo las primeras {MAX_URLS} URLs")

    urls_pdfs = cargar_pdfs(FICHERO_URLS_PDFS)
    if MAX_URLS:
        urls_pdfs = urls_pdfs[:MAX_URLS]
    total = len(urls)
    total_pdfs = len(urls_pdfs)
    print(f"\nIniciando scraping de {total} páginas + {total_pdfs} PDFs\n")

    resultados = []

    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{total}]", end=" ")

        # Extraemos el contenido de la url
        resultados.append(extraer_contenido(url))

        # Pausa para no saturar el servidor
        time.sleep(PAUSA_SEGUNDOS)

    for i, url in enumerate(urls_pdfs, start=1):
        print(f"[PDF {i}/{total_pdfs}]", end=" ")
        resultados.append(extraer_contenido_pdf(url))
        time.sleep(PAUSA_SEGUNDOS)

    # Guardamos todo en el CSV
    guardar_resultados(resultados, FICHERO_SALIDA)

    # Resumen final
    ok    = sum(1 for r in resultados if r["estado"] == 200)
    error = (total + total_pdfs) - ok
    print(f"\n{'='*40}")
    print(f"  Páginas OK:    {ok}")
    print(f"  Páginas error: {error}")
    print(f"  PDFs OK:       {total_pdfs}")
    print(f"  Total:         {total + total_pdfs}")
    print(f"{'='*40}")