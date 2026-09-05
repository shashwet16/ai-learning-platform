"""Curate a "Further Reading" list on each of the 6 lessons in "Data
Structures & Algorithms" — same reasoning and idempotence as every
other resources seed script: real, existing pages found via actual web
research, not written from memory. Leans on VisuAlgo (a well-known,
long-running interactive algorithm visualizer) more than the other two
courses' resource lists, since visualizing traversal and comparison
order is a genuinely better way to build intuition for this material
than reading about it.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_data_structures_and_algorithms_resources

Depends on seed_data_structures_and_algorithms.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource


def _big_o() -> list[Resource]:
    return [
        Resource(
            title="Big-O Cheat Sheet",
            url="https://www.bigocheatsheet.com/",
            description=(
                "A single reference page of time/space complexity for "
                "every common data structure operation and sorting "
                "algorithm — useful to come back to throughout the "
                "rest of this course, not just this one lesson."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Big O Notation",
            url="https://realpython.com/ref/computer-science-glossary/big-o-notation/",
            description=(
                "A concise glossary-style definition, good for "
                "checking your understanding of the lesson's own "
                "table of complexities against a second explanation."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _arrays_two_pointer() -> list[Resource]:
    return [
        Resource(
            title="Array",
            url="https://visualgo.net/en/array",
            description=(
                "An interactive visualization of array operations — "
                "watch insertion, deletion, and access happen step by "
                "step, which makes the O(1) access / O(n) insert "
                "tradeoff from this lesson genuinely visible."
            ),
            resource_type="interactive",
            order=1,
        ),
        Resource(
            title="Two Pointers",
            url="https://usaco.guide/silver/two-pointers",
            description=(
                "A deeper, competitive-programming-oriented treatment "
                "of the exact technique this lesson introduces, with "
                "more worked examples of the pattern."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _linked_lists() -> list[Resource]:
    return [
        Resource(
            title="Linked Lists in Python: An Introduction",
            url="https://realpython.com/linked-lists-python/",
            description=(
                "Covers the same `Node`-based structure this lesson "
                "builds, then goes further into when to reach for "
                "`collections.deque` instead of writing your own."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Linked List (Single, Doubly), Stack, Queue, Deque",
            url="https://visualgo.net/en/list",
            description=(
                "An interactive visualization of exactly the pointer-"
                "chasing this lesson's traversal loop does, one node "
                "at a time."
            ),
            resource_type="interactive",
            order=2,
        ),
    ]


def _stacks_and_queues() -> list[Resource]:
    return [
        Resource(
            title="Python Stacks, Queues, and Priority Queues in Practice",
            url="https://realpython.com/queue-in-python/",
            description=(
                "Goes past this lesson's `list`/`deque` basics into "
                "priority queues and thread-safe queue implementations "
                "for concurrent code."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Linked List, Stack, Queue, Deque",
            url="https://visualgo.net/en/list",
            description=(
                "Same interactive visualizer as the linked-lists "
                "lesson — it also has dedicated stack and queue modes, "
                "showing LIFO versus FIFO removal order directly."
            ),
            resource_type="interactive",
            order=2,
        ),
    ]


def _trees_and_graphs() -> list[Resource]:
    return [
        Resource(
            title="Graph Traversal (Depth/Breadth First Search)",
            url="https://visualgo.net/en/dfsbfs",
            description=(
                "An interactive visualization of DFS and BFS running "
                "on the same graph side by side — the clearest way to "
                "actually see why BFS explores level by level and DFS "
                "doesn't."
            ),
            resource_type="interactive",
            order=1,
        ),
        Resource(
            title="Tree Traversal",
            url="https://realpython.com/lessons/python-tree-traversal/",
            description=(
                "A short walkthrough of implementing tree traversal in "
                "Python, including how a depth-first function becomes "
                "breadth-first with one structural change."
            ),
            resource_type="video",
            order=2,
        ),
    ]


def _sorting_and_searching() -> list[Resource]:
    return [
        Resource(
            title="Sorting Algorithms in Python",
            url="https://realpython.com/sorting-algorithms-python/",
            description=(
                "Covers bubble, insertion, merge, quicksort, and "
                "Timsort from both a theoretical and hands-on "
                "implementation angle — the algorithms behind this "
                "lesson's own complexity claims."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Sorting (Bubble, Selection, Insertion, Merge, Quick, ...)",
            url="https://visualgo.net/en/sorting",
            description=(
                "An interactive visualization comparing sorting "
                "algorithms directly against each other — watching "
                "quicksort finish while bubble sort is still working "
                "makes the O(n log n) versus O(n²) gap concrete."
            ),
            resource_type="interactive",
            order=2,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "Big O and Complexity Analysis": _big_o,
    "Arrays and Two-Pointer Techniques": _arrays_two_pointer,
    "Linked Lists": _linked_lists,
    "Stacks and Queues": _stacks_and_queues,
    "Trees and Graph Traversal": _trees_and_graphs,
    "Sorting and Searching": _sorting_and_searching,
}


def _seed_one(
    db, lesson_title: str, build_resources: Callable[[], list[Resource]]
) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_data_structures_and_algorithms.py first."
        )

    existing_urls = set(
        db.execute(
            select(Resource.url).where(Resource.lesson_id == lesson.id)
        ).scalars()
    )

    seeded = 0
    skipped = 0
    for resource in build_resources():
        if resource.url in existing_urls:
            skipped += 1
            continue
        resource.lesson_id = lesson.id
        db.add(resource)
        seeded += 1
    db.commit()
    return f'"{lesson_title}": seeded {seeded}, skipped {skipped} already-present.'


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_resources in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_resources))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
