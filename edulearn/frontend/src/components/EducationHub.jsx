import { useState, useEffect } from 'react';
import './EducationHub.css';
import LearnerProfile from './LearnerProfile';
import AITutor from './AITutor';
import AdaptiveLesson from './AdaptiveLesson';
import ProgressTracker from './ProgressTracker';
import SensoryPanel from './SensoryPanel';
import { useSensorySettings } from '../lib/useSensorySettings';

const NAV = [
  { id: 'dashboard',  label: 'Dashboard',       icon: '🏠' },
  { id: 'profile',    label: 'Learner Profile',  icon: '👤' },
  { id: 'tutor',      label: 'AI Tutor',         icon: '🤖' },
  { id: 'lesson',     label: 'Today\'s Lesson',  icon: '📚' },
  { id: 'progress',   label: 'My Progress',      icon: '📈' },
  { id: 'sensory',    label: 'Display Settings', icon: '🎨' },
];

const DEFAULT_PROFILE = {
  learner_id: 'learner_1',
  name: '',
  age: 10,
  grade_level: '4th',
  primary_needs: [],
  learning_style: 'visual',
  interests: [],
  communication_style: 'verbal',
  sensory_preferences: {},
  skill_levels: {},
  strengths: [],
  challenges: [],
};

export default function EducationHub() {
  const [page, setPage] = useState('dashboard');
  const [profile, setProfile] = useState(() => {
    try {
      const saved = localStorage.getItem('edulearn_profile');
      return saved ? JSON.parse(saved) : DEFAULT_PROFILE;
    } catch { return DEFAULT_PROFILE; }
  });
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('edulearn_sessions');
      return saved ? JSON.parse(saved) : [];
    } catch { return []; }
  });
  const [settings] = useSensorySettings();

  useEffect(() => {
    localStorage.setItem('edulearn_profile', JSON.stringify(profile));
  }, [profile]);

  useEffect(() => {
    localStorage.setItem('edulearn_sessions', JSON.stringify(sessions));
  }, [sessions]);

  function addSession(s) {
    setSessions((prev) => [s, ...prev].slice(0, 50));
  }

  const hasProfile = Boolean(profile.name);
  const streak = sessions.filter((s) => {
    const d = new Date(s.date);
    const today = new Date();
    return today - d < 7 * 24 * 60 * 60 * 1000;
  }).length;

  function renderPage() {
    switch (page) {
      case 'profile':
        return <LearnerProfile profile={profile} onSave={setProfile} onBack={() => setPage('dashboard')} />;
      case 'tutor':
        return <AITutor profile={profile} onSessionEnd={addSession} />;
      case 'lesson':
        return <AdaptiveLesson profile={profile} onSessionEnd={addSession} />;
      case 'progress':
        return <ProgressTracker profile={profile} sessions={sessions} />;
      case 'sensory':
        return <SensoryPanel />;
      default:
        return <Dashboard profile={profile} sessions={sessions} streak={streak} setPage={setPage} hasProfile={hasProfile} />;
    }
  }

  return (
    <div className="hub">
      <aside className={`hub-sidebar${settings.focusMode ? ' focus-mode' : ''}`}>
        <div className="hub-logo">Edu<span>Learn</span> AI</div>
        {NAV.map((n) => (
          <button
            key={n.id}
            className={`hub-nav-btn${page === n.id ? ' active' : ''}`}
            onClick={() => setPage(n.id)}
          >
            <span className="hub-nav-icon">{n.icon}</span>
            {n.label}
          </button>
        ))}
        <div className="hub-sidebar-footer">
          <div>🧠 AI-Powered Learning</div>
          <div style={{ marginTop: 4 }}>Built for every mind</div>
        </div>
      </aside>
      <main className="hub-main">{renderPage()}</main>
    </div>
  );
}

function Dashboard({ profile, sessions, streak, setPage, hasProfile }) {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>
          {hasProfile ? `Welcome back, ${profile.name}! 👋` : 'Welcome to EduLearn AI 👋'}
        </h1>
        <p>Your personalised AI learning space — built for every kind of mind.</p>
        {hasProfile && (
          <div className="active-learner-chip">
            👤 {profile.name} · Grade {profile.grade_level}
            {profile.primary_needs.length > 0 && ` · ${profile.primary_needs.join(', ')}`}
          </div>
        )}
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-value">{sessions.length}</div>
          <div className="stat-label">Sessions Complete</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-value">{streak}</div>
          <div className="stat-label">7-Day Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-value">{sessions.length * 10}</div>
          <div className="stat-label">Stars Earned</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-value">{Math.floor(sessions.length / 3)}</div>
          <div className="stat-label">Badges Unlocked</div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>What would you like to do today?</h2>
        <div className="action-grid">
          {!hasProfile && (
            <div className="action-card" onClick={() => setPage('profile')}>
              <div className="ac-icon">👤</div>
              <h3>Set Up My Profile</h3>
              <p>Tell us about you so we can personalise everything!</p>
            </div>
          )}
          <div className="action-card" onClick={() => setPage('lesson')}>
            <div className="ac-icon">📚</div>
            <h3>Start a Lesson</h3>
            <p>AI creates a lesson just for you, step by step.</p>
          </div>
          <div className="action-card" onClick={() => setPage('tutor')}>
            <div className="ac-icon">🤖</div>
            <h3>Chat with AI Tutor</h3>
            <p>Ask anything — your patient AI tutor is always here.</p>
          </div>
          <div className="action-card" onClick={() => setPage('progress')}>
            <div className="ac-icon">📈</div>
            <h3>See My Progress</h3>
            <p>Celebrate what you've learned and see what's next.</p>
          </div>
          <div className="action-card" onClick={() => setPage('sensory')}>
            <div className="ac-icon">🎨</div>
            <h3>Display Settings</h3>
            <p>Adjust text, colours and animations to feel just right.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
