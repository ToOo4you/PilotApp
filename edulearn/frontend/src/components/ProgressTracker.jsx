import { useState } from 'react';
import './ProgressTracker.css';
import { api } from '../lib/api';

const ALL_BADGES = [
  { id: 'first_lesson',  icon: '📚', name: 'First Lesson',   threshold: 1,  type: 'sessions' },
  { id: 'five_lessons',  icon: '🎯', name: '5 Sessions',     threshold: 5,  type: 'sessions' },
  { id: 'ten_lessons',   icon: '🏆', name: '10 Sessions',    threshold: 10, type: 'sessions' },
  { id: 'tutor_fan',     icon: '🤖', name: 'Tutor Friend',   threshold: 3,  type: 'tutor' },
  { id: 'quiz_ace',      icon: '⭐', name: 'Quiz Ace',       threshold: 1,  type: 'quiz' },
  { id: 'streak_3',      icon: '🔥', name: '3-Day Streak',   threshold: 3,  type: 'streak' },
  { id: 'curious',       icon: '🌟', name: 'Super Curious',  threshold: 2,  type: 'subjects' },
  { id: 'champion',      icon: '🏅', name: 'Champion',       threshold: 20, type: 'sessions' },
];

function computeStats(sessions) {
  const total = sessions.length;
  const tutorCount = sessions.filter((s) => s.type === 'tutor').length;
  const lessonCount = sessions.filter((s) => s.type === 'lesson').length;
  const subjects = [...new Set(sessions.map((s) => s.subject).filter(Boolean))];
  const quizSessions = sessions.filter((s) => s.quiz_score);
  const streak = sessions.filter((s) => {
    const d = new Date(s.date);
    return Date.now() - d < 7 * 24 * 60 * 60 * 1000;
  }).length;

  // subject session counts
  const subjectMap = {};
  sessions.forEach((s) => {
    if (s.subject) subjectMap[s.subject] = (subjectMap[s.subject] || 0) + 1;
  });

  return { total, tutorCount, lessonCount, subjects, quizSessions, streak, subjectMap };
}

function badgeUnlocked(badge, stats) {
  switch (badge.type) {
    case 'sessions': return stats.total >= badge.threshold;
    case 'tutor':    return stats.tutorCount >= badge.threshold;
    case 'quiz':     return stats.quizSessions.length >= badge.threshold;
    case 'streak':   return stats.streak >= badge.threshold;
    case 'subjects': return stats.subjects.length >= badge.threshold;
    default: return false;
  }
}

