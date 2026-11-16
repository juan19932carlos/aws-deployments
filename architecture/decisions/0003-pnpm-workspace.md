# 0003. pnpm workspace for Node packages

- **Status:** Accepted. Supersedes the package manager row of [0002](./0002-documentation-site.md).
- **Date:** 2026-11-16

## Context

ADR 0002 chose npm for the docs site, because it was the only Node package. Future Node apps or packages may join it.

## Decision

| Area | Choice | Rejected | Why |
| --- | --- | --- | --- |
| Node package manager | pnpm workspace at the repo root, versions in a `catalog:` | npm, standalone package in `architecture/site` | Catalogs keep one version per dependency across packages, and pnpm isolates dependencies strictly. Same as `aws-xray-example`. |

## Consequences

- `pnpm-workspace.yaml` lists the Node packages. Python stays in the uv workspace; the two do not mix.
- pnpm is pinned in `mise.toml` and in `packageManager` of the root `package.json`. CI reads the latter.
- Install scripts are blocked by default. Each one must be allowed or denied in `allowBuilds`.
