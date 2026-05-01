const API_URL = 'http://127.0.0.1:5555';

const getUserId = () => {
    let userId = localStorage.getItem('sami_user_id');
    if (!userId) {
        userId = crypto.randomUUID();
        localStorage.setItem('sami_user_id', userId);
    }
    return userId;
};

export const preguntarAlRAG = async (pregunta, categoryId) => {
    const response = await fetch(`${API_URL}/pregunta`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pregunta, user_id: getUserId(), category: categoryId })
    });
    if (!response.ok) throw new Error('Error en la API');
    const data = await response.json();
    return data.respuesta;
};

export const resumirRespuesta = async (texto) => {
    const response = await fetch(`${API_URL}/resumir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto })
    });
    if (!response.ok) throw new Error('Error al resumir');
    const data = await response.json();
    return data.respuesta;
};

export const reformularRespuesta = async (texto) => {
    const response = await fetch(`${API_URL}/reformular`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto })
    });
    if (!response.ok) throw new Error('Error al reformular');
    const data = await response.json();
    return data.respuesta;
};

export const pasoAPasoRespuesta = async (texto) => {
    const response = await fetch(`${API_URL}/paso-a-paso`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto })
    });
    if (!response.ok) throw new Error('Error al generar paso a paso');
    const data = await response.json();
    return data.respuesta;
};

export const getFaqs = async (categoryId) => {
    const response = await fetch(`${API_URL}/faqs?user_id=${getUserId()}&category=${categoryId}`);
    if (!response.ok) throw new Error('Error al obtener FAQs');
    return response.json();
};

export const getHistorial = async (categoryId) => {
    const response = await fetch(`${API_URL}/historial?user_id=${getUserId()}&category=${categoryId}`);
    if (!response.ok) throw new Error('Error al obtener historial');
    return response.json();
};