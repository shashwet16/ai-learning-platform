import { apiRequest } from './client'

export interface CourseSummary {
  id: string
  title: string
  description: string
  created_at: string
}

export interface LessonSummary {
  id: string
  title: string
  order: number
}

export interface ModuleSummary {
  id: string
  title: string
  order: number
  lessons: LessonSummary[]
}

export interface CourseDetail extends CourseSummary {
  modules: ModuleSummary[]
}

export interface LessonDetail {
  id: string
  title: string
  body: string
  order: number
  module_id: string
  prev_lesson_id: string | null
  next_lesson_id: string | null
}

export function listCourses(): Promise<CourseSummary[]> {
  return apiRequest<CourseSummary[]>('/courses')
}

export function getCourse(courseId: string): Promise<CourseDetail> {
  return apiRequest<CourseDetail>(`/courses/${courseId}`)
}

export function getLesson(lessonId: string): Promise<LessonDetail> {
  return apiRequest<LessonDetail>(`/lessons/${lessonId}`)
}
