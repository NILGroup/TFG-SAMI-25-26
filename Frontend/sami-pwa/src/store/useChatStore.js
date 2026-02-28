import { create } from 'zustand';

export const useChatStore = create((set) => ({
    messages: [],
    addMessage: (text, sender) => set((state) => ({
        messages: [...state.messages, { id: Date.now(), text, sender }]
    })),
    clearChat: () => set({ messages: [] }),
}));