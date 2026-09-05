import { apiRequest } from './client'

export interface Choice {
  id: string
  text: string
  order: number
  // is_correct intentionally absent — never sent by the fetch endpoint.
}

export interface Question {
  id: string
  question_type: 'mcq' | 'open_ended'
  prompt: string
  order: number
  choices: Choice[]
}

export interface Quiz {
  id: string
  lesson_id: string
  questions: Question[]
}

export interface AnswerIn {
  question_id: string
  choice_id?: string
  answer_text?: string
}

export interface QuestionResult {
  question_id: string
  question_type: 'mcq' | 'open_ended'
  // null = not graded (unanswered), true/false = graded.
  correct: boolean | null
  feedback: string | null
  // mcq only, null for open_ended — the correct choice, revealed only
  // here (post-submission), never by getQuizForLesson above.
  correct_choice_id: string | null
}

export interface QuizSubmitResponse {
  results: QuestionResult[]
  correct_count: number
  graded_count: number
}

export function getQuizForLesson(lessonId: string): Promise<Quiz> {
  return apiRequest<Quiz>(`/lessons/${lessonId}/quiz`)
}

export function submitQuiz(
  quizId: string,
  answers: AnswerIn[],
): Promise<QuizSubmitResponse> {
  return apiRequest<QuizSubmitResponse>(`/quizzes/${quizId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  })
}
