import React from 'react';
import { 
  Stethoscope, 
  Activity, 
  BookOpen, 
  CheckSquare, 
  Calendar, 
  UploadCloud, 
  MessageSquare, 
  User, 
  LogOut,
  Sparkles
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, user, onLogout, onToggleChat }) {
  const navItems = [
    { id: 'dashboard', label: 'Progress Dashboard', icon: Activity },
    { id: 'gap-report', label: 'Gap Report (Diagnosis)', icon: Stethoscope, highlight: true },
    { id: 'quiz', label: 'Diagnostic Quiz', icon: CheckSquare },
    { id: 'revision-plan', label: 'Adaptive Revision Plan', icon: Calendar },
    { id: 'topic-map', label: 'Syllabus Map', icon: BookOpen },
    { id: 'upload', label: 'Materials Upload', icon: UploadCloud },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Study Doctor Badge */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-rose-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Stethoscope className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg text-white tracking-tight">GapFinder <span className="text-indigo-400">AI</span></span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  Study Doctor
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Diagnostic Grounded Learning Engine</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : item.highlight
                      ? 'text-rose-300 hover:text-white hover:bg-rose-500/10 border border-rose-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                  {item.highlight && !isActive && (
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Action: Tutor Chat & User Menu */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onToggleChat}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition shadow-sm"
              title="Open Grounded Study Assistant"
            >
              <MessageSquare className="w-4 h-4 text-indigo-400" />
              <span className="hidden sm:inline">Grounded Tutor</span>
              <Sparkles className="w-3 h-3 text-amber-400" />
            </button>

            {user ? (
              <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
                <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-indigo-400">
                  {user.name.charAt(0)}
                </div>
                <div className="hidden lg:block text-left">
                  <div className="text-xs font-medium text-slate-200">{user.name}</div>
                  <div className="text-[10px] text-slate-400">{user.email}</div>
                </div>
                <button
                  onClick={onLogout}
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : null}
          </div>

        </div>
      </div>
    </header>
  );
}
