import React, { useState, useEffect } from 'react';
import { 
  Stethoscope, 
  AlertCircle, 
  CheckCircle2, 
  AlertTriangle, 
  Flame, 
  ArrowRight, 
  Calendar, 
  RotateCcw, 
  MessageSquare,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  BrainCircuit
} from 'lucide-react';
import { api } from '../api';

export default function GapReport({ onTakeQuiz, onGeneratePlan, onOpenChatWithTopic }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterTier, setFilterTier] = useState('ALL'); // ALL, Weak, Medium, Strong

  const fetchGapReport = async () => {
    try {
      setLoading(true);
      const data = await api.getGapReport();
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGapReport();
  }, []);

  const getTierIcon = (status) => {
    switch (status) {
      case 'Weak':
        return <AlertCircle className="w-5 h-5 text-rose-400" />;
      case 'Medium':
        return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      case 'Strong':
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      default:
        return <Stethoscope className="w-5 h-5 text-indigo-400" />;
    }
  };

  const getTierBadge = (status) => {
    switch (status) {
      case 'Weak':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'Medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Strong':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const filteredTopics = report?.topics.filter(t => {
    if (filterTier === 'ALL') return true;
    return t.status.toUpperCase() === filterTier.toUpperCase();
  }) || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Header Banner - Study Doctor Diagnosis */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 text-rose-400 font-semibold text-xs mb-1">
              <Stethoscope className="w-4 h-4 animate-pulse" />
              <span>Step 6: Diagnostic Gap Report (Core Output)</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">Student Knowledge Gap Diagnosis</h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Acting like a study doctor, this report analyzes diagnostic test attempts, identifies exact cognitive blind spots, and prioritizes what to treat before your exam.
            </p>
          </div>

          <button
            onClick={onGeneratePlan}
            className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition shrink-0"
          >
            <Calendar className="w-4 h-4" />
            <span>Generate Adaptive Revision Plan</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Diagnostic Metrics Cards */}
        {report && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-slate-800">
            <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
              <div className="text-xs text-slate-400">Exam Readiness</div>
              <div className="text-2xl font-extrabold text-white mt-0.5">
                {report.overall_readiness_pct}%
              </div>
            </div>
            <div className="bg-rose-500/5 p-3.5 rounded-xl border border-rose-500/20">
              <div className="text-xs text-rose-400 font-medium">🔴 Weak Topics</div>
              <div className="text-2xl font-extrabold text-rose-400 mt-0.5">
                {report.summary.weak}
              </div>
            </div>
            <div className="bg-amber-500/5 p-3.5 rounded-xl border border-amber-500/20">
              <div className="text-xs text-amber-400 font-medium">🟡 Medium Topics</div>
              <div className="text-2xl font-extrabold text-amber-400 mt-0.5">
                {report.summary.medium}
              </div>
            </div>
            <div className="bg-emerald-500/5 p-3.5 rounded-xl border border-emerald-500/20">
              <div className="text-xs text-emerald-400 font-medium">🟢 Strong Topics</div>
              <div className="text-2xl font-extrabold text-emerald-400 mt-0.5">
                {report.summary.strong}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          {['ALL', 'Weak', 'Medium', 'Strong'].map(tier => (
            <button
              key={tier}
              onClick={() => setFilterTier(tier)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                filterTier === tier
                  ? 'bg-slate-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {tier === 'ALL' ? 'All Diagnoses' : `${tier} Tier`}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-500">
          Showing {filteredTopics.length} of {report?.topics.length || 0} Modules
        </span>
      </div>

      {/* Topics Diagnostic Cards List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            Synthesizing medical diagnosis of knowledge gaps...
          </div>
        ) : filteredTopics.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            No topics found for this filter.
          </div>
        ) : (
          filteredTopics.map((topic) => (
            <div
              key={topic.topic_id}
              className={`bg-slate-900 border rounded-2xl p-6 shadow-lg transition-all space-y-4 ${
                topic.status === 'Weak'
                  ? 'border-rose-500/40 hover:border-rose-500/60'
                  : topic.status === 'Medium'
                  ? 'border-amber-500/40 hover:border-amber-500/60'
                  : 'border-emerald-500/40 hover:border-emerald-500/60'
              }`}
            >
              {/* Header row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start space-x-3">
                  <div className="p-2 rounded-xl bg-slate-950/80 border border-slate-800 mt-0.5">
                    {getTierIcon(topic.status)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getTierBadge(topic.status)}`}>
                        {topic.status} Tier
                      </span>
                      <span className="text-xs text-slate-400">•</span>
                      <span className="text-xs text-slate-400 font-mono">
                        Priority Urgency: <strong className="text-white">{topic.priority_score}</strong>
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mt-1">{topic.topic_name}</h3>
                  </div>
                </div>

                <div className="flex items-center space-x-3 shrink-0">
                  <div className="text-right">
                    <div className="text-[11px] text-slate-400">Diagnostic Accuracy</div>
                    <div className={`text-base font-extrabold ${
                      topic.accuracy_pct >= 80 ? 'text-emerald-400' : topic.accuracy_pct >= 50 ? 'text-amber-400' : 'text-rose-400'
                    }`}>
                      {topic.accuracy_pct}% ({topic.attempts_count} {topic.attempts_count === 1 ? 'Attempt' : 'Attempts'})
                    </div>
                  </div>
                </div>
              </div>

              {/* Diagnostic Clinical Reason Box */}
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-400">
                  <BrainCircuit className="w-4 h-4" />
                  <span>Clinical Gap Diagnosis:</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {topic.diagnostic_reason}
                </p>
                <div className="pt-2 border-t border-slate-800/60 flex items-center space-x-2 text-[11px] text-slate-400">
                  <strong className="text-slate-300">Prescription:</strong>
                  <span>{topic.recommended_focus}</span>
                </div>
              </div>

              {/* Footer Meta & Actions */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
                <div className="flex items-center space-x-3 text-xs text-slate-400">
                  <span className="inline-flex items-center space-x-1">
                    <Flame className="w-3.5 h-3.5 text-amber-400" />
                    <span>Weightage: <strong>{topic.weightage_level}</strong> ({topic.exam_frequency} Exam Qs)</span>
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onOpenChatWithTopic(topic.topic_name)}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-xs font-medium transition"
                  >
                    <MessageSquare className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Grounded Tutor</span>
                  </button>

                  <button
                    onClick={() => onTakeQuiz(topic.topic_id, topic.topic_name)}
                    className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Retake Diagnostic</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}
