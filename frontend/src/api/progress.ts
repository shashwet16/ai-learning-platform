import { apiRequest } from './client'

export interface LessonProgress {
  lesson_id: string
  completed_at: string
}

export interface QuizScore {
  quiz_id: string
  lesson_id: string
  correct_count: number
  graded_count: number
}

export interface CourseProgress {
  completed_lessons: number
  total_lessons: number
  completed_lesson_ids: string[]
  quiz_scores: QuizScore[]
}

export function completeLesson(lessonId: string): Promise<LessonProgress> {
  return apiRequest<LessonProgress>(`/lessons/${lessonId}/complete`, {
    method: 'POST',
  })
}

export function getCourseProgress(courseId: string): Promise<CourseProgress> {
  return apiRequest<CourseProgress>(`/courses/${courseId}/progress`)
}
