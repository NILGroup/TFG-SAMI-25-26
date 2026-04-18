#pip install requests beautifulsoup4 pypdf
import json # libreria para leer el archivo obtenido en el crawling
import os #libreria para manejar rutas de archivos
import time # libreria para hacer pausas entre peticiones
import csv # libreria para guardar los resultados
import requests # libreria para hacer peticiones HTTP
from bs4 import BeautifulSoup # libreria para parsear el HTML de cada pagina
import pypdf # libreria para extraer texto de PDFs
import io # libreria para leer el PDF en memoria sin guardarlo en disco
from datetime import datetime, timezone # libreria para manejar fechas en formato ISO 8601
from urllib.parse import quote, urlsplit, urlunsplit  # para manejar URLs

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

DATA_CRAWLING = os.path.join(BASE_DIR, "Data", "Crawling")
DATA_SCRAPPING = os.path.join(BASE_DIR, "Data", "Scrapping")

FICHERO_URLS = os.path.join(DATA_CRAWLING,  "crawling_result.json")
FICHERO_URLS_PDFS = os.path.join(DATA_CRAWLING,  "crawling_pdfs.json")
FICHERO_SALIDA = os.path.join(DATA_SCRAPPING, "resultados_scrapping.csv")
PAUSA_SEGUNDOS = 1.5
MAX_URLS = None # Para probar funcionamiento de manera rapida, limitar a un numero (20 p.e.).

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def _ahora_iso8601() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _fila_error(url: str, tipo: str, estado) -> dict:
    return {
        "url":              url,
        "tipo_documento":   tipo,
        "estado_http":      estado,
        "fecha_extraccion": _ahora_iso8601(),
        "titulo":           "",
        "h1":               "",
        "h2s":              "",
        "texto_principal":  "",
    }

#Funcion para cargar las URLs desde el archivo JSON generado por el crawling
def cargar_urls(fichero: str) -> list:
    with open(fichero, "r", encoding="utf-8") as f:
        datos = json.load(f)
    urls = list({item["url"] for item in datos})
    print(f"Total URLs únicas cargadas: {len(urls)}")
    return urls

def cargar_pdfs(fichero: str) -> list:
    try:
        with open(fichero, "r", encoding="utf-8") as f:
            datos = json.load(f)
        urls = list({item["url"] for item in datos})
        print(f"Total PDFs únicos cargados: {len(urls)}")
        return urls
    except FileNotFoundError:
        print("crawling_pdfs.json no encontrado, se omiten los PDFs.")
        return []
    
#Funcion para extraer el contenido de una pagina dada su URL
def extraer_contenido(url: str) -> dict:
    fecha = _ahora_iso8601()
    try:
        respuesta = requests.get(url, headers=HEADERS, timeout=10)

        if respuesta.status_code != 200:
            print(f"  [HTTP {respuesta.status_code}] {url}")
            return _fila_error(url, "web", respuesta.status_code)

        soup = BeautifulSoup(respuesta.text, "html.parser")

        tag_titulo = soup.find("title")
        titulo = tag_titulo.get_text(strip=True) if tag_titulo else ""

        tag_h1 = soup.find("h1")
        h1 = tag_h1.get_text(strip=True) if tag_h1 else ""

        h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
        h2s_texto = " || ".join(h2s)

        for tag in soup(["nav", "header", "footer", "script", "style"]):
            tag.decompose()

        contenedor = (
            soup.find("main")
            or soup.find("div", class_="content")
            or soup.find("body")
        )
        texto = contenedor.get_text(separator=" ", strip=True) if contenedor else ""

        print(f"  [OK] {url[:80]}")

        return {
            "url":              url,
            "tipo_documento":   "web",
            "estado_http":      200,
            "fecha_extraccion": fecha,
            "titulo":           titulo,
            "h1":               h1,
            "h2s":              h2s_texto,
            "texto_principal":  texto,
        }

    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] {url}")
        return _fila_error(url, "web", "Timeout")

    except requests.exceptions.ConnectionError:
        print(f"  [CONNECTION ERROR] {url}")
        return _fila_error(url, "web", "Connection Error")

    except Exception as e:
        print(f"  [ERROR] {url} — {e}")
        return _fila_error(url, "web", "Error inesperado")
    
def extraer_contenido_pdf(url: str) -> dict:
    fecha = _ahora_iso8601()
    try:
        respuesta = requests.get(url, headers=HEADERS, timeout=20)

        content_type = respuesta.headers.get("Content-Type", "")
        content_disp = respuesta.headers.get("Content-Disposition", "")

        es_pdf = (
            "pdf" in content_type.lower()
            or ".pdf" in content_disp.lower()
            or url.lower().endswith(".pdf")
        )

        if not es_pdf:
            print(f"  [AVISO] Content-Type inesperado ({content_type}): {url[:70]}")

        if respuesta.status_code != 200:
            print(f"  [HTTP {respuesta.status_code}] {url}")
            return _fila_error(url, "pdf", respuesta.status_code)

        pdf = pypdf.PdfReader(io.BytesIO(respuesta.content))

        texto = " ".join(pagina.extract_text() or "" for pagina in pdf.pages)
        titulo_raw = (pdf.metadata.title if pdf.metadata else None) or ""

        print(f"  [OK PDF] {url[:80]}")

        return {
            "url":              url,
            "tipo_documento":   "pdf",
            "estado_http":      200,
            "fecha_extraccion": fecha,
            "titulo":           titulo_raw,
            "h1":               "",
            "h2s":              "",
            "texto_principal":  texto,
        }

    except Exception as e:
        print(f"  [ERROR PDF] {url} — {e}")
        return _fila_error(url, "pdf", "Error inesperado")
    

def guardar_resultados(resultados: list, fichero: str) -> None:
    columnas = [
        "url",
        "tipo_documento",
        "estado_http",
        "fecha_extraccion",
        "titulo",
        "h1",
        "h2s",
        "texto_principal",
    ]
    try:
        with open(fichero, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(resultados)

        print(f"\nResultados guardados en: {fichero}")

    except PermissionError:
        print("\n[ERROR] Archivo abierto, no se puede escribir.")
        
if __name__ == "__main__":
    os.makedirs(DATA_SCRAPPING, exist_ok=True)

    urls = cargar_urls(FICHERO_URLS)
    if MAX_URLS:
        urls = urls[:MAX_URLS]

    urls_pdfs = cargar_pdfs(FICHERO_URLS_PDFS)
    if MAX_URLS:
        urls_pdfs = urls_pdfs[:MAX_URLS]

    total      = len(urls)
    total_pdfs = len(urls_pdfs)

    print(f"\nIniciando scraping de {total} páginas web + {total_pdfs} PDFs\n")

    resultados = []

    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{total}]", end=" ")
        resultados.append(extraer_contenido(url))
        time.sleep(PAUSA_SEGUNDOS)

    for i, url in enumerate(urls_pdfs, start=1):
        print(f"[PDF {i}/{total_pdfs}]", end=" ")
        resultados.append(extraer_contenido_pdf(url))
        time.sleep(PAUSA_SEGUNDOS)

    guardar_resultados(resultados, FICHERO_SALIDA)

    ok    = sum(1 for r in resultados if r["estado_http"] == 200)
    error = (total + total_pdfs) - ok

    print(f"\n{'='*40}")
    print(f"  Páginas OK    : {ok}")
    print(f"  Páginas error : {error}")
    print(f"  Total         : {total + total_pdfs}")
    print(f"{'='*40}")

    print("\nSiguiente paso: ejecutar preprocesamiento.py")
