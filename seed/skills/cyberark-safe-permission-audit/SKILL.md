---
name: cyberark-safe-permission-audit
description: Review CyberArk Safe member permissions for least-privilege gaps and over-privileged access assignments
domain: cybersecurity
subdomain: identity-access-management
vendor: cyberark
tags: [pam, safe-permissions, least-privilege, audit, access-control]
mitre_attack: [T1078, T1552]
version: "1.0"
author: CyberSkills Hub
---

# CyberArk Safe Permission Audit

## When to Use
Use during quarterly PAM access reviews, before/after personnel changes in the PAM admin team, or as part of the broader CyberArk vault security audit. Trigger when a new Safe is created, when a team member leaves the PAM team, or during annual compliance audits. Maps to NIST 800-53 AC-3, CIS Control 5.1.

## Prerequisites
- CyberArk PVWA Vault Admin or Safe Manager role
- Ability to run PrivateArk Client or use PVWA Safe management views
- List of all Safes and their designated owners/business owners
- CyberArk REST API access for bulk permission analysis (recommended for large environments)

## Workflow

### Step 1: Export Safe Membership List
Use CyberArk REST API to export all Safe members and their permissions:
```
GET /PasswordVault/API/Safes/{safeName}/Members
```
For bulk environments, iterate across all Safes:
```
GET /PasswordVault/API/Safes?limit=100
```
Export columns: Safe name, member name, member type (user/group/role), and all permission flags.

### Step 2: Map Permissions to Risk Level
CyberArk Safe permissions by risk:
| Permission | Risk Level | Notes |
|---|---|---|
| Manage Safe Members | Critical | Can grant any permission to any user |
| Manage Safe | High | Change Safe properties, rename, delete |
| Retrieve Accounts | High | View full credentials in cleartext |
| List Accounts | Medium | See account names (reconnaissance risk) |
| Use Accounts | Medium | Connect via PSM (no credential view) |
| Add/Update/Delete Accounts | High | Modify credential store |
| Backup Safe | Medium | Service accounts only |
| View Audit Log | Low | Read-only, audit-safe |

### Step 3: Identify Principle of Least Privilege Violations
For each Safe, flag:
- **End users with Retrieve Accounts**: Do they need to see the password itself, or just use it via PSM? Most should use PSM (Use Accounts) not Retrieve (view password)
- **End users with Manage Safe or Manage Safe Members**: Should be restricted to PAM administrators only
- **Shared accounts with multiple Retrieve Accounts members**: Each retrieve is a potential credential exposure — prefer individual accounts or PSM-only access
- **Groups with excessive permissions**: A group granting Retrieve + Manage to a broad population = high blast radius

### Step 4: Review Owner Accountability
Every Safe should have a designated business owner:
- Verify each Safe has an owner listed (PVWA → Safes → Description field or custom attribute)
- For Safes with no documented owner: flag and assign to PAM admin team for ownership assignment
- Verify the Safe owner is an active employee (cross-reference HR data)

### Step 5: Audit Service Account and Integration Permissions
Service accounts used by applications (PVWA, CPM components, CyberArk AIM) should have minimal permissions:
- AIM/CP service accounts: need List Accounts + Retrieve Accounts only
- CPM accounts: need Add/Update/Delete Accounts + Retrieve for rotation
- PSM accounts: need Use Accounts only

Flag any service account with Manage Safe permissions (unnecessary and dangerous).

### Step 6: Review Inherited Permissions via Groups
Pull group memberships for all groups with Safe access:
- PrivateArk Client → Tools → Administrative Tools → Users and Groups → [group] → Members
- Verify group members are current and appropriate
- Flag groups with stale members (departed employees still in the group)

### Step 7: Findings
- **Critical**: Non-admin user with Manage Safe Members permission (can self-escalate)
- **Critical**: Stale/orphaned group member with Retrieve Accounts on Tier 0 Safes
- **High**: End user with Retrieve Accounts where PSM (Use Accounts) would suffice
- **High**: Service account with Manage Safe permission
- **Medium**: Safe with no documented business owner
- **Low**: Retrieve Accounts assigned to > 5 individual users on the same Safe (use PSM instead)

## Verification
- CyberArk Safe Permissions reference: docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/Safes-AddingMembers.htm
- NIST 800-53 AC-3: the system enforces approved authorizations for logical access
- CIS Control 5.1: establish and maintain an inventory of all accounts
