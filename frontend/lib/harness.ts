/**
 * Builds the Python program that runs the student's code and the mission's
 * hidden tests inside Pyodide. Contract (shared with the backend verifier):
 * - student code runs in a fresh namespace, stdout captured
 * - each test assertion is a boolean expression evaluated in that namespace
 * - the program ends with `_result_json`, a JSON string Pyodide returns
 */

export interface HiddenTest {
  assertion: string;
  description: string;
}

/** Encode an arbitrary JS string as a safe Python string literal.
 * JSON string escapes are a strict subset of Python's, so JSON.stringify
 * produces a valid Python literal with no raw newlines or quote collisions. */
export function pyLiteral(value: string): string {
  return JSON.stringify(value);
}

export function buildHarnessProgram(code: string, tests: HiddenTest[]): string {
  const payload = pyLiteral(JSON.stringify({ code, tests }));
  return `
import io, json, sys, traceback

_payload = json.loads(${payload})
_result = {"output": "", "error": None, "passed": False, "results": []}
_real_stdout = sys.stdout
_buf = io.StringIO()
sys.stdout = _buf
_ns = {}
try:
    exec(_payload["code"], _ns)
except SyntaxError:
    _result["error"] = "SyntaxError: " + traceback.format_exc(limit=0).splitlines()[-1]
except Exception:
    _lines = traceback.format_exc().splitlines()
    _result["error"] = _lines[-1] if _lines else "unknown error"
finally:
    sys.stdout = _real_stdout
    _result["output"] = _buf.getvalue()

if _result["error"] is None:
    for _t in _payload["tests"]:
        try:
            _ok = bool(eval(_t["assertion"], _ns))
            _err = None
        except Exception as _exc:
            _ok = False
            _err = f"{type(_exc).__name__}: {_exc}"
        _result["results"].append(
            {"description": _t["description"], "passed": _ok, "error": _err}
        )

_result["passed"] = (
    _result["error"] is None
    and len(_result["results"]) > 0
    and all(_r["passed"] for _r in _result["results"])
)
_result_json = json.dumps(_result)
_result_json
`;
}
