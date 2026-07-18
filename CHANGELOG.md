# 📜 Changelog: AquaSentinelPro-AI

All notable changes to the AquaSentinelPro-AI Agentic Platform will be documented in this file.

---

## [1.0.0-rc1] - 2026-07-18
This release candidates completes the final release sprint, transitioning the platform from local prototyping to production readiness.

### Added
* **Structured PDF Reports:** Configured ReportLab document compilation with customized tables, warnings, and recommendations layouts.
* **Authentication Controls:** Implemented bcrypt password hashing, short-lived JWT access tokens, and rotating refresh tokens with automatic token reuse hijacking detection.
* **Unified Dashboard:** Developed a statistics analytics query endpoint tracking total checks run, reports compiled, and images analyzed.
* **Monitoring Suite:** Programmed `/health`, `/metrics` (CPU/Memory load, query latency), and `/system/info` system statistics endpoints.
* **Multi-Environment Configuration:** Subclassed Pydantic settings into isolated `Development`, `Testing`, and `Production` settings models.
* **Structured Rotating Logs:** Deployed a file handler logging JSON objects capped at 5MB, keeping 5 backup logs.
* **Docker Support:** Compiled `backend/Dockerfile`, `frontend/Dockerfile`, and `docker-compose.yml` configs.

### Changed
* **Tailwind v4 Integration:** Upgraded Vite client dependencies to support CSS-first compiles natively using `@tailwindcss/postcss`.

### Fixed
* **SECRET_KEY Vulnerability:** Patched `auth_service.py` to pull keys dynamically from settings instead of hardcoding signature fallbacks.

---

## [0.4.0] - 2026-07-16
### Added
* Vision Specialist Agent scanning visual indicators (algae, plastics, oil, foam) using `VisionProvider` interface.
* Offline mock visual scenarios validating graph routing gates.

---

## [0.3.0] - 2026-07-15
### Added
* Water Quality Index Python scoring module.
* Compliance standard deviations check referencing WHO/BIS specifications.
* Reflection consistency loop checking for logical visual-chemical contradictions.
