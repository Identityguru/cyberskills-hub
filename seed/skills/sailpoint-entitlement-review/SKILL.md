---
name: sailpoint-entitlement-review
description: Identify access creep and over-entitlement across identities using SailPoint entitlement data and peer group analytics
domain: cybersecurity
subdomain: identity-access-management
vendor: sailpoint
tags: [iam, iga, access-creep, entitlement, least-privilege, audit]
mitre_attack: [T1078, T1068]
version: "1.0"
author: CyberSkills Hub
---

# SailPoint Entitlement Review

## When to Use
Use during access reviews, least-privilege initiatives, or post-incident investigations where excessive access may have been exploited. Trigger when a user changes roles (Mover event) or when entitlement counts for a population deviate significantly from peer benchmarks. Maps to NIST 800-53 AC-6 (Least Privilege), CIS Control 5.4.

## Prerequisites
- SailPoint IdentityNow (Org Admin) or IdentityIQ (System Admin)
- Entitlement catalog current and enriched with descriptions and risk classifications
- Identity attributes reflecting current job function and department (fed from HR)
- Peer group definitions configured (by department, job title, or manager)

## Workflow

### Step 1: Pull Entitlement Distribution by Identity
Export each identity's entitlement count across all connected applications:
- IdentityNow: Reports → Identity Reports → Entitlements by Identity
- IdentityIQ: Reports → Entitlement Owner Report

Sort descending by entitlement count. Identify outliers: users with significantly more entitlements than the median for their job title/department.

### Step 2: Identify Access Creep from Mover Events
Access creep occurs when access accumulates across role changes. Query for identities that have had role changes in the past 12 months:
```
GET /beta/search (IdentityNow) — filter: attributes.jobTitle history
```
For each Mover, verify:
- Entitlements from the previous role were revoked upon role change
- Current entitlements match the new role profile
- No entitlements exist from 2+ previous roles

### Step 3: Compare Against Peer Group Benchmarks
Use SailPoint's Access Insights or Role Mining:
- IdentityNow: AI Services → Access Insights → Outlier Analysis
- Identify identities flagged as "outliers" — users with access significantly beyond their peer group

For each outlier:
1. List entitlements not held by any peer in the same job title/department
2. Request business justification for each outlier entitlement
3. Flag entitlements with no justification for revocation

### Step 4: Review High-Risk Entitlement Holdings
Pull all identities holding entitlements classified as high-risk:
- Admin/privileged roles in any connected application
- Entitlements granting export or bulk data access
- Finance system approval rights

For each: verify current job function requires this access. Any non-privileged user holding privileged entitlements = immediate review.

### Step 5: Validate Entitlement Descriptions and Risk Classifications
Unclassified entitlements cannot be properly reviewed:
- Pull entitlements with no description or risk classification
- Assign application owners to enrich missing metadata
- Flag any application where > 20% of entitlements are unclassified as a data quality risk

### Step 6: Produce Remediation List
- **Critical**: Non-admin user with admin entitlement and no justification
- **High**: User holding entitlements from 2+ prior roles (access creep > 1 role change)
- **High**: Outlier entitlements that are sensitive data access with no peer holding the same
- **Medium**: Outlier entitlements in non-sensitive systems
- **Low**: Entitlement count > 2x peer median (review required, not automatic revocation)

## Verification
- NIST 800-53 AC-6: employ the principle of least privilege
- CIS Control 5.4: restrict administrator privileges to dedicated administrator accounts
- SailPoint IdentityNow AI Services documentation: help.identitynow.com/hc/en-us
