# pip install fastapi uvicorn

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from RAG import pregunta_a_RAG, crear_RAG


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    crear_RAG()
    print("RAG inicializado")
    
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


class Respuesta(BaseModel):
    respuesta: str


@app.get("/")
def saludo():
    return {"mensaje": "API SAMI operativa"}


@app.post("/pregunta")
async def preguntar(data: Pregunta):
    respuesta = pregunta_a_RAG(data.pregunta)
    return Respuesta(respuesta=respuesta)
