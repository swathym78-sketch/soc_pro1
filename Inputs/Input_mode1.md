**1.NON-MALICIOUS (AI Mistake: Flags as SUSPICIOUS)** 

**{**

  **"timestamp": "2026-03-08T11:20:00Z",**

  **"source\_ip": "10.0.2.15",**

  **"user": "net\_admin\_greg",**

  **"host": "WKSTN-092",**

  **"command": "wmic /node:192.168.1.50 process call create \\"cmd.exe /c ipconfig /all > C:\\\\temp\\\\net\_info.txt\\""**

**}**

**Feedback to Paste: "Authorized Network Administrator performing remote troubleshooting. The WMIC command is being used to pull IP configuration data from a workstation reporting network connectivity issues."**



**2.NON-MALICIOUS (AI Mistake: Flags as HIGH RISK)**

**{**

  **"timestamp": "2026-03-09T03:00:00Z",**

  **"source\_ip": "10.0.5.20",**

  **"user": "dba\_service",**

  **"host": "SQL-PROD-01",**

  **"command": "powershell.exe -ExecutionPolicy Bypass -Command \\"Compress-Archive -Path 'D:\\\\DB\_Data\\\\\*' -DestinationPath 'Z:\\\\Secure\_Archive\\\\DB\_Backup.zip'\\""**

**}**



**Feedback to Paste: "Authorized Database service account executing the nightly automated SQL database compression and backup to the secure network storage share."**



**3.🔴 TRUE MALICIOUS: Persistence (Rogue Account Creation)**

**{**

  **"timestamp": "2026-03-10T18:45:22Z",**

  **"source\_ip": "172.16.10.88",**

  **"user": "apache\_svc",**

  **"host": "WEB-SRV-02",**

  **"command": "cmd.exe /c net user backup\_admin P@ssw0rd123! /add \&\& net localgroup administrators backup\_admin /add"**

**}**

 **7.TRUE MALICIOUS: DCSync Attack (Credential Theft)**

**{**

  **"timestamp": "2026-03-11T01:12:05Z",**

  **"source\_ip": "10.0.0.5",**

  **"user": "temp\_admin\_01",**

  **"host": "DC-02",**

  **"command": "mimikatz.exe \\"lsadump::dcsync /domain:corp.local /all\\" exit"**

**}**



