import { AnimatePresence, motion } from 'motion/react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import FlareLanding from './components/FlareLanding.jsx';
import DashboardView from './components/DashboardView.jsx';
import { createMockAlert, createMockAlerts } from './data/mockAlerts.js';
import './styles/tokens.css';
import './styles/app.css';
import './styles/landing.css';
import './styles/dashboard.css';

const API_BASE = import.meta.env.VITE_API_BASE || '';

export default function App() {
  const [view, setView] = useState('landing');
  const [alerts, setAlerts] = useState(() => createMockAlerts());
  const [selected, setSelected] = useState(null);
  const [filters, setFilters] = useState({});
  const [activeSection, setActiveSection] = useState('overview');
  const [paused, setPaused] = useState(false);
  const [density, setDensity] = useState('comfortable');

  const updateFilters = useCallback((next) => {
    setFilters((current) => ({ ...current, ...next }));
    setSelected(null);
  }, []);

  const filteredAlerts = useMemo(() => {
    const query = filters.search?.trim().toLowerCase();
    return alerts.filter((alert) => {
      const matchesSeverity = !filters.severity || alert.severity === filters.severity;
      const matchesAttackType = !filters.attack_type || alert.attack_type === filters.attack_type;
      const haystack = [alert.id, alert.signature, alert.src_ip, alert.dest_ip, alert.attack_type, alert.mitre_technique].join(' ').toLowerCase();
      return matchesSeverity && matchesAttackType && (!query || haystack.includes(query));
    });
  }, [alerts, filters]);

  useEffect(() => {
    if (view !== 'dashboard' || paused) return undefined;
    let eventSource;
    try {
      eventSource = new EventSource(`${API_BASE}/api/v1/stream`);
      eventSource.onmessage = (event) => {
        try {
          const incoming = JSON.parse(event.data);
          if (incoming?.id) setAlerts((current) => [{ ...incoming }, ...current].slice(0, 200));
        } catch {
          // Keep the demo buffer alive when a malformed event is received.
        }
      };
    } catch {
      eventSource = undefined;
    }
    return () => eventSource?.close();
  }, [view, paused]);

  useEffect(() => {
    if (view !== 'dashboard') return undefined;
    const onKeyDown = (event) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement) return;
      if (event.key === 'Escape') { setSelected(null); return; }
      if (activeSection !== 'feed' && activeSection !== 'overview') return;
      if (event.key === 'j' || event.key === 'ArrowDown') {
        event.preventDefault();
        setSelected((current) => {
          const currentIndex = filteredAlerts.findIndex((alert) => alert.id === current?.id);
          return filteredAlerts[Math.min(currentIndex + 1, filteredAlerts.length - 1)] || null;
        });
      }
      if (event.key === 'k' || event.key === 'ArrowUp') {
        event.preventDefault();
        setSelected((current) => {
          const currentIndex = filteredAlerts.findIndex((alert) => alert.id === current?.id);
          return filteredAlerts[Math.max(currentIndex <= 0 ? 1 : currentIndex - 1, 0)] || null;
        });
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [activeSection, filteredAlerts, view]);

  const handleAddAlert = useCallback(() => {
    if (paused) return;
    setAlerts((current) => [createMockAlert(current.length + 1), ...current].slice(0, 200));
  }, [paused]);

  const handleNavigate = useCallback((section) => {
    setActiveSection(section);
    setSelected(null);
  }, []);

  return (
    <AnimatePresence mode="wait" initial={false}>
      {view === 'landing' ? (
        <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 0.985 }} transition={{ duration: 0.35 }}><FlareLanding onLaunch={() => setView('dashboard')} /></motion.div>
      ) : (
        <motion.div key="dashboard" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.35 }}>
    <DashboardView
      alerts={alerts}
      filteredAlerts={filteredAlerts}
      selected={selected}
      onSelect={setSelected}
      onClose={() => setSelected(null)}
      filters={filters}
      onFilterChange={updateFilters}
      activeSection={activeSection}
      onNavigate={handleNavigate}
      paused={paused}
      onTogglePaused={() => setPaused((current) => !current)}
      density={density}
      onDensityChange={setDensity}
      onAddAlert={handleAddAlert}
    />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
