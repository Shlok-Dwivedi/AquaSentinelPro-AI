import React from 'react';

const Settings = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Settings</h2>
        <p className="text-slate-400 mt-1">Configure profile details and review agent memory records.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white">Profile Memory Configuration</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-450">Location / City</label>
              <input 
                type="text" 
                placeholder="e.g. Mumbai, India" 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none text-slate-100"
                disabled
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-450">Water Source</label>
              <input 
                type="text" 
                placeholder="e.g. Municipal Tap" 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none text-slate-100"
                disabled
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-450">Household Size</label>
              <input 
                type="number" 
                placeholder="e.g. 4" 
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none text-slate-100"
                disabled
              />
            </div>
          </div>
          <button 
            className="w-full py-3 bg-aqua-650 text-white font-bold rounded-xl text-sm opacity-50 cursor-not-allowed"
            disabled
          >
            Save Profile Settings
          </button>
        </div>

        <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-lg font-bold text-white">Platform Memory Trace</h3>
          <p className="text-sm text-slate-450">These attributes are automatically synced by the **Memory Agent** to contextualize future pipeline requests.</p>
          <div className="p-4 bg-slate-950 rounded-xl border border-slate-850">
            <pre className="text-xs text-slate-500 font-mono">
              {`{
  "location": "Unknown",
  "water_source": "Unknown",
  "purifier_type": "None",
  "historical_analyses_count": 0
}`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
