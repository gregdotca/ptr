# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small Flask app ("PTR Record Lookup") that does reverse-DNS lookups. Demo: https://ptr.greg.ca. It runs in Docker under gunicorn.

## Commands

Production (the tracked setup):

```sh
docker-compose up -d --build     # serves on 10.0.0.3:8101 -> container :5000
```

The gunicorn command has `--no-control-socket` because ptr doesn't use gunicorn's `gunicornc` control tool, and the `app` user can't create its default socket in `/home/app/.gunicorn`. It runs `--workers 2 --threads 4` (gunicorn's threaded `gthread` worker), so one slow reverse lookup or the 0.25s POST delay doesn't block everyone else; with gunicorn's default single sync worker, requests were handled one at a time.

Local development without Docker (from `services/web/`; needs the Tailwind standalone CLI on the host to build the CSS):

```sh
pip install -r requirements.txt
tailwindcss -i project/styles/app.css -o project/assets/app.css --watch &
python manage.py --debug run     # Flask CLI via FlaskGroup in manage.py
```

Lint (the production image runs this in its builder stage, so a lint failure breaks `docker-compose build`):

```sh
flake8 --ignore=E501,W503,F401 services/web
```

Tests (from `services/web/`; pytest is in `requirements-dev.txt`). The production image also runs these in its builder stage, right after the lint, so a failing test breaks `docker-compose build` too:

```sh
pip install -r requirements-dev.txt
python -m pytest
```

The tests in `services/web/tests/` replace `socket.getnameinfo` with a fake, so they don't need the network, and skip the 0.25s spinner delay. The builder stage installs `requirements-dev.txt` to run them. The final stage copies only `manage.py` and `project/`, so the tests, pytest, and `requirements-dev.txt` stay out of the production image. `test.py` in the root is an untracked scratch script for redirect-chain checks, not part of the suite.

The compose file has a `healthcheck` that expects `GET /` to return a 302. It doesn't follow the redirect, so it doesn't depend on DNS. `restart: unless-stopped` doesn't restart a container that's only unhealthy; the status is for `docker ps` and monitoring.

## Dev/prod environment switching

Only the production files are tracked. The dev variants (`docker-compose.DEV.yml`, `services/web/Dockerfile.DEV`), `to-dev.sh`, `to-prod.sh`, and `test.py` are excluded through `.git/info/exclude`, not `.gitignore`.

`./to-dev.sh` and `./to-prod.sh` swap environments by renaming files: the active pair is always `docker-compose.yml` and `services/web/Dockerfile`, and the inactive pair gets a `.PROD` or `.DEV` suffix. So while in dev mode, the tracked `docker-compose.yml` and `Dockerfile` contain the dev versions. Check which one is active (`ls docker-compose.*.yml`) before editing either file, and switch back with `./to-prod.sh` before committing. The dev compose file runs the Flask dev server with `services/web/` bind-mounted to `/app` on port 5000. Alongside it, `tailwindcss --watch=always` rebuilds `project/assets/app.css` into the mounted directory (`--watch=always` because the container's stdin is closed), so that file on the host ends up owned by root.

## Architecture

All app logic is in `services/web/project/__init__.py`; `manage.py` only wraps `app` for the Flask CLI and gunicorn (`manage:app`).

- `GET /` redirects to `/8.8.8.8` (`DEFAULT_ADDRESS`).
- `POST /` takes the form's `address` field (an empty field falls back to `DEFAULT_ADDRESS`) and redirects to `/<address>` after a 0.25s sleep, so the loading spinner shows. The redirect is built with `url_for`, which encodes the value, so a typed address like `https://example.com` can't send the visitor to another site. Lookups are always rendered from the GET URL, which keeps results linkable.
- `GET /<address>` checks the address with `is_ip_address()` (`ipaddress.ip_address()`). Anything that isn't an IP address, such as a hostname or a path like `/robots.txt`, gets the normal page with "Invalid IP address" and a 404 status, so crawlers and bots don't treat it as a real page. Otherwise it calls `get_ptr()`, which calls `socket.getnameinfo()` with `NI_NAMEREQD` and returns `"<address> -> <hostname>"`, "No PTR record found for <address>" (`EAI_NONAME`), or "Unable to lookup PTR record" (any other lookup error). Keep `NI_NAMEREQD`: without it, `getnameinfo()` returns the address itself when there's no PTR record, which looks like a successful lookup.

There's a single template, `templates/home.html`. The lookup result (`page_body`) is a plain string and is autoescaped like every other value. Never add `|safe`: the result includes the address from the URL and a hostname from a PTR record, and whoever controls the IP's reverse zone controls that record.

Static files are served from `project/assets/` at `/assets/...` (Flask's `static_folder`, so use `url_for('static', ...)`). The favicon is vendored there. There's no JavaScript library: the Lookup button's inline `onclick` shows the loading spinner.

`services/web/.dockerignore` keeps `__pycache__`, the Dockerfiles, and a locally built `project/assets/app.css` out of the image. Don't add `project/templates/custom.headers` to it: production builds need that file in the image.

Tailwind 4 and daisyUI 5 are built at Docker build time, not loaded from a CDN. In the Dockerfile's builder stage, the Tailwind standalone CLI (version and per-architecture SHA-256s pinned as `ARG`s) compiles `project/styles/app.css` into `project/assets/app.css`, which is gitignored; the final stage copies the built file in after the project. `app.css` uses `source(none)` with `@source "../templates"`, so only the templates are scanned: a class used only from Python or JS won't be in the build unless it also appears in a template. daisyUI is the vendored plugin `project/styles/daisyui-<version>.mjs`, with only the `bumblebee` (light) and `business` (dark) themes enabled. To upgrade either one, update the `ARG`s in both `Dockerfile` and `Dockerfile.DEV`, or replace the `.mjs` file and its reference in `app.css`.

Dark mode is automatic only, with no toggle, JavaScript, or `data-theme` attribute. `bumblebee --default, business --prefersdark` in `project/styles/app.css` puts `business` inside `@media (prefers-color-scheme: dark)` on `:root:not([data-theme])`, so adding `data-theme` to `<html>` would lock the page to one theme. A `color-scheme` meta tag in `home.html` tells the browser about both modes before the CSS loads. Use daisyUI theme colours (`base-content`, `base-200`, and so on), not hard-coded colour classes (`text-gray-*`, `bg-white`), so both modes keep working. Tailwind's `dark:` variant uses the same media query, so per-mode tweaks go there (the Lookup button is `btn-accent dark:btn-primary`, because `business`'s accent is orange). Dark-mode overrides of theme variables live in an unlayered rule at the end of `project/styles/app.css`: a darker `--color-primary` for the button, and `bumblebee`'s `--radius-*` corner sizes so both modes match. Being unlayered, it beats daisyUI's layered theme.

`templates/custom.headers` is gitignored and optionally included (`ignore missing`) in `<head>`. It's for per-deployment additions such as analytics.

The stack is pinned: Python 3.14.7-slim (both Dockerfiles), Flask 3.1.3, Werkzeug 3.1.9, gunicorn 26.2.0, flake8 7.4.1, pytest 9.1.1 (dev only), Tailwind 4.3.3, and daisyUI 5.7.46. The builder stage makes wheels with `--no-deps`, so only the packages in `requirements.txt` are pinned; Flask's other dependencies are resolved when the final stage installs the wheels.
