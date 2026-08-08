"""
Expanded MITRE ATT&CK technique corpus — 30 techniques covering the full
range of attack types in the Flare pipeline. Each entry has original
summaries written for this project, not verbatim MITRE text.
"""
MITRE_TECHNIQUES = [
    {
        "id": "T1046",
        "name": "Network Service Discovery",
        "attack_types": ["port_scan"],
        "description": (
            "An attacker probes a target's open ports and running services to map out "
            "what's reachable before deciding how to attack further. Often the very first "
            "step in an intrusion, using tools like Nmap."
        ),
        "remediation": [
            "Block or rate-limit the source IP at the firewall",
            "Close unnecessary open ports and disable unused services",
            "Enable IDS alerting on sequential port-scan patterns",
            "Review logs for follow-up activity from the same source",
        ],
        "severity_hint": "low",
    },
    {
        "id": "T1595",
        "name": "Active Scanning",
        "attack_types": ["port_scan"],
        "description": (
            "Reconnaissance where an attacker actively probes the network (vulnerability "
            "scans, service banners) to find exploitable weaknesses before the real attack."
        ),
        "remediation": [
            "Rate-limit or block repeated probing from the same source",
            "Patch known vulnerabilities that scanners commonly fingerprint",
            "Reduce information leaked in service banners",
        ],
        "severity_hint": "low",
    },
    {
        "id": "T1595.001",
        "name": "Scanning IP Blocks",
        "attack_types": ["port_scan"],
        "description": (
            "An attacker scans entire IP ranges to identify live hosts and open ports, "
            "building a target map before launching further attacks."
        ),
        "remediation": [
            "Monitor for sequential IP scanning patterns in network logs",
            "Implement network segmentation to limit reconnaissance value",
            "Deploy honeypots to detect scanning activity early",
        ],
        "severity_hint": "low",
    },
    {
        "id": "T1498",
        "name": "Network Denial of Service",
        "attack_types": ["ddos"],
        "description": (
            "An attacker floods a target with traffic (e.g. SYN floods) to exhaust server "
            "resources or bandwidth, making the service unavailable to legitimate users."
        ),
        "remediation": [
            "Enable SYN cookies / rate limiting on the affected service",
            "Route traffic through a DDoS scrubbing service or CDN",
            "Block the offending source IP ranges upstream",
            "Scale horizontally or fail over if the attack is sustained",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1499",
        "name": "Endpoint Denial of Service",
        "attack_types": ["ddos"],
        "description": (
            "Similar to network DoS but targeting application-layer resources (CPU, memory, "
            "connection pools) on a specific endpoint rather than raw bandwidth."
        ),
        "remediation": [
            "Add application-layer rate limiting per client/IP",
            "Cache expensive endpoints to reduce backend load",
            "Set connection and request timeouts aggressively",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1498.001",
        "name": "Direct Network Flood",
        "attack_types": ["ddos"],
        "description": (
            "An attacker sends massive volumes of traffic directly to overwhelm network "
            "bandwidth and infrastructure, using UDP floods, ICMP floods, or SYN floods."
        ),
        "remediation": [
            "Enable upstream DDoS mitigation (CDN or scrubbing center)",
            "Configure infrastructure to drop oversized or malformed packets",
            "Implement BGP Flowspec or RTBH for source-based traffic filtering",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1190",
        "name": "Exploit Public-Facing Application",
        "attack_types": ["sql_injection"],
        "description": (
            "An attacker exploits a vulnerability in an internet-facing application (like SQL "
            "injection in a login form or search field) to gain unauthorized access or data."
        ),
        "remediation": [
            "Use parameterized queries / prepared statements everywhere",
            "Deploy a Web Application Firewall (WAF) in front of the app",
            "Patch the vulnerable application immediately",
            "Audit the database for signs of data exfiltration",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1505",
        "name": "Server Software Component (Web Shell)",
        "attack_types": ["sql_injection", "malware"],
        "description": (
            "After initial compromise (often via SQL injection or file upload flaws), an "
            "attacker plants a web shell to maintain persistent remote access to the server."
        ),
        "remediation": [
            "Scan the web root for unexpected/recently modified files",
            "Restrict write permissions on web-servable directories",
            "Rotate credentials and re-image the server if a shell is confirmed",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1190.001",
        "name": "SQL Injection",
        "attack_types": ["sql_injection"],
        "description": (
            "An attacker injects malicious SQL statements into application queries to "
            "extract, modify, or delete data, or escalate database privileges."
        ),
        "remediation": [
            "Use parameterized queries or ORM frameworks",
            "Apply input validation and sanitization on all user inputs",
            "Deploy a WAF with SQL injection rules",
            "Audit database permissions and restrict application user privileges",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1059",
        "name": "Command and Scripting Interpreter (PowerShell)",
        "attack_types": ["malware"],
        "description": (
            "An attacker uses PowerShell (or another scripting interpreter) to download and "
            "execute malicious payloads, often to evade traditional antivirus detection."
        ),
        "remediation": [
            "Disable PowerShell for non-admin users where feasible",
            "Enable PowerShell script block logging and constrained language mode",
            "Isolate the affected host from the network",
            "Scan for persistence mechanisms (scheduled tasks, registry run keys)",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1105",
        "name": "Ingress Tool Transfer",
        "attack_types": ["malware"],
        "description": (
            "An attacker downloads additional tools or malware onto a compromised host from "
            "an external server, expanding their capabilities after initial access."
        ),
        "remediation": [
            "Block outbound connections to the identified C2/download server",
            "Isolate the affected host and inspect for dropped files",
            "Review egress firewall rules for unusual outbound destinations",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1071",
        "name": "Application Layer Protocol (C2 Callback)",
        "attack_types": ["malware"],
        "description": (
            "Malware on a compromised host calls back to an attacker-controlled server over "
            "normal-looking protocols (HTTP/DNS) to receive commands or exfiltrate data."
        ),
        "remediation": [
            "Block the destination IP/domain at the firewall or DNS layer",
            "Isolate the infected host from the network immediately",
            "Hunt for other hosts beaconing to the same destination",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1110",
        "name": "Brute Force",
        "attack_types": ["brute_force"],
        "description": (
            "An attacker rapidly attempts many username/password combinations against a login "
            "service, hoping to guess valid credentials."
        ),
        "remediation": [
            "Enable account lockout after repeated failed attempts",
            "Enforce multi-factor authentication (MFA)",
            "Block the source IP at the firewall",
            "Review authentication logs for any successful logins from that source",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1078",
        "name": "Valid Accounts",
        "attack_types": ["brute_force"],
        "description": (
            "Once credentials are guessed or stolen, an attacker uses legitimate account "
            "credentials to blend in with normal activity and avoid detection."
        ),
        "remediation": [
            "Force a password reset on the affected account",
            "Review account activity for anomalous access patterns",
            "Enable MFA to prevent reuse of stolen credentials",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1071.004",
        "name": "DNS Tunneling / C2 over DNS",
        "attack_types": ["malware"],
        "description": (
            "An attacker encodes commands or exfiltrated data inside DNS queries to a domain "
            "they control, since DNS traffic is rarely inspected closely."
        ),
        "remediation": [
            "Block resolution of the suspicious domain at the DNS resolver",
            "Enable DNS query logging and anomaly detection",
            "Isolate hosts making unusual volumes of DNS requests",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1571",
        "name": "Non-Standard Port",
        "attack_types": ["malware", "port_scan"],
        "description": (
            "C2 traffic or data exfiltration running over unusual ports (4444, 8080, etc.) "
            "to evade standard port-based monitoring rules."
        ),
        "remediation": [
            "Block non-essential outbound ports at the firewall",
            "Audit connections on unusual ports for all internal hosts",
            "Implement network allowlisting for critical systems",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1497",
        "name": "Virtualization/Sandbox Evasion",
        "attack_types": ["malware"],
        "description": (
            "Malware that detects it's running in a VM or sandbox and changes behavior to "
            "avoid analysis, making it harder to detect in automated security tools."
        ),
        "remediation": [
            "Use bare-metal analysis environments for suspicious samples",
            "Monitor for anti-VM indicators in process behavior",
            "Combine sandbox analysis with manual reverse engineering",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1027",
        "name": "Obfuscated Files or Information",
        "attack_types": ["malware"],
        "description": (
            "An attacker hides malicious code or data using encoding, encryption, or "
            "compression to evade signature-based detection tools."
        ),
        "remediation": [
            "Use behavior-based detection rather than signature-only tools",
            "Decode and analyze suspicious files in isolated environments",
            "Monitor for processes executing decoded payloads",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1562",
        "name": "Impair Defenses",
        "attack_types": ["malware"],
        "description": (
            "An attacker disables or modifies security tools (EDR, AV, logging) on a "
            "compromised system to avoid detection during lateral movement and exfiltration."
        ),
        "remediation": [
            "Monitor for unexpected security tool process termination",
            "Implement tamper protection on endpoint security agents",
            "Centralize logging to prevent local log tampering",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1053",
        "name": "Scheduled Task/Job",
        "attack_types": ["malware"],
        "description": (
            "An attacker creates scheduled tasks or cron jobs to maintain persistence, "
            "execute payloads at specific times, or run malicious code after reboot."
        ),
        "remediation": [
            "Audit scheduled tasks for unauthorized entries",
            "Restrict task creation privileges to administrators",
            "Monitor task scheduler events (Event ID 4698)",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1055",
        "name": "Process Injection",
        "attack_types": ["malware"],
        "description": (
            "An attacker injects malicious code into a running legitimate process to "
            "evade AV detection and inherit the process's permissions and network access."
        ),
        "remediation": [
            "Enable memory integrity protections (HVCI)",
            "Monitor for cross-process memory operations",
            "Use EDR tools with process injection detection capabilities",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1048",
        "name": "Exfiltration Over Alternative Protocol",
        "attack_types": ["malware"],
        "description": (
            "An attacker exfiltrates stolen data over non-standard protocols like ICMP, "
            "DNS tunneling, or encrypted channels to bypass network monitoring."
        ),
        "remediation": [
            "Monitor for unusual outbound data volumes on non-standard protocols",
            "Implement DLP rules on egress traffic",
            "Restrict outbound connections to approved destinations only",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1486",
        "name": "Data Encrypted for Impact (Ransomware)",
        "attack_types": ["malware"],
        "description": (
            "Ransomware encrypts victim files and demands payment for the decryption key, "
            "often spreading laterally before activation to maximize damage."
        ),
        "remediation": [
            "Isolate the affected systems immediately to prevent spread",
            "Restore from offline backups (do not pay the ransom)",
            "Audit initial access vector and patch the entry point",
            "Reset all credentials in the affected domain",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1490",
        "name": "Inhibit System Recovery",
        "attack_types": ["malware"],
        "description": (
            "An attacker deletes volume shadow copies and backup data to prevent the "
            "victim from recovering without paying the ransom."
        ),
        "remediation": [
            "Ensure backups are stored offline and immutable",
            "Monitor for deletion of shadow copies (vssadmin delete shadows)",
            "Maintain off-site backup copies with tested restore procedures",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1566",
        "name": "Phishing",
        "attack_types": ["malware"],
        "description": (
            "An attacker sends crafted emails with malicious attachments or links to trick "
            "users into executing code, entering credentials on fake pages, or enabling macros."
        ),
        "remediation": [
            "Block the sender domain and quarantine the email",
            "Scan the user's endpoint for indicators of compromise",
            "Disable macro execution in Office documents by default",
            "Retrain the user and report to the email security team",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1098",
        "name": "Account Manipulation",
        "attack_types": ["brute_force"],
        "description": (
            "After gaining initial access, an attacker creates or modifies accounts "
            "(SSH keys, cloud IAM) to maintain persistence and elevate privileges."
        ),
        "remediation": [
            "Audit all user accounts for unauthorized additions or modifications",
            "Review SSH authorized_keys files on all servers",
            "Enable alerts on privilege escalation events in IAM/AD",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1133",
        "name": "External Remote Services",
        "attack_types": ["brute_force"],
        "description": (
            "An attacker exploits exposed remote access services (RDP, VPN, SSH) with "
            "stolen or brute-forced credentials to gain initial network access."
        ),
        "remediation": [
            "Enforce MFA on all external remote access services",
            "Restrict remote access to VPN-only and audit VPN logins",
            "Disable direct RDP/SSH from the internet",
        ],
        "severity_hint": "medium",
    },
    {
        "id": "T1003",
        "name": "OS Credential Dumping",
        "attack_types": ["malware"],
        "description": (
            "An attacker extracts password hashes or plaintext credentials from memory, "
            "registry hives, or SAM databases to escalate privileges and move laterally."
        ),
        "remediation": [
            "Enable Credential Guard on Windows hosts",
            "Detect LSASS access via Sysmon Event ID 10",
            "Reset all domain credentials after confirming credential theft",
        ],
        "severity_hint": "high",
    },
    {
        "id": "T1087",
        "name": "Account Discovery",
        "attack_types": ["port_scan", "brute_force"],
        "description": (
            "An attacker enumerates local and domain accounts to identify targets for "
            "privilege escalation and lateral movement."
        ),
        "remediation": [
            "Monitor for bulk account enumeration commands (net user, Get-ADUser)",
            "Restrict enumeration permissions to service accounts only",
            "Alert on accounts querying directory services outside normal patterns",
        ],
        "severity_hint": "low",
    },
]


def get_techniques_for_attack_type(attack_type: str) -> list[dict]:
    return [t for t in MITRE_TECHNIQUES if attack_type in t.get("attack_types", [])]
