import React, { useState, useEffect } from 'react';
import { 
  X, 
  Send, 
  Sparkles, 
  BookOpen, 
  FileText, 
  ShieldCheck, 
  AlertCircle,
  HelpCircle,
  CheckCircle2
} from 'lucide-react';
import { api } from '../api';

export default function TopicChat({ isOpen, onClose, defaultTopic = 'Memory Management & Virtual Memory' }) {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(defaultTopic);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: `Hello! I am your Grounded Study Doctor. Select a topic and ask any question. Every answer I provide is strictly retrieved from your uploaded textbook notes, accompanied by verified page citations.`,
      citations: []
    }
  ]);

  useEffect(() => {
    api.getTopics().then((res) => {
      setTopics(res);
      if (res.length > 0 && !selectedTopic) {
        setSelectedTopic(res[0].name);
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (defaultTopic) {
      setSelectedTopic(defaultTopic);
    }
  }, [defaultTopic]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!query.trim() || loading) return;

    const userText = query.trim();
    setQuery('');
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);

    try {
      const res = await api.explainTopic(selectedTopic, userText);
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: res.explanation,
          citations: res.citations || [],
          grounded: res.grounded_in_material
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: `Error retrieving grounded context: ${err.message}. Please check if notes for this topic are uploaded.`,
          citations: [],
          error: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    "Explain what a page fault is step-by-step.",
    "Why does thrashing occur and how is it detected?",
    "What are the 4 Coffman conditions for deadlock?",
    "Why is context switching pure system overhead?"
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col transition-all">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-white flex items-center gap-1.5">
              Grounded Study Tutor
              <span className="text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" /> Grounded Only
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Strictly references uploaded notes with page citations</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Grounded Topic Selector */}
      <div className="p-3 bg-slate-950/40 border-b border-slate-800/80 flex items-center space-x-2">
        <span className="text-xs font-medium text-slate-400 whitespace-nowrap">Focus Topic:</span>
        <select
          value={selectedTopic}
          onChange={(e) => setSelectedTopic(e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
        >
          {topics.map(t => (
            <option key={t.id} value={t.name}>{t.name}</option>
          ))}
        </select>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[92%] rounded-xl p-3 text-xs leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-slate-800/90 text-slate-200 border border-slate-700/80'
              }`}
            >
              <div className="whitespace-pre-line">{m.text}</div>

              {/* Citations Badges */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-700/60 space-y-1.5">
                  <div className="text-[10px] font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1">
                    <FileText className="w-3 h-3" /> Grounded Source Excerpts ({m.citations.length})
                  </div>
                  {m.citations.map((c, cIdx) => (
                    <div
                      key={cIdx}
                      className="p-2 rounded bg-slate-950/60 border border-slate-800 text-[11px] text-slate-300 space-y-1"
                    >
                      <div className="flex items-center justify-between text-indigo-400 font-medium">
                        <span>{c.filename}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 border border-indigo-500/30">
                          Page {c.page}
                        </span>
                      </div>
                      <p className="text-slate-400 italic text-[10px] line-clamp-3">
                        "{c.excerpt}"
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <span className="text-[10px] text-slate-500 mt-1 px-1">
              {m.sender === 'user' ? 'You' : 'Study Doctor (Grounded)'}
            </span>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-xs text-indigo-400 bg-slate-800/50 p-3 rounded-xl border border-indigo-500/20 animate-pulse">
            <Sparkles className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Retrieving text blocks from ChromaDB & synthesizing citation...</span>
          </div>
        )}
      </div>

      {/* Suggested Quick Questions */}
      <div className="p-2 bg-slate-950/30 border-t border-slate-800/60">
        <div className="text-[10px] text-slate-500 font-semibold mb-1 px-1">Quick Grounded Inquiries:</div>
        <div className="flex flex-wrap gap-1.5">
          {samplePrompts.map((sp, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(sp);
              }}
              className="text-[10px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded-md border border-slate-700 transition"
            >
              {sp}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-3 bg-slate-950/80 border-t border-slate-800 flex items-center space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Ask anything about ${selectedTopic}...`}
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={!query.trim() || loading}
          className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
