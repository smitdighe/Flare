import { motion } from 'motion/react';
import { useEffect, useState } from 'react';
import AnimatedNumber from './AnimatedNumber.jsx';
import StatusDot from './StatusDot.jsx';
import AlertTable from './AlertTable.jsx';
import FilterStrip from './FilterStrip.jsx';

const API_BASE = import.meta.env.VITE_API_BASE || '';

function HealthPanel() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/v1/health`)
      .then((res) => res.json())
      .then((json) => { if (!cancelled) { setHealth(json.data || json); setLoading(false); } })
      .catch(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <section className="dashboard-panel">
        <div className="border-b border-line-strong px-4 py-4">
          <div className="eyebrow text-ash-dark">External dependencies</div>
          <h2 className="mt-1 text-base font-semibold text-paper">Health metrics</h2>
        </div>
        <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">Loading health data...</div>
      </section>
    );
  }

  const services = health?.services || [];
  return (
    <section className="dashboard-panel">
      <div className="border-b border-line-strong px-4 py-4">
        <div className="eyebrow text-ash-dark">External dependencies</div>
        <h2 className="mt-1 text-base font-semibold text-paper">Health metrics</h2>
      </div>
      <div className="divide-y divide-line">
        {services.map((service, index) => {
          const tone = service.status === 'ok' ? 'live' : service.status === 'rate_limited' ? 'medium' : 'offline';
          const toneColor = service.status === 'ok' ? 'text-green' : service.status === 'rate_limited' ? 'text-amber' : 'text-red';
          return (
            <motion.div
              key={service.name}
              className="flex items-center justify-between gap-4 px-4 py-5"
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.08 }}
            >
              <div className="flex items-center gap-3">
                <StatusDot tone={tone} pulse={tone === 'live'} />
                <div>
                  <div className="font-mono-ui text-xs text-paper">{service.name}</div>
                  <div className="mt-1 font-mono-ui text-[10px] text-ash-dark">{service.message || 'external API'}</div>
                </div>
              </div>
              <div className={`font-mono-ui text-[10px] ${toneColor}`}>
                {service.latency_ms ? `${service.latency_ms}ms` : service.status?.toUpperCase()}
              </div>
            </motion.div>
          );
        })}
        {services.length === 0 && (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">No services configured</div>
        )}
      </div>
    </section>
  );
}

function TimelinePanel() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/v1/stats`)
      .then((res) => res.json())
      .then((json) => { if (!cancelled) { setStats(json.data || json); setLoading(false); } })
      .catch(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const timeline = stats?.timeline || [];
  const maxCount = Math.max(...timeline.map((t) => t.count), 1);
  const velocity = stats?.alert_velocity || 0;

  if (loading) {
    return (
      <section className="dashboard-panel">
        <div className="flex items-end justify-between border-b border-line-strong px-4 py-4">
          <div>
            <div className="eyebrow text-ash-dark">30 minute window</div>
            <h2 className="mt-1 text-base font-semibold text-paper">System logs / event velocity</h2>
          </div>
        </div>
        <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">Loading timeline...</div>
      </section>
    );
  }

  return (
    <section className="dashboard-panel">
      <div className="flex items-end justify-between border-b border-line-strong px-4 py-4">
        <div>
          <div className="eyebrow text-ash-dark">30 minute window</div>
          <h2 className="mt-1 text-base font-semibold text-paper">System logs / event velocity</h2>
        </div>
        <span className="font-mono-ui text-[10px] text-amber">{velocity} alerts/min</span>
      </div>
      <div className="p-5">
        {timeline.length === 0 ? (
          <div className="flex h-64 items-center justify-center border-b border-l border-line-strong">
            <div className="font-mono-ui text-[10px] text-ash-dark">No timeline data yet. Alerts will appear here.</div>
          </div>
        ) : (
          <div className="flex h-64 items-end gap-2 border-b border-l border-line-strong px-3 pb-0 pt-4">
            {timeline.slice(-20).map((entry, index) => (
              <div key={entry.time} className="group flex h-full flex-1 items-end">
                <motion.div
                  className="timeline-bar w-full bg-amber/45"
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ delay: index * 0.025, duration: 0.5 }}
                  style={{ height: `${(entry.count / maxCount) * 100}%`, transformOrigin: 'bottom' }}
                  title={`${entry.time}: ${entry.count} alerts`}
                />
              </div>
            ))}
          </div>
        )}
        <div className="mt-3 flex justify-between font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark">
          <span>{timeline.length > 0 ? timeline[0]?.time?.slice(11, 16) : '--:--'}</span>
          <span>{timeline.length > 0 ? timeline[timeline.length - 1]?.time?.slice(11, 16) : '--:--'}</span>
          <span>now</span>
        </div>
      </div>
    </section>
  );
}

