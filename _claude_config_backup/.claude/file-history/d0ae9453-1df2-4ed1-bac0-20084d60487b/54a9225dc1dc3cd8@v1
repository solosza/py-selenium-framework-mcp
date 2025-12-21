# Testing Conventions

Project-specific folder structures, report locations, and patterns.

## Report Location Patterns

Different project types use different conventions:

### Pattern A: Centralized Reports

All reports in one location at project root.

```
{project_root}/
  tests/
    test_*.py
  _reports/           # or tests/_reports/
    report.html
```

**When to use:** Smaller projects, single test suite, CI/CD pipelines expecting one report.

### Pattern B: Per-Layer/Component Reports

Reports next to their tests.

```
{project_root}/
  {component}/
    tests/
      test_*.py
      _reports/
        report.html
```

**When to use:** Larger projects, multiple components, want reports scoped to component.

## Project Examples

### QA Automation Framework (py_sel_framework_mcp)

**Structure:**
```
tests/
  _reports/
    report.html
  auth/
    test_login.py
  catalog/
    test_browse.py
```

**Command:**
```bash
pytest tests/ -v --html=tests/_reports/report.html --self-contained-html
```

**Convention:** Centralized reports (Pattern A).

### RAG Training Assistant (training-assistant/)

**Structure:**
```
rag/
  ingestion/
    tests/
      test_loader.py
      _reports/
        report.html
  retrieval/
    tests/
      _reports/
        report.html
```

**Command:**
```bash
pytest rag/ingestion/tests/ -v --html=rag/ingestion/tests/_reports/report.html --self-contained-html
```

**Convention:** Per-layer reports (Pattern B).

## Defect Log Location

Each project defines where defects are tracked:

| Project | Defect Log Location |
|---------|---------------------|
| py_sel_framework_mcp | `docs/DEFECT_LOG.md` |
| training-assistant | `training-assistant/docs/DEFECT_LOG.md` |

## Coverage Targets

Default targets (project can override):

| Category | Target |
|----------|--------|
| Critical paths | 100% |
| Core logic | 90%+ |
| Integration/glue | 80%+ |
| Utilities | 85%+ |

## Test Naming Conventions

```
test_{what_is_being_tested}_{expected_behavior}
```

**Examples:**
```python
test_document_creation           # Simple
test_load_file_preserves_source  # With behavior
test_skip_pycache_directories    # Edge case
```

## Adding New Project Conventions

When starting a new project, define:

1. **Report location** — Centralized or per-component?
2. **Defect log location** — Where in docs?
3. **Test folder structure** — Mirrors source or separate?
4. **Coverage requirements** — Use defaults or custom?

Document these in the project's README or CLAUDE.md.
