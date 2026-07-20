import React, { useState, useEffect } from 'react';
import { 
  Droplet, 
  ShieldAlert, 
  FileCheck, 
  Activity, 
  Calendar, 
  Eye, 
  ShieldCheck, 
  Loader2, 
  FileText, 
  TrendingUp 
} from 'lucide-react';
import { API_ENDPOINTS } from '../config';

const Dashboard = () => {
  const [backendStatus, setBackendStatus] = useState('loading'); // 'loading', 'connected', 'failed'
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const token = localStorage.getItem('token');

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.DASHBOARD, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // 1. Health check connection status
    fetch(API_ENDPOINTS.HEALTH)
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error('Network offline');
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

    // 2. Fetch user analytics
    if (token) {
      fetchDashboardData();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const stats = dashboardData?.stats || {
    total_analyses: 0,
    reports_generated: 0,
    images_analyzed: 0,
    average_water_score: 100.0
  };

  const getSafetyColor = (score) => {
    if (score >= 85) return 'text-emerald-400';
    if (score >= 50) return 'text-amber-400';
    return 'text-rose-400';
  };

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
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-lg shadow-emerald-500/5">
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

      {isLoading ? (
        <div className="h-64 flex items-center justify-center bg-slate-900/40 rounded-2xl border border-slate-800">
          <Loader2 className="animate-spin text-aqua-400" size={32} />
        </div>
      ) : (
        <>
          {/* Live Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Avg Water Score', value: `${stats.average_water_score.toFixed(1)} / 100`, change: 'Based on your chemical checks', icon: Droplet, color: 'text-sky-400 bg-sky-500/5 border-sky-500/10 shadow-sky-500/5' },
              { label: 'Analyses Logged', value: `${stats.total_analyses} Checks`, change: 'Parameter runs executed', icon: Activity, color: 'text-violet-400 bg-violet-500/5 border-violet-500/10 shadow-violet-500/5' },
              { label: 'Reports Generated', value: `${stats.reports_generated} PDF/MD`, change: 'Archives exported successfully', icon: FileCheck, color: 'text-emerald-400 bg-emerald-500/5 border-emerald-500/10 shadow-emerald-500/5' },
              { label: 'Images Analyzed', value: `${stats.images_analyzed} Photos`, change: 'Contaminants scanned offline', icon: Eye, color: 'text-amber-400 bg-amber-500/5 border-amber-500/10 shadow-amber-500/5' },
            ].map((card, idx) => {
              const Icon = card.icon;
              return (
                <div key={idx} className={`p-6 rounded-2xl border ${card.color} backdrop-blur-sm shadow-md`}>
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-semibold text-slate-400">{card.label}</span>
                    <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/50">
                      <Icon size={18} />
                    </div>
                  </div>
                  <div className="mt-4">
                    <h3 className="text-2xl font-extrabold text-white">{card.value}</h3>
                    <p className="text-xs text-slate-500 mt-1 font-medium">{card.change}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Activity Logs Split view */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Recent activities feed */}
            <div className="lg:col-span-3 bg-slate-900/40 rounded-2xl border border-slate-800 p-6 flex flex-col min-h-0 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-white mb-4 tracking-wide flex items-center gap-2">
                <TrendingUp size={18} className="text-aqua-400" /> Recent Activities
              </h3>
              
              {(!dashboardData?.recent_activity || dashboardData.recent_activity.length === 0) ? (
                <div className="flex-1 flex items-center justify-center p-8 text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
                  No recent safety activities recorded. Start a chat.
                </div>
              ) : (
                <div className="space-y-4 max-h-[350px] overflow-y-auto pr-1">
                  {dashboardData.recent_activity.map((act, idx) => (
                    <div key={idx} className="flex gap-4 p-3 bg-slate-950/30 rounded-xl border border-slate-900">
                      <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-xs font-bold text-aqua-400 flex-shrink-0">
                        {act.type === 'report' ? 'RP' : act.type === 'vision' ? 'VS' : 'AN'}
                      </div>
                      <div className="min-w-0 flex-1 space-y-0.5">
                        <p className="text-xs text-slate-200 leading-relaxed font-semibold">{act.message}</p>
                        <p className="text-[10px] text-slate-500 font-medium">
                          {new Date(act.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Analysis history summary list */}
            <div className="lg:col-span-2 bg-slate-900/40 rounded-2xl border border-slate-800 p-6 flex flex-col min-h-0 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-white mb-4 tracking-wide flex items-center gap-2">
                <Droplet size={18} className="text-sky-400" /> Previous Analyses
              </h3>
              
              {(!dashboardData?.previous_analyses || dashboardData.previous_analyses.length === 0) ? (
                <div className="flex-1 flex items-center justify-center p-8 text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
                  No chemical logs saved yet.
                </div>
              ) : (
                <div className="space-y-3 overflow-y-auto max-h-[350px] pr-1">
                  {dashboardData.previous_analyses.map((an) => (
                    <div key={an.log_id} className="p-3 bg-slate-950/30 rounded-xl border border-slate-900 flex justify-between items-center">
                      <div className="space-y-0.5 min-w-0">
                        <h4 className="text-xs font-bold text-slate-300 truncate">Score: <span className={getSafetyColor(an.score)}>{an.score} / 100</span></h4>
                        <p className="text-[10px] text-slate-500 font-medium">{new Date(an.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="text-[10px] bg-slate-900 border border-slate-850 px-2 py-1.5 rounded-lg text-slate-400 font-semibold uppercase tracking-wider">
                        {an.safety}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
