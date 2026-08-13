import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../api/client'
import { listCourses, type CourseSummary } from '../api/courses'

export function CoursesPage() {
  const [courses, setCourses] = useState<CourseSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listCourses()
      .then(setCourses)
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError ? err.message : 'Failed to load courses.',
        )
      })
  }, [])

  if (error) {
    return <p className="form-error">{error}</p>
  }

  if (courses === null) {
    return <p>Loading…</p>
  }

  return (
    <div className="courses-page">
      <span className="kicker">Catalog</span>
      <h1>Courses</h1>
      <div className="course-list">
        {courses.map((course) => (
          <Link
            key={course.id}
            to={`/courses/${course.id}`}
            className="course-card"
          >
            <h2>{course.title}</h2>
            <p>{course.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
