import { isValidElement, lazy, Suspense, useEffect, useState } from 'react'
import Markdown, { type Components } from 'react-markdown'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getLesson, type LessonDetail } from '../api/courses'
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
