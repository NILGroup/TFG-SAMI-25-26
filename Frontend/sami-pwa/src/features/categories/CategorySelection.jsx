import { useNavigate } from 'react-router-dom';
import { useAccessibilityStore } from '../../store/useAccessibilityStore';
import './CategorySelection.css';

const categories = [
    {
        id: 'academico',
        name: 'Académico',
        desc: 'Campus virtual, exámenes',
        className: 'category-card--1'

    },
    {
        id: 'administrativo',
        name: 'Administrativo',
        desc: 'Matrícula, becas y ayudas',
        className: 'category-card--2'
    },
    {
        id: 'biblioteca',
        name: 'Biblioteca',
        desc: 'Préstamos y recursos',
        className: 'category-card--3'
    },
    {
        id: 'servicios',
        name: 'Servicios',
        desc: 'Deportes, eventos, etc.',
        className: 'category-card--4'
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
                        className={`category-card ${cat.className}`}
                        onClick={() => navigate(`/query/${cat.id}`)}
                        aria-label={`Seleccionar categoría ${cat.name}`}
                    >
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