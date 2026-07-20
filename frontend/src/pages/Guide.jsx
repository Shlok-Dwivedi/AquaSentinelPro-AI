import React from 'react';
import { ArrowRight, MessageSquare, Image as ImageIcon, FileText, CheckCircle2 } from 'lucide-react';

const Guide = ({ setCurrentPage }) => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto py-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-extrabold text-white tracking-tight">Welcome to AquaSentinel-AI</h1>
        <p className="text-lg text-slate-400">Your autonomous water safety monitoring platform.</p>
      </div>

      <div className="bg-slate-900/60 rounded-2xl border border-slate-800 p-8 space-y-8 shadow-xl backdrop-blur-sm">
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-aqua-400">How It Works</h2>
          <p className="text-slate-300 leading-relaxed">
            Unlike traditional apps, AquaSentinel is powered entirely by an AI Agent Pipeline. 
            There are no manual forms to fill out. Instead, you interact with the system via the <strong>AI Assistant Chat</strong>.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-slate-950/80 rounded-xl border border-slate-800 space-y-4 shadow-md">
            <div className="w-12 h-12 rounded-lg bg-aqua-500/10 flex items-center justify-center text-aqua-400 border border-aqua-500/20">
              <MessageSquare size={24} />
            </div>
            <h3 className="text-lg font-bold text-white">1. Enter Parameters</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Open the Chat tab and type your water readings naturally. For example: <br/>
              <span className="inline-block mt-2 px-3 py-1.5 bg-slate-900 rounded-lg text-aqua-300 font-mono text-xs border border-slate-800">
                "My TDS is 750 and pH is 8.2"
              </span>
            </p>
          </div>

          <div className="p-6 bg-slate-950/80 rounded-xl border border-slate-800 space-y-4 shadow-md">
            <div className="w-12 h-12 rounded-lg bg-violet-500/10 flex items-center justify-center text-violet-400 border border-violet-500/20">
              <ImageIcon size={24} />
            </div>
            <h3 className="text-lg font-bold text-white">2. Upload Images</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Use the image upload button in the Chat to submit photos of your water. The Vision Agent will scan it for visible contaminants like algae or discoloration.
            </p>
          </div>

          <div className="p-6 bg-slate-950/80 rounded-xl border border-slate-800 space-y-4 shadow-md">
            <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 size={24} />
            </div>
            <h3 className="text-lg font-bold text-white">3. Autonomous Analysis</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              The AI automatically cross-references your inputs against WHO and BIS safety standards to determine risk levels and compliance.
            </p>
          </div>

          <div className="p-6 bg-slate-950/80 rounded-xl border border-slate-800 space-y-4 shadow-md">
            <div className="w-12 h-12 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400 border border-sky-500/20">
              <FileText size={24} />
            </div>
            <h3 className="text-lg font-bold text-white">4. Export Reports</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Once analysis completes, a comprehensive Executive Summary report is instantly generated. You can download it as PDF or Markdown from the Reports tab!
            </p>
          </div>
        </div>

        <div className="pt-6 flex justify-center border-t border-slate-800">
          <button 
            onClick={() => setCurrentPage('chat')}
            className="flex items-center gap-2 px-8 py-4 bg-aqua-600 hover:bg-aqua-500 text-white font-bold rounded-xl shadow-lg hover:shadow-aqua-600/25 transition-all active:scale-95"
          >
            Start Analyzing <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Guide;
