import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import TopicChat from './components/TopicChat';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import GapReport from './pages/GapReport';
import Quiz from './pages/Quiz';
import RevisionPlan from './pages/RevisionPlan';
import TopicMap from './pages/TopicMap';
import Upload from './pages/Upload';
import { api } from './api';

export default function App() {
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatTopic, setChatTopic] = useState('Memory Management & Virtual Memory');
  
  // Cross-page state linking
  const [quizTopicId, setQuizTopicId] = useState(null);
  const [quizTopicName, setQuizTopicName] = useState(null);

  useEffect(() => {
    // Check if token exists
    const token = localStorage.getItem('gapfinder_token');
    if (token) {
      api.getMe()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('gapfinder_token');
          setUser(null);
        })
        .finally(() => setLoadingUser(false));
    } else {
      setLoadingUser(false);
    }
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('gapfinder_token');
    setUser(null);
  };

  const handleStartQuizFromTopic = (topicId, topicName) => {
    setQuizTopicId(topicId);
    setQuizTopicName(topicName);
    setActiveTab('quiz');
  };

  const handleOpenChatWithTopic = (topicName) => {
    setChatTopic(topicName);
    setIsChatOpen(true);
  };

  if (loadingUser) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-xs">
        Initializing Study Doctor...
      </div>
    );
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onLogout={handleLogout}
        onToggleChat={() => setIsChatOpen(prev => !prev)}
      />

      {/* Main Dynamic View Content */}
      <main className="flex-1 pb-16">
        {activeTab === 'dashboard' && (
          <Dashboard
            onNavigateToGapReport={() => setActiveTab('gap-report')}
            onNavigateToQuiz={() => setActiveTab('quiz')}
            onNavigateToPlan={() => setActiveTab('revision-plan')}
          />
        )}

        {activeTab === 'gap-report' && (
          <GapReport
            onTakeQuiz={handleStartQuizFromTopic}
            onGeneratePlan={() => setActiveTab('revision-plan')}
            onOpenChatWithTopic={handleOpenChatWithTopic}
          />
        )}

        {activeTab === 'quiz' && (
          <Quiz
            initialTopicId={quizTopicId}
            initialTopicName={quizTopicName}
            onNavigateToGapReport={() => setActiveTab('gap-report')}
            onNavigateToRevisionPlan={() => setActiveTab('revision-plan')}
          />
        )}

        {activeTab === 'revision-plan' && (
          <RevisionPlan
            onTakeQuiz={handleStartQuizFromTopic}
          />
        )}

        {activeTab === 'topic-map' && (
          <TopicMap
            onStartQuiz={handleStartQuizFromTopic}
            onOpenChatWithTopic={handleOpenChatWithTopic}
          />
        )}

        {activeTab === 'upload' && (
          <Upload
            onNavigateToTopics={() => setActiveTab('topic-map')}
          />
        )}
      </main>

      {/* Grounded Tutor Chat Drawer */}
      <TopicChat
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        defaultTopic={chatTopic}
      />
    </div>
  );
}
