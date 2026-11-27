import React, { useState } from 'react';
import { 
  Stethoscope, 
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  BrainCircuit, 
  FileCheck2,
  Lock,
  Mail
} from 'lucide-react';
import { api } from '../api';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('student@demo.com');
  const [password, setPassword] = useState('demo123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.login(email, password);
      localStorage.setItem('gapfinder_token', res.token);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.demoLogin();
      localStorage.setItem('gapfinder_token', res.token);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-rose-500 shadow-xl shadow-indigo-500/20 mb-4">
          <Stethoscope className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">
          GapFinder <span className="text-indigo-400">AI</span>
        </h2>
        <p className="mt-2 text-sm text-slate-400 max-w-sm mx-auto">
          The AI-Powered "Study Doctor" — Ingest course materials, diagnose knowledge gaps, and follow an adaptive revision plan.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-slate-900/90 py-8 px-6 shadow-2xl border border-slate-800 rounded-2xl sm:px-10 backdrop-blur-xl">
          
          {/* Quick Demo Access Banner */}
          <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-indigo-500/30">
            <div className="flex items-center space-x-2 text-indigo-300 font-semibold text-xs mb-1">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Instant Evaluator Access</span>
            </div>
            <p className="text-[11px] text-slate-300 mb-3">
              Pre-loaded with CS301 Operating Systems course syllabus, chapter notes, past exam questions, and baseline diagnostic attempts.
            </p>
            <button
              type="button"
              onClick={handleDemoLogin}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/30 transition"
            >
              <span>{loading ? 'Initializing Demo...' : 'Log In with Demo Account (1-Click)'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-800" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-slate-900 px-3 text-slate-500 font-semibold">Or enter credentials</span>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
              {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleLogin}>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="block w-full pl-9 pr-3 py-2 border border-slate-700 rounded-lg bg-slate-800/80 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  placeholder="student@demo.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="block w-full pl-9 pr-3 py-2 border border-slate-700 rounded-lg bg-slate-800/80 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  placeholder="demo123"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-medium text-xs transition"
            >
              Sign In
            </button>
          </form>

          {/* Core Guarantees Badges */}
          <div className="mt-6 pt-5 border-t border-slate-800 grid grid-cols-2 gap-2 text-[10px] text-slate-400">
            <div className="flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Two-Stage Grounded RAG</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
              <span>Adaptive Study Diagnosis</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <FileCheck2 className="w-3.5 h-3.5 text-purple-400" />
              <span>Exact Source Citations</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <Stethoscope className="w-3.5 h-3.5 text-rose-400" />
              <span>Weak/Med/Strong Tiers</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
