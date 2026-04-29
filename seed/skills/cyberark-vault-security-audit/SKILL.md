---
name: cyberark-vault-security-audit
description: Review CyberArk Vault hardening, Safe permissions, and component security configuration
domain: cybersecurity
subdomain: identity-access-management
vendor: cyberark
tags: [pam, privileged-access, vault, hardening, audit, nist]
mitre_attack: [T1552, T1555, T1078.003]
version: "1.0"
author: CyberSkills Hub
---

# CyberArk Vault Security Audit

## When to Use
Use during PAM security assessments, annual security audits, post-incident reviews involving privileged credentials, or as part of a Zero Trust privileged access review. Run after any CyberArk version upgrade or infrastructure change. Maps to NIST 800-53 AC-3 (Access Enforcement), IA-5 (Authenticator Management), and CIS Control 4.

## Prerequisites
- CyberArk PVWA Auditor or Vault Administrator role
- CyberArk PrivateArk Client access (for detailed Vault configuration review)
- Network access to the Vault server for configuration verification
- CyberArk Vault hardening guide for your version (available on CyberArk docs portal)

## Workflow

### Step 1: Vault Server Hardening Baseline
Verify the Vault server meets CyberArk's hardening requirements:
- OS: Only approved OS (Windows Server, CyberArk-provided Appliance)
- No additional software installed on Vault server beyond CyberArk components
- Vault server not domain-joined (CyberArk recommendation for highest security)
- Firewall allows only CyberArk required ports (1858 for Vault, 443 for PVWA)
- Remote Desktop/SSH to Vault only via PAM session (no direct admin access)

Reference: CyberArk Vault Installation Guide — docs.cyberark.com

### Step 2: Vault Administrator Account Review
Pull all Vault-level administrator accounts:
- PrivateArk Client → Tools → Administrative Tools → Users and Groups
- Review Vault Built-in Users: Administrator, Auditor, Backup, Batch, DR, Gateway, Master, Notification Engine, Support
- Verify: Master account is used only for emergency recovery, password rotated and stored offline
- Verify: Default Administrator account password has been changed from default

Flag any non-service accounts with Vault Administrator role.

### Step 3: Safe Permission Audit
For each Safe in the Vault, review permissions:
- PVWA → Policies → Safes → select Safe → Members
- Key permissions to audit:
  - **List Accounts**: Should only be granted to users who need to know accounts exist
  - **Retrieve Accounts**: Grants password view — highest privilege, must be justified
  - **Use Accounts**: PSM connectivity — grants access to target via session
  - **Manage Safe**: Administrative rights — should be restricted to PAM admins
  - **Backup Safe**: Service accounts only

Flag any end users with Retrieve Accounts + Manage Safe on the same Safe (over-privileged).

### Step 4: Review CyberArk Component Security
Verify component-to-Vault communication uses certificates (not passwords):
- PVWA, CPM, PSM, PSMP should all authenticate via client certificates
- Check: PVWA → Administration → System Health → verify component status and certificate expiry
- Flag any components with certificate expiry within 90 days

### Step 5: Master Policy Review
PVWA → Policies → Master Policy:
- Verify password change frequency meets your policy (recommended: 30–90 days for privileged accounts)
- Verify one-time passwords are enabled for highly privileged accounts
- Verify dual control (approval workflow) is configured for critical Safes
- Check that password complexity requirements match or exceed your organization's baseline

### Step 6: Audit Log Integrity
Verify audit log configuration:
- PVWA → Administration → System Configuration → Vault Details → Audit Settings
- Logs should be forwarded to SIEM (Splunk, Sentinel, etc.) in real time
- Vault syslog forwarding configured and operational
- Log retention meets compliance requirements (minimum 1 year for SOX/PCI)

### Step 7: Findings Summary
- **Critical**: Master account password not stored offline or used for daily operations
- **Critical**: Component certificate expired or communication using password-based auth
- **High**: End users with Retrieve Accounts on Safes containing domain admin/root credentials
- **High**: Vault server is domain-joined
- **Medium**: Password rotation intervals exceed 90 days for tier-0 accounts
- **Low**: Dual control not configured for Safes containing critical infrastructure credentials

## Verification
- CyberArk documentation: docs.cyberark.com/Product-Doc/OnlineHelp/PAS
- NIST 800-53 AC-3, IA-5, AU-9 (Protection of Audit Information)
- CIS Control 4: Controlled use of administrative privileges
