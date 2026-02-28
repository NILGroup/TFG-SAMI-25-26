import { useNavigate } from 'react-router-dom';
import { useAccessibilityStore } from '../../store/useAccessibilityStore';
import './CategorySelection.css';

const categories = [
    {
        id: 'academico',
        name: 'Académico',
        desc: 'Campus virtual, exámenes',
        color: '#E3F2FD',
        icon: <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#1976D2" strokeWidth="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z" /><path d="M6 12v5c3 3 9 3 12 0v-5" /></svg>
    },
    {
        id: 'administrativo',
        name: 'Administrativo',
        desc: 'Matrícula, becas y ayudas',
        color: '#F1F8E9',
        icon: <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#689F38" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" /></svg>
    },
    {
        id: 'biblioteca',
        name: 'Biblioteca',
        desc: 'Préstamos y recursos',
        color: '#FFF3E0',
        icon: <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#F57C00" strokeWidth="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 4.5A2.5 2.5 0 016.5 7H20v12.5H6.5a2.5 2.5 0 01-2.5-2.5V4.5z" /></svg>
    },
    {
        id: 'servicios',
        name: 'Servicios',
        desc: 'Deportes, eventos, etc.',
        color: '#F3E5F5',
        icon: <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#7B1FA2" strokeWidth="2"><path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-.755 1.688-1.54 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.784.57-1.838-.197-1.539-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
    }
];

export const CategorySelection = () => {
    const navigate = useNavigate();
    const fontSize = useAccessibilityStore((state) => state.fontSize);

    return (
        <div className="categories-page-wrapper" style={{ fontSize: `${fontSize}px` }}>
            <h2 style={{ marginBottom: '30px', fontSize: '1.5em', textAlign: 'center' }}>
                ¿En qué área necesitas ayuda?
            </h2>

            <div className="categories-grid" role="list">
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        className="category-card"
                        onClick={() => navigate(`/query/${cat.id}`)}
                        aria-label={`Seleccionar categoría ${cat.name}`}
                    >
                        <div className="icon-box" style={{ backgroundColor: cat.color }} aria-hidden="true">
                            {cat.icon}
                        </div>
                        <div className="category-info">
                            <h3>{cat.name}</h3>
                            <p>{cat.desc}</p>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
};