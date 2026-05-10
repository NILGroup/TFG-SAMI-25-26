import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAccessibilityStore } from '../store/useAccessibilityStore';
import './Header.css';
import logo from '../assets/Sami.png';

export const Header = () => {
    const { togglePanel, fontSize } = useAccessibilityStore();
    const navigate = useNavigate();
    const location = useLocation();

    const isHome = location.pathname === '/';

    return (
        <header className="header-container" style={{ fontSize: `${fontSize}px` }}>
            <div className="header-left">
                {!isHome && (
                    <button onClick={() => navigate(-1)} className="back-button" aria-label="Volver">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M15 18l-6-6 6-6" />
                        </svg>
                    </button>
                )}
                <Link to="/" className="header-logo">
                    <img src={logo} alt="Logo SAMI" className="header-logo-icon" />
                    <div className="header-logo-text">
                        <span className="header-logo-title">SAMI</span>
                        <span className="header-logo-subtitle">Universidad Complutense de Madrid</span>
                    </div>
                </Link>
            </div>

            <button onClick={togglePanel} className="settings-button" aria-label="Accesibilidad">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
                </svg>
                Ajustes
            </button>
        </header>
    );
};