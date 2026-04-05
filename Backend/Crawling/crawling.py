import requests
from bs4 import BeautifulSoup
import json
import time
from collections import deque
import os

# --- CONFIGURACIÓN ---
BASE_URL = "https://educacion.ucm.es/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data", "Crawling")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Crea la carpeta si no existe

ARCHIVO_SALIDA = os.path.join(OUTPUT_DIR, "crawling_completo_educacion_ucm.json")


def crawl_completo(url_semilla):
    cola = deque([url_semilla])
    visitados = set()
    pdfs_encontrados = set()

    resultado = {
        "paginas": [],
        "pdfs": []
    }

    print(f"Iniciando rastreo completo en {url_semilla}...\n")

    while cola:
        url_actual = cola.popleft()

        if url_actual in visitados:
            continue

        try:
            visitados.add(url_actual)
            paginas = len(resultado["paginas"])
            pdfs = len(resultado["pdfs"])
            print(f"[Páginas: {paginas}] [PDFs: {pdfs}] Rastreando: {url_actual}")

            # --- Caso: la URL es directamente un PDF ---
            if url_actual.lower().endswith('.pdf'):
                if url_actual not in pdfs_encontrados:
                    pdfs_encontrados.add(url_actual)
                    resultado["pdfs"].append({
                        "url": url_actual,
                        "encontrado_en": "url_directa",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"  → PDF directo guardado: {url_actual}")
                continue

            # --- Caso: página HTML ---
            res = requests.get(url_actual, headers=HEADERS, timeout=10)

            if res.status_code != 200 or 'text/html' not in res.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(res.text, 'html.parser')

            resultado["paginas"].append({
                "url": url_actual,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # --- Extraer enlaces ---
            extensiones_omitir = ('.jpg', '.png', '.zip', '.docx', '.xlsx', '.css', '.js')

            for a in soup.find_all('a', href=True):
                enlace = a['href']

                if enlace.startswith('/'):
                    enlace = f"https://educacion.ucm.es{enlace}"

                enlace = enlace.split('#')[0].split('?')[0].rstrip('/')

                if not enlace.startswith(BASE_URL.rstrip('/')):
                    continue

                if enlace.lower().endswith('.pdf'):
                    if enlace not in pdfs_encontrados:
                        pdfs_encontrados.add(enlace)
                        resultado["pdfs"].append({
                            "url": enlace,
                            "encontrado_en": url_actual,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        print(f"  → PDF encontrado: {enlace}")
                    continue

                if (enlace not in visitados
                        and not enlace.lower().endswith(extensiones_omitir)
                        and enlace not in cola):
                    cola.append(enlace)

            time.sleep(0.1)

        except Exception as e:
            print(f"  Error en {url_actual}: {e}")

    return resultado


# --- EJECUCIÓN ---
datos = crawl_completo(BASE_URL)

with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
    json.dump(datos, f, ensure_ascii=False, indent=4)

print(f"\nProceso finalizado.")
print(f"  Páginas únicas encontradas : {len(datos['paginas'])}")
print(f"  PDFs únicos encontrados    : {len(datos['pdfs'])}")
print(f"  Resultados guardados en    : {os.path.abspath(ARCHIVO_SALIDA)}")