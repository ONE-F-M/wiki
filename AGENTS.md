# AGENTS.md - wiki

This file is the working context for agents making changes in the `wiki` app repository.

## Purpose

`wiki` is a Frappe app for structured documentation, knowledge bases, and page-level collaboration. The repository contains the web routes, DocTypes, rendering pipeline, sidebar management, revision flow, and search indexing logic that power the wiki experience.

Work in this repository should preserve three things:

1. Page readability and route stability.
2. Sidebar integrity and cached navigation output.
3. Permission checks for non-public content.

## Repository Map

Top-level files and folders that matter most:

- `wiki/hooks.py`
  App metadata, route rules, install hooks, and scheduled/search reindex hooks.
- `wiki/www/wiki.py`
  Entry route that redirects `/wiki` to the default wiki space.
- `wiki/wiki/doctype/wiki_page/wiki_page.py`
  Core page lifecycle, sanitization, sidebar rendering, revisions, permission gates, and update logic.
- `wiki/wiki/doctype/wiki_page/search.py`
  Search implementation with Redisearch support and fallback web search.
- `wiki/wiki/doctype/wiki_space/wiki_space.py`
  Space creation, route-prefix handling, and sidebar mutation logic.
- `wiki/wiki/doctype/wiki_settings/wiki_settings.py`
  Cache invalidation for settings-driven sidebar changes.
- `wiki/wiki/doctype/wiki_page_patch/wiki_page_patch.py`
  Patch approval flow for proposed page changes.
- `cypress/e2e/wiki.cy.js`
  End-to-end coverage for page create/edit/delete behavior.
- `cypress/e2e/wiki_sidebar.cy.js`
  End-to-end coverage for sidebar group creation and empty-group deletion.

## Data Model

### `Wiki Page`

The main content record.

Observed responsibilities from the code:

- Stores page title, route, content, meta fields, and the `published` / `allow_guest` visibility flags.
- Inherits `WebsiteGenerator`, so each record can render directly as a website route.
- Sanitizes HTML before save in `before_save`.
- Clears sidebar cache when page titles change.
- Updates the search index on `on_update`.
- Removes linked revision/patch/sidebar records on `on_trash`.

Important files:

- `wiki/wiki/doctype/wiki_page/wiki_page.py`
- `wiki/wiki/doctype/wiki_page/wiki_page.json`
- `wiki/wiki/custom/wiki_page.json`

### `Wiki Space`

A namespace and navigation container for related pages.

Observed behavior:

- Holds child sidebar entries in `wiki_sidebars`.
- Auto-creates a starter page and starter group if the sidebar is empty during insert.
- Rewrites child page routes when the space route changes.
- Rebuilds search index and clears sidebar cache on update.

Important file:

- `wiki/wiki/doctype/wiki_space/wiki_space.py`

### `Wiki Group Item`

Binds wiki pages to sidebar groups and ordering.

This is what the sidebar update code mutates when users rearrange groups/pages.

### `Wiki Page Revision` / `Wiki Page Revision Item`

Revision history for content changes.

Observed behavior:

- A revision is created after insert.
- Additional revisions are written when content changes through the update flow.
- Revision data is shown in page context for comparison and history views.

### `Wiki Page Patch`

The approval workflow object for edits and proposed new pages.

Observed statuses in code:

- `Draft`
- `Under Review`
- `Approved`

Important note:

The task brief mentions `Draft -> Published -> Archived`, but the code inspected in this repository does **not** show an `Archived` workflow state. Agents should not invent one. The current code path is patch-oriented: edits become `Draft` or `Under Review`, then approved patches are submitted and applied, while published visibility is controlled by fields on `Wiki Page`.

## Page Lifecycle

The lifecycle in the current codebase is:

1. A `Wiki Page` record exists and may be published.
2. User edits are submitted through `update(...)` in `wiki_page.py`.
3. The edit becomes a `Wiki Page Patch` with status `Draft` or `Under Review`.
4. If the user has submit permission and the edit is not a draft, the patch is auto-approved and submitted.
5. Revision history is preserved through `Wiki Page Revision`.

Do not describe this repo as having a full archived-state workflow unless the code is added first.

## Sidebar Structure

Sidebar rendering is not static HTML checked into the repo. It is assembled dynamically:

1. `Wiki Space.wiki_sidebars` identifies page/group membership.
2. `WikiPage.get_sidebar_items()` constructs the sidebar data structure.
3. `WikiPage.get_items()` renders the sidebar template.
4. Rendered sidebar HTML is cached under the `wiki_sidebar` cache hash.

Cache invalidation happens from multiple paths:

- page title changes
- page deletion
- wiki space updates
- wiki settings sidebar visibility changes
- sidebar reorder operations

