import { useState } from 'react';
import './AdaptiveLesson.css';
import { api } from '../lib/api';

const SUBJECTS = ['Math', 'Reading', 'Science', 'Writing', 'Social Skills', 'Life Skills'];
const FORMATS  = [
  { value: 'visual',      label: '👁️ Visual' },
  { value: 'story',       label: '📖 Story-based' },
  { value: 'game',        label: '🎮 Game-style' },
  { value: 'standard',    label: '📝 Standard' },
];
const TYPE_COLOR = { visual: 'badge-blue', hands_on: 'badge-orange', discussion: 'badge-purple', game: 'badge-green' };

export default function AdaptiveLesson({ profile, onSessionEnd }) {
  const [step, setStep] = useState('setup'); // setup | loading | lesson | quiz | done
  const [config, setConfig] = useState({ subject: 'Math', topic: '', duration: 20, format: 'visual' });
  const [lesson, setLesson] = useState(null);
  const [activityIndex, setActivityIndex] = useState(0);
  const [doneActivities, setDoneActivities] = useState(new Set());
  const [quiz, setQuiz] = useState(null);
  const [quizLoading, setQuizLoading] = useState(false);
  const [answers, setAnswers] = useState({});
  const [revealed, setRevealed] = useState(false);
  const [error, setError] = useState('');
  const sessionStart = useState(Date.now())[0];

  async function startLesson() {
    if (!config.topic.trim()) { setError('Please enter a topic!'); return; }
    setError('');
    setStep('loading');
    try {
      const data = await api.generateLesson({
        learner_profile: profile,
        subject: config.subject,
        topic: config.topic,
        duration_minutes: config.duration,
        lesson_format: config.format,
      });
      setLesson(data.lesson);
      setActivityIndex(0);
      setDoneActivities(new Set());
      setQuiz(null);
      setAnswers({});
      setRevealed(false);
      setStep('lesson');
    } catch (err) {
      setError(`Could not generate lesson: ${err.message}`);
      setStep('setup');
    }
  }

  async function loadQuiz() {
    setQuizLoading(true);
    try {
      const data = await api.generateQuiz({
        learner_profile: profile,
        subject: config.subject,
        topic: config.topic,
        question_count: 4,
      });
      setQuiz(data.quiz);
      setStep('quiz');
    } catch (err) {
      setError(`Could not load quiz: ${err.message}`);
    } finally {
      setQuizLoading(false);
    }
  }

  function markDone(i) {
    setDoneActivities((prev) => new Set([...prev, i]));
    if (i < lesson.activities.length - 1) setActivityIndex(i + 1);
  }

  function selectAnswer(qi, opt) {
    if (revealed) return;
    setAnswers((prev) => ({ ...prev, [qi]: opt }));
  }

  function submitQuiz() { setRevealed(true); }

  function finishSession() {
    const score = quiz
      ? quiz.filter((q, i) => answers[i] === q.correct_answer).length
      : null;
    onSessionEnd({
      type: 'lesson',
      subject: config.subject,
      topic: config.topic,
      date: new Date().toISOString(),
      duration_minutes: Math.round((Date.now() - sessionStart) / 60000),
      quiz_score: score !== null ? `${score}/${quiz.length}` : null,
    });
    setStep('setup');
    setLesson(null);
    setConfig((c) => ({ ...c, topic: '' }));
  }

  /* ── SETUP ─────────────────────────────────────────────── */
  if (step === 'setup') return (
    <div className="lesson-page">
      <div className="lesson-setup">
        <h1>📚 Generate a Lesson</h1>
        <p className="subtitle">Tell the AI what you want to learn — it will create a lesson just for you!</p>
        <div className="lesson-setup-form">
          <div className="form-group">
            <label>Subject</label>
            <select value={config.subject} onChange={(e) => setConfig((c) => ({ ...c, subject: e.target.value }))}>
              {SUBJECTS.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Duration (minutes)</label>
            <select value={config.duration} onChange={(e) => setConfig((c) => ({ ...c, duration: Number(e.target.value) }))}>
              {[10, 15, 20, 30, 45].map((d) => <option key={d}>{d}</option>)}
            </select>
          </div>
          <div className="form-group full-row">
            <label>Topic <span style={{ color: 'var(--accent)' }}>*</span></label>
            <input
              type="text"
              placeholder="e.g. Addition, Animals, Feelings, Reading Comprehension…"
              value={config.topic}
              onChange={(e) => setConfig((c) => ({ ...c, topic: e.target.value }))}
              onKeyDown={(e) => e.key === 'Enter' && startLesson()}
            />
          </div>
          <div className="form-group full-row">
            <label>Lesson Style</label>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {FORMATS.map((f) => (
                <label key={f.value} style={{
                  padding: '9px 18px', border: `2px solid ${config.format === f.value ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 10, cursor: 'pointer', background: config.format === f.value ? '#ede9fe' : 'var(--surface)',
                  color: config.format === f.value ? 'var(--accent-dark)' : 'var(--text)', fontWeight: config.format === f.value ? 700 : 400,
                  fontSize: '0.92rem', userSelect: 'none',
                }}>
                  <input type="radio" style={{ display: 'none' }} checked={config.format === f.value} onChange={() => setConfig((c) => ({ ...c, format: f.value }))} />
                  {f.label}
                </label>
              ))}
            </div>
          </div>
          <div className="lesson-setup-actions">
            <button className="btn-primary" onClick={startLesson}>🚀 Generate Lesson</button>
            {error && <span style={{ color: 'var(--accent)', fontWeight: 600 }}>{error}</span>}
          </div>
        </div>
      </div>
    </div>
  );

  /* ── LOADING ────────────────────────────────────────────── */
  if (step === 'loading') return (
    <div className="lesson-page" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: 20 }}>
      <div className="spinner" style={{ width: 52, height: 52, borderWidth: 4 }} />
      <h2>Creating your personalised lesson…</h2>
      <p style={{ color: 'var(--text-muted)' }}>The AI is tailoring everything just for {profile.name || 'you'}. Almost ready! 🌟</p>
    </div>
  );

  /* ── LESSON ─────────────────────────────────────────────── */
  if (step === 'lesson' && lesson) {
    const activity = lesson.activities[activityIndex];
    return (
      <div className="lesson-page">
        <div className="lesson-header">
          <h1>{lesson.title}</h1>
          <div className="lesson-meta">
            <span className="lesson-meta-chip">📚 {lesson.subject}</span>
            <span className="lesson-meta-chip">🎓 Grade {lesson.grade_level}</span>
            <span className="lesson-meta-chip">⏱ {config.duration} min</span>
          </div>
        </div>

        {lesson.objectives.length > 0 && (
          <div className="lesson-objectives">
            <h3>🎯 What You'll Learn</h3>
            <ul>{lesson.objectives.map((o, i) => <li key={i}>{o}</li>)}</ul>
          </div>
        )}

        <div className="lesson-intro">{lesson.introduction}</div>

        {/* Break reminders */}
        {lesson.break_reminders.slice(0, 1).map((b, i) => (
          <div key={i} className="break-banner">☕ Reminder: {b}</div>
        ))}

        {/* Activity stepper */}
        <div className="activity-stepper">
          <div className="stepper-nav">
            {lesson.activities.map((_, i) => (
              <button
                key={i}
                className={`stepper-dot${i === activityIndex ? ' active' : ''}${doneActivities.has(i) ? ' done' : ''}`}
                onClick={() => setActivityIndex(i)}
                aria-label={`Activity ${i + 1}`}
              >
                {doneActivities.has(i) ? '✓' : i + 1}
              </button>
            ))}
          </div>

          {activity && (
            <div className="activity-card">
              <div className="activity-type-badge">
                <span className={`badge ${TYPE_COLOR[activity.type] || 'badge-blue'}`}>{activity.type}</span>
              </div>
              <h2>{activity.name}</h2>
              <p>{activity.description}</p>
              <div className="activity-timer">⏱ About {activity.duration_minutes} minute{activity.duration_minutes !== 1 ? 's' : ''}</div>
              <div className="activity-controls">
                {activityIndex > 0 && (
                  <button className="btn-ghost" onClick={() => setActivityIndex((i) => i - 1)}>← Back</button>
                )}
                <button className="btn-primary" onClick={() => markDone(activityIndex)}>
                  {activityIndex < lesson.activities.length - 1 ? 'Done — Next Activity ▶' : '✅ Finish Activities'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Vocabulary */}
        {lesson.key_vocabulary.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <h2>📖 Key Words</h2>
            <div className="vocab-grid">
              {lesson.key_vocabulary.map((v, i) => (
                <div key={i} className="vocab-card">
                  <div className="vocab-word">{v.word}</div>
                  <div className="vocab-def">{v.definition}</div>
                  {v.example && <div className="vocab-ex">"{v.example}"</div>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Visual cues */}
        {lesson.visual_cues.length > 0 && (
          <div style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: 12, padding: '16px 20px', marginBottom: 20 }}>
            <strong style={{ color: '#0369a1' }}>🖼️ Visual Tips:</strong>
            <ul style={{ margin: '8px 0 0', paddingLeft: 20 }}>
              {lesson.visual_cues.map((c, i) => <li key={i} style={{ color: '#0369a1', fontSize: '0.92rem', marginBottom: 4 }}>{c}</li>)}
            </ul>
          </div>
        )}

        {/* Summary + actions */}
        <div className="lesson-summary">
          <h2>🌈 Lesson Summary</h2>
          <p>{lesson.summary}</p>
        </div>

        {lesson.accommodation_notes && (
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 20 }}>
            📋 <em>{lesson.accommodation_notes}</em>
          </p>
        )}

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={loadQuiz} disabled={quizLoading}>
            {quizLoading ? '⏳ Loading…' : '🧠 Take a Quiz'}
          </button>
          <button className="btn-ghost" onClick={finishSession}>✅ Mark Complete</button>
          <button className="btn-ghost" onClick={() => setStep('setup')}>← New Lesson</button>
        </div>
      </div>
    );
  }

  /* ── QUIZ ───────────────────────────────────────────────── */
  if (step === 'quiz' && quiz) {
    const score = quiz.filter((q, i) => answers[i] === q.correct_answer).length;
    if (revealed) {
      const pct = Math.round((score / quiz.length) * 100);
      return (
        <div className="lesson-page">
          <div className="quiz-score-card">
            <div style={{ fontSize: '3rem', marginBottom: 12 }}>
              {pct === 100 ? '🏆' : pct >= 75 ? '⭐' : pct >= 50 ? '💪' : '🌱'}
            </div>
            <h2>You scored {score}/{quiz.length}!</h2>
            <p>
              {pct === 100 ? "Perfect score — you're incredible! 🎉" :
               pct >= 75 ? "Amazing work! You really know this! 🌟" :
               pct >= 50 ? "Great effort! Keep practising and you'll get there! 💪" :
               "Every attempt makes you stronger! Let's review and try again! 🌱"}
            </p>
          </div>

          <div className="lesson-quiz" style={{ marginTop: 24 }}>
            {quiz.map((q, qi) => {
              const isCorrect = answers[qi] === q.correct_answer;
              return (
                <div key={qi} className="quiz-question-card">
                  <h3>{qi + 1}. {q.question}</h3>
                  {q.options.map((opt) => {
                    const isSelected = answers[qi] === opt;
                    const isRight = opt === q.correct_answer;
                    return (
                      <div key={opt} className={`quiz-option${isRight ? ' correct' : isSelected ? ' incorrect' : ''}`}>
                        {isRight ? '✅' : isSelected ? '❌' : '⚪'} {opt}
                      </div>
                    );
                  })}
                  {!isCorrect && <p className="quiz-hint">💡 Hint: {q.hint}</p>}
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 8, flexWrap: 'wrap' }}>
            <button className="btn-primary" onClick={finishSession}>✅ Finish & Save Session</button>
            <button className="btn-ghost" onClick={() => { setAnswers({}); setRevealed(false); }}>🔄 Retry Quiz</button>
            <button className="btn-ghost" onClick={() => setStep('lesson')}>← Back to Lesson</button>
          </div>
        </div>
      );
    }

    return (
      <div className="lesson-page">
        <h1>🧠 Quick Quiz — {config.topic}</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
          No pressure! Choose the best answer for each question. There's a hint if you need it. 😊
        </p>
        <div className="lesson-quiz">
          {quiz.map((q, qi) => (
            <div key={qi} className="quiz-question-card">
              <h3>{qi + 1}. {q.question}</h3>
              {q.options.map((opt) => (
                <div
                  key={opt}
                  className={`quiz-option${answers[qi] === opt ? ' selected' : ''}`}
                  onClick={() => selectAnswer(qi, opt)}
                >
                  {answers[qi] === opt ? '🔵' : '⚪'} {opt}
                </div>
              ))}
              {q.image_description && (
                <p style={{ fontSize: '0.85rem', color: '#0369a1', marginTop: 8 }}>🖼️ {q.image_description}</p>
              )}
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            className="btn-primary"
            onClick={submitQuiz}
            disabled={Object.keys(answers).length < quiz.length}
          >
            🎯 Submit Answers
          </button>
          <button className="btn-ghost" onClick={() => setStep('lesson')}>← Back</button>
        </div>
        {Object.keys(answers).length < quiz.length && (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: 10 }}>
            Answer all {quiz.length} questions before submitting.
          </p>
        )}
      </div>
    );
  }

  return null;
}
