import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { useAccessibilityStore } from '../../store/useAccessibilityStore';
import { preguntarAlRAG, getFaqs, getHistorial, resumirRespuesta, reformularRespuesta, pasoAPasoRespuesta, lecturaFacilRespuesta } from '../../services/api';
import './QueryPage.css';

export const QueryPage = () => {
    const { categoryId } = useParams();
    const navigate = useNavigate();
    const fontSize = useAccessibilityStore((state) => state.fontSize);

    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState(null);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isTransforming, setIsTransforming] = useState(false);
    const [error, setError] = useState(null);
    const [faqs, setFaqs] = useState({ globales: [], personales: [] });
    const [historial, setHistorial] = useState([]);

    useEffect(() => {
        getFaqs(categoryId)
            .then(setFaqs)
            .catch(() => { });

        getHistorial(categoryId)
            .then(setHistorial)
            .catch(() => { });
    }, [categoryId]);

    const textareaRef = useRef(null);

    const handleInputChange = (e) => {
        setQuestion(e.target.value);
        const el = textareaRef.current;
        if (el) {
            el.style.height = 'auto';
            el.style.height = `${el.scrollHeight}px`;
        }
    };

    const handleSearch = async (text) => {
        const query = text || question;
        if (!query.trim()) return;

        setQuestion(query);
        setIsLoading(true);
        setError(null);

        try {
            const respuesta = await preguntarAlRAG(query, categoryId);
            setAnswer(respuesta);
            setIsSubmitted(true);
        } catch (e) {
            setError('No se pudo conectar con el asistente. Inténtalo de nuevo.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleTransformar = async (tipo) => {
        setIsTransforming(true);
        setError(null);
        try {
            let nuevaRespuesta;
            if (tipo === 'resumir') nuevaRespuesta = await resumirRespuesta(answer);
            if (tipo === 'reformular') nuevaRespuesta = await reformularRespuesta(answer);
            if (tipo === 'pasos') nuevaRespuesta = await pasoAPasoRespuesta(answer);
            if (tipo === 'lectura-facil') nuevaRespuesta = await lecturaFacilRespuesta(answer);
            setAnswer(nuevaRespuesta);
        } catch (e) {
            setError('No se pudo transformar la respuesta.');
        } finally {
            setIsTransforming(false);
        }
    };

    return (
        <div className="query-page-container" style={{ fontSize: `${fontSize}px` }}>
            {isLoading || isTransforming ? (
                <div className="loading-screen">
                    <div className="loading-spinner"></div>
                    <p>{isTransforming ? 'Transformando la respuesta...' : 'Consultando al asistente...'}</p>
                </div>
            ) : !isSubmitted ? (
                <div className="search-panel">
                    <h2 className="category-title">Asistente: {categoryId}</h2>
                    <div className="interaction-box">

                        {historial.length > 0 && (
                            <div>
                                <p className="historial-title">Tus consultas recientes:</p>
                                <div className="historial-container">
                                    {historial.map((item) => (
                                        <button
                                            key={`historial-${item.timestamp}`}
                                            className="historial-btn"
                                            onClick={() => handleSearch(item.query)}
                                        >
                                            {item.query}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {historial.length >= 5 ? (
                            <div>
                                <p className="instruction-text">Tus preguntas frecuentes:</p>
                                <div className="faqs-container">
                                    {faqs.personales.map((faq, index) => (
                                        <button
                                            key={`personal-${index}-${faq}`}
                                            className="faq-button"
                                            onClick={() => handleSearch(faq)}
                                        >
                                            {faq}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div>
                                <p className="instruction-text">Preguntas frecuentes:</p>
                                <div className="faqs-container">
                                    {faqs.globales.map((faq, index) => (
                                        <button
                                            key={`global-${index}-${faq}`}
                                            className="faq-button"
                                            onClick={() => handleSearch(faq)}
                                        >
                                            {faq}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="input-group">
                            <textarea
                                ref={textareaRef}
                                className="main-input"
                                value={question}
                                onChange={handleInputChange}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSearch();
                                    }
                                }}
                                placeholder="Escribe aquí tu pregunta..."
                                rows={1}
                            />
                            <button
                                className="search-confirm-btn"
                                onClick={() => handleSearch()}
                            >
                                Consultar
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
                    {error && <p style={{ color: 'red', marginTop: '12px' }}>{error}</p>}
                    <footer className="response-actions">
                        <button className="action-btn" onClick={() => { setIsSubmitted(false); setQuestion(''); }}>Nueva consulta</button>
                        <button className="action-btn" onClick={() => handleTransformar('lectura-facil')} disabled={isTransforming}>Lectura Fácil</button>
                        <button className="action-btn" onClick={() => handleTransformar('resumir')} disabled={isTransforming}>Respuesta más corta</button>
                        <button className="action-btn" onClick={() => handleTransformar('pasos')} disabled={isTransforming}>Respuesta por pasos</button>
                        <button className="action-btn" onClick={() => handleTransformar('reformular')} disabled={isTransforming}>Reformular respuesta</button>
                        <button className="action-btn" onClick={() => navigate('/')}>Volver al inicio</button>
                    </footer>
                </div>
            )}
        </div>
    );
};