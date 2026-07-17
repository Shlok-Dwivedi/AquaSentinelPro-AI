import React, { useState, useEffect } from 'react';
import { 
  Droplet, 
  ShieldAlert, 
  FileCheck, 
  Activity 
} from 'lucide-react';

const Dashboard = () => {
  const [backendStatus, setBackendStatus] = useState('loading'); // 'loading', 'connected', 'failed'

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error('Network response was not ok');
      })
      .then((data) => {
        if (data.status === 'healthy') {
          setBackendStatus('connected');
        } else {
          setBackendStatus('failed');
        }
      })
      .catch(() => {
        setBackendStatus('failed');
      });
  }, []);

  return (
    <div className="space-y-8">
      {/* Header & Health Check */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Main Dashboard</h2>
          <p className="text-slate-400 mt-1">Real-time water quality monitoring and multi-agent systems overview.</p>
        </div>
        
        {/* Connection status banner */}
        <div>
          {backendStatus === 'connected' && (
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
              Backend Connected ✅
            </span>
          )}
          {backendStatus === 'loading' && (
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
              Connecting to Backend...
            </span>
          )}
          {backendStatus === 'failed' && (
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
              Backend Disconnected ❌
            </span>
          )}
        </div>
      </div>

      {/* Grid of Metric Cards (Dummy Layout) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Overall Water Score', value: '85 / 100', change: 'Optimal (WHO standards)', icon: Droplet, color: 'text-sky-400 bg-sky-500/5 border-sky-500/10' },
          { label: 'Pending Complaints', value: '1 Active', change: 'Registered Draft', icon: ShieldAlert, color: 'text-amber-400 bg-amber-500/5 border-amber-500/10' },
          { label: 'Generated Reports', value: '3 Total', change: 'PDF downloads ready', icon: FileCheck, color: 'text-emerald-400 bg-emerald-500/5 border-emerald-500/10' },
          { label: 'Active Pipeline Nodes', value: '12 Active', change: 'LangGraph Compiled', icon: Activity, color: 'text-violet-400 bg-violet-500/5 border-violet-500/10' },
        ].map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className={`p-6 rounded-2xl border ${card.color} backdrop-blur-sm`}>
              <div className="flex justify-between items-start">
                <span className="text-sm font-semibold text-slate-400">{card.label}</span>
                <div className="p-2 rounded-lg bg-slate-800/80">
                  <Icon size={18} />
                </div>
              </div>
              <div className="mt-4">
                <h3 className="text-2xl font-extrabold text-white">{card.value}</h3>
                <p className="text-xs text-slate-400 mt-1 font-medium">{card.change}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Visual Workspace placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 bg-slate-900/60 rounded-2xl border border-slate-800">
          <h3 className="text-lg font-bold text-white mb-2">Water Quality Logs (Mock Chart)</h3>
          <div className="h-64 rounded-xl bg-slate-950 border border-slate-850 flex items-center justify-center text-slate-600 font-medium">
            Timeline Chart (Pending Data)
          </div>
        </div>
        <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800">
          <h3 className="text-lg font-bold text-white mb-4">SDG 6 Impact Track</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Drinking Safety Target</span>
                <span>85%</span>
              </div>
              <div className="w-full h-2 bg-slate-950 rounded-full">
                <div className="h-2 bg-sky-500 rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Conservation Actions</span>
                <span>60%</span>
              </div>
              <div className="w-full h-2 bg-slate-950 rounded-full">
                <div className="h-2 bg-emerald-500 rounded-full" style={{ width: '60%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Municipal Responses</span>
                <span>40%</span>
              </div>
              <div className="w-full h-2 bg-slate-950 rounded-full">
                <div className="h-2 bg-violet-500 rounded-full" style={{ width: '40%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
