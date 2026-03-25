THREAT_CLASS: Fileless Malware / Defense Evasion
SIGNATURES: powershell.exe, -nop, -w hidden, -enc, -EncodedCommand, ExecutionPolicy Bypass
DESCRIPTION: Adversaries use PowerShell with execution policy bypasses and hidden windows to execute malicious payloads directly in memory. The -enc flag is highly indicative of obfuscated malicious scripts, commonly used by C2 frameworks like Cobalt Strike to hide commands from traditional EDR solutions without dropping executables on the disk.
SEVERITY: CRITICAL
MITRE_ATTACK: T1059.001

THREAT_CLASS: Credential Access / SSH Brute Force
SIGNATURES: Event ID 4625, multiple failed logins, rapid authentication requests, port 22
DESCRIPTION: An attacker is attempting to guess passwords or use stolen credential lists against an SSH or RDP service. This is characterized by dozens or hundreds of failed login attempts from a single source IP within a short timeframe, potentially followed by a successful login (Event ID 4624) indicating compromise.
SEVERITY: HIGH
MITRE_ATTACK: T1110.001

THREAT_CLASS: Command and Control (C2) Beaconing
SIGNATURES: HTTP/HTTPS POST requests, high frequency low volume traffic, unexpected destination IPs, jittered timing
DESCRIPTION: A compromised internal host is "calling home" to an attacker-controlled server. This traffic often mimics standard web browsing but occurs at precise intervals (beaconing) to exfiltrate system data and receive subsequent commands. Usually relies on domain generation algorithms (DGA) or fast-flux DNS.
SEVERITY: CRITICAL
MITRE_ATTACK: T1071

THREAT_CLASS: Initial Access / SQL Injection (SQLi)
SIGNATURES: UNION SELECT, 1=1, xp_cmdshell, %27, OR 'a'='a', DROP TABLE, WAITFOR DELAY
DESCRIPTION: The attacker is injecting malicious SQL statements into entry fields for execution. This allows them to spoof identity, tamper with existing data, exfiltrate entire database tables, or even execute OS-level commands on the database server if xp_cmdshell is enabled.
SEVERITY: HIGH
MITRE_ATTACK: T1190

THREAT_CLASS: Impact / Ransomware Precursor
SIGNATURES: vssadmin.exe delete shadows /all /quiet, bcdedit /set {default} recoveryenabled No, wbadmin delete catalog
DESCRIPTION: Before executing file encryption routines, ransomware operators frequently execute administrative commands to delete Volume Shadow Copies and disable Windows automatic recovery modes. This ensures the victim cannot easily restore their system from local backups post-encryption.
SEVERITY: CRITICAL
MITRE_ATTACK: T1490

THREAT_CLASS: Privilege Escalation / Token Manipulation
SIGNATURES: whoami /priv, seclogon, MakeMeAdmin, unexpected child process from svchost.exe, SeDebugPrivilege
DESCRIPTION: The adversary has standard user access and is attempting to exploit system vulnerabilities to gain SYSTEM or Root level privileges. They run discovery commands to check current token privileges and attempt to duplicate tokens from higher-privileged processes.
SEVERITY: HIGH
MITRE_ATTACK: T1134

THREAT_CLASS: Lateral Movement / Pass the Hash (PtH)
SIGNATURES: psexec.exe, wmiexec.py, Event ID 4624 Logon Type 3, NTLM authentication, sekurlsa::pth
DESCRIPTION: After compromising one machine, the attacker extracts credential hashes from LSASS memory using tools like Mimikatz. They then pass these hashes to authenticate to other machines on the network via NTLM or SMB without ever needing to crack the plaintext password.
SEVERITY: CRITICAL
MITRE_ATTACK: T1550.002

THREAT_CLASS: Credential Access / Kerberoasting
SIGNATURES: Event ID 4769, Ticket Options 0x40810000, RC4 encryption (0x17), excessive TGS requests
DESCRIPTION: The attacker requests Kerberos Service Principal Name (SPN) tickets (TGS) from the Domain Controller for service accounts. Because these tickets are encrypted with the service account's password hash, the attacker exports them offline to crack the hash and hijack the service account.
SEVERITY: HIGH
MITRE_ATTACK: T1558.003

THREAT_CLASS: Credential Access / DCSync Attack
SIGNATURES: Event ID 4662, Directory Service Access, DS-Replication-Get-Changes, DS-Replication-Get-Changes-All
DESCRIPTION: An attacker with Domain Admin privileges uses the Directory Replication Service (DRS) Remote Protocol to simulate a Domain Controller. They request a replication of the Active Directory database, effectively dumping all user hashes, including the krbtgt account.
SEVERITY: CRITICAL
MITRE_ATTACK: T1003.006

THREAT_CLASS: Initial Access / Cross-Site Scripting (XSS)
SIGNATURES: <script>alert(1)</script>, onerror=, javascript:eval(), %3Cscript%3E
DESCRIPTION: An attacker injects malicious client-side scripts into web pages viewed by other users. This allows them to bypass access controls, hijack user sessions, steal session cookies, or redirect users to malicious domains.
SEVERITY: MEDIUM
MITRE_ATTACK: T1189

