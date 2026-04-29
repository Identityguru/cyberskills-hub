"""
Seed script: creates admin user and populates all 15 pre-built skills.
Run from the project root: python seed/seed.py
"""
import io
import os
import sys
import zipfile
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import SessionLocal, engine
from app.models import Base, User, Skill
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

SKILLS_SOURCE_DIR = Path(__file__).parent / "skills"
SKILLS_DATA_DIR = Path(settings.skills_data_dir)

SKILL_META = [
    # Okta
    {
        "slug": "okta-suspicious-auth-detection",
        "name": "Okta Suspicious Authentication Detection",
        "description": "Detect impossible travel, brute force, and credential stuffing attacks in Okta authentication logs",
        "category": "Identity & Access Management",
        "vendor": "okta",
        "tags": ["iam", "detection", "authentication", "threat-detection", "zero-trust"],
        "mitre_attack_ids": ["T1078", "T1110", "T1110.003"],
    },
    {
        "slug": "okta-mfa-policy-gap-audit",
        "name": "Okta MFA Policy Gap Audit",
        "description": "Identify MFA coverage gaps across Okta user populations, app assignments, and sign-on policies",
        "category": "Identity & Access Management",
        "vendor": "okta",
        "tags": ["iam", "mfa", "audit", "compliance", "nist", "cis"],
        "mitre_attack_ids": ["T1078", "T1556.006"],
    },
    {
        "slug": "okta-privileged-access-review",
        "name": "Okta Privileged Access Review",
        "description": "Audit Okta super admin accounts, org-level admin roles, and service account privilege assignments",
        "category": "Identity & Access Management",
        "vendor": "okta",
        "tags": ["iam", "privileged-access", "admin-review", "least-privilege", "audit"],
        "mitre_attack_ids": ["T1078.004", "T1098"],
    },
    {
        "slug": "okta-zero-trust-sign-on-policy-assessment",
        "name": "Okta Zero Trust Sign-On Policy Assessment",
        "description": "Evaluate Okta sign-on policies and device trust configuration against NIST SP 800-207 Zero Trust Architecture pillars",
        "category": "Identity & Access Management",
        "vendor": "okta",
        "tags": ["zero-trust", "iam", "policy-review", "nist", "zta", "device-trust"],
        "mitre_attack_ids": ["T1078", "T1550"],
    },
    {
        "slug": "okta-lifecycle-management-audit",
        "name": "Okta Lifecycle Management Audit",
        "description": "Audit Okta for orphaned accounts, inactive users, and Joiner-Mover-Leaver process gaps",
        "category": "Identity & Access Management",
        "vendor": "okta",
        "tags": ["iam", "lifecycle", "jml", "orphaned-accounts", "audit", "compliance"],
        "mitre_attack_ids": ["T1078", "T1078.003"],
    },
    # SailPoint
    {
        "slug": "sailpoint-access-certification-review",
        "name": "SailPoint Access Certification Review",
        "description": "Guide SailPoint access certification campaigns, detect anomalies in reviewer decisions, and ensure certification quality",
        "category": "Identity & Access Management",
        "vendor": "sailpoint",
        "tags": ["iam", "iga", "access-certification", "audit", "iso27001", "sox"],
        "mitre_attack_ids": ["T1078"],
    },
    {
        "slug": "sailpoint-sod-violation-detection",
        "name": "SailPoint SoD Violation Detection",
        "description": "Detect and remediate Segregation of Duties policy conflicts in SailPoint IGA",
        "category": "Identity & Access Management",
        "vendor": "sailpoint",
        "tags": ["iam", "iga", "sod", "segregation-of-duties", "audit", "sox", "compliance"],
        "mitre_attack_ids": ["T1078"],
    },
    {
        "slug": "sailpoint-orphaned-account-detection",
        "name": "SailPoint Orphaned Account Detection",
        "description": "Find application accounts in SailPoint with no active identity correlation, indicating orphaned or rogue access",
        "category": "Identity & Access Management",
        "vendor": "sailpoint",
        "tags": ["iam", "iga", "orphaned-accounts", "lifecycle", "audit", "compliance"],
        "mitre_attack_ids": ["T1078", "T1078.003"],
    },
    {
        "slug": "sailpoint-entitlement-review",
        "name": "SailPoint Entitlement Review",
        "description": "Identify access creep and over-entitlement across identities using SailPoint entitlement data and peer group analytics",
        "category": "Identity & Access Management",
        "vendor": "sailpoint",
        "tags": ["iam", "iga", "access-creep", "entitlement", "least-privilege", "audit"],
        "mitre_attack_ids": ["T1078", "T1068"],
    },
    {
        "slug": "sailpoint-role-mining-analysis",
        "name": "SailPoint Role Mining Analysis",
        "description": "Use SailPoint role mining to identify role consolidation opportunities and validate birthright role assignments",
        "category": "Identity & Access Management",
        "vendor": "sailpoint",
        "tags": ["iam", "iga", "role-mining", "rbac", "role-engineering", "lifecycle"],
        "mitre_attack_ids": ["T1078"],
    },
    # CyberArk
    {
        "slug": "cyberark-vault-security-audit",
        "name": "CyberArk Vault Security Audit",
        "description": "Review CyberArk Vault hardening, Safe permissions, and component security configuration",
        "category": "Identity & Access Management",
        "vendor": "cyberark",
        "tags": ["pam", "privileged-access", "vault", "hardening", "audit", "nist"],
        "mitre_attack_ids": ["T1552", "T1555", "T1078.003"],
    },
    {
        "slug": "cyberark-privileged-session-monitoring-review",
        "name": "CyberArk Privileged Session Monitoring Review",
        "description": "Analyze CyberArk PSM session recordings for anomalous command patterns and suspicious privileged activity",
        "category": "Identity & Access Management",
        "vendor": "cyberark",
        "tags": ["pam", "psm", "session-monitoring", "threat-detection", "insider-threat"],
        "mitre_attack_ids": ["T1078.003", "T1059", "T1070", "T1136"],
    },
    {
        "slug": "cyberark-credential-rotation-compliance",
        "name": "CyberArk Credential Rotation Compliance",
        "description": "Verify CyberArk password rotation policy adherence across Safe families and identify stale or unmanaged privileged credentials",
        "category": "Identity & Access Management",
        "vendor": "cyberark",
        "tags": ["pam", "credential-management", "password-rotation", "compliance", "nist"],
        "mitre_attack_ids": ["T1552", "T1555.003"],
    },
    {
        "slug": "cyberark-jit-access-review",
        "name": "CyberArk JIT Access Review",
        "description": "Assess CyberArk Just-in-Time access patterns, approval workflow compliance, and standing privilege reduction",
        "category": "Identity & Access Management",
        "vendor": "cyberark",
        "tags": ["pam", "jit", "zero-trust", "just-in-time", "approval-workflow", "least-privilege"],
        "mitre_attack_ids": ["T1078.003", "T1098"],
    },
    {
        "slug": "cyberark-safe-permission-audit",
        "name": "CyberArk Safe Permission Audit",
        "description": "Review CyberArk Safe member permissions for least-privilege gaps and over-privileged access assignments",
        "category": "Identity & Access Management",
        "vendor": "cyberark",
        "tags": ["pam", "safe-permissions", "least-privilege", "audit", "access-control"],
        "mitre_attack_ids": ["T1078", "T1552"],
    },
]


