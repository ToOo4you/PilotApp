import './SensoryPanel.css';
import { useSensorySettings } from '../lib/useSensorySettings';

const THEMES = [
  { value: 'default',      icon: '☀️', label: 'Default' },
  { value: 'calm',         icon: '🌿', label: 'Calm Green' },
  { value: 'dark',         icon: '🌙', label: 'Dark Mode' },
  { value: 'highcontrast', icon: '⚡', label: 'High Contrast' },
];

const FONT_SIZES = [
  { value: 'small',  label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large',  label: 'Large' },
  { value: 'xlarge', label: 'X-Large' },
];

export default function SensoryPanel() {
  const [settings, update] = useSensorySettings();

  function reset() {
    update({ fontSize: 'medium', theme: 'default', reduceAnimations: false, focusMode: false, audioSupport: false, dyslexicFont: false });
  }

  return (
    <div className="sensory-page">
      <h1>🎨 Display Settings</h1>
      <p className="subtitle">Adjust how EduLearn looks and feels so it's comfortable just for you.</p>

      {/* Colour theme */}
      <div className="sensory-section">
        <h3>🎨 Colour Theme</h3>
        <div className="option-grid">
          {THEMES.map((t) => (
            <button
              key={t.value}
              className={`option-btn${settings.theme === t.value ? ' active' : ''}`}
              onClick={() => update({ theme: t.value })}
            >
              <span className="opt-icon">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Font size */}
      <div className="sensory-section">
        <h3>🔡 Text Size</h3>
        <div className="option-grid">
          {FONT_SIZES.map((f) => (
            <button
              key={f.value}
              className={`option-btn${settings.fontSize === f.value ? ' active' : ''}`}
              onClick={() => update({ fontSize: f.value })}
              style={{ fontSize: f.value === 'small' ? '0.8rem' : f.value === 'large' ? '1.05rem' : f.value === 'xlarge' ? '1.2rem' : '0.92rem' }}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Toggle options */}
      <div className="sensory-section">
        <h3>⚙️ Accessibility Options</h3>
        <div className="toggle-group">
          {[
            { key: 'reduceAnimations', label: '🚫 Reduce animations and movement' },
            { key: 'focusMode',        label: '🎯 Focus mode (minimal sidebar)' },
            { key: 'dyslexicFont',     label: '📖 Dyslexia-friendly font' },
            { key: 'audioSupport',     label: '🔊 Audio support reminders' },
          ].map(({ key, label }) => (
            <div key={key} className="toggle-row">
              <label htmlFor={`tog-${key}`}>{label}</label>
              <label className="toggle">
                <input
                  id={`tog-${key}`}
                  type="checkbox"
                  checked={!!settings[key]}
                  onChange={() => update({ [key]: !settings[key] })}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* Live preview */}
      <div className="sensory-section">
        <h3>👁️ Preview</h3>
        <div className="preview-box">
          <h4>This is what your text looks like.</h4>
          <p>EduLearn AI is built so every learner feels comfortable and confident. You can change these settings any time!</p>
        </div>
        <button className="reset-btn" onClick={reset}>↩ Reset to defaults</button>
      </div>
    </div>
  );
}
