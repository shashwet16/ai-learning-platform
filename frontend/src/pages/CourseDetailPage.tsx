import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getCourse, type CourseDetail } from '../api/courses'

export function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

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

  if (error) {
    return <p className="form-error">{error}</p>
  }

  if (course === null) {
    return <p>Loading…</p>
  }

  return (
    <div className="course-detail-page">
      <span className="kicker">Course</span>
      <h1>{course.title}</h1>
      <p className="course-detail-page__description">{course.description}</p>

      <div className="module-list">
        {course.modules.map((module) => (
          <div key={module.id} className="module-block">
            <h2>{module.title}</h2>
            <ul className="lesson-list">
              {module.lessons.map((lesson) => (
                <li key={lesson.id}>
                  <Link to={`/lessons/${lesson.id}`}>{lesson.title}</Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