def create_skill_zip(slug: str, vendor: str, readme_content: str) -> Path:
    vendor_dir = SKILLS_DATA_DIR / vendor
    vendor_dir.mkdir(parents=True, exist_ok=True)
    zip_path = vendor_dir / f"{slug}.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{slug}/SKILL.md", readme_content)
        zf.writestr(f"{slug}/references/standards.md", f"# Standards Reference\n\nSee SKILL.md for MITRE ATT&CK and NIST citations specific to {slug}.\n")
        zf.writestr(f"{slug}/assets/template.md", f"# {slug} — Findings Template\n\n## Executive Summary\n\n## Risk-Rated Findings\n\n| Finding | Risk | Recommendation | Reference |\n|---|---|---|---|\n\n## Remediation Actions\n\n## Evidence Collected\n")
    zip_path.write_bytes(buf.getvalue())
    return zip_path


def seed():
    db = SessionLocal()

    # Create admin user
    admin = db.query(User).filter(User.email == settings.admin_email).first()
    if not admin:
        admin = User(
            email=settings.admin_email,
            username=settings.admin_username,
            hashed_password=hash_password(settings.admin_password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Created admin: {settings.admin_email}")
    else:
        print(f"Admin already exists: {settings.admin_email}")

    # Seed skills
    created = 0
    for meta in SKILL_META:
        if db.query(Skill).filter(Skill.slug == meta["slug"]).first():
            print(f"  skip (exists): {meta['slug']}")
            continue

        skill_md_path = SKILLS_SOURCE_DIR / meta["slug"] / "SKILL.md"
        if not skill_md_path.exists():
            print(f"  MISSING: {skill_md_path}")
            continue

        readme = skill_md_path.read_text()
        zip_path = create_skill_zip(meta["slug"], meta["vendor"], readme)

        skill = Skill(
            slug=meta["slug"],
            name=meta["name"],
            description=meta["description"],
            category=meta["category"],
            vendor=meta["vendor"],
            version="1.0",
            author_id=admin.id,
            status="approved",
            file_path=str(zip_path),
            readme_content=readme,
            download_count=0,
        )
        skill.tags = meta["tags"]
        skill.mitre_attack_ids = meta["mitre_attack_ids"]
        db.add(skill)
        db.commit()
        created += 1
        print(f"  seeded: {meta['slug']}")

    print(f"\nDone. {created} skills seeded.")
    db.close()


if __name__ == "__main__":
    seed()
