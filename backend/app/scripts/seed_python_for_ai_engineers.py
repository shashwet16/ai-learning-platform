"""Populate the database with "Python for AI Engineers" — course #2 of
the 10-course curriculum plan (see ROADMAP.md's "Curriculum content
expansion plan"), picked up right after course #1 (Programming
Foundations) per the plan's own stated ordering.

Goes past Programming Foundations' basics into real Python fluency:
richer function signatures, comprehensions, classes, error handling,
and packages/JSON — deliberately ending on JSON, since that's the exact
mechanism ("Intro to AI Engineering" and this platform's own backend
both) every later course's API calls actually run on. Original writing
throughout, same policy as every other course script.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_python_for_ai_engineers

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Python for AI Engineers"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "Real Python fluency beyond the basics — richer functions, "
            "classes, error handling, and working with packages and "
            "JSON — the last stop before this platform's own 'Intro to "
            "AI Engineering' course."
        ),
        modules=[
            Module(
                title="Functions, Deeper",
                order=1,
                lessons=[
                    Lesson(
                        title="Default Arguments and *args/**kwargs",
                        order=1,
                        body=(
                            "# Default Arguments and *args/**kwargs\n\n"
                            "A parameter can have a default value, "
                            "making it optional to pass:\n\n"
                            "```python\n"
                            'def greet(name, greeting="Hello"):\n'
                            '    return f"{greeting}, {name}!"\n\n'
                            'greet("Ada")        # "Hello, Ada!"\n'
                            'greet("Ada", "Hi")  # "Hi, Ada!"\n'
                            "```\n\n"
                            "Two special parameter forms let a function "
                            "accept an arbitrary number of arguments:\n\n"
                            "- `*args` collects any extra *positional* "
                            "arguments into a tuple\n"
                            "- `**kwargs` collects any extra *keyword* "
                            "arguments into a dict\n\n"
                            "```python\n"
                            "def describe(*args, **kwargs):\n"
                            "    print(args)     # (1, 2, 3)\n"
                            '    print(kwargs)   # {"color": "red"}\n\n'
                            'describe(1, 2, 3, color="red")\n'
                            "```\n\n"
                            "You'll see this pattern constantly once you "
                            "start calling real libraries — something "
                            "like `requests.get(url, **kwargs)` accepts "
                            "dozens of optional settings without listing "
                            "every one of them by name.\n\n"
                            "A caution worth internalizing early: a "
                            "mutable default argument (`def f(items=[])`) "
                            "is created *once*, when the function is "
                            "defined, not fresh on every call — a "
                            "well-known Python gotcha that silently "
                            "shares state across calls unless you guard "
                            "against it with `None` and an `if` check "
                            "instead."
                        ),
                    ),
                    Lesson(
                        title="List and Dictionary Comprehensions",
                        order=2,
                        body=(
                            "# List and Dictionary Comprehensions\n\n"
                            "A comprehension builds a new list (or "
                            "dict) from an existing sequence in one "
                            "line, instead of a `for` loop with "
                            "`.append()`:\n\n"
                            "```python\n"
                            "numbers = [1, 2, 3, 4, 5]\n"
                            "squares = [n * n for n in numbers]\n"
                            "# [1, 4, 9, 16, 25]\n"
                            "```\n\n"
                            "The same loop written the long way:\n\n"
                            "```python\n"
                            "squares = []\n"
                            "for n in numbers:\n"
                            "    squares.append(n * n)\n"
                            "```\n\n"
                            "Add a condition to filter which items "
                            "make it in:\n\n"
                            "```python\n"
                            "evens = [n for n in numbers if n % 2 == 0]\n"
                            "# [2, 4]\n"
                            "```\n\n"
                            "Dict comprehensions build key-value pairs "
                            "the same way:\n\n"
                            "```python\n"
                            "lengths = {word: len(word) for word in "
                            '["a", "ab", "abc"]}\n'
                            '# {"a": 1, "ab": 2, "abc": 3}\n'
                            "```\n\n"
                            "Comprehensions aren't just shorter — "
                            "they're usually faster too, since Python "
                            "can optimize the loop internally. But "
                            "readability comes first: once a "
                            "comprehension needs more than one "
                            "condition or a nested loop, a plain `for` "
                            "loop is the more honest choice.\n\n"
                            "```python-playground\n"
                            "numbers = [1, 2, 3, 4, 5, 6, 7, 8]\n"
                            "evens_squared = [n * n for n in numbers "
                            "if n % 2 == 0]\n"
                            "print(evens_squared)\n"
                            "```"
                        ),
                    ),
                ],
            ),
            Module(
                title="Object-Oriented Basics",
                order=2,
                lessons=[
                    Lesson(
                        title="Classes and Objects",
                        order=1,
                        body=(
                            "# Classes and Objects\n\n"
                            "A class is a blueprint for creating "
                            "objects that bundle data and behavior "
                            "together:\n\n"
                            "```python\n"
                            "class Dog:\n"
                            "    def __init__(self, name, breed):\n"
                            "        self.name = name\n"
                            "        self.breed = breed\n\n"
                            "    def bark(self):\n"
                            '        return f"{self.name} says woof!"\n\n'
                            'rex = Dog("Rex", "Labrador")\n'
                            'rex.bark()  # "Rex says woof!"\n'
                            "```\n\n"
                            "`__init__` is a special method Python "
                            "calls automatically when you create a new "
                            'object (`Dog("Rex", "Labrador")`) — it\'s '
                            "where you set up the object's initial "
                            "state. `self` refers to *this particular "
                            "object*; every method takes it as its "
                            "first parameter, and Python passes it "
                            "automatically when you call "
                            "`rex.bark()`.\n\n"
                            "Each object created from a class has its "
                            "own independent copy of the data set in "
                            "`__init__`:\n\n"
                            "```python\n"
                            'fido = Dog("Fido", "Poodle")\n'
                            'rex.name    # "Rex"\n'
                            'fido.name   # "Fido" — completely separate '
                            "from rex's\n"
                            "```\n\n"
                            "Reach for a class when data and the "
                            "behavior that operates on it naturally "
                            "travel together — a `Dog` that knows its "
                            "own name and how to bark is easier to "
                            "reason about than a loose dict plus a "
                            "separate function that both have to agree "
                            "on the same keys."
                        ),
                    ),
                    Lesson(
                        title="Handling Errors: try/except",
                        order=2,
                        body=(
                            "# Handling Errors: try/except\n\n"
                            "Code fails sometimes — a file might not "
                            "exist, an API might time out, a user "
                            "might type text where a number was "
                            "expected. `try`/`except` lets your "
                            "program handle that instead of "
                            "crashing:\n\n"
                            "```python\n"
                            "try:\n"
                            "    result = 10 / 0\n"
                            "except ZeroDivisionError:\n"
                            "    result = None\n"
                            '    print("Can\'t divide by zero")\n'
                            "```\n\n"
                            "Only the exception types you name in "
                            "`except` are caught — anything else still "
                            "crashes, which is deliberate: silently "
                            "swallowing *every* error hides real bugs "
                            "instead of fixing them.\n\n"
                            "```python\n"
                            "try:\n"
                            "    age = int(user_input)\n"
                            "except ValueError:\n"
                            '    print("That\'s not a valid number")\n'
                            "```\n\n"
                            "`finally` runs no matter what — whether "
                            "the `try` block succeeded, failed, or "
                            "even hit a `return` on the way out — "
                            "which makes it the right place for "
                            "cleanup code, like closing a file:\n\n"
                            "```python\n"
                            "try:\n"
                            '    f = open("data.txt")\n'
                            "    # ... work with f ...\n"
                            "finally:\n"
                            "    f.close()\n"
                            "```\n\n"
                            "This matters more than it might look for "
                            "AI engineering specifically: a call to a "
                            "model API can fail for reasons entirely "
                            "outside your code — rate limits, network "
                            "blips, a temporary outage — and a "
                            "production system needs to catch those "
                            "failures deliberately rather than letting "
                            "one bad request crash the whole request "
                            "handler."
                        ),
                    ),
                ],
            ),
            Module(
                title="Working with Packages and Data",
                order=3,
                lessons=[
                    Lesson(
                        title="Modules, Packages, and pip",
                        order=1,
                        body=(
                            "# Modules, Packages, and pip\n\n"
                            "A module is just a Python file; a "
                            "package is a folder of modules. Python "
                            "ships with a large standard library of "
                            "modules you can use immediately:\n\n"
                            "```python\n"
                            "import math\n"
                            "math.sqrt(16)  # 4.0\n\n"
                            "from datetime import datetime\n"
                            "datetime.now()\n"
                            "```\n\n"
                            "Anything not in the standard library has "
                            "to be installed separately, which is "
                            "what `pip` (Python's package installer) "
                            "is for:\n\n"
                            "```bash\n"
                            "pip install requests\n"
                            "```\n\n"
                            "Once installed, you import it the same "
                            "way as a standard-library module:\n\n"
                            "```python\n"
                            "import requests\n"
                            'response = requests.get("https://api.example.com")\n'
                            "```\n\n"
                            "Real projects pin exact versions of "
                            "every package they depend on (often in a "
                            "`requirements.txt` or `pyproject.toml` "
                            'file) rather than "whatever pip installs '
                            'today" — without that, the exact same '
                            "code can behave differently on your "
                            "machine versus a teammate's, or in "
                            "production versus your laptop, purely "
                            "because of which package version "
                            "happened to get installed."
                        ),
                    ),
                    Lesson(
                        title="Working with JSON",
                        order=2,
                        body=(
                            "# Working with JSON\n\n"
                            "JSON (JavaScript Object Notation) is the "
                            "format almost every web API — including "
                            "every LLM provider's API — sends and "
                            "receives data in. Python's standard "
                            "library converts between JSON text and "
                            "native Python objects directly:\n\n"
                            "```python\n"
                            "import json\n\n"
                            'data = json.loads(\'{"name": "Ada", '
                            '"age": 27}\')\n'
                            "# now a real Python dict\n\n"
                            'json.dumps({"name": "Ada", "age": 27})\n'
                            "# back to a JSON string\n"
                            "```\n\n"
                            "A JSON object becomes a Python `dict`; a "
                            "JSON array becomes a `list` — exactly why "
                            "the earlier lessons on lists and "
                            "dictionaries matter here. Once you can "
                            "call `.loads()` on an API response, "
                            "everything you already know about dicts "
                            "and lists is how you actually use the "
                            "data:\n\n"
                            "```python\n"
                            "response_data = json.loads(api_response_text)\n"
                            'first_result = response_data["results"][0]\n'
                            'print(first_result["title"])\n'
                            "```\n\n"
                            "This is the exact mechanism behind every "
                            "response this platform's own backend has "
                            "sent your browser so far — a Python "
                            "dict, serialized to JSON on the way out, "
                            "parsed back into a JavaScript object on "
                            "the way in."
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
