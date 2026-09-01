import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listExercises, type ExerciseListItem } from '../api/exercises'
import { ApiError } from '../api/client'

export function PracticePage() {
  const [exercises, setExercises] = useState<ExerciseListItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listExercises()
      .then(setExercises)
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError ? err.message : 'Failed to load exercises.',
        )
      })
  }, [])

  if (error) {
    return <p className="form-error">{error}</p>
  }

  if (exercises === null) {
    return <p>Loading…</p>
  }

  return (
    <div className="practice-page">
      <span className="kicker">Practice</span>
      <h1>Coding exercises</h1>
      {exercises.length === 0 ? (
        <p className="practice-page__empty">
          No coding exercises yet — check back as more lessons add them.
        </p>
      ) : (
        <ul className="practice-list">
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <Link
                to={`/lessons/${exercise.lesson_id}`}
                className="practice-row"
              >
                <span
                  className={
                    exercise.solved
                      ? 'exercise-status exercise-status--passed'
                      : 'practice-row__unsolved'
                  }
                >
                  {exercise.solved ? '✓ Solved' : 'Unsolved'}
                </span>
                <span className="practice-row__prompt">{exercise.prompt}</span>
                <span className="practice-row__lesson">
                  {exercise.lesson_title}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
