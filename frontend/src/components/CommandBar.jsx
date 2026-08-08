import Icon from './Icon.jsx';
import StatusDot from './StatusDot.jsx';
import { useTheme } from '../contexts/ThemeContext.jsx';

const API_BASE = import.meta.env.VITE_API_BASE || '';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: 'dashboard' },
  { id: 'feed', label: 'Live feed', icon: 'view_list' },
  { id: 'health', label: 'Health metrics', icon: 'monitor_heart' },
  { id: 'timeline', label: 'System logs', icon: 'terminal' },
  { id: 'correlated', label: 'Threat clusters', icon: 'hub' },
  { id: 'eval', label: 'Evaluation', icon: 'query_stats' },
  { id: 'rules', label: 'Rules', icon: 'tune' },
  { id: 'playbooks', label: 'Playbooks', icon: 'fact_check' },
  { id: 'notifications', label: 'Notifications', icon: 'notifications' },
  { id: 'export', label: 'Export', icon: 'download' },
];

export { NAV_ITEMS };

export default function CommandBar({ search, onSearch, paused, onTogglePaused, density, onDensityChange, onMobileNav, onOpenCommands, onLogout, connectionStatus }) {
  const { theme, toggleTheme } = useTheme();
  return (
    <header className="fixed inset-x-0 top-0 z-40 flex h-[var(--topbar-height)] items-center border-b border-line-strong bg-ink-950/96 px-4 backdrop-blur-sm lg:px-6">
      <div className="flex min-w-0 items-center gap-3 lg:w-[var(--rail-width)]">
        <button type="button" className="ghost-button flex h-8 w-8 items-center justify-center lg:hidden" onClick={onMobileNav} aria-label="Open navigation">
          <Icon name="menu" size={18} />
        </button>
        <a href="#dashboard" className="flare-logo-frame">
          <img src="/flare-logo.png" alt="Flare" className="h-6 w-6 object-contain" />
        </a>
        <div className="hidden min-w-0 sm:block">
          <div className="font-mono-ui text-[11px] font-semibold tracking-[0.12em] text-paper">FLARE <span className="text-ash-dark">// OPS</span></div>
          <div className="font-mono-ui text-[8px] uppercase tracking-[0.12em] text-ash-dark">incident command{API_BASE ? ` // ${API_BASE}` : ''}</div>
        </div>
      </div>
      <div className="hidden min-w-0 flex-1 items-center px-5 lg:flex">
        <div className="signal-line truncate border-l border-line pl-5 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-ash">
          <span className="text-red">CRITICAL</span> // RDP brute force against 10.24.1.8
          <span className="mx-2 text-ash-dark">&middot;</span>
          <span className="text-amber">WATCH</span> // outbound TLS beacon drift
        </div>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <label className="hidden items-center gap-2 border border-line-strong bg-ink-900 px-2.5 py-1.5 md:flex">
          <Icon name="search" size={15} className="text-ash-dark" />
          <span className="font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark">Search</span>
          <input
            aria-label="Search alerts"
            value={search}
            onChange={(event) => onSearch(event.target.value)}
            className="w-32 bg-transparent font-mono-ui text-[10px] text-paper outline-hidden placeholder:text-ash-dark lg:w-44"
            placeholder="IP / ID / SIGNATURE"
          />
        </label>
        <button
          type="button"
          className="command-trigger ghost-button hidden h-8 items-center gap-2 px-2.5 font-mono-ui text-[9px] uppercase tracking-[0.1em] md:inline-flex"
          onClick={onOpenCommands}
        >
          <Icon name="terminal" size={14} />
          <span className="hidden xl:inline">command</span>
          <kbd className="text-ash-dark">&#8984;K</kbd>
        </button>
        <button
          type="button"
          className="ghost-button hidden h-8 items-center gap-2 border border-line-strong px-2.5 font-mono-ui text-[9px] uppercase tracking-[0.1em] md:flex"
          data-active={density === 'compact'}
          onClick={() => onDensityChange(density === 'compact' ? 'comfortable' : 'compact')}
          aria-pressed={density === 'compact'}
        >
          <Icon name="density_small" size={15} />
          <span className="hidden xl:inline">{density === 'compact' ? 'compact' : 'comfortable'}</span>
        </button>
        <button
          type="button"
          className="ghost-button hidden h-8 items-center gap-1 px-2 font-mono-ui text-[9px] uppercase tracking-[0.1em] md:flex"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          <Icon name={theme === 'dark' ? 'light_mode' : 'dark_mode'} size={15} />
          <span className="hidden xl:inline">{theme === 'dark' ? 'light' : 'dark'}</span>
        </button>
        <button
          type="button"
          className={`inline-flex h-8 items-center gap-2 border px-2.5 font-mono-ui text-[9px] uppercase tracking-[0.1em] transition-colors ${paused ? 'border-yellow bg-yellow/10 text-yellow' : 'border-green/50 bg-green/5 text-green'}`}
          onClick={onTogglePaused}
          aria-pressed={paused}
        >
          <StatusDot tone={paused ? 'medium' : 'live'} pulse={!paused} />
          <span className="hidden sm:inline">{paused ? 'paused' : 'live'}</span>
          <Icon name={paused ? 'play_arrow' : 'pause'} size={14} />
        </button>
        <div className={`hidden items-center gap-1.5 border px-2 py-1.5 font-mono-ui text-[8px] uppercase tracking-[0.1em] sm:flex ${
          connectionStatus === 'connected' ? 'border-green/30 text-green' :
          connectionStatus === 'connecting' ? 'border-yellow/30 text-yellow' :
          'border-red/30 text-red'
        }`}>
          <span className={`h-1.5 w-1.5 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green' :
            connectionStatus === 'connecting' ? 'bg-yellow animate-pulse' :
            'bg-red'
          }`} />
          <span>{connectionStatus === 'connected' ? 'WS' : connectionStatus === 'connecting' ? 'WS...' : 'SSE'}</span>
        </div>
        {onLogout && (
          <>
            <a
              href="/settings"
              className="ghost-button hidden h-8 items-center gap-1 border border-line-strong px-2.5 font-mono-ui text-[9px] uppercase tracking-[0.1em] md:flex"
            >
              <Icon name="settings" size={14} />
              <span className="hidden xl:inline">settings</span>
            </a>
            <button
              type="button"
              className="ghost-button hidden h-8 items-center gap-2 border border-line-strong px-2.5 font-mono-ui text-[9px] uppercase tracking-[0.1em] md:flex"
              onClick={onLogout}
            >
              <Icon name="logout" size={14} />
              <span className="hidden xl:inline">logout</span>
            </button>
          </>
        )}
      </div>
    </header>
  );
}
