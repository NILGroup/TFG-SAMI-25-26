import { AppRouter } from "../routes/AppRouter";
import { useAccessibilityStore } from "../store/useAccessibilityStore";

function App() {
    const { fontSize, highContrast } = useAccessibilityStore();

    document.documentElement.setAttribute(
        'data-theme',
        highContrast ? 'high-contrast' : 'default'
    );

    const globalStyle = {
        fontSize: `${fontSize}px`,
        minHeight: '100vh',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        transition: 'all 0.3s ease'
    };

    return (
        <div style={globalStyle}>
            <AppRouter />
        </div>
    );
}

export default App;