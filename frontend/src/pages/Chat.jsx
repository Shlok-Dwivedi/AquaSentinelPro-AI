import React from 'react';

const Chat = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">AI Assistant</h2>
        <p className="text-slate-400 mt-1">Chat with the agent platform. Upload water photos or input parameters to initiate the multi-agent pipeline.</p>
      </div>

      <div className="h-[600px] bg-slate-900/60 rounded-2xl border border-slate-800 flex flex-col overflow-hidden">
        {/* Messages list (Dummy placeholder) */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto">
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-aqua-500/10 text-aqua-400 flex items-center justify-center font-bold">AS</div>
            <div className="max-w-[70%] p-4 rounded-2xl bg-slate-850 text-slate-300">
              Hello! I am AquaSentinel AI. I can analyze your water safety, recommend purifiers, suggest saving tips, and draft complaints. Try uploading an image or entering your water parameters!
            </div>
          </div>
        </div>

        {/* Input area */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80">
          <div className="flex gap-4 items-center">
            <input 
              type="text" 
              placeholder="Send message to AquaSentinel..." 
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-aqua-500 text-slate-100"
              disabled
            />
            <button 
              className="px-6 py-3 rounded-xl bg-aqua-600 font-semibold text-white text-sm opacity-50 cursor-not-allowed"
              disabled
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
