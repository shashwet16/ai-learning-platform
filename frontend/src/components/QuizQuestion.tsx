import type { Question, QuestionResult } from '../api/quiz'

interface QuizQuestionProps {
  question: Question
  index: number
  // Uncontrolled-ish: the parent owns the actual answer state (keyed by
  // question id) and passes down just this question's current value,
  // the same lifting-state-up shape as ExercisePlayground owns `code`.
  choiceId: string | undefined
  answerText: string
  onChoiceChange: (choiceId: string) => void
  onAnswerTextChange: (text: string) => void
  // Present only after a submission — undefined pre-submit, at which
  // point the question renders as a plain, editable input with no
  // correctness styling at all.
  result: QuestionResult | undefined
  disabled: boolean
}

export function QuizQuestion({
  question,
  index,
  choiceId,
  answerText,
  onChoiceChange,
  onAnswerTextChange,
  result,
  disabled,
}: QuizQuestionProps) {
  const statusClass =
    result?.correct === true
      ? 'quiz-question--correct'
      : result?.correct === false
        ? 'quiz-question--incorrect'
        : ''

  return (
    <fieldset className={`quiz-question ${statusClass}`.trim()}>
      <legend className="quiz-question__prompt">
        <span className="quiz-question__number">{index + 1}.</span>{' '}
        {question.prompt}
      </legend>

      {question.question_type === 'mcq' ? (
        <div className="quiz-question__choices">
          {question.choices.map((choice) => {
            // Only meaningful once `result` exists — correct_choice_id is
            // never sent by the pre-submit fetch, so both are undefined/
            // false until the learner actually submits.
            const isCorrectChoice = result?.correct_choice_id === choice.id
            const isYourWrongChoice =
              result !== undefined && !isCorrectChoice && choiceId === choice.id
            const choiceClass = isCorrectChoice
              ? 'quiz-choice quiz-choice--correct'
              : isYourWrongChoice
                ? 'quiz-choice quiz-choice--wrong'
                : 'quiz-choice'

            return (
              <label key={choice.id} className={choiceClass}>
                <input
                  type="radio"
                  name={question.id}
                  value={choice.id}
                  checked={choiceId === choice.id}
                  onChange={() => onChoiceChange(choice.id)}
                  disabled={disabled}
                />
                {choice.text}
                {isCorrectChoice && (
                  <span className="quiz-choice__tag">Correct answer</span>
                )}
                {isYourWrongChoice && (
                  <span className="quiz-choice__tag quiz-choice__tag--wrong">
                    Your answer
                  </span>
                )}
              </label>
            )
          })}
        </div>
      ) : (
        <textarea
          className="quiz-question__textarea"
          value={answerText}
          onChange={(e) => onAnswerTextChange(e.target.value)}
          disabled={disabled}
          rows={4}
          placeholder="Type your answer…"
        />
      )}

      {result && (
        <div className="quiz-question__result">
          <span
            className={
              result.correct
                ? 'exercise-status exercise-status--passed'
                : result.correct === false
                  ? 'exercise-status exercise-status--failed'
                  : 'exercise-status'
            }
          >
            {result.correct === true && '✓ Correct'}
            {result.correct === false && '✗ Incorrect'}
            {result.correct === null && 'Not answered'}
          </span>
          {result.feedback && (
            <p className="quiz-question__feedback">{result.feedback}</p>
          )}
        </div>
      )}
    </fieldset>
  )
}
