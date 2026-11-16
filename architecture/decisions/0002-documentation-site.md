# 0002. Documentation site

- **Status:** Accepted
- **Date:** 2026-11-16

## Context

We want a journal of what was tried while learning AWS deployment, plus the lasting decisions, readable as a site.

## Decision

| Area | Choice | Rejected | Why |
| --- | --- | --- | --- |
| Documentation site | Docusaurus in docs mode, two docs instances (decisions, journal) | Docusaurus blog mode, one dated post per entry | Numbered daily files with segments fit a working journal better than blog posts. |
| Node package manager | pnpm workspace at the repo root, versions in a `catalog:` | npm, standalone package in `architecture/site` | Catalogs keep one version per dependency across packages, and pnpm isolates dependencies strictly. Future Node packages join the same workspace. |

## Consequences

- The site reads `architecture/decisions` and `architecture/journal` in place, so the markdown has one source.
- Mermaid works through `@docusaurus/theme-mermaid`.
- `pnpm-workspace.yaml` lists the Node packages. Python stays in the uv workspace; the two do not mix.
- Node and pnpm are pinned in `mise.toml`. pnpm is also pinned in `packageManager` of the root `package.json`, which CI reads.
- Install scripts are blocked by default. Each one must be allowed or denied in `allowBuilds`.
- A GitHub Actions workflow publishes the site to GitHub Pages on every push to `main` that touches the docs.
