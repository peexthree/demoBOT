import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, TrendingUp, Calendar, Briefcase, ChevronRight, BarChart3, Settings } from 'lucide-react'

// Mock Telegram WebApp object
declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        close: () => void;
        MainButton: any;
        HapticFeedback: {
            impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
        };
      }
    }
  }
}

interface Lead {
  id: string;
  name: string;
  action: string;
  time: string;
  amount: string;
  status: 'new' | 'active' | 'completed';
}

function App() {
  const [activeTab, setActiveTab] = useState<'analytics' | 'crm'>('analytics')
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [leadsCount, setLeadsCount] = useState(0)
  const [leads, setLeads] = useState<Lead[]>([])

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready()
      window.Telegram.WebApp.expand()
    }

    fetch('https://eidos-bot.onrender.com/api/crm')
      .then(res => res.json())
      .then(data => {
          setTotalRevenue(data.totalRevenue || 0)
          setLeadsCount(data.leadsCount || 0)
          setLeads(data.leads || [])
      })
      .catch(err => console.error("Error fetching CRM data:", err))
  }, [])

  return (
    <div className="min-h-screen bg-[#000000] text-[#f5f5f7] overflow-x-hidden font-sans pb-10">

      {/* Hero Header with Video Background */}
      <div className="relative h-64 w-full overflow-hidden bg-[#1c1c1e]">
        {/* Background Video (Muted, AutoPlay, Looping) */}
        <video
           className="absolute inset-0 w-full h-full object-cover opacity-60"
           autoPlay
           loop
           muted
           playsInline
        >
          <source src="/demo.mp4" type="video/mp4" />
        </video>

        {/* Gradient Overlay for Text Readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#000000] via-[#000000]/60 to-transparent z-10"></div>

        {/* Header Content */}
        <div className="absolute top-6 left-6 right-6 z-20 flex justify-between items-start">
           <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white drop-shadow-md">Рабочее пространство</h1>
              <p className="text-sm text-gray-300 mt-1 font-medium drop-shadow-sm">Acme Corporation</p>
           </div>
           <div className="w-10 h-10 rounded-full bg-[#1c1c1e]/80 backdrop-blur-md flex items-center justify-center border border-white/20 shadow-sm cursor-pointer hover:bg-[#2c2c2e]/90 transition-colors">
              <Settings size={20} className="text-white" />
           </div>
        </div>

        {/* Bottom Status Indicator */}
        <div className="absolute bottom-6 left-6 z-20 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
            <span className="text-emerald-400 text-xs font-semibold tracking-widest uppercase">Live System</span>
        </div>
      </div>

      <div className="p-6 -mt-2">
        {/* Tabs - iOS Style */}
        <div className="flex bg-[#1c1c1e] rounded-[14px] p-1 mb-8 shadow-sm">
          <button
            onClick={() => {
                setActiveTab('analytics')
                window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light')
            }}
            className={`flex-1 py-2 text-[15px] font-medium rounded-[10px] transition-all duration-200 ${activeTab === 'analytics' ? 'bg-[#2c2c2e] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}
          >
            Сводка
          </button>
          <button
            onClick={() => {
                setActiveTab('crm')
                window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light')
            }}
            className={`flex-1 py-2 text-[15px] font-medium rounded-[10px] transition-all duration-200 ${activeTab === 'crm' ? 'bg-[#2c2c2e] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}
          >
            Клиенты (CRM)
          </button>
        </div>

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Main KPI */}
            <div className="bg-[#1c1c1e] rounded-[20px] p-6 border border-white/5 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-sm text-gray-400 font-medium">Общая выручка</span>
                    <span className="flex items-center text-xs font-semibold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
                        <TrendingUp size={12} className="mr-1" /> +14.2%
                    </span>
                </div>
                <div className="text-4xl font-semibold tracking-tight">₽ {totalRevenue.toLocaleString()}</div>
                <div className="mt-6 flex h-12 items-end gap-2">
                    {[40, 65, 45, 80, 55, 90, 75].map((height, i) => (
                        <div key={i} className="flex-1 bg-[#0a84ff] rounded-t-sm" style={{ height: `${height}%`, opacity: i === 6 ? 1 : 0.6 }}></div>
                    ))}
                </div>
                <div className="flex justify-between text-[10px] text-gray-500 mt-2 font-medium">
                    <span>ПН</span><span>ВТ</span><span>СР</span><span>ЧТ</span><span>ПТ</span><span>СБ</span><span>ВС</span>
                </div>
            </div>

            {/* Secondary KPIs */}
            <div className="grid grid-cols-2 gap-4">
              <StatBlock icon={<Users size={18} />} title="Новые лиды" value={leadsCount.toString()} />
              <StatBlock icon={<Calendar size={18} />} title="Конверсия" value="24.8%" />
            </div>

            {/* Action Card */}
            <div className="bg-gradient-to-br from-[#0a84ff] to-[#0056b3] rounded-[20px] p-6 text-white shadow-lg relative overflow-hidden mt-4">
                <div className="absolute right-0 bottom-0 opacity-10">
                    <BarChart3 size={120} />
                </div>
                <h3 className="text-lg font-semibold relative z-10 mb-1">Сгенерировать отчет</h3>
                <p className="text-sm text-blue-100 relative z-10 mb-4">Детальная AI-аналитика за месяц</p>
                <button
                    onClick={() => window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('medium')}
                    className="bg-white text-[#0a84ff] px-4 py-2 rounded-full text-sm font-semibold flex items-center shadow-sm hover:scale-105 transition-transform"
                >
                    Скачать PDF <ChevronRight size={16} className="ml-1" />
                </button>
            </div>
          </motion.div>
        )}

        {/* CRM Tab */}
        {activeTab === 'crm' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
          >
             <div className="flex justify-between items-center mb-4 px-1">
                 <h2 className="text-[17px] font-semibold">Активные сделки</h2>
                 <span className="text-sm text-[#0a84ff] font-medium cursor-pointer">Смотреть все</span>
             </div>

             <div className="bg-[#1c1c1e] rounded-[20px] overflow-hidden border border-white/5 shadow-sm divide-y divide-white/5">
                 {leads.length > 0 ? leads.map(lead => (
                     <LeadRow
                       key={lead.id}
                       name={lead.name}
                       action={lead.action}
                       time={lead.time}
                       amount={lead.amount}
                       status={lead.status}
                     />
                 )) : (
                     <div className="p-4 text-center text-sm text-gray-400">Нет активных сделок</div>
                 )}
             </div>

             <button
                onClick={() => window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light')}
                className="w-full mt-6 py-4 bg-[#2c2c2e] hover:bg-[#3c3c3e] border border-white/10 rounded-[14px] text-white font-medium flex items-center justify-center gap-2 transition-all shadow-sm"
             >
               <Briefcase size={18} />
               Создать рассылку (Broadcast)
             </button>
          </motion.div>
        )}
      </div>
    </div>
  )
}

