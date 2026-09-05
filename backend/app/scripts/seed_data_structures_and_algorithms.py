"""Populate the database with "Data Structures & Algorithms" — course #3
of the 10-course curriculum plan (see ROADMAP.md's "Curriculum content
expansion plan").

Covers arrays, linked lists, stacks/queues, trees, graph traversal, and
sorting/searching, plus the complexity-analysis vocabulary needed to
reason about all of them — the plan's own stated scope, using generic
problem *categories* (two-pointer, sliding window, graph traversal)
rather than any specific copied interview question. Original writing
throughout, same policy as every other course script.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_data_structures_and_algorithms

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Data Structures & Algorithms"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "The data structures and algorithmic thinking every later "
            "course assumes — complexity analysis, arrays, linked "
            "lists, stacks/queues, trees, graphs, and sorting/searching."
        ),
        modules=[
            Module(
                title="Complexity and Arrays",
                order=1,
                lessons=[
                    Lesson(
                        title="Big O and Complexity Analysis",
                        order=1,
                        body=(
                            "# Big O and Complexity Analysis\n\n"
                            "Big O notation describes how an "
                            "algorithm's running time (or memory use) "
                            "grows as its input grows — not the exact "
                            "number of seconds, which depends on the "
                            "machine, but the *shape* of the growth, "
                            "which doesn't.\n\n"
                            "Common complexities, from best to "
                            "worst:\n\n"
                            "- **O(1)**, constant — looking up a dict "
                            "key\n"
                            "- **O(log n)**, logarithmic — binary "
                            "search\n"
                            "- **O(n)**, linear — scanning a list "
                            "once\n"
                            "- **O(n log n)**, linearithmic — a good "
                            "sort\n"
                            "- **O(n²)**, quadratic — comparing every "
                            "pair\n\n"
                            "The difference matters at scale, not on "
                            "toy inputs:\n\n"
                            "```python\n"
                            "def has_duplicate_slow(items):\n"
                            "    for i in range(len(items)):\n"
                            "        for j in range(i + 1, len(items)):\n"
                            "            if items[i] == items[j]:\n"
                            "                return True\n"
                            "    return False  # O(n²) — nested loop\n\n"
                            "def has_duplicate_fast(items):\n"
                            "    return len(set(items)) != len(items)\n"
                            "    # O(n) — one pass, using a set's O(1) "
                            "membership check\n"
                            "```\n\n"
                            "Both functions answer the same question. "
                            "At 100 items the difference is invisible; "
                            "at 1,000,000 items, one finishes instantly "
                            "and the other doesn't finish in your "
                            "lifetime. Every other lesson in this "
                            "course will name the Big O of what it "
                            "teaches — this is the vocabulary that "
                            "makes those claims mean something."
                        ),
                    ),
                    Lesson(
                        title="Arrays and Two-Pointer Techniques",
                        order=2,
                        body=(
                            "# Arrays and Two-Pointer Techniques\n\n"
                            "A Python `list` is used as this course's "
                            "array — contiguous, indexed storage where "
                            "any position is an O(1) lookup by index, "
                            "but searching for a *value* you don't "
                            "know the position of is O(n).\n\n"
                            "The **two-pointer technique** solves a "
                            "whole category of array problems in O(n) "
                            "instead of the O(n²) a naive nested loop "
                            "would need, by walking two positions "
                            "through the array at once instead of "
                            "comparing every pair:\n\n"
                            "```python\n"
                            "def has_pair_with_sum(sorted_numbers, target):\n"
                            "    left, right = 0, len(sorted_numbers) - 1\n"
                            "    while left < right:\n"
                            "        total = (\n"
                            "            sorted_numbers[left] + sorted_numbers[right]\n"
                            "        )\n"
                            "        if total == target:\n"
                            "            return True\n"
                            "        elif total < target:\n"
                            "            left += 1   # need a bigger sum\n"
                            "        else:\n"
                            "            right -= 1  # need a smaller sum\n"
                            "    return False\n"
                            "```\n\n"
                            "This only works because the input is "
                            "*sorted* — that ordering is what lets "
                            "moving a pointer reliably move the sum in "
                            "one direction. A close relative, the "
                            "**sliding window** technique, uses the "
                            "same 'two pointers, one pass' idea to "
                            "track a contiguous *subrange* of the "
                            "array (e.g. 'the longest run of items "
                            "under some limit') instead of a single "
                            "pair — same complexity win, same shape of "
                            "idea, applied to a different question."
                        ),
                    ),
                ],
            ),
            Module(
                title="Linked Structures",
                order=2,
                lessons=[
                    Lesson(
                        title="Linked Lists",
                        order=1,
                        body=(
                            "# Linked Lists\n\n"
                            "A linked list stores its items as a chain "
                            "of individual nodes, each pointing to the "
                            "next, instead of one contiguous block "
                            "like an array:\n\n"
                            "```python\n"
                            "class Node:\n"
                            "    def __init__(self, value, next=None):\n"
                            "        self.value = value\n"
                            "        self.next = next\n\n"
                            "head = Node(1, Node(2, Node(3)))\n\n"
                            "current = head\n"
                            "while current is not None:\n"
                            "    print(current.value)  # 1, 2, 3\n"
                            "    current = current.next\n"
                            "```\n\n"
                            "The tradeoff against an array is exactly "
                            "the reverse of what you'd expect from how "
                            "similar they look:\n\n"
                            "- **Access by position** is O(n) for a "
                            "linked list (you have to walk from the "
                            "head) versus O(1) for an array\n"
                            "- **Inserting at the front** is O(1) for "
                            "a linked list (just point a new node at "
                            "the old head) versus O(n) for an array "
                            "(every existing item has to shift over)\n\n"
                            "Neither structure is strictly better — "
                            "an array wins when you look things up by "
                            "position constantly; a linked list wins "
                            "when you're constantly inserting and "
                            "removing from the ends and rarely look "
                            "things up by position at all."
                        ),
                    ),
                    Lesson(
                        title="Stacks and Queues",
                        order=2,
                        body=(
                            "# Stacks and Queues\n\n"
                            "A **stack** is last-in, first-out (LIFO) "
                            "— the most recently added item is the "
                            "first one removed. Python's own `list` "
                            "already behaves like one:\n\n"
                            "```python\n"
                            "stack = []\n"
                            "stack.append(1)\n"
                            "stack.append(2)\n"
                            "stack.pop()  # 2 — the most recent item\n"
                            "```\n\n"
                            "A **queue** is first-in, first-out "
                            "(FIFO) — the earliest added item is the "
                            "first one removed. Using a plain list as "
                            "a queue works but is O(n) per removal "
                            "(everything after the front has to shift "
                            "over); `collections.deque` gives O(1) "
                            "removal from either end instead:\n\n"
                            "```python\n"
                            "from collections import deque\n\n"
                            "queue = deque()\n"
                            "queue.append(1)\n"
                            "queue.append(2)\n"
                            "queue.popleft()  # 1 — the earliest item\n"
                            "```\n\n"
                            "The choice between them tracks the "
                            "problem, not personal taste: undo "
                            "history and matching balanced parentheses "
                            "are naturally LIFO (a stack); a print "
                            "queue or task queue is naturally FIFO (a "
                            "queue) — and, as the next lesson shows, a "
                            "queue is also what breadth-first graph "
                            "traversal is built on."
                        ),
                    ),
                ],
            ),
            Module(
                title="Trees, Graphs, and Sorting",
                order=3,
                lessons=[
                    Lesson(
                        title="Trees and Graph Traversal",
                        order=1,
                        body=(
                            "# Trees and Graph Traversal\n\n"
                            "A tree is a set of nodes where each has "
                            "at most one parent and any number of "
                            "children, with a single root and no "
                            "cycles. A graph generalizes this further "
                            "— any node can connect to any other, "
                            "with no restriction on parents or "
                            "cycles.\n\n"
                            "Two traversal strategies cover almost "
                            "everything you'll do with either "
                            "structure:\n\n"
                            "**Depth-first (DFS)** — go as deep as "
                            "possible before backtracking, naturally "
                            "written with recursion (which uses the "
                            "call stack as its own stack):\n\n"
                            "```python\n"
                            "def dfs(graph, node, visited=None):\n"
                            "    if visited is None:\n"
                            "        visited = set()\n"
                            "    visited.add(node)\n"
                            "    for neighbor in graph[node]:\n"
                            "        if neighbor not in visited:\n"
                            "            dfs(graph, neighbor, visited)\n"
                            "    return visited\n"
                            "```\n\n"
                            "**Breadth-first (BFS)** — explore every "
                            "neighbor at the current distance before "
                            "going further out, using an explicit "
                            "queue (from the previous lesson) instead "
                            "of recursion:\n\n"
                            "```python\n"
                            "from collections import deque\n\n"
                            "def bfs(graph, start):\n"
                            "    visited = {start}\n"
                            "    queue = deque([start])\n"
                            "    while queue:\n"
                            "        node = queue.popleft()\n"
                            "        for neighbor in graph[node]:\n"
                            "            if neighbor not in visited:\n"
                            "                visited.add(neighbor)\n"
                            "                queue.append(neighbor)\n"
                            "    return visited\n"
                            "```\n\n"
                            "The choice isn't arbitrary: BFS "
                            "guarantees finding the *shortest* path in "
                            "an unweighted graph (it reaches every "
                            "node at distance 1 before any node at "
                            "distance 2), which DFS does not "
                            "guarantee at all."
                        ),
                    ),
                    Lesson(
                        title="Sorting and Searching",
                        order=2,
                        body=(
                            "# Sorting and Searching\n\n"
                            "Searching an unsorted list for a value is "
                            "O(n) — you might have to check every "
                            "item. Once a list is *sorted*, **binary "
                            "search** finds a value in O(log n) by "
                            "repeatedly halving the search space:\n\n"
                            "```python\n"
                            "def binary_search(sorted_items, target):\n"
                            "    left, right = 0, len(sorted_items) - 1\n"
                            "    while left <= right:\n"
                            "        mid = (left + right) // 2\n"
                            "        if sorted_items[mid] == target:\n"
                            "            return mid\n"
                            "        elif sorted_items[mid] < target:\n"
                            "            left = mid + 1\n"
                            "        else:\n"
                            "            right = mid - 1\n"
                            "    return -1\n"
                            "```\n\n"
                            "That speedup is *why* sorting is worth "
                            "doing at all when you'll search "
                            "repeatedly. Sorting algorithms themselves "
                            "range from O(n²) (bubble sort, insertion "
                            "sort — simple, fine for small or "
                            "nearly-sorted input) to O(n log n) (merge "
                            "sort, quicksort — the practical default "
                            "for anything larger).\n\n"
                            "In real code, you almost never hand-write "
                            "a sort: Python's built-in `sorted()` and "
                            "`list.sort()` use Timsort, an O(n log n) "
                            "algorithm tuned for real-world data, "
                            "including data that's already partially "
                            "sorted. Knowing how sorting works is what "
                            "lets you reason about *when* to sort "
                            "something and what it costs — not a "
                            "reason to reimplement it yourself."
                        ),
                    ),
                ],
            ),
        ],
    )


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(
            select(Course).where(Course.title == COURSE_TITLE)
        ).scalar_one_or_none()
        if existing is not None:
            print(f'Course "{COURSE_TITLE}" already exists — skipping seed.')
            return

        course = build_course()
        db.add(course)
        db.commit()

        lesson_count = sum(len(m.lessons) for m in course.modules)
        print(
            f'Seeded "{COURSE_TITLE}": {len(course.modules)} modules, '
            f"{lesson_count} lessons."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
