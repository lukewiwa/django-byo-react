# CLAUDE.md - AI Assistant Guide for django-byo-react

This document provides comprehensive guidance for AI assistants working with the django-byo-react codebase.

## Project Overview

**django-byo-react** is a minimalist Django package that provides a template tag for embedding React applications into Django templates. The package creates a div element for React to bind to and a Django `json_script` tag to pass props from Django to React.

- **Repository**: https://github.com/lukewiwa/django-byo-react
- **License**: MIT
- **Python Support**: 3.9+
- **Django Support**: 4.2+
- **Package Manager**: uv
- **Current Version**: 1.0.0

## Philosophy

This project follows a **minimal and unopinionated** design philosophy:
- Keep the codebase small and focused
- Remain agnostic about React implementation details
- Let users bring their own React setup
- No unnecessary abstractions or features
- Simple, clear, and maintainable code

## Repository Structure

```
django-byo-react/
├── django_byo_react/           # Main package directory
│   ├── __init__.py
│   ├── apps.py                 # Django app configuration
│   ├── templatetags/           # Template tag implementation
│   │   ├── __init__.py
│   │   └── byo_react.py       # Core template tag logic
│   └── templates/
│       └── django_byo_react/
│           └── includes/
│               └── byo_react.html  # Template that renders the div and script
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── settings.py            # Django settings for tests
│   └── test_django_byo_react.py  # Unit tests
├── .github/
│   └── workflows/
│       ├── test.yml           # CI testing workflow
│       └── release.yml        # PyPI deployment workflow
├── .devcontainer/             # VS Code dev container configuration
│   ├── Dockerfile
│   └── devcontainer.json
├── pyproject.toml             # Package configuration and dependencies
├── tox.ini                    # Multi-environment testing configuration
├── Makefile                   # Common development commands
├── MANIFEST.in                # Package distribution files
├── manage.py                  # Django management for testing
└── README.md                  # User-facing documentation
```

## Core Components

### Template Tag (django_byo_react/templatetags/byo_react.py:8-19)

The main functionality is in the `byo_react` inclusion tag:

```python
@register.inclusion_tag("django_byo_react/includes/byo_react.html")
def byo_react(id=None, component_name=None, className="", **kwargs):
    if id is None:
        id = uuid.uuid4()
    script_id = uuid.uuid4()
    return {
        "component_name": component_name,
        "element_id": id,
        "script_id": script_id,
        "className": className.strip(),
        "props": kwargs,
    }
```

Key features:
- Accepts optional `id` for the div element (auto-generates UUID if not provided)
- Accepts optional `component_name` for reusable components
- Accepts `className` for CSS classes
- Accepts arbitrary `**kwargs` that become React props
- Generates unique `script_id` for linking div to JSON script

### Template (django_byo_react/templates/django_byo_react/includes/byo_react.html:1-7)

Renders the HTML output:
- JSON script tag using Django's `json_script` filter
- Div element with data attributes linking to the script
- Optional component name and className attributes

## Development Workflow

### Environment Setup

This project uses **uv** for dependency management:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Activate virtual environment (if needed)
source .venv/bin/activate
```

### Running Tests

Tests use **tox** for multi-environment testing across Python and Django versions:

```bash
# Run all tests across all environments
make test
# or
uv run tox

# Run specific environment
uv run tox -e py311-django51

# Run linting only
uv run tox -e py39-lint
```

Test environments (tox.ini:4-9):
- `py39-django42` - Python 3.9 + Django 4.2
- `py310-django{42,50,51}` - Python 3.10 + Django 4.2/5.0/5.1
- `py311-django{42,50,51}` - Python 3.11 + Django 4.2/5.0/5.1
- `py312-django{42,50,51}` - Python 3.12 + Django 4.2/5.0/5.1
- `py39-lint` - Code quality checks (ruff)

### Code Quality

**Ruff** is used for both linting and formatting:

```bash
# Format code
uv run ruff format .

# Check formatting
uv run ruff format --check .

# Run linter
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

**Pyright** is used for type checking:

```bash
uv run pyright
```

Configuration:
- Ruff: Follows Black's formatting style (max line length: 88)
- Pyright: Basic type checking mode (pyproject.toml:29-30)

### Building and Deployment

```bash
# Build package
make build
# or
uvx --from build pyproject-build --installer uv

# Deploy to PyPI (local)
make deploy
# or
uvx twine upload dist/*
```

### CI/CD Workflows

**Test Workflow** (.github/workflows/test.yml):
- Runs on every push
- Uses custom Docker container with multiple Python versions
- Installs sqlite3 dependency
- Runs `make test` (tox)

**Release Workflow** (.github/workflows/release.yml):
- Triggers on GitHub releases or manual dispatch
- Runs tests first
- Builds package
- Publishes to PyPI using trusted publishing (no manual credentials)

## Development Guidelines for AI Assistants

### Code Changes

When modifying code:

