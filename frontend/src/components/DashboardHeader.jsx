import AnimatedNumber from './AnimatedNumber.jsx';
import { NAV_ITEMS } from './CommandBar.jsx';

export default function DashboardHeader({ alerts, activeSection, paused }) {
  const highCount = alerts.filter((alert) => alert.severity === 'high').length;
  const title = NAV_ITEMS.find((item) => item.id === activeSection)?.label || 'Overview';
  return (
    <div className="flex flex-col gap-5 border-b border-line-strong pb-5 md:flex-row md:items-end md:justify-between">
      <div>
        <div className="eyebrow mb-3 flex items-center gap-2">
          <span className={`h-1.5 w-1.5 rounded-full ${paused ? 'bg-yellow' : 'bg-green animate-pulse'}`} />
          {paused ? 'STREAM PAUSED' : 'STREAM ACTIVE'} <span className="text-ash-dark">// {title}</span>
        </div>
        <h1 className="font-display text-4xl font-medium tracking-[-0.055em] text-paper md:text-5xl">
          Incident command <span className="text-ash-dark">/ live queue</span>
        </h1>
        <p className="mt-2 max-w-xl text-sm leading-6 text-ash">
          Prioritize the highest-signal events, inspect the evidence trail, and move the incident forward without losing the buffer.
        </p>
      </div>
      <div className="grid grid-cols-3 border border-line-strong bg-ink-900">
        <div className="border-r border-line-strong px-4 py-3">
          <div className="font-mono-ui text-[9px] text-ash-dark">TOTAL</div>
          <div className="mt-1 font-mono-ui text-xl text-paper"><AnimatedNumber value={alerts.length} decimals={0} /></div>
        </div>
        <div className="border-r border-line-strong px-4 py-3">
          <div className="font-mono-ui text-[9px] text-ash-dark">HIGH</div>
          <div className="mt-1 font-mono-ui text-xl text-amber"><AnimatedNumber value={highCount} decimals={0} /></div>
        </div>
        <div className="px-4 py-3">
          <div className="font-mono-ui text-[9px] text-ash-dark">MEDIUM</div>
          <div className="mt-1 font-mono-ui text-xl text-yellow"><AnimatedNumber value={alerts.filter((a) => a.severity === 'medium').length} decimals={0} /></div>
        </div>
      </div>
    </div>
  );
}
