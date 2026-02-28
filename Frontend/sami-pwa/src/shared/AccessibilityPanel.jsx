import { useAccessibilityStore } from '../store/useAccessibilityStore';
import './AccessibilityPanel.css';

export const AccessibilityPanel = () => {
    const { fontSize, setFontSize, highContrast, toggleContrast, isPanelOpen, togglePanel } = useAccessibilityStore();

    if (!isPanelOpen) return null;

    const sizes = [
        { label: 'Pequeño', value: 14 },
        { label: 'Mediano', value: 18 },
        { label: 'Grande', value: 22 }
    ];

    return (
        <div className={`accessibility-sidebar`}>
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