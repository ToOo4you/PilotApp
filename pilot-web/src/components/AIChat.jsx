import React, { useState } from 'react';
import './AIChat.css';
import { API_BASE_URL } from '../lib/api';

const AIChat = ({ sessionId = 'default' }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const params = new URLSearchParams({
        session_id: sessionId,
        message: input
      });

      const response = await fetch(`${API_BASE_URL}/api/ai/chat?${params.toString()}`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      if (data.status === 'success') {
        const aiMessage = {
          role: 'assistant',
          content: data.response.message,
          timestamp: new Date().toISOString(),
          action: data.response.action_type,
          suggestions: data.response.followup_questions
        };
        setMessages(prev => [...prev, aiMessage]);
        setSuggestions(data.response.followup_questions || []);
      } else {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: 'I could not process that request. Please try again.',
            timestamp: new Date().toISOString()
          }
        ]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Chat service is unavailable right now. Please try again in a moment.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  return (
    <div className="ai-chat">
      <h2>🤖 Highway Pilot AI Assistant</h2>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>👋 Welcome! I'm your AI dispatcher. I can help you with:</p>
            <ul>
              <li>📍 Route optimization</li>
              <li>👥 Autonomous dispatch</li>
              <li>🔧 Predictive maintenance</li>
              <li>📊 Driver analytics</li>
              <li>📈 Demand forecasting</li>
            </ul>
            <p>Try asking: "Assign job JOB-123 to the best available driver"</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <span className="role">{msg.role === 'user' ? '👤' : '🤖'}</span>
              <p>{msg.content}</p>
              {msg.action && (
                <span className="action-badge">{msg.action}</span>
              )}
            </div>
          ))
        )}
        {loading && <div className="message ai loading">Thinking...</div>}
      </div>

      <div className="suggestions">
        {suggestions.length > 0 && (
          <>
            <p className="suggestions-label">💡 Suggested next actions:</p>
            <div className="suggestion-buttons">
              {suggestions.map((sugg, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setInput(sugg);
                  }}
                  className="suggestion-btn"
                >
                  {sugg}
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      <form onSubmit={sendMessage} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me to optimize routes, dispatch jobs, or analyze drivers..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? '⏳' : '📤'} Send
        </button>
      </form>
    </div>
  );
};

export default AIChat;
