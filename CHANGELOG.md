# Changelog

## 2026-10-11

- Remove jQuery. It was only used to show the loading spinner, so every
  page loaded 87 KB of JavaScript for one `onclick`. The Lookup button
  now sets the spinner's `display` to `block` directly, which is what
  jQuery's `.show()` did.
  - `services/web/project/templates/home.html`: drop the jQuery
    `<script>` tag (old line 8) and use `document.getElementById` in
    the button's `onclick` (line 18).
  - `services/web/project/assets/jquery-3.7.1.min.js`: deleted.
  - `CLAUDE.md` and `ACR.md`: updated to match.
- Add `services/web/.dockerignore`. `COPY . .` copied everything in
  `services/web/` into the image, including `__pycache__` and a
  root-owned `project/assets/app.css` left by the dev watcher. They're
  now excluded, along with the Dockerfiles. `custom.headers` is
  deliberately not excluded, since production needs it.
- Add `ACR.md` with an [AI Code Rating](https://aicoderating.com/) of
  B2b (Experienced maintainer, 26-50% AI-written code, Reviewed), and
  its badge under the title in `README.md`. About 35% of the
  non-blank code lines (57 of 163, not counting docs, the vendored
  daisyUI plugin, or jQuery) come from AI-assisted commits.
- Update Python from 3.9 to 3.14, Flask from 2.3.0 to 3.1.3, gunicorn
  from 20.1.0 to 26.2.0, and flake8 from 7.1.2 to 7.4.1, and pin
  Werkzeug to 3.1.9. Python 3.9 reached end of life in October 2025,
  so it no longer gets security fixes. gunicorn 20.1.0 has a
  request-smuggling vulnerability (CVE-2024-1135, fixed in 22.0.0).
  Werkzeug wasn't pinned, so each build installed whatever version was
  newest. gunicorn 26 also adds a control socket for its `gunicornc`
  tool, which ptr doesn't use; gunicorn tried to create it in
  `/home/app/.gunicorn`, which the `app` user can't write to, and
  logged a `Permission denied` error on every start, so it's now
  turned off with `--no-control-socket`.
  - `services/web/requirements.txt`: new Flask and gunicorn versions,
    and pin Werkzeug.
  - `services/web/Dockerfile:6,35,52`: `python:3.14.7-slim` for both
    stages, and flake8 7.4.1.
  - `docker-compose.yml:8`: add `--no-control-socket` to the gunicorn
    command.
  - `CLAUDE.md`: note the control socket setting and the new versions.
- Add `<!doctype html>`, `lang="en"`, and a viewport meta tag to the
  page, and remove three classes that did nothing. Without a doctype
  the browser rendered the page in quirks mode, which Tailwind's base
  styles don't expect; without `lang` screen readers had to guess the
  language; and without a viewport tag phones showed a zoomed-out
  desktop layout. `form` and `loading-circle` aren't daisyUI classes
  and `justify-left` isn't a Tailwind class (it's `justify-start`), so
  none of them was in the built CSS. Screenshots before and after are
  identical at desktop width in both light and dark mode. File
  changed: `services/web/project/templates/home.html:1-5,15-16,22`.
- Stop rendering the lookup result with `|safe`. It holds the address
  from the URL and a hostname from a PTR record, which whoever runs the
  IP's reverse zone controls, so any HTML that got through would have
  run on the page. The result is now autoescaped like every other
  value; it looks the same (`->` is escaped as `-&gt;`). Files changed:
  `services/web/project/templates/home.html:22`, and `CLAUDE.md`.
- Fix an open redirect in the lookup form. `POST /` passed the typed
  address straight to `redirect()`, so an address of
  `https://evil.com` or `//evil.com` sent the visitor to another site.
  The redirect is now built with `url_for`, which encodes the value,
  so it always stays on this site. Files changed:
  `services/web/project/__init__.py:3,19-22`, and `CLAUDE.md`.
- Fix the install URL in `README.md` to `http://IP_ADDRESS:8101`. It
  said `https://`, but gunicorn serves plain HTTP on that port, so the
  documented URL failed with a TLS error.
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
