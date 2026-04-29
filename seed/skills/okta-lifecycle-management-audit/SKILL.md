---
name: okta-lifecycle-management-audit
description: Audit Okta for orphaned accounts, inactive users, and Joiner-Mover-Leaver process gaps
domain: cybersecurity
subdomain: identity-access-management
vendor: okta
tags: [iam, lifecycle, jml, orphaned-accounts, audit, compliance]
mitre_attack: [T1078, T1078.003]
version: "1.0"
author: CyberSkills Hub
---

# Okta Lifecycle Management Audit

## When to Use
Run during quarterly access reviews, post-offboarding audits, or compliance assessments covering NIST 800-53 AC-2 (Account Management), SOC 2 CC6.2, or ISO 27001 A.9.2.6. Trigger immediately after any report of unauthorized access via a former employee account.

## Prerequisites
- Okta Super Admin or Read Only Admin role
- HR system integration data (Workday, BambooHR, or equivalent) or CSV export of active employees
- Okta API access for System Log queries
- Deprovisioning policy documentation for your organization

## Workflow

### Step 1: Identify Inactive Active Accounts
Pull all ACTIVE status users and filter by last login:
```
GET /api/v1/users?filter=status eq "ACTIVE"&limit=200
```
Flag users where `lastLogin` is:
- **> 90 days**: Dormant account — high risk if still holds permissions
- **null (never logged in)**: Provisioned but never used — verify if intentional

### Step 2: Cross-Reference Against HR Data
Compare Okta ACTIVE user list against current HR employee records:
- Users in Okta ACTIVE status but not in HR active employee list = potential orphaned accounts
- Users in HR active list but not in Okta = provisioning gap (different risk — new hire without access)
- Special attention to contractors and service accounts (often not in HR system — need separate owner registry)

### Step 3: Audit DEPROVISIONED and SUSPENDED Accounts
```
GET /api/v1/users?filter=status eq "DEPROVISIONED"
GET /api/v1/users?filter=status eq "SUSPENDED"
```
Verify:
- All deprovisioned accounts have corresponding HR termination records
- Time from termination date to Okta deprovisioning is within SLA (policy target: ≤ same business day)
- No deprovisioned user has active sessions (check System Log for post-deprovisioning activity)

### Step 4: Review Group Memberships for Leavers
Check that deprovisioned users were removed from all groups before deprovisioning:
```
GET /api/v1/users/{userId}/groups
```
Any deprovisioned user retaining group membership = provisioning automation failure.

### Step 5: Audit Movers (Role Changes)
Query System Log for recent role changes:
```
GET /api/v1/logs?filter=eventType eq "group.user_membership.add" or eventType eq "group.user_membership.remove"&since=<90_days_ago>
```
For users who changed departments or roles, verify:
- Old access from previous role was removed (no accumulation/access creep)
- New access appropriate to current role was granted
- Change is traceable to an ITSM ticket or HR event

### Step 6: Review Service Account Lifecycle
Service accounts are frequently overlooked in JML processes:
```
GET /api/v1/users?filter=profile.userType eq "service"
```
Or search by naming convention (e.g., `svc-`, `api-`). For each:
- Verify an active human owner is registered
- Confirm last token/credential use date is within expected range
- Flag service accounts with no recorded owner as orphaned

### Step 7: Findings Summary
- **Critical**: Active accounts for confirmed terminated employees
- **Critical**: Accounts active post-deprovisioning date with session activity
- **High**: Dormant accounts > 90 days with privileged group membership
- **High**: Service accounts with no documented owner
- **Medium**: Deprovisioning SLA breaches (> same business day for terminations)
- **Low**: Never-logged-in accounts > 30 days old (provisioning accuracy issue)

## Verification
- NIST 800-53 AC-2(3): disable accounts after a defined inactivity period
- SOC 2 CC6.2: prior to issuing system credentials and granting access, registered users are authorized
- ISO 27001 A.9.2.6: remove or adjust access rights on change/termination
