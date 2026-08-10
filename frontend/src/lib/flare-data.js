export const SEVERITY_STYLES = {
  critical: { text: "text-destructive", bg: "bg-destructive/15", ring: "border-destructive/50" },
  high: { text: "text-primary", bg: "bg-primary/15", ring: "border-primary/50" },
  medium: { text: "text-primary-glow", bg: "bg-primary-glow/10", ring: "border-primary-glow/40" },
  low: { text: "text-signal", bg: "bg-signal/10", ring: "border-signal/40" },
  unknown: { text: "text-muted-foreground", bg: "bg-muted", ring: "border-border" },
};

export const SECTIONS = [
  { slug: "overview", label: "overview" },
  { slug: "live-feed", label: "live feed" },
  { slug: "health-metrics", label: "health metrics" },
  { slug: "system-logs", label: "system logs" },
  { slug: "threat-clusters", label: "threat clusters" },
  { slug: "evaluation", label: "evaluation" },
  { slug: "rules", label: "rules" },
  { slug: "playbooks", label: "playbooks" },
  { slug: "notifications", label: "notifications" },
  { slug: "export", label: "export" },
];

export const AGENTS = [
  { name: "sentinel-alpha", load: 0.82, state: "active" },
  { name: "cortex-03", load: 0.94, state: "active" },
  { name: "sentinel-beta", load: 0.41, state: "throttled" },
  { name: "reasoner-01", load: 0.67, state: "active" },
];

export const SERVICES = [
  { name: "ids ingest", latency: 42, uptime: 99.99, state: "healthy" },
  { name: "abuseipdb", latency: 188, uptime: 99.82, state: "healthy" },
  { name: "virustotal", latency: 264, uptime: 98.41, state: "degraded" },
  { name: "vector store", latency: 61, uptime: 99.97, state: "healthy" },
  { name: "groq gateway", latency: 96, uptime: 99.91, state: "healthy" },
  { name: "websocket relay", latency: 18, uptime: 99.99, state: "healthy" },
];

export function velocitySeries(seed = 1) {
  return Array.from({ length: 32 }, (_, i) => {
    const w = Math.sin((i + seed) / 3.1) * 0.5 + Math.sin((i + seed) / 1.3) * 0.25;
    return Math.max(0.06, 0.5 + w * 0.42);
  });
}
