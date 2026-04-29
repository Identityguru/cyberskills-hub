---
name: sailpoint-access-certification-review
description: Guide SailPoint access certification campaigns, detect anomalies in reviewer decisions, and ensure certification quality
domain: cybersecurity
subdomain: identity-access-management
vendor: sailpoint
tags: [iam, iga, access-certification, audit, iso27001, sox]
mitre_attack: [T1078]
version: "1.0"
author: CyberSkills Hub
---

# SailPoint Access Certification Review

## When to Use
Use when running, monitoring, or auditing SailPoint IdentityNow/IdentityIQ access certification campaigns. Trigger on: campaign completion, audit preparation, post-campaign quality review, or when reviewer response rates are abnormally low. Maps to ISO 27001 A.9.2.5 (Review of user access rights) and SOX ITGC controls.

## Prerequisites
- SailPoint IdentityNow: Cert Admin or Org Admin role
- SailPoint IdentityIQ: System Admin or Certification Admin role
- Access to certification reports and decision audit logs
- List of targeted campaigns and their scope definitions

## Workflow

### Step 1: Pre-Campaign Scope Validation
Before a campaign completes, verify:
- Campaign scope is correctly defined: targeted identities, entitlements, and applications
- Reviewer assignments are accurate (manager-based vs. application owner-based)
- Fallback reviewers are configured for out-of-office managers
- Campaign deadline is realistic (minimum 5 business days recommended)

In IdentityNow:
- Certification Setup → Campaign Details → confirm Included Identities filter
- Verify exclusion rules are not inadvertently excluding high-risk populations

### Step 2: Monitor Reviewer Response Rate
During the campaign, track:
- Completion percentage by reviewer group
- Decision breakdown: Approve vs. Revoke vs. Allow Exception
- Reviewers with 0% completion approaching deadline

Flag reviewers who approve >95% of items without any revocations — potential rubber-stamping pattern.

### Step 3: Identify Anomalous Decision Patterns
Post-campaign, pull the certification decision audit log:
- IdentityNow: Reports → Certification Reports → Decisions by Reviewer
- IdentityIQ: Debug → Certification → Review Decision History

**Rubber-stamping indicators:**
- Reviewer certified 100% approvals across all items with no revocations
- Certifications completed in < 2 minutes for > 50 items
- Bulk approve used without individual item review

**Under-revocation indicators:**
- No reviewer in a campaign revoked any entitlement — statistically unlikely for large populations
- Application owners consistently approve their own team's access to sensitive data

### Step 4: Validate High-Risk Entitlement Decisions
For sensitive entitlements (admin roles, privileged access, financial system access):
1. Pull all "Approved" decisions for high-risk entitlements
2. Verify each approval has a business justification note
3. Cross-reference against SoD policies — any approved combination that violates SoD is a critical finding

### Step 5: Review Revocation Follow-Through
A certification that generates revocations is only valuable if those revocations are executed:
- Check remediation task completion rate in the certification report
- Flag any revocation decisions that are in "Pending Remediation" status > 30 days
- Verify provisioning connector completed the access removal in the target system

### Step 6: Certify the Certifiers
Check certifier eligibility:
- Are reviewers reviewing their own access? (should be excluded)
- Are certifiers in the population being certified? (conflict of interest)
- Do certifiers have active employment status?

## Verification
- ISO 27001 A.9.2.5: access rights reviewed at regular intervals
- SOC 2 CC6.3: established procedures to remove access after personnel changes
- Each rubber-stamping finding should include: reviewer name, items certified, time taken, revocation rate vs. population average
