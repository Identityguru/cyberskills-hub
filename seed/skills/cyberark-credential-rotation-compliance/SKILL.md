---
name: cyberark-credential-rotation-compliance
description: Verify CyberArk password rotation policy adherence across Safe families and identify stale or unmanaged privileged credentials
domain: cybersecurity
subdomain: identity-access-management
vendor: cyberark
tags: [pam, credential-management, password-rotation, compliance, nist]
mitre_attack: [T1552, T1555.003]
version: "1.0"
author: CyberSkills Hub
---

# CyberArk Credential Rotation Compliance

## When to Use
Use during compliance audits, quarterly PAM health checks, or after credential exposure incidents. Trigger when password rotation failures are detected in PVWA dashboards, when a CPM (Central Policy Manager) error is logged, or during annual penetration testing preparation. Maps to NIST 800-53 IA-5 (Authenticator Management), CIS Control 4.4.

## Prerequisites
- CyberArk PVWA Auditor or Vault Admin role
- CyberArk Central Policy Manager (CPM) deployed and operational
- Access to PVWA reports and account management views
- Platform policies defined per account type (domain admin, service account, local admin, etc.)

## Workflow

### Step 1: Pull Password Rotation Compliance Report
PVWA → Reports → Accounts:
- Filter: CPM Status = "Failed to change" or "Will not change soon" or "Change required"
- Export: account name, Safe, platform, last changed date, CPM status, next change date

This is your baseline non-compliance list.

### Step 2: Classify Non-Compliant Accounts by Risk Tier
- **Tier 0 (Critical)**: Domain Admins, Enterprise Admins, local Administrator on Tier 0 servers (DCs, PKI, ADFS)
- **Tier 1 (High)**: Server local admins, database DBA accounts, cloud root/break-glass accounts
- **Tier 2 (Medium)**: Service accounts, application accounts, workstation local admins
- **Tier 3 (Low)**: Personal admin accounts, test environment accounts

Rotation requirements by tier (recommended):
- Tier 0: ≤ 30 days, immediate rotation on suspected compromise
- Tier 1: ≤ 60 days
- Tier 2: ≤ 90 days or on credential exposure
- Tier 3: ≤ 180 days

### Step 3: Investigate CPM Failures
For accounts with CPM rotation failure, diagnose the root cause:
- **Connection failure**: Target system unreachable (network/firewall change) — escalate to infra team
- **Authentication failure**: Current password is incorrect (manual password change outside CyberArk) — reconcile immediately
- **Policy violation**: Account locked after rotation attempt — coordinate with AD team
- **Platform mismatch**: Wrong CyberArk platform assigned to account type — reassign platform

Unresolved CPM failures = credentials not rotating = compliance gap.

### Step 4: Identify Accounts Outside CPM Management
Pull accounts where CPM management is disabled:
- PVWA → Accounts → filter CPM Status = "Inactive" or check accounts with "Require password change" unchecked
- These accounts exist in the Vault for storage only — no rotation is occurring

For each inactive CPM account:
1. Determine why CPM management was disabled (documented exception?)
2. Verify if the account still exists in the target system
3. If active and no exception documented: re-enable CPM management

### Step 5: Verify Reconcile Account Configuration
Reconcile accounts allow CyberArk to fix accounts where the password has drifted:
- PVWA → Platforms → select each platform → verify Reconcile Account is configured
- Test reconcile: manually trigger reconcile on a non-critical account to verify it works

### Step 6: Review Service Account Rotation Handling
Service accounts with embedded credentials (hardcoded in app configs) are the most common CPM failure source:
- For each service account in Vault with CPM failures: verify whether application code uses CyberArk API (AIM/CP) to fetch credentials dynamically
- If credentials are hardcoded: this is a critical finding — application needs to be updated to use CyberArk SDK

### Step 7: Findings
- **Critical**: Tier 0 account not rotated in > 30 days with no exception
- **Critical**: Service account with hardcoded credential (not using CyberArk AIM)
- **High**: Tier 1 account password > 90 days old
- **High**: CPM failure with unknown root cause on privileged account
- **Medium**: CPM management disabled without documented exception
- **Low**: Rotation interval configured but > recommended for tier

## Verification
- NIST 800-53 IA-5(1): enforce minimum and maximum lifetime restrictions on authenticators
- CIS Control 4.4: use unique passwords for all privileged accounts
- CyberArk CPM documentation: docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/CPM-Landing.htm
