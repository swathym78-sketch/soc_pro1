SOC Strategic Security Playbook

Credential Dumping (Mimikatz, LSASS Abuse)

Threat Context: Attackers attempt to extract plaintext passwords, hashes, and Kerberos tickets from memory (LSASS) to move laterally.
Mitigation Strategy:

Enable Windows Defender Credential Guard to isolate LSASS.

Enable LSA Protection (RunAsPPL) via Registry.

Restrict 'Debug Programs' privilege (SeDebugPrivilege) to strictly necessary administrative groups.

Deploy EDR rules to immediately kill processes attempting to hook into lsass.exe.

PowerShell & Command-Line Abuse

Threat Context: Fileless malware and encoded commands (-enc, ExecutionPolicy Bypass) are used to execute malicious payloads in memory.
Mitigation Strategy:

Enforce PowerShell Constrained Language Mode (CLM) across the domain.

Enable Script Block Logging (Event ID 4104) and Module Logging.

Audit and restrict the use of WMIC and PowerShell for standard users.

Alert on encoded command execution patterns and base64 strings in command-line arguments.

WMI Remote Execution & Lateral Movement

Threat Context: Windows Management Instrumentation (WMI) is abused via process call create to execute code on remote systems without dropping files.
Mitigation Strategy:

Restrict remote WMI access (DCOM/RPC) to dedicated administrative IP subnets using Windows Firewall.

Monitor for Win32_ProcessStartTrace events initiated by non-standard parent processes.

Implement network segmentation to prevent workstation-to-workstation WMI communication.

Reverse Shells & Network Exfiltration

Threat Context: Attackers use tools like Netcat (nc -e) or pure PowerShell TCP clients to establish outbound connections to C2 servers.
Mitigation Strategy:

Implement strict egress filtering on perimeter firewalls (block all outbound ports by default, allow only 80/443 via proxies).

Inspect TLS traffic using SSL decryption to identify hidden C2 beacons.

Deploy Application Control (AppLocker/WDAC) to prevent unauthorized executables like netcat from running.

Privilege Escalation & Rogue Accounts

Threat Context: Attackers create rogue backup accounts or add themselves to local administrator groups to maintain persistence.
Mitigation Strategy:

Implement Local Administrator Password Solution (LAPS) to randomize local admin passwords.

Continuously monitor and alert on Event IDs 4720 (Account Created) and 4732 (Member Added to Security-Enabled Local Group).

Enforce the Principle of Least Privilege (PoLP) and use Just-In-Time (JIT) administrative access.

Vulnerable Web Servers & Path Traversal

Threat Context: External-facing web servers (Apache, Nginx) targeted via CVEs for remote code execution or unauthorized directory access.
Mitigation Strategy:

Deploy a Web Application Firewall (WAF) to filter malicious URI patterns and path traversal attempts (../).

Isolate web servers in a hardened DMZ with no direct access to the internal active directory.

Implement an aggressive 24-48 hour patch management SLA for internet-facing infrastructure.