# Journal 01: Project setup and CodeDeploy configuration
* **Date:** 2026-11-16
* **Main goal:** Set up the SAM project and configure a gradual Lambda deployment with CodeDeploy.

---

## 1. Segment: Project setup
* **Action:** Scaffolded the SAM Hello World app with a mise toolchain, then reorganized it as a uv workspace with `apps/` and `packages/`.
* **Result:** ⚠️ *Not verified*. Nothing has been built or run yet.
* **Finding / Technical note:** SAM only needs the template: each function's `CodeUri` points to its folder, here `apps/hello_world/`.

## 2. Segment: CodeDeploy configuration
* **Action:** Added `AutoPublishAlias: live`, `DeploymentPreference: Linear10PercentEvery1Minute`, an `ErrorsAlarm` and a `PreTrafficHook` to `template.yaml`.
* **Result:** ⚠️ *Not verified*. Not built and not deployed.
* **Finding / Technical note:** The alias `live` points to a published version; CodeDeploy shifts its traffic to the new version and rolls back if the alarm fires or the hook reports `Failed`.

## 3. Segment: Stale build after a code change
* **Action:** Changed the message in `app.py`, ran `sam build` and `sam deploy` to publish version 2.
* **Result:** ❌ *Failed*. `sam deploy` skipped the upload and returned "No changes to deploy": the built `app.py` was still the old one.
* **Finding / Technical note:** The cache was uv's, not SAM's. The Makefile installs the app as a package, and uv reuses its cached wheel. The built `app.py` was a hard link into `~/.cache/uv`.
* **Finding / Technical note:** uv decides a local package changed only from `pyproject.toml`, `setup.py` and `setup.cfg` (`cache-keys`), not from the source code. Same zip, same hash: SAM publishes no new version.
* **Finding / Technical note:** Workaround: bump `version` in the app's `pyproject.toml`. It works, but it is manual. Root fix: add `src/**/*.py` to `tool.uv.cache-keys`.

## 4. Segment: How `sam build` packages the Lambda
* **Action:** Traced what happens from `sam build` to the running function.
* **Result:** ✅ *Understood*.
* **Finding / Technical note:** The only install is the Makefile, on this machine. `sam deploy` only zips and uploads, CloudFormation only points Lambda at the zip in S3, and Lambda only unzips and runs.
* **Finding / Technical note:** `requirements.txt` is not for Lambda. `uv pip install --target` cannot read `uv.lock`, so `uv export` turns the lock into a pinned list. The Makefile deletes it before SAM zips the folder.
* **Finding / Technical note:** `--python-platform x86_64-manylinux2014` downloads Linux x86_64 wheels whatever the build machine is. It must match `Architectures` in the template.

## 5. Segment: First gradual deployment
* **Action:** With the version bumped to `0.1.1`, ran `sam build` and `sam deploy`, and called the API once a second with `curl`:

  ```bash
  while true; do curl -s https://vy86qf35f3.execute-api.us-east-1.amazonaws.com/Prod/hello; echo; sleep 1; done
  ```

  Mid-shift, the responses mixed both versions:

  ```
  {"message": "hello world"}
  {"message": "hello Juan"}
  {"message": "hello world"}
  {"message": "hello world"}
  {"message": "hello Juan"}
  ```
* **Result:** ✅ *Worked*. The responses moved from only `hello world`, through a mix, to only `hello Juan`.
* **Finding / Technical note:** The mix grows over the minutes, not in an exact 1-in-10 pattern: the alias routes each request at random by weight, so the old and new versions interleave.
* **Finding / Technical note:** CloudFormation finishes the stack update only when the linear shift ends. With 10% every minute, the deployment took about 9 to 10 minutes.

## 6. Segment: Drift detection on memory
* **Action:** Changed the function's memory outside CloudFormation and ran drift detection, first with memory not declared, then with `MemorySize: 128` declared in the template.
* **Result:** ✅ *Worked*. Drift was detected only once the memory was declared.
* **Finding / Technical note:** Drift detection compares only the properties declared in the template. A property left to its default is not checked, so changing it by hand goes unnoticed.

---

## 📌 Summary and Next Steps
* **Key achievements:** Gradual deployment with CodeDeploy deployed and observed: traffic moved from version 1 to version 2.
* **Technical debt or pending items for tomorrow:** Apply the `cache-keys` root fix.
