"""Attach a graded coding exercise to 5 of the 6 lessons in "Data
Structures & Algorithms" — same reasoning and idempotence as every other
exercise seed script: "Big O and Complexity Analysis" is skipped, since
it teaches a way of *reasoning about* code rather than a function whose
correctness a hidden test can check (a test can verify what a function
returns, not what its asymptotic complexity is).

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_data_structures_and_algorithms_exercises

Every test_code here uses bare `assert` statements only, same Pyodide
grading contract as every other exercise in this platform.

Depends on seed_data_structures_and_algorithms.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _arrays_two_pointer() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Arrays and Two-Pointer Techniques — write "
            "`has_pair_with_sum(sorted_numbers, target)`, returning "
            "`True` if any two numbers in `sorted_numbers` add up to "
            "`target`, using the lesson's own two-pointer technique "
            "(no nested loop)."
        ),
        starter_code=(
            "def has_pair_with_sum(sorted_numbers: list[int], target: int) -> bool:\n"
            '    """Return True if two numbers in sorted_numbers add\n'
            '    up to target, using the two-pointer technique."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert has_pair_with_sum([1, 2, 4, 7, 11], 15) is True\n"
            "assert has_pair_with_sum([1, 2, 4, 7, 11], 20) is False\n"
            "assert has_pair_with_sum([], 5) is False\n"
            "assert has_pair_with_sum([5], 5) is False\n"
            'print("All two-pointer checks passed.")\n'
        ),
    )


def _linked_lists() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Linked Lists — using the lesson's own `Node` class, "
            "write `linked_list_to_list(head)`, returning a plain "
            "Python list containing every value in the linked list "
            "starting at `head`, in order."
        ),
        starter_code=(
            "class Node:\n"
            "    def __init__(self, value, next=None):\n"
            "        self.value = value\n"
            "        self.next = next\n\n\n"
            "def linked_list_to_list(head):\n"
            '    """Return a plain Python list containing every value\n'
            '    in the linked list starting at head, in order."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "single = Node(1)\n"
            "assert linked_list_to_list(single) == [1]\n\n"
            "chain = Node(1, Node(2, Node(3)))\n"
            "assert linked_list_to_list(chain) == [1, 2, 3]\n\n"
            "assert linked_list_to_list(None) == []\n"
            'print("All linked-list checks passed.")\n'
        ),
    )


def _stacks_and_queues() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Stacks and Queues — write `is_balanced(expression)`, "
            "returning `True` if every `()`, `[]`, and `{}` in "
            "`expression` is correctly matched and nested, using a "
            "stack."
        ),
        starter_code=(
            "def is_balanced(expression: str) -> bool:\n"
            '    """Return True if every (), [], and {} in expression\n'
            '    is correctly matched and nested, using a stack."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert is_balanced("()") is True\n'
            'assert is_balanced("([{}])") is True\n'
            'assert is_balanced("(]") is False\n'
            'assert is_balanced("(()") is False\n'
            'assert is_balanced("") is True\n'
            'print("All stack checks passed.")\n'
        ),
    )


def _trees_and_graphs() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Trees and Graph Traversal — write `bfs_order(graph, "
            "start)`, returning the list of nodes visited by "
            "breadth-first search starting at `start`, in the order "
            "they were first visited (each node appears once, "
            "neighbors visited in the order they're listed for a "
            "given node)."
        ),
        starter_code=(
            "from collections import deque\n\n\n"
            "def bfs_order(graph: dict, start):\n"
            '    """Return the list of nodes visited by BFS starting\n'
            "    at start, in visitation order (each node visited\n"
            '    once, neighbors in listed order)."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "graph = {\n"
            '    "A": ["B", "C"],\n'
            '    "B": ["A", "D"],\n'
            '    "C": ["A", "D"],\n'
            '    "D": ["B", "C"],\n'
            "}\n"
            'assert bfs_order(graph, "A") == ["A", "B", "C", "D"]\n\n'
            'line = {"1": ["2"], "2": ["1", "3"], "3": ["2"]}\n'
            'assert bfs_order(line, "1") == ["1", "2", "3"]\n'
            'print("All BFS checks passed.")\n'
        ),
    )


def _sorting_and_searching() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Sorting and Searching — write `binary_search"
            "(sorted_items, target)`, returning the index of `target` "
            "in `sorted_items`, or `-1` if it isn't present."
        ),
        starter_code=(
            "def binary_search(sorted_items: list[int], target: int) -> int:\n"
            '    """Return the index of target in sorted_items, or -1\n'
            '    if it isn\'t present."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert binary_search([1, 3, 5, 7, 9], 7) == 3\n"
            "assert binary_search([1, 3, 5, 7, 9], 4) == -1\n"
            "assert binary_search([], 1) == -1\n"
            "assert binary_search([5], 5) == 0\n"
            'print("All binary search checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Arrays and Two-Pointer Techniques": _arrays_two_pointer,
    "Linked Lists": _linked_lists,
    "Stacks and Queues": _stacks_and_queues,
    "Trees and Graph Traversal": _trees_and_graphs,
    "Sorting and Searching": _sorting_and_searching,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_data_structures_and_algorithms.py first."
        )

    existing = db.execute(
        select(Exercise).where(Exercise.lesson_id == lesson.id)
    ).scalar_one_or_none()
    if existing is not None:
        return f'Lesson "{lesson_title}" already has an exercise — skipping.'

    exercise = build_exercise()
    exercise.lesson_id = lesson.id
    db.add(exercise)
    db.commit()
    return f'Seeded exercise on "{lesson_title}".'


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_exercise in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_exercise))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
