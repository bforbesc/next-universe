"""'Test the tests' guard.

Generated missions ship with a reference solution. Before any mission is
persisted, the reference solution is executed against the mission's own hidden
tests in an isolated subprocess (-I: no site-packages, no env, no cwd on path)
with a hard timeout. If the LLM wrote tests its own solution cannot pass, the
content is rejected instead of shipped — a correct student must never fail.
"""
from __future__ import annotations

import json
import subprocess
import sys

from ..schemas import HiddenTest

_RUNNER = """
import json, sys, traceback

payload = json.load(sys.stdin)
ns = {}
try:
    exec(payload["solution"], ns)
except Exception:
    print("solution crashed:\\n" + traceback.format_exc())
    sys.exit(1)

failures = []
for expr, description in payload["tests"]:
    try:
        ok = bool(eval(expr, ns))
    except Exception as exc:
        ok = False
        description = f"{description} ({type(exc).__name__}: {exc})"
    if not ok:
        failures.append(description)

if failures:
    print("failed checks: " + "; ".join(failures))
    sys.exit(1)
"""


def verify_program(
    solution: str, tests: list[HiddenTest], timeout: float = 5.0
) -> tuple[bool, str | None]:
    """Run `solution` and evaluate each test assertion in its namespace.

    Returns (ok, error). Assertions are boolean Python expressions — the same
    contract the in-browser Pyodide runner uses for student code.
    """
    payload = json.dumps(
        {"solution": solution, "tests": [[t.assertion, t.description] for t in tests]}
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", _RUNNER],
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"verification timed out after {timeout}s"
    if proc.returncode != 0:
        return False, (proc.stdout + proc.stderr).strip() or "verification failed"
    return True, None
