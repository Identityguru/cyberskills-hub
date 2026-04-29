---
name: sailpoint-sod-violation-detection
description: Detect and remediate Segregation of Duties policy conflicts in SailPoint IGA
domain: cybersecurity
subdomain: identity-access-management
vendor: sailpoint
tags: [iam, iga, sod, segregation-of-duties, audit, sox, compliance]
mitre_attack: [T1078]
version: "1.0"
author: CyberSkills Hub
---

# SailPoint Segregation of Duties Violation Detection

## When to Use
Use during SOX ITGC reviews, audit preparations, quarterly SoD policy reviews, or when new applications/entitlements are onboarded. Trigger immediately when a new SoD conflict is reported by SailPoint policy engine or when a user receives an entitlement that could create a conflict. Maps to SOC 2 CC6.3, SOX ITGC, and ISO 27001 A.6.1.2.

## Prerequisites
- SailPoint IdentityNow (Org Admin) or IdentityIQ (System Admin)
- SoD policy definitions configured in SailPoint
- Business process owner contacts for remediation approval
- Access to the target applications (SAP, Oracle EBS, Workday, etc.) for access verification

## Workflow

### Step 1: Pull Current SoD Policy Violations
In SailPoint IdentityNow:
- Governance → Policy Violations → Active Violations
- Filter by policy type: SoD

In SailPoint IdentityIQ:
- Compliance → Policy Violations → filter Type = SOD

Export the full violation list including: identity, conflicting entitlements, policy name, business process, violation date, and assigned remediation owner.

### Step 2: Classify Violations by Severity
Apply this classification:
- **Critical**: Conflicts in financial approval chains (e.g., create purchase order + approve purchase order in SAP)
- **Critical**: Access to both transaction initiation and approval in the same system
- **High**: Ability to create/modify user accounts AND grant access in the same system
- **High**: Read access to sensitive data + ability to export/transfer that data
- **Medium**: Conflicts in systems not subject to financial regulation but handling PII
- **Low**: Legacy policy violations with documented compensating controls

### Step 3: Validate Active vs. Stale Violations
Not all SoD violations are active risks:
1. Check identity's last login and last use of each conflicting entitlement
2. If the identity is inactive or the entitlement has not been used in 90+ days, classify as lower priority but still require remediation
3. Check whether any compensating controls (audit logging, periodic review) are documented

### Step 4: Review Mitigation Requests
Check for open mitigation/exception requests:
- IdentityNow: Governance → Mitigations
- Each mitigation should have: business justification, approver, expiration date, compensating control description

Flag mitigations that are:
- Expired (no renewal action taken)
- Approved without a compensating control
- Approved by the same person who holds the conflicting access

### Step 5: Remediation Workflow
For each unmitigated Critical/High violation:
1. Identify the least-privileged entitlement to remove (consult business process owner)
2. Raise a provisioning ticket to remove the conflicting entitlement
3. Assign violation to an identity owner in SailPoint for acknowledgment
4. Set remediation SLA: Critical = 48h, High = 5 business days, Medium = 30 days

### Step 6: Validate Policy Completeness
Check that SoD policies cover all critical business processes:
- Financial: AP, AR, Payroll, GL, Fixed Assets
- HR: Hire/terminate AND access provisioning
- IT: Change management AND production access
- Procurement: Requisition AND approval

Gaps in policy coverage = undetected violations.

## Verification
- SOX ITGC: SoD controls are a primary ITGC requirement for financial system access
- SOC 2 CC6.3: system access restricted based on job responsibilities
- ISO 27001 A.6.1.2: conflicting duties and areas of responsibility shall be segregated
- Each violation report must include policy name, conflicting entitlement pair, and remediation action
