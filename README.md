<div align="center">
  <img src=".github/assets/gif-sami.gif" alt="Banner de SAMI" width="1024">
</div>

---
<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-009688?style=flat&logo=fastapi&logoColor=white) 
![Uvicorn](https://img.shields.io/badge/Uvicorn-0.42.0-4051b5?style=flat&logo=unicorn&logoColor=white) 
![LangChain](https://img.shields.io/badge/LangChain-1.2.12-1C3C3C?style=flat&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5.5-F46F25?style=flat&logo=databricks&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.10.0-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-5.3.0-FF6F00?style=flat&logo=huggingface&logoColor=white)
![Loguru](https://img.shields.io/badge/Loguru-0.7.3-39AF78?style=flat&logo=python&logoColor=white)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.14.3-59666C?style=flat&logo=python&logoColor=white) 

</div>

---

## Instalación y configuración
Instrucciones para configurar el entorno del proyecto:

- Clonar el repositorio:
```bash
git clone https://github.com/NILGroup/TFG-SAMI-25-26.git
```
- Ejecutar el siguiente comando para instalar las dependencias necesarias:
```
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

### ¿Qué es SAMI?
**SAMI** *(Sistema Asistente para la Mejora a la Inclusión)* es un asistente conversacional basado en inteligencia artificial desarrollado como Trabajo de Fin de Grado para la Facultad de Educación de la Universidad Complutense de Madrid. Utiliza una arquitectura **RAG** *(Retrieval-Augmented Generation)* para responder preguntas sobre la facultad con información actualizada y verificable, poniendo especial énfasis en la **accesibilidad cognitiva** para usuarios con discapacidad intelectual.

### Problema que Resuelve
El programa **ACCEDE** de la UCM (título propio para la formación de Técnicos Auxiliares en Evaluación de Entornos Inclusivos) identificó una dificultad persistente en su alumnado: comprender la estructura organizativa, los procedimientos administrativos y el funcionamiento cotidiano de la Facultad de Educación. La información relevante se encuentra dispersa en múltiples páginas y documentos con un lenguaje excesivamente técnico, lo que supone una barrera especialmente significativa para estudiantes con discapacidad intelectual.


### Solución
SAMI permite a los usuarios:
- Realizar preguntas en lenguaje natural sobre la Facultad de Educación de la UCM.
- Obtener respuestas claras y accesibles, adaptadas a los principios de **Lectura Fácil**.
- Recibir explicaciones paso a paso de trámites y procesos administrativos.
- Consultar información fundamentada en documentación oficial extraída directamente del sitio web de la facultad.
- Recuperar el historial de conversación entre sesiones gracias a una memoria conversacional persistente.

### Público Objetivo
SAMI está dirigido principalmente al alumnado del programa **ACCEDE** de la UCM, así como a cualquier estudiante, docente o miembro del personal que necesite orientación sobre la Facultad de Educación. El sistema presta especial atención a personas con **discapacidad intelectual**, con el objetivo de fomentar su autonomía dentro del entorno universitario.

---

## Características Principales

- **RAG con Multi-Query Retrieval y Reranking**: Genera múltiples reformulaciones de cada consulta para ampliar la cobertura de búsqueda y reordena los resultados con un modelo CrossEncoder, seleccionando únicamente los fragmentos más relevantes para construir el contexto del LLM.

- **Interfaz PWA accesible**: Implementada en React + Vite, separa la formulación de preguntas y la visualización de respuestas en pantallas independientes para reducir la carga cognitiva, con soporte para temas de color, alto contraste y ajuste de tamaño de texto.

- **Adaptación dinámica de respuestas**: El usuario puede transformar cualquier respuesta sin reformular la consulta mediante botones de **Lectura Fácil**, **Paso a paso**, **Reformular** y **Resumir**, cada uno basado en distintas técnicas de prompt engineering.

- **Categorías temáticas**: Las consultas se organizan en cuatro áreas —Académico, Biblioteca, Administrativo y Servicios— que actúan como contexto adicional para el RAG y facilitan la navegación mediante un código de colores accesible.

- **Pipeline ETL propio**: Construcción automatizada de la base de conocimiento a partir del sitio web oficial de la Facultad de Educación mediante crawling, scraping, preprocesamiento y vectorización en ChromaDB.

---

## Contribuidores
<a href="https://github.com/NILGroup/TFG-SAMI-25-26/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NILGroup/TFG-SAMI-25-26" />
</a>

 ---
