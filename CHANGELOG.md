# Changelog

## 2026-10-11

- Add `CLAUDE.md` with build, lint, and run commands, the dev/prod
  switching workflow, and an architecture overview, so future Claude
  Code sessions can work in the repo without rediscovering them.
- Update the copyright notices in `LICENSE` and `README.md` to
  `Copyright (c) 2025-2026 Greg Chetcuti <greg@chetcuti.com>`, adding
  the current year and contact email.
- Bind the published port in `docker-compose.yml` to `10.0.0.3:8101`
  instead of all interfaces, so the app is only reachable on that
  address.
- Add this changelog.
