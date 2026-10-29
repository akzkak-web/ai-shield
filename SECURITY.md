# Security Policy

## Scope

AI Shield is a local security baseline scanner for AI inference services. It
performs read-only checks and produces evidence-backed findings.

Scan results have important limits:

- A rule match is not proof that a vulnerability is exploitable.
- A grade of `A` with `partial` or `none` coverage is not a proof of safety.
- `unknown` and `error` results indicate that a condition could not be
  verified, not that a service is secure.

## Reporting a security issue in AI Shield

Please report vulnerabilities in AI Shield itself, not findings discovered in
third-party services that AI Shield scanned. Issues found in a scanned target
should be reported to that target's operator through their own disclosure
process.

The project does not currently publish a dedicated security email address,
bug bounty program, or response-time SLA.

If the GitHub repository has private vulnerability reporting enabled, use the
Security tab to submit a private advisory. If private reporting is not
enabled, contact the maintainers through the repository's available
discussion or issue mechanism, but do not include live credentials,
production data, or unrelated target details.

Do not post unredacted exploit details, credentials, or private data in public
issues.

## Preferences

When reporting, include:

- affected version or commit;
- steps to reproduce;
- expected and actual behavior;
- relevant configuration, with secrets removed;
- impact assessment.

Preference is given to reports that are reproducible and contain a minimal
test case.
