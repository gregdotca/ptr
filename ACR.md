---
rating: B3b
spec: "0.1"
updated: 2026-10-11
---

# AI Code Rating

**ACR B3b** (Maintainer: Experienced · AI Share: 51–75% · Oversight: Reviewed)

This project is rated with [AI Code Rating](https://aicoderating.com/spec/0.1/), spec version 0.1.

## How AI Was Used

The maintainer wrote ptr by hand in 2025: the Flask app, the PTR lookup, the page template, and the Docker setup. In 2026 an AI coding agent added a step to the Docker build that compiles the page's CSS locally instead of loading it from a CDN, and added automatic dark mode. It also fixed an open redirect in the lookup form, stopped the page from rendering the lookup result unescaped, made accessibility and markup fixes to the page (an input label, a doctype, language and viewport tags, and removing classes that did nothing), replaced jQuery with one line of plain JavaScript, kept local build leftovers out of the Docker image, updated Python and the dependencies, fixed lookups for addresses with no PTR record, added a Docker healthcheck, and wrote the test suite. The maintainer chose the changes and the look, including the dark mode colours, and read all of the code the AI wrote. The changes were checked by running the tests and by building and running the container.

The AI's changes are also reviewed by a second AI, and the two go back and forth until it doesn't find any more issues. That doesn't change the oversight level. Commits are marked with `Co-Authored-By: Claude Code` and, where Codex reviewed them, `Reviewed-By: Codex`.
