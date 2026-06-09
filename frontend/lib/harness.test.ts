/**
 * The harness builder turns (student code + hidden tests) into one Python
 * program that Pyodide runs in a Web Worker. These tests execute the generated
 * program with real CPython so the in-browser semantics are verified to match
 * the backend's content verifier: same namespace model, same boolean-expression
 * assertion contract.
 */
import { execFileSync } from "node:child_process";
import { describe, expect, it } from "vitest";

import { buildHarnessProgram } from "./harness";

interface HarnessResult {
  output: string;
  error: string | null;
  passed: boolean;
  results: { description: string; passed: boolean; error: string | null }[];
}

function runWithCPython(program: string): HarnessResult {
  const stdout = execFileSync("python3", ["-I", "-c", `${program}\nprint(_result_json)`], {
    encoding: "utf-8",
    timeout: 10_000,
  });
  return JSON.parse(stdout.trim());
}

const TESTS = [
  { assertion: "oxygen_level == 100", description: "oxygen restored" },
  { assertion: 'ship_name == "Wanderer"', description: "ship named" },
];

describe("buildHarnessProgram", () => {
  it("passes when the code satisfies every hidden test", () => {
    const result = runWithCPython(
      buildHarnessProgram('oxygen_level = 100\nship_name = "Wanderer"', TESTS),
    );
    expect(result.passed).toBe(true);
    expect(result.error).toBeNull();
    expect(result.results).toHaveLength(2);
    expect(result.results.every((r) => r.passed)).toBe(true);
  });

  it("fails the right test and keeps its story description", () => {
    const result = runWithCPython(buildHarnessProgram("oxygen_level = 50", TESTS));
    expect(result.passed).toBe(false);
    expect(result.results[0]).toMatchObject({ description: "oxygen restored", passed: false });
    // second test references an undefined name -> failed with error, not crash
    expect(result.results[1].passed).toBe(false);
    expect(result.results[1].error).toContain("NameError");
  });

  it("captures stdout so students can print-debug", () => {
    const result = runWithCPython(
      buildHarnessProgram('print("checking", 1 + 1)\noxygen_level = 100\nship_name = "Wanderer"', TESTS),
    );
    expect(result.output).toContain("checking 2");
    expect(result.passed).toBe(true);
  });

  it("reports a crash as a friendly error instead of failing silently", () => {
    const result = runWithCPython(buildHarnessProgram('raise ValueError("boom")', TESTS));
    expect(result.passed).toBe(false);
    expect(result.error).toContain("ValueError");
    expect(result.error).toContain("boom");
  });

  it("reports syntax errors", () => {
    const result = runWithCPython(buildHarnessProgram("oxygen_level = = 100", TESTS));
    expect(result.passed).toBe(false);
    expect(result.error).toContain("SyntaxError");
  });

  it("survives hostile code content: quotes, backslashes, triple quotes, unicode", () => {
    const evil = 'x = """tri\\"ple"""\ny = \'qu"ote\'\nz = "emoji 🚀 \\\\ backslash"\noxygen_level = 100\nship_name = "Wanderer"';
    const result = runWithCPython(buildHarnessProgram(evil, TESTS));
    expect(result.error).toBeNull();
    expect(result.passed).toBe(true);
  });

  it("never lets student code fake a result (tests run even after sys tampering)", () => {
    const result = runWithCPython(
      buildHarnessProgram("import sys\nsys.stdout = None\noxygen_level = 1", TESTS),
    );
    expect(result.passed).toBe(false);
    expect(result.results[0].passed).toBe(false);
  });

  it("an empty test list never counts as a pass", () => {
    const result = runWithCPython(buildHarnessProgram("x = 1", []));
    expect(result.passed).toBe(false);
  });
});
