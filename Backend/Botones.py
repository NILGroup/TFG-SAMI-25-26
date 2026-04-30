import ollama

def _invocar(prompt: str) -> str:
    response = ollama.chat(
        model="qwen3.5",
        messages=[{"role": "user", "content": prompt}],
        think=False
    )
    return response.message.content

def boton_resumir(texto: str) -> str:
    return _invocar(f"""Resume este texto de forma concisa. Solo el resumen, sin comentarios. En español.
                    Texto: {texto}
                    Resumen:""")

def boton_reformular(texto: str) -> str:
    return _invocar(f"""Reescribe este texto con frases cortas y palabras sencillas. Solo el texto reescrito, sin comentarios. En español.
                    Texto: {texto}
                    Texto reescrito:""")

def boton_paso_a_paso(texto: str) -> str:
    return _invocar(f"""Convierte este texto en pasos numerados claros. Solo los pasos, sin comentarios. En español.
                    Texto: {texto}
                    Paso 1:""")