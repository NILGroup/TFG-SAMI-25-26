import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAccessibilityStore } from '../../store/useAccessibilityStore';
import { preguntarAlRAG } from '../../services/api';
import './QueryPage.css';

export const QueryPage = () => {
    const { categoryId } = useParams();
    const navigate = useNavigate();
    const fontSize = useAccessibilityStore((state) => state.fontSize);

    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState(null);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSearch = async (text) => {
        const query = text || question;
        if (!query.trim()) return;

        setQuestion(query);
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
                        <button className="faq-button" onClick={() => handleSearch("¿Cómo pido la beca?")}>
                            ¿Cómo pido la beca?
                        </button>
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
                        <button className="action-btn">Reformular respuesta</button>
                        <button className="action-btn" onClick={() => navigate('/')}>Volver al inicio</button>
                    </footer>
                </div>
            )}
        </div>
    );
};