import { python } from '@codemirror/lang-python'
import CodeMirror from '@uiw/react-codemirror'
import { useEffect, useState } from 'react'
import {
  getExerciseTestCode,
  getSubmissionHistory,
  submitExercise,
  type ExerciseRead,
} from '../api/exercises'
import { getPyodide, runCode } from '../lib/pyodide'

const editorTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
  ? 'dark'
  : 'light'

interface ExercisePlaygroundProps {
  exercise: ExerciseRead
}

export function ExercisePlayground({ exercise }: ExercisePlaygroundProps) {
  const [code, setCode] = useState(exercise.starter_code)
  const [output, setOutput] = useState<string | null>(null)
  const [isError, setIsError] = useState(false)
  const [action, setAction] = useState<'idle' | 'running' | 'submitting'>(
    'idle',
  )
  const [lastResult, setLastResult] = useState<{
    passed: boolean
    submittedAt: string
  } | null>(null)

  useEffect(() => {
    // Load-bearing for the roadmap's own test method ("refresh, confirm
    // the most recent result is still shown") — without this, a page
    // reload would always show "not yet attempted" even for an exercise
    // already solved in a previous session.
    getSubmissionHistory(exercise.id)
      .then((history) => {
        if (history.length === 0) return
        const latest = history[history.length - 1]
        setLastResult({
          passed: latest.passed,
          submittedAt: latest.submitted_at,
        })
      })
      .catch(() => {
        // Non-critical: if history fails to load (network hiccup, expired
        // session), the exercise is still fully usable — it just starts
        // without a persisted-status badge instead of blocking the page.
      })
  }, [exercise.id])

  async function handleRun() {
    setOutput(null)
    setIsError(false)
    setAction('running')
    const pyodide = await getPyodide()
    const result = await runCode(pyodide, code)
    setIsError(result.isError)
    setOutput(result.output)
    setAction('idle')
  }

  async function handleSubmit() {
    setOutput(null)
    setIsError(false)
    setAction('submitting')

    const pyodide = await getPyodide()
    // test_code is fetched here, at the moment of submission — not on
    // mount, and never bundled into the exercise the page already has.
    // See the backend schema's docstring: this is a soft-hidden test,
    // fetched only when actually needed, not a truly secret one.
    const { test_code: testCode } = await getExerciseTestCode(exercise.id)

    // Run the learner's code and the hidden test in the same Pyodide
    // global namespace, in one call — the test can reference whatever
    // the learner's code defined, exactly like a real unit test would.
    const result = await runCode(pyodide, `${code}\n\n${testCode}`)
    setIsError(result.isError)
    setOutput(result.isError ? result.output : 'All tests passed.')

    try {
      const submission = await submitExercise(exercise.id, {
        code,
        passed: !result.isError,
      })
      setLastResult({
        passed: submission.passed,
        submittedAt: submission.submitted_at,
      })
    } catch {
      // The local pass/fail result above is still shown even if
      // persisting it failed — only the "last submitted" badge won't
      // update.
    }

    setAction('idle')
  }

  const isBusy = action !== 'idle'
  const runLabel = action === 'running' ? 'Running…' : 'Run'
  const submitLabel = action === 'submitting' ? 'Checking…' : 'Submit'

  return (
    <div className="exercise-playground">
      <div className="exercise-playground__prompt">
        <span className="exercise-playground__kicker">Exercise</span>
        <p>{exercise.prompt}</p>
        {lastResult && (
          <span
            className={
              lastResult.passed
                ? 'exercise-status exercise-status--passed'
                : 'exercise-status exercise-status--failed'
            }
          >
            {lastResult.passed ? '✓ Solved' : '✗ Last attempt failed'}
          </span>
        )}
      </div>
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
            className="btn btn-quiet"
            onClick={handleRun}
            disabled={isBusy}
          >
            {runLabel}
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={isBusy}
          >
            {submitLabel}
          </button>
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
    </div>
  )
}