1. **Read First**: Always read existing code before suggesting changes
2. **Test Coverage**: Ensure changes are covered by tests
3. **Run Tests**: Always run `make test` after changes
4. **Type Annotations**: Use type hints where they add clarity
5. **Formatting**: Run `uv run ruff format .` before committing
6. **Linting**: Ensure `uv run ruff check .` passes

### Testing Guidelines

When writing tests (tests/test_django_byo_react.py):

1. Use Django's `TestCase` class
2. Test template rendering with `render_template` helper
3. Mock UUIDs for deterministic testing (see examples in test file)
4. Use `assertInHTML` for HTML comparison (ignores whitespace)
5. Test all parameter combinations (id, component_name, className, props)
6. Test different prop types (bool, string, dict)

### Adding Features

Before adding features, consider:

1. **Necessity**: Does this align with the minimal philosophy?
2. **User Impact**: Does this break existing usage patterns?
3. **Complexity**: Is this the simplest implementation?
4. **Tests**: Can this be thoroughly tested?
5. **Documentation**: Does README need updates?

The project intentionally avoids:
- Complex React integration
- Build tooling
- Webpack/bundler configuration
- Frontend dependencies
- Opinionated patterns

### Common Tasks

**Adding a new template tag parameter:**
1. Add parameter to `byo_react()` function signature
2. Add to context dict returned by function
3. Update template to use the parameter
4. Add tests for the new parameter
5. Update README.md with usage example

**Updating Django/Python support:**
1. Update `requires-python` in pyproject.toml
2. Update tox.ini environment list
3. Test locally with `make test`
4. Update README if needed

**Fixing bugs:**
1. Write a failing test that demonstrates the bug
2. Fix the bug
3. Ensure test passes
4. Run full test suite
5. Update documentation if behavior changed

### Git Workflow

**Branch naming:**
- Feature branches should follow: `claude/feature-description-{session_id}`
- Current branch: `claude/add-claude-documentation-Fk8A8`

**Commit messages:**
- Use clear, descriptive messages
- Focus on "why" not "what"
- Follow existing style (see `git log`)
- Include session URL in commits

**Pushing:**
```bash
git push -u origin claude/add-claude-documentation-Fk8A8
```

### Files to Never Modify

- `LICENSE` - Legal document, requires owner approval
- `uv.lock` - Auto-generated, managed by uv
- `.git/` - Git internals
- `__pycache__/` - Python cache
- `dist/` - Build artifacts
- `.tox/` - Test environment cache

### Files That Rarely Change

- `MANIFEST.in` - Only if adding new file types to distribution
- `.gitignore` - Only if new tools create new artifacts
- `.devcontainer/` - Only for development environment changes
- `manage.py` - Django boilerplate, rarely needs updates

### Key Files to Understand

1. **django_byo_react/templatetags/byo_react.py** - Core logic
2. **django_byo_react/templates/django_byo_react/includes/byo_react.html** - Output template
3. **tests/test_django_byo_react.py** - Test suite
4. **pyproject.toml** - Package metadata and dependencies
5. **tox.ini** - Test environment configuration

## Package Distribution

The package is distributed via PyPI:
- Package name: `django-byo-react`
- Installation: `pip install django-byo-react`
- Built with: hatchling
- Includes: Python files, templates, README, LICENSE (via MANIFEST.in)

## Development Container

A devcontainer is provided for VS Code:
- Based on Python 3 image
- Configured for Django development
- Includes extensions: Pylance, Ruff, GitLens, Django support
- Format on save enabled
- Type checking: basic mode
- Environment variables for cache directories

## Troubleshooting

**Tests failing:**
- Check Python version: `python --version`
- Ensure dependencies installed: `uv sync`
- Check Django compatibility in tox.ini
- Review test output for specific failures

**Import errors:**
- Ensure package installed: `uv sync`
- Check PYTHONPATH includes project root
- Verify app in INSTALLED_APPS (tests/settings.py)

**Type checking errors:**
- Install django-types: `uv add --dev django-types`
- Check pyproject.toml for pyright configuration
- Use `# type: ignore` sparingly and with comments

**Build failures:**
- Ensure all files in MANIFEST.in exist
- Check pyproject.toml syntax
- Verify build backend (hatchling) is specified

## Questions and Decisions

When uncertain:

1. **Check existing patterns**: Look at existing code first
2. **Consult README**: User documentation reflects design intent
3. **Review tests**: Tests show expected behavior
4. **Check git history**: `git log` shows evolution and reasoning
5. **Ask the user**: When truly ambiguous, ask rather than assume

## Resources

- Django Template Tags: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/
- uv documentation: https://github.com/astral-sh/uv
- Ruff documentation: https://docs.astral.sh/ruff/
- Tox documentation: https://tox.wiki/

## Summary

This is a focused, minimal package with a clear purpose. When working with this codebase:
- Prioritize simplicity and clarity
- Maintain backwards compatibility
- Test thoroughly across supported versions
- Keep documentation in sync with code
- Respect the "bring your own React" philosophy
