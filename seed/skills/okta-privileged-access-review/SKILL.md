---
name: okta-privileged-access-review
description: Audit Okta super admin accounts, org-level admin roles, and service account privilege assignments
domain: cybersecurity
subdomain: identity-access-management
vendor: okta
tags: [iam, privileged-access, admin-review, least-privilege, audit]
mitre_attack: [T1078.004, T1098]
version: "1.0"
author: CyberSkills Hub
---

# Okta Privileged Access Review

## When to Use
Use during quarterly access reviews, privileged access audits, SOC 2 or ISO 27001 audit preparations, or after personnel changes in IT/security teams. Trigger immediately after any suspected account compromise or unauthorized admin activity. Maps to NIST 800-53 AC-6 (Least Privilege) and AC-2 (Account Management).

## Prerequisites
- Okta Super Admin role (required to view all admin roles)
- Okta API token with admin scope
- Current RACI or ownership list for IT/security team roles
- HR termination and role-change notifications for the review period

## Workflow

### Step 1: Enumerate All Administrator Accounts
```
GET /api/v1/users?filter=profile.login eq "admin"  
```
Retrieve all users with admin role assignments:
```
GET /api/v1/iam/roles/assignments?resource-type=USER
```
Pull the full admin role list including custom roles:
```
GET /api/v1/iam/roles
```

### Step 2: Classify by Privilege Level
Map each admin to their role:
- **Super Admin**: Full org-level control — highest risk, must be minimized
- **Org Admin**: Broad access excluding some billing/super admin functions
- **App Admin**: Scoped to specific application(s)
- **Group Admin**: Scoped to group management
- **Read Only Admin**: Audit-safe, no change capability
- **Custom Roles**: Review each permission set individually

Flag all Super Admins — per NIST 800-53 AC-6(5), privileged accounts should be separate from standard user accounts.

### Step 3: Validate Business Justification
For every Super Admin and Org Admin:
1. Confirm active employment via HR directory
2. Verify a documented business justification exists
3. Check if the role is still appropriate given current job function
4. Flag any service accounts assigned human admin roles

### Step 4: Review Admin Account Hygiene
For each admin account, verify:
- MFA is enrolled and uses phishing-resistant factor (hardware key or Okta Verify with number matching)
- Admin activity uses a dedicated admin account (not the daily-use account)
- No inactive admin accounts (last login > 60 days)
- API tokens assigned to the account are inventoried and rotated per policy

### Step 5: Check for Privilege Creep
Compare current admin assignments against the last review:
```
GET /api/v1/logs?filter=eventType eq "user.account.privilege.grant"&since=<last_review_date>
```
Flag any admin role grants that lack corresponding ITSM change tickets.

### Step 6: Review Group-Based Admin Delegations
Check for groups that grant delegated admin rights:
```
GET /api/v1/groups?filter=type eq "OKTA_GROUP"
```
Review group memberships for admin-granting groups. Verify no stale members.

### Step 7: Produce Findings
- **Critical**: Super Admin assigned to shared/service accounts
- **Critical**: Super Admin accounts without phishing-resistant MFA
- **High**: Inactive admin accounts (> 60 days no login)
- **High**: Admin role assignments without documented justification
- **Medium**: Single admin account for both daily use and privileged tasks
- **Low**: Admin counts exceeding documented threshold (recommend ≤5 Super Admins for enterprise)

## Verification
All findings map to:
- NIST 800-53 AC-6 (Least Privilege), AC-2 (Account Management), IA-2(1) (MFA for privileged accounts)
- CIS Control 5.4: restrict administrator privileges to dedicated administrator accounts
- Okta documentation: [Administrators](https://help.okta.com/en-us/content/topics/security/administrators-admin-comparison.htm)
