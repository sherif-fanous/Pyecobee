#!/usr/bin/env python3
"""Enforce blank lines between statements, which Ruff does not check.

Two rules are applied, each to a pair of adjacent statements in the same
block:

* a blank line is required before ``return``, ``break``, ``continue``, and
  ``raise``
* a blank line is required before and after an assignment, except between
  two consecutive assignments, which may stay packed together

A pair is skipped when either statement is a ``def`` or a ``class``, or when
the first is a docstring. Ruff already owns that spacing, through the
formatter and through D202 and D204 respectively, and enforcing it here as
well would leave the two tools undoing each other's work.

Run the checker over files or directories, and it reports each missing blank
line and exits non-zero::

    python tools/blank_lines.py pyecobee tests tools

Add ``--fix`` to insert them instead. A comment sitting directly above a
statement belongs to it, so the blank line goes above the comment::

    python tools/blank_lines.py --fix pyecobee tests tools

Run this after ``ruff check --fix``, since removing a blank line can create
work here, and follow both with ``ruff format``.
"""

from __future__ import annotations

import argparse
import ast
import sys
from itertools import pairwise
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterator

JUMP = (ast.Return, ast.Break, ast.Continue, ast.Raise)
ASSIGN = (ast.Assign, ast.AnnAssign, ast.AugAssign)
DEFINITION = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DOCUMENTABLE = (ast.Module, *DEFINITION)
SUITE_FIELDS = ("body", "orelse", "finalbody")


class Violation(NamedTuple):
    """A missing blank line between two adjacent statements.

    ``insert_at`` is the zero-based line index the blank line belongs at,
    which is not always the line just above ``line``: comments sitting
    directly above a statement belong to it and stay attached.
    """

    path: Path
    line: int
    reason: str
    insert_at: int


def first_line(node: ast.stmt) -> int:
    """Return the first physical line of *node*, decorators included."""
    decorators = getattr(node, "decorator_list", None)

    return decorators[0].lineno if decorators else node.lineno


def docstring_ids(tree: ast.Module) -> set[int]:
    """Return the ids of every docstring statement in *tree*."""
    found = set()

    for node in ast.walk(tree):
        if isinstance(node, DOCUMENTABLE) and ast.get_docstring(node) is not None:
            found.add(id(node.body[0]))

    return found


def required_padding(
    previous: ast.stmt, following: ast.stmt, previous_is_docstring: bool
) -> str | None:
    """Return why *previous* and *following* need a blank line, or ``None``."""
    if previous_is_docstring:
        return None

    if isinstance(previous, DEFINITION) or isinstance(following, DEFINITION):
        return None

    if isinstance(following, JUMP):
        return f"blank line required before {type(following).__name__.lower()}"

    previous_is_assignment = isinstance(previous, ASSIGN)
    following_is_assignment = isinstance(following, ASSIGN)

    if previous_is_assignment and following_is_assignment:
        return None

    if following_is_assignment:
        return "blank line required before assignment"

    if previous_is_assignment:
        return "blank line required after assignment"

    return None


def suites(tree: ast.Module) -> Iterator[list[ast.stmt]]:
    """Yield every statement suite in *tree*."""
    for node in ast.walk(tree):
        for field in SUITE_FIELDS:
            body = getattr(node, field, None)

            if not isinstance(body, list) or len(body) < 2:
                continue

            if all(isinstance(statement, ast.stmt) for statement in body):
                yield body


def insertion_index(lines: list[str], gap_start: int, gap_end: int) -> int:
    """Return where to insert a blank line within a gap.

    Comments directly above the following statement belong to it, so the
    blank line goes above them rather than between them and their statement.
    """
    index = gap_end

    while index > gap_start and lines[index - 1].lstrip().startswith("#"):
        index -= 1

    return index


def check(path: Path) -> list[Violation]:
    """Return every missing blank line in *path*."""
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)
    docstrings = docstring_ids(tree)
    violations = []

    for body in suites(tree):
        for previous, following in pairwise(body):
            reason = required_padding(previous, following, id(previous) in docstrings)

            if reason is None:
                continue

            gap_start = previous.end_lineno
            gap_end = first_line(following) - 1

            # Statements sharing a line, as in ``if ready: return`` or
            # ``first = 1; second = 2``, cannot be padded apart.
            if gap_end <= gap_start - 1:
                continue

            if any(not lines[index].strip() for index in range(gap_start, gap_end)):
                continue

            violations.append(
                Violation(
                    path,
                    first_line(following),
                    reason,
                    insertion_index(lines, gap_start, gap_end),
                )
            )

    return violations


def fix(path: Path, violations: list[Violation]) -> None:
    """Insert the blank lines *violations* asks for into *path*."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    for violation in sorted(violations, key=lambda item: item.insert_at, reverse=True):
        lines.insert(violation.insert_at, "\n")

    path.write_text("".join(lines), encoding="utf-8")


def python_files(targets: list[str]) -> list[Path]:
    """Expand *targets* into a sorted list of Python files."""
    found = []

    for target in targets:
        path = Path(target)

        found.extend([path] if path.is_file() else sorted(path.rglob("*.py")))

    return found


def main() -> int:
    """Check, and optionally fix, every file named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("targets", nargs="+", help="files or directories to check")
    parser.add_argument("--fix", action="store_true", help="insert missing blank lines")

    arguments = parser.parse_args()

    total = 0

    for path in python_files(arguments.targets):
        violations = check(path)

        if not violations:
            continue

        total += len(violations)

        if arguments.fix:
            fix(path, violations)

            continue

        for violation in violations:
            print(f"{violation.path}:{violation.line}: {violation.reason}")

    if not total:
        return 0

    if arguments.fix:
        print(f"Inserted {total} blank lines.")

        return 0

    print(f"\n{total} missing blank lines. Re-run with --fix.", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
