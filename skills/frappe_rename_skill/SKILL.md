---
name: frappe_rename_skill
description: Rename a Frappe app (package, module, brand, DB registry) safely and verify it. Use when the user wants to rename a Frappe/ERPNext custom app, change its module or display name, or choose between an in-place rename and a new app. Covers the decision, a parameterised codemod, the in-place DB script, a hard cut onto fresh sites, verification, rollback and pitfalls.
---

# frappe_rename_skill

Rename a Frappe app: `OLD` (snake, e.g. `old_app`) to `NEW` (snake), display `Old App` to `New App`.
Evidence labels: **[field]** = done on a real, large app in a disposable bench; **[lab]** = tried only on a toy app or a clone, not on production; **[untested]** = reasoned, never run.

## 1. Decide first (ask the owner)

| Situation | Path |
|---|---|
| Nothing live, sites disposable | **Hard cut**: codemod + brand-new sites. No DB script, no aliases. Cheapest and cleanest. [field] |
| Sites hold data to keep | **In-place**: codemod + DB script on every site, then migrate. [field: ~35 s on a clone] |
| Package layout or repo must change, or both names must coexist | **New app** + move data + uninstall old. Costlier; `uninstall-app` deletes Workspace/Report/Custom Field rows by module and can drop DocType tables. [lab] |

Code-only rename (no DB step) always fails: every bench command raises ModuleNotFoundError until the registry is fixed. [field]
Ask: is anything live (emailed links, webhooks, wallet passes)? If yes, external `/api/method/OLD.*` URLs need aliases (`override_whitelisted_methods`, one entry per method) [untested]. If no, hard cut with no aliases.

## 2. Prep (never on the main line)

- Fetch, branch from the integration base, work in a separate worktree. Never push to base branches; no force push.
- Pre-gate: run the pure/unit test sweep on the base tree and record failures, so later you can tell regressions from existing failures.
- Decide the token set up front: snake, Title, kebab, CamelCase, UPPER. Decide the module: Frappe cannot keep folder `OLD/OLD` if the Module Def becomes `New App`, so rename module folder + Module Def + every `module` column together (`NEW/NEW`).
- Decide what stays: externally registered names (messaging template names approved at a vendor), short prefixes (`xx_`), domain DocTypes, hash/salt/secret config keys (renaming a key silently re-hashes or invalidates sessions), history tables. Write them in the config as protect/keep lists.
- Copy backups out of `sites/*/private/backups` before starting; Frappe prunes them.

## 3. Codemod (code phase)

`scripts/frappe_rename.py REPO --old old_app --new new_app --old-title "Old App" --new-title "New App" [--keep-prefix old_app_template_] [--protect STR ...] [--dry-run] [--scan]`

- Rewrites tracked text files, then `git mv` for paths (keeps history). Skips binary and listed top dirs (history, reports, screenshots).
- Matches glued JSON-escaped forms (`\nold_app.x`) and refuses to guess: any `old_app_<word>` identifier not covered by `--keep-prefix` or a map file aborts the run before writing (exit 2). Classify each one: hook, config key, doc name, or kept external name. [field: this caught real config keys and template names]
- Script status: the codemod design is [field] (a larger project-specific version ran on a ~3,000-file app); this generic script was only smoke-tested on a toy repo [lab]. `db_rename.py` and `db_scan.py` are [untested] generic ports of a field-proven procedure.
- `--scan` is the leftover gate: exit 0 means only protected/kept hits remain.
- Rerunnable: second run changes nothing (verify with `--dry-run`).
- After it runs, hand-check: `hooks.py`, `pyproject`/`setup`, `package.json` names, vite `base` paths, `/assets/OLD` URLs, `.gitignore`, `.gitattributes`, `.pre-commit`, `patches.txt`, translation CSVs (key is source text; edit all together), `modified` timestamps of shipped JSON (bump so in-place sites re-sync), `OLD.OLD.` module-sense dotted paths (Number Card methods).
- Commit order: (1) mechanical, (2) hand fixes, (3) docs. Keep the mechanical commit pure so it can be regenerated.

## 4a. Hard cut (nothing live)

