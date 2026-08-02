## Context

The project has setup.py metadata, a runtime requirements.txt, ignored build output, and a devcontainer targeting old Python versions. The package is a simple setuptools-style package with `pyecobee` and `pyecobee.objects`.

## Goals / Non-Goals

**Goals:**

- Use pyproject.toml and a modern PEP 517 build.
- Make uv sync --locked the documented environment setup.
- Enforce Python 3.12+ and keep the package importable.

**Non-Goals:**

- Replace requests.
- Redesign the object model.
- Change API method behavior beyond compatibility cleanup needed for Python 3.12.

## Decisions

Use setuptools as the build backend to minimize packaging risk while using uv for resolution, synchronization, locking, and commands. Keep runtime dependencies minimal and place pytest, coverage, and Ruff in a development dependency group. Use version 2.0.0 because the supported interpreter range changes.

## Risks / Trade-offs

- [Risk] A newer build backend exposes missing package metadata. → Build and install both wheel and sdist before completion.
- [Risk] A lockfile can become stale. → CI uses `uv sync --locked` and dependency updates are intentional lockfile changes.
