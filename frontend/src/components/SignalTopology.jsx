import { useMemo, useRef, memo } from 'react';
import StatusDot from './StatusDot.jsx';
import ThreeTopology from './ThreeTopology.jsx';

const STATIC_FALLBACK = [
  { x: 18, y: 28, label: 'edge-01', src_ip: '185.220.101.14', tone: 'high' },
  { x: 32, y: 58, label: 'api-gw', src_ip: '45.142.212.61', tone: 'critical' },
  { x: 51, y: 30, label: 'waf-02', src_ip: '103.77.192.88', tone: 'live' },
  { x: 61, y: 68, label: 'auth-01', src_ip: '10.24.6.43', tone: 'medium' },
  { x: 76, y: 39, label: 'db-03', src_ip: '172.18.0.4', tone: 'critical' },
  { x: 88, y: 66, label: 'egress', src_ip: '172.16.14.9', tone: 'high' },
];

const NODE_BORDER = { critical: 'border-red', high: 'border-amber', medium: 'border-yellow', live: 'border-green' };

function buildNodesFromAlerts(alerts) {
  if (!alerts || alerts.length === 0) return null;

  const ipMap = new Map();
  alerts.forEach((a) => {
    if (!a.src_ip) return;
    if (!ipMap.has(a.src_ip)) {
      ipMap.set(a.src_ip, { count: 0, maxSeverity: 'low', types: new Set() });
    }
    const entry = ipMap.get(a.src_ip);
    entry.count += 1;
    const sevOrder = { low: 0, medium: 1, high: 2 };
    if ((sevOrder[a.severity] || 0) > (sevOrder[entry.maxSeverity] || 0)) {
      entry.maxSeverity = a.severity || 'low';
    }
    if (a.attack_type) entry.types.add(a.attack_type);
  });

  const sorted = [...ipMap.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 6);

  if (sorted.length === 0) return null;

  const count = sorted.length;
  return sorted.map(([ip, data], i) => {
    const angle = (i / Math.max(count, 1)) * Math.PI * 2;
    const radius = 0.3 + (data.count / (sorted[0]?.[1].count || 1)) * 0.35;
    return {
      x: 50 + Math.cos(angle) * radius * 40,
      y: 50 + Math.sin(angle) * radius * 30,
      label: ip.split('.').slice(0, 2).join('.') + '.' + (i + 1),
      src_ip: ip,
      tone: data.maxSeverity,
      alertCount: data.count,
      attackTypes: Array.from(data.types),
    };
  });
}

function nodesChanged(a, b) {
  if (a === null && b === null) return false;
  if (a === null || b === null) return true;
  if (a.length !== b.length) return true;
  for (let i = 0; i < a.length; i++) {
    if (a[i].src_ip !== b[i].src_ip || a[i].tone !== b[i].tone || a[i].alertCount !== b[i].alertCount) return true;
  }
  return false;
}

export default memo(function SignalTopology({ alerts, activeAlert, onFocus }) {
  const computedNodes = useMemo(() => buildNodesFromAlerts(alerts), [alerts]);
  const nodesRef = useRef(STATIC_FALLBACK);
  const nodes = useMemo(() => {
    const next = computedNodes || STATIC_FALLBACK;
    if (nodesChanged(nodesRef.current, next)) {
      nodesRef.current = next;
    }
    return nodesRef.current;
  }, [computedNodes]);

  const edges = nodes.length >= 2 ? nodes.length : 0;

  return (
    <div className="relative min-h-[270px] overflow-hidden bg-ink-950 signal-grid">
      <div className="absolute inset-0 scanlines opacity-30" />
      <ThreeTopology nodes={nodes} onFocus={onFocus} />
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full opacity-70" aria-hidden="true">
        {nodes.map((node, i) => {
          const next = nodes[(i + 1) % nodes.length];
          if (!next) return null;
          return (
            <line
              key={`edge-${i}`}
              className="topology-link"
              style={{ '--link-delay': `${i * 140}ms` }}
              x1={node.x} y1={node.y}
              x2={next.x} y2={next.y}
              stroke="var(--line-strong)"
              strokeWidth="0.35"
              strokeDasharray="1.3 1.6"
            />
          );
        })}
        {activeAlert && nodes.length > 1 && (
          <line
            className="topology-route"
            x1={nodes[1]?.x || 0} y1={nodes[1]?.y || 0}
            x2={nodes[nodes.length - 2]?.x || 0} y2={nodes[nodes.length - 2]?.y || 0}
            stroke="var(--amber-500)"
            strokeOpacity="0.68"
            strokeWidth="0.55"
            strokeDasharray="2 2"
          />
        )}
      </svg>
      <div className="absolute inset-0">
        {nodes.map((node, index) => (
          <button
            type="button"
            key={node.src_ip}
            className="topology-hit absolute -translate-x-1/2 -translate-y-1/2 text-left"
            style={{ left: `${node.x}%`, top: `${node.y}%` }}
            onClick={() => onFocus?.(node)}
            aria-label={`Focus ${node.label} ${node.src_ip}`}
          >
            <span
              className={`topology-node flex h-7 w-7 items-center justify-center border ${NODE_BORDER[node.tone] || 'border-line-strong'} bg-ink-900`}
              style={{ '--node-delay': `${index * 180}ms` }}
            >
              <StatusDot tone={node.tone} pulse={node.tone === 'critical'} />
            </span>
            <span className="mt-1 block whitespace-nowrap font-mono-ui text-[9px] text-ash">{node.label}</span>
            {node.alertCount > 1 && (
              <span className="block font-mono-ui text-[8px] text-amber">{node.alertCount} alerts</span>
            )}
          </button>
        ))}
      </div>
      {activeAlert && (
        <div className="topology-focus absolute bottom-3 left-3 border border-amber/60 bg-ink-900/90 px-2 py-1 font-mono-ui text-[10px] text-amber">
          ROUTE FOCUS // {activeAlert.src_ip} → {activeAlert.dest_ip}
        </div>
      )}
      <div className="absolute right-3 top-3 font-mono-ui text-[8px] uppercase tracking-[0.14em] text-ash-dark">
        {nodes.length} nodes // {edges} edges
      </div>
    </div>
  );
});