1. Provision a **new** bench/site (clone a reference bench if provisioning from scratch is slow; never modify the reference).
2. Install the renamed app on a fresh site (`bench new-site`, `install-app NEW`). Run migrate twice; both must exit 0 with no tracebacks.
3. Old sites will break (`ModuleNotFoundError`); that is accepted. Drop them later, only after a backup and with owner sign-off, and only sites you own. Never blanket drop.
4. Scan the new DB for leftovers (`scripts/db_scan.py`).

## 4b. In-place (sites with data)  [field on clone; scripts here are untested generic versions]

Order: stop web/workers/scheduler, drain queues **on old code** (queued jobs carry old dotted paths), backup every site (+files), then:
1. Code: check out renamed tree, `mv apps/OLD apps/NEW`, fix `sites/apps.txt` and `apps.json`, `pip uninstall OLD`, `pip install -e apps/NEW --no-deps`, delete stale dist-info/.pth and the `sites/assets/OLD` symlink.
2. DB on EVERY site, before migrate, one transaction: `scripts/db_rename.py` (installed_apps, Installed Application, Module Def, `module`/`app_name` columns, Patch Log prefixes so patches do not re-run, Scheduled Job Type method, dotted-path sweep over text columns, `rename_doc` for brand-named docs, epoch `modified` for shipped JSON, site-scoped cache key delete; never `flushall`).
3. `bench --site S migrate` (expect exit 0 and no `Executing NEW.patches...`), rebuild assets, restart.
4. Compare counts (Patch Log, DocTypes, business rows) before and after. Rerunning the DB script must touch 0 rows.
Any site missed by the DB script breaks bench-wide migrate; do all in the same window.

## 5. Verification (all four, not just tests)

1. **Fresh install**: new site installs and migrates twice clean; DB scan shows no old name except intended keeps.
2. **Seeding**: run every seeder/test pack the repo has, twice (second run must add nothing). Many seeders hard-wire site names and refuse others; list the ones you could not run. On a fresh site expect: patches are marked done so patch-created seed data is missing; time zone is blank until setup runs; config keys of form `<kid>.<secret>` must be well-formed or features silently skip. [field]
3. **Browser UI** in a real browser against the new site: login, desk home, sidebar/dock, main workspaces, a report, customer/guest pages, light and dark, desktop and phone width. Look for the old name in titles and text, broken assets (`/assets/NEW/...`), and console errors. Realtime (socket.io) is usually not running on a lab bench and adds console noise. [field]
4. **Tests**: pure sweep first, then bench modules one at a time per site (shared DB deadlocks; purge only your own bench's queues between modules). Compare against the base tree on a **fresh** site pair (base vs renamed) before calling a failure a regression; shared sites accumulate state and flip results. [field]

Never claim a check passed that was not run; list what was skipped.

## 6. Rollback

Hard cut: delete the new branch and new sites; old sites untouched. In-place: stop, restore old code and pip state, `bench --site S --force restore <backup>` (with files), delete site-scoped redis keys before any bench command, migrate. [field: 38 s]. The point of no return is the first write by new code: a restore loses it. Never use `uninstall-app` as a rollback or step.

## 7. Pitfalls seen

- `bench build --app NEW` can fail in esbuild with nested or symlinked sub-apps even though it exits 0; build each frontend with its own tool and check `public/dist`.
- Built frontends (`node_modules`, `public/dist`) inside the app tree make repo-scanning tests fail; scan with them excluded or build outside.
- A rename test that reads git history (file-modified-since checks) fails by construction; use `--follow` and ignore the codemod commit.
- Guard regexes that protect site names (e2e, smoke, restore drills) may stop matching after a rename; update them first, or they fail closed or stop protecting.
- Paths in tests or tools that embed the old name (report dirs) may now point at nonexistent directories; make tests fall back to a temp dir.
- Docs that assert text (e.g. ops docs checked by tests) must be rewritten in the same commit.
- A burst worker drains other sites' jobs on a shared Redis; use a separate redis db or purge only your own queues.
- Host entries: add only your own new `/etc/hosts` lines, guarded by grep; do not edit existing ones.
- A latent bug may surface only because fresh data is generated (e.g. random hash names that are all digits tripping a PII phone scan). Fix narrowly and call it out in the PR.
- Security keys: a key literal used as a salt fallback changes under a blind rename; review.
- Never touch pre-existing benches/sites/containers; only ones you created.
