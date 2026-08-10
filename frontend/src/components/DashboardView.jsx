import { AnimatePresence, motion } from 'motion/react';
import { useEffect, useState, useCallback } from 'react';
import { DashSidebar } from './dash/DashSidebar.jsx';
import { TopBar } from './dash/TopBar.jsx';
import { RightRail } from './dash/RightRail.jsx';
import { CommandPalette } from './dash/CommandPalette.jsx';
import AlertDetailDrawer from './AlertDetailDrawer.jsx';
import WorkspacePanel from './WorkspacePanel.jsx';

export default function DashboardView({ alerts, filteredAlerts, selected, onSelect, onClose, filters, onFilterChange, activeSection, onNavigate, paused, onTogglePaused, density, onDensityChange, onAddAlert, onLogout, connectionStatus }) {
  const [commandOpen, setCommandOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setCommandOpen(true);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const handleNavigate = useCallback((section) => {
    onNavigate(section);
    setCommandOpen(false);
  }, [onNavigate]);

  return (
    <div id="dashboard" className={`page-enter min-h-screen bg-background text-foreground ${density === 'compact' ? 'density-compact' : ''}`}>
      <TopBar
        alerts={alerts}
        paused={paused}
        onTogglePaused={onTogglePaused}
        onCommand={() => setCommandOpen(true)}
        onLogout={onLogout}
        connectionStatus={connectionStatus}
      />
      <DashSidebar
        activeSection={activeSection}
        onNavigate={handleNavigate}
      />
      <main className="min-h-[calc(100vh-3.5rem)] pt-14 lg:pl-56">
        <div className="mx-auto max-w-[1400px] px-4 py-6 lg:px-7 lg:py-8">
          <div className="mt-2 mb-5 flex items-end justify-between">
            <div>
              <div className="mono-label flex items-center gap-2">
                <span className={`h-1.5 w-1.5 rounded-full ${paused ? 'bg-yellow-500' : 'bg-signal animate-blink'}`} />
                {paused ? 'STREAM PAUSED' : 'STREAM ACTIVE'} <span className="text-muted-foreground">// {activeSection}</span>
              </div>
              <h1 className="font-display mt-2 text-4xl leading-[0.95] md:text-5xl">
                Incident command <span className="text-muted-foreground">/ live queue</span>
              </h1>
              <p className="mt-2 max-w-xl text-sm text-muted-foreground">
                Prioritize the highest-signal events, inspect the evidence trail, and move the incident forward.
              </p>
            </div>
            <div className="grid grid-cols-3 border border-border bg-card">
              <div className="border-r border-border px-4 py-3">
                <div className="mono-label text-[9px]">TOTAL</div>
                <div className="mt-1 font-mono text-xl text-foreground">{alerts.length}</div>
              </div>
              <div className="border-r border-border px-4 py-3">
                <div className="mono-label text-[9px]">HIGH</div>
                <div className="mt-1 font-mono text-xl text-primary">{alerts.filter((a) => a.severity === 'high' || a.severity === 'critical').length}</div>
              </div>
              <div className="px-4 py-3">
                <div className="mono-label text-[9px]">MEDIUM</div>
                <div className="mt-1 font-mono text-xl text-yellow-500">{alerts.filter((a) => a.severity === 'medium').length}</div>
              </div>
            </div>
          </div>

          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
            <div className="min-w-0">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeSection}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
                >
                  <WorkspacePanel
                    section={activeSection}
                    alerts={alerts}
                    filteredAlerts={filteredAlerts}
                    selected={selected}
                    onSelect={onSelect}
                    filters={filters}
                    onFilterChange={onFilterChange}
                    density={density}
                    onDensityChange={onDensityChange}
                    onAddAlert={onAddAlert}
                  />
                </motion.div>
              </AnimatePresence>
            </div>
            <RightRail alerts={alerts} />
          </div>
        </div>
      </main>

      <AnimatePresence>
        {selected && (
          <motion.div key="drawer-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <button type="button" className="fixed inset-0 z-40 bg-black/70 lg:hidden" onClick={onClose} aria-label="Close alert evidence" />
          </motion.div>
        )}
      </AnimatePresence>
      {selected && <AlertDetailDrawer alert={selected} onClose={onClose} />}

      <CommandPalette
        open={commandOpen}
        onOpenChange={setCommandOpen}
        onNavigate={handleNavigate}
        alerts={alerts}
      />
    </div>
  );
}
