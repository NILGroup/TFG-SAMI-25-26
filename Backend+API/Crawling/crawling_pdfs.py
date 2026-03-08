import requests
from bs4 import BeautifulSoup
import json
import time
from collections import deque

# --- CONFIGURACIÓN ---
BASE_URL = "https://educacion.ucm.es/"
ARCHIVO_SALIDA = "crawling_pdfs.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def obtener_todos_los_pdfs(url_semilla):
    cola = deque([url_semilla])
    visitados = set()
    pdfs_encontrados = set()  # Set para evitar guardar el mismo PDF dos veces
    lista_final_pdfs = []

    print(f"Iniciando rastreo de PDFs en {url_semilla}...")

    while cola:
        url_actual = cola.popleft()

        if url_actual in visitados:
            continue

        try:
            visitados.add(url_actual)
            print(f"[Páginas visitadas: {len(visitados)}] [PDFs encontrados: {len(lista_final_pdfs)}] Rastreando: {url_actual}")
            
            # Si la URL actual es un PDF, lo guardamos
            if url_actual.lower().endswith('.pdf'):
                if url_actual not in pdfs_encontrados:
                    pdfs_encontrados.add(url_actual)
                    lista_final_pdfs.append({
                        "url": url_actual,
                        "encontrado_en": "url_directa",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"  → PDF directo guardado: {url_actual}")
                continue  # No intentamos parsear el PDF como HTML

            res = requests.get(url_actual, headers=HEADERS, timeout=10)

        # Solo procesamos páginas HTML accesibles
            if res.status_code != 200 or 'text/html' not in res.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(res.text, 'html.parser')

            # Extraer todos los enlaces de la página
            for a in soup.find_all('a', href=True):
                enlace = a['href']

                # Convertir links relativos a absolutos
                if enlace.startswith('/'):
                    enlace = f"https://educacion.ucm.es{enlace}"

                # Limpiar anclas y parámetros
                enlace = enlace.split('#')[0].split('?')[0].rstrip('/')

                # ── NOVEDAD 1: Si el enlace es un PDF, lo guardamos ──
                if enlace.lower().endswith('.pdf') and enlace not in pdfs_encontrados:
                    pdfs_encontrados.add(enlace)
                    lista_final_pdfs.append({
                        "url": enlace,
                        "encontrado_en": url_actual,   # Página donde estaba el enlace, útil para debug
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"  → PDF encontrado: {enlace}")
                    continue  # No tiene sentido añadir un PDF a la cola de páginas a visitar

                # ── NOVEDAD 2: Si es una página HTML del dominio, la añadimos a la cola ──
                extensiones_omitir = ('.jpg', '.png', '.zip', '.docx', '.xlsx', '.css', '.js')

                if (enlace.startswith(BASE_URL.rstrip('/'))
                        and enlace not in visitados
                        and not enlace.lower().endswith(extensiones_omitir)
                        and enlace not in cola):
                    cola.append(enlace)

            time.sleep(0.1)

        except Exception as e:
            print(f"Error en {url_actual}: {e}")

    return lista_final_pdfs


# --- EJECUCIÓN ---
pdfs_detectados = obtener_todos_los_pdfs(BASE_URL)

with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
    json.dump(pdfs_detectados, f, ensure_ascii=False, indent=4)

print(f"\nProceso finalizado.")
print(f"Se han encontrado un total de {len(pdfs_detectados)} PDFs únicos.")
print(f"Los resultados están en: {ARCHIVO_SALIDA}")