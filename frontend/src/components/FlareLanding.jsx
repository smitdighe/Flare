import { animate, stagger } from 'motion';
import { useEffect, useMemo, useRef, useState } from 'react';
import Icon from './Icon.jsx';
import MetricBlock from './MetricBlock.jsx';
import AnimatedNumber from './AnimatedNumber.jsx';
import ParticleField from './ParticleField.jsx';
import PipelineStageInspector from './PipelineStageInspector.jsx';
import ShaderBackdrop from './ShaderBackdrop.jsx';
import { formatTime } from './AlertTable.jsx';
import useMotionPointer from '../hooks/useMotionPointer.js';
import useScrollProgress from '../hooks/useScrollProgress.js';

const LOG_SEEDS = [
  'SENSOR / EDGE-01 / packet envelope accepted',
  'CLASSIFY / behavioral signature extracted',
  'ENRICH / reputation lookup returned signal',
  'REASON / MITRE context retrieved',
  'CORRELATE / source cluster updated',
  'POLICY / analyst action queued',
  'STREAM / event buffer synchronized',
  'WATCH / outbound route under observation',
];

const PIPELINE = [
  { index: '01', key: 'classify', label: 'CLASSIFY', title: 'Separate signal from noise.', copy: 'Every event is scored against severity and attack vector before it reaches an analyst.', icon: 'filter_alt', textClass: 'text-amber', bgClass: 'bg-amber' },
  { index: '02', key: 'enrich', label: 'ENRICH', title: 'Add the missing context.', copy: 'AbuseIPDB and VirusTotal turn a raw source IP into evidence you can act on.', icon: 'travel_explore', textClass: 'text-cyan', bgClass: 'bg-cyan' },
  { index: '03', key: 'reason', label: 'REASON', title: 'Make the next move legible.', copy: 'MITRE-grounded reasoning turns a verdict into a bounded remediation path.', icon: 'psychology', textClass: 'text-red', bgClass: 'bg-red' },
];

function TelemetryBackdrop() {
  const rows = useMemo(() => Array.from({ length: 18 }, (_, index) => `${String(index + 1).padStart(2, '0')}  ${LOG_SEEDS[index % LOG_SEEDS.length]}  // 0x${(index * 841 + 429).toString(16).toUpperCase()}`), []);
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <ShaderBackdrop />
      <ParticleField />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_24%,rgba(255,149,0,0.13),transparent_35%),linear-gradient(180deg,#050505_0%,#080808_58%,#050505_100%)] opacity-80" />
      <div className="absolute right-[-10vw] top-[9vh] h-[54vh] w-[56vw] border border-line-strong/60 signal-grid [mask-image:linear-gradient(90deg,transparent,black_28%,black_70%,transparent)]" />
      <div className="absolute left-[8vw] top-[17vh] h-px w-[38vw] bg-gradient-to-r from-transparent via-amber/45 to-transparent signal-line" />
      <div className="absolute bottom-[12vh] right-[8vw] h-px w-[28vw] bg-gradient-to-r from-transparent via-red/35 to-transparent signal-line" />
      <div className="absolute inset-x-0 top-[22%] mx-auto max-w-5xl rotate-[-7deg] font-mono-ui text-[9px] leading-7 text-ash-dark/70">
        {rows.map((row, index) => <div key={row} style={{ opacity: 0.12 + (index % 5) * 0.035 }}>{row}</div>)}
      </div>
      <div className="grain absolute inset-0" />
    </div>
  );
}

function LandingNav({ onLaunch, transitioning }) {
  return (
    <header className="relative z-10 mx-auto flex w-full max-w-[var(--content-max)] items-center justify-between border-b border-line px-5 py-4 lg:px-10">
      <a href="#top" className="flex items-center gap-3 text-paper" aria-label="Flare home"><span className="flare-logo-frame"><img src="/flare-logo.png" alt="Flare" className="h-6 w-6 object-contain" /></span><span className="font-mono-ui text-sm font-semibold tracking-[0.1em]">FLARE <span className="text-ash-dark">// ENGINE</span></span></a>
      <nav className="hidden items-center gap-7 font-mono-ui text-[10px] uppercase tracking-[0.12em] text-ash md:flex" aria-label="Landing sections"><a className="nav-link" href="#pipeline">Pipeline</a><a className="nav-link" href="#preview">Command center</a><a className="nav-link" href="#brief">Brief</a></nav>
      <button type="button" className={`ghost-button magnetic-button inline-flex items-center gap-2 px-3 py-2 font-mono-ui text-[10px] uppercase tracking-[0.1em] ${transitioning ? 'is-transitioning' : ''}`} onClick={onLaunch} disabled={transitioning}>{transitioning ? 'Opening engine' : 'Open command center'} <Icon name={transitioning ? 'sync' : 'arrow_outward'} size={15} /></button>
    </header>
  );
}

