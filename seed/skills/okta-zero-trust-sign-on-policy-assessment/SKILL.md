---
name: okta-zero-trust-sign-on-policy-assessment
description: Evaluate Okta sign-on policies and device trust configuration against NIST SP 800-207 Zero Trust Architecture pillars
domain: cybersecurity
subdomain: identity-access-management
vendor: okta
tags: [zero-trust, iam, policy-review, nist, zta, device-trust]
mitre_attack: [T1078, T1550]
version: "1.0"
author: CyberSkills Hub
---

# Okta Zero Trust Sign-On Policy Assessment

## When to Use
Use during Zero Trust Architecture (ZTA) migrations, security architecture reviews, or compliance assessments requiring NIST SP 800-207 alignment. Run when onboarding new high-value applications, when Device Trust configuration changes, or as part of quarterly security posture reviews.

## Prerequisites
- Okta Super Admin or Security Admin role
- Okta Device Trust or Okta FastPass configured (for device posture checks)
- Network zone definitions in Okta Admin
- Understanding of current application risk classification
- NIST SP 800-207 reference (available at nvlpubs.nist.gov)

## Workflow

### Step 1: Map Current Sign-On Policies to ZTA Pillars
NIST SP 800-207 defines access decisions based on: identity, device health, network context, and resource sensitivity. For each sign-on policy, document:
- **Identity signals**: MFA required? Factor strength? Risk-based auth enabled?
- **Device signals**: Device Trust enforced? Managed device required? Okta FastPass in use?
- **Network signals**: IP/network zone restrictions? Trusted network bypass (and whether it's appropriate)?
- **Resource sensitivity**: What applications does this policy protect?

### Step 2: Evaluate Identity Assurance Level
Per NIST 800-63B:
- **AAL1**: Single factor — acceptable only for low-sensitivity, public-facing resources
- **AAL2**: MFA with approved authenticators — required for sensitive business apps
- **AAL3**: Hardware-bound phishing-resistant MFA — required for privileged/admin access

Flag any app classified as medium or high sensitivity that accepts AAL1.

### Step 3: Assess Device Trust Configuration
Check Okta Device Trust policies:
- Admin → Security → Device Trust
- Verify managed device requirements are applied to all high-sensitivity apps
- Check that Okta FastPass is deployed and enforced where applicable
- Flag any policy that trusts network location as a substitute for device trust (network zone ≠ zero trust)

### Step 4: Evaluate Adaptive/Risk-Based Policies
Check Okta Identity Engine (OIE) policy rules for risk-based conditions:
- Behavior detection enabled? (Admin → Security → Behavior Detection)
- Risk scoring thresholds configured and appropriate?
- High-risk sign-in behavior triggers step-up authentication (not just logging)?

### Step 5: Identify Implicit Trust Gaps
Common ZTA anti-patterns to flag:
- **Trusted network bypass**: Policy allows no MFA if on corporate network — violates ZTA "never trust, always verify"
- **Persistent sessions > 8 hours**: Long sessions reduce re-verification frequency; flag sessions > 8h on sensitive apps
- **Missing continuous evaluation**: No re-authentication triggered on behavior change mid-session
- **App-level vs org-level MFA**: If MFA is set at app level only, new apps may launch without MFA by default

### Step 6: Score Against NIST 800-207 Tenets
Rate each tenet (1=Not Met, 2=Partial, 3=Met):
1. All data sources treated as resources — score based on app coverage
2. All communication secured regardless of network location — TLS + no network bypass
3. Access per-session, not per-network — no persistent trusted-network bypass
4. Access determined by dynamic policy — risk-based auth configured
5. All assets monitored — Okta log streaming to SIEM operational
6. Authentication and authorization are dynamic and strictly enforced — adaptive policies active
7. Collect information to improve security posture — ThreatInsight + behavior detection active

## Verification
- Reference: NIST SP 800-207 (August 2020), §3 Zero Trust Architecture Tenets
- Reference: Okta Zero Trust documentation — help.okta.com/en-us/content/topics/security/zero-trust.htm
- Each gap finding must include the specific policy name, the ZTA tenet violated, and a remediation step
