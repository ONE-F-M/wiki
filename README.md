<br>
<br>

<div align="center">
<img width="150" alt="logotype" src="https://user-images.githubusercontent.com/28212972/128001084-508e446f-2814-4e1f-a5cb-09598f5a5bdc.png">
</div>

<br>

---

<div align="center">
 Wiki App built on the <a href= "https://frappeframework.com" >Frappe Framework</a> | <a href = "https://wiki-docs.frappe.cloud/use_on_frappe_cloud">Try on Frappe Cloud</a>

 \
 [![Wiki](https://img.shields.io/endpoint?url=https://cloud.cypress.io/badge/simple/w2jgcb/master&style=flat&logo=cypress)](https://cloud.cypress.io/projects/w2jgcb/runs)
 [![CI](https://github.com/frappe/wiki/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/frappe/wiki/actions/workflows/ci.yml)
</div>

## Introduction

Frappe Wiki is an Open Source [Wiki](https://en.wikipedia.org/wiki/Wiki) app built on the <a href= "https://frappeframework.com" >Frappe Framework</a>. It is well suited to serve dynamic, text-heavy content like documentation and knowledge base. It allows publishing small changes and even new pages on the fly without downtime. It also maintains revision history and has a change approval mechanism.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| Node.js | ≥ 18 |
| [Frappe Bench](https://github.com/frappe/bench) | ≥ 5.x |
| Frappe Framework | v15 |

Make sure you have a working Frappe bench set up before proceeding. Refer to the [Frappe installation guide](https://frappeframework.com/docs/user/en/installation) if needed.

---

## Installation

```bash
# get app
bench get-app https://github.com/ONE-F-M/wiki.git --branch staging

# install on site
bench --site your-site.localhost install-app wiki
```

> **Note:** Wiki's master branch does not support v13 Frappe / ERPNext.

---

## Features

1. Create Wiki Pages with rich text content
2. Author content in Markdown or Rich Text editor
3. Set-up Controlled Wiki Updates with approval workflow
4. Revision history with diff view
5. Add attachments
6. Auto-generated Table of Contents
7. Page caching for performance
8. Custom Script Support via `Wiki Settings`
9. Wiki Spaces for organising pages into groups
10. Sidebar navigation with customisable hierarchy

---

## Architecture Overview

Wiki is a Frappe website app that uses the `WebsiteGenerator` pattern to serve pages at user-defined routes.

### Core DocTypes

| DocType | Description |
|---|---|
| **Wiki Page** | Main content page — extends `WebsiteGenerator`. Stores title, content (HTML), route, and sidebar reference |
| **Wiki Page Revision** | Tracks every edit to a page. Links back to the page and stores revision items (diffs) |
| **Wiki Page Revision Item** | Child table of revision — individual diff entries |
| **Wiki Page Patch** | Proposed edits awaiting approval (contribution workflow) |
| **Wiki Sidebar** | Defines navigation tree for a group of pages |
| **Wiki Space** | Groups pages and sidebars into logical sections |
| **Wiki Group Item** | Child table for sidebar grouping |
| **Wiki Settings** | Single DocType for app-level configuration (custom scripts, approval settings) |

### Page Lifecycle

```
Draft → Published → (Edit submitted) → Wiki Page Patch → (Approved) → New Revision
```

- Any user with edit permissions can submit a **Wiki Page Patch**
- Patches are reviewed and approved via `approve()` — this creates a new **Wiki Page Revision**
- Revisions are immutable — each edit creates a new revision entry
- Diffs between revisions are computed using `ghdiff`

### Key Modules

```
wiki/
├── wiki/doctype/         # All DocType definitions and controllers
├── www/                  # WebsiteGenerator routes (wiki.py serves pages)
├── hooks.py              # App hooks (website routes, generators, permissions)
├── install.py            # Post-install setup logic
├── public/               # Static JS/CSS assets
├── templates/            # Jinja templates for page rendering
├── fixtures/             # Fixture data (Custom Fields, etc.)
├── patches/              # Data migration patches
└── config/               # Desk and website configuration
```

---

## Running Tests

```bash
bench run-tests --app wiki --failfast
```

### Cypress E2E Tests

Wiki includes Cypress end-to-end tests in the `cypress/` directory:

```bash
npx cypress run
```

---

## Contributing

Contributions are welcome! Please follow the steps below:

### 1. Fork & Clone

```bash
git clone https://github.com/ONE-F-M/wiki.git
cd wiki
git checkout -b feature/your-feature-name
```

### 2. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Pre-commit runs the following tools automatically on every commit:

| Tool | Purpose |
|---|---|
| `ruff` | Python linting & formatting |
| `prettier` | JS/CSS formatting |
| `eslint` | JavaScript linting |
| `commitlint` | Conventional commit enforcement |

### 3. Run Tests

```bash
bench run-tests --app wiki --failfast
```

### 4. Submit a Pull Request

Push your branch and open a PR against the `staging` branch on GitHub.

### Branch Workflow

| Branch | Purpose |
|---|---|
| `staging` | Integration branch — all PRs target here first |
| `test-production` | Pre-production testing |
| `version-15` | Production release branch |

### Commit Convention

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

Allowed types: `build`, `chore`, `ci`, `deprecate`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`

---

## Screenshots

### 1. Rendered Page
<img width="1552" alt="wiki-rendered" src="https://github.com/frappe/wiki/assets/63963181/011e976e-b572-4d3a-82e8-374d26ecd0d0.png">

### 2. Edit Page
<img width="1552" alt="wiki-edit" src="https://github.com/frappe/wiki/assets/63963181/339d1422-6c99-450d-9e97-7348651abe63.png">

---

#### License

MIT