function CommandPreview({ onLaunch }) {
  const [activeRow, setActiveRow] = useState(0);
  const rows = [
    ['14:32:01', 'CRITICAL', 'SQL_INJECTION', '185.220.101.14', 'T1190'],
    ['14:31:44', 'HIGH', 'BRUTE_FORCE', '45.142.212.61', 'T1110'],
    ['14:30:17', 'MEDIUM', 'PORT_SCAN', '103.77.192.88', 'T1046'],
  ];
  return (
    <div className="preview-shell relative overflow-hidden border border-line-strong bg-ink-900/95 shadow-[18px_18px_0_rgba(255,149,0,0.08)]">
      <div className="flex items-center justify-between border-b border-line-strong px-4 py-3 font-mono-ui text-[9px] uppercase tracking-[0.12em] text-ash"><span className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full border border-green bg-transparent animate-pulse" /> live triage buffer</span><span>{String(activeRow + 1).padStart(2, '0')} of 200 signals</span></div>
      <div className="overflow-x-auto"><table className="w-full min-w-[620px] border-collapse font-mono-ui text-[10px]"><thead><tr className="text-left uppercase tracking-[0.1em] text-ash-dark"><th className="px-4 py-3 font-medium">time</th><th className="px-2 py-3 font-medium">severity</th><th className="px-2 py-3 font-medium">vector</th><th className="px-2 py-3 font-medium">source</th><th className="px-4 py-3 text-right font-medium">mitre</th></tr></thead><tbody>{rows.map((row, index) => <tr key={row[0]} className={`preview-row border-t border-line text-ash ${activeRow === index ? 'preview-row-active' : ''}`} style={{ '--preview-index': index }} onClick={() => setActiveRow(index)} tabIndex={0} onKeyDown={(event) => (event.key === 'Enter' || event.key === ' ') && setActiveRow(index)}><td className="px-4 py-3 text-paper">{row[0]}</td><td className={`px-2 py-3 ${row[1] === 'CRITICAL' ? 'text-red' : row[1] === 'HIGH' ? 'text-amber' : 'text-yellow'}`}>[ {row[1]} ]</td><td className="px-2 py-3 text-paper">{row[2]}</td><td className="px-2 py-3">{row[3]}</td><td className="px-4 py-3 text-right text-amber">{row[4]}</td></tr>)}</tbody></table></div>
      <button type="button" className="group flex w-full items-center justify-between border-t border-line-strong px-4 py-3 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-amber transition-colors hover:bg-amber hover:text-ink-950" onClick={onLaunch}><span>inspect the full buffer</span><Icon name="arrow_forward" size={15} className="transition-transform group-hover:translate-x-1" /></button>
    </div>
  );
}

