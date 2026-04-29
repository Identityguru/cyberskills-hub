---
name: sailpoint-role-mining-analysis
description: Use SailPoint role mining to identify role consolidation opportunities and validate birthright role assignments
domain: cybersecurity
subdomain: identity-access-management
vendor: sailpoint
tags: [iam, iga, role-mining, rbac, role-engineering, lifecycle]
mitre_attack: [T1078]
version: "1.0"
author: CyberSkills Hub
---

# SailPoint Role Mining Analysis

## When to Use
Use when establishing or maturing a Role-Based Access Control (RBAC) program, reducing manual entitlement assignments, or during IGA platform implementations. Trigger when entitlement assignment volume is high (>70% direct assignments vs. role-based), when access review quality is poor (too many items per reviewer), or as part of a Zero Trust least-privilege initiative.

## Prerequisites
- SailPoint IdentityNow (AI Services enabled, Org Admin) or IdentityIQ (Role Manager enabled)
- Identity attributes synchronized from HR (department, job title, location, cost center)
- At least 6 months of access data for meaningful pattern analysis
- Business process owners available for role validation

## Workflow

### Step 1: Assess Current State of Role Coverage
Determine the ratio of role-based vs. direct entitlement assignments:
- IdentityNow: Reports → Role Reports → Role Membership Summary
- Calculate: (Entitlements via roles) / (Total entitlement assignments) × 100
- Target benchmark: ≥ 70% role-based assignments

If coverage is < 50%, proceed directly to role mining before any other IGA initiative.

### Step 2: Run Role Mining
In IdentityNow:
- AI Services → Role Insights → Run Role Mining
- Configure mining parameters: minimum population threshold (e.g., ≥ 5 identities sharing same entitlement set), attribute groupings (by department + job title)

In IdentityIQ:
- Role Modeler → Role Mining → Configure and run

Review the suggested role candidates output.

### Step 3: Validate Suggested Roles
For each mined role candidate:
1. Review the entitlement composition — does it make business sense for the identified population?
2. Identify the business owner (typically department manager or application owner)
3. Verify no SoD conflicts exist within the proposed role entitlement set
4. Confirm the entitlement set represents a minimum viable access profile (not maximum observed access)

### Step 4: Identify Birthright Role Gaps
Birthright roles are access that should be granted automatically at hire:
- All employees: corporate email, intranet, HRIS self-service, VPN (if applicable)
- By department: department-specific applications and shared drives
- By job title: role-specific tools (e.g., all engineers get GitHub access)

Query for new hires in the last 6 months and check whether they received birthright access via roles or via manual ticket:
- High manual provisioning rate = missing birthright role definitions

### Step 5: Design Role Hierarchy
Organize approved roles into a hierarchy:
- **Organizational roles**: Applied automatically by HR attribute (department, location)
- **Business roles**: Represent a job function, composed of IT roles
- **IT roles**: Technical entitlement bundles for a specific application or system
- **Entitlements**: Lowest level — individual permissions

### Step 6: Measure Role Mining ROI
After implementing mined roles, track:
- Reduction in direct entitlement assignments
- Reduction in access review items per reviewer (role-level certifications are faster)
- Reduction in provisioning ticket volume
- Improvement in time-to-access for new hires

## Verification
- SailPoint Role Modeling documentation: documentation.sailpoint.com
- NIST 800-53 AC-2(7): role-based access control schemes
- Mined roles must be validated by a business process owner before activation — never activate purely on algorithmic suggestion