THREAT_CLASS: Exfiltration / DNS Tunneling
SIGNATURES: TXT record queries, abnormally long subdomains, base64 encoded subdomains, high volume of DNS requests
DESCRIPTION: An adversary is using the Domain Name System (DNS) protocol to bypass firewall restrictions and exfiltrate data. They encode stolen data into DNS queries (as long subdomains) sent to an attacker-controlled DNS server, which decodes the data and sends commands back via DNS TXT responses.
SEVERITY: HIGH
MITRE_ATTACK: T1048.003

THREAT_CLASS: Persistence / Scheduled Task Creation
SIGNATURES: schtasks.exe /create, Event ID 4698, AT.exe, unexpected XML files in C:\Windows\System32\Tasks

DESCRIPTION: To maintain access across system reboots, the attacker creates malicious scheduled tasks that execute their payload at a specific time or upon user logon. This is a primary method for establishing long-term persistence on compromised Windows endpoints.
SEVERITY: HIGH
MITRE_ATTACK: T1053.005

THREAT_CLASS: Credential Access / LSASS Memory Dumping
SIGNATURES: procdump.exe -ma lsass.exe, comsvcs.dll MiniDump, Event ID 4656 for lsass.exe, Outflank-Dumpert
DESCRIPTION: The Local Security Authority Subsystem Service (LSASS) stores active user credentials in memory. Attackers use Windows utilities or custom tools to create a memory dump of the LSASS process, transferring it offline to extract plaintext passwords and NTLM hashes.
SEVERITY: CRITICAL
MITRE_ATTACK: T1003.001

THREAT_CLASS: Defense Evasion / Indicator Removal
SIGNATURES: wevtutil cl System, wevtutil cl Security, Clear-EventLog, Event ID 1102 (The audit log was cleared)
DESCRIPTION: An attacker attempts to cover their tracks and blind the SOC by systematically deleting Windows Event Logs. The clearing of the Security log (Event ID 1102) is a massive red flag indicating an adversary is actively operating on the system and destroying forensic evidence.
SEVERITY: CRITICAL
MITRE_ATTACK: T1070.001

THREAT_CLASS: Execution / Living off the Land (LOLBins)
SIGNATURES: certutil.exe -urlcache -split -f, bitsadmin /transfer, regsvr32.exe /s /u /i:http
DESCRIPTION: The attacker is utilizing native, legitimate Windows binaries (LOLBins) to download malicious payloads or execute code. Because these tools (like certutil or bitsadmin) are trusted system utilities, they often bypass application whitelisting and antivirus detection.
SEVERITY: HIGH
MITRE_ATTACK: T1218

THREAT_CLASS: Persistence / Golden Ticket Attack
SIGNATURES: Event ID 4624 Logon Type 3 with generic usernames, 10-year ticket expiration, mismatched SID
DESCRIPTION: The attacker has compromised the KRBTGT account hash and forged a master Kerberos Ticket Granting Ticket (TGT). This "Golden Ticket" grants them unfettered, persistent administrative access to the entire Active Directory domain, even if passwords are changed.
SEVERITY: CRITICAL
MITRE_ATTACK: T1558.001

THREAT_CLASS: Lateral Movement / RDP Hijacking
SIGNATURES: tscon.exe, querying active RDP sessions, Event ID 4778, Event ID 4779
DESCRIPTION: An attacker with SYSTEM privileges takes over an active or disconnected Remote Desktop Protocol (RDP) session belonging to another user. Using the native tscon.exe utility, they connect to the session without needing the user's password, instantly assuming their identity.
SEVERITY: HIGH
MITRE_ATTACK: T1563.002

THREAT_CLASS: Lateral Movement / SMB Relay Attack
SIGNATURES: NTLMSSP, SMB signature disabled, Responder.py, unexpected lateral connections on port 445
DESCRIPTION: The attacker positions themselves on the network to intercept NTLM authentication traffic. Instead of cracking the hash, they immediately relay the intercepted authentication request to another server on the network (like a Domain Controller) to gain unauthorized access.
SEVERITY: HIGH
MITRE_ATTACK: T1557.001

THREAT_CLASS: Persistence / Web Shell Deployment
SIGNATURES: unexpected .jsp, .php, or .aspx files in webroot directory, commands executed by IIS/Apache worker processes
DESCRIPTION: Following the exploitation of a web application vulnerability, the attacker drops a malicious script (web shell) into the server's public web directory. This provides them with a persistent, web-based graphical or command-line interface to control the underlying web server.
SEVERITY: CRITICAL
MITRE_ATTACK: T1505.003

THREAT_CLASS: Credential Access / Cloud Metadata SSRF
SIGNATURES: curl https://www.google.com/search?q=http://169.254.169.254/latest/meta-data/, IAM role credentials extraction
DESCRIPTION: An attacker exploits a Server-Side Request Forgery (SSRF) vulnerability on a cloud-hosted web application to query the cloud provider's internal metadata API (169.254.169.254). This allows them to steal temporary IAM security credentials assigned to the EC2/Cloud instance.
SEVERITY: CRITICAL
MITRE_ATTACK: T1552.005