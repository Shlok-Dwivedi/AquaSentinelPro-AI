# 🛡️ Security Policy: AquaSentinelPro-AI

We take the security of our water safety assessment platform seriously. This document details our threat model, vulnerability reporting instructions, and the security controls implemented in AquaSentinelPro-AI.

---

## 🔒 Implemented Security Controls

To ensure production-grade security, AquaSentinelPro-AI enforces the following policies:

1. **Cryptographic Hashing:**
   * User passwords are encrypted using **bcrypt** (minimum work factor: 12). Plaintext passwords are never stored in the database.
2. **Stateless Access Validation:**
   * Short-lived JWT Bearer access tokens (expiry: 30 minutes) are used to authenticate requests.
3. **Rotating Refresh Tokens with Reuse Detection:**
   * Session state is verified via hashed refresh tokens stored in the database.
   * If a refresh token is reused (indicating a potential token interception anomaly), the entire user session is revoked automatically.
4. **Environment Isolation:**
   * API secret keys, database credentials, and LLM configuration keys are loaded dynamically from environment variables, preventing hardcoded secrets leaks.

---

## 🐛 Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it immediately:

* Do **NOT** open a public issue on GitHub.
* Email the lead developer directly at: `security@aquasentinelpro.org` (or contact Shlok Dwivedi via GitHub).
* Provide a clear Proof of Concept (PoC) or reproduction steps.

We will review your submission and release a patch within 48 hours.
