import { create } from 'zustand';
import WebApp from '@twa-dev/sdk';

// Расширяем интерфейс WebApp для CloudStorage
declare module '@twa-dev/sdk' {
  interface WebApp {
    CloudStorage: {
      setItem(key: string, value: string, callback?: (error: any, success: boolean) => void): void;
      getItem(key: string, callback: (error: any, value: string) => void): void;
      removeItem(key: string, callback?: (error: any, success: boolean) => void): void;
      getKeys(callback: (error: any, keys: string[]) => void): void;
    };
  }
}

interface AppState {
  userId: number | null;
  activeTab: string;
  isPro: boolean;
  profile: Record<string, any> | null;
  inputDraft: string;
  setUserId: (id: number) => void;
  setActiveTab: (tab: string) => void;
  setPro: (status: boolean) => void;
  setProfile: (data: Record<string, any>) => void;
  setInputDraft: (text: string) => void;
  syncFromCloud: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  userId: null,
  activeTab: 'dashboard',
  isPro: false,
  profile: null,
  inputDraft: '',

  setUserId: (id) => set({ userId: id }),

  setActiveTab: (tab) => {
    set({ activeTab: tab });
    if (WebApp.CloudStorage) {
      WebApp.CloudStorage.setItem('activeTab', tab);
    }
  },

  setPro: (status) => set({ isPro: status }),

  setProfile: (data) => set({ profile: data }),

  setInputDraft: (text) => {
    set({ inputDraft: text });
    if (WebApp.CloudStorage) {
      // Сохраняем черновик при изменении
      WebApp.CloudStorage.setItem('inputDraft', text);
    }
  },

  syncFromCloud: async () => {
    if (!WebApp.CloudStorage || typeof WebApp.CloudStorage.getKeys !== 'function') {
      return Promise.resolve();
    }

    return new Promise((resolve) => {
      try {
        WebApp.CloudStorage.getKeys((err, keys) => {
          if (!err && keys) {
            if (keys.includes('activeTab')) {
              WebApp.CloudStorage.getItem('activeTab', (e, v) => {
                if (!e && v) set({ activeTab: v });
              });
            }
            if (keys.includes('inputDraft')) {
              WebApp.CloudStorage.getItem('inputDraft', (e, v) => {
                if (!e && v) set({ inputDraft: v });
              });
            }
          }
          resolve();
        });
      } catch(e) { resolve(); }
    });
  }
}));
