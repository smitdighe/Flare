import { useEffect, useMemo, useRef, useState } from 'react';
import Icon from './Icon.jsx';

export default function CommandPalette({ open, onClose, commands = [], onExecute }) {
  const inputRef = useRef(null);
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => commands.filter((command) => `${command.label} ${command.detail || ''}`.toLowerCase().includes(query.toLowerCase())), [commands, query]);

  useEffect(() => {
    if (!open) return undefined;
    setQuery('');
    inputRef.current?.focus();
    const onKeyDown = (event) => event.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose, open]);

  if (!open) return null;
  return (
    <div className="command-palette-layer" role="presentation">
      <button type="button" className="command-palette-backdrop" onClick={onClose} aria-label="Close command palette" />
      <section className="command-palette" role="dialog" aria-modal="true" aria-labelledby="command-palette-title">
        <div className="flex items-center gap-3 border-b border-line-strong px-4 py-3"><Icon name="terminal" size={16} className="text-amber" /><input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 bg-transparent font-mono-ui text-sm text-paper outline-hidden placeholder:text-ash-dark" placeholder="Search commands or sections" aria-label="Search commands" /><kbd className="font-mono-ui text-[9px] text-ash-dark">ESC</kbd></div>
        <div className="sr-only" id="command-palette-title">Flare command palette</div>
        <div className="max-h-[52vh] overflow-y-auto p-2">
          {filtered.length === 0 && <div className="px-3 py-8 text-center font-mono-ui text-[10px] uppercase tracking-[0.1em] text-ash-dark">No matching commands</div>}
          {filtered.map((command, index) => <button type="button" key={command.id} className="command-row group flex w-full items-center gap-3 px-3 py-3 text-left" onClick={() => { onExecute(command.id); onClose(); }}><span className="flex h-7 w-7 items-center justify-center border border-line-strong text-ash group-hover:border-amber group-hover:text-amber"><Icon name={command.icon || 'arrow_forward'} size={15} /></span><span className="min-w-0 flex-1"><span className="block font-mono-ui text-[11px] uppercase tracking-[0.08em] text-paper">{command.label}</span>{command.detail && <span className="mt-1 block truncate text-[11px] text-ash-dark">{command.detail}</span>}</span><span className="font-mono-ui text-[9px] text-ash-dark">{index + 1}</span></button>)}
        </div>
      </section>
    </div>
  );
}
