from RAG import model


def boton_resumir(texto: str) -> str:
    return model.invoke(f"""Resume este texto de forma concisa. Solo el resumen, sin comentarios. En español.
                    Texto: {texto}
                    Resumen:""")

def boton_reformular(texto: str) -> str:
    return model.invoke(f"""Reescribe este texto con frases cortas y palabras sencillas. Solo el texto reescrito, sin comentarios. En español.
                    Texto: {texto}
                    Texto reescrito:""")

def boton_paso_a_paso(texto: str) -> str:
    return model.invoke(f"""Convierte este texto en pasos numerados claros. Solo los pasos, sin comentarios. En español.
                    Texto: {texto}
                    Paso 1:""")