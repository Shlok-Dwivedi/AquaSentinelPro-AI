import React, { useState, useEffect } from 'react';
import { Loader2, FileText, CheckCircle } from 'lucide-react';

const Complaints = ({ session }) => {
  const [complaints, setComplaints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  const token = session?.access_token;

  const fetchComplaints = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/complaints`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error('Failed to load complaints.');
      const data = await response.json();
      setComplaints(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitComplaint = async (id) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/complaints/submit/${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        fetchComplaints(); // refresh the list
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (token) fetchComplaints();
  }, [token]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Complaints</h2>
        <p className="text-slate-400 mt-1">Review official complaint drafts created by the Complaint Agent for municipal portal reporting.</p>
      </div>

      <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-6">
        <h3 className="text-lg font-bold text-white">Active Complaint Drafts</h3>
        
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="animate-spin text-aqua-400" size={32} />
          </div>
        ) : error ? (
          <div className="p-4 rounded-xl bg-rose-500/10 text-rose-400 text-sm font-semibold border border-rose-500/20">{error}</div>
        ) : complaints.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-10 text-center space-y-3 bg-slate-950/40 rounded-xl border border-dashed border-slate-800">
            <div className="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center text-slate-600">
              <FileText size={20} />
            </div>
            <p className="text-slate-500 text-sm font-medium">No complaints drafted yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {complaints.map(c => (
              <div key={c.id} className="p-5 bg-slate-950 rounded-xl border border-slate-850 space-y-3">
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                      c.severity === 'Critical' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 
                      c.severity === 'High' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                      'bg-sky-500/10 text-sky-400 border-sky-500/20'
                    }`}>
                      {c.severity} Severity
                    </span>
                    <h4 className="text-base font-bold text-white mt-2">{c.subject}</h4>
                    <p className="text-xs text-slate-500 mt-1">Target: {c.department} • {new Date(c.created_at).toLocaleDateString()}</p>
                  </div>
                  {c.status === 'Draft' ? (
                    <button 
                      onClick={() => handleSubmitComplaint(c.id)}
                      className="px-4 py-2 bg-aqua-600 hover:bg-aqua-500 text-white text-xs font-bold rounded-lg shadow-lg active:scale-95 transition"
                    >
                      Submit Draft
                    </button>
                  ) : (
                    <div className="px-3 py-1.5 bg-emerald-500/10 text-emerald-400 text-xs font-bold rounded-lg border border-emerald-500/20 flex items-center gap-1.5">
                      <CheckCircle size={14} /> Submitted
                    </div>
                  )}
                </div>
                <div className="p-4 bg-slate-900 rounded-lg border border-slate-800">
                  <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap font-medium">{c.body}</pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Complaints;
