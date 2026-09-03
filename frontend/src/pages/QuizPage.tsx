import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import {
  getQuizForLesson,
  submitQuiz,
  type AnswerIn,
  type QuestionResult,
  type Quiz,
} from '../api/quiz'
import { QuizQuestion } from '../components/QuizQuestion'

// One answer per question, keyed by question id — mirrors AnswerIn's
// shape (choice_id for mcq, answer_text for open_ended) so building the
// submit payload at the end is a direct Object.values(), not a reshape.
type AnswerState = Record<string, { choiceId?: string; answerText: string }>

export function QuizPage() {
  const { lessonId } = useParams<{ lessonId: string }>()
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [answers, setAnswers] = useState<AnswerState>({})
  const [results, setResults] = useState<
    Map<string, QuestionResult> | undefined
  >(undefined)
  const [summary, setSummary] = useState<
    { correct: number; graded: number } | undefined
  >(undefined)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!lessonId) return
    setQuiz(null)
    setError(null)
    getQuizForLesson(lessonId)
      .then(setQuiz)
      .catch((err: unknown) => {
        setError(
          err instanceof ApiError && err.status === 404
            ? 'This lesson has no quiz.'
            : 'Failed to load quiz.',
        )
      })
  }, [lessonId])

  function setChoice(questionId: string, choiceId: string) {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { ...prev[questionId], choiceId, answerText: '' },
    }))
  }

  function setAnswerText(questionId: string, answerText: string) {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { ...prev[questionId], answerText },
    }))
  }

  async function handleSubmit() {
    if (!quiz) return
    setIsSubmitting(true)

    const payload: AnswerIn[] = quiz.questions.map((q) => {
      const a = answers[q.id]
      return {
        question_id: q.id,
        choice_id: a?.choiceId,
        answer_text: a?.answerText || undefined,
      }
    })

    try {
      const response = await submitQuiz(quiz.id, payload)
      setResults(new Map(response.results.map((r) => [r.question_id, r])))
      setSummary({
        correct: response.correct_count,
        graded: response.graded_count,
      })
    } catch (err: unknown) {
      setError(err instanceof ApiError ? err.message : 'Failed to submit quiz.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (error) {
    return (
      <div className="quiz-page">
        <p className="form-error">{error}</p>
        {lessonId && (
          <Link to={`/lessons/${lessonId}`} className="back-link">
            ← Back to lesson
          </Link>
        )}
      </div>
    )
  }

  if (quiz === null) {
    return <p>Loading…</p>
  }

  const answeredCount = quiz.questions.filter((q) => {
    const a = answers[q.id]
    return a?.choiceId || a?.answerText
  }).length

  return (
    <div className="quiz-page">
      {lessonId && (
        <Link to={`/lessons/${lessonId}`} className="back-link">
          ← Back to lesson
        </Link>
      )}
      <span className="kicker">Quiz</span>
      <h1>Check your understanding</h1>

      {summary && (
        <p className="quiz-page__summary">
          Scored {summary.correct} / {summary.graded} graded question
          {summary.graded === 1 ? '' : 's'}.
        </p>
      )}

      <div className="quiz-question-list">
        {quiz.questions.map((question, index) => (
          <QuizQuestion
            key={question.id}
            question={question}
            index={index}
            choiceId={answers[question.id]?.choiceId}
            answerText={answers[question.id]?.answerText ?? ''}
            onChoiceChange={(choiceId) => setChoice(question.id, choiceId)}
            onAnswerTextChange={(text) => setAnswerText(question.id, text)}
            result={results?.get(question.id)}
            disabled={isSubmitting || results !== undefined}
          />
        ))}
      </div>

      {results === undefined && (
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={isSubmitting || answeredCount === 0}
        >
          {isSubmitting ? 'Grading…' : 'Submit answers'}
        </button>
      )}
    </div>
  )
}
