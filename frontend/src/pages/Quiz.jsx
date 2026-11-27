import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  HelpCircle, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  ArrowRight, 
  RotateCcw, 
  Stethoscope, 
  Calendar,
  Sparkles,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import { api } from '../api';

export default function Quiz({ 
  initialTopicId, 
  initialTopicName, 
  onNavigateToGapReport, 
  onNavigateToRevisionPlan 
}) {
  const [topics, setTopics] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState(initialTopicId || null);
  const [quizData, setQuizData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.getTopics().then((res) => {
      setTopics(res);
      if (!selectedTopicId && res.length > 0) {
        setSelectedTopicId(res[0].id);
      }
    }).catch(console.error);
  }, []);

  const handleLoadQuiz = async (topicId) => {
    const tId = topicId || selectedTopicId;
    if (!tId) return;

    setLoading(true);
    setResult(null);
    setSelectedAnswers({});
    try {
      const data = await api.generateQuiz(tId, 3);
      setQuizData(data);
    } catch (err) {
      alert(`Quiz generation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedTopicId) {
      handleLoadQuiz(selectedTopicId);
    }
  }, [selectedTopicId]);

  const handleSelectOption = (qIdx, optionId) => {
    if (result) return; // Locked once submitted
    setSelectedAnswers(prev => ({ ...prev, [qIdx]: optionId }));
  };

  const handleSubmit = async () => {
    if (!quizData) return;
    const answeredCount = Object.keys(selectedAnswers).length;
    if (answeredCount < quizData.questions.length) {
      if (!confirm(`You have answered ${answeredCount} of ${quizData.questions.length} questions. Submit anyway?`)) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const formattedAnswers = quizData.questions.map((q, idx) => ({
        question_index: idx + 1,
        question_text: q.question,
        options: q.options,
        student_answer: selectedAnswers[idx] || 'Unanswered',
        correct_answer: q.correct_answer || 'A',
        citation: q.citation,
        explanation: q.explanation || ''
      }));

      const res = await api.submitQuiz(quizData.topic_id, formattedAnswers);
      setResult(res);
    } catch (err) {
      alert(`Submission error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'Strong') {
      return (
        <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-4 h-4" />
          <span>Strong Mastery (≥ 80%)</span>
        </span>
      );
    }
    if (status === 'Medium') {
      return (
        <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <AlertTriangle className="w-4 h-4" />
          <span>Medium Comprehension (50% - 79%)</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
        <Stethoscope className="w-4 h-4" />
        <span>Weak Deficit (&lt; 50%) — Needs Treatment</span>
      </span>
    );
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-xs mb-1">
              <CheckSquare className="w-4 h-4" />
              <span>Step 5: Grounded Diagnostic Testing & Evaluator</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">Diagnostic Knowledge Check</h1>
            <p className="text-xs text-slate-400 mt-1 max-w-xl">
              Questions are strictly formulated from your uploaded notes and textbooks. Every question displays the exact document section and page citation.
            </p>
          </div>

          {/* Topic Selector */}
          <div className="shrink-0">
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Select Module to Test:</label>
            <select
              value={selectedTopicId || ''}
              onChange={(e) => setSelectedTopicId(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 text-xs text-white rounded-xl px-3 py-2 focus:outline-none focus:border-indigo-500"
            >
              {topics.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main Quiz Flow */}
      {loading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <Sparkles className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
          <h3 className="text-sm font-semibold text-white">Running Two-Stage RAG Pipeline...</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Stage 1: Fetching verified excerpts from ChromaDB vector store.<br/>
            Stage 2: Synthesizing grounded questions with exact page citations.
          </p>
        </div>
      ) : result ? (
        /* Evaluation & Result Breakdown */
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Diagnostic Evaluation Completed</span>
                <h2 className="text-xl font-bold text-white mt-0.5">{result.topic_name}</h2>
              </div>
              <div>{getStatusBadge(result.status)}</div>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400">Score</div>
                <div className="text-xl font-extrabold text-white">{result.score} / {result.total_questions}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400">Accuracy</div>
                <div className={`text-xl font-extrabold ${result.accuracy_pct >= 80 ? 'text-emerald-400' : result.accuracy_pct >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                  {result.accuracy_pct}%
                </div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400">Diagnosis Tier</div>
                <div className="text-xl font-extrabold text-indigo-400">{result.status}</div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 flex flex-wrap gap-3 justify-end">
              <button
                onClick={() => handleLoadQuiz(result.topic_id)}
                className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retake Quiz</span>
              </button>
              <button
                onClick={onNavigateToGapReport}
                className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md shadow-rose-600/30 transition"
              >
                <Stethoscope className="w-3.5 h-3.5" />
                <span>View Diagnosis in Gap Report</span>
              </button>
              <button
                onClick={onNavigateToRevisionPlan}
                className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition"
              >
                <Calendar className="w-3.5 h-3.5" />
                <span>Update Revision Plan</span>
              </button>
            </div>
          </div>

          {/* Question-by-Question Detailed Feedback */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-slate-300">Detailed Educational Explanations</h3>
            {result.evaluations.map((ev, idx) => (
              <div
                key={idx}
                className={`p-5 rounded-2xl border bg-slate-900 shadow-md space-y-3 ${
                  ev.is_correct ? 'border-emerald-500/30' : 'border-rose-500/30'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start space-x-2">
                    {ev.is_correct ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <span className="text-xs font-bold text-slate-400">Question {idx + 1}:</span>
                      <h4 className="text-sm font-semibold text-white mt-0.5">{ev.question}</h4>
                    </div>
                  </div>
                  <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-[10px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
                    <FileText className="w-3 h-3" />
                    <span>{ev.citation}</span>
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                  <div>
                    <span className="text-slate-400">Your Answer: </span>
                    <span className={ev.is_correct ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                      Option {ev.student_answer}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Verified Answer: </span>
                    <span className="text-emerald-400 font-bold">Option {ev.correct_answer}</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                  <span className="font-semibold text-indigo-300">Why: </span>
                  {ev.explanation}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : quizData ? (
        /* Quiz Form */
        <div className="space-y-6">
          <div className="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-slate-800">
            <span>Testing: <strong className="text-indigo-400">{quizData.topic_name}</strong></span>
            <span>{Object.keys(selectedAnswers).length} of {quizData.questions.length} Answered</span>
          </div>

          <div className="space-y-6">
            {quizData.questions.map((q, qIdx) => (
              <div 
                key={qIdx}
                className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4 hover:border-slate-700 transition"
              >
                {/* Question Header & Grounded Citation Badge */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start space-x-2.5">
                    <span className="w-6 h-6 rounded-lg bg-indigo-600/20 text-indigo-400 font-bold text-xs flex items-center justify-center shrink-0 border border-indigo-500/30">
                      {qIdx + 1}
                    </span>
                    <h3 className="text-sm font-semibold text-white leading-snug">
                      {q.question}
                    </h3>
                  </div>

                  {/* Explicit Source Citation */}
                  <span 
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 shrink-0"
                    title="Exact source location in student's notes"
                  >
                    <FileText className="w-3 h-3 text-indigo-400" />
                    <span>{q.citation}</span>
                  </span>
                </div>

                {/* Options List */}
                <div className="grid grid-cols-1 gap-2.5 pt-1">
                  {q.options.map((opt) => {
                    const isSelected = selectedAnswers[qIdx] === opt.id;
                    return (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => handleSelectOption(qIdx, opt.id)}
                        className={`w-full text-left p-3.5 rounded-xl border text-xs font-medium transition flex items-center space-x-3 ${
                          isSelected
                            ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/20'
                            : 'bg-slate-950/60 hover:bg-slate-800 text-slate-200 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        <span className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold shrink-0 ${
                          isSelected ? 'bg-white text-indigo-600' : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}>
                          {opt.id}
                        </span>
                        <span>{opt.text}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Submit Button */}
          <div className="pt-2 flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition"
            >
              {submitting ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Evaluating Answers & Grounding...</span>
                </>
              ) : (
                <>
                  <span>Submit Diagnostic Answers</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      ) : null}

    </div>
  );
}
