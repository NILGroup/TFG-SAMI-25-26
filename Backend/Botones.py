from RAG import model


def boton_resumir(texto: str) -> str:
    return model.invoke(f"""Eres SAMI, el asistente virtual de la Facultad de Educación de la Universidad Complutense de Madrid, cuyas siglas significan Sistema Accesible para la Mejora de la 
                        Inclusividad, diseñada para ayudar a los estudiantes del programa ACCEDE y al resto del alumnado a resolver dudas sobre la vida universitaria.
                        
                        Resume el siguiente texto de forma concisa, manteniendo los puntos más importantes. 
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
    return model.invoke(f"""Eres SAMI, el asistente virtual de la Facultad de Educación de la Universidad Complutense de Madrid, cuyas siglas significan Sistema Accesible para la Mejora de la 
                        Inclusividad, diseñada para ayudar a los estudiantes del programa ACCEDE y al resto del alumnado a resolver dudas sobre la vida universitaria.
                        
                        Tu tarea es reformular este texto con frases cortas y palabras sencillas. Solo el texto reescrito, sin comentarios. En español.

                        Ejemplo:
                        Texto original:
                        El periodo de matriculación permanecerá abierto hasta el 15 de septiembre y podrá realizarse de manera telemática a través de la plataforma oficial.
                        Texto reformulado:
                        "La matrícula se puede hacer por internet hasta el 15 de septiembre."

                        Texto: {texto}
                        Texto reformulado:""")

def boton_paso_a_paso(texto: str) -> str:
    return model.invoke(f"""Eres SAMI, el asistente virtual de la Facultad de Educación de la Universidad Complutense de Madrid, cuyas siglas significan Sistema Accesible para la Mejora de la 
                        Inclusividad, diseñada para ayudar a los estudiantes del programa ACCEDE y al resto del alumnado a resolver dudas sobre la vida universitaria.
                        
                        Convierte este texto en pasos numerados claros. Solo los pasos, sin comentarios. En español.
                        
                        Ejemplo 1
                        Texto original:
                        "Para realizar la matrícula debes acceder a la plataforma online, identificarte con tu cuenta institucional y seleccionar las asignaturas antes de confirmar la solicitud."
                        Respuesta:
                        1. Entra en la plataforma de matrícula.
                        2. Inicia sesión con tu cuenta institucional.
                        3. Selecciona las asignaturas.
                        4. Confirma la solicitud.

                        Ejemplo 2
                        Texto original:
                        "Los estudiantes que quieran reservar una sala de estudio en la biblioteca deberán acceder al sistema de reservas y elegir el horario disponible."
                        Respuesta:
                        1. Entra en el sistema de reservas de la biblioteca.
                        2. Busca un horario disponible.
                        3. Selecciona la sala.
                        4. Confirma la reserva.

                        Ejemplo 3
                        Texto original:
                        "Para solicitar una tutoría es necesario enviar un correo electrónico al profesor indicando el motivo de la consulta."
                        Respuesta:
                        1. Escribe un correo al profesor.
                        2. Explica el motivo de la consulta.
                        3. Envía el correo.
                        4. Espera la respuesta del profesor.

                        Ahora convierte el siguiente texto en pasos:

                        Texto: {texto}
                        Paso 1:""")