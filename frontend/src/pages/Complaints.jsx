import React from 'react';

const Complaints = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Complaints</h2>
        <p className="text-slate-400 mt-1">Review official complaint drafts created by the Complaint Agent for municipal portal reporting.</p>
      </div>

      <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-6">
        <h3 className="text-lg font-bold text-white">Active Complaint Drafts</h3>
        <div className="space-y-4">
          <div className="p-5 bg-slate-950 rounded-xl border border-slate-850 space-y-3">
            <div className="flex justify-between items-start gap-4">
              <div>
                <span className="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">Critical Severity</span>
                <h4 className="text-base font-bold text-white mt-2">Urgent: Contaminated Drinking Water Supply in Area</h4>
                <p className="text-xs text-slate-500">Target: Municipal Water and Sanitation Division</p>
              </div>
              <button 
                className="px-4 py-2 bg-aqua-600/80 text-white text-xs font-bold rounded-lg hover:bg-aqua-600 transition"
                disabled
              >
                Submit Draft
              </button>
            </div>
            <div className="p-4 bg-slate-900 rounded-lg border border-slate-800">
              <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap">
                {`Respected Sir/Madam,

I am writing to report visible brown discoloration and foam in our tap water supply. Please look into this immediately.

Sincerely,
Resident`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Complaints;
