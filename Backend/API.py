# pip install fastapi uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from RAG import pregunta_a_RAG, crear_RAG
from Botones import boton_resumir, boton_reformular, boton_paso_a_paso, boton_lectura_facil
from persistence import init_db, log_conversation, get_history, get_global_faqs, get_personal_faqs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    crear_RAG()
    print("RAG inicializado")
    init_db()
    print("Base de datos inicializada")
    
    yield  # La app corre aquí
    
    # Shutdown
    print("Liberando recursos...")
    

app = FastAPI(
    title="API de SAMI",
    description="Recibe preguntas y devuelve las respuestas proporcionadas por un LLM",
    version="1.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # puerto de Vite por defecto
    allow_methods=["*"],
    allow_headers=["*"],
)

class Pregunta(BaseModel):
    pregunta: str
    user_id: str
    category: str


class Respuesta(BaseModel):
    respuesta: str

class Texto(BaseModel):
    texto: str

@app.get("/")
def saludo():
    return {"mensaje": "API SAMI operativa"}


@app.post("/pregunta")
async def preguntar(data: Pregunta):
    respuesta = pregunta_a_RAG(data.pregunta, data.category)
    log_conversation(data.user_id, data.category, data.pregunta, respuesta)
    return Respuesta(respuesta=respuesta)
    
@app.post("/resumir")
async def resumir(data: Texto):
    respuesta = boton_resumir(data.texto)
    return Respuesta(respuesta=respuesta)

@app.post("/reformular")
async def reformular(data: Texto):
    respuesta = boton_reformular(data.texto)
    return Respuesta(respuesta=respuesta)

@app.post("/paso-a-paso")
async def paso_a_paso(data: Texto):
    respuesta = boton_paso_a_paso(data.texto)
    return Respuesta(respuesta=respuesta)

@app.post("/lectura-facil")
async def lectura_facil(data: Texto):
    respuesta = boton_lectura_facil(data.texto)
    return Respuesta(respuesta=respuesta)

@app.get("/faqs")
def faqs(user_id: str, category: str):
    return {
        "globales":   get_global_faqs(category=category),
        "personales": get_personal_faqs(user_id=user_id, category=category)
    }

@app.get("/historial")
def historial(user_id: str, category: str):
    return get_history(user_id=user_id, category=category)