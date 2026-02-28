const API_URL = 'http://127.0.0.1:5555';

export const preguntarAlRAG = async (pregunta) => {
    const response = await fetch(`${API_URL}/pregunta`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pregunta })
    });

    if (!response.ok) throw new Error('Error en la API');

    const data = await response.json();
    return data.respuesta;
};