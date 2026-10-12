# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small Flask app ("PTR Record Lookup") that does reverse-DNS lookups. Demo: https://ptr.greg.ca. It runs in Docker under gunicorn.

## Commands

Production (the tracked setup):

```sh
docker-compose up -d --build     # serves on 10.0.0.3:8101 -> container :5000
```

Local development without Docker (from `services/web/`):

```sh
pip install -r requirements.txt
python manage.py --debug run     # Flask CLI via FlaskGroup in manage.py
```

Lint (the production image runs this in its builder stage, so a lint failure breaks `docker-compose build`):

```sh
flake8 --ignore=E501,W503,F401 services/web
```

There's no test suite. `test.py` in the root is an untracked scratch script for redirect-chain checks, not a test.

## Dev/prod environment switching

Only the production files are tracked. The dev variants (`docker-compose.DEV.yml`, `services/web/Dockerfile.DEV`), `to-dev.sh`, `to-prod.sh`, and `test.py` are excluded through `.git/info/exclude`, not `.gitignore`.

`./to-dev.sh` and `./to-prod.sh` swap environments by renaming files: the active pair is always `docker-compose.yml` and `services/web/Dockerfile`, and the inactive pair gets a `.PROD` or `.DEV` suffix. So while in dev mode, the tracked `docker-compose.yml` and `Dockerfile` contain the dev versions. Switch back with `./to-prod.sh` before committing. The dev compose file runs the Flask dev server with `services/web/` bind-mounted to `/app` on port 5000.

## Architecture

All app logic is in `services/web/project/__init__.py`; `manage.py` only wraps `app` for the Flask CLI and gunicorn (`manage:app`).

- `GET /` redirects to `/8.8.8.8` (`DEFAULT_ADDRESS`).
- `POST /` takes the form's `address` field and passes it unchanged to `redirect()` as a relative URL (after a 0.25s sleep, so the loading spinner shows), which resolves to `/<address>`; an empty field falls back to `DEFAULT_ADDRESS`. The value isn't validated, so an absolute URL such as `https://example.com` redirects off-site. Lookups are always rendered from the GET URL, which keeps results linkable.
- `GET /<address>` calls `get_ptr()`, which uses `socket.getnameinfo()` and returns either `"<address> -> <hostname>"` or a fixed error string.

There's a single template, `templates/home.html`. It renders the result through `{{ page_body|safe }}`, so anything passed as `page_body` isn't escaped. Escape user-influenced input before it reaches that variable. Styling comes from Tailwind v4 (browser build) and daisyUI 5 loaded from jsDelivr; jQuery and the favicon are served locally from `assets/`, which is the Flask static folder.

`templates/custom.headers` is gitignored and optionally included (`ignore missing`) in `<head>`. It's for per-deployment additions such as analytics.

The stack is pinned: Python 3.9.21-slim, Flask 2.3.0, gunicorn 20.1.0, and flake8 7.1.2.