export default function ProgressTracker({ profile, sessions }) {
  const [insights, setInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [insightError, setInsightError] = useState('');

  const stats = computeStats(sessions);
  const totalMinutes = sessions.reduce((acc, s) => acc + (s.duration_minutes || 0), 0);

  async function fetchInsights() {
    setLoadingInsights(true);
    setInsightError('');
    try {
      const data = await api.analyzeProgress({
        learner_profile: profile,
        session_data: {
          total_sessions: stats.total,
          tutor_sessions: stats.tutorCount,
          lesson_sessions: stats.lessonCount,
          subjects_studied: stats.subjects,
          quiz_results: stats.quizSessions.map((s) => s.quiz_score),
          total_minutes: totalMinutes,
          week_streak: stats.streak,
          recent_sessions: sessions.slice(0, 5),
        },
      });
      setInsights(data.insight);
    } catch (err) {
      setInsightError(`Could not load insights: ${err.message}`);
    } finally {
      setLoadingInsights(false);
    }
  }

  const maxSubjectCount = Math.max(...Object.values(stats.subjectMap), 1);

  return (
    <div className="progress-page">
      <h1>📈 My Progress</h1>
      <p className="subtitle">
        {profile.name ? `Amazing work, ${profile.name}!` : 'Amazing work!'} Every session counts. Here's how far you've come! 🌟
      </p>

      {/* Stats */}
      <div className="progress-stats">
        {[
          { icon: '📚', value: stats.total,        label: 'Total Sessions' },
          { icon: '🔥', value: stats.streak,        label: 'This Week' },
          { icon: '⏱️', value: `${totalMinutes}m`,  label: 'Time Learning' },
          { icon: '🧠', value: stats.tutorCount,    label: 'Tutor Chats' },
          { icon: '🎯', value: stats.lessonCount,   label: 'Lessons Done' },
          { icon: '📖', value: stats.subjects.length, label: 'Subjects Explored' },
        ].map((s, i) => (
          <div key={i} className="progress-stat-card">
            <div className="psc-icon">{s.icon}</div>
            <div className="psc-value">{s.value}</div>
            <div className="psc-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Subject progress */}
      {Object.keys(stats.subjectMap).length > 0 && (
        <div className="subject-progress">
          <h2>📊 Subjects Explored</h2>
          {Object.entries(stats.subjectMap).map(([subj, count]) => (
            <div key={subj} className="subject-bar-row">
              <div className="subject-bar-label">
                <strong>{subj}</strong>
                <span>{count} session{count !== 1 ? 's' : ''}</span>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${(count / maxSubjectCount) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Badges */}
      <div className="badges-section">
        <h2>🏆 Badges</h2>
        <div className="badges-grid">
          {ALL_BADGES.map((b) => {
            const unlocked = badgeUnlocked(b, stats);
            return (
              <div key={b.id} className="badge-item" title={unlocked ? `Earned: ${b.name}` : `Locked: ${b.name}`}>
                <div className={`badge-icon${unlocked ? '' : ' locked'}`}>{b.icon}</div>
                <span className="badge-name">{b.name}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* AI Insights */}
      <div className="insights-panel">
        <h2>🤖 AI Progress Insights</h2>
        {!insights && !loadingInsights && (
          <>
            <p style={{ color: 'var(--text-muted)', marginBottom: 14 }}>
              Get a personalised AI analysis of your learning journey.
            </p>
            <button className="btn-primary" onClick={fetchInsights} disabled={stats.total === 0}>
              ✨ Generate Insights
            </button>
            {stats.total === 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: 10 }}>
                Complete at least one session to get insights!
              </p>
            )}
            {insightError && <p style={{ color: 'red', fontSize: '0.9rem', marginTop: 10 }}>{insightError}</p>}
          </>
        )}

        {loadingInsights && (
          <div className="insights-loading">
            <div className="spinner" style={{ width: 24, height: 24, borderWidth: 3 }} />
            Analysing your progress…
          </div>
        )}

        {insights && (
          <>
            <div className="celebration-msg">🎉 {insights.celebration_message}</div>

            <div className="insight-section">
              <h4>💪 Strengths</h4>
              <div className="insight-chips">
                {insights.strengths_identified.map((s, i) => (
                  <span key={i} className="insight-chip badge-green">{s}</span>
                ))}
              </div>
            </div>

            {insights.areas_for_focus.length > 0 && (
              <div className="insight-section">
                <h4>🎯 Keep Practising</h4>
                <div className="insight-chips">
                  {insights.areas_for_focus.map((a, i) => (
                    <span key={i} className="insight-chip badge-blue">{a}</span>
                  ))}
                </div>
              </div>
            )}

            {insights.recommended_next_topics.length > 0 && (
              <div className="insight-section">
                <h4>🚀 Suggested Next Topics</h4>
                <div className="insight-chips">
                  {insights.recommended_next_topics.map((t, i) => (
                    <span key={i} className="insight-chip badge-purple">{t}</span>
                  ))}
                </div>
              </div>
            )}

            {insights.suggested_modifications.length > 0 && (
              <div className="insight-section">
                <h4>🛠️ Helpful Adjustments</h4>
                <div className="insight-chips">
                  {insights.suggested_modifications.map((m, i) => (
                    <span key={i} className="insight-chip badge-orange">{m}</span>
                  ))}
                </div>
              </div>
            )}

            {insights.parent_notes && (
              <div className="parent-note">
                📬 <strong>For parents/caregivers:</strong> {insights.parent_notes}
              </div>
            )}

            <button className="btn-ghost" style={{ marginTop: 16, fontSize: '0.88rem' }} onClick={() => { setInsights(null); }}>
              🔄 Refresh Insights
            </button>
          </>
        )}
      </div>

      {/* Session history */}
      <div className="session-history">
        <h2>🗓️ Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No sessions yet — start a lesson or chat with the AI tutor!</p>
        ) : (
          sessions.slice(0, 15).map((s, i) => (
            <div key={i} className="session-row">
              <div>
                <div className="session-title">
                  {s.type === 'tutor' ? '🤖' : '📚'} {s.subject || 'General'}{s.topic ? ` — ${s.topic}` : ''}
                </div>
                <div className="session-meta">
                  {new Date(s.date).toLocaleDateString()} · {s.duration_minutes || 0} min
                  {s.type === 'tutor' && s.message_count ? ` · ${s.message_count} messages` : ''}
                </div>
              </div>
              {s.quiz_score && (
                <span className="session-score">Quiz: {s.quiz_score}</span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
