import React from 'react';
import { 
  LayoutDashboard, 
  MessageSquare, 
  TrendingUp, 
  FileText, 
  AlertOctagon, 
  Settings as SettingsIcon,
  Droplet,
  LogOut
} from 'lucide-react';

const Sidebar = ({ currentPage, setCurrentPage, currentUser, onLogout }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
    { id: 'analysis', label: 'Water Analysis', icon: TrendingUp },
    { id: 'reports', label: 'Report Hub', icon: FileText },
    { id: 'complaints', label: 'Complaints', icon: AlertOctagon },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  const getInitials = (name) => {
    if (!name) return 'US';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="bg-aqua-500/10 p-2 rounded-lg text-aqua-400">
          <Droplet size={24} className="animate-pulse" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-outfit">AquaSentinel</h1>
          <p className="text-xs text-slate-400 font-medium">Agentic Platform</p>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive 
                  ? 'bg-aqua-600 text-white shadow-lg shadow-aqua-600/20' 
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Profile Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex flex-col gap-3">
        <div className="flex items-center gap-3 p-2">
          <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-aqua-400 text-sm">
            {getInitials(currentUser?.name)}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-sm font-semibold text-white truncate">{currentUser?.name || 'User Profile'}</h4>
            <p className="text-xs text-slate-500 truncate">{currentUser?.email || 'aquasentinel-ai'}</p>
          </div>
        </div>
        
        <button 
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-red-500/10 hover:text-red-400 text-slate-400 rounded-xl text-xs font-semibold border border-slate-800 transition"
        >
          <LogOut size={14} /> Log Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
