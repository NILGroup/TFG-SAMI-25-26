import silabeador
from typing import List
import src.utils.io as io
import numpy as np

class Analizador:

    def __init__(self):
        self.resultados = {}
        self.palabras_baja_frecuencia = io.cargar_palabras_dict('data/crea_lemas.txt')
        self.palabras_comunes = io.cargar_palabras_comunes('data/10000_formas.txt', 10000)


    def analiza(self, texto: str, documento: str) -> None:
       
       """Recibe el documento procesado y un diccionario de pyphen.
       Analiza el texto de una pasada y recaba la información necesaria."""

       palabras: List = []
       silabas = 0
       letras = 0
       tokens = 0
       lemas = [t.lemma_.lower() for t in documento if t.is_alpha]
       n_lemas = len(set(lemas))
       p_raras = 0

       for token in documento:
           tokens += 1
           if token.is_alpha:
               palabras.append(token)
               letras += len(token.text)
               sil = silabeador.syllabify(token.text)
               silabas += len(sil)
               p_raras += 1 if self.es_palabra_rara(token.text.lower()) else 0

       oraciones = list(documento.sents)
       num_palabras = len(palabras)
       num_oraciones = len(oraciones)
       depths = []
       total_puncts = 0

       n_oracion_compleja = 0
       for o in oraciones:
           puncts_o = 0
           n_oracion_compleja += 1 if self.es_oracion_compleja(o) else 0
           max_depth_oracion = max(self.depth(t) for t in o)
           depths.append(max_depth_oracion)
           for t in o:
               if t.pos_ == 'PUNCT':
                   if t.i == o[-1] and t.text == '.':
                       continue
                   puncts_o += 1
           total_puncts += puncts_o

       self.resultados = {
           'palabras': palabras,
           'num_palabras': num_palabras,
           'num_silabas': silabas,
           'num_letras': letras,
           'num_tokens': tokens,
           'oraciones': oraciones,
           'num_oraciones': num_oraciones,
           'ldi': self.calcular_ldi(len(oraciones), n_lemas),
           'ilfw': self.calcular_ilfw(documento, len(palabras)),
           'num_oracion_compleja': n_oracion_compleja,
           'palabras_raras': p_raras,
           'asl': num_palabras / num_oraciones if num_oraciones > 0 else 0.0,
           'cs': n_oracion_compleja / num_oraciones if num_oraciones > 0 else 0.0,
           'depths': np.mean(depths) if depths else 0.0,
           'puncts': total_puncts
       }
       

    def contador_palabras (self) -> tuple[int, list[str]]:

        """Devuelve en primer lugar el número de palbaras que tiene el texto, y en segundo lugar una lista con esas palabras"""

        return self.resultados['num_palabras'], self.resultados['palabras']


    def contador_silabas (self) -> int:

        """Devuelve el número de sílabas del texto"""

        return self.resultados['num_silabas']

    def contador_oraciones (self) -> tuple[int, list[str]]:

        """Devuelve en primer lugar el número de oraciones y en segundo una lista de oraciones. """

        return self.resultados['num_oraciones'], self.resultados['oraciones']

    def contador_letras (self) -> int:

        """Devuelve el número de letras que hay."""

        return self.resultados['num_letras']

    def contador_tokens (self) -> int:

        """Devuelve el número de tokens que hay."""

        return self.resultados['num_tokens']
    
    def calcular_ldi(self, n_oraciones: int, n_lemas: int) -> float:

        """Calcula y devuelve el Índice de Distribución Léxica (LDI) del texto."""
        ldi = 0.0

        if n_oraciones > 0 and n_lemas > 0:
            ldi = n_lemas / n_oraciones

        return ldi
    def calcular_ilfw(self, documento: str, n_palabras: int) -> float:

        """Calcula y devuelve el Índice de Palabras con Poca Frecuencia (ILFW) del texto."""

        palabras_baja_frecuencia = 0

        for token in documento:
            if token.is_alpha:
                lema = token.lemma_.lower()
                freq = self.palabras_baja_frecuencia.get(lema)

                if freq is not None and freq < 1000:
                    palabras_baja_frecuencia += 1

        if n_palabras > 0:
            ilfw = (palabras_baja_frecuencia / n_palabras) * 100
        else:
            ilfw = 0.0

        return ilfw
    
    def es_oracion_compleja (self, oracion: str) -> bool:

        """Devuelve True si la oración es compleja, en caso contrario devuelve False."""

        hay_cluster = 0
        en_cluster = False

        for t in oracion:
            if t.pos_ in {'VERB', 'AUX'} and 'Fin' in t.morph.get('VerbForm'):
                if not en_cluster:
                    hay_cluster += 1
                    en_cluster = True
            else:
                en_cluster = False

            if hay_cluster > 1:
                break

        return hay_cluster > 1
    
    def es_palabra_rara (self, palabra: str) -> bool:

        """Para una palabra devuelve True si es una palabra rara (no se encuentra entre las 1500 máas comunes)."""

        return palabra not in self.palabras_comunes
    
    def depth (self, token) -> int:

        """Calcula la profundidad de un token en el árbol sintáctico."""

        depth = 0
        current = token

        while current.head != current:
            depth += 1
            current = current.head

        return depth
    
    def obetener_resultados(self) -> dict:

        """Devuelve un diccionario con los resultados del análisis."""

        return self.resultados