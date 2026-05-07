from RAG import model


def boton_resumir(texto: str) -> str:
    return model.invoke(f"""Resume el siguiente texto de forma concisa, manteniendo los puntos más importantes. 
                        Solo el resumen, sin comentarios. En español.

                        Ejemplo:
                        Texto: "Para acceder a la biblioteca, el estudiante deberá presentar su carnet universitario 
                        en el mostrador de entrada, donde el personal comprobará que está matriculado en el curso 
                        académico en vigor y procederá a registrar su entrada en el sistema."
                        Resumen: "Para entrar a la biblioteca necesitas tu carnet universitario. El personal lo comprueba y registra tu entrada."

                        Ahora resume este texto:
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