import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Header } from '../shared/Header';
import { CategorySelection } from '../features/categories/CategorySelection';
import { QueryPage } from '../features/query/QueryPage';
import { AccessibilityPanel } from '../shared/AccessibilityPanel';

export const AppRouter = () => {
    return (

        <BrowserRouter>

            <Header />
            <AccessibilityPanel />

            <Routes>
                <Route path="/" element={<CategorySelection />} />
                <Route path="/query/:categoryId" element={<QueryPage />} />
            </Routes>


        </BrowserRouter>
    );
}