---
name: cyberark-privileged-session-monitoring-review
description: Analyze CyberArk PSM session recordings for anomalous command patterns and suspicious privileged activity
domain: cybersecurity
subdomain: identity-access-management
vendor: cyberark
tags: [pam, psm, session-monitoring, threat-detection, insider-threat]
mitre_attack: [T1078.003, T1059, T1070, T1136]
version: "1.0"
author: CyberSkills Hub
---

# CyberArk Privileged Session Monitoring Review

## When to Use
Use during incident response involving privileged accounts, routine threat hunting in PAM activity, or compliance audits requiring evidence of privileged session oversight. Trigger on SIEM alerts for suspicious privileged activity, insider threat investigations, or post-incident forensics. Maps to NIST 800-53 AU-12 (Audit Record Generation), SI-4 (System Monitoring), and MITRE T1078.003.

## Prerequisites
- CyberArk PVWA Auditor role (minimum for session review)
- CyberArk Privileged Session Manager (PSM) deployed and recording sessions
- CyberArk Privileged Threat Analytics (PTA) enabled (if available — adds anomaly detection layer)
- SIEM with CyberArk syslog integration (for automated alert correlation)

## Workflow

### Step 1: Identify Sessions for Review
Pull sessions from PVWA → Monitoring → Live Sessions / Session Recordings:
- Filter by: time window (investigation period), target account (e.g., domain admin, root), target system, or requesting user
- Prioritize review for: sessions initiated outside business hours, sessions on critical infrastructure (DCs, production DBs, cloud consoles), sessions by recently-terminated or suspicious users

### Step 2: Review Session Metadata Before Playback
Before reviewing recordings, check session metadata for initial triage:
- Session duration (unusually short sessions may indicate automated access; unusually long sessions may indicate data exfiltration)
- Commands recorded (keystroke log available in PSM for supported connection components)
- Reason provided at checkout (if dual control or reason-code policy is active)
- Ticket ID linked (if CyberArk is integrated with ITSM — verify ticket is legitimate)

### Step 3: Analyze Command Patterns for Anomalies
In Windows RDP sessions, review keystrokes for:
- Reconnaissance commands: `net user`, `net group "Domain Admins"`, `whoami /priv`, `ipconfig /all`, `arp -a` — normal individually, suspicious in sequence
- Lateral movement indicators: `PsExec`, `wmic /node:`, `Invoke-Command`, new scheduled tasks (`schtasks /create`)
- Persistence mechanisms: new local accounts (`net user /add`), registry run key modifications
- Data staging/exfiltration: bulk file copy, `xcopy` to network shares, archive creation (`7z`, `zip`)

In Unix/Linux SSH sessions, review for:
- Privilege escalation: `sudo -l`, `su root`, SUID exploitation
- Persistence: `crontab -e`, SSH key additions (`~/.ssh/authorized_keys`)
- Data access: `find / -name "*.conf"`, bulk `/etc/passwd` or `/etc/shadow` reads

### Step 4: Correlate with PTA Alerts
If CyberArk PTA is deployed:
- PVWA → Monitoring → Suspected Threat Activity
- PTA machine learning flags anomalies: first-time access to systems, unusual command sequences, access at abnormal times
- Correlate PTA alerts with session recordings for the flagged sessions

### Step 5: Review Dual Control Compliance
For Safes with dual control (approval workflow) configured:
- Verify all sessions were preceded by an approved access request
- Check for any sessions where approval was granted by the same user as the requester (conflict — should be flagged in PTA)
- Verify approver identity was authenticated at approval time

### Step 6: Document Findings
- **Critical**: Session containing data exfiltration indicators (bulk copy, archive, transfer to external)
- **Critical**: Session accessing a system not covered by an active change ticket
- **Critical**: Persistence mechanism created in session (new user, scheduled task, SSH key)
- **High**: Reconnaissance command sequence (network discovery > credential access > lateral movement)
- **High**: Session outside business hours on critical system without documented on-call ticket
- **Medium**: Unusually short session on critical system (possible automation not going through PAM)
- **Low**: Dual control approval time < 60 seconds (rubber-stamp approval)

## Verification
- NIST 800-53 AU-12: generate audit records for defined events
- NIST 800-53 SI-4: monitor the system to detect attacks and indicators of potential attacks
- CyberArk PSM documentation: docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/PSM-Sessions-Landing.htm
