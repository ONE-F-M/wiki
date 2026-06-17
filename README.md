<br>
<br>

<div align="center">
<img width="150" alt="logotype" src="https://user-images.githubusercontent.com/28212972/128001084-508e446f-2814-4e1f-a5cb-09598f5a5bdc.png">
</div>

<br>

---

<div align="center">
 Wiki App built on the <a href="https://frappeframework.com">Frappe Framework</a> | <a href="https://wiki-docs.frappe.cloud/use_on_frappe_cloud">Try on Frappe Cloud</a>

 \
 [![Wiki](https://img.shields.io/endpoint?url=https://cloud.cypress.io/badge/simple/w2jgcb/master&style=flat&logo=cypress)](https://cloud.cypress.io/projects/w2jgcb/runs)
 [![CI](https://github.com/frappe/wiki/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/frappe/wiki/actions/workflows/ci.yml)
</div>

## Introduction

Frappe Wiki is an open source wiki app built on the Frappe Framework. It is designed for dynamic, text-heavy content such as internal documentation, knowledge bases, SOPs, and structured help content. The app supports page-level publishing, revision history, sidebars grouped by wiki space, and search across public documentation.

This repository is the `wiki` app itself. It contains the DocTypes, website routes, search indexing logic, sidebar rendering, and end-to-end tests that drive the user experience.

## What The App Does

Core capabilities visible in the current codebase:

1. Create and publish wiki pages.
2. Organize pages into wiki spaces and sidebar groups.
3. Track page revisions and review changes through wiki page patches.
4. Render markdown-like rich content into public website routes.
5. Search pages through Redisearch or Frappe web search fallback.
6. Manage wiki settings such as default space, logos, search bar visibility, dark mode, and sidebar display.

## Installation

```bash
# get app
bench get-app https://github.com/frappe/wiki

# install on site
bench --site sitename install-app wiki
```

If you are working in a multi-app bench, install `wiki` into the target site after Frappe is already available in the bench.

## Local Development

Typical local flow:

```bash
# from bench root
bench start
```

In another shell:

```bash
bench --site sitename migrate
bench --site sitename clear-cache
```

When editing front-end assets, keep the bench running so route and asset changes are visible quickly.

## Architecture Overview

The app is structured around a few main subsystems:

### 1. Website Routing

- `wiki/www/wiki.py` handles the `/wiki` entry route.
- It redirects users to the default wiki space configured in `Wiki Settings`.
- Individual pages are served through the website generator behavior of `Wiki Page`.

### 2. Content Model

- `Wiki Page` is the primary content record.
- `Wiki Space` groups pages into logical sections.
- `Wiki Group Item` controls sidebar grouping and ordering.
- `Wiki Page Revision` and `Wiki Page Revision Item` preserve edit history.
- `Wiki Page Patch` handles proposed edits and approval flow.

### 3. Rendering Pipeline

- `wiki/wiki/doctype/wiki_page/wiki_page.py` sanitizes HTML before save.
- Page content is converted to HTML for rendering.
- Table of contents HTML is generated from page headings when enabled in settings.
- Sidebar HTML is rendered dynamically and cached.

### 4. Search

- `wiki/wiki/doctype/wiki_page/search.py` provides page search.
- If Redisearch is disabled, the app falls back to Frappe web search.
- If Redisearch is enabled, indexes are maintained per wiki space route.

### 5. Cache Invalidation

Sidebar cache and search index rebuilds are triggered by:

- page updates
- page deletion
- wiki space updates
- wiki settings changes that affect sidebar visibility
- post-migrate hook
- hourly scheduler hook

## Repository Layout

```text
wiki/
├── wiki/
│   ├── config/
│   ├── doctype/
│   │   ├── migrate_to_wiki/
│   │   ├── wiki_group_item/
│   │   ├── wiki_page/
│   │   ├── wiki_page_patch/
│   │   ├── wiki_page_revision/
│   │   ├── wiki_page_revision_item/
│   │   ├── wiki_settings/
│   │   ├── wiki_sidebar/
│   │   └── wiki_space/
│   ├── public/
│   │   ├── js/
│   │   └── scss/
│   ├── templates/
│   └── www/
├── cypress/
│   ├── e2e/
│   └── support/
├── .github/
├── pyproject.toml
├── package.json
└── README.md
```

## Wiki Page Hierarchy

The current hierarchy is route-driven and space-driven rather than filesystem-driven.

High-level flow:

```text
Wiki Settings
  -> default_wiki_space
     -> Wiki Space
        -> wiki_sidebars
           -> Wiki Group Item entries
              -> Wiki Page records
                 -> rendered website routes
```

Sidebar and space behavior in practice:

- a wiki space owns grouped sidebar entries
- each group points to one or more wiki pages
- page routes usually live under the wiki space route
- when a space route changes, child page routes are rewritten

## Customization Notes

Current local/customized operational behavior visible in this repository:

- branch workflow assumes `staging`, `test-production`, and `version-15`
- repo automation includes agent-trigger workflows in `.github/workflows/`
- CI hardening and repo-standardization work is being added through task branches

When updating from upstream or porting changes:

1. Diff workflow files before overwriting them.
2. Preserve branch-specific automation tied to ONE-F-M deployment flow.
3. Re-check repo-root documentation after merges from upstream.

## Editing and Review Flow

The code currently supports a patch-driven edit flow:

1. A page exists as a `Wiki Page`.
2. Edits are submitted through the page update path.
3. The change becomes a `Wiki Page Patch`.
4. Draft edits stay in draft flow.
5. Review edits move through an approval path.
6. Approved content becomes part of the page and revision history.

Important implementation note:

The code clearly exposes `Draft` and `Under Review` patch states. If you are documenting or extending lifecycle behavior, do not claim an `Archived` state unless you add it to the code first.

## Testing

### Server Tests

Run app tests from the bench:

```bash
bench --site sitename run-tests --app wiki
```

Useful variants:

```bash
bench --site sitename run-tests --doctype "Wiki Page"
bench --site sitename run-tests --doctype "Wiki Space"
```

### Cypress E2E Tests

The repository already includes Cypress coverage for:

- creating a wiki page
- editing a wiki page
- deleting a wiki page
- creating a sidebar group
- deleting an empty sidebar group

Typical usage:

```bash
npx cypress open
```

or:

```bash
npx cypress run
```

## Contributing Guidelines

When contributing to this repository:

1. Keep route changes deliberate. Wiki URLs are user-facing and breaking them has documentation impact.
2. Clear or rebuild cache/index paths when changing sidebar or search logic.
3. Preserve permission checks for non-public content.
4. Keep changes to `Wiki Page`, `Wiki Space`, and patch/revision flows well-tested.
5. Update Cypress coverage if the editing or sidebar UI changes.
6. Prefer focused PRs scoped to one behavior at a time.

## Security Notes

Security-sensitive areas in this app:

- HTML sanitization in `Wiki Page.sanitize_html()`
- guest-read logic through `allow_guest`
- redirect-to-login behavior for unauthorized access
- public search endpoints that must stay aligned with page visibility

Do not bypass these paths casually. Search and rendering can become data-leak vectors if permission assumptions drift.

## CI / Automation

Current repo work includes CI additions for:

- test gating on PRs
- linting
- type checking
- coverage reporting

If a workflow change is needed, keep the branch targets aligned with the repo’s protected branch strategy:

- `staging`
- `test-production`
- `version-15`

## Screenshots

### 1. Rendered Page
<img width="1552" alt="wiki-rendered" src="https://github.com/frappe/wiki/assets/63963181/011e976e-b572-4d3a-82e8-374d26ecd0d0.png">

### 2. Edit Page
<img width="1552" alt="wiki-edit" src="https://github.com/frappe/wiki/assets/63963181/339d1422-6c99-450d-9e97-7348651abe63.png">

## Support

- GitHub Issues for bugs and feature requests
- Frappe Forum for general framework questions
- Repo-local `AGENTS.md` for operator/agent implementation context

#### License

MIT
