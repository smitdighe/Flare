import { AnimatePresence, motion } from 'motion/react';
import Icon from './Icon.jsx';
import { NAV_ITEMS } from './CommandBar.jsx';

export default function SideRail({ activeSection, onNavigate, mobileNavOpen, onClose }) {
  return (
    <>
      <AnimatePresence>
        {mobileNavOpen && (
          <motion.button
            type="button"
            className="fixed inset-0 z-40 bg-black/70 lg:hidden"
            onClick={onClose}
            aria-label="Close navigation"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        )}
      </AnimatePresence>
      <motion.aside
        className={`fixed bottom-0 left-0 top-[var(--topbar-height)] z-50 flex w-[var(--rail-width)] flex-col border-r border-line-strong bg-ink-900 px-3 py-5 lg:translate-x-0 ${mobileNavOpen ? 'translate-x-0' : '-translate-x-full'}`}
        animate={{ x: mobileNavOpen || window.innerWidth >= 1024 ? 0 : -260 }}
        transition={{ type: 'spring', stiffness: 380, damping: 34 }}
      >
        <div className="mb-5 border-b border-line pb-5 px-2">
          <div className="eyebrow mb-2 text-ash-dark">WORKSPACE</div>
          <div className="font-mono-ui text-xs text-paper">THREAT OPERATIONS</div>
          <div className="mt-1 font-mono-ui text-[9px] text-green">&#9679; SYSTEM NOMINAL</div>
        </div>
        <nav className="space-y-1" aria-label="Dashboard navigation">
          {NAV_ITEMS.map((item) => (
            <button
              type="button"
              key={item.id}
              className={`nav-rail-item group flex w-full items-center gap-3 border-l-2 px-3 py-2.5 text-left font-mono-ui text-[10px] uppercase tracking-[0.08em] transition-colors ${activeSection === item.id ? 'border-amber bg-amber/10 text-amber' : 'border-transparent text-ash hover:border-line-strong hover:bg-ink-850 hover:text-paper'}`}
              onClick={() => { onNavigate(item.id); onClose(); }}
              aria-current={activeSection === item.id ? 'page' : undefined}
            >
              <Icon name={item.icon} size={16} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="mt-auto space-y-4 border-t border-line pt-4">
          <div className="grid grid-cols-2 gap-2 font-mono-ui text-[9px]">
            <div>
              <div className="text-ash-dark">QUEUE</div>
              <div className="mt-1 text-paper">010 / 200</div>
            </div>
            <div>
              <div className="text-ash-dark">UPTIME</div>
              <div className="mt-1 text-green">99.98%</div>
            </div>
          </div>
          <div className="border border-line-strong bg-ink-950 p-3">
            <div className="text-[8px] uppercase tracking-[0.12em] text-ash-dark">Build</div>
            <div className="mt-1 font-mono-ui text-[9px] text-paper">v2.4.0-stable</div>
          </div>
        </div>
      </motion.aside>
    </>
  );
}
