# Wiki Agent Context

This document provides context for AI agents working with the wiki codebase.

## Project Overview

**wiki** is a documentation and knowledge management app for Frappe Framework, providing wiki-style documentation pages with markdown support, versioning, and access control.

## Tech Stack

- **Framework**: Frappe v15
- **Python**: 3.10+
- **Frontend**: Frappe UI, Vue.js
- **Markdown**: Python-Markdown with extensions
- **Database**: MariaDB 10.6+

## Repository Structure

```
wiki/
├── wiki/
│   ├── doctype/
│   │   ├── wiki_page/           # Wiki page content
│   │   ├── wiki_space/          # Wiki namespaces
│   │   ├── wiki_sidebar/        # Sidebar configuration
│   │   └── wiki_page_patch/     # Page revisions
│   ├── www/
│   │   └── wiki/                # Public wiki routes
│   ├── markdown_extensions.py   # Custom markdown processors
│   ├── search.py                # Wiki search functionality
│   └── hooks.py                 # Frappe hooks
└── README.md
```

## Key Components

### DocTypes

#### Wiki Page
- **Purpose**: Stores wiki page content
- **Fields**: route, title, content (markdown), published
- **Features**: Versioning, draft mode, approvals

#### Wiki Space
- **Purpose**: Organizes pages into namespaces
- **Fields**: space_name, route, sidebar
- **Use Case**: Separate documentation sections

#### Wiki Sidebar
- **Purpose**: Configures page navigation
- **Fields**: items (JSON), title
- **Features**: Nested structure, dynamic items

### Markdown Processing

Custom extensions in `markdown_extensions.py`:
- Wiki links: `[[Page Name]]`
- Code blocks with syntax highlighting
- Table of contents generation
- Custom CSS classes

### Search

Wiki-specific search in `search.py`:
- Full-text search across pages
- Route-based filtering
- Permission-aware results

## Architecture Patterns

### Page Rendering Flow
1. Parse route from URL
2. Load Wiki Page document
3. Convert markdown to HTML
4. Apply wiki link resolution
5. Render with sidebar

### Wiki Link Resolution
```python
def resolve_wiki_link(match):
    page_name = match.group(1)
    page = frappe.get_doc("Wiki Page", {"title": page_name})
    return f'<a href="/{page.route}">{page_name}</a>'
```

### Permission Model
- Public pages: Visible to all
- Private pages: Role-based access
- Draft pages: Only editors

## Testing Guidelines

- Use `frappe.tests.utils.FrappeTestCase`
- Test markdown rendering
- Verify wiki link resolution
- Check permission filtering
- Target 30-50% coverage

## CI/CD

- `test-on-pr.yml` - Test execution with coverage
- `linters.yml` - Code quality checks
- Coverage threshold: 30%

## Dependencies

Key dependencies:
- Frappe Framework
- Python-Markdown
- Pygments (syntax highlighting)

## Security Notes

- Sanitize markdown input
- Validate page routes
- Check permissions on every render
- Prevent XSS in custom HTML

## Common Tasks

### Adding a New Markdown Extension
1. Create processor class
2. Register in `markdown_extensions.py`
3. Add tests
4. Update documentation

### Creating Wiki Spaces
1. Define route structure
2. Configure sidebar
3. Set permissions
4. Add landing page