Any change to grouping or page labels should clear the relevant cache entries, otherwise the website can show stale navigation.

## Search Indexing

Search behavior is split into two modes:

### Fallback mode

If `Wiki Settings.use_redisearch_for_search` is disabled, search uses Frappe web search.

### Redisearch mode

If enabled, search uses Redisearch indexes per wiki space route.

Observed triggers for rebuilding/updating:

- `WikiPage.on_update()` calls `update_index(self)`
- `WikiPage.on_trash()` calls `remove_index(self)`
- `WikiSpace.on_update()` calls `rebuild_index_in_background()`
- `hooks.py` sets `after_migrate = ["wiki.wiki.doctype.wiki_page.search.rebuild_index_in_background"]`
- `hooks.py` also schedules the same rebuild hourly

Any change that affects route membership, title, or content must preserve the index update path.

## Security Rules

Non-negotiable rule:

**Never expose private pages without a permission check.**

Grounded examples from the current code:

- `WikiPage.verify_permission()` checks `allow_guest` for read access and redirects unauthorized users to login.
- `sanitize_html()` strips unsafe HTML and only permits limited iframe usage for YouTube embeds.
- Search endpoints are guest-accessible, so page visibility assumptions must stay aligned with indexing and route checks.

If you modify rendering, patch application, sidebar APIs, or search, re-check permission boundaries.

## Customizations vs Upstream

What is clearly fork-specific in this repository from local inspection:

- Branch workflow assumes `staging`, `test-production`, and `version-15`.
- Repo-level automation includes `.github/workflows/agent-trigger.yml` and `.github/workflows/agent-trigger-beta.yml`.
- CI alignment work in sprint branches adds repo-specific PR gating and typing/linting patterns.

What is **not** safe to assume:

- That every file under `wiki/` diverges from `frappe/wiki`.
- That an upstream branch named `version-15` exists in `frappe/wiki` today.

When syncing from upstream or applying automated refactors:

- Preserve repo-specific workflow files under `.github/workflows/`.
- Preserve branch protection assumptions around `staging`, `test-production`, and `version-15`.
- Diff before overwriting root docs (`README.md`, `AGENTS.md`) or CI files.

## Cypress Test Patterns

Current tests are browser-first and interaction-driven.

Patterns already in use:

- `cy.login()` in `beforeEach()`
- `cy.visit("/wiki")` to enter the public route
- `.wiki-options .dropdown-toggle` to open author actions
- `.edit-wiki-btn` to enter edit mode
- `.wiki-editor .ProseMirror` for rich-text editing
- request waits using `cy.intercept(...)` for page route/network stabilization

Current coverage areas:

- create page
- edit page
- delete page
- create sidebar group
- delete empty sidebar group

When adding E2E coverage:

- Prefer extending these flows rather than inventing a parallel harness.
- Wait on meaningful route or network events before asserting DOM state.
- Keep selectors aligned with the existing sidebar/editor structure.

Typical local command shape, depending on the team setup:

```bash
bench start
# in another shell
npx cypress open
```

or:

```bash
npx cypress run
```

## Deployment / Branch Flow

Observed repo workflow expectations:

- feature/task branches open PRs into one of `staging`, `test-production`, or `version-15`
- `staging` is the normal integration branch
- `test-production` is used as a pre-production validation branch
- `version-15` is treated as a protected long-lived branch

Agents should not push directly to those protected branches. Use task branches and PRs unless the human explicitly instructs otherwise.

## Safe Editing Guidance

When changing code here:

- Preserve route stability where possible; wiki URLs are user-facing.
- Preserve cache invalidation around sidebar/search changes.
- Preserve patch/revision history behavior.
- Preserve `allow_guest` semantics and login redirects.
- Keep Frappe website rendering conventions intact.

When changing docs here:

- Do not invent unsupported lifecycle states or background jobs.
- Prefer “observed in current code” wording for behaviors that come from source inspection.

## Files To Treat Carefully During Updates

These files are especially likely to encode repo-specific behavior and should be diffed carefully before overwriting:

- `.github/workflows/agent-trigger.yml`
- `.github/workflows/agent-trigger-beta.yml`
- `README.md`
- `AGENTS.md`
- any repo-specific PR workflows introduced for `staging`, `test-production`, or `version-15`

## Quick Start For Future Agents

If you need to debug a wiki behavior fast:

1. Start with `wiki/wiki/doctype/wiki_page/wiki_page.py`.
2. Check whether the issue is content, sidebar, patch approval, or route rendering.
3. If search is involved, inspect `wiki/wiki/doctype/wiki_page/search.py`.
4. If navigation is stale, inspect sidebar cache invalidation.
5. If the issue is editor/UI flow, inspect Cypress tests and public JS assets.

That path will usually get you to the right subsystem without guesswork.
