import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ArrowUpRight, Cpu, Waves, Orbit } from "lucide-react";
import { AGENTS, velocitySeries } from "../../lib/flare-data.js";

export function SignalVelocity() {
  const data = useMemo(() => velocitySeries(2), []);
  const [hover, setHover] = useState(null);
  const W = 300;
  const H = 96;
  const step = W / (data.length - 1);
  const pts = data.map((v, i) => [i * step, H - v * H]);
  const line = pts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const area = `${line} L${W},${H} L0,${H} Z`;
  const peak = Math.round(Math.max(...data) * 62);

  return (
    <div className="panel scanline relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <span className="mono-label flex items-center gap-2">
          <Waves className="h-3 w-3 text-primary" /> threat forecast
        </span>
        <span className="mono-label text-signal">+18.4%</span>
      </div>

      <div className="px-4 pt-3">
        <div className="font-display text-2xl leading-none">Signal velocity</div>
        <div className="mono-label mt-1.5 flex justify-between">
          <span>{hover !== null ? `${Math.round(data[hover] * 62)} events / min` : "live window"}</span>
          <span className="text-primary">peak {peak} / min</span>
        </div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="mt-2 h-28 w-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="fv-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.55" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="fv-stroke" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--primary-glow)" />
            <stop offset="100%" stopColor="var(--primary)" />
          </linearGradient>
        </defs>

        {[0.25, 0.5, 0.75].map((g) => (
          <line key={g} x1="0" x2={W} y1={H * g} y2={H * g} stroke="var(--border)" strokeWidth="0.5" />
        ))}

        <motion.path
          d={area}
          fill="url(#fv-fill)"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2 }}
        />
        <motion.path
          d={line}
          fill="none"
          stroke="url(#fv-stroke)"
          strokeWidth="1.6"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.6, ease: "easeInOut" }}
        />

        {pts.map(([x, y], i) => (
          <g key={i}>
            <rect
              x={x - step / 2}
              y={0}
              width={step}
              height={H}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
            {hover === i && (
              <>
                <line x1={x} x2={x} y1={0} y2={H} stroke="var(--primary)" strokeWidth="0.6" />
                <circle cx={x} cy={y} r="2.6" fill="var(--primary-glow)" />
              </>
            )}
          </g>
        ))}

        <motion.circle
          r="3"
          fill="var(--primary)"
          animate={{ cx: pts.map(([x]) => x), cy: pts.map(([, y]) => y) }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        />
      </svg>

      <div className="grid grid-cols-3 divide-x divide-border border-t border-border">
        {[
          ["now", "37/m"],
          ["peak", `${peak}/m`],
          ["window", "60m"],
        ].map(([k, v]) => (
          <div key={k} className="px-3 py-2.5">
            <div className="mono-label text-[9px]">{k}</div>
            <div className="font-mono text-xs text-primary">{v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AttackSurface({ alerts = [] }) {
  const nodes = useMemo(
    () =>
      alerts.slice(0, 8).map((a, i) => {
        const angle = (i / 8) * Math.PI * 2;
        const radius = 34 + (i % 3) * 21;
        return {
          id: a.id,
          ip: a.src_ip || a.src,
          vector: a.attack_type || a.vector,
          severity: a.severity,
          x: 100 + Math.cos(angle) * radius,
          y: 100 + Math.sin(angle) * radius,
        };
      }),
    [alerts],
  );
  const [active, setActive] = useState(null);

  return (
    <div className="panel relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <span className="mono-label flex items-center gap-2">
          <Orbit className="h-3 w-3 text-primary" /> attack surface
        </span>
        <span className="mono-label text-destructive">3 hot</span>
      </div>

      <div className="relative px-2 py-2">
        <svg viewBox="0 0 200 200" className="h-56 w-full">
          <defs>
            <radialGradient id="core" cx="50%" cy="50%">
              <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.9" />
              <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
            </radialGradient>
          </defs>

          {[34, 55, 76, 94].map((r, i) => (
            <motion.circle
              key={r}
              cx="100"
              cy="100"
              r={r}
              fill="none"
              stroke="var(--border)"
              strokeDasharray={i % 2 ? "2 6" : "1 4"}
              style={{ transformOrigin: "100px 100px" }}
              animate={{ rotate: i % 2 ? 360 : -360 }}
              transition={{ duration: 40 + i * 14, repeat: Infinity, ease: "linear" }}
            />
          ))}

          <motion.circle
            cx="100"
            cy="100"
            r="30"
            fill="url(#core)"
            animate={{ opacity: [0.4, 0.9, 0.4], scale: [0.9, 1.1, 0.9] }}
            transition={{ duration: 4, repeat: Infinity }}
            style={{ transformOrigin: "100px 100px" }}
          />

          {nodes.map((n) => (
            <line
              key={`l-${n.id}`}
              x1="100"
              y1="100"
              x2={n.x}
              y2={n.y}
              stroke={active === n.id ? "var(--primary)" : "var(--border)"}
              strokeWidth={active === n.id ? 1 : 0.5}
            />
          ))}

          {nodes.map((n, i) => {
            const hot = n.severity === "critical" || n.severity === "high";
            return (
              <g
                key={n.id}
                onMouseEnter={() => setActive(n.id)}
                onMouseLeave={() => setActive(null)}
                className="cursor-pointer"
              >
                <motion.circle
                  cx={n.x}
                  cy={n.y}
                  r={active === n.id ? 9 : 6}
                  fill={hot ? "var(--primary)" : "var(--muted-foreground)"}
                  fillOpacity={0.18}
                  animate={{ r: [5, 11, 5] }}
                  transition={{ duration: 3, repeat: Infinity, delay: i * 0.3 }}
                />
                <circle
                  cx={n.x}
                  cy={n.y}
                  r="3"
                  fill={hot ? "var(--primary)" : "var(--foreground)"}
                />
              </g>
            );
          })}

          <text x="100" y="103" textAnchor="middle" className="fill-foreground font-mono" fontSize="7">
            10.24.0.0/16
          </text>
        </svg>

        <AnimatePresence>
          {active && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="absolute inset-x-3 bottom-3 border border-primary/40 bg-popover/95 px-3 py-2 backdrop-blur"
            >
              <div className="font-mono text-xs text-primary">
                {nodes.find((n) => n.id === active)?.ip}
              </div>
              <div className="mono-label text-[9px]">
                {nodes.find((n) => n.id === active)?.vector} // {active}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="mono-label flex justify-between border-t border-border px-4 py-2.5">
        <span>08 origins // 08 paths</span>
        <span className="text-signal">syncing</span>
      </div>
    </div>
  );
}

export function AgentActivity() {
  return (
    <div className="panel">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <span className="mono-label flex items-center gap-2">
          <Cpu className="h-3 w-3 text-primary" /> agent activity
        </span>
        <ArrowUpRight className="h-3 w-3 text-muted-foreground" />
      </div>
      <div className="space-y-3 px-4 py-3">
        {AGENTS.map((a, i) => (
          <div key={a.name}>
            <div className="flex items-center justify-between font-mono text-[11px]">
              <span className="uppercase tracking-[0.12em]">{a.name}</span>
              <span className={a.state === "active" ? "text-signal" : "text-primary"}>{a.state}</span>
            </div>
            <div className="mt-1.5 h-1.5 w-full bg-muted">
              <motion.div
                className={`h-full ${a.state === "active" ? "bg-signal" : "bg-primary"}`}
                initial={{ width: 0 }}
                animate={{ width: `${a.load * 100}%` }}
                transition={{ duration: 1, delay: i * 0.12, ease: "easeOut" }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function RightRail({ alerts = [] }) {
  return (
    <div className="space-y-4">
      <SignalVelocity />
      <AttackSurface alerts={alerts} />
      <AgentActivity />
    </div>
  );
}
