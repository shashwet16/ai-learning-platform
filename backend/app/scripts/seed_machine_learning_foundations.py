"""Populate the database with "Machine Learning Foundations" — course
#4 of the 10-course curriculum plan (see ROADMAP.md's "Curriculum
content expansion plan").

Covers the plan's own stated scope for this course: supervised versus
unsupervised learning and evaluation basics, deliberately *before*
jumping straight to LLMs — the vocabulary (features/labels, overfitting,
precision/recall) that "Deep Learning & Transformers" (course #6) and
this platform's existing "Evaluation and Testing" lesson both assume a
reader already has. No ML libraries are used or required — every
example is either pure conceptual explanation or plain Python
illustrating the underlying arithmetic (e.g. computing precision/recall
from raw counts), consistent with every other course's stdlib-only
constraint for graded exercises. Original writing throughout.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_machine_learning_foundations

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Machine Learning Foundations"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "The core machine learning vocabulary and evaluation "
            "instincts every later course assumes — supervised versus "
            "unsupervised learning, overfitting, and how to actually "
            "measure whether a model works — before jumping straight "
            "to LLMs."
        ),
        modules=[
            Module(
                title="What Machine Learning Is",
                order=1,
                lessons=[
                    Lesson(
                        title="Supervised vs. Unsupervised Learning",
                        order=1,
                        body=(
                            "# Supervised vs. Unsupervised Learning\n\n"
                            "**Supervised learning** trains a model on "
                            "examples that already have the right "
                            "answer attached, so it can predict that "
                            "answer for new, unseen examples:\n\n"
                            "- Given past emails labeled 'spam' or "
                            "'not spam', predict the label for a new "
                            "email\n"
                            "- Given houses with known sale prices, "
                            "predict the price of a house that hasn't "
                            "sold yet\n\n"
                            "**Unsupervised learning** has no right "
                            "answer to learn from — it looks for "
                            "structure in the data itself:\n\n"
                            "- Group customers into segments based on "
                            "purchase history, with no predefined "
                            "segment labels to match\n"
                            "- Find that a set of news articles "
                            "clusters into a handful of topics, "
                            "without being told what those topics are "
                            "in advance\n\n"
                            "A third category, *reinforcement "
                            "learning* (an agent learns by trial and "
                            "error, getting a reward signal instead of "
                            "labeled examples), is out of scope for "
                            "this course but worth knowing exists.\n\n"
                            "This course focuses on supervised "
                            "learning almost entirely — it's the "
                            "category most directly relevant to "
                            "evaluating whether a model (including an "
                            "LLM's outputs, later in this platform) is "
                            "actually right."
                        ),
                    ),
                    Lesson(
                        title="Features, Labels, and Training Data",
                        order=2,
                        body=(
                            "# Features, Labels, and Training Data\n\n"
                            "In supervised learning, each example "
                            "breaks into two parts:\n\n"
                            "- **Features** — the inputs describing "
                            "the example (a house's square footage, "
                            "number of bedrooms, and location)\n"
                            "- **Label** — the answer you want the "
                            "model to predict (that house's actual "
                            "sale price)\n\n"
                            "In Python, one example is naturally a "
                            "dict, and a **dataset** is a list of "
                            "them:\n\n"
                            "```python\n"
                            "dataset = [\n"
                            '    {"sqft": 1200, "bedrooms": 2, "price": 250_000},\n'
                            '    {"sqft": 1800, "bedrooms": 3, "price": 340_000},\n'
                            '    {"sqft": 900, "bedrooms": 1, "price": 190_000},\n'
                            "]\n"
                            "```\n\n"
                            "Here, `sqft` and `bedrooms` are features; "
                            "`price` is the label. **Training** means "
                            "showing a model many such examples so it "
                            "can learn the general relationship "
                            "between features and label, well enough "
                            "to predict the label for a *new* example "
                            "it's never seen.\n\n"
                            "A pattern worth internalizing early: the "
                            "quality and quantity of training data "
                            "usually matters more to how well a model "
                            "performs than the specific algorithm "
                            "chosen — 'garbage in, garbage out' is as "
                            "true for machine learning as it is for "
                            "any other kind of software."
                        ),
                    ),
                ],
            ),
            Module(
                title="Building a Model",
                order=2,
                lessons=[
                    Lesson(
                        title="Regression vs. Classification",
                        order=1,
                        body=(
                            "# Regression vs. Classification\n\n"
                            "Supervised learning splits further by "
                            "what kind of label is being predicted:\n\n"
                            "**Regression** predicts a continuous "
                            "number:\n\n"
                            "```python\n"
                            "def predict_price(sqft):\n"
                            "    # A real model learns coefficients "
                            "like these from data;\n"
                            "    # here they're just fixed, to "
                            "illustrate the shape of the answer.\n"
                            "    return 150 * sqft + 20_000\n\n"
                            "predict_price(1200)  # 200,000 — a "
                            "number, not a category\n"
                            "```\n\n"
                            "**Classification** predicts a discrete "
                            "category from a fixed set of options:\n\n"
                            "```python\n"
                            "def classify_email(spam_score):\n"
                            '    return "spam" if spam_score > 0.5 else "not spam"\n\n'
                            "classify_email(0.8)\n"
                            '# "spam" — one of a fixed set of labels, not a number\n'
                            "```\n\n"
                            "Classification can have exactly two "
                            "possible labels (*binary*, like the spam "
                            "example) or more than two (*multi-class*, "
                            "like classifying a photo as a cat, dog, "
                            "or bird). The distinction matters because "
                            "regression and classification are "
                            "evaluated with entirely different "
                            "metrics — a later lesson in this course "
                            "covers classification's own metrics in "
                            "depth."
                        ),
                    ),
                    Lesson(
                        title="Training, Validation, and Test Splits",
                        order=2,
                        body=(
                            "# Training, Validation, and Test Splits\n\n"
                            "Evaluating a model on the same data it "
                            "was trained on is misleading — a model "
                            "can simply memorize the training "
                            "examples and score perfectly, without "
                            "having learned anything that generalizes "
                            "to new data. The standard fix is to split "
                            "the dataset into three parts *before* "
                            "training even starts:\n\n"
                            "- **Training set** — what the model "
                            "actually learns from (a common split is "
                            "around 70% of the data)\n"
                            "- **Validation set** — used to compare "
                            "different choices (which features to "
                            "use, which settings to try) *during* "
                            "development, without touching the real "
                            "test data\n"
                            "- **Test set** — touched exactly once, "
                            "at the very end, to report an honest "
                            "final number\n\n"
                            "```python\n"
                            "def split_dataset(data, train_frac=0.7, val_frac=0.15):\n"
                            "    train_end = int(len(data) * train_frac)\n"
                            "    val_end = train_end + int(len(data) * val_frac)\n"
                            "    train = data[:train_end]\n"
                            "    val = data[train_end:val_end]\n"
                            "    test = data[val_end:]\n"
                            "    return train, val, test\n"
                            "```\n\n"
                            "The discipline that matters most here "
                            "isn't the exact ratio — it's never "
                            "letting test-set performance influence "
                            "any decision made before that final "
                            "report. The moment you tune something "
                            "based on the test set, it's stopped "
                            "measuring generalization and started "
                            "measuring how well you fit it, which is "
                            "exactly the mistake this three-way split "
                            "exists to prevent."
                        ),
                    ),
                ],
            ),
            Module(
                title="Knowing If It Worked",
                order=3,
                lessons=[
                    Lesson(
                        title="Overfitting and Underfitting",
                        order=1,
                        body=(
                            "# Overfitting and Underfitting\n\n"
                            "**Overfitting** is when a model learns "
                            "the training data too specifically — "
                            "including its noise and quirks — instead "
                            "of the general pattern underneath. It "
                            "shows up as a big gap between training "
                            "performance (excellent) and validation "
                            "performance (much worse): the model "
                            "memorized rather than learned.\n\n"
                            "**Underfitting** is the opposite — the "
                            "model is too simple to capture the real "
                            "pattern at all, and performs poorly on "
                            "*both* the training and validation "
                            "data.\n\n"
                            "A useful analogy: overfitting is "
                            "memorizing the answers to last year's "
                            "practice exam without understanding the "
                            "material, then failing a new exam that "
                            "asks the same concepts in a different "
                            "way. Underfitting is not having studied "
                            "the material at all, and failing both "
                            "exams equally.\n\n"
                            "This is exactly why the previous lesson's "
                            "validation set matters: training "
                            "performance alone can't tell these two "
                            "failure modes apart from genuine success "
                            "— only checking performance on data the "
                            "model never trained on can."
                        ),
                    ),
                    Lesson(
                        title="Evaluation Metrics: Accuracy, Precision, Recall",
                        order=2,
                        body=(
                            "# Evaluation Metrics: Accuracy, Precision, Recall\n\n"
                            "**Accuracy** — the fraction of "
                            "predictions that were correct — is the "
                            "most intuitive metric, and also the most "
                            "commonly misleading one. On a dataset "
                            "where 99% of emails are *not* spam, a "
                            "model that always predicts 'not spam' "
                            "gets 99% accuracy while catching zero "
                            "actual spam.\n\n"
                            "Two more specific metrics fix this, both "
                            "computed from the same four counts: true "
                            "positives (TP), false positives (FP), "
                            "and false negatives (FN):\n\n"
                            "- **Precision** = TP / (TP + FP) — of "
                            "everything the model flagged as spam, "
                            "what fraction actually was spam?\n"
                            "- **Recall** = TP / (TP + FN) — of "
                            "everything that actually was spam, what "
                            "fraction did the model catch?\n\n"
                            "```python\n"
                            "def precision(true_positives, false_positives):\n"
                            "    predicted_pos = true_positives + false_positives\n"
                            "    return true_positives / predicted_pos\n\n"
                            "def recall(true_positives, false_negatives):\n"
                            "    actual_positive = true_positives + false_negatives\n"
                            "    return true_positives / actual_positive\n"
                            "```\n\n"
                            "The two trade off against each other: a "
                            "spam filter that flags *everything* as "
                            "spam has perfect recall (it catches "
                            "every real spam email) but terrible "
                            "precision (it also flags every real "
                            "email). Which one matters more is a "
                            "product decision, not a purely technical "
                            "one — missing a real spam email and "
                            "wrongly hiding a real email from someone "
                            "are not equally bad mistakes."
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
