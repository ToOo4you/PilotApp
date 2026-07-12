import { useState } from 'react';
import './LearnerProfile.css';

const NEEDS_OPTIONS = [
  { value: 'autism',              label: '🧩 Autism' },
  { value: 'adhd',                label: '⚡ ADHD' },
  { value: 'dyslexia',            label: '📖 Dyslexia' },
  { value: 'dyscalculia',         label: '🔢 Dyscalculia' },
  { value: 'sensory_processing',  label: '🌈 Sensory Processing' },
];

const STYLE_OPTIONS = [
  { value: 'visual',          label: '👁️ Visual' },
  { value: 'auditory',        label: '👂 Auditory' },
  { value: 'kinesthetic',     label: '🖐️ Kinesthetic' },
  { value: 'reading_writing', label: '✍️ Reading/Writing' },
];

const COMM_OPTIONS = [
  { value: 'verbal',          label: '🗣️ Verbal' },
  { value: 'AAC',             label: '📱 AAC Device' },
  { value: 'written',         label: '✏️ Written' },
  { value: 'visual_symbols',  label: '🖼️ Visual Symbols' },
];

const SUBJECTS = ['Math', 'Reading', 'Science', 'Writing', 'Social Skills', 'Life Skills'];
const SKILL_LEVELS = ['Pre-K', 'Kindergarten', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6', 'Grade 7+'];

export default function LearnerProfile({ profile, onSave, onBack }) {
  const [form, setForm] = useState({ ...profile });
  const [interestInput, setInterestInput] = useState('');
  const [strengthInput, setStrengthInput] = useState('');
  const [saved, setSaved] = useState(false);

  function set(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  }

  function toggleNeed(value) {
    const current = form.primary_needs || [];
    set('primary_needs', current.includes(value) ? current.filter((v) => v !== value) : [...current, value]);
  }

  function toggleSensory(key) {
    set('sensory_preferences', { ...form.sensory_preferences, [key]: !form.sensory_preferences?.[key] });
  }

  function addInterest() {
    const v = interestInput.trim();
    if (v && !(form.interests || []).includes(v)) {
      set('interests', [...(form.interests || []), v]);
    }
    setInterestInput('');
  }

  function removeInterest(v) {
    set('interests', (form.interests || []).filter((i) => i !== v));
  }

  function addStrength() {
    const v = strengthInput.trim();
    if (v && !(form.strengths || []).includes(v)) {
      set('strengths', [...(form.strengths || []), v]);
    }
    setStrengthInput('');
  }

  function removeStrength(v) {
    set('strengths', (form.strengths || []).filter((s) => s !== v));
  }

  function setSkillLevel(subject, level) {
    set('skill_levels', { ...form.skill_levels, [subject.toLowerCase()]: level });
  }

  function handleSave() {
    onSave({ ...form });
    setSaved(true);
  }

  return (
    <div className="profile-page">
      <h1>👤 Learner Profile</h1>
      <p className="subtitle">Tell us about you so everything can be made just right for your mind. 🌟</p>

      {/* Basic Info */}
      <div className="profile-section">
        <h3>Basic Information</h3>
        <div className="form-row">
          <div className="form-group">
            <label>First Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              placeholder="e.g. Alex"
            />
          </div>
          <div className="form-group">
            <label>Age</label>
            <input
              type="number"
              min={4} max={21}
              value={form.age}
              onChange={(e) => set('age', Number(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>Grade Level</label>
            <select value={form.grade_level} onChange={(e) => set('grade_level', e.target.value)}>
              {SKILL_LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Learning Needs */}
      <div className="profile-section">
        <h3>Learning Profile <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>(select all that apply)</span></h3>
        <div className="chip-group">
          {NEEDS_OPTIONS.map((o) => (
            <label key={o.value} className={`chip-label${(form.primary_needs || []).includes(o.value) ? ' checked' : ''}`}>
              <input type="checkbox" checked={(form.primary_needs || []).includes(o.value)} onChange={() => toggleNeed(o.value)} />
              {o.label}
            </label>
          ))}
        </div>
      </div>

      {/* Learning Style */}
      <div className="profile-section">
        <h3>How I Learn Best</h3>
        <div className="chip-group" style={{ marginBottom: 20 }}>
          {STYLE_OPTIONS.map((o) => (
            <label key={o.value} className={`chip-label${form.learning_style === o.value ? ' checked' : ''}`}>
              <input type="radio" checked={form.learning_style === o.value} onChange={() => set('learning_style', o.value)} />
              {o.label}
            </label>
          ))}
        </div>
        <h3>How I Communicate</h3>
        <div className="chip-group">
          {COMM_OPTIONS.map((o) => (
            <label key={o.value} className={`chip-label${form.communication_style === o.value ? ' checked' : ''}`}>
              <input type="radio" checked={form.communication_style === o.value} onChange={() => set('communication_style', o.value)} />
              {o.label}
            </label>
          ))}
        </div>
      </div>

      {/* Interests */}
      <div className="profile-section">
        <h3>🌟 My Interests</h3>
        <div className="interest-tags">
          {(form.interests || []).map((i) => (
            <span key={i} className="interest-tag">
              {i}
              <button onClick={() => removeInterest(i)} aria-label={`Remove ${i}`}>✕</button>
            </span>
          ))}
        </div>
        <div className="interest-input-row">
          <input
            type="text"
            placeholder="e.g. dinosaurs, minecraft, trains…"
            value={interestInput}
            onChange={(e) => setInterestInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addInterest()}
          />
          <button className="btn-primary" onClick={addInterest}>Add</button>
        </div>
      </div>

      {/* Strengths */}
      <div className="profile-section">
        <h3>💪 My Strengths</h3>
        <div className="interest-tags">
          {(form.strengths || []).map((s) => (
            <span key={s} className="interest-tag" style={{ background: '#dcfce7', color: '#16a34a' }}>
              {s}
              <button onClick={() => removeStrength(s)} aria-label={`Remove ${s}`}>✕</button>
            </span>
          ))}
        </div>
        <div className="interest-input-row">
          <input
            type="text"
            placeholder="e.g. great memory, creative, kind…"
            value={strengthInput}
            onChange={(e) => setStrengthInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addStrength()}
          />
          <button className="btn-primary" onClick={addStrength}>Add</button>
        </div>
      </div>

      {/* Subject levels */}
      <div className="profile-section">
        <h3>📚 Subject Levels</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          {SUBJECTS.map((subj) => (
            <div key={subj} className="form-group">
              <label>{subj}</label>
              <select
                value={form.skill_levels?.[subj.toLowerCase()] || ''}
                onChange={(e) => setSkillLevel(subj, e.target.value)}
              >
                <option value="">— Not set —</option>
                {SKILL_LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
          ))}
        </div>
      </div>

      {/* Sensory preferences */}
      <div className="profile-section">
        <h3>🌈 Sensory Preferences</h3>
        <div className="toggle-group">
          {[
            { key: 'low_distraction',   label: 'Low-distraction mode (minimal visuals)' },
            { key: 'audio_support',     label: 'I like audio support / text-to-speech' },
            { key: 'extra_think_time',  label: 'I need extra time to think and respond' },
            { key: 'frequent_breaks',   label: 'I benefit from frequent short breaks' },
          ].map(({ key, label }) => (
            <div key={key} className="toggle-row">
              <label htmlFor={`sens-${key}`}>{label}</label>
              <label className="toggle">
                <input
                  id={`sens-${key}`}
                  type="checkbox"
                  checked={!!form.sensory_preferences?.[key]}
                  onChange={() => toggleSensory(key)}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="profile-actions">
        <button className="btn-primary" onClick={handleSave}>💾 Save Profile</button>
        <button className="btn-ghost" onClick={onBack}>← Back</button>
        {saved && <span className="save-success">✅ Profile saved!</span>}
      </div>
    </div>
  );
}
