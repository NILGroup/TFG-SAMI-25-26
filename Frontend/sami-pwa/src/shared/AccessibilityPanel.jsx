import { useAccessibilityStore } from '../store/useAccessibilityStore';
import './AccessibilityPanel.css';

export const AccessibilityPanel = () => {
    const { fontSize, setFontSize, highContrast, toggleContrast, isPanelOpen, togglePanel, tema, setTema } = useAccessibilityStore();

    if (!isPanelOpen) return null;

    const sizes = [
        { label: 'Pequeño', value: 14 },
        { label: 'Mediano', value: 18 },
        { label: 'Grande', value: 22 }
    ];

    const temas = [
        { label: 'Rojo', value: 'rojo', color: '#8D0D19' },
        { label: 'Azul', value: 'azul', color: '#1565C0' },
        { label: 'Verde', value: 'verde', color: '#2E7D32' },
        { label: 'Morado', value: 'morado', color: '#6A1B9A' },
    ];

    return (
        <div className="accessibility-sidebar">
            <div className="sidebar-header">
                <h3>Ajustes de vista</h3>
                <button className="close-btn" onClick={togglePanel}>✕</button>
            </div>

            <section>
                <p style={{ marginBottom: '12px', fontWeight: '600' }}>Tamaño de la letra</p>
                <div className="size-selector">
                    {sizes.map((size) => (
                        <button
                            key={size.value}
                            className={`size-btn ${fontSize === size.value ? 'active' : ''}`}
                            onClick={() => setFontSize(size.value)}
                        >
                            {size.label}
                        </button>
                    ))}
                </div>
            </section>

            <section>
                <p style={{ marginBottom: '12px', fontWeight: '600' }}>Color de la aplicación</p>
                <div className="tema-selector">
                    {temas.map((t) => (
                        <button
                            key={t.value}
                            className={`tema-btn ${tema === t.value ? 'active' : ''}`}
                            onClick={() => setTema(t.value)}
                            aria-label={`Tema ${t.label}`}
                        >
                            <span className="tema-dot" style={{ backgroundColor: t.color }}></span>
                            {t.label}
                        </button>
                    ))}
                </div>
            </section>

            <section>
                <p style={{ marginBottom: '12px', fontWeight: '600' }}>Contraste visual</p>
                <button
                    className={`contrast-toggle ${highContrast ? 'active' : ''}`}
                    onClick={toggleContrast}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10zm0-2V4a8 8 0 110 16z" />
                    </svg>
                    {highContrast ? 'Modo Normal' : 'Alto Contraste'}
                </button>
            </section>
        </div>
    );
};