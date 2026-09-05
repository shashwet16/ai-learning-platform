"""Populate the database with "Programming Foundations" — course #1 of
the 10-course curriculum plan (see ROADMAP.md's "Curriculum content
expansion plan"), and the first one actually written.

A genuine complete-beginner starting point: every later course in this
platform (including the existing "Intro to AI Engineering") assumes a
learner can already read and write basic Python, which was never
actually true until this course exists. Original writing throughout —
informed by the standard variables -> control flow -> functions ->
collections progression nearly every intro-programming course follows,
never copied from any specific one.

Two lessons ("Variables and Values", "Loops") include a
```python-playground``` fenced block — LessonPage.tsx's markdown renderer
(M3.9) already special-cases this fence into a live, runnable editor, but
no seeded lesson had actually used it until now; every other lesson in
this platform only ever used the plain ```python fence, which just
renders as static, non-runnable syntax-highlighted text.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_programming_foundations

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Programming Foundations"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "A from-scratch introduction to programming in Python, for a "
            "genuine complete beginner — the foundation every later "
            "course on this platform assumes you already have."
        ),
        modules=[
            Module(
                title="The Basics",
                order=1,
                lessons=[
                    Lesson(
                        title="Variables and Values",
                        order=1,
                        body=(
                            "# Variables and Values\n\n"
                            "A variable is a name that points to a value "
                            "stored in memory. Creating one is called "
                            "*assignment*:\n\n"
                            "```python\n"
                            'age = 27\nname = "Ada"\nis_learning = True\n'
                            "```\n\n"
                            "Every value has a *type* — Python figures "
                            "the type out automatically from what you "
                            "assign, rather than making you declare it "
                            "up front:\n\n"
                            "- `int` — whole numbers, like `27`\n"
                            "- `float` — decimal numbers, like `3.14`\n"
                            "- `str` — text, wrapped in quotes\n"
                            "- `bool` — `True` or `False`\n\n"
                            "A name can be reassigned to a completely "
                            "different type later — Python won't stop "
                            "you. That makes it fast to write, but it "
                            "also means a typo in a variable name fails "
                            "at *runtime*, the moment that line actually "
                            "runs, not before — a mistake this course's "
                            "own graded exercises will make you feel "
                            "firsthand.\n\n"
                            "```python-playground\n"
                            'name = "Ada"\n'
                            "age = 27\n"
                            'print(f"{name} is {age} years old")\n'
                            "```"
                        ),
                    ),
                    Lesson(
                        title="Making Decisions: Conditionals",
                        order=2,
                        body=(
                            "# Making Decisions: Conditionals\n\n"
                            "Real programs need to behave differently "
                            "depending on their input. `if`/`elif`/`else` "
                            "is how Python branches:\n\n"
                            "```python\n"
                            "temperature = 15\n\n"
                            "if temperature > 25:\n"
                            '    print("It\'s hot")\n'
                            "elif temperature > 10:\n"
                            '    print("It\'s mild")\n'
                            "else:\n"
                            '    print("It\'s cold")\n'
                            "```\n\n"
                            "Only one branch ever runs — Python checks "
                            "each condition top to bottom and stops at "
                            "the first one that's `True`, falling "
                            "through to `else` only if none matched. "
                            "Conditions are built from comparison "
                            "operators (`==`, `!=`, `<`, `>`, `<=`, "
                            "`>=`) and combined with `and`/`or`/`not`:\n\n"
                            "```python\n"
                            "age = 20\n"
                            "has_ticket = True\n\n"
                            "if age >= 18 and has_ticket:\n"
                            '    print("Allowed in")\n'
                            "```\n\n"
                            "A common beginner slip: `=` assigns a "
                            "value, `==` compares two values. Python "
                            "won't even let you write `if age = 20:` — "
                            "it's a syntax error, not a silently wrong "
                            "result — but the two symbols still mean "
                            "completely different things, and it's worth "
                            "having that reflex before it costs you a "
                            "debugging session."
                        ),
                    ),
                ],
            ),
            Module(
                title="Repetition and Reuse",
                order=2,
                lessons=[
                    Lesson(
                        title="Loops",
                        order=1,
                        body=(
                            "# Loops\n\n"
                            "A loop repeats a block of code without you "
                            "writing it out by hand. Python has two:\n\n"
                            "**`for`** — repeats once per item in a "
                            "sequence:\n\n"
                            "```python\n"
                            "for number in range(5):\n"
                            "    print(number)  # 0, 1, 2, 3, 4\n"
                            "```\n\n"
                            "**`while`** — repeats as long as a "
                            "condition stays `True`:\n\n"
                            "```python\n"
                            "count = 0\n"
                            "while count < 5:\n"
                            "    print(count)\n"
                            "    count += 1\n"
                            "```\n\n"
                            "`for` is the right choice when you know "
                            "what you're iterating over — a list, a "
                            "range of numbers. `while` is right when "
                            "you're waiting for something to become true "
                            "and don't know in advance how many "
                            "iterations that'll take. Two keywords "
                            "control a loop mid-flight: `break` exits it "
                            "immediately, and `continue` skips straight "
                            "to the next iteration.\n\n"
                            "```python-playground\n"
                            "for number in range(1, 6):\n"
                            "    if number % 2 == 0:\n"
                            "        continue\n"
                            "    print(number)\n"
                            "```\n\n"
                            "That loop only prints the odd numbers from "
                            "1 to 5 — `continue` skips the `print` for "
                            "every even one instead of stopping the "
                            "loop entirely."
                        ),
                    ),
                    Lesson(
                        title="Functions",
                        order=2,
                        body=(
                            "# Functions\n\n"
                            "A function packages up a block of code "
                            "under a name, so you can run it again "
                            "without retyping it:\n\n"
                            "```python\n"
                            "def greet(name):\n"
                            '    return f"Hello, {name}!"\n\n'
                            'greet("Ada")  # "Hello, Ada!"\n'
                            "```\n\n"
                            "`name` here is a *parameter* — a "
                            "placeholder that becomes a real value (an "
                            "*argument*) each time the function is "
                            "called. `return` hands a value back to "
                            "whatever called the function; without it, "
                            "a function implicitly returns `None`.\n\n"
                            "Functions matter for more than avoiding "
                            "repetition. A function with a clear name "
                            "and a single job is easier to test in "
                            "isolation than a long, tangled script — "
                            "exactly the property this platform's own "
                            "graded exercises depend on: each one asks "
                            "you to write one function that a hidden "
                            "test can call and check, the same way real "
                            "production code gets tested unit by unit "
                            "rather than as one giant script."
                        ),
                    ),
                ],
            ),
            Module(
                title="Working with Collections",
                order=3,
                lessons=[
                    Lesson(
                        title="Lists",
                        order=1,
                        body=(
                            "# Lists\n\n"
                            "A list holds an ordered sequence of "
                            "values:\n\n"
                            "```python\n"
                            'fruits = ["apple", "banana", "cherry"]\n'
                            "```\n\n"
                            "Access an item by its position, starting "
                            "at `0`:\n\n"
                            "```python\n"
                            'fruits[0]   # "apple"\n'
                            'fruits[-1]  # "cherry" — negative indices '
                            "count from the end\n"
                            "```\n\n"
                            "Lists are *mutable* — you can change them "
                            "in place:\n\n"
                            "```python\n"
                            'fruits.append("date")   # add to the end\n'
                            'fruits[0] = "apricot"   # replace an item\n'
                            "len(fruits)              # 4\n"
                            "```\n\n"
                            "Looping over a list is the most common way "
                            "to process one:\n\n"
                            "```python\n"
                            "for fruit in fruits:\n"
                            "    print(fruit.upper())\n"
                            "```\n\n"
                            "A `list` is the right structure when order "
                            "matters and you'll look things up by "
                            "position or scan the whole thing — the "
                            "next lesson covers `dict`, which is the "
                            "right structure when you look things up "
                            "by name instead."
                        ),
                    ),
                    Lesson(
                        title="Dictionaries",
                        order=2,
                        body=(
                            "# Dictionaries\n\n"
                            "A dictionary stores values under *keys* "
                            "instead of positions:\n\n"
                            "```python\n"
                            'user = {"name": "Ada", "age": 27, "role": '
                            '"engineer"}\n'
                            "```\n\n"
                            "Look up a value by its key, not its "
                            "position:\n\n"
                            "```python\n"
                            'user["name"]        # "Ada"\n'
                            'user.get("email")   # None — .get() returns '
                            "None instead of crashing on a missing key\n"
                            "```\n\n"
                            "Dictionaries are also mutable:\n\n"
                            "```python\n"
                            'user["age"] = 28           # update a '
                            "value\n"
                            'user["email"] = "a@x.com"  # add a new '
                            "key\n"
                            'del user["role"]           # remove a '
                            "key\n"
                            "```\n\n"
                            "Loop over a dictionary's keys, values, or "
                            "both:\n\n"
                            "```python\n"
                            "for key, value in user.items():\n"
                            '    print(f"{key}: {value}")\n'
                            "```\n\n"
                            "Reach for a `dict` whenever the data is "
                            "naturally a set of named fields — exactly "
                            "the shape most real API responses arrive "
                            "in, including the JSON this platform's own "
                            "backend has been sending the frontend for "
                            "every lesson, quiz, and exercise you've "
                            "used so far."
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
