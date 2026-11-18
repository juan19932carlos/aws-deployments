# aws-deploy

## Purpose

- This is a sandbox to experiment with and learn about deploying applications to AWS. It is not production.
- SAM is the current deployment tool, not the subject. Other tools or approaches may be tried here.
- Explain the AWS/SAM mechanism behind each change, not just the fix, since learning is the goal.
- Favor approaches that show how deployment works over shortcuts that hide it.
- Never run `sam deploy`, `sam sync` or other AWS-changing commands. The user runs them; explain how instead.
- The user logs in with `aws login --profile personal-admin`. `samconfig.toml` pins that profile and `us-east-1`.

## Layout

- uv workspace: each Lambda lives in `apps/<name>/`, shared code in `packages/`.
- Each app owns its `src/`, `tests/`, `events/`, `pyproject.toml` and `Makefile`.
- Exception: `pre_traffic_hook` has no Makefile. Only `template-cfn.yaml` uses it; `template.yaml` keeps the hook inline.
- `template-cfn.yaml` deploys with the AWS CLI. `aws cloudformation package` ignores `InlineCode` and zips the repo root.
- `package` zips `src/` as is, `__pycache__` included, and a new hash means a new Lambda version. Clean it first.

## Build

- Deliberate: every function uses `BuildMethod: makefile`, because SAM's pip builder ignores `uv.lock` and `packages/`.
- One Makefile per app, with a target named `build-<LogicalId>`. SAM runs it; nobody calls make by hand.
- `samconfig.toml` sets `build_in_source` so the Makefile can reach the workspace root. Do not remove it.
- `make` is pinned in mise (`conda:make`) only because SAM needs it; it is not installed system-wide.
- Gotcha: uv caches the app's wheel and checks only `pyproject.toml`. A code-only change builds stale code and deploy says "No changes".
- Workaround in use: bump the app `version` on each code change. Root fix pending: `src/**/*.py` in `tool.uv.cache-keys`.
- `--python-platform` in each Makefile must match `Architectures` in the template (now x86_64).

## Template

- Deliberate: declare properties even at their default (e.g. `MemorySize: 128`). Drift detection only checks declared ones.
- See what SAM expands into with `get-template --template-stage Processed`; `sam package` output is still SAM.

## Toolchain

- All tools are pinned in `mise.toml`; uv manages Python dependencies.
- Node and pnpm are pinned in mise. Keep `node-version` in `.github/workflows/docs.yml` in line with mise.
- Keep `packageManager` in `package.json` in line with pnpm in mise; CI reads the pnpm version from it.
- Node packages use pnpm only, never npm or yarn. Versions live in the `catalog:` of `pnpm-workspace.yaml`.
- Deliberate: pnpm over npm for catalogs and strict dependencies, so future Node apps share one workspace.
- Python stays on 3.14 to match an available Lambda runtime, even though mise offers 3.15.
- No root mise tasks yet; deciding later whether to add them.

## Docs

- `architecture/` holds ADRs, `infrastructure.md` and the journal, shown by the Docusaurus site in `architecture/site`.
- Rules for these docs and for the journal are in `.claude/rules/architecture-docs.md` and `.claude/rules/journal.md`.
- Add each AWS deployment session to the journal: one file per day, new segments for later work that day.
- The site deploys to GitHub Pages under `/aws-deployments/`, so links and assets must not be root-absolute.
- Pages source is set to "GitHub Actions" in the repo settings; the workflow token cannot enable Pages itself.
- `README.md` says what the project is about and is the site homepage. Usage commands do not go there.
- The site build copies `README.md` to `src/pages/index.md` (gitignored). Edit the README, never the copy.
- Deliberate: copy over a docs instance at the repo root, whose MDX loader also grabbed `architecture/` files and broke the build.
- README must render on GitHub and in Docusaurus: no front matter, no relative links to `architecture/` files.

## Testing

- Integration tests need a deployed stack and `AWS_SAM_STACK_NAME`; run only `apps/*/tests/unit` by default.