function StatBlock({ icon, title, value }: { icon: React.ReactNode, title: string, value: string }) {
  return (
    <div className="bg-[#1c1c1e] p-5 rounded-[20px] border border-white/5 shadow-sm">
      <div className="w-8 h-8 rounded-full bg-[#2c2c2e] text-[#0a84ff] flex items-center justify-center mb-3">
        {icon}
      </div>
      <div className="text-2xl font-semibold tracking-tight mb-1">{value}</div>
      <div className="text-sm text-gray-400 font-medium">{title}</div>
    </div>
  )
}

function LeadRow({ name, action, time, amount, status }: { name: string, action: string, time: string, amount: string, status: 'new' | 'active' | 'completed' }) {
  const statusConfig = {
    new: { dot: 'bg-[#0a84ff]', bg: 'bg-[#0a84ff]/10', text: 'text-[#0a84ff]' },
    active: { dot: 'bg-amber-400', bg: 'bg-amber-400/10', text: 'text-amber-400' },
    completed: { dot: 'bg-emerald-400', bg: 'bg-emerald-400/10', text: 'text-emerald-400' }
  }

  return (
    <div
      onClick={() => window.Telegram?.WebApp?.HapticFeedback?.impactOccurred('light')}
      className="p-4 flex items-center gap-4 hover:bg-[#2c2c2e] transition-colors cursor-pointer"
    >
      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm ${statusConfig[status].bg} ${statusConfig[status].text}`}>
        {name.charAt(0)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-baseline mb-0.5">
          <h4 className="font-medium text-[15px] truncate pr-2">{name}</h4>
          <span className="text-[13px] font-medium text-white">{amount}</span>
        </div>
        <div className="flex justify-between items-center">
          <p className="text-[13px] text-gray-400 truncate pr-2">{action}</p>
          <span className="text-[12px] text-gray-500 whitespace-nowrap">{time}</span>
        </div>
      </div>
    </div>
  )
}

export default App
