import React, { useState } from 'react';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';

const Register = ({ onRegisterSuccess, switchToLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    setSuccessMessage('');
    setIsLoading(true);

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
      });

      if (signUpError) throw signUpError;
      
      if (data?.session) {
        // Email confirmation is disabled in Supabase, logged in immediately
        onRegisterSuccess(data.session);
      } else {
        // Email confirmation is enabled
        setSuccessMessage('A confirmation link has been sent to your email. Please check your inbox to verify your account.');
      }
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
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Create Account</h2>
          <p className="text-slate-400 text-xs leading-relaxed">Sign up to analyze water quality, upload source photos, and draft complaints.</p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs flex items-center gap-2">
            <AlertCircle size={14} className="flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successMessage && (
          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-xs flex items-center gap-2">
            <Sparkles size={14} className="flex-shrink-0" />
            <span>{successMessage}</span>
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
              placeholder="Create secure password" 
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
                <Sparkles size={16} /> Register
              </>
            )}
          </button>
        </form>

        <div className="relative flex items-center justify-center my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800"></div>
          </div>
          <div className="relative bg-[#0d1624] px-4 text-xs font-medium text-slate-500 uppercase">
            Or continue with
          </div>
        </div>

        <button 
          onClick={async () => {
            try {
              const { error } = await supabase.auth.signInWithOAuth({ 
                provider: 'google',
                options: { redirectTo: window.location.origin }
              });
              if (error) throw error;
            } catch (err) {
              setError(err.message);
            }
          }}
          className="w-full py-3 bg-slate-950 hover:bg-slate-800 text-slate-200 rounded-xl text-sm font-semibold border border-slate-800 transition flex items-center justify-center gap-3"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          Google
        </button>

        <div className="text-center pt-2">
          <button 
            onClick={switchToLogin}
            className="text-xs text-slate-400 hover:text-white transition font-medium"
          >
            Already have an account? <span className="text-aqua-400 font-bold hover:underline">Log in here</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Register;
