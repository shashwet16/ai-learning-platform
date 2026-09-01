import { python } from '@codemirror/lang-python'
import CodeMirror from '@uiw/react-codemirror'
import { useState } from 'react'
import { getPyodide, runCode } from '../lib/pyodide'

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

    const pyodide = await getPyodide()
    setStatus('running')

    const result = await runCode(pyodide, code)
    setIsError(result.isError)
    setOutput(result.output)
    setStatus('idle')
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
