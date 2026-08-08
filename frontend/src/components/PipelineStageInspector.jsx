import { useEffect, useRef } from 'react';
import Icon from './Icon.jsx';

const CONTENT = {
  classify: { label: 'CLASSIFY', title: 'Separate signal from noise.', copy: 'Groq scores severity and attack vector before the event reaches the analyst queue.', provider: 'GROQ // LLAMA-3.1-8B', metric: '118ms median' },
  enrich: { label: 'ENRICH', title: 'Add the missing context.', copy: 'AbuseIPDB and VirusTotal turn a raw source into evidence with reputation, hash, and route context.', provider: 'ABUSEIPDB + VIRUSTOTAL', metric: '212ms median' },
  reason: { label: 'REASON', title: 'Make the next move legible.', copy: 'Gemini grounds the decision in MITRE ATT&CK context and returns bounded remediation steps.', provider: 'GEMINI // RAG', metric: '376ms median' },
};

export default function PipelineStageInspector({ stage, onClose }) {
  const closeRef = useRef(null);
  const content = CONTENT[stage];

  useEffect(() => {
    closeRef.current?.focus();
    const onKeyDown = (event) => event.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  if (!content) return null;
  return (
    <div className="stage-inspector-layer" role="presentation">
      <button type="button" className="stage-inspector-backdrop" onClick={onClose} aria-label="Close stage inspector" />
      <section className="stage-inspector" role="dialog" aria-modal="true" aria-labelledby="stage-inspector-title">
        <div className="flex items-start justify-between gap-5 border-b border-line-strong px-5 py-5">
          <div><div className="eyebrow mb-2">PIPELINE STAGE // {content.label}</div><h2 id="stage-inspector-title" className="font-display text-3xl italic leading-none text-paper">{content.title}</h2></div>
          <button ref={closeRef} type="button" className="ghost-button flex h-8 w-8 items-center justify-center" onClick={onClose} aria-label="Close stage inspector"><Icon name="close" size={17} /></button>
        </div>
        <div className="grid gap-5 px-5 py-5 sm:grid-cols-[1fr_auto] sm:items-end">
          <p className="max-w-md text-sm leading-7 text-ash">{content.copy}</p>
          <div className="border-l border-amber pl-3 font-mono-ui text-[10px] uppercase tracking-[0.1em] text-ash"><div className="text-amber">{content.provider}</div><div className="mt-2">{content.metric}</div><div className="mt-1 text-green">status / nominal</div></div>
        </div>
        <div className="grid grid-cols-3 border-t border-line-strong font-mono-ui text-[9px] uppercase tracking-[0.08em] text-ash-dark"><div className="border-r border-line px-4 py-3"><span className="text-amber">01</span><br />ingest</div><div className="border-r border-line px-4 py-3"><span className="text-amber">02</span><br />signal pass</div><div className="px-4 py-3"><span className="text-amber">03</span><br />analyst handoff</div></div>
      </section>
    </div>
  );
}
