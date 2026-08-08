const NOW = Date.now();

const seedAlerts = [
  {
    id: 'ALT-9F2C1A', timestamp: new Date(NOW - 34_000).toISOString(), src_ip: '185.220.101.14', dest_ip: '10.24.7.18', dest_port: 443, protocol: 'TCP', signature: 'ET EXPLOIT Possible SQL Injection Attempt', severity: 'critical', attack_type: 'sql_injection', classify_latency_ms: 118, enrich_latency_ms: 244, reasoning_latency_ms: 376, ioc_reputation: 91, ioc_checked: true, vt_ip: 'malicious', vt_hash: 'suspicious', mitre_technique: 'T1190', explanation: 'The request contains a UNION-based injection sequence targeting the public application edge. The source has a high abuse score and repeated attempts across adjacent endpoints.', remediation: 'Block the source at the edge, rotate the exposed application credential, and review WAF logs for successful query execution.',
  },
  {
    id: 'ALT-7B84D0', timestamp: new Date(NOW - 82_000).toISOString(), src_ip: '45.142.212.61', dest_ip: '10.24.2.11', dest_port: 22, protocol: 'TCP', signature: 'Multiple SSH Failed Login Attempts', severity: 'high', attack_type: 'brute_force', classify_latency_ms: 96, enrich_latency_ms: 188, reasoning_latency_ms: 289, ioc_reputation: 78, ioc_checked: true, vt_ip: 'malicious', vt_hash: 'clean', mitre_technique: 'T1110', explanation: 'A burst of password guesses against an exposed SSH service crossed the behavioral threshold for automated credential attack.', remediation: 'Rate-limit the source, require key-based authentication, and confirm no successful sessions from this origin.',
  },
  {
    id: 'ALT-2D11AC', timestamp: new Date(NOW - 166_000).toISOString(), src_ip: '103.77.192.88', dest_ip: '10.24.5.9', dest_port: 8080, protocol: 'TCP', signature: 'Nmap SYN Scan Against Service Range', severity: 'medium', attack_type: 'port_scan', classify_latency_ms: 72, enrich_latency_ms: 142, reasoning_latency_ms: 204, ioc_reputation: 42, ioc_checked: true, vt_ip: 'suspicious', vt_hash: 'clean', mitre_technique: 'T1046', explanation: 'The source enumerated a contiguous range of service ports with low payload volume and no evidence of exploitation yet.', remediation: 'Keep the source under observation, reduce exposed service surface, and correlate against later exploit attempts.',
  },
  {
    id: 'ALT-4A88E6', timestamp: new Date(NOW - 240_000).toISOString(), src_ip: '10.24.6.43', dest_ip: '10.24.1.21', dest_port: 53, protocol: 'UDP', signature: 'Unusual DNS Volume To External Resolver', severity: 'high', attack_type: 'ddos', classify_latency_ms: 104, enrich_latency_ms: 221, reasoning_latency_ms: 318, ioc_reputation: 67, ioc_checked: true, vt_ip: 'suspicious', vt_hash: 'unknown', mitre_technique: 'T1071.004', explanation: 'A single internal host is emitting a statistically abnormal DNS request burst toward an external resolver, consistent with tunneling or amplification activity.', remediation: 'Isolate the host from the resolver path and inspect process-level DNS clients for beaconing or payload staging.',
  },
  {
    id: 'ALT-6C70B2', timestamp: new Date(NOW - 316_000).toISOString(), src_ip: '172.18.0.4', dest_ip: '10.24.3.76', dest_port: 445, protocol: 'TCP', signature: 'SMB Lateral Movement Pattern', severity: 'high', attack_type: 'malware', classify_latency_ms: 111, enrich_latency_ms: 206, reasoning_latency_ms: 334, ioc_reputation: 54, ioc_checked: true, vt_ip: 'unknown', vt_hash: 'malicious', mitre_technique: 'T1021.002', explanation: 'The connection sequence resembles post-compromise SMB movement between workstations, with a matching payload hash in the enrichment result.', remediation: 'Quarantine the source and destination hosts, preserve memory captures, and hunt for the same hash across the estate.',
  },
  {
    id: 'ALT-1F932E', timestamp: new Date(NOW - 412_000).toISOString(), src_ip: '192.168.4.17', dest_ip: '10.24.9.44', dest_port: 80, protocol: 'TCP', signature: 'HTTP Request With Suspicious User Agent', severity: 'medium', attack_type: 'other', classify_latency_ms: 88, enrich_latency_ms: 0, reasoning_latency_ms: 0, ioc_reputation: 0, ioc_checked: false, mitre_technique: 'T1071.001', explanation: 'The user agent is uncommon for the application and appears alongside a low-volume path probe. Context is insufficient for escalation.', remediation: 'Keep the request in watch state and enrich if the source repeats across protected routes.',
  },
  {
    id: 'ALT-581C3F', timestamp: new Date(NOW - 510_000).toISOString(), src_ip: '91.214.124.77', dest_ip: '10.24.1.8', dest_port: 3389, protocol: 'TCP', signature: 'RDP Brute Force Heuristic', severity: 'critical', attack_type: 'brute_force', classify_latency_ms: 126, enrich_latency_ms: 312, reasoning_latency_ms: 426, ioc_reputation: 96, ioc_checked: true, vt_ip: 'malicious', vt_hash: 'unknown', mitre_technique: 'T1110.001', explanation: 'The source generated sustained credential attempts against an externally reachable RDP endpoint and is strongly associated with abuse reports.', remediation: 'Disable public RDP, block the source immediately, and validate account lockout and MFA enforcement.',
  },
  {
    id: 'ALT-38F0B7', timestamp: new Date(NOW - 640_000).toISOString(), src_ip: '10.24.8.12', dest_ip: '10.24.0.2', dest_port: 443, protocol: 'TCP', signature: 'Outbound TLS Beacon Interval Deviation', severity: 'low', attack_type: 'other', classify_latency_ms: 51, enrich_latency_ms: 0, reasoning_latency_ms: 0, ioc_reputation: 0, ioc_checked: false, mitre_technique: 'T1071.001', explanation: 'A low-confidence timing deviation was detected in outbound encrypted traffic. There is no current reputation evidence or payload indicator.', remediation: 'Retain for correlation with endpoint telemetry; no containment action recommended yet.',
  },
  {
    id: 'ALT-22E9AA', timestamp: new Date(NOW - 782_000).toISOString(), src_ip: '198.51.100.42', dest_ip: '10.24.7.18', dest_port: 443, protocol: 'TCP', signature: 'Command Injection Payload In Request Body', severity: 'critical', attack_type: 'sql_injection', classify_latency_ms: 131, enrich_latency_ms: 285, reasoning_latency_ms: 401, ioc_reputation: 88, ioc_checked: true, vt_ip: 'malicious', vt_hash: 'suspicious', mitre_technique: 'T1059', explanation: 'The request body includes shell metacharacters in a parameter normally treated as data. The target is the same application edge as a prior critical alert.', remediation: 'Block the source and inspect the application host for command execution and child-process anomalies.',
  },
  {
    id: 'ALT-903E1D', timestamp: new Date(NOW - 923_000).toISOString(), src_ip: '172.16.14.9', dest_ip: '10.24.2.27', dest_port: 443, protocol: 'TCP', signature: 'Bulk Outbound Transfer To New ASN', severity: 'medium', attack_type: 'other', classify_latency_ms: 84, enrich_latency_ms: 0, reasoning_latency_ms: 0, ioc_reputation: 0, ioc_checked: false, mitre_technique: 'T1041', explanation: 'The destination ASN is new for this host and the transfer volume is elevated, but the connection is still below the exfiltration threshold.', remediation: 'Correlate with the host owner and inspect the destination reputation before escalating.',
  },
];

export function createMockAlerts() {
  return seedAlerts.map((alert) => ({ ...alert }));
}

export function createMockAlert(index = 0) {
  const source = seedAlerts[index % seedAlerts.length];
  return {
    ...source,
    id: `ALT-${Math.random().toString(16).slice(2, 8).toUpperCase()}`,
    timestamp: new Date().toISOString(),
    signature: index % 2 === 0 ? source.signature : `${source.signature} // replayed signal`,
  };
}
