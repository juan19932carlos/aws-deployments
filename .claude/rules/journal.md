# Journal

- The journal lives in `architecture/journal/`. One file per working day: `NNNN-short-title.md`, numbered from `0001`.
- Add new work of the same day to that day's file as a new segment. Do not open a new file for it.
- Everything is written in English, including the headings.
- Scope: only work toward the repo's goal, deploying to AWS. Docs site, CI, package managers and repo tooling do not go in the journal.
- Write only what actually happened and was observed in the session. Never fill gaps with plausible detail; ask instead.
- Do not reference other projects, even when a structure was reused from one.
- Be honest in **Result**. Use ⚠️ when something was built but not verified.
- The goal is learning: put the AWS mechanism you understood in **Finding / Technical note**, not just the fix.

## Template

```markdown
# Journal NN: [Short title of what you did today]
* **Date:** YYYY-MM-DD
* **Main goal:** [One sentence describing the goal of the day]

---

## 1. Segment: [Name of the block or task]
* **Action:** What you tried to do, what component you created, or what infrastructure you touched.
* **Result:** ✅ *Worked* / ❌ *Failed* / ⚠️ *With warnings* (brief explanation of the outcome).
* **Finding / Technical note:** A key detail, a strange error, or a useful command worth remembering.

## 2. Segment: [Next block]
* **Action:** ...
* **Result:** ...
* **Finding / Technical note:** ...

---

## 📌 Summary and Next Steps
* **Key achievements:** ...
* **Technical debt or pending items for tomorrow:** ...
```
