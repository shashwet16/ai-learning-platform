import { isValidElement, useEffect, useState } from 'react'
import Markdown, { type Components } from 'react-markdown'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getLesson, type LessonDetail } from '../api/courses'
import { MermaidDiagram } from '../components/MermaidDiagram'

const markdownComponents: Components = {
  pre({ children }) {
    // Fenced code blocks render as <pre><code className="language-x">...
    // </code></pre>. For a ```mermaid fence specifically, skip the <pre>
    // wrapper (and its code-block background/padding, meant for text)
    // entirely and render an actual diagram instead.
    if (
      isValidElement<{ className?: string; children?: unknown }>(children) &&
      children.props.className === 'language-mermaid'
    ) {
      return <MermaidDiagram chart={String(children.props.children ?? '')} />
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
