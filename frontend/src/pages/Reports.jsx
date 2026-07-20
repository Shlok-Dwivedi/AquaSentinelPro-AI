import React, { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Search, Calendar, Award, ShieldAlert, CheckCircle, Clock } from 'lucide-react';
import { API_ENDPOINTS } from '../config';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const token = localStorage.getItem('token');

  const fetchReports = async () => {
    setIsLoading(true);
    try {
const response = await fetch(API_ENDPOINTS.REPORTS, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error('Failed to load reports archive.');
      const data = await response.json();
      setReports(data);
      if (data.length > 0) {
        // Automatically select the latest report
        fetchReportDetails(data[0].id);
      } else {
        setSelectedReport(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchReportDetails = async (id) => {
    try {
      const response = await fetch(API_ENDPOINTS.REPORT_DETAIL(id), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const details = await response.json();
        setSelectedReport(details);
      }
    } catch (err) {
      console.error('Failed to load report details:', err);
    }
  };

  const handleDeleteReport = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this water assessment report? This will remove all exported files from the server.')) return;
    
    try {
      const response = await fetch(API_ENDPOINTS.REPORT_DETAIL(id), {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        setReports(prev => prev.filter(r => r.id !== id));
        if (selectedReport?.id === id) {
          setSelectedReport(null);
        }
        fetchReports();
      }
    } catch (err) {
      console.error('Failed to delete report:', err);
    }
  };

  const handleDownload = async (id, format) => {
    try {
      const url = API_ENDPOINTS.REPORT_DOWNLOAD(id, format);
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error('File download failed.');
      
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      const ext = format === 'pdf' ? 'pdf' : format === 'markdown' ? 'md' : 'json';
      link.download = `aquasentinel_report_${id}.${ext}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert(err.message);
    }
  };

  useEffect(() => {
    if (token) fetchReports();
  }, [token]);

  const filteredReports = reports.filter(r => 
    r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.summary.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-4rem)]">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Report Hub</h2>
        <p className="text-slate-400 mt-1">Export, search, and manage professional water safety compliance sheets (WHO / BIS IS 10500).</p>
      </div>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center bg-slate-900/40 rounded-2xl border border-slate-800">
          <Loader2 className="animate-spin text-aqua-400" size={32} />
        </div>
      ) : reports.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center bg-slate-900/40 rounded-2xl border border-slate-800 p-8 text-center select-none space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-slate-800/60 border border-slate-700 flex items-center justify-center text-slate-500 shadow-inner">
            <FileText size={28} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">No Reports Generated Yet</h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1">Initiate a multi-agent checklist review in the Assistant chat. Reports compile automatically upon completion.</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-5 gap-6 min-h-0">
          {/* Sidebar list search & filter */}
          <div className="lg:col-span-2 bg-slate-900/40 rounded-2xl border border-slate-800 p-4 flex flex-col min-h-0">
            <div className="relative mb-4">
              <Search className="absolute left-3 top-3.5 text-slate-500" size={16} />
              <input 
                type="text" 
                placeholder="Search report archive..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-xs focus:outline-none focus:border-aqua-500 text-slate-200 placeholder-slate-600"
              />
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {filteredReports.map((r) => (
                <div 
                  key={r.id}
                  onClick={() => fetchReportDetails(r.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition flex justify-between items-start gap-4 ${
                    selectedReport?.id === r.id 
                      ? 'border-aqua-500/40 bg-aqua-500/5' 
                      : 'border-slate-800/80 bg-slate-900/20 hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-1 min-w-0">
                    <h4 className="text-sm font-semibold text-slate-200 truncate">{r.title}</h4>
                    <p className="text-xs text-slate-500 flex items-center gap-1.5 font-medium">
                      <Calendar size={12} />
                      {new Date(r.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button 
                    onClick={(e) => handleDeleteReport(r.id, e)}
                    className="p-2 text-slate-500 hover:text-red-400 hover:bg-slate-800/30 rounded-lg transition"
                    title="Delete report"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Active Preview Panel */}
          <div className="lg:col-span-3 bg-slate-900/40 rounded-2xl border border-slate-800 p-6 flex flex-col min-h-0">
            {selectedReport ? (
              <div className="flex-1 flex flex-col min-h-0 space-y-6">
                <div className="flex justify-between items-start border-b border-slate-800 pb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white tracking-wide">{selectedReport.title}</h3>
                    <p className="text-xs text-slate-500 mt-1">Generated: {new Date(selectedReport.created_at).toLocaleString()}</p>
                  </div>
                  
                  {/* Download selectors */}
                  <div className="flex gap-2">
                    <button 
                      onClick={() => handleDownload(selectedReport.id, 'pdf')}
                      className="px-3.5 py-2 bg-aqua-600 hover:bg-aqua-500 text-white text-xs font-semibold rounded-lg shadow-sm hover:shadow-lg transition flex items-center gap-1.5"
                    >
                      <Download size={12} /> PDF
                    </button>
                    <button 
                      onClick={() => handleDownload(selectedReport.id, 'markdown')}
                      className="px-3 py-2 bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold rounded-lg transition flex items-center gap-1.5"
                    >
                      <Download size={12} /> MD
                    </button>
                    <button 
                      onClick={() => handleDownload(selectedReport.id, 'json')}
                      className="px-3 py-2 bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold rounded-lg transition flex items-center gap-1.5"
                    >
                      <Download size={12} /> JSON
                    </button>
                  </div>
                </div>

                {/* Report Content Cards */}
                <div className="flex-1 overflow-y-auto space-y-6 pr-1">
                  <div className="bg-slate-950/40 rounded-xl border border-slate-850 p-4 space-y-2">
                    <h4 className="text-xs font-bold text-aqua-400 uppercase tracking-wider">Executive Summary</h4>
                    <p className="text-sm text-slate-300 leading-relaxed font-medium">{selectedReport.summary}</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-950/40 rounded-xl border border-slate-850 p-4 flex items-center gap-3">
                      <Award className="text-aqua-400" size={24} />
                      <div>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Uptime Version</p>
                        <p className="text-sm font-bold text-slate-200">v1.0-milestone5</p>
                      </div>
                    </div>
                    <div className="bg-slate-950/40 rounded-xl border border-slate-850 p-4 flex items-center gap-3">
                      <Clock className="text-aqua-400" size={24} />
                      <div>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Storage Reference</p>
                        <p className="text-xs font-semibold text-slate-300 truncate max-w-[160px]">{selectedReport.id}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
                Select a report from the list to preview details.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

import { Loader2 } from 'lucide-react';
export default Reports;
