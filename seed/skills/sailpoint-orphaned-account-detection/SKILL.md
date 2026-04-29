---
name: sailpoint-orphaned-account-detection
description: Find application accounts in SailPoint that have no active identity correlation, indicating orphaned or rogue access
domain: cybersecurity
subdomain: identity-access-management
vendor: sailpoint
tags: [iam, iga, orphaned-accounts, lifecycle, audit, compliance]
mitre_attack: [T1078, T1078.003]
version: "1.0"
author: CyberSkills Hub
---

# SailPoint Orphaned Account Detection

## When to Use
Use during quarterly access reviews, application onboarding audits, or after offboarding events. Trigger when HR reports departures and you need to verify clean deprovisioning across all connected systems. Orphaned accounts — those existing in target systems with no linked identity in SailPoint — are a common persistence mechanism (MITRE T1078.003). Maps to NIST 800-53 AC-2, SOC 2 CC6.2.

## Prerequisites
- SailPoint IdentityNow (Org Admin) or IdentityIQ (System Admin)
- All target applications connected via SailPoint connectors (aggregation must be current)
- HR data source synced to SailPoint (Joiner/Mover/Leaver events flowing)

## Workflow

### Step 1: Run Account Aggregation Across All Sources
Ensure account data is current before analysis:
- IdentityNow: Admin → Connections → Sources → Aggregate all active sources
- IdentityIQ: Tasks → Run Account Aggregation for each application
- Verify last aggregation timestamp for each source — flag any source not aggregated within 24 hours as a data freshness risk

### Step 2: Pull Uncorrelated Accounts
In IdentityNow:
- Admin → Accounts → Filter: Uncorrelated = True
Export the full list.

In IdentityIQ:
- Reports → Account Activity → Uncorrelated Accounts report

These accounts exist in the target application but SailPoint cannot link them to an identity — they are either orphaned (user left) or unprocessed new accounts.

### Step 3: Classify Uncorrelated Accounts
For each uncorrelated account, determine the root cause:
1. **Orphaned — Departed Employee**: Cross-reference account name/email against HR termination records
2. **Orphaned — Rule Gap**: Account format doesn't match SailPoint correlation rule (e.g., username differs from email)
3. **Service Account — Not in Identity Cube**: Technical accounts intentionally excluded from HR identity model
4. **Provisioned Outside SailPoint**: Account created directly in the application, bypassing IGA

Flag types 1 and 4 as highest risk — these represent uncontrolled access.

### Step 4: Investigate High-Risk Orphaned Accounts
For each account classified as orphaned (departed employee):
1. Check last access/login timestamp in the target application
2. If last access was post-termination date: escalate immediately — potential insider threat or compromised credential
3. Disable account immediately pending investigation
4. Retrieve full activity log for the account for the period after termination

### Step 5: Remediate Correlation Gaps
For accounts with correlation rule gaps (type 2):
1. Document the attribute mismatch
2. Update the SailPoint correlation configuration to handle the variant
3. Re-run aggregation and verify accounts are now correlated

### Step 6: Build Orphan Prevention Controls
Recommend implementation of:
- **Terminate and Disable Task**: SailPoint lifecycle event that disables all accounts when identity status = Terminated
- **Nightly uncorrelated account alert**: Automated report emailed to IT security team
- **New source onboarding checklist**: Require correlation rule validation before connecting new applications

## Verification
- Any post-termination account access = Critical finding
- Uncorrelated account rate target: < 1% of total accounts across all sources
- NIST 800-53 AC-2(3): disable accounts after individual is no longer associated with the organization
- SailPoint reference: IdentityNow → Admin → Accounts documentation
