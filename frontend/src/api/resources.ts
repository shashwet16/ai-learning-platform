import { apiRequest } from './client'

export type ResourceType =
  'official_docs' | 'article' | 'video' | 'paper' | 'repo' | 'interactive'

export interface Resource {
  id: string
  lesson_id: string
  title: string
  url: string
  description: string
  resource_type: ResourceType
  order: number
}

// Always resolves to an array (possibly empty) — the backend never 404s
// here, since "no resources curated yet" is a valid, unremarkable state
// for a lesson, not a missing-item error like the quiz/exercise fetches.
export function getResourcesForLesson(lessonId: string): Promise<Resource[]> {
  return apiRequest<Resource[]>(`/lessons/${lessonId}/resources`)
}
