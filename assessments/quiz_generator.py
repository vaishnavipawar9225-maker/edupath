"""
Procedural quiz generators — infinite variety, no API key needed.
Each generator returns: List[(question_text, [4 choices], correct_index, marks)]
"""
import random


# ============================================================
# MATHS — ALGEBRA
# ============================================================
def generate_algebra(n=5):
    questions = []
    for _ in range(n):
        template = random.choice([
            "linear", "quadratic", "polynomial_degree", "expand", "simplify"
        ])

        if template == "linear":
            a = random.randint(2, 9)
            x = random.randint(1, 12)
            b = random.randint(1, 20)
            c = a * x + b
            text = f"Solve for x: {a}x + {b} = {c}"
            choices = [str(x), str(x + 1), str(x - 1), str(x + 2)]
            correct = choices[0]
            random.shuffle(choices)

        elif template == "quadratic":
            p = random.randint(1, 8)
            q = random.randint(1, 8)
            b = -(p + q)
            c = p * q
            text = f"Find the roots of x² + ({b})x + {c} = 0"
            correct = f"{p} and {q}"
            choices = [correct, f"{p+1} and {q}", f"{p} and {q+1}", f"-{p} and -{q}"]
            random.shuffle(choices)

        elif template == "polynomial_degree":
            degree = random.randint(2, 5)
            terms = [f"{random.randint(1,9)}x^{i}" if i > 1 else
                     f"{random.randint(1,9)}x" if i == 1 else
                     str(random.randint(1, 9))
                     for i in range(degree, -1, -1)]
            text = f"What is the degree of: {' + '.join(terms)}?"
            correct = str(degree)
            choices = [correct, str(degree + 1), str(degree - 1), str(1)]
            random.shuffle(choices)

        elif template == "expand":
            a = random.randint(2, 6)
            b = random.randint(2, 6)
            text = f"Expand: (x + {a})(x + {b})"
            correct = f"x² + {a+b}x + {a*b}"
            choices = [correct, f"x² + {a*b}x + {a+b}",
                       f"x² + {a-b}x + {a*b}", f"x² + {a+b}x + {a-b}"]
            random.shuffle(choices)

        else:  # simplify
            a = random.randint(2, 9)
            b = random.randint(1, 9)
            c = a + b
            text = f"Simplify: {a}x + {b}x"
            correct = f"{c}x"
            choices = [correct, f"{a*b}x", f"{c}x²", f"{c}"]
            random.shuffle(choices)

        questions.append((text, choices, choices.index(correct), 2))
    return questions


# ============================================================
# PHYSICS — MOTION & FORCE
# ============================================================
def generate_physics(n=5):
    questions = []
    for _ in range(n):
        template = random.choice(["force", "speed", "ohm", "gravity", "momentum"])

        if template == "force":
            m = random.randint(2, 20)
            a = random.randint(1, 10)
            f = m * a
            text = f"A mass of {m} kg accelerates at {a} m/s². What is the force?"
            correct = f"{f} N"
            choices = [correct, f"{m+a} N", f"{m*a*2} N", f"{m} N"]
            random.shuffle(choices)

        elif template == "speed":
            d = random.randint(10, 200)
            t = random.randint(2, 10)
            s = round(d / t, 2)
            text = f"A car travels {d} m in {t} s. What is its speed?"
            correct = f"{s} m/s"
            choices = [correct, f"{d*t} m/s", f"{t/d:.2f} m/s", f"{d+t} m/s"]
            random.shuffle(choices)

        elif template == "ohm":
            v = random.choice([6, 9, 12, 24])
            r = random.choice([2, 3, 4, 6, 8])
            i = round(v / r, 2)
            text = f"A {v} V battery is connected to a {r} Ω resistor. What is the current?"
            correct = f"{i} A"
            choices = [correct, f"{v*r} A", f"{r/v:.2f} A", f"{v+r} A"]
            random.shuffle(choices)

        elif template == "gravity":
            m = random.randint(1, 10)
            g = 9.8
            w = round(m * g, 1)
            text = f"What is the weight of a {m} kg object on Earth? (g = 9.8 m/s²)"
            correct = f"{w} N"
            choices = [correct, f"{m} N", f"{m*g*2:.1f} N", f"{m/g:.2f} N"]
            random.shuffle(choices)

        else:  # momentum
            m = random.randint(2, 15)
            v = random.randint(1, 20)
            p = m * v
            text = f"Calculate momentum: mass = {m} kg, velocity = {v} m/s"
            correct = f"{p} kg·m/s"
            choices = [correct, f"{m+v} kg·m/s", f"{m*v*2} kg·m/s", f"{v} kg·m/s"]
            random.shuffle(choices)

        questions.append((text, choices, choices.index(correct), 2))
    return questions


