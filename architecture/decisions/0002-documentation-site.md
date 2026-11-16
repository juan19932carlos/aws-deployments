# 0002. Documentation site

- **Status:** Accepted
- **Date:** 2026-11-16

## Context

We want a journal of what was tried while learning AWS deployment, plus the lasting decisions. Same structure as the earlier `aws-xray-example` project, so both read the same way.

## Decision

| Area | Choice | Rejected | Why |
| --- | --- | --- | --- |
| Documentation site | Docusaurus in docs mode, two docs instances (decisions, journal) | Docusaurus blog mode, one dated post per entry | Same layout as `aws-xray-example`. Numbered daily files with segments fit a working journal better than blog posts. |
| Package manager for the site | npm, standalone package in `architecture/site` | pnpm workspace, as in `aws-xray-example` | This repo is a Python uv workspace. There is no Node workspace to join, so a second package manager adds nothing. |

## Consequences

- The site reads `architecture/decisions` and `architecture/journal` in place, so the markdown has one source.
- Mermaid works through `@docusaurus/theme-mermaid`.
- Node is pinned in `mise.toml` only for this site.
- A GitHub Actions workflow publishes it to GitHub Pages on every push to `main` that touches `architecture/`.
