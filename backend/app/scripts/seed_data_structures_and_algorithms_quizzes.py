"""Attach a quiz to each of the 6 lessons in "Data Structures &
Algorithms" — same 2-MCQ + 1-open-ended shape and per-lesson idempotence
as every other quiz seed script in this platform.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_data_structures_and_algorithms_quizzes

Depends on seed_data_structures_and_algorithms.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.quiz import Choice, Question, Quiz


def _big_o() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="Which grows fastest as n increases?",
                order=1,
                choices=[
                    Choice(text="O(log n)", is_correct=False, order=1),
                    Choice(text="O(n)", is_correct=False, order=2),
                    Choice(text="O(n²)", is_correct=True, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What does Big O notation actually describe?",
                order=2,
                choices=[
                    Choice(
                        text="The exact number of seconds an algorithm takes",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="The shape of how running time grows as input grows",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="How much RAM a program uses at startup",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson compares a nested-loop duplicate check to a "
                    "set-based one. Explain why the set-based version is "
                    "faster and what its Big O is."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _arrays_two_pointer() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "What must be true about the input for the "
                    "lesson's two-pointer sum technique to work?"
                ),
                order=1,
                choices=[
                    Choice(text="It must be sorted", is_correct=True, order=1),
                    Choice(
                        text="It must contain only positive numbers",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="It must have an even number of items",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "What's the Big O of the two-pointer technique "
                    "versus a naive nested-loop check?"
                ),
                order=2,
                choices=[
                    Choice(text="Both are O(n)", is_correct=False, order=1),
                    Choice(
                        text="Two-pointer is O(n), nested loop is O(n²)",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Two-pointer is O(n²), nested loop is O(n)",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain, in your own words, how the sliding window "
                    "technique relates to the two-pointer technique."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _linked_lists() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "What's the Big O of accessing an item by "
                    "position in a linked list?"
                ),
                order=1,
                choices=[
                    Choice(text="O(1)", is_correct=False, order=1),
                    Choice(text="O(log n)", is_correct=False, order=2),
                    Choice(text="O(n)", is_correct=True, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "What's the Big O of inserting a new node at the "
                    "front of a linked list?"
                ),
                order=2,
                choices=[
                    Choice(text="O(1)", is_correct=True, order=1),
                    Choice(text="O(n)", is_correct=False, order=2),
                    Choice(text="O(n²)", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says neither an array nor a linked list is "
                    "strictly better. Explain when you'd pick each one."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _stacks_and_queues() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="A stack is:",
                order=1,
                choices=[
                    Choice(
                        text="First-in, first-out (FIFO)", is_correct=False, order=1
                    ),
                    Choice(text="Last-in, first-out (LIFO)", is_correct=True, order=2),
                    Choice(
                        text="Sorted by value, not insertion order",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Why does the lesson prefer `collections.deque` "
                    "over a plain list for a queue?"
                ),
                order=2,
                choices=[
                    Choice(
                        text=(
                            "deque supports O(1) removal from either "
                            "end; a list is O(n) from the front"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="A plain list can't store more than a few items",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="deque is the only structure that supports .append()",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Give one real example of something naturally LIFO and "
                    "one naturally FIFO, using the lesson's own reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _trees_and_graphs() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Which traversal does the lesson say guarantees "
                    "finding the shortest path in an unweighted graph?"
                ),
                order=1,
                choices=[
                    Choice(text="Depth-first (DFS)", is_correct=False, order=1),
                    Choice(text="Breadth-first (BFS)", is_correct=True, order=2),
                    Choice(text="Neither guarantees it", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "What data structure does the lesson's BFS "
                    "implementation use to track what to visit next?"
                ),
                order=2,
                choices=[
                    Choice(text="A stack", is_correct=False, order=1),
                    Choice(text="A queue", is_correct=True, order=2),
                    Choice(text="A sorted list", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain why BFS finds the shortest path but DFS doesn't "
                    "guarantee it, using the lesson's own reasoning about "
                    "distance."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _sorting_and_searching() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What's the Big O of binary search on a sorted list?",
                order=1,
                choices=[
                    Choice(text="O(n)", is_correct=False, order=1),
                    Choice(text="O(log n)", is_correct=True, order=2),
                    Choice(text="O(n log n)", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What algorithm does Python's built-in `sorted()` use?",
                order=2,
                choices=[
                    Choice(text="Bubble sort", is_correct=False, order=1),
                    Choice(text="Timsort", is_correct=True, order=2),
                    Choice(text="Quicksort", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says knowing how sorting works isn't a "
                    "reason to reimplement it yourself. Explain what it is "
                    "a reason for instead."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "Big O and Complexity Analysis": _big_o,
    "Arrays and Two-Pointer Techniques": _arrays_two_pointer,
    "Linked Lists": _linked_lists,
    "Stacks and Queues": _stacks_and_queues,
    "Trees and Graph Traversal": _trees_and_graphs,
    "Sorting and Searching": _sorting_and_searching,
}


def _seed_one(db, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_data_structures_and_algorithms.py first."
        )

    existing = db.execute(
        select(Quiz).where(Quiz.lesson_id == lesson.id)
    ).scalar_one_or_none()
    if existing is not None:
        return f'Lesson "{lesson_title}" already has a quiz — skipping.'

    quiz = build_quiz()
    quiz.lesson_id = lesson.id
    db.add(quiz)
    db.commit()
    return f'Seeded quiz on "{lesson_title}".'


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_quiz in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_quiz))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
