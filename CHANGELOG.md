# Changelog

## 2026-10-11

- Add `aria-label="Address"` to the address input in
  `services/web/project/templates/home.html`. It only had a
  placeholder, which screen readers don't reliably announce as a
  label, so the field had no accessible name.
- Add automatic dark mode that follows the visitor's system setting,
  with no toggle or JavaScript. The page was locked to the light
  `bumblebee` theme by `data-theme` on `<html>`.
  - `services/web/project/styles/app.css`: enable daisyUI's `business`
    theme for `prefers-color-scheme: dark`, and override its primary
    colour with a darker navy (`oklch(34% .085 251.473)`; text on the
    button 8.30:1) and its corner radii with `bumblebee`'s, so the
    corners match the light theme.
  - `services/web/project/templates/home.html`: remove `data-theme`,
    add a `color-scheme` meta tag, and make the Lookup button use the
    primary colour in dark mode (`dark:btn-primary`) instead of
    `business`'s orange accent.
  - `CLAUDE.md`: document how dark mode works.
- Build Tailwind 4.3.3 and daisyUI 5.7.46 CSS at Docker build time
  instead of loading them from jsDelivr. The page used the in-browser
  Tailwind compiler, a floating `daisyui@5` tag, and a separate themes
  file pinned to `5.0.0`, so every visitor downloaded and ran a
  third-party compiler, and upstream releases could change the styling
  without any change here. The build now produces one minified
  `app.css` (about 26 KB) with only the classes the template uses and
  the `bumblebee` theme.
  - `services/web/Dockerfile`: the builder stage downloads the Tailwind
    standalone CLI (checksum-verified, amd64 and arm64) and builds the
    CSS; the final stage copies in `app.css`.
  - `services/web/project/styles/app.css`: new Tailwind input file.
  - `services/web/project/styles/daisyui-5.7.46.mjs`: vendored daisyUI
    plugin, checksum-verified against the release asset.
  - `services/web/project/templates/home.html`: load `app.css` locally
    instead of the three CDN files.
  - `.gitignore`: ignore the generated `project/assets/app.css`.
  - `CLAUDE.md`: document the CSS build and the dev watcher.
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
