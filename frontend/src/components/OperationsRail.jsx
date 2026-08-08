import TelemetrySparkline from './TelemetrySparkline.jsx';
import SignalTopology from './SignalTopology.jsx';

export default function OperationsRail({ alerts, selected, paused, onTopologyFocus }) {
  const highCount = alerts.filter((alert) => alert.severity === 'high').length;
  return (
    <aside className="space-y-4">
      <section className="dashboard-panel p-4">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <div className="eyebrow text-ash-dark">Threat forecast</div>
            <h2 className="mt-1 text-base font-semibold text-paper">Signal velocity</h2>
          </div>
          <span className="font-mono-ui text-[10px] text-amber">+18.4%</span>
        </div>
        <TelemetrySparkline values={[18, 22, 19, 26, 24, 31, 27, 38, 34, 49, 46, 58]} />
        <div className="mt-3 grid grid-cols-3 border-t border-line pt-3 font-mono-ui text-[9px]">
          <div><div className="text-ash-dark">NOW</div><div className="mt-1 text-paper">07/m</div></div>
          <div><div className="text-ash-dark">PEAK</div><div className="mt-1 text-amber">14/m</div></div>
          <div><div className="text-ash-dark">WINDOW</div><div className="mt-1 text-ash">60m</div></div>
        </div>
      </section>
      <section className="dashboard-panel overflow-hidden">
        <div className="flex items-center justify-between border-b border-line-strong px-4 py-3">
          <div>
            <div className="eyebrow text-ash-dark">Topology</div>
            <h2 className="mt-1 text-base font-semibold text-paper">Active routes</h2>
          </div>
          <span className="font-mono-ui text-[10px] text-red">{highCount} hot</span>
        </div>
        <SignalTopology alerts={alerts} activeAlert={selected} onFocus={onTopologyFocus} />
        <div className="flex items-center justify-between border-t border-line px-4 py-3 font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark">
          <span>nodes 06 // edges 07</span>
          <span className={paused ? 'text-yellow' : 'text-green'}>{paused ? 'spooled' : 'syncing'}</span>
        </div>
      </section>
      <section className="dashboard-panel p-4">
        <div className="eyebrow text-ash-dark">Agent activity</div>
        <div className="mt-4 space-y-3">
          <div>
            <div className="mb-1 flex justify-between font-mono-ui text-[10px]">
              <span className="text-paper">SENTINEL-ALPHA</span>
              <span className="text-green">ACTIVE</span>
            </div>
            <div className="h-1 bg-line"><div className="agent-meter h-full w-[78%] bg-green" /></div>
          </div>
          <div>
            <div className="mb-1 flex justify-between font-mono-ui text-[10px]">
              <span className="text-paper">CORTEX-03</span>
              <span className="text-green">ACTIVE</span>
            </div>
            <div className="h-1 bg-line"><div className="agent-meter h-full w-[92%] bg-green" /></div>
          </div>
          <div>
            <div className="mb-1 flex justify-between font-mono-ui text-[10px]">
              <span className="text-paper">SENTINEL-BETA</span>
              <span className="text-amber">THROTTLED</span>
            </div>
            <div className="h-1 bg-line"><div className="agent-meter h-full w-[45%] bg-amber" /></div>
          </div>
        </div>
      </section>
    </aside>
  );
}
