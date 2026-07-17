import React from 'react';

const Analysis = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Water Analysis</h2>
        <p className="text-slate-400 mt-1">Enter water test parameters manually to run policy standard verification.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form panel */}
        <div className="lg:col-span-2 p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white">Manual Parameters Form</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { label: 'pH Level', placeholder: 'e.g. 7.2', unit: 'pH' },
              { label: 'Total Dissolved Solids (TDS)', placeholder: 'e.g. 250', unit: 'mg/L' },
              { label: 'Turbidity', placeholder: 'e.g. 1.5', unit: 'NTU' },
              { label: 'Hardness', placeholder: 'e.g. 120', unit: 'mg/L' },
              { label: 'Chlorine', placeholder: 'e.g. 0.5', unit: 'mg/L' },
              { label: 'Fluoride', placeholder: 'e.g. 0.8', unit: 'mg/L' },
            ].map((field, idx) => (
              <div key={idx} className="space-y-2">
                <label className="text-xs font-semibold text-slate-450">{field.label}</label>
                <div className="relative">
                  <input 
                    type="number" 
                    placeholder={field.placeholder} 
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none text-slate-100 pr-12"
                    disabled
                  />
                  <span className="absolute right-4 top-3.5 text-xs text-slate-500 font-semibold">{field.unit}</span>
                </div>
              </div>
            ))}
          </div>

          <button 
            className="w-full py-3 bg-aqua-650 text-white font-bold rounded-xl text-sm opacity-50 cursor-not-allowed"
            disabled
          >
            Submit Parameters for Analysis
          </button>
        </div>

        {/* Info panel */}
        <div className="p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white">Analysis Information</h3>
          <div className="space-y-4 text-sm text-slate-450">
            <p>Enter values obtained from water quality test strips or digital sensors.</p>
            <p>Our platform evaluates values against **World Health Organization (WHO)** and **Bureau of Indian Standards (BIS)** recommendations.</p>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-850 space-y-2">
              <h4 className="text-xs font-bold text-slate-300">Target Ranges</h4>
              <ul className="text-xs space-y-1.5 font-medium text-slate-500">
                <li>pH: 6.5 - 8.5</li>
                <li>TDS: &lt; 500 mg/L</li>
                <li>Turbidity: &lt; 5 NTU</li>
                <li>Chlorine: &lt; 2.0 mg/L</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analysis;
