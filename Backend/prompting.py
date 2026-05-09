import ollama
import Backend.utils.io as io

class Prompting:

    def __init__(self, tecnicas: list[str]):
        # Cargar los prompts desde archivos de texto.
        base_url = './prompts/prompt_'
        self.prompts = {
            tecnica: io.cargar_texto(base_url+tecnica+'.txt') for tecnica in tecnicas
        }

    def construccion_prompts(self, texto: str, tecnica: list[str]) -> str:

        """Recibe el tipo de técnica y el texto del corpues y construye el prompt correspondiente."""

        plantilla = "\n".join(self.prompts[t] for t in tecnica)

        prompt = [
            {
                'role': 'system',
                'content': plantilla,
            },
            {
                'role': 'user',
                'content': texto,
            }
        ]
        return prompt

    def run_prompt(self, modelo: str, prompt: str) -> str:

        """Recibe el modelo y el prompt y lo ejecuta en Ollama."""

        respuesta = ollama.chat(modelo, messages=prompt)

        return respuesta['message']['content']