export default function FlareLanding({ onLaunch }) {
  const rootRef = useRef(null);
  const [time, setTime] = useState(new Date());
  const [inspectorStage, setInspectorStage] = useState(null);
  const [transitioning, setTransitioning] = useState(false);
  const { smoothX, smoothY } = useMotionPointer();
  const { progress } = useScrollProgress();

  useEffect(() => {
    const interval = window.setInterval(() => setTime(new Date()), 1000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return undefined;
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add('is-visible')), { threshold: 0.14 });
    root.querySelectorAll('[data-reveal]').forEach((element) => observer.observe(element));
    const controls = animate(root.querySelectorAll('.hero-copy-line'), { opacity: [0, 1], y: [24, 0] }, { delay: stagger(0.09, { startDelay: 0.15 }), duration: 0.8, ease: [0.16, 1, 0.3, 1] });
    return () => { observer.disconnect(); controls.stop(); };
  }, []);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return undefined;
    const unsubscribeX = smoothX.on('change', (value) => root.style.setProperty('--spotlight-x', `${value}px`));
    const unsubscribeY = smoothY.on('change', (value) => root.style.setProperty('--spotlight-y', `${value}px`));
    return () => { unsubscribeX(); unsubscribeY(); };
  }, [smoothX, smoothY]);

  const launch = () => {
    if (transitioning) return;
    setTransitioning(true);
    window.setTimeout(onLaunch, 300);
  };

  return (
    <div ref={rootRef} id="top" className="relative min-h-screen overflow-hidden bg-ink-950 text-paper landing-hero-grid pointer-spotlight" style={{ '--scroll-progress': progress }}>
      <TelemetryBackdrop />
      <div className="landing-progress" style={{ transform: `scaleX(${progress})` }} />
      <LandingNav onLaunch={launch} transitioning={transitioning} />
      <main className="relative z-10 mx-auto max-w-[var(--content-max)] px-5 lg:px-10">
        <section className="grid min-h-[calc(100vh-74px)] items-center gap-14 py-20 lg:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)] lg:gap-20 lg:py-28">
          <div data-reveal className="reveal-block max-w-3xl hero-copy-line"><div className="eyebrow mb-7 flex items-center gap-3"><span className="h-px w-8 bg-amber" /> SYSTEM: FLARE v2.4 // OPERATIONAL</div><h1 className="font-display max-w-4xl text-[clamp(3.3rem,8.6vw,8rem)] font-medium leading-[0.88] tracking-[-0.075em] text-paper">Triage at the speed of the signal.</h1><p className="mt-8 max-w-xl text-base leading-7 text-ash md:text-lg">Flare is a multi-agent security engine for teams that need the verdict, the evidence, and the next move before the noise compounds.<span className="cursor-block" /></p><div className="mt-10 flex flex-wrap items-center gap-3"><button type="button" className="terminal-button magnetic-button inline-flex items-center gap-3 px-4 py-3 font-mono-ui text-[11px] font-semibold uppercase tracking-[0.1em]" onClick={launch}>Initiate deployment <Icon name="arrow_forward" size={16} /></button><a className="ghost-button inline-flex items-center gap-2 px-4 py-3 font-mono-ui text-[11px] uppercase tracking-[0.1em]" href="#pipeline">Read the brief <Icon name="south" size={15} /></a></div><div className="mt-12 flex flex-wrap gap-x-8 gap-y-3 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-ash-dark"><span>event time {formatTime(time.toISOString())}</span><span>no persistence layer required</span><span className="text-green">pipeline nominal</span></div></div>
          <div data-reveal className="reveal-block [transition-delay:120ms] hero-copy-line"><div className="mb-4 flex items-center justify-between font-mono-ui text-[10px] uppercase tracking-[0.12em] text-ash"><span>Field telemetry</span><span className="text-green">live</span></div><div className="grid grid-cols-2 border border-line-strong bg-ink-900/80"><div className="border-b border-r border-line-strong p-5"><MetricBlock label="Accuracy metric" value={<AnimatedNumber value={0.613} decimals={3} />} note="F1 // CICIDS2017" /></div><div className="border-b border-line-strong p-5"><MetricBlock label="Triage latency" value="<1s" note="classifier + context" tone="cyan" /></div><div className="col-span-2 p-5"><div className="flex items-end justify-between gap-5"><div><div className="font-mono-ui text-[9px] uppercase tracking-[0.12em] text-ash-dark">Active modules</div><div className="mt-2 font-mono-ui text-sm text-paper">CLASSIFY <span className="text-ash-dark">→</span> ENRICH <span className="text-ash-dark">→</span> REASON</div></div><div className="flex items-center gap-1">{[0, 1, 2, 3, 4, 5, 6].map((index) => <span key={index} className={`module-tick h-3 w-3 border ${index < 5 ? 'border-amber bg-amber' : 'border-line-strong'}`} style={{ '--module-index': index }} />)}</div></div></div></div><div className="mt-5 border-l-2 border-amber pl-4 font-mono-ui text-[10px] leading-5 text-ash">&gt; raw event arrives<br />&gt; agents isolate the meaningful parts<br />&gt; analyst gets a bounded decision</div></div>
        </section>

        <section id="pipeline" className="border-t border-line py-24 lg:py-32"><div data-reveal className="reveal-block grid gap-7 lg:grid-cols-[0.76fr_1.24fr] lg:gap-20"><div><div className="eyebrow mb-5">The operating model</div><h2 className="font-display max-w-md text-4xl font-medium tracking-[-0.055em] text-paper md:text-5xl">Three passes. One clear answer.</h2></div><p className="max-w-xl text-sm leading-7 text-ash md:text-base">The pipeline is deliberately linear. Each stage removes a different kind of uncertainty, so your team can move from raw alert to defensible action without jumping between tools.</p></div><div className="mt-14 grid border-y border-line-strong md:grid-cols-3">{PIPELINE.map((step, index) => <button type="button" key={step.index} data-reveal className={`pipeline-card reveal-block group border-line-strong p-6 text-left md:p-8 ${index < PIPELINE.length - 1 ? 'md:border-r' : ''}`} style={{ transitionDelay: `${index * 100 + 100}ms` }} onClick={() => setInspectorStage(step.key)}><div className="flex items-center justify-between"><span className="font-mono-ui text-[10px] text-ash-dark">{step.index}</span><span className={`icon ${step.textClass}`} style={{ fontSize: 20 }}>{step.icon}</span></div><div className={`mt-12 h-1 w-9 ${step.bgClass} transition-transform duration-300 group-hover:scale-x-[1.75] origin-left`} /><h3 className="font-display mt-5 text-2xl font-medium italic tracking-[-0.035em] text-paper">{step.title}</h3><p className="mt-3 text-sm leading-6 text-ash">{step.copy}</p><div className="mt-7 flex items-center justify-between font-mono-ui text-[9px] uppercase tracking-[0.12em] text-ash-dark"><span>{step.label} // agent stage</span><Icon name="north_east" size={14} className="text-amber transition-transform group-hover:-translate-y-1 group-hover:translate-x-1" /></div></button>)}</div></section>

        <section id="preview" className="grid items-center gap-12 border-t border-line py-24 lg:grid-cols-[0.78fr_1.22fr] lg:py-32"><div data-reveal className="reveal-block"><div className="eyebrow mb-5">Inside the command center</div><h2 className="font-display max-w-lg text-4xl font-medium tracking-[-0.055em] text-paper md:text-5xl">The dashboard does not ask you to admire it.</h2><p className="mt-6 max-w-md text-sm leading-7 text-ash md:text-base">It puts the alert queue, context, and recommended action in the same line of sight. Signal first. Ceremony second.</p><div className="mt-8 space-y-3 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-ash"><div className="flex items-center gap-3"><span className="h-1.5 w-1.5 bg-amber" /> focus rows with j / k</div><div className="flex items-center gap-3"><span className="h-1.5 w-1.5 bg-cyan" /> inspect evidence without losing your place</div><div className="flex items-center gap-3"><span className="h-1.5 w-1.5 bg-red" /> keep critical activity visible</div></div></div><div data-reveal className="reveal-block [transition-delay:120ms]"><CommandPreview onLaunch={launch} /></div></section>

        <section id="brief" className="border-t border-line py-24 lg:py-32"><div className="grid gap-10 lg:grid-cols-[1fr_1fr] lg:items-end"><div data-reveal className="reveal-block"><div className="eyebrow mb-5">The command brief</div><h2 className="font-display max-w-2xl text-5xl font-medium tracking-[-0.065em] text-paper md:text-7xl">Less noise.<br /><span className="text-amber">More agency.</span></h2></div><div data-reveal className="reveal-block [transition-delay:120ms]"><p className="max-w-md text-sm leading-7 text-ash md:ml-auto md:text-base">Bring the live feed into focus, let the agents do the first pass, and keep the decision surface readable for the person who owns the incident.</p><button type="button" className="terminal-button magnetic-button mt-8 inline-flex items-center gap-3 px-4 py-3 font-mono-ui text-[11px] font-semibold uppercase tracking-[0.1em]" onClick={launch}>Open Flare command center <Icon name="arrow_forward" size={16} /></button></div></div></section>
      </main>
      <footer className="relative z-10 border-t border-line"><div className="mx-auto flex max-w-[var(--content-max)] flex-col gap-3 px-5 py-6 font-mono-ui text-[10px] uppercase tracking-[0.12em] text-ash-dark md:flex-row md:items-center md:justify-between lg:px-10"><span>FLARE // MULTI-AGENT SECURITY ENGINE</span><span>CLASSIFY / ENRICH / REASON</span><span>BUILD 2.4.0-STABLE</span></div></footer>
      <div className="fixed bottom-5 left-5 z-20 hidden font-mono-ui text-[9px] uppercase tracking-[0.18em] text-ash-dark md:block">SCROLL / {String(Math.round(progress * 100)).padStart(2, '0')}%</div>
      {inspectorStage && <PipelineStageInspector stage={inspectorStage} onClose={() => setInspectorStage(null)} />}
    </div>
  );
}
