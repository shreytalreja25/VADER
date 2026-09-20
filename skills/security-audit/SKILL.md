---
name: security-audit
description: Scans repository for leaked credentials, unsafe dependencies, and OWASP vulnerabilities
version: 1.0.0
tags: [security, audit, owasp, guardrails]
---

# Security Audit Skill

When this skill is activated:
1. Scan for hardcoded secrets, private keys, JWT secrets, and API tokens.
2. Inspect for SQL injection, unsanitized subprocess shell executions, and path traversal risks.
3. Review `.gitignore` and ensure environment files (`.env*`) are safely excluded.
4. Generate a remediation report and suggest safe replacements.
