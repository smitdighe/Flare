export default function MetricBlock({ label, value, note, tone = 'amber' }) {
  const toneClass = { amber: 'text-amber', red: 'text-red', green: 'text-green', cyan: 'text-cyan' }[tone] || 'text-amber';
  return (
    <div className="metric-block border-l border-line-strong pl-3">
      <div className="font-mono-ui text-[9px] uppercase tracking-[0.12em] text-ash-dark">{label}</div>
      <div className={`metric-number mt-2 ${toneClass}`}>{value}</div>
      {note && <div className="mt-2 text-[10px] text-ash">{note}</div>}
    </div>
  );
}
