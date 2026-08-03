# Modernization baseline

Baseline established for `establish-modernization-baseline`:

```bash
uv run pytest
```

Result: **32 passed** on Python 3.14.6 with **62%** line coverage. The suite blocks network access and uses only local fixtures and mocks. The configured 60% coverage floor is intentionally below this initial result so the regression suite can absorb small maintenance changes without masking substantial coverage loss.
