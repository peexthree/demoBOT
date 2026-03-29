import { useEffect, useState } from 'react'
import WebApp from '@twa-dev/sdk'
import { useAppStore } from './store'
import { DashboardScreen } from './screens/Dashboard'

function App() {
  const { setUserId, setActiveTab, syncFromCloud, activeTab, userId } = useAppStore()
  const [isInitializing, setIsInitializing] = useState(true)

  useEffect(() => {
    const initApp = async () => {
      // Имитация загрузки
      await new Promise(resolve => setTimeout(resolve, 800));

      const user = WebApp.initDataUnsafe?.user;
      if (user) {
        setUserId(user.id);
      } else {
        // Fallback for local dev
        setUserId(123456789);
      }

      try {
        await syncFromCloud();
      } catch (e) {
        console.error("Cloud sync failed:", e);
      }

      // Снимаем лоадер и сообщаем Telegram, что мы готовы
      setIsInitializing(false);
      WebApp.ready();

      if (WebApp.HapticFeedback) {
        WebApp.HapticFeedback.notificationOccurred('success');
      }
    };

    initApp();
  }, []);

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-eidos-bg flex-col gap-4">
        <div className="w-16 h-16 border-4 border-eidos-gray/20 border-t-eidos-cyan rounded-full animate-spin"></div>
        <div className="text-eidos-cyan font-mono animate-pulse tracking-widest text-sm">ИНИЦИАЛИЗАЦИЯ ИИ...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-eidos-bg text-white pb-20 relative">
      {/* Главный Экран */}
      {activeTab === 'dashboard' && <DashboardScreen />}

      {/* Заглушки для других табов */}
      {activeTab === 'profile' && (
        <div className="p-4">
          <h1 className="text-2xl font-bold font-mono text-eidos-cyan">Профиль Бизнеса</h1>
          <p className="text-sm text-gray-400 mt-2">Здесь будет форма настройки Tone of Voice и ЦА.</p>
        </div>
      )}

      {/* Навигация (Bottom Bar) */}
      <div className="fixed bottom-0 left-0 w-full h-16 bg-black/80 backdrop-blur-lg border-t border-white/10 flex justify-around items-center px-4 z-50">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex flex-col items-center gap-1 ${activeTab === 'dashboard' ? 'text-eidos-cyan' : 'text-gray-500'}`}
        >
          <span className="text-xl">⚡</span>
          <span className="text-[10px] font-mono">ТЕРМИНАЛ</span>
        </button>
        <button
          onClick={() => setActiveTab('profile')}
          className={`flex flex-col items-center gap-1 ${activeTab === 'profile' ? 'text-eidos-cyan' : 'text-gray-500'}`}
        >
          <span className="text-xl">👤</span>
          <span className="text-[10px] font-mono">ПРОФИЛЬ</span>
        </button>
      </div>
    </div>
  )
}

export default App
