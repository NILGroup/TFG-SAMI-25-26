import { create } from 'zustand';

export const useHistorialStore = create((set, get) => ({
    historial: {},

    addPregunta: (categoryId, pregunta) => set((state) => {
        const previas = state.historial[categoryId] || [];
        const actualizadas = [pregunta, ...previas].slice(0, 5);
        return {
            historial: { ...state.historial, [categoryId]: actualizadas }
        };
    }),

    getPreguntas: (categoryId) => get().historial[categoryId] || [],

    clearHistorial: () => set({ historial: {} }),
}));