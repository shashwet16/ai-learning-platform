import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listCourses, type CourseSummary } from '../api/courses'
import { getCourseProgress, type CourseProgress } from '../api/progress'
import { useAuth } from '../context/AuthContext'

interface CourseWithProgress {
  course: CourseSummary
  progress: CourseProgress | null
}

export function DashboardPage() {
  const { user } = useAuth()
  const [rows, setRows] = useState<CourseWithProgress[] | null>(null)

  useEffect(() => {
    listCourses().then((courses) => {
      // There's no per-user enrollment model in this app — every course is
      // visible to every learner — so "your courses" here means all of
      // them. One progress request per course (there's no batched
      // all-courses endpoint, since M6.3 only specifies a per-course one);
      // acceptable at this catalog's size, same honest tradeoff M3.9 made
      // for Pyodide's download cost. A progress fetch failing for one
      // course degrades to "no progress shown" for that card rather than
      // failing the whole dashboard.
      Promise.all(
        courses.map((course) =>
          getCourseProgress(course.id)
            .then((progress): CourseWithProgress => ({ course, progress }))
            .catch((): CourseWithProgress => ({ course, progress: null })),
        ),
      ).then(setRows)
    })
  }, [])

  return (
    <div className="dashboard-page">
      <span className="kicker">Dashboard</span>
      <h1>Welcome back.</h1>
      {user && (
        <p className="dashboard-page__subtitle">
          You're signed in as {user.email}.
        </p>
      )}

      <div className="dashboard-page__actions">
        <Link to="/practice" className="btn btn-quiet">
          Practice exercises
        </Link>
        <Link to="/chat" className="btn btn-quiet">
          Chat with your AI tutor
        </Link>
      </div>

      {rows === null ? (
        <p>Loading…</p>
      ) : (
        <div className="dashboard-course-list">
          {rows.map(({ course, progress }) => {
            const total = progress?.total_lessons ?? 0
            const completed = progress?.completed_lessons ?? 0
            const percent = total > 0 ? (completed / total) * 100 : 0

            return (
              <Link
                key={course.id}
                to={`/courses/${course.id}`}
                className="dashboard-course-card"
              >
                <h2>{course.title}</h2>
                <p>{course.description}</p>
                {progress && total > 0 && (
                  <>
                    <div className="course-progress">
                      <div className="course-progress__bar">
                        <div
                          className="course-progress__fill"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <span className="course-progress__label">
                        {completed} / {total} lessons complete
                      </span>
                    </div>
                    {progress.quiz_scores.length > 0 && (
                      <p className="dashboard-course-card__quiz-scores">
                        Best quiz scores:{' '}
                        {progress.quiz_scores
                          .map((q) => `${q.correct_count}/${q.graded_count}`)
                          .join(', ')}
                      </p>
                    )}
                  </>
                )}
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
