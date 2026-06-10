"""'Test the tests' guard.

Generated missions ship with a reference solution. Before any mission is
persisted, the reference solution is executed against the mission's own hidden
tests in an isolated subprocess (-I: no site-packages, no env, no cwd on path)
with a hard timeout. If the LLM wrote tests its own solution cannot pass, the
content is rejected instead of shipped — a correct student must never fail.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from ..schemas import HiddenTest

# The runner executes generated code (reference solution + assertions).
# Two layers of containment, in addition to running in a separate short-lived
# process with a hard timeout and a scrubbed environment (see below):
#   1. The reference solution is exec'd with normal builtins — it must be real
#      Python — so this process is treated as untrusted; the parent passes it
#      NO secrets and (at deployment) should sandbox its network/syscalls.
#   2. Assertions are boolean checks, so they are eval'd with a restricted
#      builtins set: common safe helpers are available, but __import__, open,
#      eval, exec, compile etc. are not — an assertion like
#      "__import__('os').system(...)" raises NameError and fails closed.
_RUNNER = """
import json, sys, traceback

_SAFE_BUILTINS = {
    name: __builtins__[name] if isinstance(__builtins__, dict) else getattr(__builtins__, name)
    for name in (
        "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "float",
        "int", "len", "list", "max", "min", "range", "reversed", "round",
        "set", "sorted", "str", "sum", "tuple", "zip", "True", "False", "None",
    )
}

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
        ok = bool(eval(expr, {"__builtins__": _SAFE_BUILTINS}, ns))
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
    # Scrub the environment: the verifier executes generated code and must
    # never see backend secrets (e.g. ANTHROPIC_API_KEY). It needs nothing
    # from the parent env beyond a PATH to locate the interpreter's libs.
    clean_env = {"PATH": os.environ.get("PATH", "")}
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", _RUNNER],
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=clean_env,
        )
    except subprocess.TimeoutExpired:
        return False, f"verification timed out after {timeout}s"
    if proc.returncode != 0:
        return False, (proc.stdout + proc.stderr).strip() or "verification failed"
    return True, None
