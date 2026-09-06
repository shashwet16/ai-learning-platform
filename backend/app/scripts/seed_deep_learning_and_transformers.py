"""Populate the database with "Deep Learning & Transformers" — course
#6 of the 10-course curriculum plan (see ROADMAP.md's "Curriculum
content expansion plan").

Covers the plan's own stated scope for this course: neural nets,
attention, and how an LLM actually works under the hood — deliberately
building toward a full-circle callback to this platform's own existing
"What is AI Engineering?" lesson (M3.2), whose entire premise is that AI
engineers build on top of pretrained models rather than training from
scratch. This course's final lesson explains exactly *why* that
pretraining happened and what it produces.

No deep learning libraries are used or required — every code example is
either pure conceptual explanation or plain Python (math module only)
illustrating the underlying arithmetic (a single neuron's weighted sum,
one gradient-descent step, cosine similarity, softmax), consistent with
every other course's stdlib-only constraint for graded exercises.
Deliberately simplified relative to a real neural network (a single
neuron, not a trained multi-layer network; a toy scalar minimization,
not real backpropagation through many parameters) — each lesson says so
explicitly, so the simplification reads as a teaching choice, not a
factual claim about how production models actually work. Original
writing throughout.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_deep_learning_and_transformers

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Deep Learning & Transformers"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "How an LLM actually works under the hood — neurons, "
            "backpropagation, embeddings, attention, and the "
            "transformer architecture, ending with why AI engineers "
            "build on pretrained models instead of training from "
            "scratch."
        ),
        modules=[
            Module(
                title="Neural Network Basics",
                order=1,
                lessons=[
                    Lesson(
                        title="Neurons, Weights, and Activation Functions",
                        order=1,
                        body=(
                            "# Neurons, Weights, and Activation Functions\n\n"
                            "The basic building block of a neural "
                            "network is an artificial **neuron**: it "
                            "takes several numeric inputs, multiplies "
                            "each by its own learned **weight**, adds "
                            "them up along with a **bias**, and passes "
                            "the result through an **activation "
                            "function**:\n\n"
                            "```python\n"
                            "import math\n\n"
                            "def sigmoid(x):\n"
                            "    return 1 / (1 + math.exp(-x))\n\n"
                            "def neuron_output(inputs, weights, bias):\n"
                            "    pairs = zip(inputs, weights)\n"
                            "    weighted_sum = sum(i * w for i, w in pairs)\n"
                            "    return sigmoid(weighted_sum + bias)\n"
                            "```\n\n"
                            "The weights and bias are exactly what "
                            "*training* adjusts — a freshly initialized "
                            "neuron's weights are close to random, and "
                            "learning means nudging them so the "
                            "network's output gets closer to correct.\n\n"
                            "The activation function matters more than "
                            "it looks: without one (or with a linear "
                            "one), stacking many layers of neurons "
                            "would still only ever compute one big "
                            "linear function — no more expressive than "
                            "a single layer. A non-linear activation "
                            "(sigmoid above, or the more commonly used "
                            "ReLU: `max(0, x)`) is what lets a deep "
                            "network represent genuinely complex, "
                            "curved relationships between input and "
                            "output.\n\n"
                            "A single neuron, wired up this simply, is "
                            "a real (if tiny) building block — a "
                            "production model is millions or billions "
                            "of these, arranged in layers, not one."
                        ),
                    ),
                    Lesson(
                        title="Forward Pass and Backpropagation",
                        order=2,
                        body=(
                            "# Forward Pass and Backpropagation\n\n"
                            "The **forward pass** is just running the "
                            "network: feed inputs in, compute each "
                            "neuron's output layer by layer (the "
                            "previous lesson's `neuron_output`, "
                            "chained together), and get a prediction "
                            "out the other end.\n\n"
                            "A **loss function** then measures how "
                            "wrong that prediction was compared to the "
                            "correct answer — a single number where "
                            "lower is better.\n\n"
                            "**Backpropagation** is the algorithm that "
                            "works backward from the loss to figure "
                            "out how much *each individual weight* "
                            "contributed to the error, using calculus "
                            "(the chain rule) to compute a "
                            "**gradient** for every weight — the "
                            "direction and size of change to that "
                            "weight that would reduce the loss "
                            "fastest. **Gradient descent** then nudges "
                            "every weight a small step in that "
                            "direction, and the whole cycle (forward "
                            "pass → loss → backward pass → nudge "
                            "weights) repeats, often millions of "
                            "times.\n\n"
                            "Backpropagation across millions of "
                            "weights needs real calculus this course "
                            "won't derive, but the *core idea* — take "
                            "a step proportional to the slope, in the "
                            "direction that reduces error — is real "
                            "and small enough to see directly on a toy "
                            "single-variable example, minimizing "
                            "`(x - 3)²` (whose slope at any `x` is "
                            "`2 * (x - 3)`):\n\n"
                            "```python\n"
                            "def gradient_descent_step(x, learning_rate):\n"
                            "    gradient = 2 * (x - 3)\n"
                            "    return x - learning_rate * gradient\n"
                            "```\n\n"
                            "Repeatedly calling this with the same "
                            "`x` it just returned walks `x` toward "
                            "`3` — the actual minimum of `(x - 3)²` — "
                            "a one-dimensional preview of exactly what "
                            "gradient descent does to millions of "
                            "weights at once during real training."
                        ),
                    ),
                ],
            ),
            Module(
                title="From Words to Vectors",
                order=2,
                lessons=[
                    Lesson(
                        title="Embeddings: Turning Tokens into Vectors",
                        order=1,
                        body=(
                            "# Embeddings: Turning Tokens into Vectors\n\n"
                            "A neural network only operates on "
                            "numbers, but text is made of tokens (as "
                            "the existing 'Tokens, Context Windows, "
                            "and Cost' lesson covers). An **embedding** "
                            "is a learned mapping from each token to a "
                            "vector of numbers — a list of floats — "
                            "positioned in space so that tokens with "
                            "similar meaning end up near each other:\n\n"
                            "```python\n"
                            "embeddings = {\n"
                            '    "cat": [0.9, 0.1, 0.0],\n'
                            '    "kitten": [0.85, 0.15, 0.0],\n'
                            '    "car": [0.0, 0.1, 0.9],\n'
                            "}\n"
                            "```\n\n"
                            "'Near each other' is measured with "
                            "**cosine similarity** — how closely two "
                            "vectors point in the same direction, from "
                            "-1 (opposite) to 1 (identical "
                            "direction):\n\n"
                            "```python\n"
                            "import math\n\n"
                            "def cosine_similarity(vec_a, vec_b):\n"
                            "    dot = sum(a * b for a, b in zip(vec_a, vec_b))\n"
                            "    mag_a = math.sqrt(sum(a * a for a in vec_a))\n"
                            "    mag_b = math.sqrt(sum(b * b for b in vec_b))\n"
                            "    return dot / (mag_a * mag_b)\n"
                            "```\n\n"
                            "Run on the embeddings above, "
                            '`cosine_similarity` between `"cat"` and '
                            '`"kitten"` comes out much higher than '
                            'between `"cat"` and `"car"` — the '
                            "embedding has captured that cats and "
                            "kittens are related, purely from "
                            "*numbers*, with no explicit rule saying "
                            "so. Real embeddings have hundreds or "
                            "thousands of dimensions, not three, "
                            "learned from vast amounts of text rather "
                            "than hand-written like the toy example "
                            "above."
                        ),
                    ),
                    Lesson(
                        title="The Attention Mechanism",
                        order=2,
                        body=(
                            "# The Attention Mechanism\n\n"
                            "A word's meaning often depends on the "
                            "rest of the sentence: in 'the trophy "
                            "didn't fit in the suitcase because *it* "
                            "was too big', resolving what 'it' refers "
                            "to means looking at 'trophy', not just "
                            "the words next to 'it'. **Attention** is "
                            "the mechanism that lets every token in a "
                            "sequence look at every other token and "
                            "decide how much to weigh each one when "
                            "building its own updated representation.\n\n"
                            "Mechanically, each token produces three "
                            "vectors — a **query** (what am I looking "
                            "for?), a **key** (what do I offer?), and "
                            "a **value** (what information do I "
                            "actually carry?). A token's query is "
                            "compared against every other token's key "
                            "to produce a raw attention score per "
                            "pair, and those scores are converted into "
                            "weights that sum to 1 using **softmax**:\n\n"
                            "```python\n"
                            "import math\n\n"
                            "def softmax(scores):\n"
                            "    max_score = max(scores)\n"
                            "    shifted = [s - max_score for s in scores]\n"
                            "    exp_scores = [math.exp(s) for s in shifted]\n"
                            "    total = sum(exp_scores)\n"
                            "    return [e / total for e in exp_scores]\n"
                            "```\n\n"
                            "Subtracting the max score before "
                            "exponentiating doesn't change the "
                            "result mathematically — softmax is "
                            "shift-invariant — but it keeps every "
                            "exponent at or below zero, which is what "
                            "keeps large real attention scores from "
                            "overflowing to infinity in floating-point "
                            "math.\n\n"
                            "Once every score is a weight, the "
                            "token's new representation becomes a "
                            "weighted sum of every token's *value* "
                            "vector, using those weights — 'it' ends "
                            "up mostly built from 'trophy''s value "
                            "vector, because 'it''s query matched "
                            "'trophy''s key strongly."
                        ),
                    ),
                ],
            ),
            Module(
                title="The Transformer Architecture",
                order=3,
                lessons=[
                    Lesson(
                        title="The Transformer Architecture",
                        order=1,
                        body=(
                            "# The Transformer Architecture\n\n"
                            "A transformer stacks many identical "
                            "blocks, each combining the previous two "
                            "lessons' ideas: a **self-attention** "
                            "layer (every token attends to every "
                            "other token, as the last lesson "
                            "describes) followed by a small "
                            "feed-forward neural network (built from "
                            "the neurons in this course's first "
                            "lesson) applied to each token "
                            "independently.\n\n"
                            "Two structural details make this "
                            "actually trainable at the depth real "
                            "models use (dozens of stacked blocks):\n\n"
                            "- **Residual (skip) connections** — each "
                            "block's output is added back to its own "
                            "input, rather than replacing it outright, "
                            "which keeps gradients from vanishing as "
                            "they backpropagate through many stacked "
                            "blocks\n"
                            "- **Normalization** — rescaling the "
                            "numbers flowing between blocks so they "
                            "stay in a well-behaved range as they pass "
                            "through dozens of layers\n\n"
                            "The transformer's genuinely novel "
                            "contribution (from the 2017 paper that "
                            "introduced it) is processing an *entire* "
                            "sequence's attention in parallel, rather "
                            "than one token at a time the way older "
                            "recurrent architectures did — which is "
                            "what made training on the enormous "
                            "internet-scale datasets behind modern "
                            "LLMs practical on real hardware in real "
                            "time at all."
                        ),
                    ),
                    Lesson(
                        title=(
                            "From Next-Token Prediction to Chat: "
                            "Pretraining and Fine-Tuning"
                        ),
                        order=2,
                        body=(
                            "# From Next-Token Prediction to Chat: "
                            "Pretraining and Fine-Tuning\n\n"
                            "The training objective behind a base "
                            "LLM is deceptively simple: given all the "
                            "text so far, predict the single next "
                            "token, over and over, across enormous "
                            "amounts of text scraped from the "
                            "internet, books, and code. This stage is "
                            "called **pretraining**, and it's what "
                            "actually adjusts the billions of weights "
                            "this course's earlier lessons "
                            "describe.\n\n"
                            "A model trained purely this way — a "
                            "**base model** — is good at completing "
                            "text plausibly, but has no particular "
                            "reason to be a helpful assistant: asked "
                            "a question, it might just as easily "
                            "continue with more questions in the same "
                            "style, because that's what often follows "
                            "a question in its training data.\n\n"
                            "**Fine-tuning** takes that pretrained "
                            "base model and adjusts it further on a "
                            "much smaller, carefully curated dataset — "
                            "instruction/response pairs, and often "
                            "human feedback on which responses are "
                            "better (reinforcement learning from "
                            "human feedback, RLHF) — specifically to "
                            "make it behave like a helpful assistant "
                            "rather than just a text completer.\n\n"
                            "This is the exact reason this platform's "
                            "very first lesson, 'What is AI "
                            "Engineering?', defines the discipline as "
                            "building *on top of* pretrained models "
                            "rather than training from scratch: "
                            "pretraining a model from nothing costs "
                            "millions of dollars of compute and "
                            "enormous datasets, so almost no one "
                            "outside a few labs ever does it. Every "
                            "prompt, every RAG pipeline, and every "
                            "agent in this platform's other courses "
                            "works entirely on the fine-tuned side of "
                            "this line — shaping how an already-"
                            "trained model behaves, never retraining "
                            "its weights."
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
