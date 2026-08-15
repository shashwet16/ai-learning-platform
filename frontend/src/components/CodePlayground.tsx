import { python } from '@codemirror/lang-python'
import CodeMirror from '@uiw/react-codemirror'
import { useState } from 'react'
import type { PyodideAPI } from 'pyodide'

const PYODIDE_INDEX_URL = 'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/'

let pyodidePromise: Promise<PyodideAPI> | null = null

function getPyodide(): Promise<PyodideAPI> {
  // Module-level singleton, same idea as MermaidDiagram's isInitialized
  // flag — but more important here, since Pyodide's payload (the
  // WebAssembly runtime plus a full CPython standard library) is tens of
  // MB, far larger than Mermaid. Every CodePlayground on a page shares one
  // loading promise instead of each fetching its own copy. And unlike
  // Mermaid (loaded as soon as the component mounts), this import only
  // happens on first "Run" click — a learner reading a lesson with an
  // embedded playground they never run should never pay that download.
  if (!pyodidePromise) {
    pyodidePromise = import('pyodide').then(({ loadPyodide }) =>
      loadPyodide({ indexURL: PYODIDE_INDEX_URL }),
    )
  }
  return pyodidePromise
}

// Computed once at module load, not per render/keystroke — the color
// scheme preference doesn't change mid-session, so there's no reason to
// re-query matchMedia() on every CodeMirror onChange.
const editorTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
  ? 'dark'
  : 'light'

interface CodePlaygroundProps {
  code: string
}

export function CodePlayground({ code: initialCode }: CodePlaygroundProps) {
  const [code, setCode] = useState(initialCode)
  const [output, setOutput] = useState<string | null>(null)
  const [isError, setIsError] = useState(false)
  const [status, setStatus] = useState<'idle' | 'loading-runtime' | 'running'>(
    'idle',
  )

  async function handleRun() {
    setOutput(null)
    setIsError(false)
    setStatus('loading-runtime')

    // Declared outside the try block, not inside: a script can legitimately
    // print several lines *before* raising an exception (e.g. line 3 prints
    // fine, line 4 divides by zero), and the catch block below needs to
    // show that output ahead of the traceback — a real terminal wouldn't
    // discard it just because the process eventually crashed.
    let buffer = ''

    try {
      const pyodide = await getPyodide()
      setStatus('running')

      // Redirected per run, not once at load time: each run should only
      // capture output from *that* run, and re-setting these right before
      // execution keeps a fresh buffer even if a previous run's promise is
      // still settling (state update below is keyed off this closure's
      // own buffer, not shared mutable module state).
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

      await pyodide.runPythonAsync(code)
      setOutput(buffer || '(no output)')
    } catch (err) {
      // A Python-side exception surfaces here as a PythonError whose
      // `.message` is the real CPython traceback text (not a JS stack
      // trace) — that's the point of running actual Python, not a
      // reimplementation, and it's what the roadmap's own test method
      // checks for. Any stdout printed before the exception is prepended,
      // matching what a real terminal would show.
      setIsError(true)
      const traceback =
        err instanceof Error ? err.message : 'Failed to run code.'
      setOutput(buffer ? `${buffer}\n${traceback}` : traceback)
    } finally {
      setStatus('idle')
    }
  }

  const runLabel =
    status === 'loading-runtime'
      ? 'Starting Python…'
      : status === 'running'
        ? 'Running…'
        : 'Run'

  return (
    <div className="code-playground">
      <CodeMirror
        value={code}
        onChange={setCode}
        extensions={[python()]}
        theme={editorTheme}
        basicSetup={{ lineNumbers: true, foldGutter: false }}
      />
      <div className="code-playground__actions">
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleRun}
          disabled={status !== 'idle'}
        >
          {runLabel}
        </button>
        {status === 'loading-runtime' && (
          <span className="code-playground__hint">
            First run downloads the Python runtime — this can take a few
            seconds.
          </span>
        )}
      </div>
      {output !== null && (
        <pre
          className={
            isError
              ? 'code-playground__output code-playground__output--error'
              : 'code-playground__output'
          }
        >
          {output}
        </pre>
      )}
    </div>
  )
}
