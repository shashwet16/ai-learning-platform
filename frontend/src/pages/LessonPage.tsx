import { isValidElement, lazy, Suspense, useEffect, useState } from 'react'
import Markdown, { type Components } from 'react-markdown'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getLesson, type LessonDetail } from '../api/courses'
import { getExerciseForLesson, type ExerciseRead } from '../api/exercises'
import { completeLesson } from '../api/progress'
import { getQuizForLesson } from '../api/quiz'
import { MermaidDiagram } from '../components/MermaidDiagram'

// Lazy, not a static import: CodePlayground pulls in CodeMirror + the
// Python language grammar, which together add ~470KB raw / ~157KB gzip —
// bundling that into the main chunk (measured via `npm run build`: main
// chunk jumped from 361KB to 832KB raw) would tax every page, including
// lessons with no playground at all. React.lazy defers fetching the whole
// component — not just the Pyodide runtime inside it, which is separately
// deferred until "Run" is clicked — until a lesson actually renders one.
const CodePlayground = lazy(() =>
  import('../components/CodePlayground').then((m) => ({
    default: m.CodePlayground,
  })),
)

// Same reasoning, same fix — ExercisePlayground also pulls in CodeMirror.
// Rendering it is gated on `exercise` actually resolving to a real row
// (see the fetch below), so lessons with no attached exercise never even
// mount this lazy boundary, let alone fetch CodeMirror's chunk.
const ExercisePlayground = lazy(() =>
  import('../components/ExercisePlayground').then((m) => ({
    default: m.ExercisePlayground,
  })),
)

const markdownComponents: Components = {
  pre({ children }) {
    // Fenced code blocks render as <pre><code className="language-x">...
    // </code></pre>. A ```mermaid fence renders a diagram; a
    // ```python-playground fence renders a runnable editor. Both skip the
    // <pre> wrapper (and its code-block background/padding, meant for
    // plain text) entirely.
    if (isValidElement<{ className?: string; children?: unknown }>(children)) {
      const { className, children: fenceContent } = children.props
      if (className === 'language-mermaid') {
        return <MermaidDiagram chart={String(fenceContent ?? '')} />
      }
      if (className === 'language-python-playground') {
        return (
          <Suspense fallback={<div className="code-playground-loading" />}>
            <CodePlayground code={String(fenceContent ?? '')} />
          </Suspense>
        )
      }
    }
    return <pre>{children}</pre>
  },
}

export function LessonPage() {
  const { lessonId } = useParams<{ lessonId: string }>()
  const navigate = useNavigate()
  const [lesson, setLesson] = useState<LessonDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [exercise, setExercise] = useState<ExerciseRead | null>(null)
  const [hasQuiz, setHasQuiz] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)

  useEffect(() => {
    if (!lessonId) return
    // Reset before fetching, not after — otherwise clicking "next lesson"
    // would keep showing the previous lesson's content while the new one
    // is still loading, since `lesson` would still hold the old value.
    setLesson(null)
    setError(null)
    getLesson(lessonId)
      .then(setLesson)
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError ? err.message : 'Failed to load lesson.',
        )
      })
  }, [lessonId])

  useEffect(() => {
    if (!lessonId) return
    // Independent of the lesson-content fetch above, and deliberately
    // silent on failure: most lessons have no attached exercise at all,
    // and a 404 here (exercise_not_found) is the expected, common case —
    // not an error worth surfacing. Any other failure degrades the same
    // way, since this is a supplementary feature, not core lesson content.
    setExercise(null)
    getExerciseForLesson(lessonId)
      .then(setExercise)
      .catch(() => undefined)
  }, [lessonId])

  useEffect(() => {
    if (!lessonId) return
    // Same "most lessons have neither" reasoning as the exercise fetch
    // above — a 404 (quiz_not_found) is the expected common case, not an
    // error. Only the existence matters here; QuizPage does its own fetch
    // of the full quiz once the learner actually navigates to it.
    setHasQuiz(false)
    getQuizForLesson(lessonId)
      .then(() => setHasQuiz(true))
      .catch(() => undefined)
  }, [lessonId])

  useEffect(() => {
    // Reset on navigation, same as the states above. Deliberately not
    // pre-fetched from the course's progress data: this page doesn't know
    // its own course id, and re-marking an already-completed lesson is a
    // harmless no-op server-side (M6.2), so the only real cost of skipping
    // a "was this already done" check is the button briefly re-offering
    // itself on a lesson you'd previously completed.
    setIsCompleted(false)
  }, [lessonId])

  async function handleMarkComplete() {
    if (!lessonId) return
    setIsCompleting(true)
    try {
      await completeLesson(lessonId)
      setIsCompleted(true)
    } catch {
      // Best-effort: progress tracking is supplementary, not required to
      // keep reading, so a failed request just leaves the button clickable
      // again rather than surfacing a blocking error over lesson content.
    } finally {
      setIsCompleting(false)
    }
  }

  if (error) {
    return <p className="form-error">{error}</p>
  }

  if (lesson === null) {
    return <p>Loading…</p>
  }

  return (
    <div className="lesson-page">
      <button type="button" className="back-link" onClick={() => navigate(-1)}>
        ← Back to course
      </button>

      <article className="prose">
        <Markdown components={markdownComponents}>{lesson.body}</Markdown>
      </article>

      {exercise && (
        <Suspense fallback={<div className="code-playground-loading" />}>
          <ExercisePlayground exercise={exercise} />
        </Suspense>
      )}

      {hasQuiz && (
        <Link
          to={`/lessons/${lessonId}/quiz`}
          className="btn btn-quiet lesson-quiz-link"
        >
          Take the quiz →
        </Link>
      )}

      <button
        type="button"
        className="btn btn-quiet lesson-complete-btn"
        onClick={handleMarkComplete}
        disabled={isCompleting || isCompleted}
      >
        {isCompleted
          ? '✓ Marked complete'
          : isCompleting
            ? 'Marking…'
            : 'Mark lesson complete'}
      </button>

      <nav className="lesson-nav">
        {lesson.prev_lesson_id ? (
          <Link
            to={`/lessons/${lesson.prev_lesson_id}`}
            className="btn btn-quiet"
          >
            ← Previous
          </Link>
        ) : (
          <span />
        )}
        {lesson.next_lesson_id && (
          <Link
            to={`/lessons/${lesson.next_lesson_id}`}
            className="btn btn-primary"
          >
            Next lesson →
          </Link>
        )}
      </nav>
    </div>
  )
}
