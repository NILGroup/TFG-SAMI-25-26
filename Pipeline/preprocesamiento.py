import os
import csv
import re

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA_SCRAPPING = os.path.join(BASE_DIR, "Data", "Scrapping")
 
CSV_ENTRADA = os.path.join(DATA_SCRAPPING, "resultados_scrapping_raw.csv")
CSV_SALIDA  = os.path.join(DATA_SCRAPPING, "resultados_preprocesados.csv")

MIN_PALABRAS = 30

def limpiar_bom(texto: str) -> str:
    # Eliminar el BOM si está presente
    return texto.lstrip('\ufeff')

def corregir_encoding_cp1252(texto: str) -> str:
    # Reemplazar caracteres comunes de CP1252 que pueden aparecer mal codificados
    return texto.replace("\x96", "–")

def limpiar_titulo_pdf(titulo: str) -> str:
    t = titulo.strip()
    if not t:
        return ""
    if t.lower() == "nan":
        return ""
    if len(t) <= 2:
        return ""
    if t.startswith("¡Error") or t.startswith("Error"):
        return ""
    # Indicadores de doble codificacion UTF-8/Latin-1 (mojibake)
    if any(c in t for c in ["Ì", "Ã", "Â"]):
        return ""
    return t

def eliminar_breadcrumbs(texto: str) -> str:
    # Patron 1: breadcrumb con separador » o >
    texto = re.sub(
        r'^[\s]*Portada\s*[»>][\s\S]*?(?=[A-ZÁÉÍÓÚÑ][a-záéíóúñ])',
        '',
        texto
    ).strip()
 
    # Patron 2: prefijo "UCM Directo" en paginas /directo/
    texto = re.sub(r'^UCM Directo\s+', '', texto).strip()
 
    return texto

def normalizar_texto(texto: str) -> str:
    texto = re.sub(r'[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ¿¡.,;:()\-\n]', ' ', texto)
    texto = re.sub(r' {2,}', ' ', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

def limpiar_campo(texto: str) -> str:
    texto = limpiar_bom(texto)
    texto = corregir_encoding_cp1252(texto)
    texto = normalizar_texto(texto)
    return texto

def preprocesar_fila(row: dict) -> dict:
    tipo = row.get("tipo_documento", "web").strip().lower()
 
    # --- Campos de metadatos: limpiar BOM y encoding ---
    titulo = limpiar_campo(row.get("titulo", ""))
    h1     = limpiar_campo(row.get("h1", ""))
    h2s    = limpiar_campo(row.get("h2s", ""))
 
    # --- Titulo de PDF: validacion adicional tras la limpieza basica ---
    if tipo == "pdf":
        titulo = limpiar_titulo_pdf(titulo)
 
    # --- Texto principal: limpieza completa + breadcrumbs ---
    texto = limpiar_campo(row.get("texto_principal", ""))
    if tipo == "web":
        texto = eliminar_breadcrumbs(texto)
 
    # --- Metricas derivadas ---
    num_palabras = len(texto.split()) if texto else 0
    valido       = num_palabras >= MIN_PALABRAS  # False en paginas de galeria/album
 
    return {
        "url":              row.get("url", "").strip(),
        "tipo_documento":   tipo,
        "estado_http":      row.get("estado_http", "").strip(),
        "fecha_extraccion": row.get("fecha_extraccion", "").strip(),
        "titulo":           titulo,
        "h1":               h1,
        "h2s":              h2s,
        "texto_principal":  texto,
        "num_palabras":     num_palabras,
        "valido":           valido,   # True/False: indica si el doc tiene contenido suficiente
    }

def preprocesar(csv_entrada: str = CSV_ENTRADA, csv_salida: str = CSV_SALIDA) -> None:
    if not os.path.exists(csv_entrada):
        raise FileNotFoundError(
            f"No se encontró el CSV de entrada: {csv_entrada}\n"
            f"Ejecuta primero scrapping.py."
        )
 
    csv.field_size_limit(10 * 1024 * 1024)
 
    resultados  = []
    omitidos    = 0
    errores_http = 0
 
    with open(csv_entrada, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Saltar filas con errores HTTP (timeout, connection error, etc.)
            try:
                estado = int(row.get("estado_http", 0))
                if estado != 200:
                    errores_http += 1
                    continue
            except ValueError:
                errores_http += 1
                continue
 
            fila_limpia = preprocesar_fila(row)
            resultados.append(fila_limpia)
 
            if not fila_limpia["valido"]:
                omitidos += 1
 
    if not resultados:
        raise ValueError("El CSV de entrada no contiene filas procesables.")
 
    columnas = [
        "url",
        "tipo_documento",
        "estado_http",
        "fecha_extraccion",
        "titulo",
        "h1",
        "h2s",
        "texto_principal",
        "num_palabras",
        "valido",        # True = documento apto para la base de conocimiento RAG
    ]
 
    try:
        with open(csv_salida, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(resultados)
        print(f"CSV preprocesado guardado en: {csv_salida}")
    except PermissionError:
        print(
            f"\n[ERROR] No se puede escribir en: {csv_salida}\n"
            f"  → El archivo está abierto en otro programa.\n"
            f"  → Ciérralo y vuelve a ejecutar el script."
        )
        return
 
    # --- Resumen ---
    validos   = sum(1 for r in resultados if r["valido"])
    no_validos = len(resultados) - validos
    web_ok    = sum(1 for r in resultados if r["tipo_documento"] == "web"  and r["valido"])
    pdf_ok    = sum(1 for r in resultados if r["tipo_documento"] == "pdf"  and r["valido"])
    media_pal = (
        sum(r["num_palabras"] for r in resultados if r["valido"]) / validos
        if validos else 0
    )
 
    print(f"\n{'='*45}")
    print(f"  Total filas procesadas  : {len(resultados)}")
    print(f"  Errores HTTP omitidos   : {errores_http}")
    print(f"  Documentos validos      : {validos}  (web: {web_ok} | pdf: {pdf_ok})")
    print(f"  Documentos no validos   : {no_validos}  (< {MIN_PALABRAS} palabras, marcados valido=False)")
    print(f"  Media palabras/doc      : {media_pal:.0f}")
    print(f"{'='*45}")
    print(f"\nSiguiente paso: ejecutar crear_DB.py")
 
 
if __name__ == "__main__":
    print(f"CSV entrada : {CSV_ENTRADA}")
    print(f"CSV salida  : {CSV_SALIDA}")
    preprocesar()