# ============================================================
# ENGLISH — GRAMMAR
# ============================================================
VERBS = [
    ("go", "went"), ("eat", "ate"), ("run", "ran"), ("see", "saw"),
    ("take", "took"), ("write", "wrote"), ("speak", "spoke"), ("break", "broke"),
    ("give", "gave"), ("sing", "sang"), ("drink", "drank"), ("fly", "flew"),
]
PREPOSITIONS = ["under", "above", "between", "across", "behind", "through", "beside"]
ADJECTIVES = ["beautiful", "tall", "bright", "brave", "quiet", "happy", "clever"]
NOUNS = ["dog", "teacher", "river", "mountain", "garden", "book", "city"]


def generate_grammar(n=5):
    questions = []

    for _ in range(n):
        template = random.choice([
            "past_tense",
            "preposition",
            "adjective",
            "verb_id",
            "article"
        ])

        if template == "past_tense":
            present, past = random.choice(VERBS)

            text = f"What is the past tense of '{present}'?"

            correct = past
            wrong = [
                w[1] for w in VERBS
                if w[1] != past
            ]

            choices = [correct] + random.sample(wrong, 3)

        elif template == "preposition":
            # Use sentences with an unambiguous correct answer.
            examples = [
                ("The cat is hiding ___ the table.", "under"),
                ("The picture hangs ___ the sofa.", "above"),
                ("The teacher stood ___ two students.", "between"),
                ("The train passed ___ the tunnel.", "through"),
                ("The boy stood ___ his mother.", "beside"),
                ("The car is parked ___ the building.", "behind"),
                ("She walked ___ the street.", "across"),
            ]

            text, correct = random.choice(examples)

            wrong = [
                p for p in PREPOSITIONS
                if p != correct
            ]

            choices = [correct] + random.sample(wrong, 3)

        elif template == "adjective":
            adj = random.choice(ADJECTIVES)

            text = "Which word is an adjective?"

            correct = adj

            wrong_pool = (
                PREPOSITIONS + NOUNS +
                [w[0] for w in VERBS]
            )

            wrong = random.sample(wrong_pool, 3)

            choices = [correct] + wrong

        elif template == "verb_id":
            verb_pair = random.choice(VERBS)
            verb = verb_pair[0]

            text = f"Identify the verb: 'They {verb} every day.'"

            correct = verb

            wrong_pool = [
                w[0] for w in VERBS
                if w[0] != verb
            ]

            wrong = random.sample(wrong_pool, 3)

            choices = [correct] + wrong

        else:  # article
            noun = random.choice(NOUNS)

            # Use "an" before vowel sounds in these examples.
            if noun[0].lower() in "aeiou":
                correct = "an"
            else:
                correct = "a"

            text = f"Fill in: 'She saw ___ {noun}.'"

            wrong = [
                option for option in
                ["a", "an", "the", "no article"]
                if option != correct
            ]

            choices = [correct] + random.sample(wrong, 3)

        # Shuffle answers and preserve the correct answer's index.
        random.shuffle(choices)

        questions.append((
            text,
            choices,
            choices.index(correct),
            2
        ))

    return questions


# ============================================================
# DISPATCHER — pick the right generator for the quiz
# ============================================================
GENERATORS = {
    "Algebra": generate_algebra,
    "Mathematics": generate_algebra,
    "Physics": generate_physics,
    "Science": generate_physics,
    "Grammar": generate_grammar,
    "English": generate_grammar,
}

def generate_questions_for_quiz(quiz, n=5):
    # Try AI first
    from .ai_generator import generate_with_gemini
    ai_questions = generate_with_gemini(quiz.course.subject.name + " " + quiz.title, n)
    if ai_questions:
        return ai_questions
    # Fallback to procedural

def generate_questions_for_quiz(quiz, n=5):
    """Return the correct list of generated questions for a quiz."""
    course_title = quiz.course.title.lower()
    subject_name = quiz.course.subject.name

    # Try subject first, then course title
    for key, gen in GENERATORS.items():
        if key.lower() in subject_name.lower() or key.lower() in course_title:
            return gen(n)

    # Fallback: use Algebra
    return generate_algebra(n)