# Security Policy

This document describes the actual security practices for this project. It is scoped
honestly to what this application is: a single-user, local-only personal finance tool built
and used by one person (Jack Kaplan) on his own computer. It intentionally does not describe
enterprise controls (SSO, RBAC, centralized IAM, zero trust architecture, etc.) that don't
apply to a project with exactly one user and no employees - claiming those would be
inaccurate, not just unnecessary.

## Information Security Policy

- **Scope**: this application has exactly one user and runs entirely on that user's own
  personal computer. There is no multi-tenant infrastructure, no other users, and no
  employees.
- **Physical/OS access control**: access to the application and its data requires access to
  the user's computer, which is protected by a Windows account login and full-disk
  encryption (Windows Device Encryption/BitLocker).
- **Secrets management**: all API keys and credentials (Anthropic API key, Plaid client
  ID/secret, email app password) are stored in a local `.env` file, which is excluded from
  version control via `.gitignore` and never committed to the project's git history or
  transmitted anywhere except directly to the respective service.
- **Network exposure**: the application binds to `localhost` only by default. It is not
  exposed to the public internet or any network beyond the user's own machine unless the
  user explicitly reconfigures it to be.
- **Data in transit**: all outbound calls to third-party APIs (Plaid, Anthropic) use
  HTTPS/TLS 1.2+, enforced by those providers - this isn't optional configuration, Plaid and
  Anthropic's own servers require it.
- **Data at rest**: application data (accounts, transactions, budgets, chat history) is
  stored in a local SQLite file, protected by OS-level full-disk encryption.
- **Vulnerability management**: dependencies are periodically checked with `pip-audit` (see
  below). Identified vulnerabilities are patched within 7 days of detection by updating the
  affected package.
- **Access review**: as the sole user, the user periodically reviews account activity/active
  sessions on connected third-party services (Google, Plaid) to confirm no unauthorized
  access.

## Access Control Policy

- Only Jack Kaplan has access to this application, its source code, and the data it stores.
- Access requires access to the user's personal computer, protected by a Windows account
  login and full-disk encryption.
- The application has no internal user accounts, roles, or permission tiers, because it is
  designed for exactly one user - there is nothing to segment access between.
- Third-party service credentials are stored only in the local, git-ignored `.env` file and
  are never shared with any other party.

## Data Deletion & Retention Policy

- **Retention**: financial data is retained locally for as long as the user chooses to keep
  using the application. There is no fixed retention period because there is no other party
  with a stake in the data.
- **Deletion**: the user can delete all stored data at any time by deleting the local
  `finbot.db` file.
- **Revocation**: the user can revoke the application's access to any linked bank account at
  any time directly from Plaid's own dashboard, which immediately stops further data
  collection.
- No data is accessible to anyone other than the user. Data only ever leaves the user's
  computer for the direct, necessary API calls to Plaid (bank sync) and Anthropic (chat
  assistant) required to serve those specific features.

## Vulnerability Scanning

Dependencies are checked with [`pip-audit`](https://pypi.org/project/pip-audit/), which
compares installed packages against known vulnerability databases.

To run a scan:
```bash
pip install pip-audit
pip-audit
```

**Cadence**: run this periodically (recommended: monthly, and whenever dependencies are
added or updated).

**Patch SLA**: any vulnerability identified by `pip-audit` is patched within 7 days of
detection, by updating the affected package to a patched version (`pip install -U
<package>`) and re-running the test suite (`pytest`) to confirm nothing broke.
