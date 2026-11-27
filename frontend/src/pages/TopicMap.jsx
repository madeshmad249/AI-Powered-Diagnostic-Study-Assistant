import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  ChevronRight, 
  ChevronDown, 
  Layers, 
  Flame, 
  HelpCircle, 
  Play, 
  MessageSquare,
  Sparkles,
  RefreshCw,
  FolderTree
} from 'lucide-react';
import { api } from '../api';

export default function TopicMap({ onStartQuiz, onOpenChatWithTopic }) {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});
  const [refreshing, setRefreshing] = useState(false);

  const fetchTopics = async () => {
    try {
      setLoading(true);
      const data = await api.getTopics();
      setTopics(data);
      // Auto-expand all topics initially
      const initialExp = {};
      data.forEach(t => { initialExp[t.id] = true; });
      setExpanded(initialExp);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const toggleExpand = (id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleRegenerate = async () => {
    setRefreshing(true);
    try {
      const refreshed = await api.generateTopicMap();
      setTopics(refreshed);
    } catch (err) {
      alert(err.message);
    } finally {
      setRefreshing(false);
    }
  };

  const getWeightBadge = (level, freq) => {
    if (level === 'High' || freq >= 4) {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
          <Flame className="w-3 h-3 text-rose-400" />
          <span>High Weightage ({freq} Past Qs)</span>
        </span>
      );
    }
    if (level === 'Medium' || freq >= 2) {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <span>Medium Weightage ({freq} Past Qs)</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">
        <span>Low Weightage ({freq} Past Qs)</span>
      </span>
    );
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-xs mb-1">
              <FolderTree className="w-4 h-4" />
              <span>Step 3: Syllabus Hierarchy & Exam Weightage Map</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">Course Syllabus & Exam Impact Tree</h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Constructed by extracting the course syllabus tree and vector-matching past examination questions. Topics with high past-paper frequency carry higher priority in your study diagnosis.
            </p>
          </div>
          <button
            onClick={handleRegenerate}
            disabled={refreshing}
            className="self-start md:self-auto flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Sync Syllabus Map</span>
          </button>
        </div>
      </div>

      {/* Topics Hierarchy List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            Constructing structured syllabus topic map...
          </div>
        ) : topics.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900 rounded-2xl border border-slate-800">
            No topics mapped yet. Please upload a course syllabus first.
          </div>
        ) : (
          topics.map((t, idx) => {
            const isExp = expanded[t.id];
            return (
              <div 
                key={t.id} 
                className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-md transition-all hover:border-slate-700"
              >
                {/* Module Header */}
                <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start space-x-3 cursor-pointer" onClick={() => toggleExpand(t.id)}>
                    <button className="p-1 rounded-md bg-slate-800 text-slate-400 hover:text-white mt-0.5">
                      {isExp ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>
                    <div>
                      <div className="flex items-center space-x-2.5">
                        <span className="text-xs font-mono font-bold text-indigo-400">Module 0{idx + 1}</span>
                        <h3 className="text-base font-bold text-white hover:text-indigo-300 transition">
                          {t.name}
                        </h3>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 max-w-2xl">{t.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0 pl-7 md:pl-0">
                    {getWeightBadge(t.weightage_level, t.exam_frequency)}
                    
                    <button
                      onClick={() => onStartQuiz(t.id, t.name)}
                      className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Take Diagnostic Quiz</span>
                    </button>

                    <button
                      onClick={() => onOpenChatWithTopic(t.name)}
                      className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
                      title="Explain this topic with Grounded Tutor"
                    >
                      <MessageSquare className="w-4 h-4 text-indigo-400" />
                    </button>
                  </div>
                </div>

                {/* Subtopics Accordion */}
                {isExp && t.subtopics && t.subtopics.length > 0 && (
                  <div className="bg-slate-950/60 border-t border-slate-800/80 px-6 py-4">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
                      Subtopic Granularity ({t.subtopics.length} Sections)
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                      {t.subtopics.map((st) => (
                        <div
                          key={st.id}
                          className="p-3 rounded-xl bg-slate-900 border border-slate-800/80 flex items-center justify-between text-xs hover:border-indigo-500/40 transition"
                        >
                          <div className="flex items-center space-x-2 truncate">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />
                            <span className="text-slate-200 font-medium truncate">{st.name}</span>
                          </div>
                          <span className="text-[10px] text-slate-500 shrink-0 ml-2">Grounded</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
