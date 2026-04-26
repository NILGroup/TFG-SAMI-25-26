from RAG import model

def boton_resumir(texto: str) -> str:
    prompt = f""" Resume el siguiente texto de forma concisa, manteniendo los puntos más importantes. Responde en español. 
        Texto: {texto}
        Resumen:"""
    return model.invoke(prompt)
    
def boton_reformular(texto: str) -> str:
    prompt = f"""Reformula el siguiente texto usando frases cortas y sencillas, 
        vocabulario cotidiano y sin tecnicismos. Responde en español.
        Texto: {texto}
        Reformulación:"""
    return model.invoke(prompt)    

def boton_paso_a_paso(texto: str) -> str:
    prompt = f"""Explica la siguiente información siguiendo un razonamiento paso a paso.

        Primero, analiza la información.
        Después, descompónla en pasos lógicos.
        Finalmente, presenta los pasos numerados de forma clara.

        Información:
        {texto}

        Respuesta final:
        Paso 1:"""
    return model.invoke(prompt)