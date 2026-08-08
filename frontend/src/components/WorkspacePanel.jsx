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

function SeverityChart({ alerts }) {
  const counts = { high: 0, medium: 0, low: 0 };
  alerts.forEach((a) => { if (counts[a.severity] !== undefined) counts[a.severity] += 1; });
  const total = alerts.length || 1;
  const segments = [
    { label: 'HIGH', count: counts.high, color: '#e94560', pct: (counts.high / total) * 100 },
    { label: 'MED', count: counts.medium, color: '#f59e0b', pct: (counts.medium / total) * 100 },
    { label: 'LOW', count: counts.low, color: '#30d158', pct: (counts.low / total) * 100 },
  ];

  let offset = 0;
  const radius = 40;
  const circumference = 2 * Math.PI * radius;

  return (
    <section className="dashboard-panel p-4">
      <div className="eyebrow text-ash-dark">Severity distribution</div>
      <div className="mt-4 flex items-center gap-6">
        <div className="relative">
          <svg width="110" height="110" viewBox="0 0 100 100">
            {segments.map((seg) => {
              const dash = (seg.pct / 100) * circumference;
              const el = (
                <circle
                  key={seg.label}
                  cx="50" cy="50" r={radius}
                  fill="none"
                  stroke={seg.color}
                  strokeWidth="12"
                  strokeDasharray={`${dash} ${circumference - dash}`}
                  strokeDashoffset={-offset}
                  transform="rotate(-90 50 50)"
                  style={{ transition: 'stroke-dasharray 0.5s ease' }}
                />
              );
              offset += dash;
              return el;
            })}
            <text x="50" y="48" textAnchor="middle" fill="#e0e0e0" fontSize="14" fontWeight="bold" fontFamily="monospace">{total}</text>
            <text x="50" y="60" textAnchor="middle" fill="#666" fontSize="7" fontFamily="monospace">ALERTS</text>
          </svg>
        </div>
        <div className="space-y-2">
          {segments.map((seg) => (
            <div key={seg.label} className="flex items-center gap-3 font-mono-ui text-[10px]">
              <span className="h-2 w-2 rounded-full" style={{ background: seg.color }} />
              <span className="w-10 text-ash-dark">{seg.label}</span>
              <span className="text-paper">{seg.count}</span>
              <span className="text-ash-dark">{seg.pct.toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ExportPanel({ filters }) {
  const [exporting, setExporting] = useState(null);

  const handleExport = async (format) => {
    setExporting(format);
    const params = new URLSearchParams();
    if (filters.severity) params.set('severity', filters.severity);
    if (filters.attack_type) params.set('attack_type', filters.attack_type);
    if (filters.search) params.set('search', filters.search);
    params.set('limit', '500');

    try {
      const token = localStorage.getItem('flare_token');
      const res = await fetch(`${API_BASE}/api/v1/export/alerts/${format}?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `flare_alerts.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
    } finally {
      setExporting(null);
    }
  };

  return (
    <section className="dashboard-panel p-4">
      <div className="eyebrow text-ash-dark">Export data</div>
      <div className="mt-4 space-y-3">
        <button
          type="button"
          onClick={() => handleExport('csv')}
          disabled={exporting === 'csv'}
          className="flex w-full items-center gap-3 border border-line-strong bg-ink-900 px-4 py-3 font-mono-ui text-[10px] text-paper transition-colors hover:border-green/50 hover:bg-green/5 disabled:opacity-50"
        >
          <span className="text-green">CSV</span>
          <span className="text-ash-dark">{exporting === 'csv' ? 'Exporting...' : 'Download filtered alerts as CSV'}</span>
        </button>
        <button
          type="button"
          onClick={() => handleExport('pdf')}
          disabled={exporting === 'pdf'}
          className="flex w-full items-center gap-3 border border-line-strong bg-ink-900 px-4 py-3 font-mono-ui text-[10px] text-paper transition-colors hover:border-red/50 hover:bg-red/5 disabled:opacity-50"
        >
          <span className="text-red">PDF</span>
          <span className="text-ash-dark">{exporting === 'pdf' ? 'Exporting...' : 'Generate formatted PDF report'}</span>
        </button>
      </div>
    </section>
  );
}

function RulesPanel() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', conditions: { logic: 'AND', conditions: [{ field: 'severity', operator: 'equals', value: 'high' }] }, actions: [{ type: 'set_severity', value: 'high' }] });
  const [error, setError] = useState('');

  const fetchRules = () => {
    const token = localStorage.getItem('flare_token');
    fetch(`${API_BASE}/api/v1/rules`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((d) => { setRules(d.rules || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchRules(); }, []);

  const handleCreate = async () => {
    setError('');
    const token = localStorage.getItem('flare_token');
    try {
      const res = await fetch(`${API_BASE}/api/v1/rules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(form),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Failed'); }
      setShowForm(false);
      setForm({ name: '', description: '', conditions: { logic: 'AND', conditions: [{ field: 'severity', operator: 'equals', value: 'high' }] }, actions: [{ type: 'set_severity', value: 'high' }] });
      fetchRules();
    } catch (err) { setError(err.message); }
  };

  const handleDelete = async (id) => {
    const token = localStorage.getItem('flare_token');
    await fetch(`${API_BASE}/api/v1/rules/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
    fetchRules();
  };

  return (
    <section className="dashboard-panel">
      <div className="flex items-center justify-between border-b border-line-strong px-4 py-4">
        <div>
          <div className="eyebrow text-ash-dark">Custom rules</div>
          <h2 className="mt-1 text-base font-semibold text-paper">Alert rules</h2>
        </div>
        <button type="button" onClick={() => setShowForm(!showForm)} className="font-mono-ui text-[10px] text-amber hover:text-amber/80">
          {showForm ? 'Cancel' : '+ New Rule'}
        </button>
      </div>

      {showForm && (
        <div className="border-b border-line p-4 space-y-3">
          {error && <div className="font-mono-ui text-[10px] text-red">{error}</div>}
          <input
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Rule name"
            className="w-full border border-line-strong bg-ink-900 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none"
          />
          <input
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Description (optional)"
            className="w-full border border-line-strong bg-ink-900 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none"
          />
          <div className="grid grid-cols-3 gap-2">
            <select value={form.conditions.conditions[0].field} onChange={(e) => setForm({ ...form, conditions: { ...form.conditions, conditions: [{ ...form.conditions.conditions[0], field: e.target.value }] } })} className="border border-line-strong bg-ink-900 px-2 py-2 font-mono-ui text-[10px] text-paper">
              <option value="severity">Severity</option>
              <option value="attack_type">Attack Type</option>
              <option value="src_ip">Source IP</option>
              <option value="dest_port">Dest Port</option>
            </select>
            <select value={form.conditions.conditions[0].operator} onChange={(e) => setForm({ ...form, conditions: { ...form.conditions, conditions: [{ ...form.conditions.conditions[0], operator: e.target.value }] } })} className="border border-line-strong bg-ink-900 px-2 py-2 font-mono-ui text-[10px] text-paper">
              <option value="equals">Equals</option>
              <option value="contains">Contains</option>
              <option value="not_equals">Not Equals</option>
              <option value="greater_than">Greater Than</option>
            </select>
            <input
              value={form.conditions.conditions[0].value}
              onChange={(e) => setForm({ ...form, conditions: { ...form.conditions, conditions: [{ ...form.conditions.conditions[0], value: e.target.value }] } })}
              placeholder="Value"
              className="border border-line-strong bg-ink-900 px-2 py-2 font-mono-ui text-[10px] text-paper outline-none"
            />
          </div>
          <button type="button" onClick={handleCreate} className="w-full bg-amber/20 border border-amber/40 py-2 font-mono-ui text-[10px] text-amber hover:bg-amber/30">
            Create Rule
          </button>
        </div>
      )}

      <div className="divide-y divide-line">
        {loading ? (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">Loading...</div>
        ) : rules.length === 0 ? (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">No rules yet. Create one to customize alert handling.</div>
        ) : (
          rules.map((rule) => (
            <div key={rule.id} className="flex items-center justify-between px-4 py-4">
              <div>
                <div className="font-mono-ui text-xs text-paper">{rule.name}</div>
                <div className="mt-1 font-mono-ui text-[10px] text-ash-dark">{rule.description || 'No description'}</div>
                <div className="mt-1 font-mono-ui text-[9px] text-amber">{rule.match_count} matches</div>
              </div>
              <div className="flex items-center gap-2">
                <StatusDot tone={rule.is_enabled ? 'live' : 'offline'} />
                <button type="button" onClick={() => handleDelete(rule.id)} className="font-mono-ui text-[10px] text-red hover:text-red/80">Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

function PlaybooksPanel() {
  const [playbooks, setPlaybooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', alert_type: '', steps: [{ type: 'manual', title: '', description: '' }] });
  const [error, setError] = useState('');

  const fetchPlaybooks = () => {
    const token = localStorage.getItem('flare_token');
    fetch(`${API_BASE}/api/v1/playbooks`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((d) => { setPlaybooks(d.playbooks || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchPlaybooks(); }, []);

  const handleCreate = async () => {
    setError('');
    const token = localStorage.getItem('flare_token');
    try {
      const res = await fetch(`${API_BASE}/api/v1/playbooks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...form, is_enabled: true }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Failed'); }
      setShowForm(false);
      setForm({ name: '', description: '', alert_type: '', steps: [{ type: 'manual', title: '', description: '' }] });
      fetchPlaybooks();
    } catch (err) { setError(err.message); }
  };

  const handleDelete = async (id) => {
    const token = localStorage.getItem('flare_token');
    await fetch(`${API_BASE}/api/v1/playbooks/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
    fetchPlaybooks();
  };

  return (
    <section className="dashboard-panel">
      <div className="flex items-center justify-between border-b border-line-strong px-4 py-4">
        <div>
          <div className="eyebrow text-ash-dark">Incident response</div>
          <h2 className="mt-1 text-base font-semibold text-paper">Playbooks</h2>
        </div>
        <button type="button" onClick={() => setShowForm(!showForm)} className="font-mono-ui text-[10px] text-amber hover:text-amber/80">
          {showForm ? 'Cancel' : '+ New Playbook'}
        </button>
      </div>

      {showForm && (
        <div className="border-b border-line p-4 space-y-3">
          {error && <div className="font-mono-ui text-[10px] text-red">{error}</div>}
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Playbook name" className="w-full border border-line-strong bg-ink-900 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none" />
          <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" className="w-full border border-line-strong bg-ink-900 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none" />
          <input value={form.alert_type} onChange={(e) => setForm({ ...form, alert_type: e.target.value })} placeholder="Alert type (e.g. ddos, malware)" className="w-full border border-line-strong bg-ink-900 px-3 py-2 font-mono-ui text-[11px] text-paper outline-none" />
          <div className="space-y-2">
            {form.steps.map((step, i) => (
              <div key={i} className="flex gap-2">
                <input value={step.title} onChange={(e) => { const s = [...form.steps]; s[i] = { ...s[i], title: e.target.value }; setForm({ ...form, steps: s }); }} placeholder={`Step ${i + 1} title`} className="flex-1 border border-line-strong bg-ink-900 px-2 py-1 font-mono-ui text-[10px] text-paper outline-none" />
                <button type="button" onClick={() => setForm({ ...form, steps: form.steps.filter((_, j) => j !== i) })} className="text-red font-mono-ui text-[10px]">x</button>
              </div>
            ))}
            <button type="button" onClick={() => setForm({ ...form, steps: [...form.steps, { type: 'manual', title: '', description: '' }] })} className="font-mono-ui text-[10px] text-amber">+ Add step</button>
          </div>
          <button type="button" onClick={handleCreate} className="w-full bg-amber/20 border border-amber/40 py-2 font-mono-ui text-[10px] text-amber hover:bg-amber/30">Create Playbook</button>
        </div>
      )}

      <div className="divide-y divide-line">
        {loading ? (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">Loading...</div>
        ) : playbooks.length === 0 ? (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">No playbooks yet.</div>
        ) : (
          playbooks.map((pb) => (
            <div key={pb.id} className="px-4 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-mono-ui text-xs text-paper">{pb.name}</div>
                  <div className="mt-1 font-mono-ui text-[10px] text-ash-dark">{pb.description || 'No description'}</div>
                  <div className="mt-1 font-mono-ui text-[9px] text-amber">{pb.execution_count} executions // {pb.steps?.length || 0} steps</div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusDot tone={pb.is_enabled ? 'live' : 'offline'} />
                  <button type="button" onClick={() => handleDelete(pb.id)} className="font-mono-ui text-[10px] text-red hover:text-red/80">Delete</button>
                </div>
              </div>
              {pb.steps && pb.steps.length > 0 && (
                <div className="mt-3 space-y-1">
                  {pb.steps.map((step, i) => (
                    <div key={i} className="flex items-center gap-2 font-mono-ui text-[9px] text-ash-dark">
                      <span className="text-amber">{i + 1}.</span>
                      <span className={`px-1 py-0.5 ${step.type === 'auto' ? 'bg-green/10 text-green' : 'bg-blue/10 text-blue'}`}>{step.type}</span>
                      <span>{step.title || 'Untitled step'}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </section>
  );
}

function NotificationsPanel() {
  const [prefs, setPrefs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [channel, setChannel] = useState('email');
  const [eventType, setEventType] = useState('alert.high_severity');

  const fetchPrefs = () => {
    const token = localStorage.getItem('flare_token');
    fetch(`${API_BASE}/api/v1/notifications/preferences`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((d) => { setPrefs(d.preferences || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchPrefs(); }, []);

  const handleToggle = async (pref) => {
    const token = localStorage.getItem('flare_token');
    await fetch(`${API_BASE}/api/v1/notifications/preferences`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ channel: pref.channel, event_type: pref.event_type, is_enabled: !pref.is_enabled }),
    });
    fetchPrefs();
  };

  const handleAdd = async () => {
    const token = localStorage.getItem('flare_token');
    await fetch(`${API_BASE}/api/v1/notifications/preferences`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ channel, event_type: eventType, is_enabled: true }),
    });
    fetchPrefs();
  };

  const handleDelete = async (id) => {
    const token = localStorage.getItem('flare_token');
    await fetch(`${API_BASE}/api/v1/notifications/preferences/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
    fetchPrefs();
  };

  return (
    <section className="dashboard-panel">
      <div className="border-b border-line-strong px-4 py-4">
        <div className="eyebrow text-ash-dark">Alert notifications</div>
        <h2 className="mt-1 text-base font-semibold text-paper">Notification preferences</h2>
      </div>

      <div className="border-b border-line p-4">
        <div className="flex gap-2">
          <select value={channel} onChange={(e) => setChannel(e.target.value)} className="border border-line-strong bg-ink-900 px-2 py-2 font-mono-ui text-[10px] text-paper">
            <option value="email">Email</option>
            <option value="slack">Slack</option>
          </select>
          <select value={eventType} onChange={(e) => setEventType(e.target.value)} className="flex-1 border border-line-strong bg-ink-900 px-2 py-2 font-mono-ui text-[10px] text-paper">
            <option value="alert.high_severity">High Severity Alert</option>
            <option value="rule.matched">Rule Matched</option>
            <option value="export.ready">Export Ready</option>
          </select>
          <button type="button" onClick={handleAdd} className="bg-amber/20 border border-amber/40 px-3 py-2 font-mono-ui text-[10px] text-amber hover:bg-amber/30">Add</button>
        </div>
      </div>

      <div className="divide-y divide-line">
        {loading ? (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">Loading...</div>
        ) : prefs.length === 0 ? (
          <div className="px-4 py-8 text-center font-mono-ui text-[10px] text-ash-dark">No notification preferences configured.</div>
        ) : (
          prefs.map((pref) => (
            <div key={pref.id} className="flex items-center justify-between px-4 py-4">
              <div className="flex items-center gap-3">
                <StatusDot tone={pref.is_enabled ? 'live' : 'offline'} />
                <div>
                  <div className="font-mono-ui text-xs text-paper">{pref.channel.toUpperCase()}</div>
                  <div className="mt-1 font-mono-ui text-[10px] text-ash-dark">{pref.event_type}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button type="button" onClick={() => handleToggle(pref)} className="font-mono-ui text-[10px] text-amber hover:text-amber/80">
                  {pref.is_enabled ? 'Disable' : 'Enable'}
                </button>
                <button type="button" onClick={() => handleDelete(pref.id)} className="font-mono-ui text-[10px] text-red hover:text-red/80">Delete</button>
              </div>
            </div>
          ))
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
  if (section === 'rules') return <RulesPanel />;
  if (section === 'playbooks') return <PlaybooksPanel />;
  if (section === 'notifications') return <NotificationsPanel />;
  if (section === 'export') return <ExportPanel filters={filters} />;
  return null;
}
