import { AnimatePresence, motion } from 'motion/react';
import { useEffect, useMemo, useState, useCallback } from 'react';
import CommandBar from './CommandBar.jsx';
import SideRail from './SideRail.jsx';
import DashboardHeader from './DashboardHeader.jsx';
import WorkspacePanel from './WorkspacePanel.jsx';
import OperationsRail from './OperationsRail.jsx';
import AlertDetailDrawer from './AlertDetailDrawer.jsx';
import CommandPalette from './CommandPalette.jsx';
import { NAV_ITEMS } from './CommandBar.jsx';

export default function DashboardView({ alerts, filteredAlerts, selected, onSelect, onClose, filters, onFilterChange, activeSection, onNavigate, paused, onTogglePaused, density, onDensityChange, onAddAlert, onCommand, onLogout, connectionStatus }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        setMobileNavOpen(false);
      }
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setCommandOpen(true);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const commands = useMemo(() => [
    ...NAV_ITEMS.map((item) => ({ id: item.id, label: `Open ${item.label}`, detail: 'Navigate workspace', icon: item.icon })),
    { id: paused ? 'resume' : 'pause', label: paused ? 'Resume live stream' : 'Pause live stream', detail: 'Control incoming SSE events', icon: paused ? 'play_arrow' : 'pause' },
    { id: 'simulate', label: 'Simulate signal', detail: 'Add a synthetic alert to the buffer', icon: 'add' },
    { id: 'close', label: 'Close selected alert', detail: 'Dismiss the evidence drawer', icon: 'close' },
  ], [paused]);

  const executeCommand = (command) => {
    if (NAV_ITEMS.some((item) => item.id === command)) onNavigate(command);
    else if (command === 'pause' || command === 'resume') onTogglePaused();
    else if (command === 'simulate') onAddAlert();
    else if (command === 'close') onClose();
    onCommand?.(command);
  };

  const handleTopologyFocus = useCallback((node) => {
    onFilterChange({ search: node.src_ip || node.label });
  }, [onFilterChange]);

  return (
    <div id="dashboard" className={`page-enter min-h-screen bg-ink-950 text-paper ${density === 'compact' ? 'density-compact' : ''}`}>
      <CommandBar
        search={filters.search || ''}
        onSearch={(search) => onFilterChange({ search: search || undefined })}
        paused={paused}
        onTogglePaused={onTogglePaused}
        density={density}
        onDensityChange={onDensityChange}
        onMobileNav={() => setMobileNavOpen(true)}
        onOpenCommands={() => setCommandOpen(true)}
        onLogout={onLogout}
        connectionStatus={connectionStatus}
      />
      <SideRail
        activeSection={activeSection}
        onNavigate={onNavigate}
        mobileNavOpen={mobileNavOpen}
        onClose={() => setMobileNavOpen(false)}
      />
      <main className="min-h-screen pt-[var(--topbar-height)] lg:pl-[var(--rail-width)]">
        <div className="mx-auto max-w-[var(--content-max)] px-4 py-6 lg:px-7 lg:py-8">
          <DashboardHeader alerts={alerts} activeSection={activeSection} paused={paused} />
          <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
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
            <OperationsRail
              alerts={alerts}
              selected={selected}
              paused={paused}
              onTopologyFocus={handleTopologyFocus}
            />
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
      <CommandPalette open={commandOpen} commands={commands} onExecute={executeCommand} onClose={() => setCommandOpen(false)} />
    </div>
  );
}
