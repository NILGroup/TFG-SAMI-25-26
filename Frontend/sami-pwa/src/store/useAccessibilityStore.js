import { create } from 'zustand';

export const useAccessibilityStore = create((set) => ({
    fontSize: 16,
    highContrast: false,
    isPanelOpen: false,
    tema: 'rojo',
    setFontSize: (size) => set({ fontSize: size }),
    toggleContrast: () => set((state) => ({ highContrast: !state.highContrast })),
    togglePanel: () => set((state) => ({ isPanelOpen: !state.isPanelOpen })),
    setTema: (tema) => set({ tema }),
}));