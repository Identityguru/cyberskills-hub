---
name: okta-suspicious-auth-detection
description: Detect impossible travel, brute force, and credential stuffing attacks in Okta authentication logs
domain: cybersecurity
subdomain: identity-access-management
vendor: okta
tags: [iam, detection, authentication, threat-detection, zero-trust]
mitre_attack: [T1078, T1110, T1110.003]
version: "1.0"
author: CyberSkills Hub
---

# Okta Suspicious Authentication Detection

## When to Use
Use this skill when investigating authentication anomalies, responding to Okta ThreatInsight alerts, conducting identity threat hunting, or reviewing user sign-in activity for indicators of compromise. Trigger on: repeated failed logins, impossible travel alerts, spike in MFA push denials, or SIEM correlation rules firing on Okta System Log events.

## Prerequisites
- Okta admin access (Read Only Admin or Super Admin)
- Okta System Log API access (`/api/v1/logs`)
- Okta ThreatInsight enabled (Admin → Security → General)
- SIEM integration (optional but recommended: Splunk, Sentinel, or Okta Log Streaming)
- Baseline of normal user geolocation and device patterns

## Workflow

### Step 1: Pull Recent Authentication Events
Query Okta System Log API for authentication events over the investigation window (default: 24 hours):
```
GET /api/v1/logs?filter=eventType eq "user.session.start"&since=<ISO8601>&until=<ISO8601>
```
Filter for failed events:
```
GET /api/v1/logs?filter=eventType eq "user.authentication.auth_via_mfa" and outcome.result eq "FAILURE"
```

### Step 2: Identify Brute Force Patterns
Flag users with ≥5 failed authentication attempts within a 10-minute window from the same IP. Indicators:
- Rapid sequential failures across multiple accounts from one IP (password spraying — T1110.003)
- Single account with high failure velocity (brute force — T1110)
- Failures followed immediately by success (credential stuffing — T1078)

### Step 3: Detect Impossible Travel
For each authenticated session, compare:
- `client.geographicalContext.city` and `country` across consecutive sessions
- Calculate minimum travel time between two geolocations
- Flag if time between sessions is less than physically possible travel time

### Step 4: Review MFA Push Fatigue Indicators
Query for repeated MFA push denials:
```
eventType eq "user.mfa.okta_verify.deny_push"
```
Flag users with ≥3 MFA denials in 15 minutes — potential MFA fatigue attack (T1078.004).

### Step 5: Correlate with ThreatInsight
Check Okta ThreatInsight for IP reputation data:
- Admin → Reports → ThreatInsight
- Flag sessions from IPs classified as `UNKNOWN` or `BLOCKED`

### Step 6: Triage and Escalate
For each flagged user:
1. Check if the activity is from a registered device (Okta Device Trust)
2. Review the user's recent access patterns in the Okta admin console
3. If confirmed suspicious: suspend user, terminate all sessions, initiate credential reset
4. Document findings using the template in `/assets/template.md`

## Verification
- Confirmed brute force: 5+ sequential failures from same IP within 10 minutes
- Confirmed impossible travel: consecutive sessions from geographically impossible locations within ≤2 hours
- Confirmed credential stuffing: low per-account failure count but broad user population targeted from single IP
- All findings rated per risk matrix in `/references/standards.md`
