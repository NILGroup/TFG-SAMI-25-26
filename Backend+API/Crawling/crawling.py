import requests
from bs4 import BeautifulSoup
import json
import time
from collections import deque

# --- CONFIGURACIÓN ---
BASE_URL = "https://educacion.ucm.es/"
ARCHIVO_SALIDA = "urls_completas_educacion_ucm.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def obtener_todas_las_urls(url_semilla):
    cola = deque([url_semilla])
    visitados = set()
    lista_final_urls = []

    print(f"Iniciando rastreo de URLs en {url_semilla}...")

    while cola:
        url_actual = cola.popleft()
        
        # Evitar procesar la misma URL mas de una vez
        if url_actual in visitados:
            continue
            
        try:
            visitados.add(url_actual)
            print(f"[{len(visitados)}] Localizando enlaces en: {url_actual}")
            
            # Realizo la peticion
            res = requests.get(url_actual, headers=HEADERS, timeout=10)
            
            # Solo procesamos si es una pagina HTML accesible
            if res.status_code != 200 or 'text/html' not in res.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Guardamos la URL en la lista de resultados junto a su timestamp
            lista_final_urls.append({
                "url": url_actual,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # Extraer todos los enlaces de la página
            for a in soup.find_all('a', href=True):
                enlace = a['href']
                
                # 1. Convertir links relativos a absolutos
                if enlace.startswith('/'):
                    enlace = f"https://educacion.ucm.es{enlace}"
                
                # 2. Limpiar anclas (#) y parámetros de consulta (?) para evitar duplicados
                enlace = enlace.split('#')[0].split('?')[0]
                
                # 3. Quitar la barra diagonal final para evitar '.../inicio' y '.../inicio/' como distintas
                enlace = enlace.rstrip('/')

                extensiones_omitir = ('.pdf', '.jpg', '.png', '.zip', '.docx', '.xlsx', '.clss', '.css', '.js')
                
                if (enlace.startswith(BASE_URL.rstrip('/')) and 
                    enlace not in visitados and 
                    not enlace.lower().endswith(extensiones_omitir)):
                    
                    if enlace not in cola:
                        cola.append(enlace)

            # Pausa mínima para no saturar
            time.sleep(0.1)

        except Exception as e:
            print(f"Error en {url_actual}: {e}")
            
    return lista_final_urls

# --- EJECUCIÓN ---
urls_detectadas = obtener_todas_las_urls(BASE_URL)

# Guardar el objeto JSON en el archivo TXT
with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
    json.dump(urls_detectadas, f, ensure_ascii=False, indent=4)

print(f"\nProceso finalizado.")
print(f"Se han encontrado un total de {len(urls_detectadas)} URLs únicas.")
print(f"Los resultados están en: {ARCHIVO_SALIDA}")