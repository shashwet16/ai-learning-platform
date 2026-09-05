import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getCourse, type CourseDetail } from '../api/courses'
import { getCourseProgress } from '../api/progress'

export function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  // Undefined (not fetched yet) is distinct from an empty Set (fetched, zero
  // lessons complete) — the checkmarks below simply render nothing extra
  // until this resolves, rather than needing a separate loading flag.
  const [completedLessonIds, setCompletedLessonIds] = useState<
    Set<string> | undefined
  >(undefined)

  useEffect(() => {
    if (!courseId) return
    getCourse(courseId)
      .then(setCourse)
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError ? err.message : 'Failed to load course.',
        )
      })
  }, [courseId])

  useEffect(() => {
    if (!courseId) return
    // Progress is a supplementary overlay on top of the course content
    // above, not core content itself — same "fetch independently, degrade
    // silently" reasoning LessonPage uses for its exercise/quiz existence
    // checks, so a progress-fetch failure doesn't block reading the course.
    getCourseProgress(courseId)
      .then((progress) =>
        setCompletedLessonIds(new Set(progress.completed_lesson_ids)),
      )
      .catch(() => undefined)
  }, [courseId])

  if (error) {
    return <p className="form-error">{error}</p>
  }

  if (course === null) {
    return <p>Loading…</p>
  }

  const totalLessons = course.modules.reduce(
    (sum, module) => sum + module.lessons.length,
    0,
  )
  const completedCount = completedLessonIds?.size ?? 0

  return (
    <div className="course-detail-page">
      <span className="kicker">Course</span>
      <h1>{course.title}</h1>
      <p className="course-detail-page__description">{course.description}</p>

      {completedLessonIds && totalLessons > 0 && (
        <div className="course-progress">
          <div className="course-progress__bar">
            <div
              className="course-progress__fill"
              style={{ width: `${(completedCount / totalLessons) * 100}%` }}
            />
          </div>
          <span className="course-progress__label">
            {completedCount} / {totalLessons} lessons complete
          </span>
        </div>
      )}

      <div className="module-list">
        {course.modules.map((module) => (
          <div key={module.id} className="module-block">
            <h2>{module.title}</h2>
            <ul className="lesson-list">
              {module.lessons.map((lesson) => (
                <li key={lesson.id}>
                  <Link to={`/lessons/${lesson.id}`}>
                    {completedLessonIds?.has(lesson.id) && (
                      <span
                        className="lesson-list__check"
                        aria-label="Completed"
                      >
                        ✓
                      </span>
                    )}
                    {lesson.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
