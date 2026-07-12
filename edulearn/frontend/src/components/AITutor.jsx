import { useState, useRef, useEffect } from 'react';
import './AITutor.css';
import { api } from '../lib/api';

const SUBJECTS = ['Math', 'Reading', 'Science', 'Writing', 'Social Skills', 'Life Skills', 'General'];

const TONE_EMOJI = { encouraging: '😊', celebratory: '🎉', calm: '🌿', patient: '🕊️' };

export default function AITutor({ profile, onSessionEnd }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [subject, setSubject] = useState('General');
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const sessionStart = useRef(Date.now());

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: 'user', content: text };
    const newHistory = [...messages.map((m) => ({ role: m.role, content: m.content })), userMsg];

    setMessages((prev) => [
      ...prev,
      { role: 'user', content: text, timestamp: new Date().toLocaleTimeString() },
    ]);
    setInput('');
    setLoading(true);

    try {
      const data = await api.tutorChat({
        learner_profile: profile,
        message: text,
        conversation_history: newHistory,
        current_subject: subject !== 'General' ? subject : null,
      });

      const r = data.response;
      setMessages((prev) => [
        ...prev,
        {
          role: 'tutor',
          content: r.message,
          tone: r.tone,
          next_step: r.next_step,
          break_suggested: r.break_suggested,
          visual_support: r.visual_support,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'tutor',
          content: `Oops! I had a little hiccup. Can you try again? I'm still here for you! 💙 (${err.message})`,
          tone: 'calm',
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function endSession() {
    if (messages.length === 0) return;
    onSessionEnd({
      type: 'tutor',
      subject,
      date: new Date().toISOString(),
      duration_minutes: Math.round((Date.now() - sessionStart.current) / 60000),
      message_count: messages.filter((m) => m.role === 'user').length,
    });
    setMessages([]);
    sessionStart.current = Date.now();
  }

  const noProfile = !profile.name;

  return (
    <div className="tutor-page">
      <div className="tutor-header">
        <h1>🤖 AI Tutor</h1>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div className="tutor-subject-select">
            <span>📚</span>
            <select value={subject} onChange={(e) => setSubject(e.target.value)}>
              {SUBJECTS.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          {messages.length > 0 && (
            <button className="btn-ghost" style={{ padding: '8px 14px', fontSize: '0.85rem' }} onClick={endSession}>
              ✅ End Session
            </button>
          )}
        </div>
      </div>

      <div className="tutor-messages">
        {messages.length === 0 ? (
          <div className="tutor-empty">
            <div className="empty-icon">🤖</div>
            <h3>Hi{profile.name ? `, ${profile.name}` : ''}! I'm your AI tutor.</h3>
            <p>
              Ask me anything about {subject !== 'General' ? subject : 'any subject'}.
              I'm patient, kind, and here just for you.
              There are no silly questions! 😊
            </p>
            {noProfile && (
              <p style={{ color: 'var(--accent)', fontWeight: 600 }}>
                💡 Tip: Set up your Learner Profile so I can personalise my answers even more!
              </p>
            )}
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i}>
              <div className={`msg-row ${msg.role}`}>
                <div className="msg-avatar">
                  {msg.role === 'tutor' ? '🤖' : '👤'}
                </div>
                <div>
                  <div className="msg-bubble">{msg.content}</div>
                  <div className="msg-meta">
                    {msg.role === 'tutor' && msg.tone && (
                      <span>{TONE_EMOJI[msg.tone] || '😊'} {msg.tone} &nbsp;·&nbsp;</span>
                    )}
                    {msg.timestamp}
                  </div>
                  {msg.role === 'tutor' && msg.next_step && (
                    <div className="next-step-card">👉 {msg.next_step}</div>
                  )}
                </div>
              </div>
              {msg.role === 'tutor' && msg.break_suggested && (
                <div className="break-card">
                  ☕ Suggested: Take a short break! Stretch, breathe, or grab some water. You deserve it! 🌟
                </div>
              )}
              {msg.role === 'tutor' && msg.visual_support && (
                <div style={{
                  background: '#f0f9ff',
                  border: '1px solid #bae6fd',
                  borderRadius: 10,
                  padding: '10px 14px',
                  fontSize: '0.88rem',
                  color: '#0369a1',
                }}>
                  🖼️ Visual idea: {msg.visual_support}
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="msg-row tutor">
            <div className="msg-avatar">🤖</div>
            <div className="msg-bubble" style={{ display: 'flex', gap: 6, alignItems: 'center', color: 'var(--text-muted)' }}>
              <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
              Thinking…
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="tutor-input-area">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question… (Enter to send, Shift+Enter for new line)"
          rows={2}
          disabled={loading}
        />
        <button className="send-btn" onClick={sendMessage} disabled={loading || !input.trim()} aria-label="Send">
          ➤
        </button>
      </div>
    </div>
  );
}
