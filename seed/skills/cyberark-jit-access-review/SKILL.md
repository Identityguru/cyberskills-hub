---
name: cyberark-jit-access-review
description: Assess CyberArk Just-in-Time access patterns, approval workflow compliance, and standing privilege reduction
domain: cybersecurity
subdomain: identity-access-management
vendor: cyberark
tags: [pam, jit, zero-trust, just-in-time, approval-workflow, least-privilege]
mitre_attack: [T1078.003, T1098]
version: "1.0"
author: CyberSkills Hub
---

# CyberArk Just-in-Time Access Review

## When to Use
Use during Zero Trust Architecture assessments, PAM maturity reviews, or compliance audits requiring evidence of minimal standing privilege. Trigger when implementing CyberArk's Vendor PAM (VPAM) or when migrating from standing privileged access to JIT. Maps to NIST SP 800-207 §3.3 (resource access is granted on a per-session basis), NIST 800-53 AC-6(9).

## Prerequisites
- CyberArk PVWA configured with Dual Control (access approval workflow) on critical Safes
- CyberArk Vendor PAM (for external/vendor JIT) if applicable
- CyberArk Dynamic Privileged Access (DPA) configured if using cloud JIT
- ITSM integration (ServiceNow, Jira) for ticket-based access validation

## Workflow

### Step 1: Inventory Current JIT vs. Standing Access Configuration
Determine which accounts use JIT (time-limited access) vs. standing (always available):
- PVWA → Policies → Safes → check each Safe for Dual Control settings
- Standing access = account available 24/7 without approval
- JIT = requires approval workflow before access is granted

Map current state:
- % of critical Safes with Dual Control enabled
- % of privileged sessions requiring a valid ITSM ticket reference

Target: Tier 0 and Tier 1 accounts should require dual control (JIT approval). No standing access to domain admin credentials.

### Step 2: Review Approval Workflow Configuration
For Safes with Dual Control enabled:
- PVWA → Policies → Access Control → select Safe → Dual Control settings
- Verify: minimum approvers required (recommend ≥ 1 for normal, ≥ 2 for Tier 0)
- Verify: approvers are not the same user as the requester (system should enforce this)
- Verify: approval time window is defined (time from approval to session start, e.g., 30 minutes)
- Verify: ITSM ticket validation is enforced (not just a free-text reason field)

### Step 3: Analyze Approval Pattern Quality
Pull approval history for the past 90 days:
- PVWA → Reports → Account Activity → filter for Dual Control requests
- Measure:
  - Average approval time (< 2 minutes consistently = rubber-stamp approvals)
  - Approval rejection rate (0% rejections = policy not enforced in practice)
  - After-hours approvals without on-call ticket reference

Flag: approvers who have never rejected a request — likely rubber-stamping.

### Step 4: Review Vendor/Third-Party JIT Access
If CyberArk Vendor PAM is deployed:
- PVAM console → check vendor invitations currently active
- Verify each active vendor session: vendor is currently engaged, not a dormant invitation
- Review vendor session recordings for compliance (no data exfiltration indicators)
- Verify vendors cannot create persistent accounts in the environment

Flag: vendor invitations active > 30 days without session activity.

### Step 5: Assess Cloud JIT (CyberArk DPA)
If CyberArk Dynamic Privileged Access is deployed for cloud:
- DPA console → review ephemeral account provisioning logs
- Verify ephemeral accounts are deprovisioned at session end (no residual cloud IAM users)
- Check: JIT access policies enforce MFA at the cloud provider level before issuing ephemeral credentials

### Step 6: Identify Standing Privilege Reduction Opportunities
Pull accounts currently with standing access (no dual control) on Tier 0/1 Safes:
- These are candidates for JIT migration
- For each: assess feasibility of enabling dual control (does the account support timeout-based use?)
- Produce a phased JIT migration roadmap: quick wins (low-use accounts) first

### Step 7: Findings
- **Critical**: Domain admin Safe without dual control (standing access to highest-privilege credentials)
- **Critical**: Active vendor JIT invitation with no recent session activity (>30 days idle)
- **High**: Approval workflow where requester = approver (technical control gap)
- **High**: Tier 0 accounts accessible without ITSM ticket validation
- **Medium**: Consistent rubber-stamp approvals (< 2 min, 0% rejection rate)
- **Low**: JIT access window too long (> 4 hours for routine maintenance tasks)

## Verification
- NIST SP 800-207 §3.3: all resource access is granted on a per-session basis
- NIST 800-53 AC-6(9): log use of privileged functions
- CyberArk Dual Control documentation: docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/Dual-Control.htm
