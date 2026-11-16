# Journal 01: Setup, uv workspace and gradual deployment
* **Date:** 2026-11-16
* **Main goal:** Set up a reproducible SAM project with uv and prepare a gradual Lambda deployment with CodeDeploy.

---

## 1. Segment: Toolchain with mise
* **Action:** Pinned aws-cli `2.40.3`, aws-sam `1.172.1`, Python `3.14.10` and uv `0.13.8` in `mise.toml`.
* **Result:** ✅ *Worked*. All tools install and report the pinned versions.
* **Finding / Technical note:** mise offers Python 3.15, but the local version must match a Lambda runtime AWS offers, so it stays on 3.14.

## 2. Segment: SAM Hello World
* **Action:** Ran `sam init` (Python Hello World). It created a subfolder, so its content was moved to the repo root.
* **Result:** ✅ *Worked*.
* **Finding / Technical note:** The template already used `python3.14`. Added `.aws-sam/` to `.gitignore`: it is build output.

## 3. Segment: uv workspace with `apps/` and `packages/`
* **Action:** Moved the function to `apps/hello_world` (`src/`, `tests/`, `events/`, own `pyproject.toml`). Root `pyproject.toml` is the workspace.
* **Result:** ✅ *Worked*. Unit tests pass, `sam build` succeeds, `sam local invoke` returns `hello world`.
* **Finding / Technical note:** SAM does not enforce the `sam init` layout. It only needs the template, and each function's `CodeUri` can point anywhere.

## 4. Segment: Building with uv through a Makefile
* **Action:** Set `BuildMethod: makefile` on the function. The app's Makefile runs `uv export` and `uv pip install --target $(ARTIFACTS_DIR)`.
* **Result:** ⚠️ *With warnings*. Two failures before it worked.
* **Finding / Technical note:** SAM's pip builder ignores `uv.lock`, so the Makefile is SAM's only hook. It needed `make` (not installed, pinned via mise `conda:make`). It needed `build_in_source = true`, because SAM otherwise copies the app to a temp folder. And it needed the commands to run from the workspace root, because `uv export` writes paths relative to it.

## 5. Segment: Gradual deployment with CodeDeploy
* **Action:** Added `AutoPublishAlias: live`, `DeploymentPreference: Linear10PercentEvery1Minute`, an `ErrorsAlarm` and a `PreTrafficHook`.
* **Result:** ⚠️ *With warnings*. `sam validate --lint` and `sam build` pass. Not deployed yet.
* **Finding / Technical note:** A version is immutable; an alias is a movable pointer. API Gateway now calls `live`. The first deploy has no shift: `live` just points to version 1.
* **Finding / Technical note:** `Errors` counts only failed invocations (exception, timeout, out of memory). Returning `statusCode: 500` is not an error to Lambda. The alarm watches only the new version (`ExecutedVersion`).
* **Finding / Technical note:** CodeDeploy ignores the hook's return value. The hook must call `PutLifecycleEventHookExecutionStatus` with `Succeeded` or `Failed`. The SAM-created role only invokes functions named `CodeDeployHook_*`.

---

## 📌 Summary and Next Steps
* **Key achievements:** Reproducible toolchain, uv workspace that SAM can build, gradual deployment defined in the template.
* **Technical debt or pending items for tomorrow:** First `sam deploy`. Change `app.py` and deploy again to watch the traffic shift. Set `HOOK_STATUS: Failed` to watch a rollback.
