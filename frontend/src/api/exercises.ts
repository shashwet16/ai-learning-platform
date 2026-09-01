import { apiRequest } from './client'

export interface ExerciseRead {
  id: string
  lesson_id: string
  prompt: string
  starter_code: string
  order: number
}

export interface ExerciseListItem {
  id: string
  lesson_id: string
  lesson_title: string
  prompt: string
  order: number
  solved: boolean
}

export interface ExerciseSubmission {
  id: string
  exercise_id: string
  code: string
  passed: boolean
  submitted_at: string
}

export function getExerciseForLesson(lessonId: string): Promise<ExerciseRead> {
  return apiRequest<ExerciseRead>(`/exercises/${lessonId}`)
}

export function listExercises(): Promise<ExerciseListItem[]> {
  return apiRequest<ExerciseListItem[]>('/exercises')
}

// Only ever called right before grading (see ExercisePlayground) — never
// on page load. The hidden test is soft-hidden, not secret; see the
// backend schema's own docstring for the full reasoning.
export function getExerciseTestCode(
  exerciseId: string,
): Promise<{ test_code: string }> {
  return apiRequest<{ test_code: string }>(`/exercises/${exerciseId}/test-code`)
}

export function submitExercise(
  exerciseId: string,
  body: { code: string; passed: boolean },
): Promise<ExerciseSubmission> {
  return apiRequest<ExerciseSubmission>(
    `/exercises/${exerciseId}/submissions`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  )
}

export function getSubmissionHistory(
  exerciseId: string,
): Promise<ExerciseSubmission[]> {
  return apiRequest<ExerciseSubmission[]>(
    `/exercises/${exerciseId}/submissions`,
  )
}
