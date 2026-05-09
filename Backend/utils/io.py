from pathlib import Path
import pandas as pd

def cargar_texto(ruta: str) -> str:

    """Carga el contenido de un archivo de texto y lo devuelve como un string."""
    
    with open(ruta, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()
    return contenido

def guardar_texto(ruta_base: str, texto: str, evaluacion: object, validacion: dict) -> None:
    """
    Guarda:
    - Texto adaptado en un .txt
    - Añade métricas en un CSV acumulativo
    - Añade validación en un CSV acumulativo (fila=texto, columnas=pautas)
    """

    ruta_base = Path(ruta_base)
    ruta_base.parent.mkdir(parents=True, exist_ok=True)

    txt_path = ruta_base.with_suffix('.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(texto)

    metricas = {}
    metricas['texto'] = ruta_base.stem
    if hasattr(evaluacion, 'fernandez_huerta'):
        metricas['fernandez_huerta'] = round(evaluacion.fernandez_huerta(), 2)
    if hasattr(evaluacion, 'promedio_longitud_oraciones'):
        metricas['prom_long_oraciones_palabras'] = round(evaluacion.promedio_longitud_oraciones(), 2)
    if hasattr(evaluacion, 'promedio_longitud_oraciones_letras'):
        metricas['prom_long_oraciones_letras'] = round(evaluacion.promedio_longitud_oraciones_letras(), 2)
    if hasattr(evaluacion, 'promedio_longitud_tokens'):
        metricas['prom_long_oraciones_tokens'] = round(evaluacion.promedio_longitud_tokens(), 2)
    if hasattr(evaluacion, 'calular_lexical_complexity_index'):
        metricas['lexical_complexity_index'] = round(evaluacion.calular_lexical_complexity_index(), 2)
    if hasattr(evaluacion, 'calcular_spanish_readability_index'):
        metricas['spanish_readability_index'] = round(evaluacion.calcular_spanish_readability_index(), 2)
    if hasattr(evaluacion, 'calcular_sentence_complexity_index'):
        metricas['sentence_complexity_index'] = round(evaluacion.calcular_sentence_complexity_index(), 2)
    if hasattr(evaluacion, 'calcular_percentage_of_complex_sentences'):
        metricas['percentage_complex_sentences'] = round(evaluacion.calcular_percentage_of_complex_sentences(), 2)
    if hasattr(evaluacion, 'calcular_embedding_depth'):
        metricas['embedding_depth'] = round(evaluacion.calcular_embedding_depth(), 2)
    if hasattr(evaluacion, 'calcular_punct'):
        metricas['punct_por_oracion'] = round(evaluacion.calcular_punct(), 2)

    df_metricas = pd.DataFrame([metricas])

    csv_metricas_path = ruta_base.parent / 'metricas_adaptaciones.csv'
    # Añadir al CSV, crear si no existe
    if csv_metricas_path.exists():
        df_metricas.to_csv(csv_metricas_path, mode='a', index=False, header=False, sep=';', decimal=',', encoding='utf-8')
    else:
        df_metricas.to_csv(csv_metricas_path, mode='w', index=False, sep=';', decimal=',', encoding='utf-8')

    validacion_dict = {'texto': ruta_base.stem}
    for pauta, elementos in validacion.items():
        validacion_dict[pauta] = 1 if elementos else 0

    if not validacion_dict:
        validacion_dict = {'Todas las pautas se cumplen': 0}
    df_validacion = pd.DataFrame([validacion_dict])

    csv_validacion_path = ruta_base.parent / 'validacion_adaptaciones.csv'
    if csv_validacion_path.exists():
        df_validacion.to_csv(csv_validacion_path, mode='a', index=False, header=False, sep=';', encoding='utf-8')
    else:
        df_validacion.to_csv(csv_validacion_path, mode='w', index=False, sep=';', encoding='utf-8')


def cargar_palabras_dict(ruta: str) -> dict:

    """Carga un archivo de palabras y sus frecuencias en un diccionario."""
    
    frec_por_lema = {}
    with open(ruta, encoding="utf-8") as f:

        next(f)  # saltar cabecera
        for line in f:
            cols = line.strip().split("\t")
            if len(cols) < 3:
                continue

            lema = cols[0].lower()
            try:
                freq = int(cols[2])
            except ValueError:
                continue

            # No sé si es necesario acumular frecuencias si hay lemas repetidos
            ###### TODO: comprobar si hay lemas repetidos en el archivo
            frec_por_lema[lema] = frec_por_lema.get(lema, 0) + freq

    return frec_por_lema

def cargar_palabras_comunes(ruta_txt: str, top: int) -> set[str]:

    """Carga las N palabras más frecuentes de un TXT y devuelve un set."""

    palabras_frecuentes = set()
    
    with open(ruta_txt, encoding="utf-8") as f:
        next(f)
        for i, line in enumerate(f):
            if i >= top:
                break
            cols = line.strip().split("\t")
            if not cols:
                continue
            palabra = cols[0].lower()
            palabras_frecuentes.add(palabra)
        print (i)
    
    return palabras_frecuentes

from pathlib import Path

def cargar_textos_carpeta(carpeta: str) -> dict:
    """
    Carga todos los archivos .txt de la carpeta especificada.
    """
    carpeta_path = Path(carpeta)

    if not carpeta_path.exists() or not carpeta_path.is_dir():
        raise FileNotFoundError(f"La carpeta '{carpeta}' no existe o no es un directorio.")

    textos = {}
    for archivo in carpeta_path.glob("*.txt"):
        with open(archivo, "r", encoding="utf-8") as f:
            textos[archivo.stem] = f.read()  # stem = nombre sin extensión

    return textos
