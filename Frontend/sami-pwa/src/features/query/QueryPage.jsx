import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAccessibilityStore } from '../../store/useAccessibilityStore';
import { preguntarAlRAG } from '../../services/api';
import './QueryPage.css';


const FAQS_POR_CATEGORIA = {
    academico: [
        {
            pregunta: '¿Cómo accedo al campus virtual?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cuándo son los exámenes finales en la facultad de Educación?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cómo puedo ponerme en contacto con un profesor de una asignatura?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        }
    ],
    administrativo: [
        {
            pregunta: '¿Qué becas y/o ayudas económicas puedo pedir?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cuándo abre el plazo de matrícula en la Facultad de Educación?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cómo puedo aportar nueva documentación a la universidad?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
    ],
    biblioteca: [
        {
            pregunta: '¿Cómo renuevo el préstamo de un libro?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cómo reservo una sala en la biblioteca?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Qué horarios tiene la biblioteca de la facultad de Educación?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        }
    ],
    servicios: [
        {
            pregunta: '¿Cómo accedo al campus virtual?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cómo accedo al campus virtual?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        },
        {
            pregunta: '¿Cómo accedo al campus virtual?',
            respuesta: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
        }
    ]


};

export const QueryPage = () => {
    const { categoryId } = useParams();
    const navigate = useNavigate();
    const fontSize = useAccessibilityStore((state) => state.fontSize);

    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState(null);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const faqs = FAQS_POR_CATEGORIA[categoryId] || [];

    const handleSearch = async (text, respuestaDirecta = null) => {
        const query = text || question;
        if (!query.trim()) return;

        setQuestion(query);

        if (respuestaDirecta != null) {
            setAnswer(respuestaDirecta);
            setIsSubmitted(true);
            return;
        }
        setIsLoading(true);
        setError(null);

        try {
            const respuesta = await preguntarAlRAG(query);
            setAnswer(respuesta);
            setIsSubmitted(true);
        } catch (e) {
            setError('No se pudo conectar con el asistente. Inténtalo de nuevo.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="query-page-container" style={{ fontSize: `${fontSize}px` }}>
            {!isSubmitted ? (
                <div className="search-panel">
                    <h2 className="category-title">Asistente: {categoryId}</h2>
                    <div className="interaction-box">
                        {faqs.map((faq) => (
                            <button
                                key={faq.pregunta}
                                className="faq-button"
                                onClick={() => handleSearch(faq.pregunta, faq.respuesta)}
                            >
                                {faq.pregunta}
                            </button>
                        ))}
                        <div className="input-group">
                            <input
                                className="main-input"
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                placeholder="Escribe aquí..."
                                disabled={isLoading}
                            />
                            <button
                                className="search-confirm-btn"
                                onClick={() => handleSearch()}
                                disabled={isLoading}
                            >
                                {isLoading ? 'Consultando...' : 'Consultar'}
                            </button>
                        </div>
                        {error && <p style={{ color: 'red', marginTop: '12px' }}>{error}</p>}
                    </div>
                </div>
            ) : (
                <div className="response-panel">
                    <header className="response-header">
                        <h1>{question}</h1>
                    </header>
                    <div className="explanation-card">
                        <p>{answer}</p>
                    </div>
                    <footer className="response-actions">
                        <button className="action-btn" onClick={() => { setIsSubmitted(false); setQuestion(''); }}>Nueva consulta</button>
                        <button className="action-btn">Lectura Fácil</button>
                        <button className="action-btn">Respuesta más corta</button>
                        <button className="action-btn" onClick={() => navigate('/')}>Volver al inicio</button>
                    </footer>
                </div>
            )}
        </div>
    );
};