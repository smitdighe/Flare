import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronDown, Copy, X, ArrowRight, ShieldAlert } from "lucide-react";
import { toast } from "sonner";

function Section({ label, children, right }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="border-b border-border">
      <div className="flex items-center justify-between px-5 py-3">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="mono-label flex items-center gap-2 text-primary transition-opacity hover:opacity-80"
        >
          <motion.span animate={{ rotate: open ? 0 : -90 }}>
            <ChevronDown className="h-3 w-3" />
          </motion.span>
          {label}
        </button>
        {right}
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-4">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function AlertDrawer({ alert, onClose }) {
  const copy = (value, label) => {
    navigator.clipboard?.writeText(value).catch(() => {});
    toast.success(`${label} copied`, { description: value });
  };

  if (!alert) return null;

  return (
    <AnimatePresence>
      <>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 z-40 bg-background/70 backdrop-blur-sm"
        />
        <motion.aside
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "spring", stiffness: 300, damping: 32 }}
          className="fixed right-0 top-0 z-50 flex h-full w-full max-w-xl flex-col overflow-y-auto border-l border-border bg-card shadow-[var(--shadow-panel)]"
        >
          <div className="sticky top-0 z-10 border-b border-border bg-card/95 px-5 py-4 backdrop-blur">
            <div className="flex items-start justify-between">
              <div>
                <div className="mono-label text-primary">signal evidence // {alert.id}</div>
                <div className="font-display mt-1 text-3xl leading-none">{alert.attack_type || alert.vector}</div>
                <div className="mono-label mt-2 flex items-center gap-2">
                  <span className={`h-1.5 w-1.5 rounded-full bg-current ${
                    { critical: "text-destructive", high: "text-primary", medium: "text-primary-glow", low: "text-signal" }[alert.severity] || "text-muted-foreground"
                  }`} />
                  {alert.severity} // {alert.protocol || alert.proto}:{alert.dest_port || alert.port}
                </div>
              </div>
              <motion.button
                whileHover={{ rotate: 90 }}
                type="button"
                onClick={onClose}
                className="border border-border p-2 text-muted-foreground transition-colors hover:border-destructive/60 hover:text-destructive"
              >
                <X className="h-4 w-4" />
              </motion.button>
            </div>

            <div className="mt-4 h-1 w-full bg-muted">
              <motion.div
                className="h-full bg-primary"
                initial={{ width: 0 }}
                animate={{ width: `${alert.confidence || alert.ioc_reputation || 80}%` }}
                transition={{ duration: 0.9, ease: "easeOut" }}
              />
            </div>
            <div className="mono-label mt-1.5">classifier confidence {alert.confidence || alert.ioc_reputation || 80}%</div>
          </div>

          <Section
            label="route"
            right={
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => copy(alert.src_ip || alert.src, "source")}
                  className="mono-label flex items-center gap-1 hover:text-primary"
                >
                  <Copy className="h-3 w-3" /> copy src
                </button>
                <button
                  type="button"
                  onClick={() => copy(alert.dest_ip || alert.dst, "destination")}
                  className="mono-label flex items-center gap-1 hover:text-primary"
                >
                  <Copy className="h-3 w-3" /> copy dst
                </button>
              </div>
            }
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="font-mono text-lg">{alert.src_ip || alert.src}</div>
                <div className="mono-label text-[9px]">source // abuse {alert.ioc_reputation || alert.abuse || 0}%</div>
              </div>
              <motion.div
                animate={{ x: [-6, 6, -6] }}
                transition={{ duration: 2.2, repeat: Infinity }}
                className="text-primary"
              >
                <ArrowRight className="h-4 w-4" />
              </motion.div>
              <div className="text-right">
                <div className="font-mono text-lg">{alert.dest_ip || alert.dst}</div>
                <div className="mono-label text-[9px]">dest port {alert.dest_port || alert.port}</div>
              </div>
            </div>
          </Section>

          <Section label="pipeline trace">
            <div className="space-y-3">
              {(alert.stages || [
                { name: "classify", engine: "groq // llama-3.1-8b", ms: alert.classify_latency_ms || 88 },
                { name: "enrich", engine: "abuseipdb + virustotal", ms: alert.enrich_latency_ms || 174 },
                { name: "reason", engine: "gemini-1.5-flash // rag", ms: alert.reasoning_latency_ms || 302 },
              ]).map((s, i) => (
                <motion.div
                  key={s.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + i * 0.12 }}
                >
                  <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-[0.16em]">
                    <span className="flex items-center gap-2 text-primary">
                      <span className="h-2 w-2 bg-primary" /> {s.name}
                    </span>
                    <span className="text-primary">{s.ms}ms</span>
                  </div>
                  <div className="mono-label mt-1 text-[9px]">{s.engine}</div>
                  <div className="mt-1.5 h-1 w-full bg-muted">
                    <motion.div
                      className="h-full bg-primary/70"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(100, (s.ms / 320) * 100)}%` }}
                      transition={{ duration: 0.8, delay: 0.15 + i * 0.12 }}
                    />
                  </div>
                </motion.div>
              ))}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <div className="border border-border px-3 py-2 font-mono text-[11px]">
                  abuse {alert.ioc_reputation || alert.abuse || 0}%
                </div>
                <div className="border border-border px-3 py-2 font-mono text-[11px] text-primary">
                  {alert.vt_ip || alert.vt || "vt clean"}
                </div>
              </div>
            </div>
          </Section>

          <Section label="mitre att&ck / technique">
            <div className="font-mono text-2xl text-primary">{alert.mitre_technique || alert.mitre}</div>
            <div className="mt-1 font-mono text-xs">{alert.mitre_name || alert.mitreName}</div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              The retrieved technique grounds the reasoning stage and prioritises the next analyst action.
            </p>
          </Section>

          <Section label="agent log // explanation">
            <div className="border border-border bg-background/60 px-3 py-3 font-mono text-xs leading-relaxed text-muted-foreground">
              <span className="text-primary">// </span>
              {alert.explanation || "Awaiting reason stage output."}
            </div>
          </Section>

          <Section label="recommended action">
            <div className="border-l-2 border-primary bg-primary/5 px-3 py-3 text-sm">{alert.remediation || alert.action}</div>
            <motion.button
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.97 }}
              type="button"
              onClick={() =>
                toast.success("Action queued", { description: `${alert.id} handed to playbook runner` })
              }
              className="mt-4 flex items-center gap-2 bg-primary px-4 py-2.5 font-mono text-[11px] uppercase tracking-[0.18em] text-primary-foreground"
              style={{ boxShadow: "var(--shadow-ember)" }}
            >
              <ShieldAlert className="h-3.5 w-3.5" /> queue action <ArrowRight className="h-3.5 w-3.5" />
            </motion.button>
          </Section>
        </motion.aside>
      </>
    </AnimatePresence>
  );
}
