import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  BookOpen, 
  FileText, 
  ArrowRight, 
  Stethoscope, 
  Calendar,
  Sparkles,
  Award
} from 'lucide-react';
import { api } from '../api';

export default function Dashboard({ onNavigateToGapReport, onNavigateToQuiz, onNavigateToPlan }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardMetrics()
      .then(setMetrics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Hero Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>AI Diagnostic Engine Active</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Study Doctor Progress Overview
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Welcome back, Alex. Your course materials have been ingested, mapped to exam weightage, and diagnosed. Track your attempt-over-attempt score evolution and targeted revision below.
          </p>

          <div className="pt-4 flex flex-wrap gap-3">
            <button
              onClick={onNavigateToGapReport}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs shadow-lg shadow-rose-600/30 transition"
            >
              <Stethoscope className="w-4 h-4" />
              <span>Inspect Gap Report (Diagnosis)</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={onNavigateToPlan}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs transition"
            >
              <Calendar className="w-4 h-4 text-indigo-400" />
              <span>View Revision Timetable</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Diagnostic Accuracy</span>
            <Activity className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {metrics ? `${metrics.average_accuracy}%` : '--'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Across all grounded tests</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Quizzes Completed</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">
            {metrics ? metrics.quizzes_taken : '--'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Grounded diagnostic runs</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Syllabus Modules</span>
            <BookOpen className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">
            {metrics ? metrics.total_topics : '--'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">With past exam weightages</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Indexed Files</span>
            <FileText className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-extrabold text-purple-400">
            {metrics ? metrics.total_documents : '--'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Syllabus, Notes & Past Papers</div>
        </div>
      </div>

      {/* Two Column Layout: Score Trend Chart & Tier Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Attempt-over-Attempt Trend Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              <span>Attempt-over-Attempt Score History</span>
            </h2>
            <span className="text-[11px] text-slate-400">Tracks performance evolution</span>
          </div>

          {loading ? (
            <div className="h-56 flex items-center justify-center text-xs text-slate-500">Loading attempt trends...</div>
          ) : !metrics?.recent_attempts || metrics.recent_attempts.length === 0 ? (
            <div className="h-56 flex items-center justify-center text-xs text-slate-500">No diagnostic attempts recorded yet.</div>
          ) : (
            <div className="space-y-4 pt-2">
              <div className="h-48 flex items-end justify-between gap-3 px-4 pb-2 border-b border-slate-800">
                {metrics.recent_attempts.map((att, idx) => {
                  const heightPct = Math.max(15, att.accuracy_pct);
                  const barColor = att.accuracy_pct >= 80 
                    ? 'bg-emerald-500 shadow-emerald-500/30' 
                    : att.accuracy_pct >= 50 
                    ? 'bg-amber-500 shadow-amber-500/30' 
                    : 'bg-rose-500 shadow-rose-500/30';
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                      {/* Tooltip on hover */}
                      <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition bg-slate-950 text-white text-[10px] py-1 px-2 rounded border border-slate-700 whitespace-nowrap z-20 pointer-events-none">
                        {att.topic_name}: {att.accuracy_pct}%
                      </div>
                      <span className="text-[11px] font-bold text-slate-300">{att.accuracy_pct}%</span>
                      <div 
                        className={`w-full max-w-[48px] rounded-t-lg transition-all shadow-lg ${barColor}`}
                        style={{ height: `${heightPct}%` }}
                      />
                      <span className="text-[10px] text-slate-500 truncate max-w-[64px] text-center">
                        Attempt {idx + 1}
                      </span>
                    </div>
                  );
                })}
              </div>
              <div className="text-[11px] text-slate-400 flex items-center justify-between">
                <span>Earliest Attempts</span>
                <span>Latest Attempts (Up to 100% on Mastered Topics)</span>
              </div>
            </div>
          )}
        </div>

        {/* Knowledge Diagnosis Tiers Distribution */}
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-5">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Stethoscope className="w-4 h-4 text-rose-400" />
            <span>Diagnostic Tier Status</span>
          </h2>

          <div className="space-y-3.5">
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <div>
                  <div className="text-xs font-bold text-white">Weak Tier (&lt; 50%)</div>
                  <div className="text-[10px] text-rose-300">Urgent prescription needed</div>
                </div>
              </div>
              <span className="text-xl font-extrabold text-rose-400">{metrics?.weak_count || 0}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <div>
                  <div className="text-xs font-bold text-white">Medium Tier (50% - 79%)</div>
                  <div className="text-[10px] text-amber-300">Needs boundary reinforcement</div>
                </div>
              </div>
              <span className="text-xl font-extrabold text-amber-400">{metrics?.medium_count || 0}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <div>
                  <div className="text-xs font-bold text-white">Strong Tier (≥ 80%)</div>
                  <div className="text-[10px] text-emerald-300">Retained conceptual mastery</div>
                </div>
              </div>
              <span className="text-xl font-extrabold text-emerald-400">{metrics?.strong_count || 0}</span>
            </div>
          </div>

          <button
            onClick={onNavigateToQuiz}
            className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            Launch Grounded Diagnostic Test
          </button>
        </div>

      </div>

    </div>
  );
}
