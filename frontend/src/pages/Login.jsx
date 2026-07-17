import React, { useState } from 'react';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';

const Login = ({ onLoginSuccess, switchToRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Authentication failed');
      }

      const data = await response.json();
      onLoginSuccess(data.access_token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-6 select-none">
      <div className="w-full max-w-md bg-slate-900/60 rounded-3xl border border-slate-800 p-8 space-y-6 backdrop-blur-md shadow-2xl">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-aqua-500/10 text-aqua-400 border border-aqua-500/20 flex items-center justify-center font-bold text-lg mx-auto shadow-inner">
            AS
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Welcome to AquaSentinel</h2>
          <p className="text-slate-400 text-xs leading-relaxed">Log in to access your dashboard, monitor water parameters, and generate safety compliance reports.</p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs flex items-center gap-2">
            <AlertCircle size={14} className="flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Email Address</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com" 
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-aqua-500 text-slate-100 placeholder-slate-600 transition"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-400">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password" 
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-aqua-500 text-slate-100 placeholder-slate-600 transition"
              required
            />
          </div>

          <button 
            type="submit"
            className="w-full py-3.5 bg-aqua-600 hover:bg-aqua-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-aqua-600/15 hover:shadow-aqua-500/20 active:scale-[0.98] transition flex items-center justify-center gap-2"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <Sparkles size={16} /> Log In
              </>
            )}
          </button>
        </form>

        <div className="text-center">
          <button 
            onClick={switchToRegister}
            className="text-xs text-slate-400 hover:text-white transition font-medium"
          >
            Don't have an account? <span className="text-aqua-400 font-bold hover:underline">Register here</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
