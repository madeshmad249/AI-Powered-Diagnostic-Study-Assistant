import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Clock, 
  Flame, 
  CheckCircle2, 
  RotateCcw, 
  ArrowRight, 
  BookOpen, 
  Sliders, 
  Sparkles,
  CheckSquare,
  Square,
  Layers,
  ChevronRight
} from 'lucide-react';
import { api } from '../api';

export default function RevisionPlan({ onTakeQuiz }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [targetDays, setTargetDays] = useState(5);
  const [dailyHours, setDailyHours] = useState(2.0);
  const [generating, setGenerating] = useState(false);
  const [completedBlocks, setCompletedBlocks] = useState({});

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const data = await api.getRevisionPlan();
      setPlan(data);
      if (data) {
        setTargetDays(data.target_days);
        setDailyHours(data.daily_hours);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  const handleGenerate = async (e) => {
    e?.preventDefault();
    setGenerating(true);
    try {
      const updated = await api.generateRevisionPlan(Number(targetDays), Number(dailyHours));
      setPlan(updated);
    } catch (err) {
      alert(`Plan generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const toggleBlockCompleted = (dayIdx, blockIdx) => {
    const key = `${dayIdx}_${blockIdx}`;
    setCompletedBlocks(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Weak':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'Medium':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      case 'Strong':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      default:
        return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-xs mb-1">
              <Calendar className="w-4 h-4" />
              <span>Step 7: Adaptive Time-Bound Revision Plan</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">Dynamic Study Timetable</h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Prioritized by the formula: <code className="text-indigo-300 font-mono text-xs">Priority = (1 - Accuracy) × (1 + ExamWeight × 0.2)</code>. Weakest, high-yield topics are tackled first and dynamically adapt as your quiz scores improve.
            </p>
          </div>

          {/* Time Budget Controller Form */}
          <form onSubmit={handleGenerate} className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-wrap items-end gap-3 shrink-0">
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">Days Left</label>
              <input
                type="number"
                min="1"
                max="30"
                value={targetDays}
                onChange={(e) => setTargetDays(e.target.value)}
                className="w-20 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-bold"
              />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">Hours / Day</label>
              <input
                type="number"
                step="0.5"
                min="0.5"
                max="12"
                value={dailyHours}
                onChange={(e) => setDailyHours(e.target.value)}
                className="w-24 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-bold"
              />
            </div>
            <button
              type="submit"
              disabled={generating}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs shadow-md shadow-indigo-600/30 transition"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>{generating ? 'Re-planning...' : 'Update Plan'}</span>
            </button>
          </form>
        </div>
      </div>

      {/* Schedule Days */}
      <div className="space-y-6">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            Calculating optimal revision timetable...
          </div>
        ) : !plan || !plan.schedule || plan.schedule.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            No revision schedule generated yet. Click "Update Plan" above.
          </div>
        ) : (
          plan.schedule.map((dayItem, dIdx) => (
            <div 
              key={dayItem.day}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg space-y-4"
            >
              {/* Day Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-extrabold text-sm flex items-center justify-center">
                    {dayItem.day}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{dayItem.day_title}</h3>
                    <div className="text-[11px] text-slate-400">
                      Total Allocated: <strong className="text-indigo-400">{(dayItem.total_study_minutes / 60).toFixed(1)} hrs</strong> ({dayItem.total_study_minutes} mins)
                    </div>
                  </div>
                </div>
              </div>

              {/* Study Blocks */}
              <div className="space-y-3">
                {dayItem.blocks.map((block, bIdx) => {
                  const key = `${dIdx}_${bIdx}`;
                  const isDone = completedBlocks[key];
                  return (
                    <div
                      key={bIdx}
                      className={`p-4 rounded-xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                        isDone
                          ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                          : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-start space-x-3.5">
                        <button
                          onClick={() => toggleBlockCompleted(dIdx, bIdx)}
                          className="mt-0.5 text-slate-400 hover:text-emerald-400 transition"
                          title="Mark Block Completed"
                        >
                          {isDone ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-500/20" />
                          ) : (
                            <Square className="w-5 h-5 text-slate-600 hover:text-slate-400" />
                          )}
                        </button>

                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusColor(block.status)}`}>
                              {block.status}
                            </span>
                            <span className="text-xs font-bold text-white">
                              {block.topic_name}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed">
                            {block.focus_objective}
                          </p>
                          <div className="text-[11px] text-slate-400 flex items-center space-x-2 pt-0.5">
                            <span className="text-indigo-400">{block.recommended_source}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 shrink-0 pl-8 md:pl-0">
                        <div className="flex items-center space-x-1 text-xs text-indigo-300 bg-indigo-500/10 px-3 py-1.5 rounded-lg border border-indigo-500/20 font-mono font-semibold">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{block.time_allocated_minutes} min</span>
                        </div>

                        {block.topic_id ? (
                          <button
                            onClick={() => onTakeQuiz(block.topic_id, block.topic_name)}
                            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
                          >
                            <span>Verify</span>
                            <ChevronRight className="w-3.5 h-3.5" />
                          </button>
                        ) : null}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}
