export default function TelemetrySparkline({ values = [20, 24, 18, 27, 22, 35, 29, 42, 34, 50], tone = 'amber' }) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const width = 220;
  const height = 52;
  const points = values.map((value, index) => {
    const x = (index / (values.length - 1)) * width;
    const y = height - ((value - min) / Math.max(max - min, 1)) * (height - 8) - 4;
    return `${x},${y}`;
  }).join(' ');

  const toneClass = { amber: 'text-amber', red: 'text-red', green: 'text-green', cyan: 'text-cyan' }[tone] || 'text-amber';

  return (
    <div className="telemetry-sparkline">
      <div className="flex items-center justify-between font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark"><span>0 events / min</span><span>peak {max} events / min</span></div>
      <svg viewBox={`0 0 ${width} ${height}`} className={`mt-1 h-12 w-full ${toneClass}`} role="img" aria-label={`Threat volume trend from ${min} to ${max} events per minute`}>
        <path d={`M 0 ${height - 1} H ${width}`} stroke="currentColor" strokeOpacity="0.2" strokeWidth="1" />
        <polyline className="sparkline-path" points={points} fill="none" stroke="currentColor" strokeWidth="2" vectorEffect="non-scaling-stroke" />
        <circle className="sparkline-endpoint" cx={width} cy={Number(points.split(' ').at(-1)?.split(',')[1] || height / 2)} r="3" fill="currentColor" />
      </svg>
      <div className="mt-1 flex justify-between font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark"><span>15m ago</span><span>now</span></div>
    </div>
  );
}
