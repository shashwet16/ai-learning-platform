import type { PyodideAPI } from 'pyodide'

const PYODIDE_INDEX_URL = 'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/'

let pyodidePromise: Promise<PyodideAPI> | null = null

export function getPyodide(): Promise<PyodideAPI> {
  // Module-level singleton, shared by every consumer (the ungraded
  // playground and the graded exercise playground both call this) —
  // Pyodide's payload (WebAssembly runtime + full CPython stdlib) is tens
  // of MB, so a lesson with both an ungraded snippet and a graded exercise
  // must only ever download it once. Deferred until first call, not
  // imported at module load, for the same reason: a lesson with neither
  // should never pay this cost at all.
  if (!pyodidePromise) {
    pyodidePromise = import('pyodide').then(({ loadPyodide }) =>
      loadPyodide({ indexURL: PYODIDE_INDEX_URL }),
    )
  }
  return pyodidePromise
}

export interface RunResult {
  output: string
  isError: boolean
}

/**
 * Runs `code` against an already-loaded Pyodide instance, capturing
 * stdout/stderr exactly as a real terminal would — including output
 * printed before an eventual exception (see M3.9: an earlier version
 * discarded pre-exception output because its buffer lived inside the
 * `try` block; this version declares it outside so the catch path can
 * still see it).
 */
export async function runCode(
  pyodide: PyodideAPI,
  code: string,
): Promise<RunResult> {
  let buffer = ''

  pyodide.setStdout({
    batched: (text) => {
      buffer += buffer ? `\n${text}` : text
    },
  })
  pyodide.setStderr({
    batched: (text) => {
      buffer += buffer ? `\n${text}` : text
    },
  })

  try {
    await pyodide.runPythonAsync(code)
    return { output: buffer || '(no output)', isError: false }
  } catch (err) {
    // A Python-side exception surfaces here as a PythonError whose
    // `.message` is the real CPython traceback text.
    const traceback = err instanceof Error ? err.message : 'Failed to run code.'
    return {
      output: buffer ? `${buffer}\n${traceback}` : traceback,
      isError: true,
    }
  }
}
