import React, { useState } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

const Analysis = ({ session }) => {
  const [formData, setFormData] = useState({
    ph: '',
    tds: '',
    turbidity: '',
    hardness: '',
    chlorine: '',
    fluoride: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResult(null);

    const data = new FormData();
    data.append('message', 'Please analyze these manual water parameters.');
    
    // Only append fields that are filled out
    Object.entries(formData).forEach(([key, val]) => {
      if (val.trim() !== '') {
        data.append(key, val);
      }
    });

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/message', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: data
      });

      if (!response.ok) throw new Error('Failed to analyze parameters');
      const resData = await response.json();
      setResult(resData.synthesized_response);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const parseInlineMarkdown = (text) => {
    const parts = text.split(/\*\*([^*]+)\*\*/g);
    return parts.map((part, idx) => {
      if (idx % 2 === 1) return <strong key={idx} className="font-bold text-white">{part}</strong>;
      return part;
    });
  };

  const renderSimpleMarkdown = (text) => {
    return text.split('\n').map((line, i) => {
      if (line.startsWith('## ')) return <h3 key={i} className="text-lg font-bold text-white mt-4 mb-2">{line.replace('## ', '')}</h3>;
      if (line.startsWith('### ')) return <h4 key={i} className="text-md font-bold text-aqua-400 mt-3 mb-1">{line.replace('### ', '')}</h4>;
      if (line.startsWith('* ') || line.startsWith('- ')) {
        return (
          <div key={i} className="flex items-start gap-2 text-sm text-slate-300 ml-2 my-1">
            <span className="text-aqua-500 font-bold text-xs mt-1">•</span>
            <span>{parseInlineMarkdown(line.substring(2))}</span>
          </div>
        );
      }
      return <p key={i} className="text-sm text-slate-300 my-1">{parseInlineMarkdown(line)}</p>;
    });
  };
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Water Analysis</h2>
        <p className="text-slate-400 mt-1">Enter water test parameters manually to run policy standard verification.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form panel */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 p-6 bg-slate-900/60 rounded-2xl border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white">Manual Parameters Form</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { id: 'ph', label: 'pH Level', placeholder: 'e.g. 7.2', unit: 'pH' },
              { id: 'tds', label: 'Total Dissolved Solids (TDS)', placeholder: 'e.g. 250', unit: 'mg/L' },
              { id: 'turbidity', label: 'Turbidity', placeholder: 'e.g. 1.5', unit: 'NTU' },
              { id: 'hardness', label: 'Hardness', placeholder: 'e.g. 120', unit: 'mg/L' },
              { id: 'chlorine', label: 'Chlorine', placeholder: 'e.g. 0.5', unit: 'mg/L' },
              { id: 'fluoride', label: 'Fluoride', placeholder: 'e.g. 0.8', unit: 'mg/L' },
            ].map((field, idx) => (
              <div key={idx} className="space-y-2">
                <label className="text-xs font-semibold text-slate-450">{field.label}</label>
                <div className="relative">
                  <input 
                    type="number" 
                    step="0.01"
                    value={formData[field.id]}
                    onChange={(e) => handleInputChange(field.id, e.target.value)}
                    placeholder={field.placeholder} 
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-aqua-500 text-slate-100 pr-12 transition-all"
                    disabled={isLoading}
                  />
                  <span className="absolute right-4 top-3.5 text-xs text-slate-500 font-semibold">{field.unit}</span>
                </div>
              </div>
            ))}
          </div>

          <button 
            type="submit"
            className={`w-full py-3 font-bold rounded-xl text-sm transition-all flex items-center justify-center gap-2 ${isLoading ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-aqua-600 hover:bg-aqua-500 text-white shadow-lg active:scale-95'}`}
            disabled={isLoading}
          >
            {isLoading && <Loader2 size={16} className="animate-spin" />}
            {isLoading ? 'Running Pipeline...' : 'Submit Parameters for Analysis'}
          </button>
        </form>

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

      {/* Results Section */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
          <AlertCircle size={20} />
          <p className="text-sm font-semibold">{error}</p>
        </div>
      )}

      {result && (
        <div className="p-6 bg-slate-900/40 rounded-2xl border border-aqua-500/30 shadow-[0_0_15px_rgba(34,211,238,0.1)] space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <CheckCircle2 className="text-emerald-400" size={24} />
            <h3 className="text-xl font-bold text-white">AI Analysis Complete</h3>
          </div>
          <div className="bg-slate-950/80 rounded-xl p-6 border border-slate-800">
            {renderSimpleMarkdown(result)}
          </div>
        </div>
      )}
    </div>
  );
};

export default Analysis;
