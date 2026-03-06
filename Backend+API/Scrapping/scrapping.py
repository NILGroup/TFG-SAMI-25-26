#pip install requests beautifulsoup4
import json # libreria para leer el archivo obtenido en el crawling
import time # libreria para hacer pausas entre peticiones
import csv # libreria para guardar los resultados
import requests # libreria para hacer peticiones HTTP
from bs4 import BeautifulSoup # libreria para parsear el HTML de cada pagina

FICHERO_URLS = "urls_completas_educacion_ucm.json"
FICHERO_SALIDA = "resultados_scrapping.csv"
PAUSA_SEGUNDOS = 1.5
MAX_URLS = None # Para probar funcionamiento de manera rápida, limitar a un número (20 p.e.).

#Función para cargar las URLs desde el archivo JSON generado por el crawling
def cargar_urls(fichero):
    with open(fichero, "r", encoding = "utf-8") as f:
        datos = json.load(f)
    
    urls_unicas = list({item['url'] for item in datos})
    print(f"Total URLs únicas cargadas: {len(urls_unicas)}")
    return urls_unicas



