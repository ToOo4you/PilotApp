import { useState, useEffect } from 'react';

const STORAGE_KEY = 'edulearn_sensory';

const DEFAULTS = {
  fontSize: 'medium',       // small | medium | large | xlarge
  theme: 'default',         // default | calm | highcontrast | dark
  reduceAnimations: false,
  focusMode: false,         // hides sidebar decorations
  audioSupport: false,
  dyslexicFont: false,
};

export function useSensorySettings() {
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? { ...DEFAULTS, ...JSON.parse(saved) } : DEFAULTS;
    } catch {
      return DEFAULTS;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    applyTheme(settings);
  }, [settings]);

  function update(patch) {
    setSettings((prev) => ({ ...prev, ...patch }));
  }

  return [settings, update];
}

const FONT_SIZES = { small: '15px', medium: '17px', large: '20px', xlarge: '24px' };

const THEMES = {
  default:      { '--bg': '#f0f4ff', '--surface': '#ffffff', '--text': '#1e293b', '--text-muted': '#64748b', '--accent': '#6366f1', '--accent-dark': '#4338ca', '--border': '#e2e8f0' },
  calm:         { '--bg': '#f0faf4', '--surface': '#ffffff', '--text': '#1a3a2a', '--text-muted': '#4a7a5a', '--accent': '#22c55e', '--accent-dark': '#16a34a', '--border': '#bbf7d0' },
  highcontrast: { '--bg': '#000000', '--surface': '#1a1a1a', '--text': '#ffffff',  '--text-muted': '#cccccc', '--accent': '#ffff00', '--accent-dark': '#cccc00', '--border': '#555555' },
  dark:         { '--bg': '#0f172a', '--surface': '#1e293b', '--text': '#f1f5f9', '--text-muted': '#94a3b8', '--accent': '#818cf8', '--accent-dark': '#6366f1', '--border': '#334155' },
};

function applyTheme(settings) {
  const root = document.documentElement;
  const themeVars = THEMES[settings.theme] || THEMES.default;
  Object.entries(themeVars).forEach(([k, v]) => root.style.setProperty(k, v));
  root.style.setProperty('--font-size-base', FONT_SIZES[settings.fontSize] || FONT_SIZES.medium);
  root.style.setProperty('--font-family-base',
    settings.dyslexicFont
      ? '"OpenDyslexic", "Comic Sans MS", "Trebuchet MS", sans-serif'
      : '"Segoe UI", "Helvetica Neue", Arial, sans-serif'
  );
  root.style.setProperty('--animation-duration', settings.reduceAnimations ? '0.01ms' : '250ms');
}