function EvalPanel() {
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/v1/eval`)
      .then((res) => res.json())
      .then((json) => { if (!cancelled) { setEvalData(json.data || json); setLoading(false); } })
      .catch(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <section className="dashboard-panel">
        <div className="border-b border-line-strong px-4 py-4">
          <div className="eyebrow text-ash-dark">Evaluation</div>
          <h2 className="mt-1 text-base font-semibold text-paper">Classification evaluation</h2>
        </div>
        <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">Loading eval data...</div>
      </section>
    );
  }

  const matrix = evalData?.confusion_matrix?.matrix || [[0,0,0],[0,0,0],[0,0,0]];
  const labels = evalData?.confusion_matrix?.labels || ['low', 'medium', 'high'];
  const severityAccuracy = evalData?.severity_accuracy || 0;
  const highF1 = evalData?.high_severity_f1 || 0;
  const avgLatency = evalData?.avg_latency_ms || 0;
  const sampleSize = evalData?.sample_size || 0;

  return (
    <section className="dashboard-panel">
      <div className="border-b border-line-strong px-4 py-4">
        <div className="eyebrow text-ash-dark">{sampleSize} labeled alerts</div>
        <h2 className="mt-1 text-base font-semibold text-paper">Classification evaluation</h2>
      </div>
      <div className="grid gap-4 p-4 md:grid-cols-3">
        <div className="metric-block border border-line-strong p-4">
          <div className="font-mono-ui text-[9px] text-ash-dark">SEVERITY ACCURACY</div>
          <div className="mt-2 font-mono-ui text-3xl text-amber"><AnimatedNumber value={severityAccuracy} decimals={2} /></div>
        </div>
        <div className="metric-block border border-line-strong p-4">
          <div className="font-mono-ui text-[9px] text-ash-dark">HIGH F1</div>
          <div className="mt-2 font-mono-ui text-3xl text-green"><AnimatedNumber value={highF1 || 0} decimals={2} /></div>
        </div>
        <div className="metric-block border border-line-strong p-4">
          <div className="font-mono-ui text-[9px] text-ash-dark">AVG LATENCY</div>
          <div className="mt-2 font-mono-ui text-3xl text-cyan"><AnimatedNumber value={avgLatency} suffix="ms" decimals={0} /></div>
        </div>
      </div>
      <div className="border-t border-line p-4">
        <div className="eyebrow mb-4 text-ash-dark">Confusion matrix // actual x predicted</div>
        <div className="grid max-w-[360px] grid-cols-4 gap-1 font-mono-ui text-[10px]">
          <div />
          {labels.map((l) => <div key={l} className="p-2 text-center text-ash-dark">{l.toUpperCase()}</div>)}
          {labels.map((label, row) => (
            <div key={label} className="contents">
              <div className="p-2 text-right text-ash-dark">{label.toUpperCase()}</div>
              {matrix[row]?.map((value, col) => (
                <motion.div
                  key={`${row}-${col}`}
                  className={`p-3 text-center ${row === col ? 'bg-green/15 text-green' : 'bg-red/10 text-red'}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: (row * 3 + col) * 0.06 }}
                >
                  {value}
                </motion.div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CorrelatedPanel({ alerts, onFilterChange }) {
  const clusters = Object.values(
    alerts.reduce((acc, alert) => {
      const key = alert.src_ip;
      if (!acc[key]) acc[key] = { ip: key, count: 0, types: new Set() };
      acc[key].count += 1;
      acc[key].types.add(alert.attack_type);
      return acc;
    }, {})
  ).sort((a, b) => b.count - a.count);

  return (
    <section className="dashboard-panel">
      <div className="border-b border-line-strong px-4 py-4">
        <div className="eyebrow text-ash-dark">Source IP correlation</div>
        <h2 className="mt-1 text-base font-semibold text-paper">Threat clusters</h2>
      </div>
      <div className="divide-y divide-line">
        {clusters.map((cluster, index) => (
          <motion.button
            type="button"
            key={cluster.ip}
            className="cluster-row flex w-full items-center justify-between gap-4 px-4 py-5 text-left transition-colors hover:bg-amber/5"
            onClick={() => onFilterChange({ search: cluster.ip })}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06 }}
          >
            <div>
              <div className="font-mono-ui text-sm text-paper">{cluster.ip}</div>
              <div className="mt-1 font-mono-ui text-[10px] uppercase tracking-[0.08em] text-ash-dark">{Array.from(cluster.types).join(' // ')}</div>
            </div>
            <div className="text-right">
              <div className="font-mono-ui text-lg text-amber">{String(cluster.count).padStart(2, '0')}</div>
              <div className="font-mono-ui text-[9px] text-ash-dark">linked alerts</div>
            </div>
          </motion.button>
        ))}
        {clusters.length === 0 && (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">No clusters found yet</div>
        )}
      </div>
    </section>
  );
}

export default function WorkspacePanel({ section, alerts, filteredAlerts, selected, onSelect, filters, onFilterChange, density, onDensityChange, onAddAlert }) {
  if (section === 'overview' || section === 'feed') {
    return (
      <section className="dashboard-panel min-w-0">
        <div className="flex items-center justify-between border-b border-line-strong px-4 py-3">
          <div>
            <div className="eyebrow text-ash-dark">Priority queue // {String(filteredAlerts.length).padStart(3, '0')} visible</div>
            <h2 className="mt-1 text-base font-semibold text-paper">Live alert feed</h2>
          </div>
          <div className="hidden items-center gap-4 font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark sm:flex">
            <span><span className="text-amber">J/K</span> navigate</span>
            <span><span className="text-amber">ENTER</span> inspect</span>
          </div>
        </div>
        <FilterStrip
          filters={filters}
          onFilterChange={onFilterChange}
          resultCount={filteredAlerts.length}
          density={density}
          onDensityChange={onDensityChange}
          onAddAlert={onAddAlert}
          onClear={() => onFilterChange({ search: undefined, severity: undefined, attack_type: undefined })}
        />
        <AlertTable
          alerts={filteredAlerts}
          selected={selected}
          onSelect={onSelect}
          density={density}
          query={filters.search || filters.severity || filters.attack_type ? 'active filters' : ''}
          onClear={() => onFilterChange({ search: undefined, severity: undefined, attack_type: undefined })}
        />
      </section>
    );
  }
  if (section === 'health') return <HealthPanel />;
  if (section === 'timeline') return <TimelinePanel />;
  if (section === 'correlated') return <CorrelatedPanel alerts={alerts} onFilterChange={onFilterChange} />;
  if (section === 'eval') return <EvalPanel />;
  return null;
}
