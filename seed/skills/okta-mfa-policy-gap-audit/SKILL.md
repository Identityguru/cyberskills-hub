---
name: okta-mfa-policy-gap-audit
description: Identify MFA coverage gaps across Okta user populations, app assignments, and sign-on policies
domain: cybersecurity
subdomain: identity-access-management
vendor: okta
tags: [iam, mfa, audit, compliance, nist, cis]
mitre_attack: [T1078, T1556.006]
version: "1.0"
author: CyberSkills Hub
---

# Okta MFA Policy Gap Audit

## When to Use
Use during compliance audits (SOC 2 CC6.1, NIST 800-53 IA-2, CIS Control 6.3), zero trust assessments, or after any identity-related security incident. Run quarterly at minimum. Trigger when new applications are onboarded, user populations change, or audit findings reference authentication control gaps.

## Prerequisites
- Okta Super Admin or Read Only Admin role
- Okta API access (`/api/v1/policies`, `/api/v1/apps`, `/api/v1/users`)
- List of all applications in scope (particularly those handling sensitive data or privileged access)
- Compliance framework mappings (NIST 800-63B AAL2/AAL3 requirements for your data classification)

## Workflow

### Step 1: Enumerate All Sign-On Policies
```
GET /api/v1/policies?type=OKTA_SIGN_ON
```
For each policy, retrieve the associated rules:
```
GET /api/v1/policies/{policyId}/rules
```
Document: which groups each policy applies to, whether MFA is required or optional, network zone conditions, and device trust conditions.

### Step 2: Map Policies to Applications
```
GET /api/v1/apps?limit=200
```
For each app, identify the applied sign-on policy and whether it enforces MFA. Flag any app without an explicitly MFA-enforcing policy.

**High-risk app classification for mandatory MFA:**
- Admin consoles and privileged access tools
- Finance and HR applications
- Cloud infrastructure consoles (AWS, Azure, GCP)
- Any app storing PII, PHI, or financial data

### Step 3: Identify MFA-Exempt User Populations
Check for group-based policy exclusions that bypass MFA:
- Service accounts assigned to human user policies
- Executive or VIP groups with softened MFA requirements
- Break-glass accounts without MFA enrollment

```
GET /api/v1/groups?filter=profile.name eq "MFA-Exempt"
```

### Step 4: Audit MFA Factor Enrollment
Pull MFA enrollment statistics:
```
GET /api/v1/users?filter=status eq "ACTIVE"
```
For sampled users, check enrolled factors:
```
GET /api/v1/users/{userId}/factors
```
Flag users with:
- No enrolled MFA factors
- Only SMS/voice OTP enrolled (phishable — does not meet NIST 800-63B AAL2)
- Okta Verify push only (vulnerable to MFA fatigue without number matching enabled)

### Step 5: Verify Number Matching and Additional Context
Per Okta's guidance (updated 2023), verify number matching is enabled for all Okta Verify push policies:
- Admin → Security → Authenticators → Okta Verify → Edit → Enable Number Challenge

### Step 6: Compile Gap Report
Produce a risk-rated gap list:
- **Critical**: Active users with no MFA on privileged apps
- **High**: Phishable factors (SMS/voice) as sole MFA for sensitive apps
- **Medium**: MFA optional (not required) on non-critical apps
- **Low**: Users enrolled in fewer than 2 factor types (no backup factor)

## Verification
Cross-reference your findings against:
- NIST SP 800-63B §4.2 (AAL2 requirements): hardware security keys or Okta Verify with number matching
- CIS Control 6.3: require MFA for all administrative access
- SOC 2 CC6.1: logical access controls with authentication verification
