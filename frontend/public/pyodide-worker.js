/* Pyodide Web Worker: receives { id, program }, runs the program, replies with
 * { id, ok, resultJson | error }. The program is built by lib/harness.ts and
 * ends with a JSON string expression. */
importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js");

const pyodideReady = loadPyodide({
  indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
});

self.onmessage = async (event) => {
  const { id, program } = event.data;
  try {
    const pyodide = await pyodideReady;
    const resultJson = await pyodide.runPythonAsync(program);
    self.postMessage({ id, ok: true, resultJson });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err) });
  }
};
