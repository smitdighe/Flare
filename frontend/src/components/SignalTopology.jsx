import StatusDot from './StatusDot.jsx';
import ThreeTopology from './ThreeTopology.jsx';

const NODES = [
  { x: 18, y: 28, label: 'edge-01', src_ip: '185.220.101.14', tone: 'high' },
  { x: 32, y: 58, label: 'api-gw', src_ip: '45.142.212.61', tone: 'critical' },
  { x: 51, y: 30, label: 'waf-02', src_ip: '103.77.192.88', tone: 'live' },
  { x: 61, y: 68, label: 'auth-01', src_ip: '10.24.6.43', tone: 'medium' },
  { x: 76, y: 39, label: 'db-03', src_ip: '172.18.0.4', tone: 'critical' },
  { x: 88, y: 66, label: 'egress', src_ip: '172.16.14.9', tone: 'high' },
];
const LINKS = [[0, 1], [0, 2], [1, 3], [2, 3], [2, 4], [3, 4], [4, 5]];
const NODE_BORDER = { critical: 'border-red', high: 'border-amber', medium: 'border-yellow', live: 'border-green' };

export default function SignalTopology({ activeAlert, onFocus }) {
  return (
    <div className="relative min-h-[270px] overflow-hidden bg-ink-950 signal-grid" onDoubleClick={() => onFocus?.(NODES[1])}>
      <div className="absolute inset-0 scanlines opacity-30" />
      <ThreeTopology nodes={NODES} onFocus={onFocus} />
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full opacity-70" aria-hidden="true">{LINKS.map(([from, to], index) => <line key={`${from}-${to}`} className="topology-link" style={{ '--link-delay': `${index * 140}ms` }} x1={NODES[from].x} y1={NODES[from].y} x2={NODES[to].x} y2={NODES[to].y} stroke="var(--line-strong)" strokeWidth="0.35" strokeDasharray="1.3 1.6" />)}<line className="topology-route" x1="32" y1="58" x2="76" y2="39" stroke="var(--amber-500)" strokeOpacity="0.68" strokeWidth="0.55" strokeDasharray="2 2" /></svg>
      <div className="absolute inset-0">{NODES.map((node, index) => <button type="button" key={node.label} className="topology-hit absolute -translate-x-1/2 -translate-y-1/2 text-left" style={{ left: `${node.x}%`, top: `${node.y}%` }} onClick={() => onFocus?.(node)} aria-label={`Focus ${node.label} ${node.src_ip}`}><span className={`topology-node flex h-7 w-7 items-center justify-center border ${NODE_BORDER[node.tone] || 'border-line-strong'} bg-ink-900`} style={{ '--node-delay': `${index * 180}ms` }}><StatusDot tone={node.tone} pulse={node.tone === 'critical'} /></span><span className="mt-1 block whitespace-nowrap font-mono-ui text-[9px] text-ash">{node.label}</span></button>)}</div>
      {activeAlert && <div className="topology-focus absolute bottom-3 left-3 border border-amber/60 bg-ink-900/90 px-2 py-1 font-mono-ui text-[10px] text-amber">ROUTE FOCUS // {activeAlert.src_ip} → {activeAlert.dest_ip}</div>}
      <div className="absolute right-3 top-3 font-mono-ui text-[8px] uppercase tracking-[0.14em] text-ash-dark">click node / filter source</div>
    </div>
  );
}
