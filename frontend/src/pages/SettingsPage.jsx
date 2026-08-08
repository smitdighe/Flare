import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext.jsx';
import { useTheme } from '../contexts/ThemeContext.jsx';
import Icon from '../components/Icon.jsx';

const API_BASE = import.meta.env.VITE_API_BASE || '';

const TABS = [
  { id: 'profile', label: 'Profile', icon: 'person' },
  { id: 'security', label: 'Security', icon: 'lock' },
  { id: 'appearance', label: 'Appearance', icon: 'palette' },
];

function ProfileTab({ user, authFetch }) {
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  const handleSave = async () => {
    setSaving(true);
    setMsg('');
    try {
      const res = await authFetch(`${API_BASE}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      });
      if (res.ok) setMsg('Profile updated');
      else setMsg('Failed to update profile');
    } catch { setMsg('Network error'); }
    setSaving(false);
  };

  return (
    <div className="space-y-4">
      <h3 className="font-mono-ui text-[11px] uppercase tracking-[0.12em] text-amber">Profile Settings</h3>
      <div className="space-y-3">
        <label className="block">
          <span className="font-mono-ui text-[9px] uppercase tracking-[0.1em] text-ash-dark">Name</span>
          <input value={name} onChange={(e) => setName(e.target.value)} className="mt-1 block w-full border border-line-strong bg-ink-800 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none focus:border-amber" />
        </label>
        <label className="block">
          <span className="font-mono-ui text-[9px] uppercase tracking-[0.1em] text-ash-dark">Email</span>
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" className="mt-1 block w-full border border-line-strong bg-ink-800 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none focus:border-amber" />
        </label>
      </div>
      <button onClick={handleSave} disabled={saving} className="ghost-button border border-amber px-4 py-2 font-mono-ui text-[9px] uppercase tracking-[0.1em] text-amber hover:bg-amber/10 disabled:opacity-50">
        {saving ? 'Saving...' : 'Save Profile'}
      </button>
      {msg && <p className="font-mono-ui text-[10px] text-green">{msg}</p>}
    </div>
  );
}

function SecurityTab({ authFetch }) {
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  const handleChange = async () => {
    setSaving(true);
    setMsg('');
    try {
      const res = await authFetch(`${API_BASE}/api/v1/auth/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
      });
      if (res.ok) { setMsg('Password changed'); setCurrentPw(''); setNewPw(''); }
      else { const err = await res.json(); setMsg(err.detail || 'Failed'); }
    } catch { setMsg('Network error'); }
    setSaving(false);
  };

  return (
    <div className="space-y-4">
      <h3 className="font-mono-ui text-[11px] uppercase tracking-[0.12em] text-amber">Security</h3>
      <div className="space-y-3">
        <label className="block">
          <span className="font-mono-ui text-[9px] uppercase tracking-[0.1em] text-ash-dark">Current Password</span>
          <input value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} type="password" className="mt-1 block w-full border border-line-strong bg-ink-800 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none focus:border-amber" />
        </label>
        <label className="block">
          <span className="font-mono-ui text-[9px] uppercase tracking-[0.1em] text-ash-dark">New Password</span>
          <input value={newPw} onChange={(e) => setNewPw(e.target.value)} type="password" className="mt-1 block w-full border border-line-strong bg-ink-800 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none focus:border-amber" />
        </label>
      </div>
      <button onClick={handleChange} disabled={saving || !currentPw || !newPw} className="ghost-button border border-amber px-4 py-2 font-mono-ui text-[9px] uppercase tracking-[0.1em] text-amber hover:bg-amber/10 disabled:opacity-50">
        {saving ? 'Changing...' : 'Change Password'}
      </button>
      {msg && <p className="font-mono-ui text-[10px] text-green">{msg}</p>}
    </div>
  );
}

function AppearanceTab() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className="space-y-4">
      <h3 className="font-mono-ui text-[11px] uppercase tracking-[0.12em] text-amber">Appearance</h3>
      <div className="flex items-center gap-3">
        <span className="font-mono-ui text-[10px] uppercase tracking-[0.1em] text-ash-dark">Theme</span>
        <button onClick={toggleTheme} className="ghost-button border border-line-strong px-3 py-1.5 font-mono-ui text-[9px] uppercase tracking-[0.1em] text-paper hover:bg-ink-800">
          <Icon name={theme === 'dark' ? 'light_mode' : 'dark_mode'} size={14} className="mr-1" />
          {theme === 'dark' ? 'Dark' : 'Light'}
        </button>
      </div>
    </div>
  );
}

export default function SettingsPage({ onBack }) {
  const { user, authFetch } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="min-h-screen bg-ink-950 px-4 py-6 lg:px-7 lg:py-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6 flex items-center gap-3">
          <button onClick={onBack} className="ghost-button border border-line-strong px-2 py-1 font-mono-ui text-[9px] uppercase tracking-[0.1em] text-ash-dark hover:text-paper">
            <Icon name="arrow_back" size={14} />
          </button>
          <h1 className="font-display text-lg text-paper">Settings</h1>
        </div>
        <div className="flex gap-1 border-b border-line-strong">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 border-b-2 px-3 py-2 font-mono-ui text-[9px] uppercase tracking-[0.1em] transition-colors ${
                activeTab === tab.id ? 'border-amber text-amber' : 'border-transparent text-ash-dark hover:text-paper'
              }`}
            >
              <Icon name={tab.icon} size={14} />
              {tab.label}
            </button>
          ))}
        </div>
        <div className="mt-6">
          {activeTab === 'profile' && <ProfileTab user={user} authFetch={authFetch} />}
          {activeTab === 'security' && <SecurityTab authFetch={authFetch} />}
          {activeTab === 'appearance' && <AppearanceTab />}
        </div>
      </div>
    </div>
  );
}
